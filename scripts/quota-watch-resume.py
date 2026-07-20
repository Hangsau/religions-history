#!/usr/bin/env python3
"""MiniMax-M3 額度自動恢復 watcher。

背景常駐：週期性查 MiniMax Token Plan 的 remains API（不呼叫 LLM）。
- 額度為零 → 依 5 → 10 → 20 → 30 分鐘退避後再查。
- 額度回來 → 將 runtime state 切回 running、啟動 supervise-pipeline.py（detached）+ 記錄 + 自身退出。

只做二元偵測（MiniMax Anthropic 相容端點不回 ratelimit header，查不到實際 5H/7D 用量）。
不發任何通知。HALT flag 存在時停止自動恢復。

用法：pythonw scripts/quota-watch-resume.py [--tier 核心] [--max-days 天]
"""
from __future__ import annotations

import json
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

DEFAULT_MAX_DAYS = 10     # 安全上限：超過就自動退出，避免殭屍常駐
BACKOFF_SECONDS = (300, 600, 1200, 1800)


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


def _iso_from_millis(value: object) -> str | None:
    if not isinstance(value, (int, float)):
        return None
    return datetime.fromtimestamp(value / 1000, TZ).isoformat()


def probe_quota() -> tuple[bool, str, dict]:
    """讀官方 remains API，不產生 LLM 請求；回 (可恢復, 說明, 可刊版 quota 摘要)。"""
    if not MINIMAX_TOKEN_PATH.exists():
        return False, "no token file", {}
    token = MINIMAX_TOKEN_PATH.read_text(encoding="utf-8").strip()
    req = urllib.request.Request(QUOTA_URL, method="GET", headers={
        "Authorization": f"Bearer {token}",
        "content-type": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        models = payload.get("model_remains", [])
        general = next((item for item in models if item.get("model_name") == "general"), None)
        if not isinstance(general, dict):
            return False, "quota response missing general model", {"raw_status": payload.get("base_resp")}
        interval = general.get("current_interval_remaining_percent")
        weekly = general.get("current_weekly_remaining_percent")
        summary = {
            "model": "general",
            "interval_remaining_percent": interval,
            "weekly_remaining_percent": weekly,
            "interval_resets_at": _iso_from_millis(general.get("end_time")),
            "weekly_resets_at": _iso_from_millis(general.get("weekly_end_time")),
            "interval_status": general.get("current_interval_status"),
            "weekly_status": general.get("current_weekly_status"),
        }
        usable = isinstance(interval, (int, float)) and interval > 0 and isinstance(weekly, (int, float)) and weekly > 0
        detail = f"5h={interval}% weekly={weekly}%"
        return usable, detail, summary
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}", {}
    except Exception as e:  # noqa: BLE001 網路波動等，續等
        return False, f"err {type(e).__name__}: {e}", {}


def resume(tier: str) -> None:
    state = load_state()
    state.update(status="running", resumed_at=datetime.now(TZ).isoformat(),
                 last_error=None, next_retry_at=None)
    save_state(state)
    proc = subprocess.Popen(
        [sys.executable, str(ROOT / "scripts" / "supervise-pipeline.py"), tier],
        cwd=str(ROOT),
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
        | getattr(subprocess, "DETACHED_PROCESS", 0),
        close_fds=True,
    )
    log(f"[resume] 已啟動 supervise-pipeline.py tier={tier} pid={proc.pid}")


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--tier", default="核心")
    ap.add_argument("--max-days", type=float, default=DEFAULT_MAX_DAYS)
    args = ap.parse_args()

    deadline = datetime.now(TZ) + timedelta(days=args.max_days)
    log(f"[start] quota-watch 啟動 backoff=5/10/20/30m tier={args.tier} "
        f"deadline={deadline.strftime('%Y-%m-%d %H:%M')}")

    if load_state().get("status") != "waiting_quota":
        log("[exit] runtime state 並非 waiting_quota，無事可做，退出")
        return

    while True:
        if HALT.exists():
            log("[exit] 偵測人工 HALT，停止自動恢復")
            return
        if datetime.now(TZ) > deadline:
            log("[exit] 超過 max-days 安全上限仍未恢復，退出（請人工檢查 MiniMax 額度）")
            return
        state = load_state()
        if state.get("status") != "waiting_quota":
            log("[exit] 等待狀態已由其他程序解除")
            return
        retry_text = state.get("next_retry_at")
        if retry_text:
            try:
                retry_at = datetime.fromisoformat(retry_text)
                while datetime.now(TZ) < retry_at:
                    if HALT.exists():
                        log("[exit] 偵測人工 HALT，停止自動恢復")
                        return
                    time.sleep(min(30, max(1, (retry_at - datetime.now(TZ)).total_seconds())))
            except (TypeError, ValueError):
                pass
        attempt = int(state.get("retry_attempt", 0))
        delay = BACKOFF_SECONDS[min(attempt, len(BACKOFF_SECONDS) - 1)]
        next_retry = datetime.now(TZ) + timedelta(seconds=delay)
        state.update(retry_attempt=attempt + 1, next_retry_at=next_retry.isoformat())
        save_state(state)
        ok, detail, quota = probe_quota()
        state = load_state()
        state["quota"] = quota
        save_state(state)
        if ok:
            log(f"[detected] MiniMax 額度已恢復（{detail}），自動恢復管線")
            resume(args.tier)
            log("[exit] 恢復完成，watcher 退出")
            return
        state = load_state()
        state["last_error"] = detail
        save_state(state)
        log(f"[wait] 仍耗盡（{detail}），{delay // 60} 分鐘後再探")
        time.sleep(delay)


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
