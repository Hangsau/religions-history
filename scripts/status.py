#!/usr/bin/env python
"""
統一狀態看板：一個指令看到收集 / 翻譯 / 對齊分類 的全貌。

pull-based，無 daemon：隨時跑 `python scripts/status.py` 取當下快照。
同時印到終端 + 寫 00-overview/STATUS.md（GitHub 上也看得到）。

Usage:
  PYTHONIOENCODING=utf-8 python scripts/status.py
"""

import json
import subprocess
from collections import Counter
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRANSLATIONS_DIR = ROOT / "translations"
LOGS = ROOT / "logs"
OUT = ROOT / "00-overview" / "STATUS.md"

ALIGN_FIELDS = [
    ("text_role", "文本角色"),
    ("is_original_language", "原文/譯文"),
    ("era", "成書時期"),
    ("genre", "文類"),
    ("semantic_tags", "語義標籤"),
    ("psych_tags", "心理讀經標籤"),
    ("keywords", "關鍵詞"),
]


def bar(pct: float, width: int = 24) -> str:
    n = round(pct / 100 * width)
    return "█" * n + "·" * (width - n)


def load_all() -> list[dict]:
    out = []
    for p in sorted(TRANSLATIONS_DIR.glob("*/meta.json")):
        try:
            out.append(json.loads(p.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            continue
    return out


def filled(v) -> bool:
    return v not in (None, "", [], {})


def semantic_complete(meta: dict) -> bool:
    return meta.get("tag_status") == "done" and filled(meta.get("semantic_tags"))


def psych_complete(meta: dict) -> bool:
    return meta.get("psych_tag_status") == "done" and filled(meta.get("psych_tags"))


def translation_file_complete(path: Path) -> bool:
    if not path.exists() or path.stat().st_size <= 100:
        return False
    try:
        return "<!-- CHUNK " not in path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False


def translation_complete(meta: dict, translations_dir: Path = TRANSLATIONS_DIR) -> bool:
    slug = meta.get("slug")
    return (isinstance(slug, str) and meta.get("translation_status") == "done"
            and translation_file_complete(translations_dir / slug / "01-translation.md"))


def field_complete(meta: dict, key: str) -> bool:
    if key in {"semantic_tags", "keywords"}:
        return semantic_complete(meta) and filled(meta.get(key))
    if key == "psych_tags":
        return psych_complete(meta)
    return filled(meta.get(key))


def classification_complete(meta: dict) -> bool:
    return (filled(meta.get("era")) and filled(meta.get("genre"))
            and semantic_complete(meta) and psych_complete(meta))


def git_recent(n: int = 6) -> list[str]:
    try:
        r = subprocess.run(["git", "log", f"-{n}", "--oneline", "--no-decorate"],
                           cwd=ROOT, capture_output=True, text=True,
                           encoding="utf-8", errors="replace",
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return [l for l in r.stdout.splitlines() if l.strip()]
    except Exception:  # noqa: BLE001
        return []


def log_tail(name: str) -> str:
    p = LOGS / name
    if not p.exists():
        return "（無日誌）"
    try:
        lines = [l for l in p.read_text(encoding="utf-8", errors="replace").splitlines() if l.strip()]
        return lines[-1] if lines else "（空）"
    except OSError:
        return "（讀取失敗）"


def log_ok_count(name: str) -> int:
    p = LOGS / name
    if not p.exists():
        return 0
    try:
        return sum(1 for l in p.read_text(encoding="utf-8", errors="replace").splitlines() if "[ok]" in l)
    except OSError:
        return 0


def build() -> str:
    metas = load_all()
    n = len(metas)
    ts = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S +0800")
    total_bytes = sum(m.get("size_bytes") or 0 for m in metas)
    religions = len({m.get("religion") for m in metas})

    L = []
    L.append("# STATUS — religions-history 統一看板")
    L.append("")
    L.append(f"> 由 `scripts/status.py` 產生（pull-based 快照，勿手改）。更新：{ts}")
    L.append("")
    L.append(f"**{n} 部 / {religions} 宗教 / {total_bytes/1024/1024:.0f} MB**")
    L.append("")

    # ---- 對齊覆蓋率 ----
    L.append("## 對齊覆蓋率（欄位回填進度）")
    L.append("")
    L.append("| 欄位 | 已填 | 覆蓋率 | |")
    L.append("|------|------|--------|---|")
    for key, label in ALIGN_FIELDS:
        c = sum(1 for m in metas if field_complete(m, key))
        pct = 100 * c / n if n else 0
        L.append(f"| {label} `{key}` | {c}/{n} | {pct:5.1f}% | `{bar(pct)}` |")
    L.append("")

    # ---- 分類進度 by tier（兩條標籤軸皆齊全）----
    L.append("## M3 分類進度（era+genre+semantic+psych 齊全）")
    L.append("")
    tiers = ["核心", "次要", "總集"]
    tier_tot = Counter(m.get("tier") for m in metas)
    L.append("| tier | 完成 | 總數 | |")
    L.append("|------|------|------|---|")
    for t in tiers:
        tot = tier_tot.get(t, 0)
        done = sum(1 for m in metas if m.get("tier") == t and classification_complete(m))
        pct = 100 * done / tot if tot else 0
        L.append(f"| {t} | {done} | {tot} | `{bar(pct)}` {pct:4.0f}% |")
    L.append("")

    # ---- 翻譯進度 ----
    tr_done = sum(1 for m in metas if translation_complete(m))
    L.append("## 翻譯進度")
    L.append("")
    L.append(f"- metadata done 且完整檔案通過：**{tr_done} / {n}** 部已翻譯（`01-translation.md`）")
    L.append("")

    # ---- 收集 / 下載（Pipeline A）----
    import time as _time
    now = _time.time()
    paths = list(TRANSLATIONS_DIR.glob("*/meta.json"))
    L.append("## 收集 / 下載（Pipeline A）")
    L.append("")
    if paths:
        newest = max(paths, key=lambda p: p.stat().st_mtime)
        landed = sum(1 for p in paths if now - p.stat().st_mtime < 1800)
        ago_m = int((now - newest.stat().st_mtime) / 60)
        L.append(f"- 最新收錄：`{newest.parent.name}`（{ago_m} 分前）· 近 30 分 **+{landed}** 部")
    dl_logs = list(LOGS.glob("pipeline-a*.log"))
    if dl_logs:
        active = max(dl_logs, key=lambda p: p.stat().st_mtime)
        L.append(f"- 下載日誌 `{active.name}`：`{log_tail(active.name)}`")
    L.append("")

    # ---- 背景管線 ----
    L.append("## 背景管線快照")
    L.append("")
    L.append(f"- **分類（classify-metadata）**：日誌已分類 {log_ok_count('classify-core.log')} 部")
    L.append(f"  - 最新：`{log_tail('classify-core.log')}`")
    ps = ROOT / "00-overview" / "PIPELINE_STATUS.md"
    if ps.exists():
        for line in ps.read_text(encoding="utf-8").splitlines():
            if (line.startswith("- 進度") or line.startswith("- 目前處理")
                    or line.startswith("- P0 尚未") or line.startswith("- 一般失敗")
                    or line.startswith("- 已阻塞")):
                L.append(f"- **翻譯管線**：{line.lstrip('- ')}")
    L.append("")

    # ---- 最近 commits ----
    L.append("## 最近 git 提交")
    L.append("")
    for c in git_recent():
        L.append(f"- `{c}`")
    L.append("")

    return "\n".join(L) + "\n"


def main():
    md = build()
    OUT.write_text(md, encoding="utf-8", newline="\n")
    print(md)
    print(f"[written] {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
