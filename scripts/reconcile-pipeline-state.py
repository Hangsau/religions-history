#!/usr/bin/env python
"""Reconcile publishability with metadata without deleting user content.

Default is dry-run. `--apply` only downgrades false completion claims; it never
promotes a translation and never deletes translations or existing tag arrays.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRANSLATIONS_DIR = ROOT / "translations"
FAILED_RE = re.compile(r"<!--\s*CHUNK\s+\d+/\d+\s+FAILED\b", re.IGNORECASE)


def incomplete_translation(path: Path) -> bool:
    if not path.exists() or path.stat().st_size <= 100:
        return True
    try:
        return bool(FAILED_RE.search(path.read_text(encoding="utf-8", errors="replace")))
    except OSError:
        return True


def changes_for(meta: dict, translation_path: Path) -> dict:
    if meta.get("translation_status") != "done" or not incomplete_translation(translation_path):
        return {}
    changes = {"translation_status": "needs-review"}
    if meta.get("tag_status") == "done":
        changes["tag_status"] = "none"
    if meta.get("psych_tag_status") == "done":
        changes["psych_tag_status"] = "none"
    return changes


def _atomic_write_json(path: Path, payload: dict) -> None:
    fd, temp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass


def reconcile(translations_dir: Path = TRANSLATIONS_DIR, apply: bool = False) -> list[dict]:
    report = []
    for meta_path in sorted(translations_dir.glob("*/meta.json")):
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        slug = meta_path.parent.name
        changes = changes_for(meta, meta_path.parent / "01-translation.md")
        if not changes:
            continue
        report.append({"slug": slug, "changes": changes})
        if apply:
            meta.update(changes)
            _atomic_write_json(meta_path, meta)
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="apply safe downgrades")
    parser.add_argument("--json", action="store_true", help="machine-readable report")
    args = parser.parse_args()
    report = reconcile(apply=args.apply)
    if args.json:
        print(json.dumps({"applied": args.apply, "count": len(report), "items": report},
                         ensure_ascii=False, indent=2))
    else:
        mode = "APPLY" if args.apply else "DRY-RUN"
        print(f"{mode}: {len(report)} metadata records require safe downgrade")
        for item in report:
            fields = ", ".join(f"{key}={value}" for key, value in item["changes"].items())
            print(f"  {item['slug']}: {fields}")


if __name__ == "__main__":
    main()
