"""Build a disabled reviewable tag queue; never enables or starts generation."""
import collections
import hashlib
import json
from datetime import datetime, timezone

import tagging_queue
import translate


def main():
    if tagging_queue.MANIFEST_PATH.exists():
        raise SystemExit('Queue already exists; review it instead of replacing active work.')
    entries, deferred = [], []
    for meta_path in sorted(translate.TRANSLATIONS_DIR.glob('*/meta.json')):
        meta = json.loads(meta_path.read_text(encoding='utf-8'))
        if meta.get('alias_of'):
            continue
        if (meta.get('tag_status') == 'done' and meta.get('semantic_tags')
                and meta.get('psych_tag_status') == 'done' and meta.get('psych_tags')):
            continue
        base = meta_path.parent
        source, reason = tagging_queue.select_source(base, meta)
        if reason:
            deferred.append({'slug': base.name, 'reason': reason})
            continue
        entries.append({'slug': base.name, 'tier': meta.get('tier'),
                        'religion': meta.get('religion'),
                        'source_file': source.relative_to(base).as_posix(),
                        'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                        'source_bytes': source.stat().st_size})
    ranks = {'核心': 0, '次要': 1, '總集逐部': 2}
    entries.sort(key=lambda e: (ranks.get(e['tier'], 3), e['source_bytes'], e['slug']))
    data = {'schema_version': 1, 'enabled': False,
            'created_at': datetime.now(timezone.utc).astimezone().isoformat(),
            'tasks': ['tag'], 'name': tagging_queue.QUEUE_NAME,
            'selection': 'Canonical untagged books with complete translation or verified Chinese source; at least 100 non-whitespace body characters; no known transliteration, corruption or partial translation.',
            'review_boundary': 'Automated source checks establish readability/integrity, not semantic or translation quality. Short sources are deferred for review, not declared invalid.',
            'entries': entries, 'deferred': deferred,
            'deferred_counts': dict(collections.Counter(e['reason'] for e in deferred))}
    translate._atomic_write_text(tagging_queue.MANIFEST_PATH,
                                 json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    tagging_queue.load()
    print(json.dumps({'queued': len(entries),
                      'tiers': dict(collections.Counter(e['tier'] for e in entries)),
                      'deferred': data['deferred_counts'], 'enabled': False}, ensure_ascii=False))


if __name__ == '__main__':
    main()
