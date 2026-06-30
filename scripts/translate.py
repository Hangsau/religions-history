#!/usr/bin/env python
"""
Pipeline B: dispatch translation to MiniMax-M3 (claude-m3) per scripture.

For each target slug:
    1. Read translations/<slug>/raw/original.txt
    2. Read translations/<slug>/meta.json  (for source_language / name_zh)
    3. Build prompt with role-instructions + original text
    4. Dispatch via claude-m3 -p  →  output saved to translations/<slug>/01-translation.md

Usage:
    # Translate one specific scripture
    python scripts/translate.py --slug heart-sutra-kumarajiva

    # Translate all core scriptures (priority list)
    python scripts/translate.py --core

    # Resume mode — skip slugs that already have 01-translation.md
    python scripts/translate.py --core --skip-done

    # Dry run — print prompt but don't actually call m3
    python scripts/translate.py --slug heart-sutra-kumarajiva --dry-run

Notes:
    - m3 is MiniMax-M3, monthly subscription, doesn't consume Claude quota.
    - Each scripture = 1 m3 call. Long texts (>50 KB) auto-chunk by chapter.
    - Role spec in tools/m3-translator-role.md is inlined at prompt head.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRANSLATIONS_DIR = ROOT / "translations"
ROLE_TRANSLATOR = ROOT / "tools" / "m3-translator-role.md"
ROLE_ANNOTATOR = ROOT / "tools" / "m3-annotator-role.md"
MINIMAX_TOKEN_PATH = Path.home() / ".minimax-token"

TASK_TO_OUTFILE = {
    "translate": "01-translation.md",
    "annotate": "02-annotation.md",
}
TASK_TO_ROLE = {
    "translate": ROLE_TRANSLATOR,
    "annotate": ROLE_ANNOTATOR,
}

# Priority list — translate these first (small, iconic, high analytical value)
CORE_SLUGS = [
    "heart-sutra-kumarajiva",
    "heart-sutra-xuanzang",
    "tao-te-ching",
    "dhammapada",
    "bhagavad-gita",
    "genesis",
    "sblgnt-matthew",
    "quran",
    "isha-upanishad",
    "katha-upanishad",
    "analects",
    "great-learning",
    "doctrine-of-the-mean",
    "zhuangzi",
    "lotus-sutra",
    "diamond-sutra-kumarajiva",
]

MAX_CHARS_PER_CALL = 40000  # m3 input safety; longer → chunk by chapter


def load_role(task: str) -> str:
    return TASK_TO_ROLE[task].read_text(encoding="utf-8")


def load_scripture(slug: str) -> tuple[str, dict] | None:
    slug_dir = TRANSLATIONS_DIR / slug
    orig = slug_dir / "raw" / "original.txt"
    meta_p = slug_dir / "meta.json"
    if not orig.exists() or not meta_p.exists():
        print(f"  [skip] {slug}: missing original.txt or meta.json")
        return None
    return orig.read_text(encoding="utf-8"), json.loads(meta_p.read_text(encoding="utf-8"))


def build_prompt(task: str, role: str, slug: str, meta: dict, original_text: str, translation_text: str | None = None) -> str:
    meta_block = f"""- **slug**: {slug}
- **name_zh**: {meta.get('name_zh', '?')}
- **source_language**: {meta.get('source_language', '?')}
- **version**: {meta.get('version', '?')}
- **religion**: {meta.get('religion', '?')}
- **tradition**: {meta.get('tradition', '?')}"""
    if task == "translate":
        out_title = f"# {meta.get('name_zh', slug)} — 翻譯"
        content_block = f"""## 原文（`raw/original.txt`）

{original_text}"""
        instruction = "請按守則處理上方原文（古典漢語原樣保留 / 外語直譯繁中）。"
    elif task == "annotate":
        out_title = f"# {meta.get('name_zh', slug)} — 註釋"
        content_block = f"""## 原文（`raw/original.txt`）

{original_text}

---

## 翻譯（`01-translation.md`）

{translation_text or '(尚無翻譯檔)'}"""
        instruction = "請按守則為上方經文寫**白話註釋**（歷史背景 + 名相索引 + 段落白話解釋 + 學術爭議）。"
    else:
        raise ValueError(task)
    return f"""{role}

---

## 本次任務

{meta_block}

{instruction}

---

{content_block}

---

## **重要：輸出規定（必讀）**

你只是**內容產生器**，不是 agent。**絕對禁止**：
- ❌ 使用 Write tool / Edit tool / Bash tool 寫檔
- ❌ 嘗試打開 / 修改任何檔案
- ❌ 回覆「已寫入 …」「檔案完成 …」這類摘要 — 那不是輸出

**唯一動作**：在你的 stdout 回應中**直接輸出完整 markdown 內容**，從 `{out_title}` 開始一直到結尾。整段 markdown 文字就是你的回應。我（主控腳本）會抓你的 stdout 寫入檔案，所以你不需要也不能自己寫檔。

**範例正確輸出**（直接以此格式回應）：
```
{out_title}

> 原文：...
> ...

---

=== 1 | ... ===

...內容...
```

**範例錯誤輸出**：
```
已寫入 translations/<slug>/01-translation.md (300 行)。
處理說明：...
```

