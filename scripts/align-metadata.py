#!/usr/bin/env python
"""
0-token rule-based metadata alignment.

Fills is_original_language + text_role from the `language` field, HIGH-CONFIDENCE
buckets only. Ambiguous languages (e.g. Latin = Vulgate translation vs classical
original) are left untouched for the human/audit queue, per CLAUDE.md §3
「不確定的一律不自動標」.

Only edits meta.json (never raw/original.txt) so SHA-256 is preserved.

Usage:
  PYTHONIOENCODING=utf-8 python scripts/align-metadata.py            # dry-run (default)
  PYTHONIOENCODING=utf-8 python scripts/align-metadata.py --apply    # write changes
"""

import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRANSLATIONS_DIR = ROOT / "translations"

# High-confidence original languages -> (is_original_language=True, text_role="original")
ORIGINAL_LANGS = {
    "古典漢語",       # 佛/道/儒 漢傳原典
    "Hebrew", "希伯來",  # Tanakh / Talmud 原文
    "Pali",           # 巴利三藏
    "Sanskrit",       # 梵文原典
    "Koine Greek",    # 新約希臘原文
    "古典阿拉伯",      # 古蘭經
    "古典阿拉伯語",
}

# High-confidence translation languages -> (is_original_language=False, text_role="translation")
# Any language string containing these substrings is treated as a translation.
TRANSLATION_SUBSTR = (
    "English",   # 所有 English / English (translation) / English (Budge...) 皆譯本
    "古典中文",   # 和合本中譯（與「古典漢語」相反：中文但為譯文）
)

# Ambiguous -> never auto-fill (leave for human/audit queue)
AMBIGUOUS_LANGS = {
    "Latin",  # Vulgate=translation, 但古典拉丁原典=original，需逐部判
}


def classify(language: str):
    """Return (is_original, text_role) or (None, None) if ambiguous/unknown."""
    if language in AMBIGUOUS_LANGS:
        return None, None
    if language in ORIGINAL_LANGS:
        return True, "original"
    if any(s in language for s in TRANSLATION_SUBSTR):
        return False, "translation"
    return None, None  # unknown -> safe default, don't guess


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry-run)")
    args = ap.parse_args()

    changed_iol = 0
    changed_role = 0
    skipped_ambiguous = Counter()
    skipped_unknown = Counter()
    touched_files = 0

    for meta_p in sorted(TRANSLATIONS_DIR.glob("*/meta.json")):
        try:
            m = json.loads(meta_p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        lang = m.get("language") or ""
        is_orig, role = classify(lang)
        if is_orig is None:
            if lang in AMBIGUOUS_LANGS:
                skipped_ambiguous[lang] += 1
            elif m.get("is_original_language") is None or not m.get("text_role"):
                skipped_unknown[lang] += 1
            continue

        file_dirty = False
        # Backfill is_original_language only if missing (don't overwrite prior human calls).
        if m.get("is_original_language") is None:
            m["is_original_language"] = is_orig
            changed_iol += 1
            file_dirty = True
        # Backfill text_role only if empty.
        if not m.get("text_role"):
            m["text_role"] = role
            changed_role += 1
            file_dirty = True

        if file_dirty:
            touched_files += 1
            if args.apply:
                # Re-read fresh right before writing so a concurrent pipeline write
                # (semantic_tags / translation_status on the same file) is not clobbered.
                # Set only our two fields, and only if still empty.
                try:
                    fresh = json.loads(meta_p.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, OSError):
                    fresh = m
                if fresh.get("is_original_language") is None:
                    fresh["is_original_language"] = is_orig
                if not fresh.get("text_role"):
                    fresh["text_role"] = role
                meta_p.write_text(
                    json.dumps(fresh, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )

    mode = "APPLIED" if args.apply else "DRY-RUN (no files written)"
    print(f"[{mode}]")
    print(f"  files touched:            {touched_files}")
    print(f"  is_original_language set: {changed_iol}")
    print(f"  text_role set:            {changed_role}")
    print(f"  skipped (ambiguous lang): {sum(skipped_ambiguous.values())} {dict(skipped_ambiguous)}")
    print(f"  skipped (unknown lang, still empty): {sum(skipped_unknown.values())}")
    if skipped_unknown:
        for k, v in skipped_unknown.most_common(15):
            print(f"      {k!r}: {v}")


if __name__ == "__main__":
    main()
