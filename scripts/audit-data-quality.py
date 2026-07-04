#!/usr/bin/env python3
"""audit-data-quality.py — 全庫資料完整性稽核（免費，純本地掃描）。

檢查項目：
  1. 空 / 截斷的 original.txt（有效內容過短）
  2. U+FFFD 置換字（編碼損壞硬訊號）
  3. mojibake 簽名（UTF-8 被當 Latin-1 解的殘跡：Ã/Â/â€…）
  4. checksum 宣告（meta.checksum_sha256）vs 實檔不符
  5. 重複內容（同 SHA 出現在不同 slug）
  6. meta 缺關鍵欄（language / is_original_language / text_role）
  7. 章節分隔符 `=== N | label ===` 缺失
  8. 語言標籤不一致（Hebrew/希伯來、Koine Greek/希臘、Latin/拉丁…）
  9. 外語檔「預期字集占比過低」（疑亂碼 / 抓錯內容）

輸出：00-overview/data-quality-report.md
用法：PYTHONIOENCODING=utf-8 python scripts/audit-data-quality.py
"""
import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRANS = ROOT / "translations"
OUT = ROOT / "00-overview" / "data-quality-report.md"
TZ = timezone(timedelta(hours=8))

MOJIBAKE_RE = re.compile(r"Ã[-¿ ]|Â[-¿]|â€|Ã©|Ã¨|Ã¤|Ã¶|Ã¼|Ã\x9f")
SEP_RE = re.compile(r"^===\s*\d+\s*\|", re.M)

# 語言標籤正規化：變體 → 標準名（只用於「不一致」報告，不改資料）
LANG_ALIASES = {
    "希伯來": "Hebrew", "希臘": "Ancient Greek", "拉丁": "Latin",
    "梵語": "Sanskrit", "梵文": "Sanskrit", "巴利": "Pali", "巴利語": "Pali",
}

# 各語言的「預期 Unicode 區塊」判斷函式（romanized 者以 Latin 判）
def _block(ch):
    o = ord(ch)
    if 0x4E00 <= o <= 0x9FFF or 0x3400 <= o <= 0x4DBF: return "CJK"
    if 0x0370 <= o <= 0x03FF or 0x1F00 <= o <= 0x1FFF: return "Greek"
    if 0x0590 <= o <= 0x05FF: return "Hebrew"
    if 0x0600 <= o <= 0x06FF: return "Arabic"
    if 0x0900 <= o <= 0x097F: return "Devanagari"
    if 0x0F00 <= o <= 0x0FFF: return "Tibetan"
    if 0x0041 <= o <= 0x024F: return "Latin"
    return "other"

EXPECT = {  # meta.language 關鍵字 → 預期主字集
    "古典漢語": "CJK", "古典中文": "CJK",
    "Hebrew": "Hebrew", "希伯來": "Hebrew",
    "Koine Greek": "Greek", "Ancient Greek": "Greek", "希臘": "Greek",
    "Arabic": "Arabic",
    "藏": "Tibetan",
    # 註：本庫 Sanskrit/Pali 全為 IAST 羅馬轉寫（sacred-texts / GRETIL），
    #     預期字集本就是 Latin，不列入字集檢查（列入會全數誤報）。
}


def expected_block(lang: str):
    # 譯本語言標籤（English (translation from …)）含 "Greek" 等子字串，
    # 但內容是英文 Latin，不可用子字串誤配；先排除。
    if "translation" in lang or lang.startswith("English"):
        return None
    for k, v in EXPECT.items():
        if k in lang:
            return v
    return None  # 未知 / romanized → 不檢字集


