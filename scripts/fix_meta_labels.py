#!/usr/bin/env python3
"""fix_meta_labels.py — 修 audit-data-quality 揪出的 meta 標籤問題（只改 meta.json）。

兩類修正（都不動 raw/original.txt，不破 SHA-256）：
  1. 語言標籤中文→英文標準名：
       希伯來 → Hebrew、拉丁 → Latin、希臘 → Ancient Greek
     （希臘 11 部是 Homer/Plato/Herodotus 古典希臘，非 Koine；Koine 專指新約，
       已有 27 部 SBLGNT 各卷正確標 Koine Greek，不動。）
  2. 回填 text_role / is_original_language（僅限有把握的類別，其餘留 null）：
       - is_original_language==True 且 text_role 缺 → text_role="original"
       - vulgate-*（Jerome 拉丁譯本）→ is_original_language=False, text_role="translation"
       - huangting-neijing / mozi（道/墨古典漢語原典）→ True, "original"
     不確定者一律略過（CLAUDE.md §3 未標＝安全預設，不臆測）。

用法：
  PYTHONIOENCODING=utf-8 python scripts/fix_meta_labels.py --dry-run
  PYTHONIOENCODING=utf-8 python scripts/fix_meta_labels.py --apply
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRANS = ROOT / "translations"

LANG_FIX = {"希伯來": "Hebrew", "拉丁": "Latin", "希臘": "Ancient Greek"}
CJK_ORIGINALS = {"huangting-neijing", "mozi"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    apply = args.apply

    lang_fixed, role_fixed = [], []
    for mp in sorted(TRANS.glob("*/meta.json")):
        slug = mp.parent.name
        try:
            meta = json.loads(mp.read_text(encoding="utf-8"))
        except Exception:
            continue
        changed = False

        lang = (meta.get("language") or "").strip()
        if lang in LANG_FIX:
            meta["language"] = LANG_FIX[lang]
            lang_fixed.append((slug, lang, LANG_FIX[lang]))
            changed = True

        if meta.get("text_role") is None:
            iol = meta.get("is_original_language")
            new_role = None
            if iol is True:
                new_role = "original"
            elif iol is False:
                new_role = "translation"
            elif slug.startswith("vulgate-"):
                meta["is_original_language"] = False
                new_role = "translation"
            elif slug in CJK_ORIGINALS:
                meta["is_original_language"] = True
                new_role = "original"
            if new_role:
                meta["text_role"] = new_role
                role_fixed.append((slug, new_role, meta.get("is_original_language")))
                changed = True

        if changed and apply:
            mp.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
                          encoding="utf-8", newline="\n")

    print(f"=== 語言標籤修正（{len(lang_fixed)} 部）===")
    from collections import Counter
    for k, v in Counter((a, b) for _, a, b in lang_fixed).most_common():
        print(f"  {k[0]} → {k[1]}：{v} 部")
    print(f"\n=== text_role 回填（{len(role_fixed)} 部）===")
    for k, v in Counter((b, c) for _, b, c in role_fixed).most_common():
        print(f"  text_role={k[0]}, is_original_language={k[1]}：{v} 部")
    print(f"\n{'落地' if apply else 'dry-run'}：共 {len(lang_fixed)+len(role_fixed)} 處變更"
          + ("" if apply else "（加 --apply 落地）"))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
