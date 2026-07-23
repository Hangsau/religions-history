import importlib.util
import io
import json
import sys
import tempfile
import unittest
import urllib.error
from datetime import datetime, timedelta
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location("quota_watch_resume", SCRIPTS / "quota-watch-resume.py")
quota_watch = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(quota_watch)


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


class QuotaProbeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.token = Path(self.temp.name) / "token"
        self.token.write_text("token", encoding="utf-8")
        self.now = datetime(2026, 7, 21, 8, 0, tzinfo=quota_watch.TZ)
        self.interval_reset = self.now + timedelta(hours=2)
        self.weekly_reset = self.now + timedelta(days=3)
        self.token_patch = mock.patch.object(quota_watch, "MINIMAX_TOKEN_PATH", self.token)
        self.token_patch.start()

    def tearDown(self):
        self.token_patch.stop()
        self.temp.cleanup()

    @staticmethod
    def millis(value):
        return int(value.timestamp() * 1000)

    def payload(self, interval=20, weekly=30, interval_reset=None, weekly_reset=None):
        return {"model_remains": [{
            "model_name": "general",
            "current_interval_remaining_percent": interval,
            "current_weekly_remaining_percent": weekly,
            "end_time": self.millis(interval_reset or self.interval_reset),
            "weekly_end_time": self.millis(weekly_reset or self.weekly_reset),
            "current_interval_status": 1,
            "current_weekly_status": 1,
        }]}

    def probe(self, payload):
        with mock.patch.object(quota_watch.urllib.request, "urlopen", return_value=FakeResponse(payload)):
            return quota_watch.probe_quota(self.now)

    def test_usable_quota_has_no_retry_target(self):
        outcome, _, summary, retry_at = self.probe(self.payload())
        self.assertEqual(outcome, "usable")
        self.assertIsNone(retry_at)
        self.assertEqual(summary["interval_remaining_percent"], 20)

    def test_interval_exhaustion_uses_interval_reset_plus_buffer(self):
        outcome, _, _, retry_at = self.probe(self.payload(interval=0))
        self.assertEqual(outcome, "official_reset")
        self.assertEqual(retry_at, self.interval_reset + timedelta(seconds=15))

    def test_interval_reserve_stops_before_zero(self):
        outcome, _, summary, retry_at = self.probe(self.payload(interval=4))
        self.assertEqual(outcome, "official_reset")
        self.assertEqual(summary["interval_remaining_percent"], 4)
        self.assertEqual(retry_at, self.interval_reset + timedelta(seconds=15))

    def test_weekly_exhaustion_uses_weekly_reset_plus_buffer(self):
        outcome, _, _, retry_at = self.probe(self.payload(weekly=0))
        self.assertEqual(outcome, "official_reset")
        self.assertEqual(retry_at, self.weekly_reset + timedelta(seconds=15))

    def test_dual_exhaustion_uses_later_reset(self):
        outcome, _, _, retry_at = self.probe(self.payload(interval=0, weekly=0))
        self.assertEqual(outcome, "official_reset")
        self.assertEqual(retry_at, self.weekly_reset + timedelta(seconds=15))

    def test_missing_or_expired_reset_uses_fallback(self):
        missing = self.payload(interval=0)
        missing["model_remains"][0]["end_time"] = None
        self.assertEqual(self.probe(missing)[0], "fallback")
        expired = self.payload(interval=0, interval_reset=self.now - timedelta(seconds=1))
        self.assertEqual(self.probe(expired)[0], "fallback")

    def test_invalid_percentage_uses_fallback(self):
        self.assertEqual(self.probe(self.payload(interval=True))[0], "fallback")
        self.assertEqual(self.probe(self.payload(weekly=float("nan")))[0], "fallback")

    def test_http_error_uses_fallback_without_quota_replacement(self):
        error = urllib.error.HTTPError("url", 429, "limited", {}, io.BytesIO())
        with mock.patch.object(quota_watch.urllib.request, "urlopen", side_effect=error):
            outcome, detail, summary, retry_at = quota_watch.probe_quota(self.now)
        self.assertEqual(outcome, "fallback")
        self.assertEqual(summary, {})
        self.assertIsNone(retry_at)
        self.assertIn("429", detail)


