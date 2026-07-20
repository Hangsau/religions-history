#!/usr/bin/env python
"""Canonical translation priority manifest and validation helpers."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT / "00-overview" / "translation-priority.json"
TRANSLATIONS_DIR = ROOT / "translations"
RANK = {"P0": 0, "P1": 1, "P2": 2}
DEFAULTS = {"核心": "P1", "次要": "P2", "總集": "P2"}
SLUG_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def load_manifest(path: Path = MANIFEST_PATH) -> dict:
    if not path.exists():
        return {"schema_version": 1, "defaults": DEFAULTS, "entries": []}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise ValueError("translation priority manifest requires schema_version=1")
    if not isinstance(payload.get("entries"), list):
        raise ValueError("translation priority manifest entries must be a list")
    return payload


def priority_map(path: Path = MANIFEST_PATH) -> dict[str, str]:
    result = {}
    for entry in load_manifest(path)["entries"]:
        if not isinstance(entry, dict):
            raise ValueError("priority entry must be an object")
        slug, priority = entry.get("slug"), entry.get("priority")
        if not isinstance(slug, str) or not SLUG_RE.fullmatch(slug):
            raise ValueError(f"invalid priority slug: {slug!r}")
        if priority not in RANK:
            raise ValueError(f"invalid priority for {slug}: {priority!r}")
        if slug in result:
            raise ValueError(f"duplicate priority slug: {slug}")
        result[slug] = priority
    return result


def priority_for(slug: str, tier: str, mapping: dict[str, str] | None = None) -> str:
    mapping = mapping if mapping is not None else priority_map()
    return mapping.get(slug, DEFAULTS.get(tier, "P2"))


def audit(path: Path = MANIFEST_PATH, translations_dir: Path = TRANSLATIONS_DIR) -> list[str]:
    errors = []
    try:
        manifest = load_manifest(path)
        mapping = priority_map(path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [str(exc)]
    entry_by_slug = {entry["slug"]: entry for entry in manifest["entries"]}
    religions = set()
    for slug, priority in mapping.items():
        meta_path = translations_dir / slug / "meta.json"
        if not meta_path.exists():
            errors.append(f"missing priority slug: {slug}")
            continue
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"bad meta for {slug}: {exc}")
            continue
        if meta.get("alias_of"):
            errors.append(f"priority slug is alias: {slug} -> {meta['alias_of']}")
        if priority == "P0":
            religion = meta.get("religion")
            if religion:
                religions.add(religion)
            if not str(entry_by_slug[slug].get("reason", "")).strip():
                errors.append(f"P0 missing reason: {slug}")
            original = translations_dir / slug / "raw" / "original.txt"
            if not original.exists() or original.stat().st_size < 100:
                errors.append(f"P0 missing/thin source: {slug}")
    declared = set(manifest.get("required_religions", []))
    for religion in sorted(declared - religions):
        errors.append(f"required religion lacks P0: {religion}")
    return errors


if __name__ == "__main__":
    problems = audit()
    if problems:
        for problem in problems:
            print(f"FAIL {problem}")
        raise SystemExit(1)
    mapping = priority_map()
    print(f"PASS translation priority manifest: {sum(v == 'P0' for v in mapping.values())} P0 entries")
