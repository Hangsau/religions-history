#!/usr/bin/env python
"""Summarize local pipeline throughput without exposing prompts or content."""

import argparse
import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
METRICS_PATH = ROOT / "logs" / "pipeline-metrics.jsonl"
TZ = timezone(timedelta(hours=8))


def load_events(path: Path, since: datetime) -> list[dict]:
    events = []
    if not path.exists():
        return events
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            event = json.loads(line)
            timestamp = datetime.fromisoformat(event["timestamp"])
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            continue
        if timestamp >= since:
            events.append(event)
    return events


def summarize(events: list[dict], hours: float) -> dict:
    attempts = [event for event in events if event.get("event", "attempt") == "attempt"]
    completed = [event for event in events if event.get("event") == "book_completed"]
    outcomes = Counter(event.get("outcome", "unknown") for event in attempts)
    elapsed_hours = max(hours, 1 / 3600)
    return {
        "window_hours": hours,
        "attempts": len(attempts),
        "outcomes": dict(sorted(outcomes.items())),
        "completed_books": len(completed),
        "completed_books_per_hour": round(len(completed) / elapsed_hours, 2),
        "successful_input_chars": sum(
            int(event.get("input_chars") or 0)
            for event in attempts if event.get("outcome") == "success"
        ),
        "resume_attempts": sum(bool(event.get("resumed")) for event in attempts),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hours", type=float, default=1.0)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.hours <= 0:
        parser.error("--hours must be greater than zero")
    now = datetime.now(TZ)
    result = summarize(load_events(METRICS_PATH, now - timedelta(hours=args.hours)), args.hours)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    print(f"window: {result['window_hours']:g}h")
    print(f"attempts: {result['attempts']}  outcomes: {result['outcomes']}")
    print(f"completed books: {result['completed_books']} ({result['completed_books_per_hour']}/h)")
    print(f"successful input chars: {result['successful_input_chars']}")
    print(f"resume attempts: {result['resume_attempts']}")


if __name__ == "__main__":
    main()
