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
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRANSLATIONS_DIR = ROOT / "translations"
OVERVIEW_DIR = ROOT / "00-overview"
MANIFEST_PATH = OVERVIEW_DIR / "core-manifest.md"
ORIGINAL_TODO_PATH = OVERVIEW_DIR / "original-text-todo.md"
# Cores already investigated to have no cleanly-collectable original (hard source-access
# block, no single底本, or oral/no-script tradition). Documented per-slug with probed sources
# so the 待補 list separates "collectable, not yet done" from "verified no clean source".
SOURCE_STATUS_PATH = ROOT / "scripts" / "catalog" / "original-source-status.json"
_STATUS_LABELS = {
    "blocked-access": "來源受牆／無乾淨匯出（原文存於已知數位語料庫但存取受阻）",
    "no-single-original": "英/西譯為學術彙編或選集，無單一底本",
    "oral-no-script": "口傳傳統，無文字書寫系統（採錄本即最早可及形式）",
}


def _load_source_status() -> dict:
    if not SOURCE_STATUS_PATH.exists():
        return {}
    try:
        return json.loads(SOURCE_STATUS_PATH.read_text(encoding="utf-8")).get("statuses", {})
    except (json.JSONDecodeError, OSError):
        return {}

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
    if meta.get("composition_note"):  # already manually reviewed, rationale recorded
        return False
    hay = " ".join(str(meta.get(k, "")) for k in ("name_zh", "name_en", "name_original", "slug")).lower()
    return any(h.lower() in hay for h in _TRANSLIT_HINTS)


# Content-truth guard (2026-07-03): the sole-source (待補原文) list used to trust the
# metadata label alone, which created phantom entries — e.g. homer-greek is 99% Greek
# text on disk but was labelled "English translation" and so kept resurfacing as
# "needs original". This reads the actual bytes: fraction of alphabetic characters that
# are NON-Latin script. A file that carries substantial Greek/Cyrillic/Devanagari/Han/
# Arabic/Hebrew/Coptic/cuneiform already contains its original and is NOT 待補.
# Limitation: originals in Latin script (Old Norse, Welsh, Nahuatl, romanized Avestan,
# Latin Vulgate) read ~0 non-Latin, so this only rescues non-Latin-script originals —
# which is exactly where the label bug bit. Latin-script cases stay label-dependent.
NATIVE_SCRIPT_MIN = 0.15
_LATIN_RANGES = ((0x0041, 0x005A), (0x0061, 0x007A), (0x00C0, 0x024F), (0x1E00, 0x1EFF))


def _is_latin_letter(o: int) -> bool:
    return any(lo <= o <= hi for lo, hi in _LATIN_RANGES)


def _native_script_ratio(slug: str) -> float:
    """Fraction of alphabetic chars in original.txt that are non-Latin script."""
    p = TRANSLATIONS_DIR / slug / "raw" / "original.txt"
    if not p.exists():
        return 0.0
    try:
        txt = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return 0.0
    latin = nonlatin = 0
    for ch in txt:
        o = ord(ch)
        if _is_latin_letter(o):
            latin += 1
        elif unicodedata.category(ch).startswith("L"):
            nonlatin += 1
    tot = latin + nonlatin
    return (nonlatin / tot) if tot else 0.0


