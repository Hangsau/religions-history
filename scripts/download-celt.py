#!/usr/bin/env python
"""
Download Old/Middle Irish (and other Celtic) originals from CELT — the Corpus
of Electronic Texts, University College Cork (celt.ucc.ie).

CELT publishes each text at /published/<ID>.html. G-prefixed IDs are the
original-language editions (e.g. G301012 = Táin Bó Cúailnge Recension I, Old
Irish "Fecht n-óen do Ailill ⁊ do Meidb ..."); T-prefixed IDs are translations.
Each page is a rendered TEI document: a metadata header, then the title
repeated once, then the body, ending "Finit." with no trailing apparatus. We
cut the header by splitting on the SECOND occurrence of the <h1> title.

List the G-IDs per entry under `celt_ids`.

Usage:
    python scripts/download-celt.py --slug tain-bo-cuailnge-ga
    python scripts/download-celt.py --religion 凱爾特 --all
"""

import argparse
import hashlib
import json
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
CATALOG_DIR = ROOT / "scripts" / "catalog"
TRANSLATIONS_DIR = ROOT / "translations"

CELT_BASE = "https://celt.ucc.ie/published/"
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


def fetch_html(celt_id: str) -> str:
    url = CELT_BASE + celt_id + ".html"
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


def extract_celt_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(["script", "style", "head"]):
        tag.decompose()
    # The TEI header ends with a heading that repeats the title as
    # "<title>: Author: <name>" immediately before the body. Every heading that
    # carries "Author:" is header chrome; the LAST one is the pre-body anchor.
    author_heads = [h for h in soup.find_all(["h1", "h2", "h3"]) if "Author:" in h.get_text()]
    if author_heads:
        anchor = author_heads[-1]
        parts = [s.strip() for s in anchor.find_all_next(string=True)]
        full = "\n".join(parts)
    else:
        full = soup.get_text("\n", strip=True)
    lines = [ln.strip() for ln in full.split("\n") if ln.strip()]
    return "\n".join(lines)


def download_scripture(entry: dict) -> dict:
    slug = entry["slug"]
    ids = entry.get("celt_ids") or ([entry["celt_id"]] if entry.get("celt_id") else [])
    if not ids:
        return {"slug": slug, "status": "error", "reason": "no celt_id(s)"}

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
    for cid in ids:
        url = CELT_BASE + cid + ".html"
        print(f"  [fetch] {cid}")
        urls.append(url)
        _polite_sleep_inline(SLEEP_BETWEEN_REQUESTS)
        try:
            html = fetch_html(cid)
        except FileNotFoundError:
            print(f"  [not-found] {cid}")
            return {"slug": slug, "status": "not_found", "reason": cid}
        except (RuntimeError, requests.RequestException) as e:
            return {"slug": slug, "status": "error", "reason": str(e)}
        text = extract_celt_text(html)
        if text:
            chapters.append((cid, text))

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
        "religion": entry.get("religion", "凱爾特"),
        "language": entry.get("language", "古愛爾蘭語"),
        "version": entry.get("version", "CELT (celt.ucc.ie)"),
        "version_date": entry.get("version_date", "—"),
        "source_platform": "celt.ucc.ie",
        "source_url": urls[0],
        "downloaded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "size_bytes": len(original_bytes),
        "checksum_sha256": sha,
        "chapter_count": len(chapters),
        "expected_chapter_count": entry.get("expected_chapter_count"),
        "license": "Academic use (CELT / celt.ucc.ie, CC BY-NC or PD editions)",
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
    print(f"[ok] {slug}: {len(chapters)} texts, {meta['size_bytes']} bytes")
    return {"slug": slug, "status": "ok", "meta": meta}


def load_catalog(religion: str) -> list[dict]:
    name_map = {"凱爾特": "celtic-celt.json"}
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
    for cat_file in CATALOG_DIR.glob("*-celt*.json"):
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
            sys.exit(f"slug not in any celt catalog: {args.slug}")
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
