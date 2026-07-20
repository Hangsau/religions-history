import json
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import status_gui  # noqa: E402


class StatusBoardDataTests(unittest.TestCase):
    def test_fresh_runtime_loads_and_old_schema_is_safe(self):
        with tempfile.TemporaryDirectory() as td:
            runtime = Path(td) / "runtime.json"
            runtime.write_text(json.dumps({
                "status": "running", "slug": "live-book",
                "updated_at": "2026-07-20T20:00:00+08:00",
            }), encoding="utf-8")
            now = 1784548830.0  # 2026-07-20T20:00:30+08:00
            with mock.patch.object(status_gui, "RUNTIME", runtime):
                state = status_gui.load_runtime(now)
            self.assertTrue(state["_fresh"])
            self.assertEqual(state["slug"], "live-book")
            self.assertNotIn("chunk", state)

    def test_malformed_and_stale_runtime_do_not_claim_freshness(self):
        with tempfile.TemporaryDirectory() as td:
            runtime = Path(td) / "runtime.json"
            with mock.patch.object(status_gui, "RUNTIME", runtime):
                runtime.write_text("{partial", encoding="utf-8")
                self.assertEqual(status_gui.load_runtime(), {})
                runtime.write_text(json.dumps({
                    "status": "running", "updated_at": "2020-01-01T00:00:00+00:00"
                }), encoding="utf-8")
                self.assertFalse(status_gui.load_runtime(time.time())["_fresh"])

    def test_quota_backoff_stays_fresh_until_announced_retry(self):
        with tempfile.TemporaryDirectory() as td:
            runtime = Path(td) / "runtime.json"
            runtime.write_text(json.dumps({
                "status": "waiting_quota",
                "updated_at": "2026-07-20T19:30:00+08:00",
                "next_retry_at": "2026-07-20T20:30:00+08:00",
            }), encoding="utf-8")
            with mock.patch.object(status_gui, "RUNTIME", runtime):
                state = status_gui.load_runtime(1784550000.0)
            self.assertTrue(state["_fresh"])

    def test_runtime_overrides_stale_log_activity(self):
        runtime = {
            "status": "running", "_fresh": True, "slug": "runtime-book",
            "task": "tag", "chunk": 2, "chunks_total": 7,
        }
        with tempfile.TemporaryDirectory() as td, \
                mock.patch.object(status_gui.status, "LOGS", Path(td)), \
                mock.patch.object(status_gui.status, "TRANSLATIONS_DIR", Path(td) / "translations"):
            activity = status_gui.translation_activity(time.time(), runtime)
        self.assertEqual(activity["current"], "runtime-book")
        self.assertEqual(activity["action"], "tag")
        self.assertEqual(activity["chunk"], "2/7")

    def test_publication_blockers_only_scan_translation_files(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            bad = root / "bad"
            good = root / "good"
            bad.mkdir()
            good.mkdir()
            (bad / "01-translation.md").write_text(
                "<!-- CHUNK 3/9 FAILED — retry needed -->", encoding="utf-8")
            (bad / "02-annotation.md").write_text(
                "<!-- CHUNK 1/2 FAILED -->", encoding="utf-8")
            (good / "01-translation.md").write_text("完整內容", encoding="utf-8")
            self.assertEqual(status_gui.publication_blockers(root), ["bad"])

    def test_completion_axes_stay_independent_for_partial_metadata(self):
        counts = status_gui.completion_counts([
            {"translation_status": "done", "semantic_tags": ["a"], "psych_tags": ["b"],
             "tag_status": "done", "psych_tag_status": "done"},
            {"translation_status": "done", "semantic_tags": ["a"], "psych_tags": [],
             "tag_status": "done", "psych_tag_status": "none"},
            {"translation_status": "pending", "semantic_tags": [], "psych_tags": ["b"],
             "tag_status": "none", "psych_tag_status": "done"},
            {"semantic_tags": ["stale"], "psych_tags": ["stale"],
             "tag_status": "none", "psych_tag_status": "none"},
        ])
        self.assertEqual(counts, {
            "tr_done": 2, "semantic_done": 2, "psych_done": 2, "fully_done": 1,
        })

    def test_large_metadata_set_is_counted_without_special_cases(self):
        metas = [
            {"translation_status": "done", "semantic_tags": ["a"], "psych_tags": ["b"],
             "tag_status": "done", "psych_tag_status": "done"}
            for _ in range(5000)
        ]
        self.assertEqual(status_gui.completion_counts(metas)["fully_done"], 5000)

    def test_runtime_reader_tolerates_concurrent_partial_writes(self):
        with tempfile.TemporaryDirectory() as td:
            runtime = Path(td) / "runtime.json"
            runtime.write_text("{}", encoding="utf-8")
            errors = []

            def writer():
                try:
                    for _ in range(50):
                        runtime.write_text("{partial", encoding="utf-8")
                        runtime.write_text(json.dumps({
                            "status": "running", "slug": "book",
                            "updated_at": "2026-07-20T20:00:00+08:00",
                        }), encoding="utf-8")
                except Exception as exc:  # pragma: no cover - assertion captures it
                    errors.append(exc)

            with mock.patch.object(status_gui, "RUNTIME", runtime):
                thread = threading.Thread(target=writer)
                thread.start()
                for _ in range(100):
                    state = status_gui.load_runtime(1784548830.0)
                    self.assertIsInstance(state, dict)
                thread.join()
            self.assertEqual(errors, [])


class FakeTimerRoot:
    def __init__(self):
        self.jobs = set()
        self.cancelled = []
        self.next_id = 0

    def after(self, _delay, _callback):
        self.next_id += 1
        job = f"job-{self.next_id}"
        self.jobs.add(job)
        return job

    def after_cancel(self, job):
        self.jobs.discard(job)
        self.cancelled.append(job)


class StatusBoardTimerTests(unittest.TestCase):
    def test_repeated_schedule_keeps_one_job(self):
        board = status_gui.Board.__new__(status_gui.Board)
        board.root = FakeTimerRoot()
        board._refresh_job = None
        for _ in range(10):
            board._schedule_refresh()
        self.assertEqual(len(board.root.jobs), 1)
        self.assertEqual(len(board.root.cancelled), 9)


if __name__ == "__main__":
    unittest.main()
