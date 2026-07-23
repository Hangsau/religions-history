#!/usr/bin/env python3
"""MiniMax-M3 額度自動恢復 watcher。

額度耗盡時依官方 5H/7D reset time 單次等待；官方時間不可用時才採
5/10/20/30 分鐘 fallback。HALT flag 存在時停止自動恢復。
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

from pipeline_lock import create_pid_lock

ROOT = Path(__file__).resolve().parent.parent
LOGS = ROOT / "logs"
HALT = LOGS / "pipeline-HALT.flag"  # 僅人工暫停；自動配額等待不使用此檔
RUNTIME = LOGS / "pipeline-runtime.json"
WATCH_LOG = LOGS / "quota-watch.log"
PIDFILE = LOGS / "quota-watch.pid"
MINIMAX_TOKEN_PATH = Path.home() / ".minimax-token"
QUOTA_URL = "https://www.minimax.io/v1/token_plan/remains"
TZ = timezone(timedelta(hours=8))

DEFAULT_MAX_DAYS = 10
BACKOFF_SECONDS = (300, 600, 1200, 1800)
RESET_BUFFER_SECONDS = 15
WAIT_SLICE_SECONDS = 30
INTERVAL_RESERVE_PERCENT = float(os.environ.get("RELIGIONS_QUOTA_INTERVAL_RESERVE", "5"))
WEEKLY_RESERVE_PERCENT = float(os.environ.get("RELIGIONS_QUOTA_WEEKLY_RESERVE", "2"))
WAITING_STATUSES = {"waiting_quota", "waiting_provider"}


def log(msg: str) -> None:
    line = f"{datetime.now(TZ).strftime('%Y-%m-%d %H:%M:%S')} {msg}"
    print(line, flush=True)
    LOGS.mkdir(exist_ok=True)
    with WATCH_LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_state() -> dict:
    try:
        return json.loads(RUNTIME.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save_state(state: dict) -> None:
    state["updated_at"] = datetime.now(TZ).isoformat()
    RUNTIME.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=RUNTIME.name + ".", suffix=".tmp", dir=RUNTIME.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(state, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, RUNTIME)
    finally:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass


def _percentage(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    return number if math.isfinite(number) and 0 <= number <= 100 else None


def _datetime_from_millis(value: object) -> datetime | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        return None
    try:
        return datetime.fromtimestamp(number / 1000, TZ)
    except (OSError, OverflowError, ValueError):
        return None


def probe_quota(now: datetime | None = None) -> tuple[str, str, dict, datetime | None]:
    """Return usable, official_reset, or fallback with an optional retry time."""
    now = now or datetime.now(TZ)
    if not MINIMAX_TOKEN_PATH.exists():
        return "fallback", "no token file", {}, None
    token = MINIMAX_TOKEN_PATH.read_text(encoding="utf-8").strip()
    req = urllib.request.Request(QUOTA_URL, method="GET", headers={
        "Authorization": f"Bearer {token}",
        "content-type": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        models = payload.get("model_remains", [])
        general = next((item for item in models if item.get("model_name") == "general"), None)
        if not isinstance(general, dict):
            return "fallback", "quota response missing general model", {"raw_status": payload.get("base_resp")}, None
        interval = _percentage(general.get("current_interval_remaining_percent"))
        weekly = _percentage(general.get("current_weekly_remaining_percent"))
        interval_reset = _datetime_from_millis(general.get("end_time"))
        weekly_reset = _datetime_from_millis(general.get("weekly_end_time"))
        summary = {
            "model": "general",
            "interval_remaining_percent": interval,
            "weekly_remaining_percent": weekly,
            "interval_resets_at": interval_reset.isoformat() if interval_reset else None,
            "weekly_resets_at": weekly_reset.isoformat() if weekly_reset else None,
            "interval_status": general.get("current_interval_status"),
            "weekly_status": general.get("current_weekly_status"),
        }
        if interval is None or weekly is None:
            return "fallback", "quota response has invalid percentages", summary, None
        exhausted_resets = []
        if interval <= INTERVAL_RESERVE_PERCENT:
            if interval_reset is None or interval_reset <= now:
                return "fallback", "5h quota reset time missing or expired", summary, None
            exhausted_resets.append(interval_reset)
        if weekly <= WEEKLY_RESERVE_PERCENT:
            if weekly_reset is None or weekly_reset <= now:
                return "fallback", "weekly quota reset time missing or expired", summary, None
            exhausted_resets.append(weekly_reset)
        detail = (f"5h={interval:g}% (reserve {INTERVAL_RESERVE_PERCENT:g}%) "
                  f"weekly={weekly:g}% (reserve {WEEKLY_RESERVE_PERCENT:g}%)")
        if not exhausted_resets:
            return "usable", detail, summary, None
        retry_at = max(exhausted_resets) + timedelta(seconds=RESET_BUFFER_SECONDS)
        return "official_reset", detail, summary, retry_at
    except urllib.error.HTTPError as exc:
        return "fallback", f"HTTP {exc.code}", {}, None
    except Exception as exc:  # network and provider response failures use fallback
        return "fallback", f"err {type(exc).__name__}: {exc}", {}, None


def _retry_at(state: dict) -> datetime | None:
    value = state.get("next_retry_at")
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=TZ)
    return parsed.astimezone(TZ)


def _wait_until(target: datetime, mode: str, deadline: datetime) -> str:
    while datetime.now(TZ) < target:
        if HALT.exists():
            return "halt"
        if datetime.now(TZ) > deadline:
            return "deadline"
        state = load_state()
        if state.get("status") not in WAITING_STATUSES:
            return "state_changed"
        state_mode = state.get("wait_mode") or state.get("quota_wait_mode")
        if state_mode != mode or _retry_at(state) != target:
            return "target_changed"
        remaining = (target - datetime.now(TZ)).total_seconds()
        time.sleep(min(WAIT_SLICE_SECONDS, max(1, remaining)))
    return "due"


def resume(tier: str) -> bool:
    if HALT.exists():
        return False
    state = load_state()
    if state.get("status") not in WAITING_STATUSES:
        return False
    state.update(status="running", resumed_at=datetime.now(TZ).isoformat(),
                 last_error=None, next_retry_at=None, quota_wait_mode=None,
                 wait_mode=None, resumed_by="quota-watch-resume.py")
    save_state(state)
    proc = subprocess.Popen(
        [sys.executable, str(ROOT / "scripts" / "supervise-pipeline.py"), tier],
        cwd=str(ROOT),
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
        | getattr(subprocess, "DETACHED_PROCESS", 0),
        close_fds=True,
    )
    log(f"[resume] 已啟動 supervise-pipeline.py tier={tier} pid={proc.pid}")
    return True


def _fallback_attempt(state: dict) -> int:
    value = state.get("retry_attempt", 0)
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else 0


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--tier", default="核心")
    parser.add_argument("--max-days", type=float, default=DEFAULT_MAX_DAYS)
    args = parser.parse_args()

    deadline = datetime.now(TZ) + timedelta(days=args.max_days)
    log(f"[start] quota-watch 啟動 official-reset + fallback=5/10/20/30m tier={args.tier} "
        f"deadline={deadline.strftime('%Y-%m-%d %H:%M')}")

    if load_state().get("status") not in WAITING_STATUSES:
        log("[exit] runtime state 並非 generation wait，無事可做，退出")
        return

    while True:
        if HALT.exists():
            log("[exit] 偵測人工 HALT，停止自動恢復")
            return
        if datetime.now(TZ) > deadline:
            log("[exit] 超過 max-days 安全上限仍未恢復，退出（請人工檢查 MiniMax 額度）")
            return
        state = load_state()
        if state.get("status") not in WAITING_STATUSES:
            log("[exit] 等待狀態已由其他程序解除")
            return
        waiting_status = state.get("status")
        mode = state.get("wait_mode") or state.get("quota_wait_mode")
        target = _retry_at(state)
        if mode in {"official_reset", "fallback"} and target is not None and target > datetime.now(TZ):
            wait_result = _wait_until(target, mode, deadline)
            if wait_result == "halt":
                log("[exit] 偵測人工 HALT，停止自動恢復")
                return
            if wait_result == "deadline":
                log("[exit] 超過 max-days 安全上限仍未恢復，退出（請人工檢查 MiniMax 額度）")
                return
            if wait_result != "due":
                continue

        outcome, detail, quota, retry_at = probe_quota()
        if HALT.exists():
            log("[exit] probe 完成時偵測人工 HALT，不改狀態")
            return
        state = load_state()
        if state.get("status") not in WAITING_STATUSES:
            log("[exit] probe 完成前等待狀態已由其他程序解除")
            return
        if quota:
            state["quota"] = quota
        if outcome == "usable":
            save_state(state)
            log(f"[detected] MiniMax 額度已恢復（{detail}），自動恢復管線")
            if resume(args.tier):
                log("[exit] 恢復完成，watcher 退出")
            else:
                log("[exit] 恢復前狀態改變，未啟動 supervisor")
            return
        if outcome == "official_reset" and retry_at is not None:
            state.update(status="waiting_quota", quota_wait_mode="official_reset",
                         wait_mode="official_reset", next_retry_at=retry_at.isoformat(),
                         retry_attempt=0, last_error=detail, failure_code="quota_reserve",
                         failure_scope="provider")
            if isinstance(state.get("handoff"), dict):
                state["handoff"].update(reason="quota_reserve",
                                        next_retry_at=retry_at.isoformat())
            save_state(state)
            log(f"[wait] 額度耗盡（{detail}），依官方 reset 單次等待至 {retry_at.isoformat()}")
            continue

        attempt = _fallback_attempt(state) if mode == "fallback" else 0
        delay = BACKOFF_SECONDS[min(attempt, len(BACKOFF_SECONDS) - 1)]
        next_retry = datetime.now(TZ) + timedelta(seconds=delay)
        next_status = "waiting_provider" if waiting_status == "waiting_provider" else "waiting_quota"
        state.update(status=next_status, quota_wait_mode="fallback", wait_mode="fallback",
                     retry_attempt=attempt + 1, next_retry_at=next_retry.isoformat(),
                     last_error=detail)
        if isinstance(state.get("handoff"), dict):
            state["handoff"]["next_retry_at"] = next_retry.isoformat()
        save_state(state)
        log(f"[wait] 官方 reset 不可用（{detail}），fallback {delay // 60} 分鐘後單次再探")


def acquire_pidfile() -> bool:
    """Allow only one quota watcher, while recovering a stale PID file."""
    for _ in range(2):
        if create_pid_lock(PIDFILE):
            return True
        try:
            pid = int(PIDFILE.read_text(encoding="utf-8").strip())
            os.kill(pid, 0)
            log(f"[locked] quota watcher 已在執行 pid={pid}，本程序退出")
            return False
        except (OSError, ValueError):
            PIDFILE.unlink(missing_ok=True)
    return False


if __name__ == "__main__":
    if not acquire_pidfile():
        sys.exit(0)
    try:
        main()
    finally:
        try:
            if PIDFILE.exists() and PIDFILE.read_text(encoding="utf-8").strip() == str(os.getpid()):
                PIDFILE.unlink()
        except OSError:
            pass
