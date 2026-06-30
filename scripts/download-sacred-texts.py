#!/usr/bin/env python
"""
Download religious texts from sacred-texts.com — generic for any tradition.

sacred-texts.com structure:
    /<tradition>/<book>/index.htm — book table of contents with chapter href list
    /<tradition>/<book>/<chapter>.htm — individual chapter content

Needs browser User-Agent (Mozilla Mac) to avoid 403.

Catalog entry:
{
  "slug": "vendidad",
  "st_book_path": "zor/sbe04",
  "name_zh": "...",
  "religion": "瑣羅亞斯德",
  "tier": "核心",
  "is_original_language": false  // most sacred-texts are 19c English translations
}

Usage:
    python scripts/download-sacred-texts.py --slug vendidad
    python scripts/download-sacred-texts.py --religion 瑣羅亞斯德 --all
"""

import argparse
import hashlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
CATALOG_DIR = ROOT / "scripts" / "catalog"
TRANSLATIONS_DIR = ROOT / "translations"

ST_BASE = "https://www.sacred-texts.com/"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
REQ_TIMEOUT = 30
SLEEP_BETWEEN_REQUESTS = 0.5
MAX_RETRIES = 5
BACKOFF_INITIAL = 10.0


def fetch_html(path: str) -> str:
    url = urljoin(ST_BASE, path.lstrip("/"))
    headers = {"User-Agent": USER_AGENT}
    backoff = BACKOFF_INITIAL
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.get(url, headers=headers, timeout=REQ_TIMEOUT)
            if r.status_code == 404:
                raise FileNotFoundError(f"404 at {url}")
            if r.status_code in (429, 503):
                print(f"  [rate-limit {r.status_code}] sleep {backoff:.0f}s")
                time.sleep(backoff)
                backoff *= 2
                continue
            r.raise_for_status()
            r.encoding = "utf-8"
            return r.text
        except requests.RequestException as e:
            print(f"  [req-error attempt {attempt}/{MAX_RETRIES}] sleep {backoff:.0f}s: {e}")
            time.sleep(backoff)
            backoff *= 2
    raise RuntimeError(f"max retries exceeded for {url}")


def find_chapter_files(index_html: str, book_path: str) -> list[tuple[str, str]]:
    """Return list of (filename, title) for chapters in book index."""
    soup = BeautifulSoup(index_html, "html.parser")
    # book_path is like "zor/sbe04" - chapter files are sbe04NN.htm or similar
    # We want all <A HREF="X.htm"> where X doesn't contain / and not "index.htm"
    seen = set()
    out = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if "/" in href or not href.endswith(".htm") or href in ("index.htm",):
            continue
        if href in seen:
            continue
        seen.add(href)
        title = a.get_text(strip=True) or href
        out.append((href, title))
    return out


def extract_chapter_text(html: str) -> str:
    """Extract main text from sacred-texts.com chapter HTML."""
    soup = BeautifulSoup(html, "html.parser")
    # Sacred-texts.com pages typically have nav at top (Previous / Next) then content
    # Strip <head>, <script>, navigation tables
    for tag in soup.find_all(["script", "style", "head"]):
        tag.decompose()
    # Remove first center-aligned nav block (Previous Next stuff)
    for center in soup.find_all("center"):
        text = center.get_text(strip=True)
        if text and ("Previous" in text or "Next" in text or "Index" in text):
            center.decompose()
    # Remove last <p> with navigation
    for p in soup.find_all("p"):
        t = p.get_text(strip=True)
        if "Next:" in t or "Previous:" in t:
            p.decompose()
    body = soup.find("body") or soup
    text = body.get_text("\n", strip=True)
    # Drop common chrome lines
    lines = []
    for line in text.split("\n"):
        s = line.strip()
        if not s:
            continue
        if re.match(r"^(Sacred Texts|Buy this Book|Next:|Previous:|Buy a CD|Buy CD|Index)", s):
            continue
        if re.match(r"^p\. \d+$", s):
            continue
        lines.append(s)
    return "\n".join(lines)


