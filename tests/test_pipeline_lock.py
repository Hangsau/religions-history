import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import pipeline_lock  # noqa: E402


class PipelineLockTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.lock = Path(self.temp.name) / "generation.lock"
        self.patch = mock.patch.object(pipeline_lock, "LOCK_PATH", self.lock)
        self.patch.start()

    def tearDown(self):
        self.patch.stop()
        self.temp.cleanup()

    def test_only_one_live_owner(self):
        self.assertTrue(pipeline_lock.acquire_run_lock())
        with mock.patch.object(os, "kill", return_value=None):
            self.assertFalse(pipeline_lock.acquire_run_lock())
        pipeline_lock.release_run_lock()
        self.assertFalse(self.lock.exists())

    def test_stale_lock_is_reclaimed(self):
        self.lock.write_text("999999", encoding="utf-8")
        with mock.patch.object(os, "kill", side_effect=OSError):
            self.assertTrue(pipeline_lock.acquire_run_lock())
        self.assertEqual(self.lock.read_text(encoding="utf-8"), str(os.getpid()))

    def test_non_owner_cannot_release(self):
        self.lock.write_text("999999", encoding="utf-8")
        pipeline_lock.release_run_lock()
        self.assertTrue(self.lock.exists())


if __name__ == "__main__":
    unittest.main()
