#!/usr/bin/env python
"""
Track collection progress against v3 inventory + report gaps per religion.

Reads:
    translations/*/meta.json  →  current state (what's downloaded)
    methodology/per-religion-scriptures.md  →  target inventory (what's planned)

Outputs:
    00-overview/PROGRESS.md  →  per-religion progress dashboard
                                  含 done count / target count / 完成率 / 待做清單
    00-overview/PROGRESS.json →  machine-readable

Failure mode tracking:
    Reads scripts/failed.json (if exists) for items that failed past batches.
    Failed items can be retried via download-<source>.py with appropriate flags.

Usage:
    python scripts/track-progress.py
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRANSLATIONS_DIR = ROOT / "translations"
INVENTORY_PATH = ROOT / "methodology" / "per-religion-scriptures.md"
OUT_JSON = ROOT / "00-overview" / "PROGRESS.json"
OUT_MD = ROOT / "00-overview" / "PROGRESS.md"

# Inventory v3 targets — manually-curated per-religion totals based on v3 §統計
# Format: religion → {tier: target_count}
# These are the "expected when all listed entries are downloaded" goals.
# 'full' refers to total-canon展開 (道藏全/塔木德全), not just v3-listed主要 entries.
TARGETS = {
    "佛教": {
        "core": 60,         # core sutras across all traditions
        "v3_listed": 460,   # all v3-listed Buddhist entries (Pali + 漢傳 + 藏傳 + 梵文 + 其他)
        "full_canon": 13000, # full Tripitaka in all traditions
    },
    "道教": {
        "core": 15,
        "v3_listed": 40,
        "full_canon": 6000,  # 道藏 5305 + 續道藏 + 道藏輯要
    },
    "儒教": {
        "core": 9,
        "v3_listed": 35,
        "full_canon": 5000,  # 十三經注疏 + 四庫經部 + 皇清經解
    },
    "印度教": {
        "core": 25,
        "v3_listed": 250,
        "full_canon": 3000,  # 4 Vedas + 108 Upanishads + 18+18 Puranas + 史詩 + Tantra
    },
    "猶太教": {
        "core": 24,          # Tanakh 24 卷
        "v3_listed": 150,
        "full_canon": 1000,  # +Mishnah 63 + Talmud 76 + Midrash + Halakhah + Kabbalah
    },
    "基督教": {
        "core": 66,          # 聖經 66 卷
        "v3_listed": 250,
        "full_canon": 3000,  # +教父全集 + 中世紀 + 改革宗 + 外典 + 死海古卷
    },
    "伊斯蘭": {
        "core": 1,           # 古蘭經
        "v3_listed": 200,
        "full_canon": 50000, # 含六大聖訓萬則
    },
    "瑣羅亞斯德": {
        "core": 5,
        "v3_listed": 50,
        "full_canon": 200,
    },
    "神道": {
        "core": 5,
        "v3_listed": 20,
        "full_canon": 200,
    },
    "兩河": {
        "core": 4,
        "v3_listed": 60,
        "full_canon": 600,
    },
    "古埃及": {
        "core": 3,
        "v3_listed": 60,
        "full_canon": 1000,
    },
    "古希臘羅馬": {
        "core": 10,
        "v3_listed": 100,
        "full_canon": 500,
    },
    "北歐": {
        "core": 2,
        "v3_listed": 30,
        "full_canon": 300,
    },
    "凱爾特": {
        "core": 4,
        "v3_listed": 40,
        "full_canon": 500,
    },
    "斯拉夫": {
        "core": 2,
        "v3_listed": 10,
        "full_canon": 100,
    },
    "諾斯底": {
        "core": 9,
        "v3_listed": 60,
        "full_canon": 200,
    },
    "美洲": {
        "core": 3,
        "v3_listed": 50,
        "full_canon": 500,
    },
    "非洲": {
        "core": 2,
        "v3_listed": 30,
        "full_canon": 500,
    },
    "耆那教": {
        "core": 5,
        "v3_listed": 60,
        "full_canon": 150,
    },
    "錫克教": {
        "core": 1,
        "v3_listed": 10,
        "full_canon": 30,
    },
    "巴哈伊": {
        "core": 5,
        "v3_listed": 25,
        "full_canon": 1200,
    },
    "現代新興": {
        "core": 5,
        "v3_listed": 100,
        "full_canon": 1000,
    },
}


def load_current_state() -> dict:
    """Read all meta.json, group by religion."""
    by_religion: dict[str, list[dict]] = defaultdict(list)
    for meta_p in sorted(TRANSLATIONS_DIR.glob("*/meta.json")):
        try:
            m = json.loads(meta_p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        religion = m.get("religion") or "unknown"
        by_religion[religion].append({
            "slug": m.get("slug"),
            "name_zh": m.get("name_zh"),
            "tradition": m.get("tradition"),
            "tier": m.get("tier"),
            "source": m.get("source_platform"),
            "is_original": m.get("is_original_language"),
            "size_bytes": m.get("size_bytes", 0),
        })
    return dict(by_religion)


def compute_progress(by_religion: dict) -> dict:
    """For each religion, compute done counts at multiple granularities."""
    report = {}
    for religion, scripts in sorted(by_religion.items()):
        done = len(scripts)
        target = TARGETS.get(religion, {})
        report[religion] = {
            "done": done,
            "target_core": target.get("core", 0),
            "target_v3_listed": target.get("v3_listed", 0),
            "target_full_canon": target.get("full_canon", 0),
            "pct_core": round(min(100, done / target["core"] * 100), 1) if target.get("core") else None,
            "pct_v3_listed": round(min(100, done / target["v3_listed"] * 100), 1) if target.get("v3_listed") else None,
            "pct_full": round(done / target["full_canon"] * 100, 2) if target.get("full_canon") else None,
            "with_translation": sum(1 for s in scripts if (TRANSLATIONS_DIR / (s["slug"] or "") / "01-translation.md").exists()),
            "with_semantic_tags": sum(1 for s in scripts if s.get("tradition") and "semantic_tags" in str(s)),  # placeholder
            "total_bytes": sum(s["size_bytes"] for s in scripts),
            "by_tradition": dict(Counter((s["tradition"] or "—") for s in scripts).most_common()),
            "by_source": dict(Counter((s["source"] or "—") for s in scripts).most_common()),
            "original_count": sum(1 for s in scripts if s["is_original"]),
        }
    return report


def write_outputs(report: dict, by_religion: dict):
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_bytes((json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))

    md = []
    md.append("# 進度追蹤 PROGRESS")
    md.append("")
    md.append("> 自動產生 by `scripts/track-progress.py`")
    md.append("> 每宗教三層完成度：**core**（核心經典）/ **v3_listed**（v3 列出 ~2400 entries）/ **full_canon**（道藏全 / 大正藏全 / 塔木德全等估計）")
    md.append("")

    total_done = sum(r["done"] for r in report.values())
    total_listed = sum(r["target_v3_listed"] or 0 for r in report.values())
    total_full = sum(r["target_full_canon"] or 0 for r in report.values())
    total_bytes = sum(r["total_bytes"] for r in report.values())
    total_translated = sum(r["with_translation"] for r in report.values())

    md.append("## 總覽")
    md.append("")
    md.append(f"- 總部數: **{total_done}** / v3 列出 {total_listed} ({total_done * 100 // max(1, total_listed)}%)")
    md.append(f"- 對全 canon 估計: {total_done} / {total_full} ≈ {total_done * 100 / max(1, total_full):.1f}%")
    md.append(f"- 總大小: {total_bytes / 1024 / 1024:.1f} MB")
    md.append(f"- 已 AI 翻譯: {total_translated} / {total_done} ({total_translated * 100 // max(1, total_done)}%)")
    md.append("")

    md.append("## 各宗教完成度")
    md.append("")
    md.append("| 宗教 | 已抓 | core 目標 | v3 目標 | full 估計 | core % | v3 % | full % | 已翻譯 |")
    md.append("|------|------|-----------|---------|-----------|--------|------|--------|--------|")
    for religion, r in sorted(report.items(), key=lambda x: -x[1]["done"]):
        md.append(
            f"| {religion} | {r['done']} | {r['target_core']} | {r['target_v3_listed']} | {r['target_full_canon']} | "
            f"{r['pct_core']}% | {r['pct_v3_listed']}% | {r['pct_full']}% | {r['with_translation']} |"
        )

    md.append("")
    md.append("## 各宗教 — 已有的傳統 / 來源")
    md.append("")
    for religion, r in sorted(report.items()):
        if r["done"] == 0:
            continue
        md.append(f"### {religion} ({r['done']} 部)")
        md.append("")
        md.append(f"- 傳統分布: {r['by_tradition']}")
        md.append(f"- 來源分布: {r['by_source']}")
        md.append(f"- 原文 / 譯文: {r['original_count']} / {r['done'] - r['original_count']}")
        md.append("")

    md.append("## 重點缺口（建議下次抓）")
    md.append("")
    md.append("以下宗教 core 完成率 <100%（最優先）：")
    md.append("")
    for religion, r in sorted(report.items(), key=lambda x: x[1]["pct_core"] or 0):
        if (r["pct_core"] or 0) < 100:
            md.append(f"- **{religion}**: core {r['done']}/{r['target_core']} ({r['pct_core']}%) — 待抓 {r['target_core'] - r['done']} 部")
    md.append("")
    md.append("以下宗教 v3-listed 完成率 <80%（次優先）：")
    md.append("")
    for religion, r in sorted(report.items(), key=lambda x: x[1]["pct_v3_listed"] or 0):
        if (r["pct_v3_listed"] or 0) < 80 and (r["pct_core"] or 0) >= 100:
            md.append(f"- **{religion}**: v3 {r['done']}/{r['target_v3_listed']} ({r['pct_v3_listed']}%) — 待抓 {max(0, r['target_v3_listed'] - r['done'])} 部")
    md.append("")

    md.append("## 翻譯 + 標籤進度")
    md.append("")
    md.append(f"已 AI 翻譯: {total_translated} / {total_done} ({total_translated * 100 // max(1, total_done)}%)")
    md.append("")
    md.append("（Pipeline B 翻譯尚未啟動。啟動後此區更新。）")
    md.append("")

    OUT_MD.write_bytes(("\n".join(md) + "\n").encode("utf-8"))
    print(f"wrote {OUT_MD}")
    print(f"  total: {total_done} / v3-listed {total_listed} ({total_done * 100 // max(1, total_listed)}%)")
    print(f"  full canon: {total_done * 100 / max(1, total_full):.1f}%")
    print(f"  translated: {total_translated} / {total_done}")


def main():
    by_religion = load_current_state()
    report = compute_progress(by_religion)
    write_outputs(report, by_religion)


if __name__ == "__main__":
    main()
