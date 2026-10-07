"""Persistent, source-bound tag-only work selected independently of translation."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT / '00-overview' / 'tagging-queue.json'
QUEUE_NAME = '標籤補齊'
SLUG_RE = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._-]*$')
SHA_RE = re.compile(r'^[a-f0-9]{64}$')
SOURCE_FILES = {'raw/original.txt', '01-translation.md'}


def load(path: Path | None = None) -> dict:
    path = path or MANIFEST_PATH
    if not path.exists():
        return {'schema_version': 1, 'enabled': False, 'entries': []}
    data = json.loads(path.read_text(encoding='utf-8'))
    if (not isinstance(data, dict) or data.get('schema_version') != 1
            or not isinstance(data.get('enabled'), bool)
            or not isinstance(data.get('entries'), list)):
        raise ValueError('invalid tagging queue schema')
    seen = set()
    for entry in data['entries']:
        if not isinstance(entry, dict):
            raise ValueError('tagging entry must be an object')
        slug = entry.get('slug')
        if not isinstance(slug, str) or not SLUG_RE.fullmatch(slug) or slug in seen:
            raise ValueError('unsafe or duplicate tagging slug')
        if entry.get('source_file') not in SOURCE_FILES:
            raise ValueError(f'invalid tagging source for {slug}')
        digest = entry.get('source_sha256')
        if not isinstance(digest, str) or not SHA_RE.fullmatch(digest):
            raise ValueError(f'invalid tagging source checksum for {slug}')
        seen.add(slug)
    return data


def effective_tier(fallback: str = '核心') -> str:
    return QUEUE_NAME if load()['enabled'] else fallback


def worker_args(fallback: str = '核心') -> list[str]:
    if load()['enabled']:
        return ['--tag-queue']
    if fallback == QUEUE_NAME:
        raise ValueError('tagging queue was disabled; refuse to switch to translation')
    return ['--tier', fallback]


def select_source(base: Path, meta: dict) -> tuple[Path | None, str | None]:
    # Import lazily: translate imports this module only for its resume command.
    import translate
    if meta.get('alias_of'):
        return None, 'alias'
    if meta.get('text_role') == 'transliteration':
        return None, 'transliteration_requires_review'
    tr = base / '01-translation.md'
    if tr.exists():
        if not translate.has_complete_translation(tr):
            return None, 'incomplete_translation'
        source = tr
    else:
        language = meta.get('source_language') or meta.get('language')
        if language not in (*translate._CHINESE_LANGS, '漢文', 'Chinese'):
            return None, 'no_chinese_source'
        if meta.get('verified') is not True:
            return None, 'source_not_verified'
        source = base / 'raw/original.txt'
    try:
        raw = source.read_bytes()
        text = raw.decode('utf-8')
    except (OSError, UnicodeError):
        return None, 'source_unreadable'
    if source != tr and hashlib.sha256(raw).hexdigest() != meta.get('checksum_sha256'):
        return None, 'source_checksum_mismatch'
    body = '\n'.join(line for line in text.splitlines() if not line.startswith('=== '))
    if len(''.join(body.split())) < 100:
        return None, 'short_body_requires_review'
    if '\ufffd' in text or '<!-- CHUNK ' in text or translate.find_contamination(text):
        return None, 'source_needs_repair'
    return source, None


def validate_source(entry: dict, translations_dir: Path) -> str | None:
    base = translations_dir / entry['slug']
    try:
        meta = json.loads((base / 'meta.json').read_text(encoding='utf-8'))
        source, reason = select_source(base, meta)
        if reason:
            return reason
        if source.relative_to(base).as_posix() != entry['source_file']:
            return 'tagging_source_changed'
        if hashlib.sha256(source.read_bytes()).hexdigest() != entry['source_sha256']:
            return 'tagging_source_changed'
    except (OSError, ValueError):
        return 'source_unreadable'
    return None
