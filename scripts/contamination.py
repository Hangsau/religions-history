"""
contamination.py — Shared patterns for detecting M3 session-tail contamination in chunk output.

Imported by translate.py (chunk guard) and verify.py (--contamination scan).

Pattern rationale
-----------------
M3 session stop-hooks append a report after the actual content. The patterns below are
anchored to that report's distinctive vocabulary and are chosen to minimise false positives
against normal scripture text (which contains terms like 「已」、「狀態」 but NOT
pipeline-internal compound phrases).

All patterns are applied line-by-line unless noted.
"""

import re
from typing import NamedTuple


class ContaminationMatch(NamedTuple):
    line_no: int    # 1-based
    line: str
    pattern_name: str


# ---------------------------------------------------------------------------
# Pattern catalogue
# ---------------------------------------------------------------------------

# Hard patterns — unambiguous pipeline vocabulary; any occurrence in scripture = contaminated.
_HARD_PATTERNS: list[tuple[str, str]] = [
    # git operation phrases
    ("已 commit",        r"已[\s]*commit"),                              # 「已 commit + push」
    ("commit + push",    r"commit\s*\+\s*push"),                        # canonical stop-hook phrase
    ("git push",         r"\bgit\s+push\b"),
    ("git add",          r"\bgit\s+add\b"),
    ("git pull",         r"\bgit\s+pull\b"),
    # pipeline internal file / component names
    ("PIPELINE_STATUS",  r"\bPIPELINE_STATUS\b"),
    ("HANDOFF.md",       r"\bHANDOFF\.md\b"),
    ("auto-pipeline",    r"\bauto-pipeline\b"),
    ("supervise-pipeline", r"\bsupervise-pipeline\b"),
    # commit hash only when on same line as commit/push keyword
    # (standalone 8-hex may appear in Talmudic / manuscript siglum notation)
    ("commit hash",      r"(?:commit|push).*\b[0-9a-f]{8}\b|\b[0-9a-f]{8}\b.*(?:commit|push)"),
    # pipeline-status structural markers
    ("core-manifest",    r"\bcore-manifest\b"),
    ("pipeline-checkpoints", r"\bpipeline-checkpoints\b"),
    ("track-progress",   r"\btrack-progress\b"),
    ("build-tag-index",  r"\bbuild-tag-index\b"),
    # explicit pipeline action phrases
    ("Pipeline B+C",     r"Pipeline\s+B\+C"),
    ("Pipeline A",       r"Pipeline\s+A\s+收集"),   # more specific to avoid match on "Pipeline A" in prose
    ("semantic_tags 已回填", r"semantic_tags\s+已回填"),
    ("verify PASS",      r"verify\s+PASS"),
    ("pipeline 此刻正處理", r"pipeline\s+此刻正處理"),
    ("iteration 收尾",   r"iteration\s+收尾"),
]

# Compile to single regex per pattern
_COMPILED_HARD: list[tuple[str, re.Pattern]] = [
    (name, re.compile(pat, re.IGNORECASE))
    for name, pat in _HARD_PATTERNS
]

# Soft patterns — phrases that CAN appear in religious commentary but are suspicious
# in context.  We log them as WARNING in contamination scan (not used as hard block in guard).
# Currently unused by the guard; included here for future --verbose mode.
_SOFT_PATTERNS: list[tuple[str, str]] = [
    ("本次會話",    r"本次會話"),
    ("任務完成",    r"任務完成"),
    ("以上就是",    r"以上就是"),
]

_COMPILED_SOFT: list[tuple[str, re.Pattern]] = [
    (name, re.compile(pat))
    for name, pat in _SOFT_PATTERNS
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def find_contamination(text: str) -> list[ContaminationMatch]:
    """Return all hard-pattern matches found in *text*, as a list of ContaminationMatch.

    Each match records the 1-based line number, the matched line, and the pattern name.
    An empty list means the text is clean.
    """
    matches: list[ContaminationMatch] = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for name, rx in _COMPILED_HARD:
            if rx.search(line):
                matches.append(ContaminationMatch(lineno, line, name))
                break  # one match per line is enough
    return matches


def is_contaminated(text: str) -> bool:
    """Quick boolean check — True if ANY hard pattern matches anywhere in *text*."""
    return bool(find_contamination(text))
