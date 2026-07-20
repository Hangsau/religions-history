#!/usr/bin/env python
"""Versioned ordinary-failure state for the translation pipeline.

Quota waiting is deliberately excluded: it lives in pipeline-runtime.json and
must never consume ordinary retry attempts.
"""
from __future__ import annotations

import json
import os
import re
import tempfile
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable

from pipeline_lock import create_pid_lock

ROOT = Path(__file__).resolve().parent.parent
FAILED_PATH = ROOT / "logs" / "pipeline-failed.json"
UPDATE_LOCK = ROOT / "logs" / "pipeline-failed.lock"
SCHEMA_VERSION = 2
RETRY_DELAYS = (300, 900, 1800)  # three retries: 5m, 15m, 30m
SLUG_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_LOCAL_UPDATE_LOCK = threading.Lock()


def empty_state() -> dict:
    return {"schema_version": SCHEMA_VERSION, "failures": {}}


def _parse_time(value: object) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(str(value))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return None


def _validate_v2_failures(failures: dict) -> None:
    for slug, entry in failures.items():
        if not isinstance(slug, str) or not SLUG_RE.fullmatch(slug):
            raise ValueError(f"invalid failed-state slug: {slug!r}")
        if not isinstance(entry, dict):
            raise ValueError(f"failed-state entry must be an object: {slug}")
        status = entry.get("status")
        if status not in {"retryable", "blocked"}:
            raise ValueError(f"invalid failed-state status for {slug}: {status!r}")
        attempts = entry.get("attempts")
        if isinstance(attempts, bool) or not isinstance(attempts, int) or attempts < 0:
            raise ValueError(f"invalid failed-state attempts for {slug}: {attempts!r}")
        for key in ("first_failed_at", "last_failed_at"):
            if _parse_time(entry.get(key)) is None:
                raise ValueError(f"invalid failed-state {key} for {slug}")
        next_retry = entry.get("next_retry_at")
        if status == "retryable" and _parse_time(next_retry) is None:
            raise ValueError(f"retryable failed-state entry lacks next_retry_at: {slug}")
        if status == "blocked" and next_retry is not None:
            raise ValueError(f"blocked failed-state entry has next_retry_at: {slug}")
        for key in ("tier", "task", "error_code", "last_error"):
            if not isinstance(entry.get(key), str):
                raise ValueError(f"invalid failed-state {key} for {slug}")


def migrate(payload: object) -> tuple[dict, bool]:
    """Return canonical v2 state and whether an on-disk rewrite is needed."""
    if payload in (None, {}):
        return empty_state(), payload != empty_state()
    if not isinstance(payload, dict):
        raise ValueError("failed state must be a JSON object")
    if payload.get("schema_version") == SCHEMA_VERSION:
        failures = payload.get("failures")
        if not isinstance(failures, dict):
            raise ValueError("failed state v2 requires an object 'failures'")
        _validate_v2_failures(failures)
        return {"schema_version": SCHEMA_VERSION, "failures": failures}, False
    if "schema_version" in payload:
        raise ValueError(f"unsupported failed state schema: {payload.get('schema_version')}")

    migrated = empty_state()
    for slug, old in payload.items():
        if not SLUG_RE.fullmatch(str(slug)) or not isinstance(old, dict):
            continue
        parsed_at = _parse_time(old.get("at"))
        at = (parsed_at or datetime.now(timezone.utc)).isoformat()
        migrated["failures"][slug] = {
            "status": "retryable",
            "attempts": 1,
            "first_failed_at": at,
            "last_failed_at": at,
            "next_retry_at": at,
            "tier": str(old.get("tier", "核心")),
            "task": str(old.get("task", "pipeline")),
            "error_code": str(old.get("error_code", "legacy_failure")),
            "last_error": str(old.get("last_error", "migrated from failed-state v1")),
        }
    return migrated, True


def load(path: Path = FAILED_PATH) -> tuple[dict, bool]:
    if not path.exists():
        return empty_state(), False
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"malformed failed state: {exc}") from exc
    return migrate(payload)


