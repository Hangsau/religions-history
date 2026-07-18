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
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRANSLATIONS_DIR = ROOT / "translations"
ROLE_TRANSLATOR = ROOT / "tools" / "m3-translator-role.md"
ROLE_ANNOTATOR = ROOT / "tools" / "m3-annotator-role.md"
ROLE_TAGGER = ROOT / "tools" / "m3-tagger-role.md"
CONCEPTS_PATH = ROOT / "00-overview" / "concepts.md"
MINIMAX_TOKEN_PATH = Path.home() / ".minimax-token"  # 月費 M3，唯一翻譯後端
RUNTIME_STATE_PATH = ROOT / "logs" / "pipeline-runtime.json"
TZ = timezone(timedelta(hours=8))

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


# Language buckets for the fallback heuristic when is_original_language / text_role are unset.
# 288/365 core metas lack is_original_language, so ordering must degrade gracefully.
# NOTE: 古典中文 = 和合本 中譯本 (translation); 古典漢語 = 佛/道/儒 漢傳原典 (original). Real split in corpus.
_TRANSLATION_LANG_HINTS = ("古典中文", "Latin")  # 和合本 + Vulgate — both are translations

# Languages that are ALREADY Chinese → target language == source, so we preserve verbatim
# and MUST NOT spend a (paid, reasoning) LLM call to echo the text back. 守則「漢傳原樣保留不耗 LLM」。
_CHINESE_LANGS = (
    "古典漢語", "上古漢語", "中古漢語",      # 佛/道/儒 漢傳原典 (original)
    "古典中文", "現代漢語", "現代漢語譯本", "白話文", "中文",  # 和合本等既有中譯 (translation-preserve)
)


def _is_original_text(meta: dict) -> bool:
    """Best-effort original-vs-translation decision, degrading gracefully.

    Priority: text_role (explicit) → is_original_language (explicit) → language heuristic.
    Unknown languages default to original (safe: verbatim-preserve, no lossy re-translation).
    """
    role = meta.get("text_role")
    if role == "translation":
        return False
    if role in ("original", "transliteration", "contested"):
        return True
    if isinstance(meta.get("is_original_language"), bool):
        return meta["is_original_language"]
    lang = (meta.get("source_language") or meta.get("language") or "")
    if lang.startswith("English") or lang in _TRANSLATION_LANG_HINTS:
        return False
    return True  # 古典漢語 / 希伯來 / Greek / Sanskrit / Pali / 未知 → original-priority (verbatim-safe)


