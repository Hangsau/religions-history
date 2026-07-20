import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "reconcile-pipeline-state.py"
SPEC = importlib.util.spec_from_file_location("reconcile_pipeline_state", SCRIPT)
reconcile = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(reconcile)


class ReconcilePipelineStateTests(unittest.TestCase):
    def make_book(self, root: Path, slug: str, translation: str, status: str = "done") -> Path:
        base = root / slug
        base.mkdir()
        meta = {
            "translation_status": status, "tag_status": "done",
            "psych_tag_status": "done", "semantic_tags": ["x"], "psych_tags": ["y"],
        }
        (base / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
        (base / "01-translation.md").write_text(translation, encoding="utf-8")
        return base

    def test_dry_run_apply_and_idempotence(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            base = self.make_book(root, "bad", "x" * 120 + "<!-- CHUNK 2/3 FAILED -->")
            self.assertEqual(len(reconcile.reconcile(root, apply=False)), 1)
            before = json.loads((base / "meta.json").read_text(encoding="utf-8"))
            self.assertEqual(before["translation_status"], "done")
            self.assertEqual(len(reconcile.reconcile(root, apply=True)), 1)
            after = json.loads((base / "meta.json").read_text(encoding="utf-8"))
            self.assertEqual(after["translation_status"], "needs-review")
            self.assertEqual(after["tag_status"], "none")
            self.assertEqual(after["semantic_tags"], ["x"])
            self.assertEqual(reconcile.reconcile(root, apply=True), [])

    def test_annotation_marker_does_not_affect_translation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            base = self.make_book(root, "good", "# 完整\n" + "正文" * 100)
            (base / "02-annotation.md").write_text("<!-- CHUNK 1/2 FAILED -->", encoding="utf-8")
            self.assertEqual(reconcile.reconcile(root), [])

    def test_never_promotes_unverified_translation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.make_book(root, "pending", "# 完整\n" + "正文" * 100, status="none")
            self.assertEqual(reconcile.reconcile(root, apply=True), [])


if __name__ == "__main__":
    unittest.main()