def main():
    by_religion: dict[str, list[dict]] = defaultdict(list)
    religions_in_corpus: set[str] = set()
    translit_suspects: list[dict] = []
    role_counts: dict[str, int] = defaultdict(int)
    # English cores whose original-language sibling is already collected. Any -original
    # slug that declares original_of=<english-slug> clears that english slug off the待補 list.
    covered_by_original: set[str] = set()
    for meta_p in sorted(TRANSLATIONS_DIR.glob("*/meta.json")):
        try:
            meta = json.loads(meta_p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if meta.get("original_of") and (meta.get("text_role") == "original"):
            oo = meta["original_of"]
            covered_by_original.update([oo] if isinstance(oo, str) else oo)
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
        native_ratio = _native_script_ratio(slug)
        by_religion[rel].append({
            "slug": slug,
            "religion": rel,
            "name_zh": meta.get("name_zh", ""),
            "language": meta.get("language", ""),
            "text_role": meta.get("text_role") or "",
            "translated": tr_done,
            "tagged": tag_done,
            "native_ratio": native_ratio,
            "has_native_script": native_ratio >= NATIVE_SCRIPT_MIN,
        })

    total = sum(len(v) for v in by_religion.values())
    tr_total = sum(1 for v in by_religion.values() for e in v if e["translated"])
    tag_total = sum(1 for v in by_religion.values() for e in v if e["tagged"])

    # Sole-source vs redundant translation classification. A core is genuinely 待補原文
    # only when it is BOTH (a) not labelled text_role==original AND (b) its original.txt
    # does not already carry a non-Latin native script on disk (content-truth guard).
    # This stops the phantom-entry recurrence: homer-greek is 99% Greek bytes, so even
    # though its label said "English translation" it no longer lands on the待補 list.
    # 待補 is tracked PER-SLUG within the ancient/pagan religions that were bulk-collected as
    # 19c English anthologies (sacred-texts.com). Per-slug matters: 古希臘羅馬 having the Greek
    # Homer (homer-greek) does NOT cover Ovid/Virgil/Plato, whose Latin/Greek originals are
    # still missing — a religion-level "covered" flag would wrongly hide them.
    # Mainstream religions (佛/道/儒/基督/伊斯蘭/印度/猶太) have dedicated original pipelines
    # (CBETA / ctext / sblgnt / quran / sefaria / gretil …), so their non-original cores are
    # redundant 對照, not 待補, and are excluded here. This also stops the 和合本/漢譯 false
    # positives: those live in mainstream religions and never enter this set.
    BACKFILL_RELIGIONS = {
        "古希臘羅馬", "瑣羅亞斯德", "古埃及", "諾斯底", "赫爾墨斯", "美洲",
        "瑪雅", "阿茲特克", "印加", "凱爾特", "兩河", "北歐", "錫克教",
        "非洲", "耆那教", "斯拉夫", "神道", "巴哈伊",
    }

    def _is_sole_source(e: dict) -> bool:
        # content-truth guard: a native-script file already carries its original on disk.
        # covered-by-sibling guard: an original-language sibling slug was already collected.
        return (e["religion"] in BACKFILL_RELIGIONS
                and e["text_role"] != "original"
                and not e["has_native_script"]
                and e["slug"] not in covered_by_original)

    # Cores inside candidate sole-source religions whose bytes prove the original is already
    # on disk but whose label still says otherwise — a data-quality backlog: fix text_role,
    # do NOT re-download.
    mislabeled_originals = sorted(
        (e for v in by_religion.values() for e in v
         if e["religion"] in BACKFILL_RELIGIONS
         and e["has_native_script"] and e["text_role"] != "original"),
        key=lambda e: -e["native_ratio"],
    )

    source_status = _load_source_status()

    def _is_actionable_sole_source(e: dict) -> bool:
        # 待補 that is genuinely collectable: sole-source AND not yet documented as
        # having no clean original source.
        return _is_sole_source(e) and e["slug"] not in source_status

    sole_source_slugs = [e for v in by_religion.values() for e in v if _is_actionable_sole_source(e)]
    # Documented-no-clean-source cores that still count as sole-source (English-only on disk).
    documented_slugs = [e for v in by_religion.values() for e in v
                        if _is_sole_source(e) and e["slug"] in source_status]
    sole_source_religions = sorted(
        {e["religion"] for v in by_religion.values() for e in v if _is_actionable_sole_source(e)},
        key=lambda r: -sum(1 for e in by_religion[r] if _is_actionable_sole_source(e)),
    )

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

    # Sole-source (English-only) religions — policy is settled, not an open gap
    lines += [
        "",
        "## 唯一英譯本核心（政策已定，非待決缺口）",
        "",
        "> 這些宗教的核心語料**目前只有英譯本、語料庫無原文**。政策：**先英→中翻譯**"
        "（`m3-translator-role.md` English 列，二手翻譯）讓它有中文可讀；**原文另列 "
        "`original-text-todo.md` 追蹤補抓**。此為已定政策，audit 不再視為不明缺口。",
        "",
        f"- 唯一英譯本宗教：**{len(sole_source_religions)}** 個 / 核心 **{len(sole_source_slugs)}** 部",
        f"- 名單：{('、'.join(sole_source_religions)) or '（無）'}",
        "",
        "### 內容檢查：原文已在庫但 text_role 標錯（改標，非缺口）",
        "",
        "> `original.txt` 實測含 ≥15% 非拉丁原生文字，卻未標 `text_role=original`。"
        "改標即可，勿重複下載。詳見 `original-text-todo.md` 末段。",
        "",
    ]
    lines += ([f"- `{e['slug']}` {e['name_zh']}（{e['religion']}，原生文字 {round(e['native_ratio']*100)}%）"
               for e in mislabeled_originals] or ["- （無）"])

    lines += ["", "## 各宗教核心明細", ""]
    for rel in sorted(by_religion, key=lambda r: -len(by_religion[r])):
        lines.append(f"### {rel}（{len(by_religion[rel])} 部）")
        lines.append("")
        for e in sorted(by_religion[rel], key=lambda x: x["slug"]):
            tr = "譯✓" if e["translated"] else "譯–"
            tg = "標✓" if e["tagged"] else "標–"
            lines.append(f"- `{e['slug']}` {e['name_zh']}（{e['language']}）{tr} {tg}")
        lines.append("")

    # Persistent 待補原文 backlog — the durable home for "still fill the original later"
    todo = [
        "# 待補原文清單（original-text-todo）",
        "",
        "> 由 `scripts/audit-core.py` 自動產生。列出**核心語料只有英譯本、且原文有乾淨來源可收但尚未收**的部。",
        "> 政策：先英→中翻譯（過渡），原文取得後重譯。這是 Pipeline A 的補抓待辦，非阻塞。",
        "> 已查明「無乾淨原文來源」的部另列文末分區（來源狀態表 `scripts/catalog/original-source-status.json`）。",
        "",
        f"- 可收待補原文核心：**{len(sole_source_slugs)}** 部，橫跨 **{len(sole_source_religions)}** 宗教",
        "",
    ]
    for rel in sole_source_religions:
        entries = sorted((e for e in by_religion[rel] if _is_actionable_sole_source(e)),
                         key=lambda x: x["slug"])
        if not entries:
            continue
        todo.append(f"## {rel}（{len(entries)} 部）")
        todo.append("")
        for e in entries:
            tr = "已英→中✓" if e["translated"] else "未譯"
            todo.append(f"- [ ] `{e['slug']}` {e['name_zh']}（{e['language']}）— {tr}，原文待補")
        todo.append("")

    if documented_slugs:
        todo += [
            "---",
            "",
            "## 已查明無乾淨原文來源（附探查記錄，非未查的待辦）",
            "",
            "> 這些核心經過實際探查，確認目前無乾淨可收的原文來源。分三類，逐部附理由與已探來源。",
            "> 出現乾淨來源即收——移除 `original-source-status.json` 對應條目即回到可收待補。",
            "",
            f"- 已查明無乾淨來源：**{len(documented_slugs)}** 部",
            "",
        ]
        by_status: dict[str, list[dict]] = defaultdict(list)
        for e in sorted(documented_slugs, key=lambda x: x["slug"]):
            by_status[source_status[e["slug"]].get("status", "?")].append(e)
        for st in ("blocked-access", "no-single-original", "oral-no-script"):
            group = by_status.get(st)
            if not group:
                continue
            todo.append(f"### {_STATUS_LABELS.get(st, st)}（{len(group)} 部）")
            todo.append("")
            for e in group:
                info = source_status[e["slug"]]
                probed = "；".join(info.get("probed", []))
                todo.append(f"- `{e['slug']}` {e['name_zh']}（{e['religion']}）")
                todo.append(f"  - 理由：{info.get('reason', '')}")
                if probed:
                    todo.append(f"  - 已探來源：{probed}")
            todo.append("")

    if mislabeled_originals:
        todo += [
            "---",
            "",
            "## 原文其實已在庫、只是 text_role 標錯（改標，不需下載）",
            "",
            "> `audit-core.py` 內容檢查：`original.txt` 實際含 ≥15% 非拉丁原生文字，"
            "但 `text_role` 未標 `original`。這些不是缺口，是標籤債，改 `text_role=original` 即可。",
            "",
        ]
        for e in mislabeled_originals:
            pct = round(e["native_ratio"] * 100)
            todo.append(f"- [ ] `{e['slug']}` {e['name_zh']}（原生文字 {pct}%）— 改標 text_role=original")
        todo.append("")

    OVERVIEW_DIR.mkdir(exist_ok=True)
    MANIFEST_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    ORIGINAL_TODO_PATH.write_text("\n".join(todo) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {MANIFEST_PATH.relative_to(ROOT)}")
    print(f"wrote {ORIGINAL_TODO_PATH.relative_to(ROOT)} "
          f"({len(sole_source_slugs)} 部可收待補 / {len(sole_source_religions)} 宗教; "
          f"{len(documented_slugs)} 部已查明無乾淨來源)")
    print(f"  核心 {total} / 已譯 {tr_total} / 已標籤 {tag_total}")
    if mislabeled_originals:
        print(f"  內容檢查揪出原文已在庫但標錯 text_role: {len(mislabeled_originals)} 部 "
              f"({', '.join(e['slug'] for e in mislabeled_originals[:8])})")
    if absent:
        print(f"  語料庫缺口: {', '.join(absent)}")
    if no_core_but_present:
        print(f"  有經文但無核心標記: {', '.join(sorted(no_core_but_present))}")
    if translit_suspects:
        print(f"  疑似音譯待確認 text_role: {len(translit_suspects)} 部 "
              f"({', '.join(e['slug'] for e in translit_suspects[:8])})")


if __name__ == "__main__":
    main()
