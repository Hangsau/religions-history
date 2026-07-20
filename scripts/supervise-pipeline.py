#!/usr/bin/env python3
"""
supervise-pipeline.py — 讓 Pipeline B+C（翻譯+標籤）不再靜默停擺。

背景問題（2026-07-04 事故）：
  auto-pipeline.py 是一次性子進程，當初掛在互動 session 的背景 shell 底下；
  session 一關，OS 就把整棵進程樹收掉，翻譯永久停擺且無人察覺——GitHub 看似
  「有進展」其實只剩一支脫離式的收集爬蟲在爬週邊碎屑。

本 supervisor 負責：
  1. 反覆啟動 auto-pipeline，直到佇列跑完（stdout 出現 this_run=0）。
  2. auto-pipeline 異常退出（被殺 / crash）時自動重啟。
  3. 連續 MAX_QUICK_STRIKES 次「啟動後幾乎立刻退出」或連續 MAX_NOPROGRESS 輪
     「一部都沒 processed」→ 判定系統性問題（多半 M3 配額耗盡 / claude -p 端點異常），
     寫 logs/pipeline-alert.txt 並停止，不無限燒配額。
  4. 每輪寫心跳到 logs/supervisor.log。

正確啟動方式（脫離 session，撐得過關機視窗）：
  powershell Start-Process pythonw -ArgumentList 'scripts/supervise-pipeline.py' -WindowStyle Hidden
"""
import os
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from pipeline_lock import create_pid_lock

ROOT = Path(__file__).resolve().parent.parent
LOGS = ROOT / "logs"
LOGS.mkdir(exist_ok=True)
HEARTBEAT = LOGS / "supervisor.log"
ALERT = LOGS / "pipeline-alert.txt"
HALT = LOGS / "pipeline-HALT.flag"   # 人工暫停開關：存在即不啟動翻譯（刊版亦不復活）；刪除即恢復
RUNTIME = LOGS / "pipeline-runtime.json"
RUN_LOG = LOGS / "supervisor-run.log"
PIDFILE = LOGS / "supervisor.pid"  # 刊版靠此判斷 supervisor 是否還活著（避免重複拉起）

TIER = sys.argv[1] if len(sys.argv) > 1 else "核心"
TZ = timezone(timedelta(hours=8))

MAX_QUICK_STRIKES = 3   # 連續幾次「啟動後幾乎立刻退出」即判系統性問題
QUICK_SECONDS = 120     # 幾秒內退出算「立刻失敗」
MAX_NOPROGRESS = 2      # 連續幾輪「一部都沒 processed」即判系統性問題
BACKOFF_BASE = 30       # 重啟退避秒數（× strikes）


def hb(msg: str) -> None:
    line = f"{datetime.now(TZ).strftime('%Y-%m-%d %H:%M:%S')} {msg}"
    print(line, flush=True)
    with HEARTBEAT.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def alert(msg: str) -> None:
    ALERT.write_text(
        f"{datetime.now(TZ).strftime('%Y-%m-%d %H:%M:%S')} +0800\n{msg}\n",
        encoding="utf-8")
    hb(f"[ALERT] {msg}")


