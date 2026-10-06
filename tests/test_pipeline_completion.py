import importlib.util
import json
import sys
import tempfile
import time
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import translate
import status_gui

spec = importlib.util.spec_from_file_location("pipeline_completion", SCRIPTS / "auto-pipeline.py")
pipeline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pipeline)


class PipelineCompletionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.translations = self.root / "translations"
        self.logs = self.root / "logs"
        self.logs.mkdir()
        self.overview = self.root / "00-overview"
        self.overview.mkdir()
        self.runtime = self.logs / "pipeline-runtime.json"
        self.halt = self.logs / "pipeline-HALT.flag"
        self.state = {"schema_version": 2, "failures": {}}
        self.queue = []
        patches = [
            mock.patch.object(pipeline, "TRANSLATIONS_DIR", self.translations),
            mock.patch.object(pipeline, "RUNTIME_PATH", self.runtime),
            mock.patch.object(pipeline, "STATUS_PATH", self.overview / "PIPELINE_STATUS.md"),
            mock.patch.object(pipeline, "HALT_PATH", self.halt),
            mock.patch.object(translate, "TRANSLATIONS_DIR", self.translations),
            mock.patch.object(translate, "RUNTIME_STATE_PATH", self.runtime),
            mock.patch.object(translate, "load_slugs_by_tier", side_effect=lambda tier: self.queue),
            mock.patch.object(pipeline.pipeline_priority, "priority_map", return_value={}),
            mock.patch.object(pipeline.pipeline_failures, "load", side_effect=lambda: (self.state, False)),
            mock.patch.object(pipeline, "rebuild_indexes", return_value=[]),
            mock.patch.object(pipeline, "commit_batch"),
            mock.patch.object(status_gui.status, "LOGS", self.logs),
            mock.patch.object(status_gui.status, "TRANSLATIONS_DIR", self.translations),
            mock.patch.object(status_gui, "HALT", self.halt),
        ]
        for patch in patches:
            patch.start()
            self.addCleanup(patch.stop)

    def book(self, slug="demo", **meta):
        base = self.translations / slug
        base.mkdir(parents=True)
        data = {"slug": slug, "tier": "核心", **meta}
        (base / "meta.json").write_text(json.dumps(data), encoding="utf-8")
        self.queue.append(slug)
        return base

    def run_main(self, *args):
        with mock.patch.object(sys, "argv", ["auto-pipeline.py", "--no-push", *args]):
            pipeline.main()

    def test_blocked_empty_run_replaces_stale_running_and_board_ignores_fresh_log(self):
        self.book()
        self.state["failures"]["demo"] = {"status": "blocked", "tier": "核心", "next_retry_at": None}
        self.runtime.write_text(json.dumps({"status": "running", "slug": "old-book", "task": "tag"}), encoding="utf-8")
        self.run_main()
        state = json.loads(self.runtime.read_text(encoding="utf-8"))
        self.assertEqual((state["status"], state["idle_reason"]), ("idle", "blocked"))
        self.assertIsNone(state["slug"])
        self.assertEqual(state["blocked_slugs"], ["demo"])
        report = (self.overview / "PIPELINE_STATUS.md").read_text(encoding="utf-8")
        self.assertIn("**idle**", report)
        self.assertNotIn("old-book", report)
        (self.logs / "supervisor-run.log").write_text("[1/1] old-book\n[chunk 3/4] old-book (tag)", encoding="utf-8")
        health = status_gui.pipeline_health(time.time(), state)
        self.assertIn("已阻塞", health["text"])
        self.assertEqual(health["color"], status_gui.BAD)
        activity = status_gui.translation_activity(time.time(), state)
        self.assertIsNone(activity["current"])
        self.assertIsNone(activity["chunk"])

    def test_empty_finished_run_is_idle_done(self):
        self.run_main()
        state = json.loads(self.runtime.read_text(encoding="utf-8"))
        self.assertEqual(state["idle_reason"], "done")
        self.assertIn("(完成)", (self.overview / "PIPELINE_STATUS.md").read_text(encoding="utf-8"))

    def test_deferred_retry_and_batch_limit_remain_distinct(self):
        self.book()
        retry = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        self.state["failures"]["demo"] = {"status": "retryable", "tier": "核心", "next_retry_at": retry}
        self.run_main()
        state = json.loads(self.runtime.read_text(encoding="utf-8"))
        self.assertEqual((state["idle_reason"], state["next_retry_at"]), ("retry_wait", retry))
        self.state["failures"].clear()
        pipeline.finish_runtime("核心", self.queue, ["translate", "tag"], self.state)
        state = json.loads(self.runtime.read_text(encoding="utf-8"))
        self.assertEqual(state["idle_reason"], "batch_limit")
        self.assertEqual(state["runnable_count"], 1)

    def test_provider_wait_is_preserved(self):
        for status in ("waiting_quota", "waiting_provider"):
            before = json.dumps({"status": status, "slug": "demo", "chunk": 2, "next_retry_at": "later"})
            self.runtime.write_text(before, encoding="utf-8")
            pipeline.finish_runtime("核心", [], ["tag"], self.state)
            self.assertEqual(self.runtime.read_text(encoding="utf-8"), before)

    def test_only_missing_clean_complete_metadata_is_reconciled(self):
        for slug, text, extra in [
            ("clean", "# 翻譯\n" + "正文" * 100, {}),
            ("review", "# 翻譯\n" + "正文" * 100, {"translation_status": "needs-review"}),
            ("partial", "<!-- CHUNK 1/2 FAILED -->" + "正文" * 100, {}),
            ("dirty", "# 翻譯\n" + "正文" * 100 + "\n我（主控腳本）會抓你的 stdout 寫入檔案", {}),
            ("short", "", {}),
        ]:
            base = self.book(slug, **extra)
            (base / "01-translation.md").write_text(text, encoding="utf-8")
        touched = pipeline.reconcile_missing_translation_status(self.queue)
        self.assertEqual([p.parent.name for p in touched], ["clean"])
        self.assertEqual(json.loads(touched[0].read_text(encoding="utf-8"))["translation_status"], "done")

    def test_pipeline_dry_run_does_not_write_report_runtime_or_metadata(self):
        base = self.book(tag_status="done", psych_tag_status="done", semantic_tags=["meaning"], psych_tags=["death"])
        (base / "01-translation.md").write_text("# 翻譯\n" + "正文" * 100, encoding="utf-8")
        before = (base / "meta.json").read_bytes()
        self.run_main("--dry-run")
        self.assertFalse(self.runtime.exists())
        self.assertFalse((self.overview / "PIPELINE_STATUS.md").exists())
        self.assertEqual(before, (base / "meta.json").read_bytes())


if __name__ == "__main__":
    unittest.main()
