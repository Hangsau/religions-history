#!/usr/bin/env python
"""
Generate 00-overview/INDEX.json from all translations/<slug>/meta.json.

Provides:
- Total count
- By religion / tradition / language
- Total bytes
- Sortable list of all scriptures with key meta fields

Run after each batch of downloads.
"""

import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRANSLATIONS_DIR = ROOT / "translations"
OUT_PATH = ROOT / "00-overview" / "INDEX.json"
README_PATH = ROOT / "00-overview" / "INDEX.md"


def main():
    entries = []
    for meta_p in sorted(TRANSLATIONS_DIR.glob("*/meta.json")):
        try:
            m = json.loads(meta_p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        entries.append({
            "slug": m.get("slug"),
            "name_zh": m.get("name_zh"),
            "name_en": m.get("name_en"),
            "religion": m.get("religion"),
            "tradition": m.get("tradition"),
            "language": m.get("language"),
            "version": m.get("version"),
            "version_date": m.get("version_date"),
            "source_platform": m.get("source_platform"),
            "tier": m.get("tier"),
            "is_original_language": m.get("is_original_language"),
            "size_bytes": m.get("size_bytes"),
            "chapter_count": m.get("chapter_count"),
            "verified": m.get("verified"),
        })

    # Stats
    by_religion = Counter(e["religion"] or "unknown" for e in entries)
    by_tradition = Counter(f"{e['religion']} - {e['tradition']}" if e.get("tradition") else e["religion"] for e in entries)
    by_language = Counter(e["language"] or "unknown" for e in entries)
    by_source = Counter(e["source_platform"] or "unknown" for e in entries)
    total_bytes = sum((e["size_bytes"] or 0) for e in entries)
    verified_count = sum(1 for e in entries if e["verified"])
    original_count = sum(1 for e in entries if e["is_original_language"])

    summary = {
        "total_count": len(entries),
        "verified_count": verified_count,
        "original_language_count": original_count,
        "total_size_mb": round(total_bytes / 1024 / 1024, 1),
        "by_religion": dict(by_religion.most_common()),
        "by_tradition": dict(by_tradition.most_common()),
        "by_language": dict(by_language.most_common()),
        "by_source_platform": dict(by_source.most_common()),
    }

    out = {"summary": summary, "scriptures": entries}
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_bytes((json.dumps(out, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))

    # Generate readable markdown summary
    md_lines = []
    md_lines.append(f"# religions-history 資料庫索引\n")
    md_lines.append(f"> 自動產生 by `scripts/generate-index.py`\n")
    md_lines.append(f"\n## 統計總覽\n")
    md_lines.append(f"- 總計: **{summary['total_count']}** 部")
    md_lines.append(f"- 已驗證: {summary['verified_count']}")
    md_lines.append(f"- 原文 (vs 譯文): {summary['original_language_count']} / {summary['total_count']}")
    md_lines.append(f"- 總大小: ~{summary['total_size_mb']} MB\n")

    md_lines.append("## 按宗教\n")
    md_lines.append("| 宗教 | 部數 |")
    md_lines.append("|------|------|")
    for r, c in summary["by_religion"].items():
        md_lines.append(f"| {r} | {c} |")

    md_lines.append("\n## 按傳統 (宗教 - 傳統)\n")
    md_lines.append("| 傳統 | 部數 |")
    md_lines.append("|------|------|")
    for t, c in summary["by_tradition"].items():
        if c >= 2:  # filter noise
            md_lines.append(f"| {t} | {c} |")

    md_lines.append("\n## 按來源平台\n")
    md_lines.append("| 來源 | 部數 |")
    md_lines.append("|------|------|")
    for s, c in summary["by_source_platform"].items():
        md_lines.append(f"| {s} | {c} |")

    md_lines.append("\n## 全部經文清單 (slug, religion, size)\n")
    md_lines.append("| slug | 中文名 | 宗教 | 大小 (bytes) |")
    md_lines.append("|------|--------|------|------|")
    for e in sorted(entries, key=lambda x: (x["religion"] or "", x["slug"] or "")):
        md_lines.append(f"| `{e['slug']}` | {e['name_zh']} | {e['religion']} | {e['size_bytes']} |")

    README_PATH.write_bytes(("\n".join(md_lines) + "\n").encode("utf-8"))
    print(f"wrote {OUT_PATH} + {README_PATH}")
    print(f"  total: {summary['total_count']} / {summary['total_size_mb']} MB / {len(summary['by_religion'])} religions")


if __name__ == "__main__":
    main()
