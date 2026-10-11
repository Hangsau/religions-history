"""Apply source-bound tag review records to content-rejected tag checkpoints.

Generalises the one-off chunk-525 repair (tmp/tag-resume-20261007/review-525.py):
each `translations/<slug>/reviews/tag-chunk-NNNN.json` with status
`reviewed_not_applied` replaces exactly one blocked checkpoint chunk, only when the
source and chunk hashes still match. A slug whose blocked chunks are all repaired is
unblocked so the normal tag_one completeness checks finish it.

    PYTHONIOENCODING=utf-8 python scripts/apply_tag_reviews.py            # dry check
    PYTHONIOENCODING=utf-8 python scripts/apply_tag_reviews.py --apply
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import pipeline_failures  # noqa: E402
import pipeline_lock  # noqa: E402
import translate as tr  # noqa: E402

REQUIRED = ("slug", "chunk_index", "source_sha256", "input_sha256", "payload", "reviewer")


def check(path: Path, semantic: set[str], psych: set[str]) -> tuple[dict, Path, dict]:
    record = json.loads(path.read_text(encoding="utf-8"))
    missing = [k for k in REQUIRED if k not in record]
    assert not missing, f"{path}: missing {missing}"
    slug, index = record["slug"], record["chunk_index"]
    assert path.parent.parent.name == slug, f"{path}: slug mismatch"
    active = tr.CHECKPOINT_ROOT / slug / "tag" / "active"
    manifest = json.loads((active / "manifest.json").read_text(encoding="utf-8"))
    chunk = manifest["chunks"][index - 1]
    assert chunk["index"] == index
    assert manifest["source_sha256"] == record["source_sha256"], f"{slug}: source changed"
    assert chunk["input_sha256"] == record["input_sha256"], f"{slug}#{index}: chunk changed"
    assert chunk["status"] == "blocked", f"{slug}#{index}: status {chunk['status']}"
    payload = record["payload"]
    assert tr.valid_tag_payload(payload), f"{slug}#{index}: invalid payload"
    assert payload["semantic_tags"] and set(payload["semantic_tags"]) <= semantic, \
        f"{slug}#{index}: semantic tags {payload['semantic_tags']}"
    assert payload["psych_tags"] and set(payload["psych_tags"]) <= psych, \
        f"{slug}#{index}: psych tags {payload['psych_tags']}"
    return record, active, manifest


def apply_one(path: Path, record: dict, active: Path, manifest: dict) -> None:
    index = record["chunk_index"]
    chunk = manifest["chunks"][index - 1]
    part = active / chunk["output_file"]
    assert not part.exists(), f"{part}: refuse to overwrite"
    provenance = {"review_id": record.get("review_id"), "reviewer": record["reviewer"],
                  "reviewer_type": record.get("reviewer_type", "AI_assistant"),
                  "review_path": path.relative_to(ROOT).as_posix(),
                  "not_minimax_generation": True}
    chunk["review"] = provenance
    chunk["prior_rejection"] = record.get("prior_rejection") or {
        k: chunk.get(k) for k in ("status", "error_code", "last_error", "blocked_at")}
    for key in ("error_code", "last_error", "blocked_at"):
        chunk.pop(key, None)
    tr._save_checkpoint_part(active, manifest, index, json.dumps(
        {**record["payload"], "_provenance": provenance}, ensure_ascii=False, sort_keys=True))
    record.update(status="applied_to_checkpoint", applied_at=datetime.now(tr.TZ).isoformat(),
                  output_sha256=chunk["output_sha256"])
    tr._atomic_write_text(path, json.dumps(record, ensure_ascii=False, indent=2) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write checkpoints (default: check only)")
    args = ap.parse_args()
    semantic, psych = tr.load_tag_whitelist(), tr.load_psych_tag_whitelist()
    pending = [p for p in sorted(tr.TRANSLATIONS_DIR.glob("*/reviews/tag-chunk-*.json"))
               if json.loads(p.read_text(encoding="utf-8")).get("status") == "reviewed_not_applied"]
    checked = [(p, *check(p, semantic, psych)) for p in pending]
    print(f"[check] {len(checked)} pending review(s) valid")
    if not args.apply:
        return 0
    if not pipeline_lock.acquire_run_lock():
        return 1
    try:
        slugs = set()
        for path, record, active, _ in checked:
            # Re-read: an earlier review of the same slug rewrote this manifest.
            manifest = json.loads((active / "manifest.json").read_text(encoding="utf-8"))
            apply_one(path, record, active, manifest)
            slugs.add(record["slug"])
            print(f"[applied] {record['slug']}#{record['chunk_index']}")
        for slug in sorted(slugs):
            manifest = json.loads((tr.CHECKPOINT_ROOT / slug / "tag" / "active" / "manifest.json")
                                  .read_text(encoding="utf-8"))
            if any(c["status"] == "blocked" for c in manifest["chunks"]):
                print(f"[still-blocked] {slug}: other chunks need review")
                continue
            pipeline_failures.unblock(slug, tr.TRANSLATIONS_DIR)
            print(f"[unblock] {slug}")
    finally:
        pipeline_lock.release_run_lock()
    return 0


if __name__ == "__main__":
    sys.exit(main())
