#!/usr/bin/env python
"""
Download Old Norse (Íslenzka) saga texts from sagadb.org (the Icelandic Saga
Database, ed. Sveinbjörn Þórðarson).

sagadb.org serves each saga as a single XHTML page at /<name>.is (the Old Norse
original; the .en / .* variants are translations). The text sits in
`div.content div.columns` as an <h1> title, <h2> "N. kafli" chapter headings and
<p> paragraphs, preceded by a "Format: ..." nav line we drop.

Use this for the Íslendingasögur that heimskringla.no / is.wikisource lack a
clean Old Norse full text for (Laxdæla, Vatnsdæla, Kormáks, Víga-Glúms,
Fóstbræðra, ...). List each under `sagadb_slug` in scripts/catalog/norse-sagadb.json.

Usage:
    python scripts/download-sagadb.py --slug laxdaela-saga-on
    python scripts/download-sagadb.py --religion 北歐 --all
"""

import argparse
import hashlib
import json
import random
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
CATALOG_DIR = ROOT / "scripts" / "catalog"
TRANSLATIONS_DIR = ROOT / "translations"
CATALOG_FILE = CATALOG_DIR / "norse-sagadb.json"

SAGADB_BASE = "https://www.sagadb.org/"
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


def fetch_html(sagadb_slug: str) -> str:
    url = f"{SAGADB_BASE}{sagadb_slug}.is"
    headers = {"User-Agent": USER_AGENT}
    backoff = BACKOFF_INITIAL
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.get(url, headers=headers, timeout=REQ_TIMEOUT, allow_redirects=True)
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


_KAFLI_RE = re.compile(r"^\s*(\d+)\.\s*kafli\b", re.IGNORECASE)


def extract_saga_text(html: str) -> tuple[str, int]:
    """Return (text, chapter_count). Chapter headings ('N. kafli' <h2>s) are
    emitted as `=== N | kafli ===` separators so verify.py's CHAPTER_SEP_RE
    matches, consistent with the wikisource/heimskringla Norse texts."""
    soup = BeautifulSoup(html, "html.parser")
    col = soup.select_one("div.content div.columns") or soup.select_one("div.content")
    if col is None:
        return "", 0
    for tag in col.select("script, style"):
        tag.decompose()
    # Drop the "Format: Web | XHTML | ..." nav paragraph(s).
    for p in col.find_all("p"):
        t = p.get_text(" ", strip=True)
        if t.startswith("Format:") or t.startswith("Citation"):
            p.decompose()

    out_lines: list[str] = []
    chapter_count = 0
    for el in col.find_all(["h1", "h2", "h3", "p"]):
        raw = el.get_text(" ", strip=True)
        if not raw:
            continue
        if el.name in ("h2", "h3"):
            m = _KAFLI_RE.match(raw)
            if m:
                chapter_count += 1
                out_lines.append(f"=== {m.group(1)} | kafli ===")
                continue
        out_lines.append(raw)

    if chapter_count == 0:
        # No chapter headings (single-block saga): whole body is one chapter.
        text = col.get_text("\n", strip=True)
        lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
        return "\n".join(lines), 1
    return "\n".join(out_lines), chapter_count


def download_scripture(entry: dict) -> dict:
    slug = entry["slug"]
    sagadb_slug = entry.get("sagadb_slug")
    if not sagadb_slug:
        return {"slug": slug, "status": "error", "reason": "no sagadb_slug"}

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

    url = f"{SAGADB_BASE}{sagadb_slug}.is"
    print(f"  [fetch] {sagadb_slug}.is")
    _polite_sleep_inline(SLEEP_BETWEEN_REQUESTS)
    try:
        html = fetch_html(sagadb_slug)
    except FileNotFoundError:
        print(f"  [not-found] {sagadb_slug}.is")
        return {"slug": slug, "status": "not_found", "reason": f"{sagadb_slug}.is"}
    except (RuntimeError, requests.RequestException) as e:
        return {"slug": slug, "status": "error", "reason": str(e)}

    text, chapter_count = extract_saga_text(html)
    if not text:
        return {"slug": slug, "status": "empty"}

    out_dir.mkdir(parents=True, exist_ok=True)
    original_text = text.rstrip() + "\n"
    original_bytes = original_text.encode("utf-8")

    (out_dir / "original.txt").write_bytes(original_bytes)
    (out_dir / "source-urls.txt").write_bytes((url + "\n").encode("utf-8"))
    sha = hashlib.sha256(original_bytes).hexdigest()
    (out_dir / "checksums.sha256").write_bytes(f"{sha}  original.txt\n".encode("utf-8"))

    meta = {
        "slug": slug,
        "name_zh": entry["name_zh"],
        "name_en": entry.get("name_en", ""),
        "name_original": entry.get("name_original") or entry["name_zh"],
        "religion": entry.get("religion", "北歐"),
        "language": entry.get("language", "古諾斯語"),
        "version": entry.get("version", "sagadb.org (Icelandic Saga Database)"),
        "version_date": entry.get("version_date", "—"),
        "source_platform": "sagadb.org",
        "source_url": url,
        "downloaded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "size_bytes": len(original_bytes),
        "checksum_sha256": sha,
        "chapter_count": chapter_count,
        "expected_chapter_count": entry.get("expected_chapter_count"),
        "license": "Public domain / academic use (sagadb.org)",
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
    print(f"[ok] {slug}: {meta['size_bytes']} bytes")
    return {"slug": slug, "status": "ok", "meta": meta}


def load_catalog() -> list[dict]:
    if not CATALOG_FILE.exists():
        sys.exit(f"catalog not found: {CATALOG_FILE}")
    data = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    out = []
    for e in data["scriptures"]:
        e.setdefault("religion", data["religion"])
        e.setdefault("language", data.get("language"))
        out.append(e)
    return out


def find_entry(slug: str) -> dict | None:
    for e in load_catalog():
        if e["slug"] == slug:
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
            sys.exit(f"slug not in sagadb catalog: {args.slug}")
        r = download_scripture(e)
        print(json.dumps({k: v for k, v in r.items() if k != "meta"}, ensure_ascii=False, indent=2))
        return

    if args.religion or args.all:
        for e in load_catalog():
            try:
                download_scripture(e)
            except Exception as ex:
                print(f"[exception] {e['slug']}: {ex}")
        return

    p.print_help()


if __name__ == "__main__":
    main()
