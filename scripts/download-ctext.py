#!/usr/bin/env python
"""
Download a scripture from ctext.org via api.ctext.org and save to translations/<slug>/raw/.

Strategy (in order):
    1. Try API gettext(top_urn) — works for single-section texts (道德經, 黃帝陰符經)
    2. If response is {subsections: [...]}, recurse on each child URN
    3. If response is {error: ERR_REQUIRES_AUTHENTICATION}:
       - Use catalog `chapter_urns` if provided
       - Else mark text as `auth_required`, skip
    4. If ERR_INVALID_URN: ctext_slug wrong, mark `not_on_ctext`, skip

Usage:
    python scripts/download-ctext.py --slug tao-te-ching
    python scripts/download-ctext.py --religion 道教 --all

Auth: api.ctext.org gettext on individual leaf chapter URNs (like ctp:liezi/tian-rui)
does NOT need auth. So `chapter_urns` lists in catalog bypass the auth wall for top URNs.

Output files (per scripture):
    translations/<slug>/raw/original.txt        ← Chinese text, with chapter separators
    translations/<slug>/raw/source-urls.txt     ← API URLs fetched
    translations/<slug>/raw/checksums.sha256    ← SHA-256 of original.txt
    translations/<slug>/meta.json               ← metadata
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
CATALOG_DIR = ROOT / "scripts" / "catalog"
TRANSLATIONS_DIR = ROOT / "translations"

API_BASE = "https://api.ctext.org"
HTML_BASE = "https://ctext.org"
USER_AGENT = "religions-history-research/0.1 (https://github.com/Hangsau/religions-history; academic use)"
REQ_TIMEOUT = 30
SLEEP_BETWEEN_REQUESTS = 2.0
MAX_RETRIES = 5
BACKOFF_INITIAL = 20.0
MAX_RECURSION_DEPTH = 5


def fetch_json(url: str) -> dict:
    headers = {"User-Agent": USER_AGENT}
    backoff = BACKOFF_INITIAL
    last_exc = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.get(url, headers=headers, timeout=REQ_TIMEOUT)
            if r.status_code in (403, 429, 503):
                print(f"  [rate-limit {r.status_code}] sleep {backoff:.0f}s (attempt {attempt}/{MAX_RETRIES})")
                time.sleep(backoff)
                backoff *= 2
                continue
            r.raise_for_status()
            data = r.json()
            # API-level rate limit signal
            if isinstance(data, dict) and data.get("error", {}).get("code") == "ERR_REQUEST_LIMIT":
                print(f"  [api-rate-limit] sleep {backoff:.0f}s (attempt {attempt}/{MAX_RETRIES})")
                time.sleep(backoff)
                backoff *= 2
                continue
            return data
        except requests.RequestException as e:
            last_exc = e
            print(f"  [req-error {type(e).__name__}] sleep {backoff:.0f}s (attempt {attempt}/{MAX_RETRIES}): {e}")
            time.sleep(backoff)
            backoff *= 2
    raise requests.HTTPError(f"max retries exceeded for {url}: {last_exc}")


def gettext(urn: str) -> dict:
    url = f"{API_BASE}/gettext?urn={urn}"
    return fetch_json(url)


def fetch_urn_recursive(urn: str, fetched_urns: list[str], depth: int = 0, is_top: bool = False) -> list[tuple[str, list[str]]]:
    """Recursively fetch a URN and its subsections.

    Returns list of (leaf_urn, paragraphs) in document order.

    Semantics:
        - At chapter-level URN (has '/' after ctp:), fulltext items = paragraphs in one chapter.
        - At book-level URN (no '/'), if API returns fulltext directly (e.g. ctp:dao-de-jing
          gives 81 items), each item is a chapter — expand to N synthetic chapter URNs.
    """
    if depth > MAX_RECURSION_DEPTH:
        raise RuntimeError(f"max recursion depth at {urn}")

    print(f"  [gettext] {urn}")
    fetched_urns.append(urn)
    time.sleep(SLEEP_BETWEEN_REQUESTS)
    data = gettext(urn)

    if "error" in data:
        raise RuntimeError(f"gettext({urn}) -> {data['error'].get('code')}")

    if "fulltext" in data:
        items = list(data["fulltext"])
        urn_path = urn.split(":", 1)[-1] if ":" in urn else urn
        if "/" not in urn_path and is_top and len(items) > 1:
            # Top-level book URN returned flat fulltext = each item is a chapter
            return [(f"{urn}#{i}", [t]) for i, t in enumerate(items, 1)]
        return [(urn, items)]

    if "subsections" in data:
        results = []
        for sub_urn in data["subsections"]:
            results.extend(fetch_urn_recursive(sub_urn, fetched_urns, depth + 1, is_top=False))
        return results

    raise RuntimeError(f"gettext({urn}) -> unexpected response: {list(data.keys())}")


def urn_to_label(urn: str) -> str:
    """Extract a chapter label from a URN like 'ctp:analects/xue-er' -> 'xue-er'."""
    if "#" in urn:
        # synthetic flat chapter, e.g. ctp:dao-de-jing#5
        return urn.split("#", 1)[1]
    if ":" in urn:
        urn = urn.split(":", 1)[1]
    parts = urn.split("/")
    return "/".join(parts[1:]) if len(parts) > 1 else urn


def download_scripture(entry: dict) -> dict:
    slug = entry["slug"]
    if entry.get("skip_reason"):
        print(f"[skip] {slug}: {entry['skip_reason']}")
        return {"slug": slug, "status": "skipped", "reason": entry["skip_reason"]}
    if entry.get("defer_reason"):
        print(f"[defer] {slug}: {entry['defer_reason']}")
        return {"slug": slug, "status": "deferred", "reason": entry["defer_reason"]}
    ctext_slug = entry["ctext_slug"]
    out_dir = TRANSLATIONS_DIR / slug / "raw"

    meta_path_check = TRANSLATIONS_DIR / slug / "meta.json"
    if meta_path_check.exists():
        try:
            existing = json.loads(meta_path_check.read_text(encoding="utf-8"))
            if existing.get("verified") and (out_dir / "original.txt").exists():
                print(f"[skip] {slug}: already verified")
                return {"slug": slug, "status": "already_verified"}
        except (json.JSONDecodeError, OSError):
            pass

    out_dir.mkdir(parents=True, exist_ok=True)

    top_urn = f"ctp:{ctext_slug}"
    fetched_urns: list[str] = []

    # Use catalog-provided chapter URN list if present (bypass auth wall)
    chapter_urns = entry.get("chapter_urns")

    chapters: list[tuple[str, list[str]]] = []
    try:
        if chapter_urns:
            for cu in chapter_urns:
                print(f"  [gettext] {cu}")
                fetched_urns.append(cu)
                time.sleep(SLEEP_BETWEEN_REQUESTS)
                data = gettext(cu)
                if "error" in data:
                    raise RuntimeError(f"gettext({cu}) -> {data['error'].get('code')}")
                if "fulltext" not in data:
                    raise RuntimeError(f"gettext({cu}) -> no fulltext (keys: {list(data.keys())})")
                chapters.append((cu, list(data["fulltext"])))
        else:
            chapters = fetch_urn_recursive(top_urn, fetched_urns, is_top=True)
    except RuntimeError as e:
        msg = str(e)
        if "ERR_REQUIRES_AUTHENTICATION" in msg:
            print(f"[auth-required] {slug}: subsection discovery needs ctext API key")
            return {"slug": slug, "status": "auth_required", "reason": msg}
        if "ERR_INVALID_URN" in msg:
            print(f"[invalid-urn] {slug}: ctext_slug '{ctext_slug}' not found")
            return {"slug": slug, "status": "invalid_urn", "reason": msg}
        print(f"[error] {slug}: {msg}")
        return {"slug": slug, "status": "error", "reason": msg}
    except requests.RequestException as e:
        print(f"[fetch-error] {slug}: {e}")
        return {"slug": slug, "status": "fetch_error", "reason": str(e)}

    if not chapters:
        return {"slug": slug, "status": "empty", "reason": "no chapters"}

    # Build original.txt
    lines = []
    for i, (urn, paragraphs) in enumerate(chapters, 1):
        label = urn_to_label(urn)
        lines.append(f"=== {i} | {label} ===")
        lines.extend(paragraphs)
        lines.append("")
    original_text = "\n".join(lines).rstrip() + "\n"
    original_bytes = original_text.encode("utf-8")

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "original.txt").write_bytes(original_bytes)
    (out_dir / "source-urls.txt").write_bytes(("\n".join(f"{API_BASE}/gettext?urn={u}" for u in fetched_urns) + "\n").encode("utf-8"))
    sha = hashlib.sha256(original_bytes).hexdigest()
    (out_dir / "checksums.sha256").write_bytes(f"{sha}  original.txt\n".encode("utf-8"))

    meta = {
        "slug": slug,
        "name_zh": entry["name_zh"],
        "name_en": entry["name_en"],
        "name_original": entry["name_zh"],
        "religion": entry.get("religion", "道教"),
        "language": entry.get("language", "古典漢語"),
        "version": entry["version"],
        "version_date": entry["version_date"],
        "source_platform": "ctext.org (api)",
        "source_url": f"{API_BASE}/gettext?urn={top_urn}",
        "downloaded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "size_bytes": len(original_bytes),
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
    (TRANSLATIONS_DIR / slug / "meta.json").write_bytes((json.dumps(meta, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))

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


def find_entry(slug: str) -> dict | None:
    for cat_file in CATALOG_DIR.glob("*.json"):
        data = json.loads(cat_file.read_text(encoding="utf-8"))
        for e in data["scriptures"]:
            if e["slug"] == slug:
                e.setdefault("religion", data["religion"])
                e.setdefault("language", data.get("language"))
                return e
    return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--slug", help="single scripture slug")
    p.add_argument("--religion", help="download all scriptures of a religion (e.g. 道教)")
    p.add_argument("--all", action="store_true", help="(with --religion) iterate all entries")
    args = p.parse_args()

    if args.slug and not args.religion:
        e = find_entry(args.slug)
        if not e:
            sys.exit(f"slug not in any catalog: {args.slug}")
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
