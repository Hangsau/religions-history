#!/usr/bin/env python
"""
Layer 2 alignment: classify era + genre + semantic_tags + keywords from ORIGINALS.

One M3 call per text (title + head of raw/original.txt) returns all four fields
(+ is_original_language ONLY for ambiguous Latin). Decoupled from translation —
reads raw/original.txt directly, does NOT need 01-translation.md.

Token discipline (user is quota-conscious but "burn it well"):
  - one call per text, not four
  - reads only title + first MAX_HEAD_CHARS of the original (classification needs
    the opening + title, not the whole scripture)
  - skips texts whose target fields are already filled
  - whitelist-filters era (7) / genre (11) / semantic_tags (concepts.md); hallucinated
    values are dropped
  - core tier first, batch commit+push so a quota cutoff loses nothing

Only edits meta.json (never raw/original.txt) → SHA-256 preserved. Re-reads each
meta right before writing so concurrent pipeline writes are not clobbered.

Usage:
  PYTHONIOENCODING=utf-8 python scripts/classify-metadata.py --tier 核心
  PYTHONIOENCODING=utf-8 python scripts/classify-metadata.py --tier 核心 --limit 3 --dry-run
  PYTHONIOENCODING=utf-8 python scripts/classify-metadata.py --all --batch 25
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

import translate  # reuse call_m3, load_tag_whitelist, parse_tag_json, load_slugs_by_tier
from pipeline_lock import acquire_run_lock, release_run_lock

ROOT = Path(__file__).resolve().parent.parent
TRANSLATIONS_DIR = ROOT / "translations"

ERA_VOCAB = {
    "bronze-age", "axial-age", "classical-antiquity", "medieval",
    "early-modern", "modern", "undated-traditional",
}
GENRE_VOCAB = {
    "scripture-revealed", "law-code", "commentary", "epic-myth", "hymn-liturgy",
    "wisdom-aphorism", "prophecy-apocalypse", "philosophy-doctrine",
    "hagiography-history", "incantation-magic", "folk-ethnography",
}

MAX_HEAD_CHARS = 6000  # opening slice of original.txt fed to M3 for classification


def needs_classify(meta: dict) -> bool:
    if not meta.get("era"):
        return True
    if not meta.get("genre"):
        return True
    if meta.get("tag_status") != "done" or not meta.get("semantic_tags"):
        return True
    if meta.get("psych_tag_status") != "done" or not meta.get("psych_tags"):
        return True
    # Latin is_original ambiguity: resolve here rather than leaving for human.
    if (meta.get("language") or "").strip() == "Latin" and meta.get("is_original_language") is None:
        return True
    return False


def build_prompt(meta: dict, head: str, tag_vocab: set[str], psych_vocab: set[str]) -> str:
    lang = meta.get("language") or ""
    ask_iol = lang.strip() == "Latin" and meta.get("is_original_language") is None
    era_list = " ".join(sorted(ERA_VOCAB))
    genre_list = " ".join(sorted(GENRE_VOCAB))
    vocab = " ".join(sorted(tag_vocab))
    psych = " ".join(sorted(psych_vocab))
    iol_line = (
        '\n- `is_original_language`：此文本語言為 Latin。若為 Vulgate 等「從希伯來/希臘譯成拉丁」的譯本填 false；'
        '若為直接以拉丁文寫成的原典（教父著作、羅馬宗教文本等）填 true。無法判斷則省略此欄。'
        if ask_iol else ""
    )
    iol_field = ', "is_original_language": true' if ask_iol else ""
    return f"""你是宗教文獻分類器。根據下列文本的標題與開頭，輸出結構化分類。

宗教：{meta.get('religion')}　傳統：{meta.get('tradition')}　語言：{lang}
標題：{meta.get('name_zh')} / {meta.get('name_en')} / {meta.get('name_original')}

--- 文本開頭（節錄）---
{head}
--- 節錄結束 ---

