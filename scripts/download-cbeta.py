#!/usr/bin/env python
"""
Download a Buddhist scripture from CBETA (Chinese Buddhist Electronic Text Association)
and save to translations/<slug>/raw/.

CBETA has the complete 漢譯大藏經 (Taisho + Shinsan) with open API:
    https://cbetaonline.dila.edu.tw/api/

API structure (open, no auth, no hard rate limit for individual users):
    /api/totals → high-level catalogue summary
    /api/works/<work-id> → metadata for a work (e.g. T0250 for 心經, T0235 for 金剛經)
    /api/juans/<work-id>/<juan> → text of one juan (卷)

Usage:
    python scripts/download-cbeta.py --slug heart-sutra-kumarajiva
    python scripts/download-cbeta.py --religion 漢譯佛經 --all
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

CBETA_API = "https://cbetaonline.dila.edu.tw/api"
USER_AGENT = "religions-history-research/0.1 (https://github.com/Hangsau/religions-history; academic use)"
REQ_TIMEOUT = 30
SLEEP_BETWEEN_REQUESTS = 1.0
MAX_RETRIES = 5
BACKOFF_INITIAL = 15.0


def api_get(path: str, params: dict | None = None) -> dict:
    url = f"{CBETA_API}/{path.lstrip('/')}"
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


def fetch_work_juans(work_id: str) -> list[str]:
    """Get list of juan numbers for a work via /api/works/<work_id>."""
    data = api_get(f"works/{work_id}")
    # Response structure varies; the works endpoint returns metadata including juan list
    if "results" in data and data["results"]:
        w = data["results"][0]
        juan_count = w.get("juan", 1)
        if isinstance(juan_count, str) and juan_count.isdigit():
            juan_count = int(juan_count)
        return [str(i) for i in range(1, juan_count + 1)]
    return ["1"]


def fetch_juan_text(work_id: str, juan: str) -> str:
    """Fetch one juan's text. Tries multiple endpoint shapes."""
    # The CBETA API returns html-ish content; we strip tags for plain text.
    data = api_get(f"juans", params={"work": work_id, "juan": juan, "format": "json"})
    # Adapt to actual response shape
    if isinstance(data, dict):
        if "results" in data and data["results"]:
            first = data["results"][0]
            for key in ("body", "content", "text", "html"):
                if key in first and first[key]:
                    return strip_html(first[key])
        for key in ("body", "content", "text", "html"):
            if key in data and data[key]:
                return strip_html(data[key])
    return ""


def strip_html(html: str) -> str:
    text = re.sub(r"<[^>]+>", "", html)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&lt;", "<", text)
    text = re.sub(r"&gt;", ">", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"　+", "　", text)
    text = re.sub(r"\n\s*\n", "\n\n", text)
    return text.strip()


def download_scripture(entry: dict) -> dict:
    slug = entry["slug"]
    if entry.get("skip_reason"):
        print(f"[skip] {slug}: {entry['skip_reason']}")
        return {"slug": slug, "status": "skipped", "reason": entry["skip_reason"]}
    if entry.get("defer_reason"):
        print(f"[defer] {slug}: {entry['defer_reason']}")
        return {"slug": slug, "status": "deferred", "reason": entry["defer_reason"]}

    work_id = entry.get("cbeta_work_id")
    if not work_id:
        return {"slug": slug, "status": "error", "reason": "no cbeta_work_id"}

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

    try:
        juans = entry.get("juans") or fetch_work_juans(work_id)
        print(f"  [work] {work_id} ({len(juans)} juans)")
        chapters: list[tuple[str, str]] = []
        urls: list[str] = []
        for j in juans:
            print(f"  [juan] {work_id} 卷 {j}")
            time.sleep(SLEEP_BETWEEN_REQUESTS)
            urls.append(f"{CBETA_API}/juans?work={work_id}&juan={j}")
            text = fetch_juan_text(work_id, j)
            if text.strip():
                chapters.append((j, text))
    except (RuntimeError, requests.RequestException) as e:
        return {"slug": slug, "status": "error", "reason": str(e)}

    if not chapters:
        return {"slug": slug, "status": "empty", "reason": f"no text returned for {work_id}"}

    out_dir.mkdir(parents=True, exist_ok=True)
    lines = []
    for i, (label, text) in enumerate(chapters, 1):
        lines.append(f"=== {i} | 卷{label} ===")
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
        "religion": entry.get("religion", "佛教-漢譯"),
        "language": entry.get("language", "古典漢語"),
        "version": entry.get("version", f"CBETA {work_id}"),
        "version_date": entry.get("version_date", "—"),
        "source_platform": "CBETA",
        "source_url": f"https://cbetaonline.dila.edu.tw/zh/{work_id}",
        "downloaded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "size_bytes": len(original_bytes),
        "checksum_sha256": sha,
        "chapter_count": len(chapters),
        "expected_chapter_count": entry.get("expected_chapter_count"),
        "expected_size_min": entry.get("expected_size_min"),
        "expected_size_max": entry.get("expected_size_max"),
        "license": "CC BY-NC-SA 4.0 (CBETA)",
        "verified": False,
        "tier": entry.get("tier"),
        "notes": entry.get("notes"),
    }
    (TRANSLATIONS_DIR / slug / "meta.json").write_bytes(
        (json.dumps(meta, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    )
    print(f"[ok] {slug}: {len(chapters)} juans, {meta['size_bytes']} bytes")
    return {"slug": slug, "status": "ok", "meta": meta}


def load_catalog(religion: str) -> list[dict]:
    name_map = {"漢譯佛經": "buddhism-cbeta.json"}
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
    for cat_file in CATALOG_DIR.glob("buddhism-cbeta*.json"):
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
            sys.exit(f"slug not in any buddhism-cbeta catalog: {args.slug}")
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
