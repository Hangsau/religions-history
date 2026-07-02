#!/usr/bin/env python
"""
Audit the tier=核心 corpus: per religion, how many core scriptures exist and
how many are translated / tagged. Flags religions in the schema enum that have
zero core texts (collection gaps, e.g. 神道).

The 核心 designation lives in each meta.json `tier` field (source of truth).
The v3 methodology (per-religion-scriptures.md) is prose and not machine-parsed;
gap-filling against it stays a manual review pointer.

Usage:
    python scripts/audit-core.py          # writes 00-overview/core-manifest.md
"""

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRANSLATIONS_DIR = ROOT / "translations"
OVERVIEW_DIR = ROOT / "00-overview"
MANIFEST_PATH = OVERVIEW_DIR / "core-manifest.md"

# religions declared in meta_template.json enum — used to detect zero-core gaps
ALL_RELIGIONS = [
    "佛教", "道教", "儒教", "印度教", "耆那教", "錫克教", "猶太教", "基督教",
    "伊斯蘭", "巴哈伊", "瑣羅亞斯德", "神道", "兩河", "古埃及", "古希臘羅馬",
    "北歐", "凱爾特", "斯拉夫", "赫爾墨斯", "諾斯底", "非洲", "瑪雅",
    "阿茲特克", "印加", "現代新興",
]


# Name/title markers that hint a text may be a phonetic transliteration (音譯),
# not a meaning-bearing translatable text. Flagged for manual text_role review so the
# pipeline doesn't vernacular-translate a dhāraṇī. Detection is advisory, never auto-classifies.
_TRANSLIT_HINTS = ("咒", "陀羅尼", "真言", "神咒", "dharani", "dhāraṇī",
                   "mantra", "曼怛羅", "明咒")


def _suspect_transliteration(meta: dict) -> bool:
    if meta.get("text_role"):  # already classified → not a pending suspect
        return False
    hay = " ".join(str(meta.get(k, "")) for k in ("name_zh", "name_en", "name_original", "slug")).lower()
    return any(h.lower() in hay for h in _TRANSLIT_HINTS)


