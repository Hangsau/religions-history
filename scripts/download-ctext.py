#!/usr/bin/env python
"""
Download a scripture from ctext.org and save to translations/<slug>/raw/.

Usage:
    python scripts/download-ctext.py --slug tao-te-ching
    python scripts/download-ctext.py --religion 道教 --all

Auto-detects single-page vs multi-chapter texts.

Output files (per scripture):
    translations/<slug>/raw/original.txt        ← Chinese text, with chapter separators
    translations/<slug>/raw/source-urls.txt     ← URLs fetched
    translations/<slug>/raw/checksums.sha256    ← SHA-256 of original.txt
    translations/<slug>/meta.json               ← metadata (validated against scripts/meta_template.json)
"""

import argparse
import hashlib
import json
import os
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
CHAPTER_SEP_RE = re.compile(r"^=== \d+ \|", re.MULTILINE)

CTEXT_BASE = "https://ctext.org"
USER_AGENT = "religions-history-research/0.1 (https://github.com/Hangsau/religions-history; academic use)"
REQ_TIMEOUT = 30
SLEEP_BETWEEN_REQUESTS = 1.5


def fetch(url: str) -> str:
    headers = {"User-Agent": USER_AGENT}
    r = requests.get(url, headers=headers, timeout=REQ_TIMEOUT)
    r.raise_for_status()
    r.encoding = "utf-8"
    return r.text


def extract_ctext_passages(html: str) -> list[str]:
    """Extract Chinese text passages from a ctext.org page.

    Returns list of stripped Chinese text strings (in document order),
    excluding label cells (e.g. '道德經:').
    """
    soup = BeautifulSoup(html, "html.parser")
    passages = []
    for td in soup.find_all("td", class_="ctext"):
        text = td.get_text(strip=True)
        if not text or len(text) < 5:
            continue
        if text.endswith((":", "：")):
            continue
        if not any("一" <= c <= "鿿" for c in text):
            continue
        passages.append(text)
    return passages


def find_subchapter_links(html: str, parent_slug: str) -> list[tuple[str, str]]:
    """Find sub-chapter pages linked from an index page.

    Returns list of (href, chapter_title) in document order.
    Only matches links of form /<parent_slug>/<subchapter>/zh.
    """
    soup = BeautifulSoup(html, "html.parser")
    links: list[tuple[str, str]] = []
    seen = set()
    href_re = re.compile(rf"^/?{re.escape(parent_slug)}/([^/]+)/zh/?$")
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("http"):
            # absolute URL — match the path portion
            m = re.match(rf"^https?://ctext\.org/{re.escape(parent_slug)}/([^/]+)/zh/?$", href)
            if not m:
                continue
            sub = m.group(1)
        else:
            m = href_re.match(href)
            if not m:
                continue
            sub = m.group(1)
        if sub in seen:
            continue
        seen.add(sub)
        title = a.get_text(strip=True) or sub
        full_url = urljoin(CTEXT_BASE, f"/{parent_slug}/{sub}/zh")
        links.append((full_url, title))
    return links


