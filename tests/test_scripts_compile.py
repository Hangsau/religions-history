import py_compile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


class ScriptsCompileTests(unittest.TestCase):
    def test_every_script_compiles(self):
        # supervise-pipeline.py is never imported by other tests; a syntax error there
        # silently kills every supervisor the desktop board launches.
        for path in sorted(SCRIPTS.glob("*.py")):
            with self.subTest(script=path.name):
                py_compile.compile(str(path), doraise=True)


if __name__ == "__main__":
    unittest.main()
