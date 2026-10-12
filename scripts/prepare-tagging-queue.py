"""Build a reviewable tag queue; disabled unless --enable records the user's authorization.

    python scripts/prepare-tagging-queue.py                       # round 1: Chinese sources only
    python scripts/prepare-tagging-queue.py --allow-original      # later rounds: also untranslated
                                                                  # non-Chinese originals
A finished queue (every entry tagged) is archived next to it before a new one is written.
"""
import argparse
import collections
import hashlib
import json
from datetime import datetime, timezone

import tagging_queue
import translate


def _tagged(meta: dict) -> bool:
    return bool(meta.get('tag_status') == 'done' and meta.get('semantic_tags')
                and meta.get('psych_tag_status') == 'done' and meta.get('psych_tags'))


def _archive_finished_queue() -> None:
    path = tagging_queue.MANIFEST_PATH
    old = tagging_queue.load()
    pending = [e['slug'] for e in old['entries'] if not _tagged(json.loads(
        (translate.TRANSLATIONS_DIR / e['slug'] / 'meta.json').read_text(encoding='utf-8')))]
    if pending:
        raise SystemExit(f'Queue still has {len(pending)} untagged entries; '
                         'review it instead of replacing active work.')
    stamp = (old.get('created_at') or '')[:10] or 'undated'
    archive = path.with_name(f'tagging-queue-{stamp}.json')
    if archive.exists():
        raise SystemExit(f'{archive.name} already exists')
    path.replace(archive)
    print(f'archived finished queue -> {archive.name}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--allow-original', action='store_true',
                    help='also queue untranslated non-Chinese originals (tagged from raw/original.txt)')
    ap.add_argument('--enable', metavar='AUTHORIZATION',
                    help="enable immediately, recording the user's instruction verbatim")
    args = ap.parse_args()
    if tagging_queue.MANIFEST_PATH.exists():
        _archive_finished_queue()
    entries, deferred = [], []
    for meta_path in sorted(translate.TRANSLATIONS_DIR.glob('*/meta.json')):
        meta = json.loads(meta_path.read_text(encoding='utf-8'))
        if meta.get('alias_of'):
            continue
        if _tagged(meta):
            continue
        base = meta_path.parent
        source, reason = tagging_queue.select_source(base, meta, args.allow_original)
        if reason:
            deferred.append({'slug': base.name, 'reason': reason})
            continue
        entry = {'slug': base.name, 'tier': meta.get('tier'),
                 'religion': meta.get('religion'),
                 'source_file': source.relative_to(base).as_posix(),
                 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                 'source_bytes': source.stat().st_size}
        language = meta.get('source_language') or meta.get('language')
        if args.allow_original and source.name == 'original.txt' and language not in (
                *translate._CHINESE_LANGS, '漢文', 'Chinese'):
            entry['source_policy'] = 'original'
        entries.append(entry)
    ranks = {'核心': 0, '次要': 1, '總集逐部': 2, 'Sefaria full crawl': 3}
    entries.sort(key=lambda e: (ranks.get(e['tier'], 3), e['source_bytes'], e['slug']))
    data = {'schema_version': 1, 'enabled': False,
            'created_at': datetime.now(timezone.utc).astimezone().isoformat(),
            'tasks': ['tag'], 'name': tagging_queue.QUEUE_NAME,
            'selection': ('Canonical untagged books with complete translation or verified '
                          + ('original-language source (any language)' if args.allow_original
                             else 'Chinese source')
                          + '; at least 100 non-whitespace body characters; no known '
                          'transliteration, corruption or partial translation.'),
            'review_boundary': 'Automated source checks establish readability/integrity, not semantic or translation quality. Short sources are deferred for review, not declared invalid.',
            'entries': entries, 'deferred': deferred,
            'deferred_counts': dict(collections.Counter(e['reason'] for e in deferred))}
    if args.enable:
        data.update(enabled=True, enabled_at=data['created_at'], authorization=args.enable)
    translate._atomic_write_text(tagging_queue.MANIFEST_PATH,
                                 json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    tagging_queue.load()
    print(json.dumps({'queued': len(entries),
                      'tiers': dict(collections.Counter(e['tier'] for e in entries)),
                      'deferred': data['deferred_counts'], 'enabled': data['enabled']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
