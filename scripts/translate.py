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
ROLE_TAGGER = ROOT / "tools" / "m3-tagger-role.md"
CONCEPTS_PATH = ROOT / "00-overview" / "concepts.md"
MINIMAX_TOKEN_PATH = Path.home() / ".minimax-token"

TASK_TO_OUTFILE = {
    "translate": "01-translation.md",
    "annotate": "02-annotation.md",
}
TASK_TO_ROLE = {
    "translate": ROLE_TRANSLATOR,
    "annotate": ROLE_ANNOTATOR,
    "tag": ROLE_TAGGER,
}


def load_tag_whitelist() -> set[str]:
    """Parse the controlled-vocabulary tags (backtick code-spans) from concepts.md."""
    if not CONCEPTS_PATH.exists():
        return set()
    import re as _re
    text = CONCEPTS_PATH.read_text(encoding="utf-8")
    # tags look like `ultimate-reality` — lowercase words joined by hyphens
    return set(_re.findall(r"`([a-z][a-z0-9-]+)`", text))


def load_slugs_by_tier(tier: str) -> list[str]:
    """Return slugs whose meta.json tier == given value, sorted."""
    out = []
    for meta_p in sorted(TRANSLATIONS_DIR.glob("*/meta.json")):
        try:
            meta = json.loads(meta_p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if meta.get("tier") == tier:
            out.append(meta_p.parent.name)
    return out

MAX_CHARS_PER_CALL = 8000  # m3 input safety; longer → chunk by chapter (larger sizes risk m3 timeouts)
CHUNK_HEADER_RE = "=== "  # chapter boundary marker in original.txt


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
    source_language = meta.get("source_language") or meta.get("language", "?")
    meta_block = f"""- **slug**: {slug}
- **name_zh**: {meta.get('name_zh', '?')}
- **source_language**: {source_language}
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
    sys.stdout.flush()  # ensure prior prints land before subprocess wait
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


def split_chapters(original_text: str) -> list[str]:
    """Split original.txt on `=== N | label ===` boundaries.
    Returns list of chunks where each chunk starts with `=== ...`."""
    lines = original_text.split("\n")
    chunks = []
    current = []
    for line in lines:
        if line.startswith(CHUNK_HEADER_RE):
            if current:
                chunks.append("\n".join(current))
            current = [line]
        else:
            current.append(line)
    if current:
        chunks.append("\n".join(current))
    return chunks


def group_chunks(chapters: list[str], max_chars: int) -> list[list[str]]:
    """Pack chapters into groups, each group totaling <= max_chars."""
    groups = []
    cur_group: list[str] = []
    cur_size = 0
    for ch in chapters:
        ch_size = len(ch) + 1  # +1 for \n joiner
        if ch_size > max_chars:
            # single chapter exceeds limit — split it raw
            if cur_group:
                groups.append(cur_group)
                cur_group, cur_size = [], 0
            # naive split
            for i in range(0, len(ch), max_chars):
                groups.append([ch[i:i + max_chars]])
            continue
        if cur_size + ch_size > max_chars and cur_group:
            groups.append(cur_group)
            cur_group, cur_size = [], 0
        cur_group.append(ch)
        cur_size += ch_size
    if cur_group:
        groups.append(cur_group)
    return groups


def strip_output_wrappers(output: str) -> str:
    output = output.strip()
    if not output.startswith("#"):
        first_h = output.find("\n# ")
        if first_h > 0:
            output = output[first_h:].strip()
    if output.startswith("```markdown\n"):
        output = output[len("```markdown\n"):]
    if output.startswith("```\n"):
        output = output[len("```\n"):]
    output = output.rstrip()
    if output.endswith("```"):
        output = output[:-3].rstrip()
    return output


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

    translation_text = None
    if task == "annotate":
        tr_path = TRANSLATIONS_DIR / slug / "01-translation.md"
        if tr_path.exists():
            translation_text = tr_path.read_text(encoding="utf-8")
        else:
            print(f"  [error] {slug} (annotate): 01-translation.md not yet exists; run --task translate first")
            return False

    # The text we chunk: original for translate, translation for annotate
    # (annotation should reason over the translated/preserved Chinese form, not the raw source language)
    chunkable_text = original_text if task == "translate" else translation_text
    aux_text = None if task == "translate" else original_text  # not actively chunked, just for reference

    # Single-call path: text fits
    if len(chunkable_text) <= MAX_CHARS_PER_CALL:
        prompt = build_prompt(task, role, slug, meta, chunkable_text, translation_text)
        print(f"  [start] {slug} ({task})  (prompt {len(prompt)} chars)")
        output = call_m3(prompt, dry_run=dry_run)
        if output is None or dry_run:
            return dry_run
        output = strip_output_wrappers(output)
        out_path.write_text(output + "\n", encoding="utf-8", newline="\n")
        print(f"  [done] {slug} ({task})  →  {out_name} ({len(output)} chars)")
        return True

    # Chunked path
    chapters = split_chapters(chunkable_text)
    groups = group_chunks(chapters, MAX_CHARS_PER_CALL - 5000)  # reserve room for role+prompt
    print(f"  [chunk] {slug} ({task}): {len(chapters)} chapters → {len(groups)} chunks")

    parts: list[str] = []
    for i, group in enumerate(groups, 1):
        chunk_text = "\n".join(group)
        chunk_meta_note = f"\n\n**注意：本經分 {len(groups)} 段處理，這是第 {i}/{len(groups)} 段。請只處理本段內容，標題列只在第 1 段需要，後續段直接從 `=== N | label ===` 開始即可。**"
        # For annotate, pass chunk as the "translation" to annotate (since we're chunking the translation now)
        if task == "translate":
            prompt = build_prompt(task, role, slug, meta, chunk_text + chunk_meta_note, translation_text)
        else:
            # Annotation: chunk_text is the translation chunk; original is not actively passed in chunked mode
            prompt = build_prompt(task, role, slug, meta, "(原文略，見原文檔)", chunk_text + chunk_meta_note)
        print(f"    [chunk {i}/{len(groups)}] {slug} ({task})  ({len(chunk_text)} chars)")
        output = call_m3(prompt, dry_run=dry_run)
        if output is None:
            print(f"    [warn] chunk {i} failed for {slug} ({task}); marking placeholder + continuing")
            parts.append(f"\n<!-- CHUNK {i}/{len(groups)} FAILED — retry needed -->\n")
            continue
        if dry_run:
            continue
        output = strip_output_wrappers(output)
        if i > 1:
            # Strip duplicate title header from later chunks
            lines = output.split("\n")
            for j, line in enumerate(lines):
                if line.startswith(CHUNK_HEADER_RE):
                    output = "\n".join(lines[j:])
                    break
        parts.append(output)

    if dry_run:
        return True
    final = "\n\n".join(parts)
    out_path.write_text(final + "\n", encoding="utf-8", newline="\n")
    print(f"  [done] {slug} ({task})  →  {out_name} ({len(final)} chars, {len(groups)} chunks)")
    return True


def build_tag_prompt(role: str, slug: str, meta: dict, text: str, whitelist: set[str], chunk_note: str = "") -> str:
    source_language = meta.get("source_language") or meta.get("language", "?")
    vocab = " ".join(sorted(whitelist))
    return f"""{role}

---

## 本次任務

- **slug**: {slug}
- **name_zh**: {meta.get('name_zh', '?')}
- **religion**: {meta.get('religion', '?')}
- **source_language**: {source_language}

## semantic_tags 受控詞彙白名單（只能從這裡選，表外詞一律放 keywords）

{vocab}

{chunk_note}

---

## 待標記文本

{text}

---

## **輸出規定（必讀）**

你只是 JSON 產生器。**唯一動作**：在 stdout 直接輸出一個 JSON 物件，格式：

{{"semantic_tags": ["tag-a", "tag-b"], "keywords": ["關鍵詞1", "神名", "地名", "主題詞"]}}

- `semantic_tags`：**只能**填上方白名單內的英文 tag，挑真正切題的 3–8 個，表外詞禁止放這。
- `keywords`：5–15 個自由詞（神名 / 地名 / 關鍵術語 / 核心主題），繁中或原文皆可，供搜尋用。
- 不要 markdown fence、不要前言、不要解釋。第一個字元是 `{{`，最後一個是 `}}`。
"""


def parse_tag_json(output: str) -> dict | None:
    """Extract first {...} JSON object from M3 output."""
    output = output.strip()
    start = output.find("{")
    end = output.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        obj = json.loads(output[start:end + 1])
    except json.JSONDecodeError:
        return None
    if not isinstance(obj, dict):
        return None
    return obj


def merge_meta_tags(slug: str, semantic_tags: list[str], keywords: list[str]) -> None:
    """Merge tags into meta.json, preserving all existing fields + verify.py's format."""
    meta_p = TRANSLATIONS_DIR / slug / "meta.json"
    meta = json.loads(meta_p.read_text(encoding="utf-8"))
    meta["semantic_tags"] = semantic_tags
    meta["keywords"] = keywords
    meta["tag_status"] = "done"
    meta_p.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8", newline="\n")


def tag_one(slug: str, role: str, whitelist: set[str], skip_done: bool = False, dry_run: bool = False) -> bool:
    slug_dir = TRANSLATIONS_DIR / slug
    meta_p = slug_dir / "meta.json"
    if not meta_p.exists():
        print(f"  [skip] {slug} (tag): no meta.json")
        return False
    meta = json.loads(meta_p.read_text(encoding="utf-8"))
    if skip_done and meta.get("tag_status") == "done" and meta.get("semantic_tags"):
        print(f"  [skip-done] {slug} (tag)")
        return True

    # Prefer the Chinese translation (compact) as tagging source; fall back to original
    tr_path = slug_dir / "01-translation.md"
    orig_path = slug_dir / "raw" / "original.txt"
    if tr_path.exists() and tr_path.stat().st_size > 100:
        text = tr_path.read_text(encoding="utf-8")
    elif orig_path.exists():
        text = orig_path.read_text(encoding="utf-8")
    else:
        print(f"  [skip] {slug} (tag): no translation or original")
        return False

    sem: set[str] = set()
    kw: list[str] = []

    def ingest(obj: dict) -> None:
        for t in obj.get("semantic_tags", []) or []:
            if isinstance(t, str) and t in whitelist:
                sem.add(t)
        for k in obj.get("keywords", []) or []:
            if isinstance(k, str) and k.strip() and k not in kw:
                kw.append(k.strip())

    # Chunk if large; union tags across chunks
    if len(text) <= MAX_CHARS_PER_CALL:
        prompt = build_tag_prompt(role, slug, meta, text, whitelist)
        print(f"  [start] {slug} (tag)  (prompt {len(prompt)} chars)")
        output = call_m3(prompt, dry_run=dry_run)
        if output is None or dry_run:
            return dry_run
        obj = parse_tag_json(output)
        if obj is None:
            print(f"  [error] {slug} (tag): unparseable JSON")
            return False
        ingest(obj)
    else:
        chapters = split_chapters(text)
        groups = group_chunks(chapters, MAX_CHARS_PER_CALL - 5000)
        print(f"  [chunk] {slug} (tag): {len(chapters)} chapters → {len(groups)} chunks")
        got_any = False
        for i, group in enumerate(groups, 1):
            chunk_text = "\n".join(group)
            note = f"**本經分 {len(groups)} 段，這是第 {i}/{len(groups)} 段，只針對本段抽標籤。**"
            prompt = build_tag_prompt(role, slug, meta, chunk_text, whitelist, note)
            print(f"    [chunk {i}/{len(groups)}] {slug} (tag)")
            output = call_m3(prompt, dry_run=dry_run)
            if output is None:
                continue
            obj = parse_tag_json(output)
            if obj:
                ingest(obj)
                got_any = True
        if not got_any and not dry_run:
            print(f"  [error] {slug} (tag): all chunks failed")
            return False

    if dry_run:
        return True
    semantic_tags = sorted(sem)
    keywords = kw[:15]
    merge_meta_tags(slug, semantic_tags, keywords)
    print(f"  [done] {slug} (tag)  →  {len(semantic_tags)} tags, {len(keywords)} keywords")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", help="single slug to process")
    ap.add_argument("--core", action="store_true", help="process all tier=核心 slugs (from meta.json)")
    ap.add_argument("--tier", help="process all slugs of a given tier (核心/次要/總集)")
    ap.add_argument("--all", action="store_true", help="process all scriptures")
    ap.add_argument("--task", choices=["translate", "annotate", "tag", "both"], default="translate",
                    help="translate=只翻譯; annotate=只註釋; tag=抽標籤; both=先翻後註")
    ap.add_argument("--skip-done", action="store_true", help="skip slugs already done")
    ap.add_argument("--dry-run", action="store_true", help="print prompt but don't call m3")
    args = ap.parse_args()

    if args.slug:
        targets = [args.slug]
    elif args.core:
        targets = load_slugs_by_tier("核心")
    elif args.tier:
        targets = load_slugs_by_tier(args.tier)
    elif args.all:
        targets = [p.parent.name for p in sorted(TRANSLATIONS_DIR.glob("*/meta.json"))]
    else:
        sys.exit("specify --slug / --core / --tier / --all")

    tasks = ["translate", "annotate"] if args.task == "both" else [args.task]
    print(f"targets: {len(targets)} × tasks: {tasks}")

    whitelist = load_tag_whitelist() if "tag" in tasks else set()
    total_ok = 0
    total = len(targets) * len(tasks)
    for task in tasks:
        if not TASK_TO_ROLE[task].exists():
            sys.exit(f"missing role spec: {TASK_TO_ROLE[task]}")
        role = load_role(task)
        for slug in targets:
            if task == "tag":
                ok = tag_one(slug, role, whitelist, args.skip_done, args.dry_run)
            else:
                ok = translate_one(slug, task, role, args.skip_done, args.dry_run)
            if ok:
                total_ok += 1
    print(f"\ndone: {total_ok}/{total}")


if __name__ == "__main__":
    main()
