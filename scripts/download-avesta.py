#!/usr/bin/env python
"""
Download Avestan (and Pahlavi transliteration) texts from avesta.org
(the Zoroastrian Archives, ed. Joseph H. Peterson).

Avestan pages carry the Geldner 1896 romanised transliteration — genuine
original-language text (e.g. Yasna 28 "ýânîm manô ýânîm vacô ..."). Each page
is plain HTML with UTF-8 diacritics (â ê î ô û ã å ñ ç sh zh kh). We fetch,
strip the site navigation chrome + edition boilerplate, and keep the verse body.

A scripture may span several pages (Yasna = 12 pages, Yashts = ~22). List them
in the catalog under `avesta_paths` (relative to AVESTA_BASE).

Usage:
    python scripts/download-avesta.py --slug avesta-sbe04-ae
    python scripts/download-avesta.py --religion 瑣羅亞斯德 --all
"""

import argparse
import hashlib
import json
import random
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

AVESTA_BASE = "https://www.avesta.org/"
USER_AGENT = "religions-history-research/0.1 (academic research; contact: psyhangsau@gmail.com; +https://github.com/Hangsau/religions-history)"
REQ_TIMEOUT = 30
SLEEP_BETWEEN_REQUESTS = 0.5

_polite_req_count = 0
_LONG_PAUSE_EVERY = 100
_LONG_PAUSE_SECONDS = 30.0
MAX_RETRIES = 5
BACKOFF_INITIAL = 10.0

# Exact navigation strings that top/tail every page.
NAV_EXACT = {
    "Avesta -- Zoroastrian Archives", "Contents", "Prev", "Next", "English",
    "Home", "Glossary", "Avestan", "Transcription font", "Avestan font",
    "Sitemap", "Index...", "HTML", "PDF", "EPUB",
}
# Line prefixes that are edition boilerplate / editorial notes, not scripture.
DROP_PREFIXES = (
    "Avesta -- Zoroastrian", "Part ", "AVESTA:", "Based on edition",
    "Avesta, the Sacred", "of the Parsis", "Stuttgart", "This digital edition",
    "Comments in {}", "Punctuation and spelling", "to conform", "with other texts",
    "Translated by", "Please let me know", "A new translation", "normalized",
    "This edition", "Digital edition", "has been preserved",
)


def _polite_sleep_inline(base: float) -> None:
    global _polite_req_count
    _polite_req_count += 1
    time.sleep(base + random.uniform(0, 0.5))
    if _polite_req_count > 0 and _polite_req_count % _LONG_PAUSE_EVERY == 0:
        print(f"  [polite-pause] {_LONG_PAUSE_SECONDS:.0f}s break after {_polite_req_count} requests")
        time.sleep(_LONG_PAUSE_SECONDS)


def fetch_html(path_or_url: str) -> str:
    url = path_or_url if path_or_url.startswith("http") else urljoin(AVESTA_BASE, path_or_url.lstrip("/"))
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


def extract_avesta_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(["script", "style", "head"]):
        tag.decompose()
    lines = soup.get_text("\n", strip=True).split("\n")
    cleaned: list[str] = []
    for line in lines:
        s = line.strip()
        if not s:
            continue
        if s in NAV_EXACT:
            continue
        if any(s.startswith(p) for p in DROP_PREFIXES):
            continue
        cleaned.append(s)
    return "\n".join(cleaned)


def download_scripture(entry: dict) -> dict:
    slug = entry["slug"]
    paths = entry.get("avesta_paths") or ([entry["avesta_path"]] if entry.get("avesta_path") else [])
    if not paths:
        return {"slug": slug, "status": "error", "reason": "no avesta_path(s)"}

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
    for path in paths:
        url = urljoin(AVESTA_BASE, path.lstrip("/"))
        print(f"  [fetch] {path}")
        urls.append(url)
        _polite_sleep_inline(SLEEP_BETWEEN_REQUESTS)
        try:
            html = fetch_html(path)
        except FileNotFoundError:
            print(f"  [not-found] {path}")
            return {"slug": slug, "status": "not_found", "reason": path}
        except (RuntimeError, requests.RequestException) as e:
            return {"slug": slug, "status": "error", "reason": str(e)}
        text = extract_avesta_text(html)
        if text:
            chapters.append((Path(path).stem, text))

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
        "religion": entry.get("religion", "瑣羅亞斯德"),
        "language": entry.get("language", "阿維斯塔語"),
        "version": entry.get("version", "avesta.org (Geldner 1896 transliteration)"),
        "version_date": entry.get("version_date", "—"),
        "source_platform": "avesta.org",
        "source_url": urls[0],
        "downloaded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "size_bytes": len(original_bytes),
        "checksum_sha256": sha,
        "chapter_count": len(chapters),
        "expected_chapter_count": entry.get("expected_chapter_count"),
        "license": "Public domain / academic use (avesta.org)",
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
    name_map = {"瑣羅亞斯德": "zoroastrian-avesta.json"}
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
    for cat_file in CATALOG_DIR.glob("*-avesta*.json"):
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
            sys.exit(f"slug not in any avesta catalog: {args.slug}")
        r = download_scripture(e)
        print(json.dumps({k: v for k, v in r.items() if k != "meta"}, ensure_ascii=False, indent=2))
        return

    if args.religion:
        for e in load_catalog(args.religion):
            try:
                r = download_scripture(e)
            except Exception as ex:
                r = {"slug": e["slug"], "status": "exception", "reason": repr(ex)}
                print(f"[exception] {e['slug']}: {ex}")
        return

    p.print_help()


if __name__ == "__main__":
    main()
