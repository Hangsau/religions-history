#!/usr/bin/env python
"""
Download Old Norse (Norrønt) texts from heimskringla.no (the Old Norse e-text
archive, ed. Carsten Lyngdrup Madsen & Jesper Lauridsen).

heimskringla.no is a MediaWiki whose /wiki/ pages default to the Old Norse
original (Guðni Jónsson editions) — e.g. Völuspá "Hljóðs bið ek allar / helgar
kindir ...". The api.php endpoint is disabled, so we scrape the rendered HTML:
take `.mw-parser-output`, drop the language-selector table and the edition
`<center>` header, keep the verse/prose body.

A scripture may span many pages (Poetic Edda = ~46 poems, Heimskringla = 17
sagas, Völsunga saga = 1 page). List them per entry under `heim_pages`
(un-encoded page titles; the downloader URL-quotes them).

Usage:
    python scripts/download-heimskringla.py --slug poetic-edda-on
    python scripts/download-heimskringla.py --religion 北歐 --all
"""

import argparse
import hashlib
import json
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
CATALOG_DIR = ROOT / "scripts" / "catalog"
TRANSLATIONS_DIR = ROOT / "translations"

HEIM_BASE = "https://www.heimskringla.no/wiki/"
USER_AGENT = "religions-history-research/0.1 (academic research; contact: psyhangsau@gmail.com; +https://github.com/Hangsau/religions-history)"
REQ_TIMEOUT = 30
SLEEP_BETWEEN_REQUESTS = 0.5

_polite_req_count = 0
_LONG_PAUSE_EVERY = 100
_LONG_PAUSE_SECONDS = 30.0
MAX_RETRIES = 5
BACKOFF_INITIAL = 10.0


def _polite_sleep_inline(base: float) -> None:
    global _polite_req_count
    _polite_req_count += 1
    time.sleep(base + random.uniform(0, 0.5))
    if _polite_req_count > 0 and _polite_req_count % _LONG_PAUSE_EVERY == 0:
        print(f"  [polite-pause] {_LONG_PAUSE_SECONDS:.0f}s break after {_polite_req_count} requests")
        time.sleep(_LONG_PAUSE_SECONDS)


def fetch_html(page: str) -> str:
    url = HEIM_BASE + quote(page.replace(" ", "_"))
    headers = {"User-Agent": USER_AGENT}
    backoff = BACKOFF_INITIAL
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.get(url, headers=headers, timeout=REQ_TIMEOUT)
            if r.status_code == 404:
                raise FileNotFoundError(f"404 at {url}")
            if r.status_code in (429, 403, 503):
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


def extract_norse_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    po = soup.select_one(".mw-parser-output") or soup.select_one("#mw-content-text")
    if po is None:
        return ""
    # Language-selector table + edition <center> header + editorial chrome.
    for sel in ("table.toccolours", "center", "sup.reference", ".mw-editsection",
                ".noprint", "style", "script", "table.metadata"):
        for tag in po.select(sel):
            tag.decompose()
    text = po.get_text("\n", strip=True)
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    return "\n".join(lines)


def download_scripture(entry: dict) -> dict:
    slug = entry["slug"]
    pages = entry.get("heim_pages") or ([entry["heim_page"]] if entry.get("heim_page") else [])
    if not pages:
        return {"slug": slug, "status": "error", "reason": "no heim_page(s)"}

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

    chapters: list[tuple[str, str]] = []
    urls: list[str] = []
    for page in pages:
        url = HEIM_BASE + quote(page.replace(" ", "_"))
        print(f"  [fetch] {page}")
        urls.append(url)
        _polite_sleep_inline(SLEEP_BETWEEN_REQUESTS)
        try:
            html = fetch_html(page)
        except FileNotFoundError:
            print(f"  [not-found] {page}")
            return {"slug": slug, "status": "not_found", "reason": page}
        except (RuntimeError, requests.RequestException) as e:
            return {"slug": slug, "status": "error", "reason": str(e)}
        text = extract_norse_text(html)
        if text:
            chapters.append((page, text))

    if not chapters:
        return {"slug": slug, "status": "empty"}

    out_dir.mkdir(parents=True, exist_ok=True)
    lines = []
    for i, (label, text) in enumerate(chapters, 1):
        lines.append(f"=== {i} | {label} ===")
        lines.append(text)
        lines.append("")
    original_text = "\n".join(lines).rstrip() + "\n"
    original_bytes = original_text.encode("utf-8")

    (out_dir / "original.txt").write_bytes(original_bytes)
    (out_dir / "source-urls.txt").write_bytes(("\n".join(urls) + "\n").encode("utf-8"))
    sha = hashlib.sha256(original_bytes).hexdigest()
    (out_dir / "checksums.sha256").write_bytes(f"{sha}  original.txt\n".encode("utf-8"))

    meta = {
        "slug": slug,
        "name_zh": entry["name_zh"],
        "name_en": entry.get("name_en", ""),
        "name_original": entry.get("name_original") or entry["name_zh"],
        "religion": entry.get("religion", "北歐"),
        "language": entry.get("language", "古諾斯語"),
        "version": entry.get("version", "heimskringla.no (Guðni Jónsson ed.)"),
        "version_date": entry.get("version_date", "—"),
        "source_platform": "heimskringla.no",
        "source_url": urls[0],
        "downloaded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "size_bytes": len(original_bytes),
        "checksum_sha256": sha,
        "chapter_count": len(chapters),
        "expected_chapter_count": entry.get("expected_chapter_count"),
        "license": "Public domain / academic use (heimskringla.no)",
        "verified": False,
        "tier": entry.get("tier"),
        "notes": entry.get("notes"),
    }
    for k in ("text_role", "is_original_language", "translation_of", "original_of", "composition_note"):
        v = entry.get(k)
        if v is not None:
            meta[k] = v
    (TRANSLATIONS_DIR / slug / "meta.json").write_bytes(
        (json.dumps(meta, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    )
    print(f"[ok] {slug}: {len(chapters)} pages, {meta['size_bytes']} bytes")
    return {"slug": slug, "status": "ok", "meta": meta}


def load_catalog(religion: str) -> list[dict]:
    name_map = {"北歐": "norse-heimskringla.json"}
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
    for cat_file in CATALOG_DIR.glob("*-heimskringla*.json"):
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
            sys.exit(f"slug not in any heimskringla catalog: {args.slug}")
        r = download_scripture(e)
        print(json.dumps({k: v for k, v in r.items() if k != "meta"}, ensure_ascii=False, indent=2))
        return

    if args.religion:
        for e in load_catalog(args.religion):
            try:
                download_scripture(e)
            except Exception as ex:
                print(f"[exception] {e['slug']}: {ex}")
        return

    p.print_help()


if __name__ == "__main__":
    main()