def download_scripture(entry: dict) -> dict:
    """Download one scripture. Returns updated meta dict."""
    slug = entry["slug"]
    ctext_slug = entry["ctext_slug"]
    multi = entry.get("multi_chapter", False)
    out_dir = TRANSLATIONS_DIR / slug / "raw"
    out_dir.mkdir(parents=True, exist_ok=True)

    fetched_urls: list[str] = []

    if entry.get("skip_reason"):
        print(f"[skip] {slug}: {entry['skip_reason']}")
        return {"slug": slug, "status": "skipped", "reason": entry["skip_reason"]}

    index_url = f"{CTEXT_BASE}/{ctext_slug}/zh"
    print(f"[fetch] {index_url}")
    fetched_urls.append(index_url)
    try:
        html = fetch(index_url)
    except requests.HTTPError as e:
        return {"slug": slug, "status": "fetch_error", "reason": str(e)}

    passages_on_index = extract_ctext_passages(html)
    total_chars_on_index = sum(len(p) for p in passages_on_index)

    chapters: list[tuple[str, str]] = []  # (title, text)

    if multi or len(passages_on_index) < 2 or total_chars_on_index < 200:
        sub_links = find_subchapter_links(html, ctext_slug)
        if not sub_links:
            # fall back to whatever we got
            if passages_on_index:
                for i, p in enumerate(passages_on_index, 1):
                    chapters.append((str(i), p))
            else:
                return {"slug": slug, "status": "empty", "reason": "no passages on index and no sub-chapters found"}
        else:
            print(f"[multi] {len(sub_links)} sub-chapters")
            for sub_url, sub_title in sub_links:
                time.sleep(SLEEP_BETWEEN_REQUESTS)
                print(f"  [fetch] {sub_url}")
                fetched_urls.append(sub_url)
                try:
                    sub_html = fetch(sub_url)
                except requests.HTTPError as e:
                    return {"slug": slug, "status": "fetch_error", "reason": f"{sub_url}: {e}"}
                sub_passages = extract_ctext_passages(sub_html)
                if not sub_passages:
                    continue
                joined = "\n\n".join(sub_passages)
                chapters.append((sub_title, joined))
    else:
        for i, p in enumerate(passages_on_index, 1):
            chapters.append((str(i), p))

    if not chapters:
        return {"slug": slug, "status": "empty", "reason": "no chapters extracted"}

    # Write original.txt
    lines = []
    for i, (title, text) in enumerate(chapters, 1):
        lines.append(f"=== {i} | {title} ===")
        lines.append(text)
        lines.append("")
    original_text = "\n".join(lines).rstrip() + "\n"
    original_bytes = original_text.encode("utf-8")
    original_path = out_dir / "original.txt"
    original_path.write_bytes(original_bytes)

    # Source URLs
    (out_dir / "source-urls.txt").write_bytes(("\n".join(fetched_urls) + "\n").encode("utf-8"))

    # SHA-256
    sha = hashlib.sha256(original_bytes).hexdigest()
    (out_dir / "checksums.sha256").write_bytes(f"{sha}  original.txt\n".encode("utf-8"))

    # meta.json
    meta_path = TRANSLATIONS_DIR / slug / "meta.json"
    meta = {
        "slug": slug,
        "name_zh": entry["name_zh"],
        "name_en": entry["name_en"],
        "name_original": entry["name_zh"],
        "religion": entry.get("religion", "道教"),
        "language": entry.get("language", "古典漢語"),
        "version": entry["version"],
        "version_date": entry["version_date"],
        "source_platform": "ctext.org",
        "source_url": index_url,
        "downloaded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "size_bytes": len(original_text.encode("utf-8")),
        "checksum_sha256": sha,
        "chapter_count": len(chapters),
        "expected_chapter_count": entry.get("expected_chapter_count"),
        "expected_size_min": entry.get("expected_size_min"),
        "expected_size_max": entry.get("expected_size_max"),
        "license": "CC BY-SA 4.0",
        "verified": False,
        "tier": entry.get("tier"),
        "notes": entry.get("notes"),
    }
    meta_path.write_bytes((json.dumps(meta, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))

    print(f"[ok] {slug}: {len(chapters)} chapters, {meta['size_bytes']} bytes")
    return {"slug": slug, "status": "ok", "meta": meta}


def load_catalog(religion: str) -> list[dict]:
    name_map = {"道教": "daoism.json", "儒教": "confucianism.json"}
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


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--slug", help="single scripture slug (project slug, e.g. tao-te-ching)")
    p.add_argument("--religion", help="download all scriptures of a religion (e.g. 道教)")
    p.add_argument("--all", action="store_true", help="(with --religion) download all, not just one")
    args = p.parse_args()

    if args.slug and not args.religion:
        # find which catalog
        for cat_file in CATALOG_DIR.glob("*.json"):
            data = json.loads(cat_file.read_text(encoding="utf-8"))
            for e in data["scriptures"]:
                if e["slug"] == args.slug:
                    e.setdefault("religion", data["religion"])
                    e.setdefault("language", data.get("language"))
                    r = download_scripture(e)
                    print(json.dumps(r, ensure_ascii=False, indent=2, default=str))
                    return
        sys.exit(f"slug not found in any catalog: {args.slug}")

    if args.religion:
        entries = load_catalog(args.religion)
        results = []
        for e in entries:
            try:
                r = download_scripture(e)
            except Exception as ex:
                r = {"slug": e["slug"], "status": "exception", "reason": str(ex)}
            results.append(r)
            time.sleep(SLEEP_BETWEEN_REQUESTS)
        summary = {s: sum(1 for r in results if r["status"] == s) for s in {r["status"] for r in results}}
        print("\n[summary]", json.dumps(summary, ensure_ascii=False))
        return

    p.print_help()


if __name__ == "__main__":
    main()
