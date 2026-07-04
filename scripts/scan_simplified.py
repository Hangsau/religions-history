#!/usr/bin/env python3
"""scan_simplified.py — 偵測「古典漢語」原文是否為簡體字來源（精準版）。

背景問題：若抓到的原文是「簡體字」，代表來源是 1950 年代後的中國大陸
重排本，年代離祖本太遠，不該當作研究用「原文」。

第一版用 OpenCC s2t 差異率，但 OpenCC 會把文言正統異體字（云=曰、于、里、
咸=皆、尸=祭主、几=案几、无=易經本字、后=君王、余=我）也轉掉，造成大量誤報。

本版只數「1950 年代後才造、文言絕不可能出現」的真簡化字（偏旁類 + 明確結構
簡化）。這些字一旦成批出現，才是真正的簡體重排本證據。
"""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRANS = ROOT / "translations"

# 真簡化字：文言/傳統文本中絕不可能自然出現的簡化形。
# 排除所有古典異體字（云于里咸尸几无后余并恒脚却床群等）。
TRUE_SIMPLIFIED = set(
    # 偏旁類簡化（言讠、門门、車车、見见、貝贝、金钅、糸纟、頁页、食饣、馬马、鳥鸟、魚鱼）
    "讠门车见贝钅纟页饣马鸟鱼龙韦风飞齐"
    # 結構簡化（不含古典異體）
    "这个们国说话请谁读语课谢际认识实现将样觉见"
    "学会应义为众岁兴举亲农师变书东电时华与专业丛严"
    "术边过还进远连达违迁运迭违测浊层属岂屿峡"
    "对难观欢欢劝权双发圣对树戏鸡邓邮阳阴陆阶队"
    "亿仅从仑仓仪们价众优伟传伤伦体佣侠俭"
    "关兴军农冯净凤击划别刘则刚创劲动务"
    "厂厅历厉压厌县参双发变叠叶号叹只台"
    "启员呗听吗呜呢周响哑唤啧团园图圆"
    "块坏垄垒垫壮声壶处备复够头夹"
)

# 移除誤入的古典異體 / 本字（保險起見，明確踢掉）——這些不是簡化字：
#   周(本字，非「週」的簡化)、台(天台/三台/台州古已有)、迭(更迭古字)、
#   叶(叶韻古字)、坏(古異體)、别(別/别古並用)、价(詩經「价人」=善)。
# 其餘 东兴阶门举实鱼个与众复应权国为华声处备县参… 皆為真簡化字，保留。
_CLASSICAL_OK = set(
    "云于里咸尸几无后余并恒脚却床群向布挂了岳携迹欲念干斗占背回准朴痒猫葱涌熏厨范注唇冲折烟栗辟胄逊协监诸辞宾编陈志亘"
    "周台迭叶坏别价"
    "只从呢"  # 只(語錄「只是」)、从(從古字/甲骨本字)、呢(語錄口語助詞)
)
TRUE_SIMPLIFIED -= _CLASSICAL_OK

THRESHOLD_COUNT = 8   # 真簡化字絕對數 >= 8 才列（避免偶發夾雜）
THRESHOLD_RATIO = 0.001  # 或占全文 >= 0.1%


def is_cjk(ch: str) -> bool:
    return "一" <= ch <= "鿿"


def main() -> None:
    suspects = []
    scanned = 0
    for meta_path in sorted(TRANS.glob("*/meta.json")):
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        lang = (meta.get("source_language") or meta.get("language") or "").strip()
        if lang != "古典漢語":
            continue
        orig = meta_path.parent / "raw" / "original.txt"
        if not orig.exists():
            continue
        text = orig.read_text(encoding="utf-8", errors="replace")
        if not text.strip():
            continue
        scanned += 1
        cjk_total = sum(1 for c in text if is_cjk(c))
        hits = Counter(c for c in text if c in TRUE_SIMPLIFIED)
        n = sum(hits.values())
        ratio = n / cjk_total if cjk_total else 0.0
        if n >= THRESHOLD_COUNT or ratio >= THRESHOLD_RATIO:
            top = " ".join(f"{c}×{k}" for c, k in hits.most_common(12))
            suspects.append((ratio, n, cjk_total, meta_path.parent.name, top))

    suspects.sort(reverse=True)
    print("=== 古典漢語 原文『真簡化字』偵測（精準版）===")
    print(f"掃描 {scanned} 部；命中疑簡體來源 {len(suspects)} 部")
    print(f"真簡化字集大小：{len(TRUE_SIMPLIFIED)} 字；閾值：絕對數>=8 或占比>=0.1%\n")
    if not suspects:
        print("結論：無任何一部含成批真簡化字 → 全部是繁體/文言正統來源。")
        return
    print(f"{'占比':>7}  {'簡字數':>6}  {'全文':>8}  slug  (命中字×次)")
    for ratio, n, total, slug, top in suspects:
        print(f"{ratio:7.2%}  {n:6d}  {total:8d}  {slug}  {top}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
