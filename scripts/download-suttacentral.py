#!/usr/bin/env python
"""
Download Pali Buddhist scriptures from SuttaCentral and save to translations/<slug>/raw/.

SuttaCentral API:
    https://suttacentral.net/api/menu/<uid>          → list children (suttaplex menu)
    https://suttacentral.net/api/bilarasuttas/<uid>/sujato?lang=en
        → returns dict with root_text (Pali) + translation_text (English) by segment ID

Usage:
    python scripts/download-suttacentral.py --slug digha-nikaya
    python scripts/download-suttacentral.py --religion 巴利佛經 --all
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

SC_API = "https://suttacentral.net/api"
USER_AGENT = "religions-history-research/0.1 (academic research; contact: psyhangsau@gmail.com; +https://github.com/Hangsau/religions-history)"
REQ_TIMEOUT = 30
SLEEP_BETWEEN_REQUESTS = 0.5

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


def api_get(path: str) -> dict | list:
    url = f"{SC_API}/{path.lstrip('/')}"
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
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
            return r.json()
        except requests.RequestException as e:
            print(f"  [req-error attempt {attempt}/{MAX_RETRIES}] sleep {backoff:.0f}s: {e}")
            time.sleep(backoff)
            backoff *= 2
    raise RuntimeError(f"max retries exceeded for {url}")


def list_leaf_uids(uid: str, depth: int = 0) -> list[str]:
    """Recursively walk menu/<uid> to get all leaf sutta UIDs."""
    if depth > 6:
        return []
    try:
        data = api_get(f"menu/{uid}")
    except FileNotFoundError:
        return []
    leaves: list[str] = []
    for item in data if isinstance(data, list) else [data]:
        if not item:
            continue
        children = item.get("children") or []
        if children:
            for child in children:
                child_uid = child.get("uid")
                if not child_uid:
                    continue
                if child.get("node_type") == "leaf":
                    leaves.append(child_uid)
                else:
                    _polite_sleep_inline(SLEEP_BETWEEN_REQUESTS)
                    leaves.extend(list_leaf_uids(child_uid, depth + 1))
        elif item.get("uid"):
            leaves.append(item["uid"])
    return leaves


def fetch_sutta_text(sutta_uid: str) -> tuple[str, str]:
    """Get (pali_text, english_text) for a sutta via bilarasuttas/<uid>/sujato."""
    try:
        data = api_get(f"bilarasuttas/{sutta_uid}/sujato?lang=en")
    except FileNotFoundError:
        return "", ""
    root = data.get("root_text") or {}
    trans = data.get("translation_text") or {}
    keys = data.get("keys_order") or sorted(root.keys())
    pali = "\n".join(root.get(k, "").strip() for k in keys if root.get(k))
    english = "\n".join(trans.get(k, "").strip() for k in keys if trans.get(k))
    return pali, english


def download_scripture(entry: dict) -> dict:
    slug = entry["slug"]
    if entry.get("skip_reason"):
        print(f"[skip] {slug}: {entry['skip_reason']}")
        return {"slug": slug, "status": "skipped", "reason": entry["skip_reason"]}
    if entry.get("defer_reason"):
        print(f"[defer] {slug}: {entry['defer_reason']}")
        return {"slug": slug, "status": "deferred", "reason": entry["defer_reason"]}

    root_uid = entry.get("sc_uid")
    if not root_uid:
        return {"slug": slug, "status": "error", "reason": "no sc_uid"}

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

    print(f"  [menu] {root_uid}")
    try:
        leaves = list_leaf_uids(root_uid)
    except (RuntimeError, FileNotFoundError) as e:
        return {"slug": slug, "status": "error", "reason": str(e)}

    if not leaves:
        # Try fetching directly as a leaf
        leaves = [root_uid]

    print(f"  [leaves] {len(leaves)} suttas")
    chapters_pali: list[tuple[str, str]] = []
    chapters_en: list[tuple[str, str]] = []
    fetched: list[str] = []

    for uid in leaves:
        print(f"  [sutta] {uid}")
        fetched.append(uid)
        _polite_sleep_inline(SLEEP_BETWEEN_REQUESTS)
        try:
            pali, english = fetch_sutta_text(uid)
        except RuntimeError as e:
            return {"slug": slug, "status": "error", "reason": f"{uid}: {e}"}
        except FileNotFoundError:
            continue
        if pali:
            chapters_pali.append((uid, pali))
        if english:
            chapters_en.append((uid, english))

    if not chapters_pali and not chapters_en:
        return {"slug": slug, "status": "empty"}

    out_dir.mkdir(parents=True, exist_ok=True)
    primary = chapters_pali if chapters_pali else chapters_en
    primary_lang = "Pali" if chapters_pali else "English"
    lines = []
    for i, (label, text) in enumerate(primary, 1):
        lines.append(f"=== {i} | {label} ===")
        lines.append(text)
        lines.append("")
    original_text = "\n".join(lines).rstrip() + "\n"
    original_bytes = original_text.encode("utf-8")
    (out_dir / "original.txt").write_bytes(original_bytes)
    sha = hashlib.sha256(original_bytes).hexdigest()
    (out_dir / "checksums.sha256").write_bytes(f"{sha}  original.txt\n".encode("utf-8"))

    if chapters_en and chapters_pali:
        en_lines = []
        for i, (label, text) in enumerate(chapters_en, 1):
            en_lines.append(f"=== {i} | {label} ===")
            en_lines.append(text)
            en_lines.append("")
        (out_dir / "translation-en.txt").write_bytes(("\n".join(en_lines).rstrip() + "\n").encode("utf-8"))

    (out_dir / "source-urls.txt").write_bytes(
        ("\n".join(f"{SC_API}/bilarasuttas/{u}/sujato?lang=en" for u in fetched) + "\n").encode("utf-8")
    )

    meta = {
        "slug": slug,
        "name_zh": entry["name_zh"],
        "name_en": entry.get("name_en", ""),
        "name_original": entry.get("name_original") or entry["name_zh"],
        "religion": entry.get("religion", "佛教-巴利"),
        "language": entry.get("language", primary_lang),
        "version": entry.get("version", "SuttaCentral 校勘版"),
        "version_date": entry.get("version_date", "—"),
        "source_platform": "SuttaCentral",
        "source_url": f"https://suttacentral.net/{root_uid}",
        "downloaded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "size_bytes": len(original_bytes),
        "checksum_sha256": sha,
        "chapter_count": len(primary),
        "expected_chapter_count": entry.get("expected_chapter_count"),
        "license": "CC BY-NC 4.0 (Sujato)",
        "verified": False,
        "tier": entry.get("tier"),
        "notes": entry.get("notes"),
    }
    (TRANSLATIONS_DIR / slug / "meta.json").write_bytes(
        (json.dumps(meta, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    )
    print(f"[ok] {slug}: {len(primary)} suttas, {meta['size_bytes']} bytes ({primary_lang})")
    return {"slug": slug, "status": "ok", "meta": meta}


def load_catalog(religion: str) -> list[dict]:
    name_map = {"巴利佛經": "buddhism-pali.json", "佛教-巴利": "buddhism-pali.json"}
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
    for cat_file in CATALOG_DIR.glob("buddhism-pali*.json"):
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
            sys.exit(f"slug not in any buddhism-pali catalog: {args.slug}")
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