def load_slugs_by_tier(tier: str) -> list[str]:
    """Return slugs whose meta.json tier == given value, ordered original-first then short-first.

    Transliteration short-circuits cheaply (verbatim), so we don't special-case its order.
    """
    rows = []  # (not_original, size_bytes, slug)
    for meta_p in sorted(TRANSLATIONS_DIR.glob("*/meta.json")):
        try:
            meta = json.loads(meta_p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if meta.get("tier") != tier:
            continue
        if meta.get("alias_of"):  # 同內容重複份，canonical 才跑，別名跳過
            continue
        slug = meta_p.parent.name
        orig = meta_p.parent / "raw" / "original.txt"
        size = orig.stat().st_size if orig.exists() else 0
        rows.append((0 if _is_original_text(meta) else 1, size, slug))
    rows.sort(key=lambda r: (r[0], r[1], r[2]))
    return [slug for _, _, slug in rows]

MAX_CHARS_PER_CALL = 8000  # m3 input safety; longer → chunk by chapter (larger sizes risk m3 timeouts)
CHUNK_HEADER_RE = "=== "  # chapter boundary marker in original.txt


def load_role(task: str) -> str:
    # 角色檔 header 用 __TRANSLATION_MODEL__ placeholder；填成當前主力 model，避免寫死名稱。
    return TASK_TO_ROLE[task].read_text(encoding="utf-8").replace("__TRANSLATION_MODEL__", PRIMARY_MODEL)


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


def _run_claude(prompt: str, base_url: str, token: str, model: str) -> tuple[str | None, str | None]:
    """跑一次 `claude -p`（Anthropic-相容端點）。回 (stdout, None) 或 (None, err_msg)。"""
    env = os.environ.copy()
    env["ANTHROPIC_BASE_URL"] = base_url
    env["ANTHROPIC_AUTH_TOKEN"] = token
    env["ANTHROPIC_MODEL"] = model
    env["ANTHROPIC_SMALL_FAST_MODEL"] = model
    try:
        result = subprocess.run(
            ["claude", "-p", "--permission-mode", "bypassPermissions"],
            input=prompt.encode("utf-8"),
            capture_output=True,
            # Normal M3 chunks complete in roughly a minute or two.  Do not leave
            # the persistent state as "running" for ten minutes on a stuck quota request.
            timeout=180,
            env=env,
            # Windows: 別讓 claude 這個主控台程式從背景進程彈出黑框視窗
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        if result.returncode != 0:
            return None, f"exit {result.returncode}: {result.stderr.decode('utf-8', errors='replace')[:500]}"
        return result.stdout.decode("utf-8", errors="replace"), None
    except subprocess.TimeoutExpired:
        return None, "timeout after 180s"
    except FileNotFoundError:
        return None, "`claude` CLI not found in PATH"


MINIMAX_ANTHROPIC_URL = "https://api.minimax.io/anthropic"

# ── 翻譯後端：改 model 只改這裡，call_m3 的 log marker、header 標示、刊版顯示全自動跟隨 ──
PRIMARY_MODEL = "MiniMax-M3"          # 主力：月費 Coding Plan，零邊際成本、不吃 Anthropic 配額
# 每次成功都印此 marker 到 stdout→supervisor-run.log；刊版 translation_activity 解析它顯示現用 model。
MODEL_MARKER = "  [model] {name} ({role})"

# 記錄本次 translate_one 實際成功呼叫過的 model（primary / fallback 都算）；
# translate_one 入口清空、call_m3 成功時 add，orchestrator 讀取回填 meta.json translation_models，
# 讓「哪些檔被 fallback 翻過」可稽核（header 標示仍是 PRIMARY_MODEL，此欄才是權威來源）。
LAST_MODELS_USED: set[str] = set()
CURRENT_WORK: dict[str, object] = {"slug": None, "task": None, "chunk": None, "chunks_total": None}


def _write_runtime_state(**changes: object) -> None:
    """Persist pipeline state independently of the GUI/supervisor process."""
    RUNTIME_STATE_PATH.parent.mkdir(exist_ok=True)
    try:
        state = json.loads(RUNTIME_STATE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        state = {}
    state.update(changes)
    state["updated_at"] = datetime.now(TZ).isoformat()
    RUNTIME_STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n",
                                  encoding="utf-8", newline="\n")


def set_current_work(slug: str, task: str, chunk: int | None = None,
                     chunks_total: int | None = None) -> None:
    CURRENT_WORK.update(slug=slug, task=task, chunk=chunk, chunks_total=chunks_total)
    _write_runtime_state(status="running", slug=slug, task=task, chunk=chunk,
                         chunks_total=chunks_total, last_error=None, next_retry_at=None,
                         request_started_at=datetime.now(TZ).isoformat())


def is_waiting_quota() -> bool:
    try:
        return json.loads(RUNTIME_STATE_PATH.read_text(encoding="utf-8")).get("status") == "waiting_quota"
    except (OSError, json.JSONDecodeError):
        return False


def _wait_for_quota(error: str) -> None:
    now = datetime.now(TZ)
    _write_runtime_state(status="waiting_quota", detected_at=now.isoformat(),
                         next_retry_at=(now + timedelta(minutes=5)).isoformat(),
                         retry_attempt=0, last_error=error, **CURRENT_WORK)
    print("  [quota] M3 流量／額度限制；已保留目前 chunk，停止後續工作並等待自動恢復")


def _resolve_backend(model: str) -> tuple[str, str] | None:
    """解析唯一允許的 MiniMax-M3 後端；token 缺失回 None。"""
    if model.lower().startswith("minimax"):
        if MINIMAX_TOKEN_PATH.exists():
            tok = MINIMAX_TOKEN_PATH.read_text(encoding="utf-8").strip()
            if tok:
                return MINIMAX_ANTHROPIC_URL, tok
        return None
    return None


def call_m3(prompt: str, dry_run: bool = False) -> str | None:
    """只呼叫 MiniMax-M3；配額訊號或連續無詳情 exit 1 立即停管線。"""
    sys.stdout.flush()  # ensure prior prints land before subprocess wait
    if dry_run:
        print(f"\n[DRY RUN] prompt length: {len(prompt)} chars\n{'='*60}")
        print(prompt[:2000] + "\n...[truncated]...\n" + prompt[-500:])
        return None

    backend = _resolve_backend(PRIMARY_MODEL)
    if backend is None:
        _wait_for_quota("MiniMax-M3 token unavailable")
        return None
    base_url, token = backend
    blank_exit_ones = 0
    for attempt in range(1, 4):
        out, err = _run_claude(prompt, base_url, token, PRIMARY_MODEL)
        if out is not None:
            print(MODEL_MARKER.format(name=PRIMARY_MODEL, role="primary"))
            LAST_MODELS_USED.add(PRIMARY_MODEL)
            return out
        detail = (err or "").lower()
        if any(x in detail for x in ("429", "quota", "rate limit", "rate_limit", "traffic", "too many requests", "timeout")):
            _wait_for_quota(err or "M3 quota/rate-limit signal")
            return None
        if (err or "").strip() in ("exit 1:", "exit 1: "):
            blank_exit_ones += 1
            print(f"  [warn] {PRIMARY_MODEL} 無詳情 exit 1（{blank_exit_ones}/3）")
            if blank_exit_ones >= 3:
                _wait_for_quota("MiniMax-M3 repeated detail-free exit 1")
                return None
            continue
        print(f"  [warn] {PRIMARY_MODEL} 失敗（{err}）")
        return None
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
    LAST_MODELS_USED.clear()  # 本檔用過哪些 model，供 orchestrator 翻完後回填 meta（純 verbatim 路徑則為空）
    out_name = TASK_TO_OUTFILE[task]
    out_path = TRANSLATIONS_DIR / slug / out_name
    if skip_done and out_path.exists() and out_path.stat().st_size > 100:
        print(f"  [skip-done] {slug} ({task})")
        return True

    loaded = load_scripture(slug)
    if not loaded:
        return False
    original_text, meta = loaded

    # Transliteration short-circuit (e.g. 大悲咒/陀羅尼): 漢字記梵音非表意，禁止意譯。
    # 原樣保留 + 附成書說明；梵文還原/釋義留給 02-annotation.md。不呼叫 M3、不計 quota。
    if task == "translate" and meta.get("text_role") == "transliteration":
        note = meta.get("composition_note") or "音譯文本：漢字記錄原語（多為梵文）讀音，非表意翻譯；此處原樣保留，梵文還原與釋義見 02-annotation.md。"
        body = (f"# {meta.get('name_zh', slug)} — 原文（音譯保留）\n\n"
                f"> **text_role: transliteration** — {note}\n\n"
                f"> 本檔依守則「音譯不意譯」原樣保留原文；不做白話翻譯。\n\n"
                f"---\n\n{original_text}")
        if dry_run:
            print(f"  [dry-run transliteration] {slug}: would write verbatim ({len(body)} chars)")
            return True
        out_path.write_text(body + "\n", encoding="utf-8", newline="\n")
        print(f"  [transliteration] {slug}: verbatim preserved → {out_name} ({len(body)} chars, no M3 call)")
        return True

    # Chinese-source short-circuit: 原文本身即中文（漢傳原典 / 和合本等中譯）→ 目標語==來源語，
    # 依守則「古典漢語原樣保留 / 中譯本不重譯」原樣寫出，不呼叫 LLM（省 reasoning token、避免 LLM 竄改原文）。
    if task == "translate":
        src_lang = (meta.get("source_language") or meta.get("language") or "").strip()
        if src_lang in _CHINESE_LANGS:
            role_label = "中譯本原樣保留" if src_lang in _TRANSLATION_LANG_HINTS else "漢語原文原樣保留"
            body = (f"# {meta.get('name_zh', slug)} — 翻譯\n\n"
                    f"> 原文：`raw/original.txt`\n"
                    f"> 原文語言：{src_lang}\n"
                    f"> 翻譯：原樣保留（本身已是中文，不呼叫 LLM）\n"
                    f"> 說明：{role_label}\n"
                    f"> 守則：見 `tools/m3-translator-role.md`\n"
                    f"> 註釋見：`02-annotation.md`\n\n"
                    f"---\n\n{original_text}")
            if dry_run:
                print(f"  [dry-run zh-verbatim] {slug}: would write verbatim ({len(body)} chars)")
                return True
            out_path.write_text(body + "\n", encoding="utf-8", newline="\n")
            print(f"  [zh-verbatim] {slug}: {src_lang} 原樣保留 → {out_name} ({len(body)} chars, no LLM call)")
            return True

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
        set_current_work(slug, task)
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
        set_current_work(slug, task, i, len(groups))
        output = call_m3(prompt, dry_run=dry_run)
        if output is None:
            print(f"    [warn] chunk {i} failed for {slug} ({task}); keeping prior file unchanged")
            return False
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
        set_current_work(slug, "tag")
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
            set_current_work(slug, "tag", i, len(groups))
            output = call_m3(prompt, dry_run=dry_run)
            if output is None:
                if is_waiting_quota():
                    return False
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