class WatchStateTests(unittest.TestCase):
    def test_official_reset_is_saved_before_wait_without_reprobe(self):
        state = {"status": "waiting_quota", "next_retry_at": "legacy", "retry_attempt": 2}
        retry_at = datetime.now(quota_watch.TZ) + timedelta(hours=2)

        def load_state():
            return dict(state)

        def save_state(updated):
            state.clear()
            state.update(updated)

        with mock.patch.object(quota_watch, "load_state", side_effect=load_state), \
             mock.patch.object(quota_watch, "save_state", side_effect=save_state), \
             mock.patch.object(quota_watch, "probe_quota", return_value=("official_reset", "limited", {"model": "general"}, retry_at)) as probe, \
             mock.patch.object(quota_watch, "_wait_until", return_value="halt") as wait_until, \
             mock.patch.object(quota_watch, "HALT", mock.Mock(**{"exists.return_value": False})), \
             mock.patch.object(quota_watch, "log"), \
             mock.patch.object(sys, "argv", ["quota-watch-resume.py"]):
            quota_watch.main()
        probe.assert_called_once_with()
        wait_until.assert_called_once()
        self.assertEqual(state["quota_wait_mode"], "official_reset")
        self.assertEqual(state["next_retry_at"], retry_at.isoformat())
        self.assertEqual(state["retry_attempt"], 0)

    def test_fallback_is_scheduled_once_at_five_minutes(self):
        state = {"status": "waiting_quota", "retry_attempt": 0}

        def load_state():
            return dict(state)

        def save_state(updated):
            state.clear()
            state.update(updated)

        started = datetime.now(quota_watch.TZ)
        with mock.patch.object(quota_watch, "load_state", side_effect=load_state), \
             mock.patch.object(quota_watch, "save_state", side_effect=save_state), \
             mock.patch.object(quota_watch, "probe_quota", return_value=("fallback", "HTTP 503", {}, None)) as probe, \
             mock.patch.object(quota_watch, "_wait_until", return_value="halt") as wait_until, \
             mock.patch.object(quota_watch, "HALT", mock.Mock(**{"exists.return_value": False})), \
             mock.patch.object(quota_watch, "log"), \
             mock.patch.object(sys, "argv", ["quota-watch-resume.py"]):
            quota_watch.main()
        scheduled = datetime.fromisoformat(state["next_retry_at"])
        self.assertEqual(state["quota_wait_mode"], "fallback")
        self.assertEqual(state["retry_attempt"], 1)
        self.assertGreaterEqual((scheduled - started).total_seconds(), 299)
        self.assertLessEqual((scheduled - started).total_seconds(), 301)
        probe.assert_called_once_with()
        wait_until.assert_called_once()

    def test_changed_wait_target_interrupts_without_sleep(self):
        target = datetime.now(quota_watch.TZ) + timedelta(hours=1)
        state = {"status": "waiting_quota", "quota_wait_mode": "fallback",
                 "next_retry_at": (target + timedelta(minutes=1)).isoformat()}
        with mock.patch.object(quota_watch, "load_state", return_value=state), \
             mock.patch.object(quota_watch, "HALT", mock.Mock(**{"exists.return_value": False})), \
             mock.patch.object(quota_watch.time, "sleep") as sleep:
            result = quota_watch._wait_until(target, "fallback", target + timedelta(days=1))
        self.assertEqual(result, "target_changed")
        sleep.assert_not_called()

    def test_halt_prevents_resume(self):
        with mock.patch.object(quota_watch, "HALT", mock.Mock(**{"exists.return_value": True})), \
             mock.patch.object(quota_watch.subprocess, "Popen") as popen:
            self.assertFalse(quota_watch.resume("核心"))
        popen.assert_not_called()

    def test_provider_wait_can_resume_from_same_handoff(self):
        state = {"status": "waiting_provider", "slug": "book", "chunk": 3,
                 "handoff": {"resume_from_checkpoint": True}}
        with mock.patch.object(quota_watch, "HALT", mock.Mock(**{"exists.return_value": False})), \
                mock.patch.object(quota_watch, "load_state", return_value=dict(state)), \
                mock.patch.object(quota_watch, "save_state") as save, \
                mock.patch.object(quota_watch.subprocess, "Popen", return_value=mock.Mock(pid=9)), \
                mock.patch.object(quota_watch, "log"):
            self.assertTrue(quota_watch.resume("核心"))
        updated = save.call_args.args[0]
        self.assertEqual(updated["status"], "running")
        self.assertEqual(updated["slug"], "book")
        self.assertEqual(updated["chunk"], 3)

    def test_fallback_attempt_rejects_bool_and_negative(self):
        self.assertEqual(quota_watch._fallback_attempt({"retry_attempt": True}), 0)
        self.assertEqual(quota_watch._fallback_attempt({"retry_attempt": -1}), 0)
        self.assertEqual(quota_watch._fallback_attempt({"retry_attempt": 3}), 3)


if __name__ == "__main__":
    unittest.main()
