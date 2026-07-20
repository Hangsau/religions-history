import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import translate


class PsychTagTests(unittest.TestCase):
    def test_vocab_is_exact_table_vocabulary(self):
        vocab = translate.load_psych_tag_whitelist()
        self.assertEqual(48, len(vocab))
        self.assertIn("death", vocab)
        self.assertIn("nature-animals-ecology", vocab)
        self.assertNotIn("liberation-by-devotion", vocab)
        self.assertNotIn("X-impermanence", vocab)

    def test_merge_keeps_axes_separate(self):
        with tempfile.TemporaryDirectory() as temp:
            old = translate.TRANSLATIONS_DIR
            try:
                translate.TRANSLATIONS_DIR = Path(temp)
                base = Path(temp) / "demo"
                base.mkdir()
                (base / "meta.json").write_text("{}", encoding="utf-8")
                translate.merge_meta_tags("demo", ["new-sem"], ["death"], ["死亡"])
                meta = json.loads((base / "meta.json").read_text(encoding="utf-8"))
            finally:
                translate.TRANSLATIONS_DIR = old
        self.assertEqual(["new-sem"], meta["semantic_tags"])
        self.assertEqual(["death"], meta["psych_tags"])
        self.assertEqual("done", meta["tag_status"])
        self.assertEqual("done", meta["psych_tag_status"])

    def test_index_has_independent_psych_axis(self):
        spec = importlib.util.spec_from_file_location("build_tag_index", SCRIPTS / "build-tag-index.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as temp:
            old = module.TRANSLATIONS_DIR
            try:
                module.TRANSLATIONS_DIR = Path(temp)
                base = Path(temp) / "demo"
                base.mkdir()
                (base / "meta.json").write_text(json.dumps({
                    "slug": "demo", "name_zh": "示例", "religion": "佛教",
                    "semantic_tags": ["impermanence"], "psych_tags": ["death"],
                    "keywords": ["死亡"], "tag_status": "done",
                    "psych_tag_status": "done",
                }), encoding="utf-8")
                semantic, keywords, psych, tagged = module.build()
            finally:
                module.TRANSLATIONS_DIR = old
        self.assertEqual(1, tagged)
        self.assertIn("impermanence", semantic)
        self.assertIn("死亡", keywords)
        self.assertIn("death", psych)
    def test_classify_reprocesses_downgraded_tag_axes(self):
        spec = importlib.util.spec_from_file_location(
            "classify_metadata_status", SCRIPTS / "classify-metadata.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        stale = {
            "semantic_tags": ["old"], "psych_tags": ["old"],
            "tag_status": "none", "psych_tag_status": "none",
            "era": "modern", "genre": "commentary",
        }
        self.assertTrue(module.needs_classify(stale))
        with tempfile.TemporaryDirectory() as temp:
            old = module.TRANSLATIONS_DIR
            try:
                module.TRANSLATIONS_DIR = Path(temp)
                base = Path(temp) / "demo"
                base.mkdir()
                (base / "meta.json").write_text(json.dumps(stale), encoding="utf-8")
                module.apply_classification(
                    "demo",
                    {"semantic_tags": ["new"], "psych_tags": ["death"], "keywords": ["新"]},
                    {"new"}, {"death"})
                meta = json.loads((base / "meta.json").read_text(encoding="utf-8"))
            finally:
                module.TRANSLATIONS_DIR = old
        self.assertEqual(meta["semantic_tags"], ["new"])
        self.assertEqual(meta["psych_tags"], ["death"])
        self.assertEqual(meta["tag_status"], "done")
        self.assertEqual(meta["psych_tag_status"], "done")

    def test_index_excludes_axes_without_done_status(self):
        spec = importlib.util.spec_from_file_location("build_tag_index_status", SCRIPTS / "build-tag-index.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as temp:
            old = module.TRANSLATIONS_DIR
            try:
                module.TRANSLATIONS_DIR = Path(temp)
                base = Path(temp) / "demo"
                base.mkdir()
                (base / "meta.json").write_text(json.dumps({
                    "slug": "demo", "semantic_tags": ["impermanence"],
                    "psych_tags": ["death"], "keywords": ["死亡"],
                    "tag_status": "none", "psych_tag_status": "none",
                }), encoding="utf-8")
                semantic, keywords, psych, tagged = module.build()
            finally:
                module.TRANSLATIONS_DIR = old
        self.assertEqual((semantic, keywords, psych, tagged), ({}, {}, {}, 0))


if __name__ == "__main__":
    unittest.main()
