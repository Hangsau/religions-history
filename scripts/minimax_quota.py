"""Read MiniMax Coding Plan quota without exposing credentials or prompts."""

from __future__ import annotations

import json
import math
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

RESET_BUFFER_SECONDS = 15


def _percentage(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    return number if math.isfinite(number) and 0 <= number <= 100 else None


def _datetime_from_millis(value: object, tz: timezone) -> datetime | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        return None
    try:
        return datetime.fromtimestamp(number / 1000, tz)
    except (OSError, OverflowError, ValueError):
        return None


def probe_quota(token_path: Path, quota_url: str, tz: timezone,
                now: datetime | None = None, timeout: float = 30,
                interval_reserve: float = 5, weekly_reserve: float = 2
                ) -> tuple[str, str, dict, datetime | None]:
    """Return usable, official_reset, or fallback with an optional retry time.

    The reserve thresholds deliberately stop generation *before* the account reaches
    zero.  This avoids launching a chunk that cannot finish and leaves room for a
    clean checkpoint/handoff.
    """
    now = now or datetime.now(tz)
    if not token_path.exists():
        return "fallback", "no token file", {}, None
    token = token_path.read_text(encoding="utf-8").strip()
    req = urllib.request.Request(quota_url, method="GET", headers={
        "Authorization": f"Bearer {token}",
        "content-type": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        models = payload.get("model_remains", [])
        general = next((item for item in models if item.get("model_name") == "general"), None)
        if not isinstance(general, dict):
            return "fallback", "quota response missing general model", {
                "raw_status": payload.get("base_resp")}, None
        interval = _percentage(general.get("current_interval_remaining_percent"))
        weekly = _percentage(general.get("current_weekly_remaining_percent"))
        interval_reset = _datetime_from_millis(general.get("end_time"), tz)
        weekly_reset = _datetime_from_millis(general.get("weekly_end_time"), tz)
        summary = {
            "model": "general",
            "interval_remaining_percent": interval,
            "weekly_remaining_percent": weekly,
            "interval_reserve_percent": interval_reserve,
            "weekly_reserve_percent": weekly_reserve,
            "interval_resets_at": interval_reset.isoformat() if interval_reset else None,
            "weekly_resets_at": weekly_reset.isoformat() if weekly_reset else None,
            "interval_status": general.get("current_interval_status"),
            "weekly_status": general.get("current_weekly_status"),
            "checked_at": now.isoformat(),
        }
        if interval is None or weekly is None:
            return "fallback", "quota response has invalid percentages", summary, None
        reserve_resets = []
        if interval <= interval_reserve:
            if interval_reset is None or interval_reset <= now:
                return "fallback", "5h quota reset time missing or expired", summary, None
            reserve_resets.append(interval_reset)
        if weekly <= weekly_reserve:
            if weekly_reset is None or weekly_reset <= now:
                return "fallback", "weekly quota reset time missing or expired", summary, None
            reserve_resets.append(weekly_reset)
        detail = (f"5h={interval:g}% (reserve {interval_reserve:g}%) "
                  f"weekly={weekly:g}% (reserve {weekly_reserve:g}%)")
        if not reserve_resets:
            return "usable", detail, summary, None
        return ("official_reset", detail, summary,
                max(reserve_resets) + timedelta(seconds=RESET_BUFFER_SECONDS))
    except urllib.error.HTTPError as exc:
        return "fallback", f"HTTP {exc.code}", {}, None
    except Exception as exc:  # network and malformed provider responses fail open upstream
        return "fallback", f"err {type(exc).__name__}: {exc}", {}, None
