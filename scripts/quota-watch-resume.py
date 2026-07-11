#!/usr/bin/env python3
"""MiniMax-M3 額度自動恢復 watcher。

背景常駐：週期性用最小請求探測 MiniMax primary 端點。
- 429（額度耗盡）→ 睡 INTERVAL 後再探。
- 200（額度回來）→ 刪 logs/pipeline-HALT.flag + 啟動 supervise-pipeline.py（detached）+ 記錄 + 自身退出。

只做二元偵測（MiniMax Anthropic 相容端點不回 ratelimit header，查不到實際 5H/7D 用量）。
不發任何通知。若 HALT flag 已被人工刪除（有人先手動恢復），視為已處理，直接退出不重複啟動。

用法：pythonw scripts/quota-watch-resume.py [--interval 秒] [--tier 核心] [--max-days 天]
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOGS = ROOT / "logs"
HALT = LOGS / "pipeline-HALT.flag"
WATCH_LOG = LOGS / "quota-watch.log"
MINIMAX_TOKEN_PATH = Path.home() / ".minimax-token"
MINIMAX_URL = "https://api.minimax.io/anthropic/v1/messages"
PRIMARY_MODEL = "MiniMax-M3"
TZ = timezone(timedelta(hours=8))

DEFAULT_INTERVAL = 1200   # 20 分鐘探一次（429 免費、200 只花 ~16 token）
DEFAULT_MAX_DAYS = 10     # 安全上限：超過就自動退出，避免殭屍常駐


def log(msg: str) -> None:
    line = f"{datetime.now(TZ).strftime('%Y-%m-%d %H:%M:%S')} {msg}"
    print(line, flush=True)
    LOGS.mkdir(exist_ok=True)
    with WATCH_LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def probe_ok() -> tuple[bool, str]:
    """回 (額度是否可用, 說明)。200=可用；429=耗盡；其他/網路錯=暫視為不可用續等。"""
    if not MINIMAX_TOKEN_PATH.exists():
        return False, "no token file"
    token = MINIMAX_TOKEN_PATH.read_text(encoding="utf-8").strip()
    body = json.dumps({
        "model": PRIMARY_MODEL,
        "max_tokens": 16,
        "messages": [{"role": "user", "content": "ping"}],
    }).encode("utf-8")
    req = urllib.request.Request(MINIMAX_URL, data=body, method="POST", headers={
        "x-api-key": token,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status == 200, f"HTTP {resp.status}"
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}"  # 429 = 仍耗盡
    except Exception as e:  # noqa: BLE001 網路波動等，續等
        return False, f"err {type(e).__name__}: {e}"


def resume(tier: str) -> None:
    if HALT.exists():
        HALT.unlink()
        log(f"[resume] 已刪除 {HALT.name}")
    else:
        log(f"[resume] {HALT.name} 已不存在（人工先恢復？），仍續啟 supervisor")
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
    ap.add_argument("--interval", type=int, default=DEFAULT_INTERVAL)
    ap.add_argument("--tier", default="核心")
    ap.add_argument("--max-days", type=float, default=DEFAULT_MAX_DAYS)
    args = ap.parse_args()

    deadline = datetime.now(TZ) + timedelta(days=args.max_days)
    log(f"[start] quota-watch 啟動 interval={args.interval}s tier={args.tier} "
        f"deadline={deadline.strftime('%Y-%m-%d %H:%M')}")

    if not HALT.exists():
        log("[exit] 啟動時 HALT flag 就不存在（管線未暫停），無事可做，退出")
        return

    while True:
        if datetime.now(TZ) > deadline:
            log("[exit] 超過 max-days 安全上限仍未恢復，退出（請人工檢查 MiniMax 額度）")
            return
        ok, detail = probe_ok()
        if ok:
            log(f"[detected] MiniMax 額度已恢復（{detail}），自動恢復管線")
            resume(args.tier)
            log("[exit] 恢復完成，watcher 退出")
            return
        log(f"[wait] 仍耗盡（{detail}），{args.interval}s 後再探")
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