## 只能從封閉詞彙選（表外值一律不要輸出）

era（成書時期，單值）：{era_list}
  - bronze-age=青銅時代~3000–1200BCE；axial-age=軸心時代~800–200BCE；
    classical-antiquity=古典晚期~200BCE–600CE；medieval=中古~600–1500CE；
    early-modern=近世~1500–1800CE；modern=近現代1800CE–；
    undated-traditional=年代不可考/口傳（部落神話、民俗採集）。以成書年代非抄本/譯本。

genre（主導文類，單值）：{genre_list}
  - scripture-revealed=經典/啟示；law-code=律法/戒律；commentary=註疏/論；
    epic-myth=史詩/神話；hymn-liturgy=讚歌/禮儀；wisdom-aphorism=智慧/箴言；
    prophecy-apocalypse=預言/啟示錄；philosophy-doctrine=哲學/教義；
    hagiography-history=傳記/史傳；incantation-magic=咒術/魔法；folk-ethnography=民俗/民族誌。

semantic_tags（跨宗教概念白名單，挑真正切題 3–8 個，表外詞禁止）：
{vocab}

psych_tags（人生問題軸白名單，獨立挑真正切題 1–5 個）：
{psych}
{iol_line}

## 輸出格式（**只輸出一個 JSON 物件，不要前言、不要 markdown fence**）

{{"era": "axial-age", "genre": "scripture-revealed", "semantic_tags": ["tag-a", "tag-b"], "psych_tags": ["death"], "keywords": ["神名", "地名", "核心主題"]{iol_field}}}

