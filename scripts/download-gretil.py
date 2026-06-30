#!/usr/bin/env python
"""
Download Sanskrit texts from GRETIL (Göttingen Register of Electronic Texts in Indian Languages).

GRETIL hosts canonical Sanskrit text files at:
    http://gretil.sub.uni-goettingen.de/gretil/<category-path>/<file>.htm

Examples:
    - Rgveda: 1_sanskr/1_veda/1_sam/1_rv/rvh1-10u.htm
    - Bhagavad Gītā: 1_sanskr/2_epic/mbh/sas/02_bhag_u.htm  (need to check)
    - Yoga Sūtra: 1_sanskr/6_sastra/3_phil/yoga/...

Each entry is plain HTML with UTF-8 IAST Sanskrit text. We extract text content,
strip HTML markup, and keep the body Sanskrit.

Usage:
    python scripts/download-gretil.py --slug rigveda
    python scripts/download-gretil.py --religion 印度教梵文 --all
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
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
CATALOG_DIR = ROOT / "scripts" / "catalog"
TRANSLATIONS_DIR = ROOT / "translations"

GRETIL_BASE = "http://gretil.sub.uni-goettingen.de/gretil/"
USER_AGENT = "religions-history-research/0.1 (academic research; contact: psyhangsau@gmail.com; +https://github.com/Hangsau/religions-history)"
REQ_TIMEOUT = 30
SLEEP_BETWEEN_REQUESTS = 0.5

_polite_req_count = 0
_LONG_PAUSE_EVERY = 100
_LONG_PAUSE_SECONDS = 30.0
MAX_RETRIES = 5
BACKOFF_INITIAL = 10.0

# IAST diacritics common in Sanskrit text
SANSKRIT_CHARS = re.compile(r"[a-zA-Zāīūṛṝṅñṭḍṇśṣḥṃṁ̥]")



def _polite_sleep_inline(base: float) -> None:
    """Sleep base + random jitter; every 100 requests take 30s break."""
    global _polite_req_count
    _polite_req_count += 1
    time.sleep(base + random.uniform(0, 0.5))
    if _polite_req_count > 0 and _polite_req_count % _LONG_PAUSE_EVERY == 0:
        print(f"  [polite-pause] {_LONG_PAUSE_SECONDS:.0f}s break after {_polite_req_count} requests")
        time.sleep(_LONG_PAUSE_SECONDS)


def fetch_html(path_or_url: str) -> str:
    if path_or_url.startswith("http"):
        url = path_or_url
    else:
        url = urljoin(GRETIL_BASE, path_or_url.lstrip("/"))
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


def extract_sanskrit_text(html: str) -> str:
    """Extract Sanskrit text from GRETIL HTML, skipping the header notice."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(["script", "style", "head"]):
        tag.decompose()
    text = soup.get_text("\n", strip=True)
    lines = text.split("\n")

    # Skip GRETIL boilerplate
    drop_prefixes = [
        "THIS GRETIL TEXT FILE IS FOR REFERENCE",
        "COPYRIGHT AND TERMS OF USAGE",
        "Text converted to Unicode",
        "(This file is to be used",
        "set to UTF-8.",
        "description:",
        "multibyte sequence:",
    ]

    cleaned: list[str] = []
    skip_until_blank = False
    started = False
    for line in lines:
        s = line.strip()
        if not s:
            skip_until_blank = False
            continue
        if any(s.startswith(p) for p in drop_prefixes):
            skip_until_blank = True
            continue
        if skip_until_blank:
            # Skip until we get clearly text content
            if re.search(r"^\d|[āīūṛ]", s):
                skip_until_blank = False
            else:
                continue
        # Drop lines that are just metadata (URLs, attribution, etc) before main text
        if not started:
            if re.search(r"https?://|\.htm|\bedited by|\bDetlef\b", s, re.IGNORECASE):
                continue
            if re.match(r"^[A-Z][a-zA-Zāīūṛ ]{0,30}$", s) and "ā" not in s:
                # Likely text title only, skip
                continue
            started = True
        cleaned.append(s)
    return "\n".join(cleaned)


def download_scripture(entry: dict) -> dict:
    slug = entry["slug"]
    if entry.get("skip_reason"):
        print(f"[skip] {slug}: {entry['skip_reason']}")
        return {"slug": slug, "status": "skipped", "reason": entry["skip_reason"]}
    if entry.get("defer_reason"):
        print(f"[defer] {slug}: {entry['defer_reason']}")
        return {"slug": slug, "status": "deferred", "reason": entry["defer_reason"]}

    paths = entry.get("gretil_paths") or ([entry["gretil_path"]] if entry.get("gretil_path") else [])
    if not paths:
        return {"slug": slug, "status": "error", "reason": "no gretil_path(s)"}

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
        url = urljoin(GRETIL_BASE, path.lstrip("/"))
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
        text = extract_sanskrit_text(html)
        if text:
            label = Path(path).stem
            chapters.append((label, text))

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
        "religion": entry.get("religion", "印度教"),
        "language": entry.get("language", "Sanskrit"),
        "version": entry.get("version", "GRETIL standard edition"),
        "version_date": entry.get("version_date", "—"),
        "source_platform": "GRETIL",
        "source_url": urls[0],
        "downloaded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "size_bytes": len(original_bytes),
        "checksum_sha256": sha,
        "chapter_count": len(chapters),
        "expected_chapter_count": entry.get("expected_chapter_count"),
        "license": "Academic use (GRETIL reference)",
        "verified": False,
        "tier": entry.get("tier"),
        "notes": entry.get("notes"),
    }
    (TRANSLATIONS_DIR / slug / "meta.json").write_bytes(
        (json.dumps(meta, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    )
    print(f"[ok] {slug}: {len(chapters)} files, {meta['size_bytes']} bytes")
    return {"slug": slug, "status": "ok", "meta": meta}


def load_catalog(religion: str) -> list[dict]:
    name_map = {"印度教梵文": "hinduism-gretil.json", "印度教": "hinduism-gretil.json"}
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
    for cat_file in CATALOG_DIR.glob("hinduism-gretil*.json"):
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
            sys.exit(f"slug not in any hinduism-gretil catalog: {args.slug}")
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
