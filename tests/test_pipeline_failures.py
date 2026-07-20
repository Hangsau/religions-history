import json
import sys
import tempfile
import threading
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import pipeline_failures  # noqa: E402


class PipelineFailureTests(unittest.TestCase):
    def paths(self, td):
        root = Path(td)
        return root / "failed.json", root / "failed.lock"

    def test_v1_migration_is_idempotent(self):
        old = {"book": {"at": "2026-07-20T00:00:00+00:00", "tier": "核心"}}
        state, changed = pipeline_failures.migrate(old)
        self.assertTrue(changed)
        self.assertEqual(state["failures"]["book"]["attempts"], 1)
        again, changed_again = pipeline_failures.migrate(state)
        self.assertFalse(changed_again)
        self.assertEqual(again, state)

    def test_unknown_and_malformed_schema_are_rejected(self):
        with self.assertRaises(ValueError):
            pipeline_failures.migrate({"schema_version": 99, "failures": {}})
        with self.assertRaises(ValueError):
            pipeline_failures.migrate({
                "schema_version": 2,
                "failures": {"book": {"status": "retryable", "attempts": "one"}},
            })
        with tempfile.TemporaryDirectory() as td:
            path, _ = self.paths(td)
            path.write_text("{partial", encoding="utf-8")
            with self.assertRaises(ValueError):
                pipeline_failures.load(path)

    def test_three_retries_then_block_on_next_failure(self):
        with tempfile.TemporaryDirectory() as td:
            path, lock = self.paths(td)
            now = datetime(2026, 7, 20, tzinfo=timezone.utc)
            for attempt, delay in enumerate(pipeline_failures.RETRY_DELAYS, 1):
                entry = pipeline_failures.record_failure(
                    "book", "核心", "translate", "failed", "x", now, path, lock)
                self.assertEqual(entry["status"], "retryable")
                self.assertEqual(entry["attempts"], attempt)
                self.assertEqual(datetime.fromisoformat(entry["next_retry_at"]),
                                 now + timedelta(seconds=delay))
            entry = pipeline_failures.record_failure(
                "book", "核心", "translate", "failed", "x", now, path, lock)
            self.assertEqual(entry["status"], "blocked")
            self.assertIsNone(entry["next_retry_at"])

    def test_unblock_rejects_paths_and_unknown_slugs(self):
        with tempfile.TemporaryDirectory() as td:
            path, lock = self.paths(td)
            translations = Path(td) / "translations"
            with self.assertRaises(ValueError):
                pipeline_failures.unblock("../escape", translations, path, lock)
            with self.assertRaises(ValueError):
                pipeline_failures.unblock("missing", translations, path, lock)

    def test_simultaneous_writers_do_not_lose_slugs(self):
        with tempfile.TemporaryDirectory() as td:
            path, lock = self.paths(td)
            errors = []

            def writer(slug):
                try:
                    pipeline_failures.record_failure(
                        slug, "核心", "tag", "failed", "x", path=path, lock_path=lock)
                except Exception as exc:  # pragma: no cover
                    errors.append(exc)

            threads = [threading.Thread(target=writer, args=(f"book-{i}",)) for i in range(20)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            state, _ = pipeline_failures.load(path)
            self.assertEqual(errors, [])
            self.assertEqual(len(state["failures"]), 20)


if __name__ == "__main__":
    unittest.main()
