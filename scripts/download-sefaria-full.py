#!/usr/bin/env python
"""
Download entire Sefaria library by recursing through /api/index categorization.

Usage:
    python scripts/download-sefaria-full.py --category Tanakh
    python scripts/download-sefaria-full.py --all      # full library (huge)
    python scripts/download-sefaria-full.py --category "Talmud Bavli" --limit 5  # test
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
TRANSLATIONS_DIR = ROOT / "translations"

SEFARIA_API = "https://www.sefaria.org/api"
USER_AGENT = "religions-history-research/0.1 (https://github.com/Hangsau/religions-history; academic use)"
REQ_TIMEOUT = 30
SLEEP_BETWEEN_REQUESTS = 0.5
MAX_RETRIES = 5
BACKOFF_INITIAL = 10.0


def api_get(path: str, params: dict | None = None) -> dict | list:
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


def get_index() -> list:
    """Sefaria /api/index returns a list of top-level category objects."""
    return api_get("index")


def collect_books(node, books, current_category=""):
    """Recursively flatten the Sefaria index tree to (category_path, book_title) tuples."""
    if isinstance(node, dict):
        cat = node.get("category")
        title = node.get("title")
        contents = node.get("contents")
        if title and "title" in node and not contents:
            # leaf book entry
            books.append({
                "title": title,
                "category": current_category,
                "primary_category": node.get("primary_category", current_category),
                "lengths": node.get("schema", {}).get("lengths") if "schema" in node else None,
            })
        elif contents:
            new_cat = current_category + ("/" if current_category else "") + (cat or title or "")
            for sub in contents:
                collect_books(sub, books, new_cat)
        elif title:
            # leaf with title but no contents
            books.append({
                "title": title,
                "category": current_category,
                "primary_category": current_category,
            })


def slugify(title: str) -> str:
    s = title.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


def strip_html(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"&nbsp;", " ", s)
    s = re.sub(r"&amp;", "&", s)
    s = re.sub(r"&lt;", "<", s)
    s = re.sub(r"&gt;", ">", s)
    return s


def fetch_book_text(book_title: str) -> tuple[list[str], list[str], int]:
    """Fetch entire book by figuring out chapter count from index, then iterating.

    Returns (hebrew_chapters_list, english_chapters_list, count).
    """
    # First get book index for chapter count
    try:
        idx = api_get(f"index/{book_title.replace(' ', '%20')}")
    except RuntimeError as e:
        return ([], [], 0)
    lengths = idx.get("lengths") or idx.get("schema", {}).get("lengths") or []
    n_chap = lengths[0] if lengths else 1
    if not isinstance(n_chap, int) or n_chap < 1:
        n_chap = 1
    # Cap pathological chapter counts
    n_chap = min(n_chap, 1000)

    he_chs: list[str] = []
    en_chs: list[str] = []
    for ch in range(1, n_chap + 1):
        ref = f"{book_title} {ch}"
        time.sleep(SLEEP_BETWEEN_REQUESTS)
        try:
            data = api_get(f"texts/{ref.replace(' ', '%20')}", params={"context": 0})
        except RuntimeError:
            continue
        he = data.get("he", [])
        en = data.get("text", [])
        he_text = "\n".join(strip_html(v) for v in he if isinstance(v, str))
        en_text = "\n".join(strip_html(v) for v in en if isinstance(v, str))
        if he_text or en_text:
            if he_text:
                he_chs.append(he_text)
            if en_text:
                en_chs.append(en_text)
    return he_chs, en_chs, len(he_chs) or len(en_chs)


def download_book(book: dict) -> dict:
    title = book["title"]
    slug = f"sefaria-{slugify(title)}"
    meta_path = TRANSLATIONS_DIR / slug / "meta.json"
    out_dir = TRANSLATIONS_DIR / slug / "raw"

    if meta_path.exists():
        try:
            existing = json.loads(meta_path.read_text(encoding="utf-8"))
            if existing.get("verified") and (out_dir / "original.txt").exists():
                return {"slug": slug, "status": "already_verified"}
        except (json.JSONDecodeError, OSError):
            pass

    print(f"  [book] {title}")
    try:
        he_chs, en_chs, n = fetch_book_text(title)
    except RuntimeError as e:
        return {"slug": slug, "status": "error", "reason": str(e)}

    if not he_chs and not en_chs:
        return {"slug": slug, "status": "empty"}

    primary = he_chs if he_chs else en_chs
    primary_lang = "Hebrew" if he_chs else "English"

    out_dir.mkdir(parents=True, exist_ok=True)
    lines = []
    for i, text in enumerate(primary, 1):
        lines.append(f"=== {i} | chapter {i} ===")
        lines.append(text)
        lines.append("")
    original_text = "\n".join(lines).rstrip() + "\n"
    original_bytes = original_text.encode("utf-8")
    (out_dir / "original.txt").write_bytes(original_bytes)
    sha = hashlib.sha256(original_bytes).hexdigest()
    (out_dir / "checksums.sha256").write_bytes(f"{sha}  original.txt\n".encode("utf-8"))

    if en_chs and he_chs:
        en_lines = []
        for i, text in enumerate(en_chs, 1):
            en_lines.append(f"=== {i} | chapter {i} ===")
            en_lines.append(text)
            en_lines.append("")
        (out_dir / "translation-en.txt").write_bytes(("\n".join(en_lines).rstrip() + "\n").encode("utf-8"))

    (out_dir / "source-urls.txt").write_bytes(f"{SEFARIA_API}/index/{title.replace(' ', '%20')}\n".encode("utf-8"))

    category = book.get("primary_category", "")
    meta = {
        "slug": slug,
        "name_zh": title,
        "name_en": title,
        "name_original": title,
        "religion": "猶太教",
        "tradition": category,
        "language": primary_lang,
        "version": "Sefaria edition",
        "version_date": "—",
        "source_platform": "Sefaria",
        "source_url": f"https://www.sefaria.org/{title.replace(' ', '%20')}",
        "downloaded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "size_bytes": len(original_bytes),
        "checksum_sha256": sha,
        "chapter_count": n,
        "license": "CC BY-NC 4.0 (Sefaria)",
        "verified": False,
        "tier": "Sefaria full crawl",
        "is_original_language": primary_lang == "Hebrew",
        "notes": f"Category: {category}",
    }
    (TRANSLATIONS_DIR / slug / "meta.json").write_bytes(
        (json.dumps(meta, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    )
    return {"slug": slug, "status": "ok", "chapters": n, "size": len(original_bytes)}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--category", help="top-level Sefaria category (Tanakh / Mishnah / Talmud / Midrash / etc)")
    p.add_argument("--all", action="store_true", help="ALL Sefaria books (huge, defer in production)")
    p.add_argument("--limit", type=int, help="cap N books for testing")
    args = p.parse_args()

    print("[fetch] /api/index")
    idx = get_index()
    books: list[dict] = []
    if args.category:
        # Find that category's contents
        for top in idx:
            if isinstance(top, dict) and top.get("category") == args.category:
                collect_books(top, books, args.category)
                break
        if not books:
            sys.exit(f"category not found: {args.category}")
    else:
        for top in idx:
            collect_books(top, books)

    print(f"[books] {len(books)} discovered")
    if args.limit:
        books = books[:args.limit]
        print(f"[limit] {len(books)} after --limit")

    summary = {}
    for book in books:
        try:
            r = download_book(book)
        except Exception as ex:
            r = {"slug": "unknown", "status": "exception", "reason": repr(ex)}
        status = r["status"]
        summary[status] = summary.get(status, 0) + 1
        if status == "ok":
            print(f"  [ok] {r['slug']}: {r['chapters']} chapters, {r['size']} bytes")
        elif status not in ("already_verified",):
            print(f"  [{status}] {book.get('title', '?')}: {r.get('reason', '')}")

    print(f"\n[summary] {json.dumps(summary, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
