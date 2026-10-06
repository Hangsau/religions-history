import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import pipeline_lock  # noqa: E402


class PipelineLockTests(unittest.TestCase):
    def test_second_process_cannot_enter_while_first_owns_generation(self):
        program = (
            "import sys; from pathlib import Path; "
            "sys.path.insert(0, sys.argv[1]); import pipeline_lock as lock; "
            "lock.LOCK_PATH=Path(sys.argv[2]); acquired=lock.acquire_run_lock(); "
            "print('OWNER' if acquired else 'BLOCKED', flush=True); "
            "sys.stdin.readline() if acquired and sys.argv[3]=='hold' else None; "
            "lock.release_run_lock() if acquired else None"
        )
        args = [sys.executable, "-c", program, str(SCRIPTS), str(self.lock)]
        owner = subprocess.Popen(args + ["hold"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, text=True,
                                 creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        try:
            self.assertEqual(owner.stdout.readline().strip(), "OWNER")
            second = subprocess.run(args + ["try"], capture_output=True, text=True, timeout=10,
                                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertIn("BLOCKED", second.stdout)
            self.assertEqual(int(self.lock.read_text()), owner.pid)
        finally:
            owner.communicate("release\n", timeout=10)
        self.assertFalse(self.lock.exists())

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
