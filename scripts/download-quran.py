#!/usr/bin/env python
"""
Download Quran from Quran.com API and Tanzil and save to translations/<slug>/raw/.

Quran.com API:
    https://api.quran.com/api/v4/verses/by_chapter/<n>?language=ar&per_page=300

Returns Arabic text per verse. Quran has 114 chapters (surah), 6236 verses.

Usage:
    python scripts/download-quran.py --slug quran-al-fatiha
    python scripts/download-quran.py --religion 伊斯蘭 --all
"""

import argparse
import hashlib
import json
import re
import sys
import time
import random
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
CATALOG_DIR = ROOT / "scripts" / "catalog"
TRANSLATIONS_DIR = ROOT / "translations"

QURAN_API = "https://api.quran.com/api/v4"
USER_AGENT = "religions-history-research/0.1 (academic research; contact: psyhangsau@gmail.com; +https://github.com/Hangsau/religions-history)"
REQ_TIMEOUT = 30
SLEEP_BETWEEN_REQUESTS = 0.3

_polite_req_count = 0
_LONG_PAUSE_EVERY = 100
_LONG_PAUSE_SECONDS = 30.0
MAX_RETRIES = 5
BACKOFF_INITIAL = 10.0



def _polite_sleep_inline(base: float) -> None:
    """Sleep base + random jitter; every 100 requests take 30s break."""
    global _polite_req_count
    _polite_req_count += 1
    time.sleep(base + random.uniform(0, 0.5))
    if _polite_req_count > 0 and _polite_req_count % _LONG_PAUSE_EVERY == 0:
        print(f"  [polite-pause] {_LONG_PAUSE_SECONDS:.0f}s break after {_polite_req_count} requests")
        time.sleep(_LONG_PAUSE_SECONDS)


def api_get(path: str, params: dict | None = None) -> dict:
    url = f"{QURAN_API}/{path.lstrip('/')}"
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


def fetch_surah_verses(surah: int) -> list[tuple[str, str]]:
    """Return list of (verse_key, arabic_text) for one surah."""
    page = 1
    verses: list[tuple[str, str]] = []
    while True:
        data = api_get("verses/by_chapter/" + str(surah),
                       params={"per_page": 300, "page": page, "fields": "text_uthmani,verse_key"})
        items = data.get("verses", [])
        if not items:
            break
        for v in items:
            ar = v.get("text_uthmani") or v.get("text_imlaei") or ""
            verses.append((v.get("verse_key"), ar))
        if data.get("pagination", {}).get("next_page"):
            page = data["pagination"]["next_page"]
            _polite_sleep_inline(SLEEP_BETWEEN_REQUESTS)
        else:
            break
    return verses


def download_scripture(entry: dict) -> dict:
    slug = entry["slug"]
    if entry.get("skip_reason"):
        print(f"[skip] {slug}: {entry['skip_reason']}")
        return {"slug": slug, "status": "skipped", "reason": entry["skip_reason"]}
    if entry.get("defer_reason"):
        print(f"[defer] {slug}: {entry['defer_reason']}")
        return {"slug": slug, "status": "deferred", "reason": entry["defer_reason"]}

    surah_range = entry.get("surah_range")  # e.g. [1, 114]
    if not surah_range:
        return {"slug": slug, "status": "error", "reason": "no surah_range"}

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

    lo, hi = surah_range
    print(f"  [surahs] {lo}-{hi}")
    chapters: list[tuple[str, str]] = []
    for s in range(lo, hi + 1):
        print(f"  [surah] {s}")
        _polite_sleep_inline(SLEEP_BETWEEN_REQUESTS)
        try:
            verses = fetch_surah_verses(s)
        except RuntimeError as e:
            return {"slug": slug, "status": "error", "reason": f"surah {s}: {e}"}
        if not verses:
            continue
        text = "\n".join(f"{vk}    {ar}" for vk, ar in verses)
        chapters.append((str(s), text))

    if not chapters:
        return {"slug": slug, "status": "empty"}

    out_dir.mkdir(parents=True, exist_ok=True)
    lines = []
    for i, (label, text) in enumerate(chapters, 1):
        lines.append(f"=== {i} | 章{label} ===")
        lines.append(text)
        lines.append("")
    original_text = "\n".join(lines).rstrip() + "\n"
    original_bytes = original_text.encode("utf-8")

    (out_dir / "original.txt").write_bytes(original_bytes)
    (out_dir / "source-urls.txt").write_bytes(
        ("\n".join(f"{QURAN_API}/verses/by_chapter/{s}" for s in range(lo, hi + 1)) + "\n").encode("utf-8")
    )
    sha = hashlib.sha256(original_bytes).hexdigest()
    (out_dir / "checksums.sha256").write_bytes(f"{sha}  original.txt\n".encode("utf-8"))

    meta = {
        "slug": slug,
        "name_zh": entry["name_zh"],
        "name_en": entry.get("name_en", ""),
        "name_original": entry.get("name_original") or entry["name_zh"],
        "religion": entry.get("religion", "伊斯蘭"),
        "language": entry.get("language", "古典阿拉伯"),
        "version": entry.get("version", "Uthmani 正典本"),
        "version_date": entry.get("version_date", "651 AD"),
        "source_platform": "Quran.com API",
        "source_url": f"https://quran.com/{lo}",
        "downloaded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "size_bytes": len(original_bytes),
        "checksum_sha256": sha,
        "chapter_count": len(chapters),
        "expected_chapter_count": entry.get("expected_chapter_count"),
        "license": "Public Domain (Uthmani text)",
        "verified": False,
        "tier": entry.get("tier"),
        "notes": entry.get("notes"),
    }
    (TRANSLATIONS_DIR / slug / "meta.json").write_bytes(
        (json.dumps(meta, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    )
    print(f"[ok] {slug}: {len(chapters)} surahs, {meta['size_bytes']} bytes")
    return {"slug": slug, "status": "ok", "meta": meta}


def load_catalog(religion: str) -> list[dict]:
    name_map = {"伊斯蘭": "islam.json"}
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
    for cat_file in CATALOG_DIR.glob("islam*.json"):
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
            sys.exit(f"slug not in any islam catalog: {args.slug}")
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
