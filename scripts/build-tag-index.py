#!/usr/bin/env python
"""
Pipeline C: build reverse indexes from every meta.json's semantic_tags + keywords.

Outputs:
    00-overview/tag-index.json      { tag: [ {slug, name_zh, religion}, ... ], ... }
    00-overview/keyword-index.json  { keyword: [ {slug, name_zh, religion}, ... ], ... }

These are the cross-scripture link structure: scriptures sharing a tag/keyword are related.

Usage:
    python scripts/build-tag-index.py
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRANSLATIONS_DIR = ROOT / "translations"
OVERVIEW_DIR = ROOT / "00-overview"


def build() -> tuple[dict, dict, int]:
    tag_index: dict[str, list] = defaultdict(list)
    kw_index: dict[str, list] = defaultdict(list)
    tagged = 0

    for meta_p in sorted(TRANSLATIONS_DIR.glob("*/meta.json")):
        try:
            meta = json.loads(meta_p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        sem = meta.get("semantic_tags") or []
        kw = meta.get("keywords") or []
        if not sem and not kw:
            continue
        tagged += 1
        entry = {
            "slug": meta.get("slug", meta_p.parent.name),
            "name_zh": meta.get("name_zh", ""),
            "religion": meta.get("religion", ""),
        }
        for t in sem:
            tag_index[t].append(entry)
        for k in kw:
            kw_index[k].append(entry)

    # sort keys; sort entries by slug for stable diffs
    tag_out = {t: sorted(v, key=lambda e: e["slug"]) for t, v in sorted(tag_index.items())}
    kw_out = {k: sorted(v, key=lambda e: e["slug"]) for k, v in sorted(kw_index.items())}
    return tag_out, kw_out, tagged


def main():
    tag_out, kw_out, tagged = build()
    OVERVIEW_DIR.mkdir(exist_ok=True)
    (OVERVIEW_DIR / "tag-index.json").write_text(
        json.dumps(tag_out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    (OVERVIEW_DIR / "keyword-index.json").write_text(
        json.dumps(kw_out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote tag-index.json ({len(tag_out)} tags) + keyword-index.json ({len(kw_out)} keywords)")
    print(f"  from {tagged} tagged scriptures")
    if tagged == 0:
        print("  (no scriptures tagged yet — run: python scripts/translate.py --core --task tag)")


if __name__ == "__main__":
    main()
