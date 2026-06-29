#!/usr/bin/env python
"""
Download Jewish texts from Sefaria.org and save to translations/<slug>/raw/.

Sefaria has a comprehensive JSON API:
    https://www.sefaria.org/api/texts/<ref>      → full chapter/section text
    https://www.sefaria.org/api/index/<book>     → metadata + section structure

For our purposes we use:
    /api/texts/<book>?context=0 → returns {"text": [...]} for English/translation
                                  and {"he": [...]} for Hebrew source

We download Hebrew source as primary, English alongside.

Usage:
    python scripts/download-sefaria.py --slug genesis
    python scripts/download-sefaria.py --religion 猶太教 --all
"""

import argparse
import hashlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
CATALOG_DIR = ROOT / "scripts" / "catalog"
TRANSLATIONS_DIR = ROOT / "translations"

SEFARIA_API = "https://www.sefaria.org/api"
USER_AGENT = "religions-history-research/0.1 (https://github.com/Hangsau/religions-history; academic use)"
REQ_TIMEOUT = 30
SLEEP_BETWEEN_REQUESTS = 0.5
MAX_RETRIES = 5
BACKOFF_INITIAL = 10.0


def api_get(path: str, params: dict | None = None) -> dict:
    url = f"{SEFARIA_API}/{path.lstrip('/')}"
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    backoff = BACKOFF_INITIAL
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.get(url, params=params, headers=headers, timeout=REQ_TIMEOUT)
            if r.status_code in (429, 503):
                print(f"  [rate-limit {r.status_code}] sleep {backoff:.0f}s")
                time.sleep(backoff)
                backoff *= 2
                continue
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            print(f"  [req-error attempt {attempt}/{MAX_RETRIES}] sleep {backoff:.0f}s: {e}")
            time.sleep(backoff)
            backoff *= 2
    raise RuntimeError(f"max retries exceeded for {url}")


def get_book_index(book: str) -> dict:
    """Get book metadata + structure (lengths of chapters)."""
    return api_get(f"index/{book.replace(' ', '%20')}")


def strip_html(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"&nbsp;", " ", s)
    s = re.sub(r"&amp;", "&", s)
    s = re.sub(r"&lt;", "<", s)
    s = re.sub(r"&gt;", ">", s)
    return s


def fetch_chapter(book: str, chapter: int) -> tuple[str, str]:
    """Returns (hebrew_text, english_text) for one chapter."""
    ref = f"{book} {chapter}".replace(" ", "%20")
    data = api_get(f"texts/{ref}", params={"context": 0})
    he = data.get("he", [])
    en = data.get("text", [])
    he_text = "\n".join(strip_html(v) for v in he if isinstance(v, str))
    en_text = "\n".join(strip_html(v) for v in en if isinstance(v, str))
    return he_text, en_text