def main() -> None:
    empty, fffd, mojibake, checksum_bad, no_sep = [], [], [], [], []
    meta_missing = []
    lang_inconsistent = Counter()
    script_suspect = []
    sha_to_slugs = defaultdict(list)
    total = 0

    for meta_path in sorted(TRANS.glob("*/meta.json")):
        slug = meta_path.parent.name
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception as e:
            meta_missing.append((slug, f"meta.json 壞: {e}"))
            continue
        total += 1
        lang = (meta.get("language") or meta.get("source_language") or "").strip()

        # meta 缺欄
        miss = [f for f in ("language",) if not meta.get(f)]
        if meta.get("is_original_language") is None:
            miss.append("is_original_language")
        if meta.get("text_role") is None:
            miss.append("text_role")
        if miss:
            meta_missing.append((slug, "缺 " + "/".join(miss)))

        # 語言標籤不一致
        if lang in LANG_ALIASES:
            lang_inconsistent[f"{lang} → 應統一為 {LANG_ALIASES[lang]}"] += 1

        orig = meta_path.parent / "raw" / "original.txt"
        if not orig.exists():
            empty.append((slug, "無 original.txt"))
            continue
        raw = orig.read_bytes()
        text = raw.decode("utf-8", errors="replace")
        stripped = re.sub(r"===\s*\d+\s*\|[^\n]*===", "", text)
        stripped = re.sub(r"\s", "", stripped)

        # 空 / 截斷
        if len(stripped) < 50:
            empty.append((slug, f"有效內容僅 {len(stripped)} 字"))
            continue

        # U+FFFD
        nf = text.count("�")
        if nf > 0:
            fffd.append((slug, nf))

        # mojibake
        nm = len(MOJIBAKE_RE.findall(text))
        if nm >= 5:
            mojibake.append((slug, nm))

        # checksum 宣告 vs 實檔
        declared = meta.get("checksum_sha256")
        actual = hashlib.sha256(raw).hexdigest()
        if declared and declared != actual:
            checksum_bad.append((slug, f"meta={declared[:12]} 實={actual[:12]}"))
        sha_to_slugs[actual].append(slug)

        # 章節分隔符
        if not SEP_RE.search(text):
            no_sep.append(slug)

        # 外語字集占比
        exp = expected_block(lang)
        if exp:
            cnt = Counter(_block(c) for c in stripped[:5000])
            tot = sum(cnt.values()) or 1
            ratio = cnt.get(exp, 0) / tot
            if ratio < 0.30:
                top = cnt.most_common(3)
                script_suspect.append((slug, lang, exp, f"{ratio:.0%}", top))

    dups = {h: s for h, s in sha_to_slugs.items() if len(s) > 1}

    # ---- 寫報告 ----
    L = []
    L.append("# 資料完整性稽核報告")
    L.append("")
    L.append(f"> 自動產生：`scripts/audit-data-quality.py`　{datetime.now(TZ).strftime('%Y-%m-%d %H:%M')} +0800")
    L.append(f"> 掃描 {total} 部")
    L.append("")
    L.append("## 摘要")
    L.append("")
    L.append("| 問題 | 數量 |")
    L.append("|------|------|")
    L.append(f"| 空 / 截斷 original.txt | {len(empty)} |")
    L.append(f"| U+FFFD 編碼損壞 | {len(fffd)} |")
    L.append(f"| mojibake 疑似 | {len(mojibake)} |")
    L.append(f"| checksum 不符 | {len(checksum_bad)} |")
    L.append(f"| 重複內容(同 SHA) | {len(dups)} 組 |")
    L.append(f"| meta 缺關鍵欄 | {len(meta_missing)} |")
    L.append(f"| 缺章節分隔符 | {len(no_sep)} |")
    L.append(f"| 語言標籤不一致 | {sum(lang_inconsistent.values())} |")
    L.append(f"| 外語字集占比過低 | {len(script_suspect)} |")
    L.append("")

    def section(title, rows, fmt):
        L.append(f"## {title}（{len(rows)}）")
        L.append("")
        if not rows:
            L.append("_無_")
        else:
            for r in rows[:200]:
                L.append("- " + fmt(r))
            if len(rows) > 200:
                L.append(f"- …另 {len(rows)-200} 筆")
        L.append("")

    section("空 / 截斷 original.txt", empty, lambda r: f"`{r[0]}` — {r[1]}")
    section("U+FFFD 編碼損壞", fffd, lambda r: f"`{r[0]}` — {r[1]} 個置換字")
    section("mojibake 疑似", mojibake, lambda r: f"`{r[0]}` — {r[1]} 處")
    section("checksum 不符（meta vs 實檔）", checksum_bad, lambda r: f"`{r[0]}` — {r[1]}")
    section("外語字集占比過低（疑亂碼 / 抓錯）", script_suspect,
            lambda r: f"`{r[0]}` lang={r[1]} 期望{r[2]} 實占{r[3]} 分布{r[4]}")
    section("缺章節分隔符", [(s,) for s in no_sep], lambda r: f"`{r[0]}`")
    section("meta 缺關鍵欄", meta_missing, lambda r: f"`{r[0]}` — {r[1]}")

    L.append(f"## 重複內容（同 SHA-256，{len(dups)} 組）")
    L.append("")
    if not dups:
        L.append("_無_")
    else:
        for h, slugs in list(dups.items())[:100]:
            L.append(f"- `{h[:12]}` × {len(slugs)}：{', '.join(slugs)}")
        if len(dups) > 100:
            L.append(f"- …另 {len(dups)-100} 組")
    L.append("")

    L.append("## 語言標籤不一致")
    L.append("")
    if not lang_inconsistent:
        L.append("_無_")
    else:
        for k, v in lang_inconsistent.most_common():
            L.append(f"- {k}：{v} 部")
    L.append("")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    print(f"掃描 {total} 部。報告 → {OUT.relative_to(ROOT)}")
    print(f"空/截斷={len(empty)} FFFD={len(fffd)} mojibake={len(mojibake)} "
          f"checksum壞={len(checksum_bad)} 重複={len(dups)}組 meta缺={len(meta_missing)} "
          f"缺分隔={len(no_sep)} 語言不一致={sum(lang_inconsistent.values())} 字集疑={len(script_suspect)}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
