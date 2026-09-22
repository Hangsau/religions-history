"""Shared single-instance lock for every MiniMax generation entrypoint."""

import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCK_PATH = ROOT / "logs" / "auto-pipeline.lock"


def create_pid_lock(path: Path) -> bool:
    """Atomically publish a PID lock whose owner is never partially written."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".lock", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(str(os.getpid()))
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temp_name, path)
            return True
        except FileExistsError:
            return False
    finally:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass


def pid_alive(pid: int) -> bool:
    """Windows 上不可用 `os.kill(pid, 0)` 探活。

    CPython 的 Windows os.kill 走 OpenProcess(PROCESS_ALL_ACCESS)，對 deskboard 以
    DETACHED_PROCESS 派出的 pythonw（supervisor / auto-pipeline）會拋 WinError 87，
    跟「PID 不存在」長得一模一樣。2026-09-23 實測：四個確實在跑的 pid 全被判成
    dead，鎖被當殘留刪掉，同一本書於是跑了兩個 auto-pipeline —— 正是 CLAUDE.md
    明令禁止的「同源並行雙跑」。

    判不出來時一律回 True：寧可多擋一次啟動，也不要放行第二個生成程序。
    """
    if os.name == "nt":
        import ctypes
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        ERROR_INVALID_PARAMETER = 87
        STILL_ACTIVE = 259
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not handle:
            return kernel32.GetLastError() != ERROR_INVALID_PARAMETER
        try:
            code = ctypes.c_ulong()
            if kernel32.GetExitCodeProcess(handle, ctypes.byref(code)):
                return code.value == STILL_ACTIVE
            return True
        finally:
            kernel32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except OSError:
        return True
    return True


def acquire_run_lock() -> bool:
    for _ in range(2):
        if create_pid_lock(LOCK_PATH):
            return True
        try:
            pid = int(LOCK_PATH.read_text(encoding="utf-8").strip())
        except (OSError, ValueError):
            LOCK_PATH.unlink(missing_ok=True)
            continue
        if pid_alive(pid):
            print(f"[locked] generation pipeline already running (pid={pid})")
            return False
        LOCK_PATH.unlink(missing_ok=True)
    return False


def release_run_lock() -> None:
    try:
        if LOCK_PATH.read_text(encoding="utf-8").strip() == str(os.getpid()):
            LOCK_PATH.unlink()
    except OSError:
        pass