def _atomic_write(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(state, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass


def save(state: dict, path: Path = FAILED_PATH) -> None:
    canonical, _ = migrate(state)
    _atomic_write(path, canonical)


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _acquire_update_lock(path: Path, timeout: float = 5.0) -> None:
    deadline = time.monotonic() + timeout
    path.parent.mkdir(parents=True, exist_ok=True)
    while True:
        if create_pid_lock(path):
            return
        try:
            owner = int(path.read_text(encoding="utf-8").strip())
        except (OSError, ValueError):
            owner = 0
        if not owner or not _pid_alive(owner):
            path.unlink(missing_ok=True)
            continue
        if time.monotonic() >= deadline:
            raise TimeoutError(f"failed-state update lock held by pid={owner}")
        time.sleep(0.05)


def update(mutator: Callable[[dict], None], path: Path = FAILED_PATH,
           lock_path: Path = UPDATE_LOCK) -> dict:
    with _LOCAL_UPDATE_LOCK:
        _acquire_update_lock(lock_path)
        try:
            state, _ = load(path)
            mutator(state)
            save(state, path)
            return state
        finally:
            try:
                if lock_path.exists() and lock_path.read_text(encoding="utf-8").strip() == str(os.getpid()):
                    lock_path.unlink()
            except OSError:
                pass


def record_failure(slug: str, tier: str, task: str, error_code: str,
                   last_error: str, now: datetime | None = None,
                   path: Path = FAILED_PATH, lock_path: Path = UPDATE_LOCK) -> dict:
    if not SLUG_RE.fullmatch(slug):
        raise ValueError(f"invalid slug: {slug!r}")
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    result = {}

    def mutate(state: dict) -> None:
        nonlocal result
        old = state["failures"].get(slug, {})
        attempts = int(old.get("attempts", 0)) + 1
        first = old.get("first_failed_at") or now.isoformat()
        if attempts <= len(RETRY_DELAYS):
            status = "retryable"
            next_retry = (now + timedelta(seconds=RETRY_DELAYS[attempts - 1])).isoformat()
        else:
            status = "blocked"
            next_retry = None
        result = {
            "status": status,
            "attempts": attempts,
            "first_failed_at": first,
            "last_failed_at": now.isoformat(),
            "next_retry_at": next_retry,
            "tier": tier,
            "task": task,
            "error_code": error_code,
            "last_error": str(last_error)[:1000],
        }
        state["failures"][slug] = result

    update(mutate, path, lock_path)
    return result


def clear_failure(slug: str, path: Path = FAILED_PATH, lock_path: Path = UPDATE_LOCK) -> None:
    update(lambda state: state["failures"].pop(slug, None), path, lock_path)


def unblock(slug: str, translations_dir: Path, path: Path = FAILED_PATH,
            lock_path: Path = UPDATE_LOCK, now: datetime | None = None) -> None:
    if not SLUG_RE.fullmatch(slug) or not (translations_dir / slug / "meta.json").exists():
        raise ValueError(f"unknown or unsafe canonical slug: {slug!r}")
    now = now or datetime.now(timezone.utc)

    def mutate(state: dict) -> None:
        entry = state["failures"].get(slug)
        if not entry:
            raise ValueError(f"slug is not failed: {slug}")
        entry.update(status="retryable", attempts=0, next_retry_at=now.isoformat(),
                     last_error="manually unblocked")

    update(mutate, path, lock_path)


def is_due(entry: dict, now: datetime | None = None) -> bool:
    if entry.get("status") != "retryable":
        return False
    parsed = _parse_time(entry.get("next_retry_at"))
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    return parsed is None or parsed <= current


def next_retry_delay(state: dict, tier: str, now: datetime | None = None) -> float | None:
    current = now or datetime.now(timezone.utc)
    times = []
    for entry in state.get("failures", {}).values():
        if entry.get("tier") != tier or entry.get("status") != "retryable":
            continue
        parsed = _parse_time(entry.get("next_retry_at"))
        if parsed:
            times.append(max(0.0, (parsed - current).total_seconds()))
        else:
            times.append(0.0)
    return min(times) if times else None