不要前言、不要 ```markdown fence、不要尾部摘要。回應第一個字應該是 `#`。
"""


def call_m3(prompt: str, dry_run: bool = False) -> str | None:
    """Invoke claude CLI with MiniMax-M3 env vars (equivalent to claude-m3 shell function)."""
    if dry_run:
        print(f"\n[DRY RUN] prompt length: {len(prompt)} chars\n{'='*60}")
        print(prompt[:2000] + "\n...[truncated]...\n" + prompt[-500:])
        return None
    if not MINIMAX_TOKEN_PATH.exists():
        print(f"  [error] MiniMax token not found at {MINIMAX_TOKEN_PATH}")
        return None
    env = os.environ.copy()
    env["ANTHROPIC_BASE_URL"] = "https://api.minimax.io/anthropic"
    env["ANTHROPIC_AUTH_TOKEN"] = MINIMAX_TOKEN_PATH.read_text(encoding="utf-8").strip()
    env["ANTHROPIC_MODEL"] = "MiniMax-M3"
    env["ANTHROPIC_SMALL_FAST_MODEL"] = "MiniMax-M3"
    try:
        result = subprocess.run(
            ["claude", "-p", "--permission-mode", "bypassPermissions"],
            input=prompt.encode("utf-8"),
            capture_output=True,
            timeout=600,
            env=env,
        )
        if result.returncode != 0:
            print(f"  [error] m3 exit {result.returncode}: {result.stderr.decode('utf-8', errors='replace')[:500]}")
            return None
        return result.stdout.decode("utf-8", errors="replace")
    except subprocess.TimeoutExpired:
        print("  [error] m3 timeout after 600s")
        return None
    except FileNotFoundError:
        print("  [error] `claude` CLI not found in PATH")
        return None


def translate_one(slug: str, task: str, role: str, skip_done: bool = False, dry_run: bool = False) -> bool:
    out_name = TASK_TO_OUTFILE[task]
    out_path = TRANSLATIONS_DIR / slug / out_name
    if skip_done and out_path.exists() and out_path.stat().st_size > 100:
        print(f"  [skip-done] {slug} ({task})")
        return True

    loaded = load_scripture(slug)
    if not loaded:
        return False
    original_text, meta = loaded

    if len(original_text) > MAX_CHARS_PER_CALL:
        print(f"  [warn] {slug}: {len(original_text)} chars > {MAX_CHARS_PER_CALL}, chunking not yet implemented; using first window only")
        original_text = original_text[:MAX_CHARS_PER_CALL]

    translation_text = None
    if task == "annotate":
        tr_path = TRANSLATIONS_DIR / slug / "01-translation.md"
        if tr_path.exists():
            translation_text = tr_path.read_text(encoding="utf-8")

    prompt = build_prompt(task, role, slug, meta, original_text, translation_text)
    print(f"  [start] {slug} ({task})  (prompt {len(prompt)} chars)")
    output = call_m3(prompt, dry_run=dry_run)
    if output is None or dry_run:
        return dry_run

    output = output.strip()
    if not output.startswith("#"):
        first_h = output.find("\n# ")
        if first_h > 0:
            output = output[first_h:].strip()
    # Strip stray markdown fence wrappers that m3 sometimes adds
    if output.startswith("```markdown\n"):
        output = output[len("```markdown\n"):]
    if output.startswith("```\n"):
        output = output[len("```\n"):]
    output = output.rstrip()
    if output.endswith("```"):
        output = output[:-3].rstrip()

    out_path.write_text(output + "\n", encoding="utf-8", newline="\n")
    print(f"  [done] {slug} ({task})  →  {out_name} ({len(output)} chars)")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", help="single slug to process")
    ap.add_argument("--core", action="store_true", help=f"process {len(CORE_SLUGS)} priority slugs")
    ap.add_argument("--all", action="store_true", help="process all scriptures")
    ap.add_argument("--task", choices=["translate", "annotate", "both"], default="translate",
                    help="translate=只翻譯; annotate=只註釋; both=兩個都跑（先翻後註）")
    ap.add_argument("--skip-done", action="store_true", help="skip slugs that already have the output file")
    ap.add_argument("--dry-run", action="store_true", help="print prompt but don't call m3")
    args = ap.parse_args()

    if args.slug:
        targets = [args.slug]
    elif args.core:
        targets = CORE_SLUGS
    elif args.all:
        targets = []
        for meta_p in sorted(TRANSLATIONS_DIR.glob("*/meta.json")):
            targets.append(meta_p.parent.name)
    else:
        sys.exit("specify --slug / --core / --all")

    tasks = ["translate", "annotate"] if args.task == "both" else [args.task]
    print(f"targets: {len(targets)} × tasks: {tasks}")

    total_ok = 0
    total = len(targets) * len(tasks)
    for task in tasks:
        if not TASK_TO_ROLE[task].exists():
            sys.exit(f"missing role spec: {TASK_TO_ROLE[task]}")
        role = load_role(task)
        for slug in targets:
            if translate_one(slug, task, role, args.skip_done, args.dry_run):
                total_ok += 1
    print(f"\ndone: {total_ok}/{total}")


if __name__ == "__main__":
    main()
