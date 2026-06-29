#!/usr/bin/env python
"""
Verify a downloaded scripture meets its meta.json declaration.

Usage:
    python scripts/verify.py --slug tao-te-ching
    python scripts/verify.py --all

Exit code 0 if PASS, 1 if any FAIL.

Checks (each scripture):
    1. translations/<slug>/raw/original.txt exists
    2. SHA-256 of original.txt matches meta.json checksum_sha256
    3. byte size matches meta.json size_bytes
    4. detected chapter count matches meta.json chapter_count
    5. if meta has expected_chapter_count, chapter_count == expected
    6. if meta has expected_size_min / expected_size_max, size within range
    7. meta.json schema (required fields present, basic type sanity)

Updates meta.json verified=true on PASS.
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRANSLATIONS_DIR = ROOT / "translations"
CHAPTER_SEP_RE = re.compile(r"^=== \d+ \|", re.MULTILINE)

REQUIRED_META_FIELDS = [
    "slug", "name_zh", "name_en", "name_original", "religion", "language",
    "version", "version_date", "source_platform", "source_url",
    "downloaded_at", "size_bytes", "checksum_sha256", "chapter_count",
    "license", "verified",
]


def verify_one(slug: str) -> tuple[bool, list[str]]:
    """Verify a single scripture. Returns (passed, [reasons])."""
    reasons: list[str] = []
    base = TRANSLATIONS_DIR / slug
    meta_path = base / "meta.json"
    original_path = base / "raw" / "original.txt"

    if not meta_path.exists():
        return False, [f"meta.json missing: {meta_path}"]
    if not original_path.exists():
        return False, [f"original.txt missing: {original_path}"]

    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return False, [f"meta.json invalid JSON: {e}"]

    for f in REQUIRED_META_FIELDS:
        if f not in meta:
            reasons.append(f"meta missing required field: {f}")

    text_bytes = original_path.read_bytes()
    actual_size = len(text_bytes)
    actual_sha = hashlib.sha256(text_bytes).hexdigest()
    text = text_bytes.decode("utf-8")
    actual_chapters = len(CHAPTER_SEP_RE.findall(text))

    if meta.get("size_bytes") != actual_size:
        reasons.append(f"size mismatch: meta={meta.get('size_bytes')} actual={actual_size}")
    if meta.get("checksum_sha256") != actual_sha:
        reasons.append(f"sha256 mismatch: meta={meta.get('checksum_sha256')[:16]}... actual={actual_sha[:16]}...")
    if meta.get("chapter_count") != actual_chapters:
        reasons.append(f"chapter count mismatch: meta={meta.get('chapter_count')} actual={actual_chapters}")

    expected = meta.get("expected_chapter_count")
    if expected is not None and actual_chapters != expected:
        reasons.append(f"expected {expected} chapters, got {actual_chapters}")

    e_min = meta.get("expected_size_min")
    e_max = meta.get("expected_size_max")
    if e_min is not None and actual_size < e_min:
        reasons.append(f"size {actual_size} below expected min {e_min}")
    if e_max is not None and actual_size > e_max:
        reasons.append(f"size {actual_size} above expected max {e_max}")

    passed = not reasons
    if passed and not meta.get("verified"):
        meta["verified"] = True
        meta_path.write_bytes((json.dumps(meta, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    return passed, reasons


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--slug")
    p.add_argument("--all", action="store_true")
    args = p.parse_args()

    if args.slug:
        slugs = [args.slug]
    elif args.all:
        slugs = sorted([d.name for d in TRANSLATIONS_DIR.iterdir() if d.is_dir() and (d / "meta.json").exists()])
        if not slugs:
            print("no scriptures with meta.json found")
            sys.exit(0)
    else:
        p.print_help()
        sys.exit(2)

    any_fail = False
    for s in slugs:
        ok, reasons = verify_one(s)
        if ok:
            print(f"PASS  {s}")
        else:
            any_fail = True
            print(f"FAIL  {s}")
            for r in reasons:
                print(f"      - {r}")

    sys.exit(1 if any_fail else 0)


if __name__ == "__main__":
    main()
