#!/usr/bin/env python
"""
Download entire CBETA volumes (大正藏 + 卍續藏) directly from cbeta-org/xml-p5 GitHub.
Each work becomes one translations/cbeta-T<vol>n<work>/ entry.

Uses the same TEI parsing as download-cbeta.py, just iterates entire volume directories
via GitHub Contents API.

Usage:
    python scripts/download-cbeta-full.py --volume T01           # one volume
    python scripts/download-cbeta-full.py --canon T --all        # all T volumes
    python scripts/download-cbeta-full.py --canon X --all        # all X (卍續藏)

Catalog auto-generated from GitHub Contents API; no manual catalog needed.
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

# Reuse TEI parser from download-cbeta.py
sys.path.insert(0, str(Path(__file__).resolve().parent))
from importlib.util import spec_from_file_location, module_from_spec
_spec = spec_from_file_location("dl_cbeta", str(Path(__file__).resolve().parent / "download-cbeta.py"))
_dl_cbeta = module_from_spec(_spec)
_spec.loader.exec_module(_dl_cbeta)
tei_to_text = _dl_cbeta.tei_to_text
fetch_xml = _dl_cbeta.fetch_xml

ROOT = Path(__file__).resolve().parent.parent
TRANSLATIONS_DIR = ROOT / "translations"

GH_API = "https://api.github.com/repos/cbeta-org/xml-p5/contents"
CBETA_RAW = "https://raw.githubusercontent.com/cbeta-org/xml-p5/master"
USER_AGENT = "religions-history-research/0.1 (academic research; contact: psyhangsau@gmail.com; +https://github.com/Hangsau/religions-history)"
SLEEP_BETWEEN_FILES = 0.3

_polite_req_count = 0
_LONG_PAUSE_EVERY = 100
_LONG_PAUSE_SECONDS = 30.0


def _polite_sleep_inline(base: float) -> None:
    """Sleep base + random jitter; every 100 requests take 30s break."""
    global _polite_req_count
    _polite_req_count += 1
    time.sleep(base + random.uniform(0, 0.5))
    if _polite_req_count > 0 and _polite_req_count % _LONG_PAUSE_EVERY == 0:
        print(f"  [polite-pause] {_LONG_PAUSE_SECONDS:.0f}s break after {_polite_req_count} requests")
        time.sleep(_LONG_PAUSE_SECONDS)

# Volumes/canon descriptions for meta
CANON_NAMES = {
    "T": "大正新脩大藏經 (Taishō Tripiṭaka)",
    "X": "卍新纂大日本續藏經 (Manji Zokuzōkyō)",
    "K": "高麗大藏經",
    "J": "嘉興大藏經",
    "F": "房山石經",
    "A": "趙城金藏",
    "P": "永樂北藏",
    "L": "乾隆藏",
    "B": "大藏經補編",
    "C": "中華大藏經",
    "U": "洪武南藏",
    "Y": "印順法師全集",
    "ZW": "藏外佛教文獻",
    "GA": "國家圖書館善本佛典",
}


def list_volume_files(canon: str, volume: str) -> list[str]:
    """List all XML filenames in a volume directory via GitHub Contents API."""
    url = f"{GH_API}/{canon}/{volume}"
    headers = {"User-Agent": USER_AGENT, "Accept": "application/vnd.github.v3+json"}
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    items = r.json()
    return [it["name"] for it in items if it["name"].endswith(".xml")]


def list_canon_volumes(canon: str) -> list[str]:
    """List all volume subdirectories under a canon root."""
    url = f"{GH_API}/{canon}"
    headers = {"User-Agent": USER_AGENT, "Accept": "application/vnd.github.v3+json"}
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    items = r.json()
    return sorted([it["name"] for it in items if it["type"] == "dir" and it["name"].startswith(canon)])


def download_work(canon: str, volume: str, xml_filename: str) -> dict:
    """Download one work XML, parse, write to translations/cbeta-<vol>n<workid>/.

    Filename like T01n0001.xml → slug cbeta-T01n0001
    """
    m = re.match(r"(T|X|K|J|F|A|P|L|B|C|U|Y|ZW|GA)(\d+)n(\w+)\.xml", xml_filename)
    if not m:
        return {"file": xml_filename, "status": "bad_filename"}
    work_canon, vol_num, work_id = m.groups()
    slug = f"cbeta-{work_canon}{vol_num}n{work_id}"

    meta_path = TRANSLATIONS_DIR / slug / "meta.json"
    out_dir = TRANSLATIONS_DIR / slug / "raw"
    if meta_path.exists():
        try:
            existing = json.loads(meta_path.read_text(encoding="utf-8"))
            if existing.get("verified") and (out_dir / "original.txt").exists():
                return {"file": xml_filename, "status": "already_verified", "slug": slug}
        except (json.JSONDecodeError, OSError):
            pass

    cbeta_path = f"{canon}/{volume}/{xml_filename}"
    try:
        xml = fetch_xml(cbeta_path)
    except Exception as e:
        return {"file": xml_filename, "status": "fetch_error", "reason": str(e)}

    try:
        chapters, xml_meta = tei_to_text(xml)
    except Exception as e:
        return {"file": xml_filename, "status": "parse_error", "reason": str(e)}

    if not chapters:
        return {"file": xml_filename, "status": "empty"}

    out_dir.mkdir(parents=True, exist_ok=True)
    lines = []
    for i, (label, text) in enumerate(chapters, 1):
        lines.append(f"=== {i} | 卷{label} ===")
        lines.append(text)
        lines.append("")
    original_text = "\n".join(lines).rstrip() + "\n"
    original_bytes = original_text.encode("utf-8")

    (out_dir / "original.txt").write_bytes(original_bytes)
    (out_dir / "source-urls.txt").write_bytes((f"{CBETA_RAW}/{cbeta_path}\n").encode("utf-8"))
    sha = hashlib.sha256(original_bytes).hexdigest()
    (out_dir / "checksums.sha256").write_bytes(f"{sha}  original.txt\n".encode("utf-8"))

    meta = {
        "slug": slug,
        "name_zh": xml_meta.get("title_zh", f"CBETA {work_canon}{vol_num}n{work_id}"),
        "name_en": xml_meta.get("title_en", ""),
        "name_original": xml_meta.get("title_zh", ""),
        "religion": "佛教",
        "tradition": "漢傳",
        "language": "古典漢語",
        "version": xml_meta.get("author", "CBETA TEI"),
        "version_date": "—",
        "source_platform": f"CBETA TEI P5 XML (GitHub): {CANON_NAMES.get(work_canon, work_canon)}",
        "source_url": f"{CBETA_RAW}/{cbeta_path}",
        "downloaded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "size_bytes": len(original_bytes),
        "checksum_sha256": sha,
        "chapter_count": len(chapters),
        "expected_chapter_count": None,
        "license": "CC BY-NC-SA 4.0 (CBETA)",
        "verified": False,
        "tier": "總集逐部",
        "is_original_language": work_canon in ("T", "X", "K", "J", "F", "A", "P", "L", "B", "C"),
        "notes": f"From CBETA xml-p5 / canon {work_canon} / volume {volume}",
    }
    (TRANSLATIONS_DIR / slug / "meta.json").write_bytes(
        (json.dumps(meta, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    )
    return {"file": xml_filename, "status": "ok", "slug": slug, "chapters": len(chapters), "size": len(original_bytes)}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--canon", default="T", help="canon root (T/X/K/J/B/etc.)")
    p.add_argument("--volume", help="single volume like T08")
    p.add_argument("--from-volume", help="start at this volume (T01 etc.)")
    p.add_argument("--to-volume", help="stop after this volume")
    p.add_argument("--all", action="store_true")
    args = p.parse_args()

    if args.volume:
        volumes = [args.volume]
    else:
        volumes = list_canon_volumes(args.canon)
        if args.from_volume:
            volumes = [v for v in volumes if v >= args.from_volume]
        if args.to_volume:
            volumes = [v for v in volumes if v <= args.to_volume]

    if not volumes:
        sys.exit("no volumes selected")

    print(f"[canon] {args.canon}  [volumes] {len(volumes)}: {volumes[:5]}...{volumes[-3:] if len(volumes) > 5 else ''}")

    total_summary = {}
    for vol in volumes:
        print(f"\n[volume] {vol}")
        try:
            files = list_volume_files(args.canon, vol)
        except Exception as e:
            print(f"  [list-error] {e}")
            total_summary["list_error"] = total_summary.get("list_error", 0) + 1
            continue
        print(f"  [files] {len(files)}")
        for filename in files:
            _polite_sleep_inline(SLEEP_BETWEEN_FILES)
            r = download_work(args.canon, vol, filename)
            status = r["status"]
            total_summary[status] = total_summary.get(status, 0) + 1
            if status == "ok":
                print(f"  [ok] {r['slug']}: {r['chapters']} juans, {r['size']} bytes")
            elif status not in ("already_verified",):
                print(f"  [{status}] {filename}: {r.get('reason', '')}")

    print(f"\n[summary] {json.dumps(total_summary, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
