#!/usr/bin/env python3
"""dedup_mark_aliases.py — 標記同內容雙存的重複 slug（不刪檔，可逆）。

背景：部分經典同時以 CBETA 編號 slug（如 cbeta-T09n0262）與語意 slug（如
lotus-sutra）各存一份，raw/original.txt byte 相同（同 SHA-256）。翻譯/標籤
管線會把兩份各跑一次＝同一部經重複付費。

策略（非破壞）：每組保留「meta 較完整」的一份為 canonical（多半是語意 slug，
tier=核心、已有 semantic_tags/keywords），另一份標 `alias_of: <canonical>` +
`dedup_note`。raw/original.txt 與 checksums 一律不動（不破 SHA-256）。
管線端由 `load_slugs_by_tier` 讀到 `alias_of` 即跳過（見 translate.py）。

用法：
  PYTHONIOENCODING=utf-8 python scripts/dedup_mark_aliases.py --dry-run
  PYTHONIOENCODING=utf-8 python scripts/dedup_mark_aliases.py --apply
"""
import argparse
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRANS = ROOT / "translations"

TIER_RANK = {"核心": 0, "延伸": 1, "總集逐部": 2}


def _has(slug: str, fname: str) -> bool:
    p = TRANS / slug / fname
    return p.exists() and p.stat().st_size > 100


def richness(slug: str, meta: dict) -> tuple:
    """越前面越該當 canonical：已翻/已註的優先（避免棄置成果），
    再比 tier 越核心、標籤越多、欄位越多。"""
    done_work = 0 if (_has(slug, "01-translation.md") or _has(slug, "02-annotation.md")) else 1
    tier = TIER_RANK.get(meta.get("tier"), 3)
    ntags = len(meta.get("semantic_tags") or []) + len(meta.get("keywords") or [])
    return (done_work, tier, -ntags, -len(meta))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    apply = args.apply

    sha_to = defaultdict(list)
    metas = {}
    for mp in sorted(TRANS.glob("*/meta.json")):
        slug = mp.parent.name
        orig = mp.parent / "raw" / "original.txt"
        if not orig.exists():
            continue
        try:
            metas[slug] = json.loads(mp.read_text(encoding="utf-8"))
        except Exception:
            continue
        sha_to[hashlib.sha256(orig.read_bytes()).hexdigest()].append(slug)

    groups = {h: s for h, s in sha_to.items() if len(s) > 1}
    decisions = []
    for h, slugs in groups.items():
        # 已標過的 alias 略過，避免重覆處理
        ranked = sorted(slugs, key=lambda s: richness(s, metas[s]))
        canonical = ranked[0]
        for alias in ranked[1:]:
            decisions.append((alias, canonical))

    print(f"=== 重複組 {len(groups)}，將標 alias {len(decisions)} 部 ===")
    for alias, canon in decisions:
        already = metas[alias].get("alias_of")
        flag = "" if not already else f"  (已標 alias_of={already})"
        print(f"  {alias}  →  canonical: {canon}{flag}")

    if apply:
        n = 0
        for alias, canon in decisions:
            mp = TRANS / alias / "meta.json"
            meta = metas[alias]
            if meta.get("alias_of") == canon:
                continue
            meta["alias_of"] = canon
            meta["dedup_note"] = (
                f"與 {canon} 同內容（同 SHA-256）雙存；此份為別名，"
                f"管線跳過不重複翻譯/標籤。2026-07-05 scripts/dedup_mark_aliases.py")
            mp.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
                          encoding="utf-8", newline="\n")
            n += 1
        print(f"\n落地：{n} 部標為 alias（raw/original.txt 與 checksums 未動）")
    else:
        print("\n（dry-run，未改檔。加 --apply 落地。）")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
