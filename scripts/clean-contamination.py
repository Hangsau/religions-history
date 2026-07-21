#!/usr/bin/env python3
"""
clean-contamination.py — Remove M3 session-tail contamination from 01-translation.md files.

Usage:
    python scripts/clean-contamination.py [--apply] [--report]
    --dry-run  (default) Print what would be removed without writing any files.
    --apply    Write cleaned files atomically (tmp + replace).
    --report   Print structured summary: CLEANED / SKIPPED / INCOMPLETE lists.

Contamination form
------------------
M3 session-tail blobs are always appended as *independent paragraphs* separated
from surrounding scripture by blank lines. They are never interleaved with
scripture lines mid-sentence.

Excision rule
-------------
When a contamination match is found on line L:
  1. Walk backward from L-1 to find the start of the surrounding "paragraph block"
     (a contiguous run of non-blank lines). Call it BLOCK_START.
  2. Walk forward from L+1 to find the end of the block. Call it BLOCK_END.
  3. Also absorb any trailing blank lines immediately after BLOCK_END
     (to avoid leaving double-blank gaps).
  4. SAFETY guards — if ANY line in the identified block matches a scripture-structure
     pattern, mark the block as SKIP (add to human-review list):
       - Section header:  ^=== \\d+ \\|
       - Markdown heading: ^#+\\s
     These structural lines must never be removed automatically.
  5. Multiple contamination matches within the same block are deduplicated (one
     excision covers all).

Only 01-translation.md files are touched; raw/, meta.json, 02-annotation.md
are never modified.
"""

import sys
import os
import re
import tempfile
import shutil
from pathlib import Path

# Locate project root relative to this script
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
TRANSLATIONS_DIR = PROJECT_ROOT / "translations"

# Add scripts/ to path so we can import contamination
sys.path.insert(0, str(SCRIPT_DIR))
from contamination import find_contamination

# ---------------------------------------------------------------------------
# Structure-line guards (never auto-remove lines matching these)
# ---------------------------------------------------------------------------
STRUCTURE_PATTERNS = [
    re.compile(r"^=== \d+"),        # section header  === N | label ===
    re.compile(r"^#+\s"),           # markdown heading
]

def is_structure_line(line: str) -> bool:
    s = line.strip()
    return any(p.match(s) for p in STRUCTURE_PATTERNS)


# ---------------------------------------------------------------------------
# Block detection helpers
# ---------------------------------------------------------------------------
def find_block(lines: list[str], match_lineno: int) -> tuple[int, int]:
    """Return (block_start, block_end) 0-based inclusive indices for the
    paragraph block containing 1-based match_lineno."""
    idx = match_lineno - 1  # convert to 0-based

    # Walk backward to block start
    start = idx
    while start > 0 and lines[start - 1].strip():
        start -= 1

    # Walk forward to block end
    end = idx
    while end < len(lines) - 1 and lines[end + 1].strip():
        end += 1

    return start, end


def find_excision_ranges(lines: list[str], contamination_matches) -> tuple[list[tuple[int,int]], list[dict]]:
    """Return (excision_ranges, skipped_blocks).

    excision_ranges: list of (start, end) 0-based inclusive line indices to remove,
                     including trailing blank lines after each block.
    skipped_blocks:  list of dicts with keys: lineno, line, pattern_name, reason.
    """
    # Group matches by block; use block_start as key
    block_matches: dict[int, list] = {}  # block_start -> list of matches
    skipped: list[dict] = []

    for m in contamination_matches:
        block_start, block_end = find_block(lines, m.line_no)

        # Check safety guards
        block_lines = lines[block_start:block_end + 1]
        structure_hit = next((l.rstrip() for l in block_lines if is_structure_line(l)), None)
        if structure_hit is not None:
            skipped.append({
                "lineno": m.line_no,
                "line": m.line.rstrip(),
                "pattern_name": m.pattern_name,
                "reason": f"block contains structure line: {structure_hit!r}",
                "block_start": block_start + 1,
                "block_end": block_end + 1,
            })
        else:
            if block_start not in block_matches:
                block_matches[block_start] = []
            block_matches[block_start].append((block_end, m))

    # Build excision ranges (block + trailing blank lines)
    excision_ranges: list[tuple[int,int]] = []
    for block_start, entries in block_matches.items():
        block_end = max(e[0] for e in entries)
        # absorb trailing blank lines
        trail_end = block_end
        while trail_end + 1 < len(lines) and not lines[trail_end + 1].strip():
            trail_end += 1
        excision_ranges.append((block_start, trail_end))

    # Merge overlapping/adjacent ranges
    excision_ranges.sort()
    merged: list[tuple[int,int]] = []
    for start, end in excision_ranges:
        if merged and start <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))

    return merged, skipped


def apply_excisions(lines: list[str], ranges: list[tuple[int,int]]) -> list[str]:
    """Return lines with the given 0-based inclusive ranges removed."""
    remove_set: set[int] = set()
    for start, end in ranges:
        remove_set.update(range(start, end + 1))
    return [l for i, l in enumerate(lines) if i not in remove_set]


