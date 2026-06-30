#!/usr/bin/env python
"""
Download SBLGNT (Society of Biblical Literature Greek New Testament) from
GitHub morphgnt/sblgnt repo and save Greek NT 27 books to translations/.

Source format (one file per book):
    morphgnt: BCV TAG WORD_NFC WORD_NORM_LEMMA LEMMA
    e.g.: 010101 N- ----NSF- Βίβλος Βίβλος βίβλος βίβλος

We extract column 5 (normalized form) and group by verse (BCV).

Output:
    translations/sblgnt-<book-slug>/raw/original.txt
        === N | <chapter> ===
        1:1    Βίβλος γενέσεως Ἰησοῦ Χριστοῦ υἱοῦ Δαυὶδ ...
        1:2    Ἀβραὰμ ἐγέννησεν τὸν Ἰσαάκ, ...
        ...

Usage:
    python scripts/download-sblgnt.py --slug sblgnt-matthew
    python scripts/download-sblgnt.py --religion 基督教-希臘新約 --all
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

SBLGNT_RAW = "https://raw.githubusercontent.com/morphgnt/sblgnt/master"
USER_AGENT = "religions-history-research/0.1 (https://github.com/Hangsau/religions-history; academic use)"
REQ_TIMEOUT = 30
SLEEP_BETWEEN_REQUESTS = 0.5
MAX_RETRIES = 5
BACKOFF_INITIAL = 10.0


def fetch_text(filename: str) -> str:
    url = f"{SBLGNT_RAW}/{filename}"
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


def parse_morphgnt(text: str) -> list[tuple[str, int, int, list[str]]]:
    """Parse a morphgnt file. Returns list of (verse_key, chap, verse, [words])."""
    verses: dict[tuple[int, int], list[str]] = {}
    book_id = None
    for line in text.split("\n"):
        parts = line.split()
        if len(parts) < 5:
            continue
        bcv = parts[0]
        if len(bcv) != 6 or not bcv.isdigit():
            continue
        book_n = int(bcv[:2])
        chap = int(bcv[2:4])
        verse = int(bcv[4:6])
        # Column 5 is form with diacritics (NFC normalized)
        word = parts[4] if len(parts) > 4 else ""
        if not word:
            continue
        book_id = book_n
        key = (chap, verse)
        verses.setdefault(key, []).append(word)
    out = []
    for (chap, verse), words in sorted(verses.items()):
        out.append((f"{chap}:{verse}", chap, verse, words))
    return out


def download_scripture(entry: dict) -> dict:
    slug = entry["slug"]
    if entry.get("skip_reason"):
        print(f"[skip] {slug}: {entry['skip_reason']}")
        return {"slug": slug, "status": "skipped", "reason": entry["skip_reason"]}
    if entry.get("defer_reason"):
        print(f"[defer] {slug}: {entry['defer_reason']}")
        return {"slug": slug, "status": "deferred", "reason": entry["defer_reason"]}

    filename = entry.get("sblgnt_file")
    if not filename:
        return {"slug": slug, "status": "error", "reason": "no sblgnt_file"}

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

    print(f"  [fetch] {filename}")
    time.sleep(SLEEP_BETWEEN_REQUESTS)
    try:
        raw = fetch_text(filename)
    except FileNotFoundError as e:
        return {"slug": slug, "status": "not_found", "reason": str(e)}
    except (RuntimeError, requests.RequestException) as e:
        return {"slug": slug, "status": "error", "reason": str(e)}

    verses = parse_morphgnt(raw)
    if not verses:
        return {"slug": slug, "status": "empty"}

    # Group by chapter
    chapters: dict[int, list[tuple[int, str]]] = {}
    for vk, ch, v, words in verses:
        chapters.setdefault(ch, []).append((v, " ".join(words)))

    out_dir.mkdir(parents=True, exist_ok=True)
    lines = []
    for ch in sorted(chapters):
        lines.append(f"=== {ch} | chapter {ch} ===")
        for v, text in sorted(chapters[ch]):
            lines.append(f"{ch}:{v}    {text}")
        lines.append("")
    original_text = "\n".join(lines).rstrip() + "\n"
    original_bytes = original_text.encode("utf-8")

    (out_dir / "original.txt").write_bytes(original_bytes)
    (out_dir / "source-urls.txt").write_bytes(f"{SBLGNT_RAW}/{filename}\n".encode("utf-8"))
    sha = hashlib.sha256(original_bytes).hexdigest()
    (out_dir / "checksums.sha256").write_bytes(f"{sha}  original.txt\n".encode("utf-8"))

    meta = {
        "slug": slug,
        "name_zh": entry["name_zh"],
        "name_en": entry.get("name_en", ""),
        "name_original": entry.get("name_original") or entry["name_zh"],
        "religion": entry.get("religion", "基督教"),
        "tradition": entry.get("tradition", "新約-希臘原文"),
        "language": entry.get("language", "Koine Greek"),
        "version": entry.get("version", "SBLGNT (Society of Biblical Literature, 2010)"),
        "version_date": entry.get("version_date", "1st century AD (composed) / 2010 (critical edition)"),
        "source_platform": "morphgnt/sblgnt (GitHub)",
        "source_url": f"{SBLGNT_RAW}/{filename}",
        "downloaded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "size_bytes": len(original_bytes),
        "checksum_sha256": sha,
        "chapter_count": len(chapters),
        "expected_chapter_count": entry.get("expected_chapter_count"),
        "expected_size_min": entry.get("expected_size_min"),
        "expected_size_max": entry.get("expected_size_max"),
        "license": "CC BY 4.0 (SBLGNT) / MIT (morphgnt analysis)",
        "verified": False,
        "tier": entry.get("tier"),
        "is_original_language": True,
        "notes": entry.get("notes"),
    }
    (TRANSLATIONS_DIR / slug / "meta.json").write_bytes(
        (json.dumps(meta, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    )
    print(f"[ok] {slug}: {len(chapters)} chapters, {meta['size_bytes']} bytes")
    return {"slug": slug, "status": "ok", "meta": meta}


def load_catalog(religion: str) -> list[dict]:
    name_map = {"基督教-希臘新約": "christianity-sblgnt.json"}
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
    for cat_file in CATALOG_DIR.glob("christianity-sblgnt*.json"):
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
            sys.exit(f"slug not in catalog: {args.slug}")
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
