import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import tagging_queue as queue
import translate


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


class TaggingQueueTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.translations = self.root / 'translations'
        self.base = self.translations / 'demo'
        (self.base / 'raw').mkdir(parents=True)
        self.raw = self.base / 'raw/original.txt'
        self.raw.write_text('=== 1 | 正文 ===\n' + '寬忍止息瞋恚。' * 40, encoding='utf-8')
        self.meta = {'slug': 'demo', 'tier': '次要', 'language': '古典漢語',
                     'verified': True, 'text_role': 'original',
                     'checksum_sha256': hashlib.sha256(self.raw.read_bytes()).hexdigest()}
        self.write_meta()
        self.entry = {'slug': 'demo', 'source_file': 'raw/original.txt',
                      'source_sha256': self.meta['checksum_sha256']}
        self.manifest = self.root / 'tagging-queue.json'
        self.data = {'schema_version': 1, 'enabled': True, 'entries': [self.entry]}
        self.write_manifest()
        patch = mock.patch.object(queue, 'MANIFEST_PATH', self.manifest)
        patch.start()
        self.addCleanup(patch.stop)

    def write_meta(self):
        (self.base / 'meta.json').write_text(json.dumps(self.meta), encoding='utf-8')

    def write_manifest(self):
        self.manifest.write_text(json.dumps(self.data), encoding='utf-8')

    def test_missing_disabled_and_empty_manifest(self):
        self.assertFalse(queue.load(self.root / 'missing')['enabled'])
        self.data.update(enabled=False, entries=[])
        self.write_manifest()
        self.assertEqual(queue.worker_args('次要'), ['--tier', '次要'])
        with self.assertRaises(ValueError):
            queue.worker_args(queue.QUEUE_NAME)
        self.data['enabled'] = True
        self.write_manifest()
        self.assertEqual(queue.load()['entries'], [])
        self.assertEqual(queue.worker_args('核心'), ['--tag-queue'])

    def test_rejects_invalid_schema_duplicates_traversal_and_hash(self):
        for data in [[], {'schema_version': 3}, {**self.data, 'enabled': 'yes'},
                     {**self.data, 'entries': [self.entry, self.entry]},
                     {**self.data, 'entries': [{**self.entry, 'slug': '../escape'}]},
                     {**self.data, 'entries': [{**self.entry, 'source_file': '../token'}]},
                     {**self.data, 'entries': [{**self.entry, 'source_sha256': 'bad'}]}]:
            with self.subTest(data=data):
                self.manifest.write_text(json.dumps(data), encoding='utf-8')
                with self.assertRaises(ValueError):
                    queue.load()

    def test_source_hash_and_language_are_rechecked(self):
        self.assertIsNone(queue.validate_source(self.entry, self.translations))
        self.raw.write_text('different source' * 100, encoding='utf-8')
        self.assertEqual(queue.validate_source(self.entry, self.translations), 'source_checksum_mismatch')
        self.meta['checksum_sha256'] = hashlib.sha256(self.raw.read_bytes()).hexdigest()
        self.write_meta()
        self.assertEqual(queue.validate_source(self.entry, self.translations), 'tagging_source_changed')
        self.meta['language'] = 'Hebrew'
        self.write_meta()
        self.assertEqual(queue.validate_source(self.entry, self.translations), 'no_chinese_source')

    def test_short_alias_transliteration_and_incomplete_sources_are_deferred(self):
        for fields, reason in [({'alias_of': 'canonical'}, 'alias'),
                               ({'text_role': 'transliteration'}, 'transliteration_requires_review'),
                               ({'verified': False}, 'source_not_verified')]:
            self.assertEqual(queue.select_source(self.base, {**self.meta, **fields})[1], reason)
        self.raw.write_text('=== 1 | 很長的書名 ===\n短文', encoding='utf-8')
        self.meta['checksum_sha256'] = hashlib.sha256(self.raw.read_bytes()).hexdigest()
        self.assertEqual(queue.select_source(self.base, self.meta)[1], 'short_body_requires_review')
        (self.base / '01-translation.md').write_text('<!-- CHUNK 1/2 FAILED -->' + '文' * 200, encoding='utf-8')
        self.assertEqual(queue.select_source(self.base, self.meta)[1], 'incomplete_translation')

    def test_complete_translation_allowed_but_selection_change_invalidates_snapshot(self):
        self.meta['language'] = 'Sanskrit'
        self.write_meta()
        tr = self.base / '01-translation.md'
        tr.write_text('完整譯文' * 100, encoding='utf-8')
        self.assertEqual(queue.select_source(self.base, self.meta), (tr, None))
        self.assertEqual(queue.validate_source(self.entry, self.translations), 'tagging_source_changed')

    def test_changed_source_is_terminal_without_spending_model_calls(self):
        import pipeline_failures
        result = pipeline_failures.record_failure(
            'demo', queue.QUEUE_NAME, 'tag', 'tag_source_changed', 'source changed',
            path=self.root / 'failed.json', lock_path=self.root / 'failed.lock')
        self.assertEqual(result['status'], 'blocked')
        self.assertEqual(result['attempts'], 1)

    def test_failed_corpus_verification_prevents_push(self):
        pipeline = module('tag_verify_gate_test', 'auto-pipeline.py')
        with mock.patch.object(pipeline, 'ROOT', self.root), \
                mock.patch.object(pipeline, 'run_git', return_value=(0, 'ok')) as git, \
                mock.patch.object(pipeline.subprocess, 'run', return_value=mock.Mock(returncode=1)):
            pipeline.commit_batch([self.raw], 'test', push=True)
        self.assertFalse(any(call.args[0][0] == 'push' for call in git.call_args_list))

    def test_legacy_supervisor_argument_starts_persisted_tag_job(self):
        with mock.patch.object(sys, 'argv', ['supervise-pipeline.py', '核心']):
            supervisor = module('tag_supervisor_test', 'supervise-pipeline.py')
        self.assertEqual(supervisor.TIER, queue.QUEUE_NAME)
        proc = mock.Mock(stdout=iter(['tier=標籤補齊 this_run=1\n', 'done: processed 1/1\n']), returncode=0)
        with mock.patch.object(supervisor, 'RUN_LOG', self.root / 'run.log'), \
                mock.patch.object(supervisor.subprocess, 'Popen', return_value=proc) as popen:
            result = supervisor.run_once()
        self.assertIn('--tag-queue', popen.call_args.args[0])
        self.assertNotIn('--tier', popen.call_args.args[0])
        self.assertEqual(result[2], 1)

    def test_quota_resume_with_legacy_argument_uses_tag_job(self):
        watcher = module('tag_quota_test', 'quota-watch-resume.py')
        state = {'status': 'waiting_provider', 'slug': 'demo', 'tasks': ['tag']}
        with mock.patch.object(watcher, 'HALT', self.root / 'HALT'), \
                mock.patch.object(watcher, 'load_state', return_value=state), \
                mock.patch.object(watcher, 'save_state'), mock.patch.object(watcher, 'log'), \
                mock.patch.object(watcher.subprocess, 'Popen', return_value=mock.Mock(pid=1)) as popen:
            self.assertTrue(watcher.resume('核心'))
        self.assertEqual(popen.call_args.args[0][-1], queue.QUEUE_NAME)

    def test_tag_only_worker_keeps_translation_axis_and_restarts_without_api(self):
        pipeline = module('tag_pipeline_test', 'auto-pipeline.py')
        runtime = self.root / 'runtime.json'
        before = self.raw.read_bytes()
        payload = {'semantic_tags': ['forgiveness'], 'psych_tags': ['emotions-passions'], 'keywords': ['寬忍']}
        with ExitStack() as stack:
            for obj, name, value in [
                (pipeline, 'TRANSLATIONS_DIR', self.translations),
                (pipeline, 'RUNTIME_PATH', runtime), (pipeline, 'STATUS_PATH', self.root / 'status.md'),
                (pipeline, 'HALT_PATH', self.root / 'HALT'),
                (translate, 'TRANSLATIONS_DIR', self.translations),
                (translate, 'RUNTIME_STATE_PATH', runtime),
                (translate, 'CHECKPOINT_ROOT', self.root / 'checkpoints'),
                (translate, 'METRICS_PATH', self.root / 'metrics.jsonl')]:
                stack.enter_context(mock.patch.object(obj, name, value))
            stack.enter_context(mock.patch.object(pipeline.pipeline_failures, 'load', return_value=({'schema_version': 2, 'failures': {}}, False)))
            stack.enter_context(mock.patch.object(pipeline, 'rebuild_indexes', return_value=[]))
            stack.enter_context(mock.patch.object(pipeline, 'commit_batch'))
            translator = stack.enter_context(mock.patch.object(translate, 'translate_one', side_effect=AssertionError('must not translate')))
            call = stack.enter_context(mock.patch.object(translate, '_call_tag_json', return_value=('ok', payload)))
            stack.enter_context(mock.patch.object(sys, 'argv', ['auto-pipeline.py', '--tag-queue', '--no-push']))
            pipeline.main()
            pipeline.main()
            self.assertEqual(call.call_count, 1)
            translator.assert_not_called()
        meta = json.loads((self.base / 'meta.json').read_text(encoding='utf-8'))
        self.assertEqual(meta['tag_status'], 'done')
        self.assertEqual(meta['psych_tag_status'], 'done')
        self.assertNotIn('translation_status', meta)
        self.assertFalse((self.base / '01-translation.md').exists())
        self.assertEqual(before, self.raw.read_bytes())
        self.assertEqual(meta['tag_source']['source_sha256'], self.entry['source_sha256'])
        self.assertEqual(json.loads(runtime.read_text(encoding='utf-8'))['tasks'], ['tag'])
        self.assertIn('已完成雙標籤', (self.root / 'status.md').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
