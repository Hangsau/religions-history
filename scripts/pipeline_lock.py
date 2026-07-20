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


def acquire_run_lock() -> bool:
    for _ in range(2):
        if create_pid_lock(LOCK_PATH):
            return True
        try:
            pid = int(LOCK_PATH.read_text(encoding="utf-8").strip())
            os.kill(pid, 0)
            print(f"[locked] generation pipeline already running (pid={pid})")
            return False
        except (OSError, ValueError):
            LOCK_PATH.unlink(missing_ok=True)
    return False


def release_run_lock() -> None:
    try:
        if LOCK_PATH.read_text(encoding="utf-8").strip() == str(os.getpid()):
            LOCK_PATH.unlink()
    except OSError:
        pass
