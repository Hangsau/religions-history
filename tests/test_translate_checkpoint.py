import json
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import translate  # noqa: E402


class TranslateCheckpointTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.translations = self.root / "translations"
        self.checkpoints = self.root / "logs" / "pipeline-checkpoints"
        self.runtime = self.root / "logs" / "pipeline-runtime.json"
        self.metrics = self.root / "logs" / "pipeline-metrics.jsonl"
        self.patches = [
            mock.patch.object(translate, "TRANSLATIONS_DIR", self.translations),
            mock.patch.object(translate, "CHECKPOINT_ROOT", self.checkpoints),
            mock.patch.object(translate, "RUNTIME_STATE_PATH", self.runtime),
            mock.patch.object(translate, "METRICS_PATH", self.metrics),
        ]
        for patcher in self.patches:
            patcher.start()

    def tearDown(self):
        for patcher in reversed(self.patches):
            patcher.stop()
        self.temp.cleanup()

    def make_slug(self, slug="demo", chapter_chars=2900):
        base = self.translations / slug
        (base / "raw").mkdir(parents=True)
        original = "\n".join(
            f"=== {i} | c{i} ===\n" + chr(64 + i) * chapter_chars
            for i in range(1, 4)
        )
        (base / "raw" / "original.txt").write_text(original, encoding="utf-8")
        (base / "meta.json").write_text(json.dumps({
            "slug": slug, "name_zh": "測試", "language": "Greek",
            "religion": "測試", "version": "test", "text_role": "original",
        }), encoding="utf-8")
        return base, original

    def test_partial_failure_resumes_only_missing_chunk(self):
        base, _ = self.make_slug()
        published = base / "01-translation.md"
        published.write_text("OLD PUBLISHED CONTENT\n" * 10, encoding="utf-8")
        role = "translation role"
        first_outputs = [
            "# 測試 — 翻譯\n\n=== 1 | c1 ===\n第一段",
            "=== 2 | c2 ===\n第二段",
            None,
        ]
        with mock.patch.object(translate, "call_m3", side_effect=first_outputs):
            self.assertFalse(translate.translate_one("demo", "translate", role))
        self.assertTrue(published.read_text(encoding="utf-8").startswith("OLD PUBLISHED"))
        active = self.checkpoints / "demo" / "translate" / "active"
        manifest = json.loads((active / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual([c["status"] for c in manifest["chunks"]], ["done", "done", "pending"])

        with mock.patch.object(translate, "call_m3", return_value="=== 3 | c3 ===\n第三段") as call:
            self.assertTrue(translate.translate_one("demo", "translate", role))
        self.assertEqual(call.call_count, 1)
        final = published.read_text(encoding="utf-8")
        self.assertIn("第一段", final)
        self.assertIn("第二段", final)
        self.assertIn("第三段", final)
        self.assertFalse(active.exists())

    def test_source_change_archives_checkpoint(self):
        _, source = self.make_slug()
        chunks = ["one", "two"]
        active, manifest, _ = translate._prepare_checkpoint("demo", "translate", source, "role", chunks)
        translate._save_checkpoint_part(active, manifest, 1, "# output\n")
        new_active, _, completed = translate._prepare_checkpoint(
            "demo", "translate", source + "changed", "role", chunks
        )
        self.assertEqual(completed, {})
        self.assertTrue(new_active.exists())
        self.assertTrue(any(p.name.startswith("stale-") for p in new_active.parent.iterdir()))

    def test_role_change_archives_checkpoint(self):
        _, source = self.make_slug()
        chunks = ["one", "two"]
        active, manifest, _ = translate._prepare_checkpoint("demo", "translate", source, "old role", chunks)
        translate._save_checkpoint_part(active, manifest, 1, "# output\n")
        new_active, _, completed = translate._prepare_checkpoint(
            "demo", "translate", source, "new role", chunks
        )
        self.assertEqual(completed, {})
        self.assertTrue(any(p.name.startswith("stale-") for p in new_active.parent.iterdir()))

    def test_oversized_single_chapter_resumes_without_marker_requirement(self):
        base = self.translations / "oversized"
        (base / "raw").mkdir(parents=True)
        original = "=== 1 | huge ===\n" + "甲" * 9000
        (base / "raw" / "original.txt").write_text(original, encoding="utf-8")
        (base / "meta.json").write_text(json.dumps({
            "slug": "oversized", "name_zh": "大章", "language": "Greek",
            "religion": "測試", "version": "test", "text_role": "original",
        }), encoding="utf-8")
        with mock.patch.object(translate, "call_m3", side_effect=[
            "# 大章 — 翻譯\n第一段", "無章節標記的續段", None,
        ]):
            self.assertFalse(translate.translate_one("oversized", "translate", "role"))
        with mock.patch.object(translate, "call_m3", return_value="最後續段") as call:
            self.assertTrue(translate.translate_one("oversized", "translate", "role"))
        self.assertEqual(call.call_count, 2)
        final = (base / "01-translation.md").read_text(encoding="utf-8")
        self.assertIn("無章節標記的續段", final)
        self.assertIn("最後續段", final)

    def test_corrupt_part_is_not_reused(self):
        _, source = self.make_slug()
        active, manifest, _ = translate._prepare_checkpoint(
            "demo", "translate", source, "role", ["one", "two"]
        )
        translate._save_checkpoint_part(active, manifest, 1, "# valid\n")
        (active / "chunk-0001.md").write_text("corrupt", encoding="utf-8")
        _, refreshed, completed = translate._prepare_checkpoint(
            "demo", "translate", source, "role", ["one", "two"]
        )
        self.assertEqual(completed, {})
        self.assertEqual(refreshed["chunks"][0]["status"], "pending")

    def test_dry_run_creates_no_checkpoint_or_metrics(self):
        self.make_slug()
        with mock.patch.object(translate, "call_m3", return_value=None):
            self.assertTrue(translate.translate_one("demo", "translate", "role", dry_run=True))
        self.assertFalse(self.checkpoints.exists())
        self.assertFalse(self.metrics.exists())
        self.assertFalse(self.runtime.exists())

    def test_tag_chunk_failure_does_not_publish_partial_axes(self):
        base, _ = self.make_slug()
        role = "tag role"
        first = json.dumps({
            "semantic_tags": ["meaning"], "psych_tags": ["death"], "keywords": ["x"],
        })
        with mock.patch.object(translate, "call_m3", side_effect=[first, None]):
            self.assertFalse(translate.tag_one(
                "demo", role, {"meaning"}, {"death"}))
        meta = json.loads((base / "meta.json").read_text(encoding="utf-8"))
        self.assertNotIn("tag_status", meta)
        self.assertNotIn("psych_tag_status", meta)

    def test_token_and_timeout_are_ordinary_errors_but_429_waits(self):
        with mock.patch.object(translate, "_resolve_backend", return_value=None):
            self.assertIsNone(translate.call_m3("prompt"))
        state = json.loads(self.runtime.read_text(encoding="utf-8"))
        self.assertEqual(state["status"], "error")

        with mock.patch.object(translate, "_resolve_backend", return_value=("url", "token")), \
                mock.patch.object(translate, "_run_claude", return_value=(None, "timeout after 360s")):
            self.assertIsNone(translate.call_m3("prompt"))
        state = json.loads(self.runtime.read_text(encoding="utf-8"))
        self.assertEqual(state["status"], "error")

        with mock.patch.object(translate, "_resolve_backend", return_value=("url", "token")), \
                mock.patch.object(translate, "_run_claude", return_value=(None, "HTTP 429 rate limit")):
            self.assertIsNone(translate.call_m3("prompt"))
        state = json.loads(self.runtime.read_text(encoding="utf-8"))
        self.assertEqual(state["status"], "waiting_quota")
        self.assertIsNone(state["next_retry_at"])
        self.assertIsNone(state["quota_wait_mode"])
        self.assertEqual(state["retry_attempt"], 0)

    def test_complete_translation_rejects_failed_marker(self):
        path = self.root / "translation.md"
        path.write_text("x" * 200, encoding="utf-8")
        self.assertTrue(translate.has_complete_translation(path))
        path.write_text("x" * 200 + "<!-- CHUNK 1/2 FAILED -->", encoding="utf-8")
        self.assertFalse(translate.has_complete_translation(path))

    def test_timeout_terminates_windows_process_tree(self):
        proc = mock.Mock(pid=4321, returncode=None)
        proc.communicate.side_effect = [
            translate.subprocess.TimeoutExpired("claude", 1),
            (b"", b""),
        ]
        with mock.patch.object(translate.subprocess, "Popen", return_value=proc), \
                mock.patch.object(translate.subprocess, "run") as run, \
                mock.patch.object(translate.os, "name", "nt"):
            output, error = translate._run_claude("prompt", "url", "token", "model")
        self.assertIsNone(output)
        self.assertIn("timeout after", error)
        self.assertEqual("taskkill", run.call_args.args[0][0])
        self.assertIn("/T", run.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
