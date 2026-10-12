"""Queue books whose psych_tags were cut alphabetically for a psych re-tag.

Before 2026-10-12, tag_one kept `sorted(psych)[:5]`: on multi-chunk books the union of
chunk tags was cut by spelling, not agreement. Affected = tagged books whose tagging
source exceeds one call (MAX_CHARS_PER_CALL) and that hold exactly 5 psych tags and no
tag-passages.json (written only by the fixed code).

Each affected meta gets `psych_retag` (old psych_tags stay visible until replaced;
semantic_tags/keywords are preserved by tag_one). Entries are put at the FRONT of the
enabled tagging queue so corrections run before new coverage.

    python scripts/prepare-psych-retag.py            # report only
    python scripts/prepare-psych-retag.py --apply
"""
import argparse
import collections
import hashlib
import json
from datetime import datetime, timezone

import tagging_queue
import translate

REASON = "alphabetical-truncation-2026-10-12"


def affected():
    found, skipped = [], collections.Counter()
    for meta_path in sorted(translate.TRANSLATIONS_DIR.glob("*/meta.json")):
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        base = meta_path.parent
        if (meta.get("psych_tag_status") != "done" or len(meta.get("psych_tags") or []) < 5
                or meta.get("psych_retag") or (base / "tag-passages.json").exists()):
            continue
        source, reason = tagging_queue.select_source(base, meta, allow_original=True,
                                                     allow_replacement=True)
        if reason:
            skipped[reason] += 1
            continue
        if len(source.read_text(encoding="utf-8")) <= translate.MAX_CHARS_PER_CALL:
            continue
        found.append((base, meta, source))
    return found, skipped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    found, skipped = affected()
    print(json.dumps({"affected": len(found),
                      "tiers": dict(collections.Counter(m.get("tier") for _, m, _ in found)),
                      "unselectable": dict(skipped)}, ensure_ascii=False))
    if not args.apply:
        return
    manifest = tagging_queue.load()
    if not manifest["enabled"]:
        raise SystemExit("tagging queue is disabled; enable a queue before adding re-tags")
    queued = {e["slug"] for e in manifest["entries"]}
    now = datetime.now(timezone.utc).astimezone().isoformat()
    new_entries = []
    for base, meta, source in found:
        if base.name in queued:
            continue
        entry = {"slug": base.name, "tier": meta.get("tier"), "religion": meta.get("religion"),
                 "source_file": source.relative_to(base).as_posix(),
                 "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                 "source_bytes": source.stat().st_size, "retag": REASON}
        language = meta.get("source_language") or meta.get("language")
        if source.name == "original.txt" and language not in (
                *translate._CHINESE_LANGS, "漢文", "Chinese"):
            entry["source_policy"] = "original"
        if "�" in source.read_text(encoding="utf-8"):
            entry["allow_replacement"] = True
        new_entries.append(entry)
        meta["psych_retag"] = {"reason": REASON, "marked_at": now}
        translate._atomic_write_text(base / "meta.json",
                                     json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
    ranks = {"核心": 0, "次要": 1, "總集逐部": 2}
    new_entries.sort(key=lambda e: (ranks.get(e["tier"], 3), e["source_bytes"], e["slug"]))
    manifest["entries"] = new_entries + manifest["entries"]
    manifest["retag_added_at"] = now
    manifest["retag_count"] = manifest.get("retag_count", 0) + len(new_entries)
    translate._atomic_write_text(tagging_queue.MANIFEST_PATH,
                                 json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    tagging_queue.load()
    print(f"[retag] marked {len(new_entries)} books; queue now {len(manifest['entries'])} entries")


if __name__ == "__main__":
    main()
