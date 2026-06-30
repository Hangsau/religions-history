#!/usr/bin/env python
"""
Download a scripture from zh.wikisource.org and save to translations/<slug>/raw/.

Wikisource has nearly all Chinese classical texts (儒道佛經史子集), no auth, no
hard rate limit. Pages are organized hierarchically: a title like 周易參同契
may be either:
  - leaf (whole text on one page); or
  - root with subpages like 周易參同契/卷上, 周易參同契/01章, etc.

Strategy:
  1. prefixsearch with "<title>/" prefix to discover subpages
  2. If subpages exist (>0 non-meta): root is TOC → fetch each subpage
  3. If no subpages: fetch the title page directly as the whole text
  4. Strip MediaWiki nav/infobox/footnote chrome, extract Chinese text

Usage:
    python scripts/download-wikisource.py --slug zhouyi-cantong-qi
    python scripts/download-wikisource.py --religion 道教 --all
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
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
CATALOG_DIR = ROOT / "scripts" / "catalog"
TRANSLATIONS_DIR = ROOT / "translations"

WS_API_DEFAULT = "https://zh.wikisource.org/w/api.php"
WS_API_LANG = {
    "zh": "https://zh.wikisource.org/w/api.php",
    "ja": "https://ja.wikisource.org/w/api.php",
    "en": "https://en.wikisource.org/w/api.php",
    "la": "https://la.wikisource.org/w/api.php",
    "sa": "https://sa.wikisource.org/w/api.php",
}
WS_API = WS_API_DEFAULT  # mutated via --lang in main()
USER_AGENT = "religions-history-research/0.1 (https://github.com/Hangsau/religions-history; academic use)"
REQ_TIMEOUT = 30
SLEEP_BETWEEN_REQUESTS = 0.5
MAX_RETRIES = 5
BACKOFF_INITIAL = 10.0

# Subpages whose titles end with these are meta/navigation, not text content
META_SUBPAGE_SUFFIXES = ("/全覽", "/目錄", "/編", "/編者按", "/校勘記")


def api_get(params: dict) -> dict:
    headers = {"User-Agent": USER_AGENT}
    backoff = BACKOFF_INITIAL
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.get(WS_API, params={**params, "format": "json", "formatversion": 2},
                             headers=headers, timeout=REQ_TIMEOUT)
            if r.status_code in (429, 503):
                print(f"  [rate-limit {r.status_code}] sleep {backoff:.0f}s")
                time.sleep(backoff)
                backoff *= 2
                continue
            r.raise_for_status()
            if not r.text.strip():
                raise ValueError("empty response")
            return r.json()
        except (requests.RequestException, ValueError) as e:
            print(f"  [req-error attempt {attempt}/{MAX_RETRIES}] sleep {backoff:.0f}s: {e}")
            time.sleep(backoff)
            backoff *= 2
    raise RuntimeError(f"max retries exceeded for {params}")


def discover_subpages(title: str) -> list[str]:
    """Return all true subpages of title (title/...) excluding meta pages.

    Uses allpages API (strict prefix) rather than prefixsearch (which is fuzzy
    and returns sibling/related pages like '周易/同人' for '周易參同契/').
    """
    prefix = title + "/"
    subs: list[str] = []
    continue_param: dict = {}
    while True:
        params = {
            "action": "query",
            "list": "allpages",
            "apprefix": prefix,
            "aplimit": 500,
            "apnamespace": 0,
        }
        params.update(continue_param)
        data = api_get(params)
        for p in data.get("query", {}).get("allpages", []):
            t = p["title"]
            if not t.startswith(prefix):
                continue
            if any(t.endswith(suf) for suf in META_SUBPAGE_SUFFIXES):
                continue
            subs.append(t)
        if "continue" in data:
            continue_param = data["continue"]
        else:
            break
    return sorted(subs, key=natural_sort_key)


def natural_sort_key(s: str) -> tuple:
    """Sort so that 01章, 02章, ... come in numeric order before 10章."""
    parts = re.split(r"(\d+)", s)
    return tuple((int(p) if p.isdigit() else p) for p in parts)


def get_page_text(title: str) -> str:
    """Fetch the page rendered HTML and extract Chinese plain text."""
    data = api_get({
        "action": "parse",
        "page": title,
        "prop": "text",
        "redirects": 1,
    })
    if "error" in data:
        raise RuntimeError(f"parse({title}): {data['error']}")
    html = data.get("parse", {}).get("text", "")
    if not html:
        return ""
    return extract_main_text(html)


def extract_main_text(html: str) -> str:
    """Extract main body Chinese text from Wikisource parsed HTML."""
    soup = BeautifulSoup(html, "html.parser")
    # Remove non-text chrome aggressively
    for sel in [
        "table.metadata", "div.noprint", "table.noprint",
        "div.mw-references-wrap", "ol.references",
        "div.thumb", "div.sister-projects",
        "div.toc", "span.mw-editsection",
        "div.printfooter", "table.toccolours",
        "div.navbox", "table.navbox", "div.catlinks",
        "div.dablink", "div.hatnote",
        "table.wikisource-template", "table[role='presentation']",
        "table.infobox", "table.header_notes",
        "div.header_notes", "table.headertemplate",
        "div.PD-icon", "p.PD-icon", "table.PD-icon",
        # Wikisource-specific elements
        ".header_notes", ".sister-box", ".sisterproject",
        ".tright", ".tleft", ".gallery",
    ]:
        for el in soup.select(sel):
            el.decompose()
    container = soup.select_one("div.mw-parser-output") or soup

    # Patterns that indicate this line is chrome, not content
    chrome_patterns = [
        re.compile(r"^姊妹計?畫?:"),
        re.compile(r"^姊妹计?划?:"),
        re.compile(r"参阅维基百科"),
        re.compile(r"參閱維基百科"),
        re.compile(r"此作品在全世界都"),  # 此作品在全世界都(属|於)于公有领域...
        re.compile(r"^本作品.*已(進|进)入公有(領|领)域"),
        re.compile(r"^数据项$|^資料項?$"),
        re.compile(r"^Wikidata"),
        re.compile(r"^数字图书馆"),
        re.compile(r"^(分类|分類)：?"),
        re.compile(r"^本作品.*已進入公有領域$"),
        re.compile(r"^本作品.*已进入公有领域$"),
        re.compile(r"^Public domain"),
        re.compile(r"^This work is in the public domain"),
    ]

    def is_chrome(text: str) -> bool:
        for p in chrome_patterns:
            if p.search(text):
                return True
        return False

    parts = []
    for el in container.find_all(["p", "dt", "dd", "li", "blockquote"], recursive=True):
        t = el.get_text(strip=True)
        if not t:
            continue
        # Drop only if there's no script content at all (whitespace / digits only)
        if not re.search(r"[^\s\d.,;:!?'\"()-]", t):
            continue
        if is_chrome(t):
            continue
        parts.append(t)
    if not parts:
        t = container.get_text("\n", strip=True)
        parts = [
            line for line in t.split("\n")
            if line.strip() and len(line.strip()) > 2 and not is_chrome(line)
        ]
    return "\n".join(parts)


def download_scripture(entry: dict) -> dict:
    slug = entry["slug"]
    if entry.get("skip_reason"):
        print(f"[skip] {slug}: {entry['skip_reason']}")
        return {"slug": slug, "status": "skipped", "reason": entry["skip_reason"]}
    if entry.get("defer_reason"):
        print(f"[defer] {slug}: {entry['defer_reason']}")
        return {"slug": slug, "status": "deferred", "reason": entry["defer_reason"]}

    title = entry.get("wikisource_title") or entry.get("name_zh")
    if not title:
        return {"slug": slug, "status": "error", "reason": "no wikisource_title or name_zh"}

    # Skip-if-verified
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

    fetched_titles: list[str] = []
    chapters: list[tuple[str, str]] = []

    try:
        if entry.get("wikisource_subpages_explicit"):
            subs = entry["wikisource_subpages_explicit"]
        else:
            subs = discover_subpages(title)

        if subs:
            print(f"  [multi] {len(subs)} subpages")
            for sub in subs:
                print(f"  [parse] {sub}")
                fetched_titles.append(sub)
                time.sleep(SLEEP_BETWEEN_REQUESTS)
                text = get_page_text(sub)
                if not text.strip():
                    print(f"    (empty)")
                    continue
                label = sub.split("/", 1)[1] if "/" in sub else sub
                chapters.append((label, text))
        else:
            print(f"  [parse] {title}")
            fetched_titles.append(title)
            text = get_page_text(title)
            if not text.strip():
                return {"slug": slug, "status": "empty", "reason": f"{title} has no extractable text"}
            chapters.append((title, text))
    except RuntimeError as e:
        return {"slug": slug, "status": "error", "reason": str(e)}
    except requests.RequestException as e:
        return {"slug": slug, "status": "fetch_error", "reason": str(e)}

    if not chapters:
        return {"slug": slug, "status": "empty", "reason": "no non-empty chapters"}

    out_dir.mkdir(parents=True, exist_ok=True)

    lines = []
    for i, (label, text) in enumerate(chapters, 1):
        lines.append(f"=== {i} | {label} ===")
        lines.append(text)
        lines.append("")
    original_text = "\n".join(lines).rstrip() + "\n"
    original_bytes = original_text.encode("utf-8")

    (out_dir / "original.txt").write_bytes(original_bytes)
    ws_host = WS_API.replace("/w/api.php", "")
    page_urls = [f"{ws_host}/wiki/{t.replace(' ', '_')}" for t in fetched_titles]
    (out_dir / "source-urls.txt").write_bytes(("\n".join(page_urls) + "\n").encode("utf-8"))
    sha = hashlib.sha256(original_bytes).hexdigest()
    (out_dir / "checksums.sha256").write_bytes(f"{sha}  original.txt\n".encode("utf-8"))

    meta = {
        "slug": slug,
        "name_zh": entry["name_zh"],
        "name_en": entry.get("name_en", ""),
        "name_original": entry["name_zh"],
        "religion": entry.get("religion", "道教"),
        "language": entry.get("language", "古典漢語"),
        "version": entry.get("version", "Wikisource 通行本"),
        "version_date": entry.get("version_date", "—"),
        "source_platform": WS_API.split("//")[1].split("/")[0],
        "source_url": f"{ws_host}/wiki/{title.replace(' ', '_')}",
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
    (TRANSLATIONS_DIR / slug / "meta.json").write_bytes(
        (json.dumps(meta, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    )
    print(f"[ok] {slug}: {len(chapters)} chapters, {meta['size_bytes']} bytes")
    return {"slug": slug, "status": "ok", "meta": meta}


def load_catalog(religion: str) -> list[dict]:
    name_map = {
        "道教": "daoism-ws.json",
        "儒教": "confucianism-ws.json",
        "基督教": "christianity-ws.json",
        "基督教-拉丁": "christianity-vulgate.json",
        "神道": "shinto-ws.json",
        "世界古典": "world-classics-en-ws.json",
    }
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
    for cat_file in CATALOG_DIR.glob("*-ws.json"):
        data = json.loads(cat_file.read_text(encoding="utf-8"))
        for e in data["scriptures"]:
            if e["slug"] == slug:
                e.setdefault("religion", data["religion"])
                e.setdefault("language", data.get("language"))
                return e
    return None


def main():
    global WS_API
    p = argparse.ArgumentParser()
    p.add_argument("--slug")
    p.add_argument("--religion")
    p.add_argument("--all", action="store_true")
    p.add_argument("--lang", default="zh", choices=list(WS_API_LANG.keys()))
    args = p.parse_args()
    WS_API = WS_API_LANG[args.lang]

    if args.slug and not args.religion:
        e = find_entry(args.slug)
        if not e:
            sys.exit(f"slug not in any -ws catalog: {args.slug}")
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
