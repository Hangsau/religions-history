#!/usr/bin/env python
"""
Download public-domain full texts from archive.org (Internet Archive).

Use for pre-1928 PD editions that are NOT cleanly available on wikisource /
sacred-texts (e.g. early Baha'i translations whose modern Haifa editions are
copyright-asserted, but whose original 1906/1908 printings are US public domain).

archive.org fulltext lives at:
    https://archive.org/download/<identifier>/<identifier>_djvu.txt

That file is raw OCR of the scanned book — page running-heads, hyphenation and
occasional garble. We store it as a single `=== 1 | <title> ===` section and
lightly clean form-feeds / trailing whitespace. Structural chapter splitting is
left to the translation pass; provenance (OCR, edition, IA identifier) is noted
in meta.json so downstream knows it is a scan, not a curated etext.

Catalog entry (scripts/catalog/<religion>-archive.json):
{
  "slug": "some-answered-questions",
  "ia_identifier": "someansweredques00abduiala",
  "name_zh": "已答之問",
  "name_en": "Some Answered Questions",
  "religion": "巴哈伊",
  "version": "Laura Clifford Barney tr., 1908 (1st ed.)",
  "version_date": "1908 AD",
  "tier": "核心",
  "is_original_language": false
}

Usage:
    PYTHONIOENCODING=utf-8 python scripts/download-archive.py --slug some-answered-questions
    PYTHONIOENCODING=utf-8 python scripts/download-archive.py --catalog bahai-archive.json --all
"""

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _polite import USER_AGENT, polite_sleep  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CATALOG_DIR = ROOT / "scripts" / "catalog"
TRANSLATIONS_DIR = ROOT / "translations"

IA_BASE = "https://archive.org/download"
REQ_TIMEOUT = 60
MAX_RETRIES = 5
BACKOFF_INITIAL = 10.0


def fetch_text(url: str) -> str:
    headers = {"User-Agent": USER_AGENT}
    backoff = BACKOFF_INITIAL
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.get(url, headers=headers, timeout=REQ_TIMEOUT)
            if r.status_code == 404:
                raise FileNotFoundError(f"404 at {url}")
            if r.status_code in (429, 503):
                print(f"  [rate-limit {r.status_code}] sleep {backoff:.0f}s")
                polite_sleep(backoff)
                backoff *= 2
                continue
            r.raise_for_status()
            r.encoding = "utf-8"
            return r.text
        except requests.RequestException as e:
            print(f"  [req-error attempt {attempt}/{MAX_RETRIES}] sleep {backoff:.0f}s: {e}")
            polite_sleep(backoff)
            backoff *= 2
    raise RuntimeError(f"max retries exceeded for {url}")


def clean_ocr(raw: str) -> str:
    """Light cleanup of djvu OCR: drop form-feeds, normalize newlines, trim
    trailing whitespace per line, collapse >2 blank lines. No aggressive
    de-hyphenation — that risks corrupting genuine text."""
    text = raw.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\x0c", "\n")  # form feed = page break
    lines = [ln.rstrip() for ln in text.split("\n")]
    out = []
    blank = 0
    for ln in lines:
        if ln.strip():
            blank = 0
            out.append(ln)
        else:
            blank += 1
            if blank <= 2:
                out.append("")
    return "\n".join(out).strip() + "\n"


def download_scripture(entry: dict) -> dict:
    slug = entry["slug"]
    identifier = entry.get("ia_identifier")
    if not identifier:
        return {"slug": slug, "status": "error", "reason": "no ia_identifier"}

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

    url = f"{IA_BASE}/{identifier}/{identifier}_djvu.txt"
    print(f"  [fetch] {url}")
    polite_sleep(0.5)
    try:
        raw = fetch_text(url)
    except FileNotFoundError as e:
        return {"slug": slug, "status": "not_found", "reason": str(e)}
    except (RuntimeError, requests.RequestException) as e:
        return {"slug": slug, "status": "error", "reason": str(e)}

    body = clean_ocr(raw)
    if len(body.strip()) < 500:
        return {"slug": slug, "status": "empty", "reason": f"only {len(body)} chars"}

    title = entry.get("name_en") or slug
    original_text = f"=== 1 | {title} ===\n{body}"
    original_bytes = original_text.encode("utf-8")

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "original.txt").write_bytes(original_bytes)
    details_url = f"https://archive.org/details/{identifier}"
    (out_dir / "source-urls.txt").write_bytes((url + "\n" + details_url + "\n").encode("utf-8"))
    sha = hashlib.sha256(original_bytes).hexdigest()
    (out_dir / "checksums.sha256").write_bytes(f"{sha}  original.txt\n".encode("utf-8"))

    notes = entry.get("notes") or ""
    prov = f"archive.org OCR (_djvu.txt) of scan {identifier}; light cleanup only, chapter structure not split."
    notes = (notes + " " + prov).strip() if notes else prov

    meta = {
        "slug": slug,
        "name_zh": entry["name_zh"],
        "name_en": entry.get("name_en", ""),
        "name_original": entry.get("name_original") or entry["name_zh"],
        "religion": entry.get("religion", "—"),
        "tradition": entry.get("tradition"),
        "language": entry.get("language", "English"),
        "version": entry.get("version", "archive.org scan"),
        "version_date": entry.get("version_date", "—"),
        "source_platform": "archive.org",
        "source_url": details_url,
        "downloaded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "size_bytes": len(original_bytes),
        "checksum_sha256": sha,
        "chapter_count": 1,
        "expected_chapter_count": entry.get("expected_chapter_count"),
        "license": entry.get("license", "Public Domain (pre-1928 US publication)"),
        "verified": False,
        "tier": entry.get("tier"),
        "text_role": entry.get("text_role"),
        "is_original_language": entry.get("is_original_language", False),
        "notes": notes,
    }
    (TRANSLATIONS_DIR / slug / "meta.json").write_bytes(
        (json.dumps(meta, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    )
    print(f"[ok] {slug}: OCR fulltext, {meta['size_bytes']} bytes")
    return {"slug": slug, "status": "ok", "meta": meta}


def load_catalog(name: str) -> dict:
    return json.loads((CATALOG_DIR / name).read_text(encoding="utf-8"))


def find_entry(slug: str) -> tuple[dict, dict]:
    for path in CATALOG_DIR.glob("*archive*.json"):
        cat = json.loads(path.read_text(encoding="utf-8"))
        for e in cat.get("scriptures", []):
            if e["slug"] == slug:
                return cat, e
    raise SystemExit(f"slug not found in any *archive*.json catalog: {slug}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug")
    ap.add_argument("--catalog")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()

    if args.slug:
        _, entry = find_entry(args.slug)
        res = download_scripture(entry)
        print(json.dumps(res.get("status"), ensure_ascii=False))
        return

    if args.catalog and args.all:
        cat = load_catalog(args.catalog)
        results = []
        for e in cat.get("scriptures", []):
            results.append(download_scripture(e))
        ok = sum(1 for r in results if r["status"] in ("ok", "already_verified"))
        print(f"\n=== {ok}/{len(results)} ok ===")
        for r in results:
            if r["status"] not in ("ok", "already_verified"):
                print(f"  {r['status']}: {r['slug']} — {r.get('reason','')}")
        return

    ap.error("need --slug X, or --catalog F --all")


if __name__ == "__main__":
    main()