- era / genre：各填一個封閉詞彙值；真無法判斷填 null。
- semantic_tags：只能填上方白名單英文 tag。
- psych_tags：只能填人生問題軸白名單，且不得混入 semantic_tags。
- keywords：5–15 個自由詞（神名/地名/術語/主題），繁中或原文皆可，供搜尋。
第一個字元必須是 {{。"""


def read_head(slug: str) -> str | None:
    orig = TRANSLATIONS_DIR / slug / "raw" / "original.txt"
    if not orig.exists():
        return None
    try:
        text = orig.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    return text[:MAX_HEAD_CHARS]


def apply_classification(slug: str, obj: dict, tag_vocab: set[str],
                         psych_vocab: set[str]) -> list[str]:
    """Write only missing whitelisted fields; re-read fresh for concurrency safety."""
    meta_p = TRANSLATIONS_DIR / slug / "meta.json"
    try:
        meta = json.loads(meta_p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    changed = []

    era = obj.get("era")
    if not meta.get("era") and era in ERA_VOCAB:
        meta["era"] = era
        changed.append("era")

    genre = obj.get("genre")
    if not meta.get("genre") and genre in GENRE_VOCAB:
        meta["genre"] = genre
        changed.append("genre")

    tags = [t for t in (obj.get("semantic_tags") or []) if isinstance(t, str) and t in tag_vocab]
    if (meta.get("tag_status") != "done" or not meta.get("semantic_tags")) and tags:
        meta["semantic_tags"] = sorted(set(tags))
        kw = [k for k in (obj.get("keywords") or []) if isinstance(k, str) and k.strip()][:15]
        meta["keywords"] = kw
        meta["tag_status"] = "done"
        changed.append("tags")

    psych_tags = [t for t in (obj.get("psych_tags") or [])
                  if isinstance(t, str) and t in psych_vocab]
    if (meta.get("psych_tag_status") != "done" or not meta.get("psych_tags")) and psych_tags:
        meta["psych_tags"] = sorted(set(psych_tags))[:5]
        meta["psych_tag_status"] = "done"
        changed.append("psych_tags")

    if (meta.get("language") or "").strip() == "Latin" and meta.get("is_original_language") is None:
        iol = obj.get("is_original_language")
        if isinstance(iol, bool):
            meta["is_original_language"] = iol
            meta["text_role"] = "translation" if not iol else "original"
            changed.append("is_original")

    if changed:
        translate._atomic_write_text(
            meta_p, json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
    return changed


def _git(args: list[str]) -> tuple[int, str]:
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                       text=True, encoding="utf-8", errors="replace",
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def git_commit_push(paths: list[Path], n_done: int, push: bool) -> None:
    """Stage only OUR touched paths, pull --rebase before push, retry.
    Mirrors auto-pipeline discipline so the two writers coexist. Tolerates
    index.lock / non-fast-forward: local meta.json is on disk and recoverable."""
    if not paths:
        return
    rels = [str(p.relative_to(ROOT)) for p in paths]
    code, _ = _git(["add", "--", *rels])
    if code != 0:  # e.g. index.lock held by auto-pipeline this instant
        print("  [git] add skipped (lock?), meta on disk, will retry next batch")
        return
    code, out = _git(["commit", "--only", "-q", "-m",
                      f"align: M3 classify era/genre/tags (batch, +{n_done})",
                      "--", *rels])
    if code != 0:
        if "nothing to commit" not in out:
            print(f"  [git] commit failed: {out[:160]}")
        return
    print(f"  [git] committed {len(rels)} paths (+{n_done} done)")
    if not push:
        return
    _git(["pull", "--rebase"])
    for attempt in range(3):
        code, out = _git(["push"])
        if code == 0:
            print("  [git] pushed")
            return
        print(f"  [git] push attempt {attempt + 1} failed: {out[:100]}")
        _git(["pull", "--rebase"])
    print("  [git] push failed 3x — local commit kept, continuing")


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--tier", help="核心 / 次要 / 總集")
    g.add_argument("--all", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--batch", type=int, default=25, help="commit+push every N done")
    ap.add_argument("--no-push", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    tag_vocab = translate.load_tag_whitelist()
    psych_vocab = translate.load_psych_tag_whitelist()
    if not tag_vocab or not psych_vocab:
        sys.exit("[error] empty controlled vocabulary")

    if args.tier:
        slugs = translate.load_slugs_by_tier(args.tier)
    else:
        slugs = [p.parent.name for p in sorted(TRANSLATIONS_DIR.glob("*/meta.json"))]

    done = 0
    skipped = 0
    failed = 0
    considered = 0
    batch_paths: list[Path] = []
    for slug in slugs:
        if args.limit and considered >= args.limit:
            break
        meta_p = TRANSLATIONS_DIR / slug / "meta.json"
        try:
            meta = json.loads(meta_p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if not needs_classify(meta):
            skipped += 1
            continue
        considered += 1
        head = read_head(slug)
        if not head:
            print(f"  [skip-nohead] {slug}")
            failed += 1
            continue
        prompt = build_prompt(meta, head, tag_vocab, psych_vocab)
        if args.dry_run:
            print(f"\n[DRY] {slug} (prompt {len(prompt)} chars)")
            print(prompt[:1200] + "\n...[truncated]...")
            continue
        out = translate.call_m3(prompt)
        if not out:
            print(f"  [fail-m3] {slug}")
            failed += 1
            continue
        obj = translate.parse_tag_json(out)
        if not obj:
            print(f"  [fail-parse] {slug}")
            failed += 1
            continue
        changed = apply_classification(slug, obj, tag_vocab, psych_vocab)
        if changed:
            done += 1
            batch_paths.append(meta_p)
            print(f"  [ok] {slug}: {', '.join(changed)}  era={obj.get('era')} genre={obj.get('genre')}")
            if done % args.batch == 0:
                git_commit_push(batch_paths, done, push=not args.no_push)
                batch_paths = []
        else:
            skipped += 1

    if not args.dry_run and batch_paths:
        git_commit_push(batch_paths, done, push=not args.no_push)
    print(f"\n[summary] done={done} skipped={skipped} failed={failed}")


if __name__ == "__main__":
    if not acquire_run_lock():
        sys.exit(0)
    try:
        main()
    finally:
        release_run_lock()