def run_once() -> tuple[int, int, int, float, int | None, int]:
    """Run once; return rc, queue count, processed, elapsed, retry wait, blocked count."""
    cmd = [sys.executable, str(ROOT / "scripts" / "auto-pipeline.py"), "--tier", TIER]
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUNBUFFERED": "1"}
    this_run, processed, retry_wait, blocked_only = -1, -1, None, 0
    start = time.time()
    with RUN_LOG.open("a", encoding="utf-8") as logf:
        logf.write(f"\n===== supervisor run @ {datetime.now(TZ)} =====\n")
        logf.flush()
        proc = subprocess.Popen(
            cmd, cwd=str(ROOT), env=env,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace",
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        for line in proc.stdout:
            logf.write(line)
            logf.flush()
            m = re.search(r"this_run=(\d+)", line)
            if m:
                this_run = int(m.group(1))
            m = re.search(r"done: processed (\d+)/", line)
            if m:
                processed = int(m.group(1))
            m = re.search(r"\[retry-wait\] next ordinary retry in (\d+)s", line)
            if m:
                retry_wait = int(m.group(1))
            m = re.search(r"\[blocked-only\] (\d+) blocked items", line)
            if m:
                blocked_only = int(m.group(1))
        proc.wait()
    return proc.returncode, this_run, processed, time.time() - start, retry_wait, blocked_only


def waiting_quota() -> bool:
    try:
        return json.loads(RUNTIME.read_text(encoding="utf-8")).get("status") == "waiting_quota"
    except (OSError, json.JSONDecodeError):
        return False


def start_quota_watcher() -> None:
    proc = subprocess.Popen(
        [sys.executable, str(ROOT / "scripts" / "quota-watch-resume.py"), "--tier", TIER],
        cwd=str(ROOT), creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
        | getattr(subprocess, "DETACHED_PROCESS", 0), close_fds=True)
    hb(f"[waiting_quota] 已啟動 quota watcher pid={proc.pid}，等待 M3 恢復")


def main() -> None:
    if HALT.exists():
        hb(f"[halt] 偵測到 {HALT.name}，人工暫停中，不啟動翻譯。刪除該檔即恢復。")
        return
    if ALERT.exists():
        ALERT.unlink()  # 新 supervisor 上線，清掉舊警報
    hb(f"[start] supervisor tier={TIER} pid={os.getpid()}")
    quick_strikes = 0
    noprogress = 0
    while True:
        if HALT.exists():
            hb(f"[halt] 偵測到 {HALT.name}，暫停迴圈退出。刪除該檔並重啟即恢復。")
            break
        rc, this_run, processed, elapsed, retry_wait, blocked_only = run_once()
        hb(f"[run] rc={rc} this_run={this_run} processed={processed} elapsed={elapsed:.0f}s")

        if HALT.exists():
            hb("[halt] worker 已在安全邊界退出，supervisor 不再啟動新一輪")
            break

        if waiting_quota():
            start_quota_watcher()
            break

        if this_run == 0 and retry_wait is not None:
            delay = max(5, min(retry_wait, 1800))
            hb(f"[retry-wait] 目前只有未到期的一般失敗；{delay}s 後重建佇列")
            time.sleep(delay)
            continue

        if this_run == 0 and blocked_only:
            hb(f"[blocked] {blocked_only} 部需人工修復後 --unblock；supervisor 正常退出")
            break

        if this_run == 0:
            hb("[done] 佇列已全部完成，supervisor 正常退出")
            break

        if processed == 0:
            noprogress += 1
            if noprogress >= MAX_NOPROGRESS:
                alert(f"連續 {noprogress} 輪一部都沒完成（this_run={this_run}）；"
                      f"多半 M3 配額耗盡或 claude -p 端點異常。已停止自動重啟，待人工處理。")
                break
        else:
            noprogress = 0

        if elapsed < QUICK_SECONDS and processed <= 0:
            quick_strikes += 1
            if quick_strikes >= MAX_QUICK_STRIKES:
                alert(f"連續 {quick_strikes} 次啟動後 <{QUICK_SECONDS}s 即退出（rc={rc}）；"
                      f"疑環境 / 端點問題。已停止自動重啟，待人工處理。")
                break
        else:
            quick_strikes = 0

        backoff = BACKOFF_BASE * max(1, quick_strikes)
        hb(f"[restart] {backoff}s 後重啟（quick_strikes={quick_strikes} noprogress={noprogress}）")
        time.sleep(backoff)

    hb("[exit] supervisor 結束")


def acquire_pidfile() -> bool:
    """Allow only one supervisor, while recovering a stale PID file."""
    for _ in range(2):
        if create_pid_lock(PIDFILE):
            return True
        try:
            pid = int(PIDFILE.read_text(encoding="utf-8").strip())
            os.kill(pid, 0)
            hb(f"[locked] supervisor 已在執行 pid={pid}，本程序退出")
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
                PIDFILE.unlink()  # 只清自己寫的那份，避免誤刪後繼者的
        except OSError:
            pass