def download_scripture(entry: dict) -> dict:
    slug = entry["slug"]
    if entry.get("skip_reason"):
        print(f"[skip] {slug}: {entry['skip_reason']}")
        return {"slug": slug, "status": "skipped", "reason": entry["skip_reason"]}
    if entry.get("defer_reason"):
        print(f"[defer] {slug}: {entry['defer_reason']}")
        return {"slug": slug, "status": "deferred", "reason": entry["defer_reason"]}

    book_path = entry.get("st_book_path")
    if not book_path:
        return {"slug": slug, "status": "error", "reason": "no st_book_path"}

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

    index_path = f"{book_path}/index.htm"
    print(f"  [index] {index_path}")
    try:
        index_html = fetch_html(index_path)
    except FileNotFoundError as e:
        return {"slug": slug, "status": "not_found", "reason": str(e)}
    except (RuntimeError, requests.RequestException) as e:
        return {"slug": slug, "status": "error", "reason": str(e)}

    chapters_list = find_chapter_files(index_html, book_path)
    if not chapters_list:
        return {"slug": slug, "status": "empty", "reason": "no chapter links in index"}

    print(f"  [chapters] {len(chapters_list)}")
    chapter_data: list[tuple[str, str]] = []
    urls: list[str] = []
    for filename, title in chapters_list:
        chapter_path = f"{book_path}/{filename}"
        url = urljoin(ST_BASE, chapter_path)
        print(f"  [fetch] {chapter_path}")
        urls.append(url)
        time.sleep(SLEEP_BETWEEN_REQUESTS)
        try:
            ch_html = fetch_html(chapter_path)
        except FileNotFoundError:
            print(f"    (not found, skip)")
            continue
        except (RuntimeError, requests.RequestException) as e:
            return {"slug": slug, "status": "error", "reason": f"{chapter_path}: {e}"}
        text = extract_chapter_text(ch_html)
        if text.strip():
            chapter_data.append((title, text))

    if not chapter_data:
        return {"slug": slug, "status": "empty"}

    out_dir.mkdir(parents=True, exist_ok=True)
    lines = []
    for i, (title, text) in enumerate(chapter_data, 1):
        lines.append(f"=== {i} | {title} ===")
        lines.append(text)
        lines.append("")
    original_text = "\n".join(lines).rstrip() + "\n"
    original_bytes = original_text.encode("utf-8")

    (out_dir / "original.txt").write_bytes(original_bytes)
    (out_dir / "source-urls.txt").write_bytes(("\n".join([urljoin(ST_BASE, index_path)] + urls) + "\n").encode("utf-8"))
    sha = hashlib.sha256(original_bytes).hexdigest()
    (out_dir / "checksums.sha256").write_bytes(f"{sha}  original.txt\n".encode("utf-8"))

    meta = {
        "slug": slug,
        "name_zh": entry["name_zh"],
        "name_en": entry.get("name_en", ""),
        "name_original": entry.get("name_original") or entry["name_zh"],
        "religion": entry.get("religion", "—"),
        "tradition": entry.get("tradition"),
        "language": entry.get("language", "English"),
        "version": entry.get("version", "sacred-texts.com edition"),
        "version_date": entry.get("version_date", "—"),
        "source_platform": "sacred-texts.com",
        "source_url": urljoin(ST_BASE, index_path),
        "downloaded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "size_bytes": len(original_bytes),
        "checksum_sha256": sha,
        "chapter_count": len(chapter_data),
        "expected_chapter_count": entry.get("expected_chapter_count"),
        "license": "Public Domain (most sacred-texts pre-1928)",
        "verified": False,
        "tier": entry.get("tier"),
        "is_original_language": entry.get("is_original_language", False),
        "notes": entry.get("notes"),
    }
    (TRANSLATIONS_DIR / slug / "meta.json").write_bytes(
        (json.dumps(meta, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    )
    print(f"[ok] {slug}: {len(chapter_data)} chapters, {meta['size_bytes']} bytes")
    return {"slug": slug, "status": "ok", "meta": meta}


CATALOG_MAP = {
    "瑣羅亞斯德": "zoroastrianism-st.json",
    "耆那教": "jainism-st.json",
    "古埃及": "egypt-st.json",
    "古希臘羅馬": "classical-st.json",
    "北歐": "norse-st.json",
    "凱爾特": "celtic-st.json",
    "巴哈伊": "bahai-st.json",
    "諾斯底": "gnostic-st.json",
    "曼達派": "mandaean-st.json",
    "美洲": "americas-st.json",
    "非洲": "africa-st.json",
}


def load_catalog(religion: str) -> list[dict]:
    if religion not in CATALOG_MAP:
        sys.exit(f"unknown religion: {religion}")
    path = CATALOG_DIR / CATALOG_MAP[religion]
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
    for cat_file in CATALOG_DIR.glob("*-st.json"):
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
            sys.exit(f"slug not in any -st catalog: {args.slug}")
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
