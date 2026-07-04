#!/usr/bin/env python3
"""normalize_wikisource_zh.py — 外科式簡→繁正規化（只動維基文庫古典漢語檔）。

背景：zh.wikisource 逐章由不同貢獻者輸入，部分章節用簡體字，造成同一部古籍
字形不統一。ctext 重抓不可行（多章節經撞 ERR_REQUIRES_AUTHENTICATION）。

策略（保守白名單）：
  1. 取 OpenCC s2t 對這些檔會轉的所有字（候選）。
  2. 排除兩類，一律不轉：
     (A) 文言正字 / 獨立傳統字（云=曰、于=介詞、里=村里、游=游泳、尸=祭尸、
         后=君后、余=我、无=易經本字、几=案几、咸=皆、采、范、征、占…）。
     (B) 一簡對多繁的歧義字（干→乾/幹、后→後/后、里→裡/里、松→鬆/松、
         面→麵/面、谷→穀/谷、复→復/複/覆、制→製/制、系→係/繫…）——
         逐字轉會選錯，交人工或留原樣。
  3. 剩下「一簡對一繁、簡體形本身非傳統字」者才轉（礼→禮、宾→賓、辞→辭、
     启→啟、听→聽、陈→陳、经→經、领→領、妇→婦、执→執、国→國、学→學…）。
  存疑一律不轉：寧留簡體殘字，不改壞正字。CBETA（99.7%）一字不動。

用法：
  PYTHONIOENCODING=utf-8 python scripts/normalize_wikisource_zh.py --dry-run
  PYTHONIOENCODING=utf-8 python scripts/normalize_wikisource_zh.py --apply
"""
import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

from opencc import OpenCC

ROOT = Path(__file__).resolve().parent.parent
TRANS = ROOT / "translations"
_cc = OpenCC("s2t")

# (A) 文言正字 / 獨立傳統字：本身在文言有獨立字義，OpenCC 想轉但轉了就錯。
CLASSICAL_KEEP = set(
    "云于里游尸凶群后干无辟斗余占范征咸采秘岳丑朴托床峰并恒内几仆长台当"
    "兹尔来种丧适虫叶卜别价从只呢周迭坏胄涂户机荐兹瓮卧岩强吁愿其"
)
# (B) 一簡對多繁的歧義字：逐字轉會選錯義項，一律不轉。
AMBIGUOUS_MULTI = set(
    "干后里松面谷复制系志表钟板郁划佣折曲云于余无几尸卜斗种适虫别秘台当"
    "征范咸采占丑朴并游凶恒内长术尽发同历厉夸"
    "吃冲准"  # 吃(喫/口吃)、冲(衝/沖)、准(準/准許) 低頻但義項歧義，一律不轉
)
EXCLUDE = CLASSICAL_KEEP | AMBIGUOUS_MULTI
# OpenCC 選異體時改回台標準繁體形
OVERRIDE = {"为": "為", "众": "眾"}

TARGET_SLUGS = [
    "baopuzi", "book-of-changes", "book-of-poetry", "chun-qiu-zuo-zhuan", "er-ya",
    "gongyang-zhuan", "guo-yu", "huainanzi", "huangting-neijing", "jin-si-lu",
    "kongzi-jiayu", "liji", "shang-shu", "taiping-jing", "wenzhongzi-zhongshuo",
    "wenzi", "yi-li", "yunji-qiqian", "zhou-li", "zhuzi-yulei",
]


def is_cjk(ch: str) -> bool:
    return "一" <= ch <= "鿿"


def collect_candidates() -> Counter:
    """回 OpenCC 在目標檔會轉的字 → 總出現次數。"""
    cand = Counter()
    for slug in TARGET_SLUGS:
        p = TRANS / slug / "raw" / "original.txt"
        if not p.exists():
            continue
        t = p.read_text(encoding="utf-8", errors="replace")
        for ch in set(t):
            if is_cjk(ch):
                conv = _cc.convert(ch)
                if len(conv) == 1 and conv != ch:
                    cand[ch] += t.count(ch)
    return cand


def build_map() -> tuple[dict[str, str], list[tuple[str, int]]]:
    """回 (安全轉換表, 被排除字清單[(字,次數)])。"""
    cand = collect_candidates()
    smap = {}
    excluded = []
    for ch, n in cand.most_common():
        if ch in EXCLUDE:
            excluded.append((ch, n))
            continue
        t = OVERRIDE.get(ch) or _cc.convert(ch)
        if len(t) == 1 and t != ch:
            smap[ch] = t
    return smap, excluded


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    apply = args.apply

    smap, excluded = build_map()
    print(f"=== 安全轉換表（{len(smap)} 字，一簡對一繁、非傳統字）===")
    print(" ".join(f"{s}→{t}" for s, t in smap.items()))
    print()
    print(f"=== 排除不轉（{len(excluded)} 字，文言正字 / 歧義字）===")
    print(" ".join(f"{c}×{n}" for c, n in excluded))
    print()

    trans = str.maketrans(smap)
    changed = []
    for slug in TARGET_SLUGS:
        orig = TRANS / slug / "raw" / "original.txt"
        if not orig.exists():
            continue
        text = orig.read_text(encoding="utf-8", errors="replace")
        new = text.translate(trans)
        n = sum(1 for a, b in zip(text, new) if a != b)
        if n == 0:
            continue
        changed.append((n, slug))
        if apply:
            orig.write_text(new, encoding="utf-8", newline="\n")
            cs = TRANS / slug / "raw" / "checksums.sha256"
            if cs.exists():
                h = hashlib.sha256(new.encode("utf-8")).hexdigest()
                out = []
                for line in cs.read_text(encoding="utf-8").splitlines():
                    parts = line.split(None, 1)
                    if len(parts) == 2 and parts[1].strip().endswith("original.txt"):
                        out.append(f"{h}  {parts[1].strip()}")
                    else:
                        out.append(line)
                cs.write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
            # 同步 meta.json 的 checksum_sha256 + size_bytes
            mp = TRANS / slug / "meta.json"
            if mp.exists():
                try:
                    meta = json.loads(mp.read_text(encoding="utf-8"))
                    meta["checksum_sha256"] = hashlib.sha256(new.encode("utf-8")).hexdigest()
                    meta["size_bytes"] = len(new.encode("utf-8"))
                    mp.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
                                  encoding="utf-8", newline="\n")
                except Exception:
                    pass

    changed.sort(reverse=True)
    print(f"=== {'落地' if apply else 'dry-run'}：{len(changed)} 部有變動 ===")
    for n, slug in changed:
        print(f"  {n:5d} 字  {slug}")
    if not apply:
        print("\n（dry-run，未改檔。加 --apply 落地。）")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