def download_scripture(entry: dict) -> dict:
    slug = entry["slug"]
    if entry.get("skip_reason"):
        print(f"[skip] {slug}: {entry['skip_reason']}")
        return {"slug": slug, "status": "skipped", "reason": entry["skip_reason"]}
    if entry.get("defer_reason"):
        print(f"[defer] {slug}: {entry['defer_reason']}")
        return {"slug": slug, "status": "deferred", "reason": entry["defer_reason"]}

    book = entry.get("sefaria_book")
    if not book:
        return {"slug": slug, "status": "error", "reason": "no sefaria_book"}

    meta_path = TRANSLATIONS_DIR / slug / "meta.json"
    out_dir = TRANSLATIONS_DIR / slug / "raw"
    if meta_path.exists():
        try:
            existing = json.loads(meta_path.read_text(encoding="utf-8"))
            if existing.get("verified") and (out_dir / "original.txt").exists():
                print(f"[skip] {slug}: already verified")
                return {"slug": slug, "status": "already_verified"}
        except (json.JSONDecodeError, OSError):
            pass

    try:
        idx = get_book_index(book)
    except RuntimeError as e:
        return {"slug": slug, "status": "error", "reason": str(e)}

    # Determine chapter count
    lengths = idx.get("lengths", [])
    schema = idx.get("schema", {})
    if lengths and isinstance(lengths, list):
        n_chapters = lengths[0] if lengths else 1
    else:
        n_chapters = schema.get("lengths", [1])[0] if isinstance(schema.get("lengths"), list) else 1

    n_chapters = entry.get("chapter_count_override", n_chapters)

    print(f"  [book] {book} ({n_chapters} chapters)")
    chapters_he: list[tuple[str, str]] = []
    chapters_en: list[tuple[str, str]] = []
    fetched_refs: list[str] = []

    try:
        for ch in range(1, n_chapters + 1):
            ref = f"{book} {ch}"
            print(f"  [chapter] {ref}")
            fetched_refs.append(ref)
            time.sleep(SLEEP_BETWEEN_REQUESTS)
            he, en = fetch_chapter(book, ch)
            if he:
                chapters_he.append((str(ch), he))
            if en:
                chapters_en.append((str(ch), en))
    except RuntimeError as e:
        return {"slug": slug, "status": "error", "reason": str(e)}

    if not chapters_he and not chapters_en:
        return {"slug": slug, "status": "empty", "reason": "no text returned"}

    out_dir.mkdir(parents=True, exist_ok=True)

    # Write Hebrew as original.txt (per project convention: original language first)
    primary = chapters_he if chapters_he else chapters_en
    primary_lang = "Hebrew" if chapters_he else "English"
    lines = []
    for i, (label, text) in enumerate(primary, 1):
        lines.append(f"=== {i} | {label} ===")
        lines.append(text)
        lines.append("")
    original_text = "\n".join(lines).rstrip() + "\n"
    original_bytes = original_text.encode("utf-8")
    (out_dir / "original.txt").write_bytes(original_bytes)
    sha = hashlib.sha256(original_bytes).hexdigest()
    (out_dir / "checksums.sha256").write_bytes(f"{sha}  original.txt\n".encode("utf-8"))

    # English translation as separate file (for cross-check; not primary)
    if chapters_en and chapters_he:
        en_lines = []
        for i, (label, text) in enumerate(chapters_en, 1):
            en_lines.append(f"=== {i} | {label} ===")
            en_lines.append(text)
            en_lines.append("")
        (out_dir / "translation-en.txt").write_bytes(("\n".join(en_lines).rstrip() + "\n").encode("utf-8"))

    urls = [f"{SEFARIA_API}/texts/{r.replace(' ', '%20')}?context=0" for r in fetched_refs]
    (out_dir / "source-urls.txt").write_bytes(("\n".join(urls) + "\n").encode("utf-8"))

    meta = {
        "slug": slug,
        "name_zh": entry["name_zh"],
        "name_en": entry.get("name_en", book),
        "name_original": entry.get("name_original") or book,
        "religion": entry.get("religion", "猶太教"),
        "language": entry.get("language", primary_lang),
        "version": entry.get("version", "Sefaria 校勘版"),
        "version_date": entry.get("version_date", "—"),
        "source_platform": "Sefaria",
        "source_url": f"https://www.sefaria.org/{book.replace(' ', '%20')}",
        "downloaded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "size_bytes": len(original_bytes),
        "checksum_sha256": sha,
        "chapter_count": len(primary),
        "expected_chapter_count": entry.get("expected_chapter_count"),
        "expected_size_min": entry.get("expected_size_min"),
        "expected_size_max": entry.get("expected_size_max"),
        "license": "CC BY-NC 4.0 (Sefaria)",
        "verified": False,
        "tier": entry.get("tier"),
        "notes": entry.get("notes"),
    }
    (TRANSLATIONS_DIR / slug / "meta.json").write_bytes(
        (json.dumps(meta, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    )
    print(f"[ok] {slug}: {len(primary)} chapters, {meta['size_bytes']} bytes ({primary_lang})")
    return {"slug": slug, "status": "ok", "meta": meta}


def load_catalog(religion: str) -> list[dict]:
    name_map = {"猶太教": "judaism.json"}
    if religion not in name_map:
        sys.exit(f"unknown religion: {religion}")
    path = CATALOG_DIR / name_map[religion]
    if not path.exists():
        sys.exit(f"catalog not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    out = []
    for e in data["scriptures"]:
        e.setdefault("religion", data["religion"])
        e.setdefault("language", data.get("language"))
        out.append(e)
    return out


def find_entry(slug: str) -> dict | None:
    for cat_file in CATALOG_DIR.glob("judaism*.json"):
        data = json.loads(cat_file.read_text(encoding="utf-8"))
        for e in data["scriptures"]:
            if e["slug"] == slug:
                e.setdefault("religion", data["religion"])
                e.setdefault("language", data.get("language"))
                return e
    return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--slug")
    p.add_argument("--religion")
    p.add_argument("--all", action="store_true")
    args = p.parse_args()

    if args.slug and not args.religion:
        e = find_entry(args.slug)
        if not e:
            sys.exit(f"slug not in any judaism catalog: {args.slug}")
        r = download_scripture(e)
        print(json.dumps({k: v for k, v in r.items() if k != "meta"}, ensure_ascii=False, indent=2))
        return

    if args.religion:
        entries = load_catalog(args.religion)
        results = []
        for e in entries:
            try:
                r = download_scripture(e)
            except Exception as ex:
                r = {"slug": e["slug"], "status": "exception", "reason": repr(ex)}
                print(f"[exception] {e['slug']}: {ex}")
            results.append(r)
        summary = {}
        for r in results:
            s = r["status"]
            summary[s] = summary.get(s, 0) + 1
        print("\n[summary]", json.dumps(summary, ensure_ascii=False))
        return

    p.print_help()


if __name__ == "__main__":
    main()