# ---------------------------------------------------------------------------
# Completeness check
# ---------------------------------------------------------------------------
def check_completeness(slug: str, translation_file: Path) -> list[str]:
    """Return list of issues; empty = looks complete.

    Checks:
    1. Section headers (=== N | ...) are consecutive starting from 1.
    2. At least one content line exists (file is non-trivial).
    """
    issues = []
    text = translation_file.read_text(encoding="utf-8")
    lines = text.splitlines()

    if len(lines) < 5:
        issues.append(f"file suspiciously short ({len(lines)} lines)")
        return issues

    # Extract section numbers
    section_pattern = re.compile(r"^=== (\d+) \|")
    section_nums = []
    for line in lines:
        m = section_pattern.match(line.strip())
        if m:
            section_nums.append(int(m.group(1)))

    if not section_nums:
        # No section headers — may be a single-block text; not necessarily incomplete
        return issues

    section_nums.sort()
    expected = list(range(1, max(section_nums) + 1))
    missing = sorted(set(expected) - set(section_nums))
    if missing:
        issues.append(f"missing section numbers: {missing}")

    # Compare against raw/original.txt chapter count if available
    raw_path = translation_file.parent / "raw" / "original.txt"
    if raw_path.exists():
        raw_text = raw_path.read_text(encoding="utf-8", errors="replace")
        raw_sections = section_pattern.findall(raw_text)
        if raw_sections:
            raw_count = max(int(n) for n in raw_sections)
            if section_nums and max(section_nums) < raw_count * 0.8:
                issues.append(
                    f"translation has {max(section_nums)} sections but raw has {raw_count} "
                    f"(≥20% gap — likely truncated)"
                )

    return issues


# ---------------------------------------------------------------------------
# Main processing
# ---------------------------------------------------------------------------
def process_file(translation_file: Path, apply: bool, verbose: bool = True) -> dict:
    """Process one 01-translation.md file.

    Returns result dict with keys:
      slug, status (CLEANED/SKIPPED/CLEAN), ranges_removed, lines_removed,
      skipped_blocks, incompleteness_issues.
    """
    slug = translation_file.parent.name
    text = translation_file.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    # Detect contamination
    matches = find_contamination(text)
    if not matches:
        return {"slug": slug, "status": "CLEAN", "ranges_removed": [], "lines_removed": 0,
                "skipped_blocks": [], "incompleteness_issues": []}

    lines_no_end = [l.rstrip("\r\n") for l in lines]
    excision_ranges, skipped = find_excision_ranges(lines_no_end, matches)

    result = {
        "slug": slug,
        "status": "SKIPPED" if (skipped and not excision_ranges) else ("CLEANED" if excision_ranges else "CLEAN"),
        "ranges_removed": excision_ranges,
        "lines_removed": sum(end - start + 1 for start, end in excision_ranges),
        "skipped_blocks": skipped,
        "incompleteness_issues": [],
    }

    if verbose:
        if excision_ranges:
            print(f"\n[{'DRY-RUN' if not apply else 'APPLY'}] {slug}")
            for start, end in excision_ranges:
                preview_lines = lines_no_end[start:min(start+3, end+1)]
                preview = " | ".join(l[:80] for l in preview_lines)
                print(f"  lines {start+1}-{end+1} ({end-start+1} lines): {preview!r}")
        if skipped:
            for s in skipped:
                print(f"  SKIP line {s['lineno']} [{s['pattern_name']}]: {s['reason']}")

    if apply and excision_ranges:
        cleaned_lines = apply_excisions(lines_no_end, excision_ranges)
        cleaned_text = "\n".join(cleaned_lines)
        if cleaned_text and not cleaned_text.endswith("\n"):
            cleaned_text += "\n"

        # Atomic write
        tmp = translation_file.with_suffix(".tmp")
        tmp.write_text(cleaned_text, encoding="utf-8")
        shutil.move(str(tmp), str(translation_file))

        # Completeness check on cleaned file
        result["incompleteness_issues"] = check_completeness(slug, translation_file)

    return result


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Clean M3 contamination from 01-translation.md files")
    parser.add_argument("--apply", action="store_true", help="Write files (default: dry-run)")
    parser.add_argument("--report", action="store_true", help="Print structured summary at end")
    parser.add_argument("--slug", help="Process a single slug only")
    args = parser.parse_args()

    dry_run = not args.apply

    if dry_run:
        print("=== DRY-RUN MODE (use --apply to write files) ===\n")
    else:
        print("=== APPLY MODE — files will be modified ===\n")

    # Find files to process
    if args.slug:
        slug_dirs = [TRANSLATIONS_DIR / args.slug]
    else:
        slug_dirs = sorted(TRANSLATIONS_DIR.iterdir())

    results = []
    for slug_dir in slug_dirs:
        if not slug_dir.is_dir():
            continue
        tf = slug_dir / "01-translation.md"
        if not tf.exists():
            continue
        result = process_file(tf, apply=args.apply)
        results.append(result)

    # Summary
    cleaned = [r for r in results if r["status"] == "CLEANED"]
    skipped = [r for r in results if r["status"] == "SKIPPED" or r["skipped_blocks"]]
    incomplete = [r for r in results if r["incompleteness_issues"]]

    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Files scanned:  {len(results)}")
    print(f"Files cleaned:  {len(cleaned)}")
    total_lines = sum(r["lines_removed"] for r in cleaned)
    print(f"Lines removed:  {total_lines}")
    print(f"Files skipped (human review needed): {len([r for r in results if r['skipped_blocks']])}")
    print(f"Incomplete after clean: {len(incomplete)}")

    if args.report or True:
        if cleaned:
            print(f"\n--- CLEANED ({len(cleaned)}) ---")
            for r in cleaned:
                print(f"  {r['slug']:50s}  -{r['lines_removed']} lines")

        all_skipped_blocks = []
        for r in results:
            for s in r["skipped_blocks"]:
                all_skipped_blocks.append((r["slug"], s))
        if all_skipped_blocks:
            print(f"\n--- SKIPPED blocks (human review) ---")
            for slug, s in all_skipped_blocks:
                print(f"  {slug} line {s['lineno']} [{s['pattern_name']}]: {s['reason']}")

        if incomplete:
            print(f"\n--- INCOMPLETE (content possibly missing) ---")
            for r in incomplete:
                for issue in r["incompleteness_issues"]:
                    print(f"  {r['slug']}: {issue}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