def main():
    by_religion: dict[str, list[dict]] = defaultdict(list)
    religions_in_corpus: set[str] = set()
    translit_suspects: list[dict] = []
    role_counts: dict[str, int] = defaultdict(int)
    for meta_p in sorted(TRANSLATIONS_DIR.glob("*/meta.json")):
        try:
            meta = json.loads(meta_p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        rel = meta.get("religion", "?")
        religions_in_corpus.add(rel)
        if meta.get("tier") != "核心":
            continue
        slug = meta_p.parent.name
        role_counts[meta.get("text_role") or "(未標)"] += 1
        if _suspect_transliteration(meta):
            translit_suspects.append({"slug": slug, "name_zh": meta.get("name_zh", ""),
                                      "religion": rel})
        tr_done = (TRANSLATIONS_DIR / slug / "01-translation.md").exists()
        tag_done = bool(meta.get("tag_status") == "done" and meta.get("semantic_tags"))
        by_religion[rel].append({
            "slug": slug,
            "name_zh": meta.get("name_zh", ""),
            "language": meta.get("language", ""),
            "translated": tr_done,
            "tagged": tag_done,
        })

    total = sum(len(v) for v in by_religion.values())
    tr_total = sum(1 for v in by_religion.values() for e in v if e["translated"])
    tag_total = sum(1 for v in by_religion.values() for e in v if e["tagged"])

    lines = [
        "# 核心經文清單（core-manifest）",
        "",
        "> 由 `scripts/audit-core.py` 自動產生。核心 = `meta.json` 的 `tier == 核心`。",
        "",
        f"- 核心總數：**{total}** 部",
        f"- 已翻譯：**{tr_total}** / {total}",
        f"- 已標籤：**{tag_total}** / {total}",
        "",
        "## 各宗教核心進度",
        "",
        "| 宗教 | 核心數 | 已譯 | 已標籤 |",
        "|------|-------|------|-------|",
    ]
    for rel in sorted(by_religion, key=lambda r: -len(by_religion[r])):
        v = by_religion[rel]
        tr = sum(1 for e in v if e["translated"])
        tg = sum(1 for e in v if e["tagged"])
        lines.append(f"| {rel} | {len(v)} | {tr} | {tg} |")

    # distinguish true content gaps (absent from corpus) from tier-labelling gaps
    absent = [r for r in ALL_RELIGIONS if r not in religions_in_corpus]
    no_core_but_present = [r for r in religions_in_corpus
                           if r not in by_religion and r != "?"]
    lines += [
        "",
        "## 缺口分析",
        "",
        "### A. 語料庫完全沒有（真內容缺口，需補抓 / 寫爬蟲）",
        "",
        "> schema enum 有此宗教但語料庫一部都沒有。神道需另寫 NDL 爬蟲。",
        "> 註：schema 把美洲細分為瑪雅/阿茲特克/印加、赫爾墨斯獨立，但語料庫用較粗的『美洲』『諾斯底』歸類，故此清單含分類折疊項，非全為真缺口。",
        "",
    ]
    lines += ([f"- **{r}**" for r in absent] or ["- （無）"])
    lines += [
        "",
        "### B. 有經文但無核心標記（只需補標 tier，不需下載）",
        "",
    ]
    lines += ([f"- **{r}**" for r in sorted(no_core_but_present)] or ["- （無）"])

    # text_role coverage + transliteration safety net
    lines += [
        "",
        "## text_role 分類覆蓋",
        "",
        "> `original`/`translation`/`transliteration`/`contested`；`(未標)` = 尚未判定，"
        "翻譯管線按 `language` 走安全預設（原文原樣保留 / 外語直譯），不臆測。",
        "",
        "| text_role | 核心部數 |",
        "|-----------|---------|",
    ]
    for role in ("original", "translation", "transliteration", "contested", "(未標)"):
        if role_counts.get(role):
            lines.append(f"| {role} | {role_counts[role]} |")

    lines += [
        "",
        "### 疑似音譯 / 咒語，待人工確認 text_role",
        "",
        "> 標題含 咒 / 陀羅尼 / 真言 / mantra 等且尚未標 text_role。"
        "音譯文本禁意譯，需人工確認後標 `text_role: transliteration`，翻譯管線才會原樣保留。",
        "",
    ]
    lines += ([f"- `{e['slug']}` {e['name_zh']}（{e['religion']}）" for e in translit_suspects]
              or ["- （無）"])

    lines += ["", "## 各宗教核心明細", ""]
    for rel in sorted(by_religion, key=lambda r: -len(by_religion[r])):
        lines.append(f"### {rel}（{len(by_religion[rel])} 部）")
        lines.append("")
        for e in sorted(by_religion[rel], key=lambda x: x["slug"]):
            tr = "譯✓" if e["translated"] else "譯–"
            tg = "標✓" if e["tagged"] else "標–"
            lines.append(f"- `{e['slug']}` {e['name_zh']}（{e['language']}）{tr} {tg}")
        lines.append("")

    OVERVIEW_DIR.mkdir(exist_ok=True)
    MANIFEST_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {MANIFEST_PATH.relative_to(ROOT)}")
    print(f"  核心 {total} / 已譯 {tr_total} / 已標籤 {tag_total}")
    if absent:
        print(f"  語料庫缺口: {', '.join(absent)}")
    if no_core_but_present:
        print(f"  有經文但無核心標記: {', '.join(sorted(no_core_but_present))}")
    if translit_suspects:
        print(f"  疑似音譯待確認 text_role: {len(translit_suspects)} 部 "
              f"({', '.join(e['slug'] for e in translit_suspects[:8])})")


if __name__ == "__main__":
    main()
