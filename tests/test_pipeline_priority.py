import json
import importlib.util
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import pipeline_priority  # noqa: E402

AUTO_SCRIPT = SCRIPTS / "auto-pipeline.py"
AUTO_SPEC = importlib.util.spec_from_file_location("auto_pipeline", AUTO_SCRIPT)
auto_pipeline = importlib.util.module_from_spec(AUTO_SPEC)
AUTO_SPEC.loader.exec_module(auto_pipeline)


def make_book(root: Path, slug: str, religion: str = "Test") -> None:
    base = root / slug
    (base / "raw").mkdir(parents=True)
    (base / "raw" / "original.txt").write_text("x" * 200, encoding="utf-8")
    (base / "meta.json").write_text(json.dumps({
        "slug": slug, "tier": "核心", "religion": religion,
        "tag_status": "none", "psych_tag_status": "none",
    }), encoding="utf-8")


class PipelinePriorityTests(unittest.TestCase):
    def test_manifest_rejects_duplicate_and_alias(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            translations = root / "translations"
            make_book(translations, "alias")
            meta_path = translations / "alias" / "meta.json"
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            meta["alias_of"] = "canonical"
            meta_path.write_text(json.dumps(meta), encoding="utf-8")
            manifest = root / "priority.json"
            manifest.write_text(json.dumps({
                "schema_version": 1, "required_religions": [],
                "entries": [{"slug": "alias", "priority": "P0", "reason": "x"}],
            }), encoding="utf-8")
            self.assertTrue(any("alias" in e for e in pipeline_priority.audit(manifest, translations)))

    def test_due_p0_retry_precedes_new_p0_and_p1(self):
        with tempfile.TemporaryDirectory() as td:
            translations = Path(td)
            for slug in ("p1", "p0-new", "p0-retry", "p0-future", "p0-blocked"):
                make_book(translations, slug)
            now = datetime(2026, 7, 20, tzinfo=timezone.utc)
            failures = {
                "p0-retry": {"status": "retryable", "next_retry_at": (now - timedelta(seconds=1)).isoformat()},
                "p0-future": {"status": "retryable", "next_retry_at": (now + timedelta(hours=1)).isoformat()},
                "p0-blocked": {"status": "blocked", "next_retry_at": None},
            }
            priorities = {slug: "P0" for slug in failures}
            priorities["p0-new"] = "P0"
            pending = auto_pipeline.build_pending(
                ["p1", "p0-new", "p0-retry", "p0-future", "p0-blocked"],
                ["translate"], failures, "核心", now, translations, priorities)
            self.assertEqual(pending, ["p0-retry", "p0-new", "p1"])

    def test_deferred_and_blocked_items_are_not_counted_complete(self):
        with tempfile.TemporaryDirectory() as td:
            translations = Path(td)
            for slug in ("done", "future", "blocked"):
                make_book(translations, slug)
            (translations / "done" / "01-translation.md").write_text(
                "complete translation\n" * 20, encoding="utf-8")
            self.assertEqual(
                auto_pipeline.count_completed(
                    ["done", "future", "blocked"], ["translate"], translations),
                1,
            )

    def test_empty_queue(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(auto_pipeline.build_pending(
                [], ["translate"], {}, "核心", translations_dir=Path(td), priorities={}), [])


if __name__ == "__main__":
    unittest.main()
