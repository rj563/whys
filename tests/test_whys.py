import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WHYS = os.path.join(ROOT, "bin", "whys")
FIX = os.path.join(ROOT, "tests", "fixtures")


def run(*args, env=None):
    p = subprocess.run([sys.executable, WHYS, *args], capture_output=True, text=True, env=env)
    return p.returncode, p.stdout


class LintTest(unittest.TestCase):
    def test_lint_closed(self):
        code, out = run("lint", os.path.join(FIX, "closed.md"))
        self.assertEqual(code, 0, out)
        self.assertEqual(out.splitlines()[0], "status=closed depth=4 open=0 statements=7")

    def test_lint_open(self):
        code, out = run("lint", os.path.join(FIX, "open.md"))
        self.assertEqual(code, 0, out)
        self.assertIn("status=open", out)
        self.assertIn("open=2", out)

    def test_lint_bad(self):
        code, out = run("lint", os.path.join(FIX, "bad.md"))
        self.assertEqual(code, 1)
        self.assertIn("L5: missing tag", out)
        self.assertIn("L6: bad id S1..2", out)
        self.assertIn("L7: parent S9 missing", out)
        self.assertIn("L8: unknown tag #nope", out)

    def test_lint_dir_unique_ids(self):
        code, out = run("lint", os.path.join(FIX, "project"))
        self.assertEqual(code, 0, out)
        with tempfile.TemporaryDirectory() as d:
            for f in ("a.md", "b.md"):
                shutil.copy(os.path.join(FIX, "project", f), d)
            with open(os.path.join(d, "a.md"), "a") as fh:
                fh.write("S2  Duplicate. [owner]\n")
            code, out = run("lint", d)
            self.assertEqual(code, 1)
            self.assertIn("duplicate S2", out)

    def test_lint_replaced_by_must_exist(self):
        with tempfile.TemporaryDirectory() as d:
            shutil.copy(os.path.join(FIX, "project", "a.md"), d)
            code, out = run("lint", d)
            self.assertEqual(code, 1)
            self.assertIn("replacement S2 missing", out)

    def test_depth_past_five_ok(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as fh:
            ids = ["S1", "S1.1", "S1.1.1", "S1.1.1.1", "S1.1.1.1.1", "S1.1.1.1.1.1"]
            fh.write("".join(f"{i}  x. [owner]\n" for i in ids))
        try:
            code, out = run("lint", fh.name)
            self.assertEqual(code, 0, out)
            self.assertIn("depth=6", out)
        finally:
            os.unlink(fh.name)

    def test_lint_missing_path(self):
        code, out = run("lint", os.path.join(FIX, "nope.md"))
        self.assertEqual(code, 1)
        self.assertIn("not found", out)


class CoverTest(unittest.TestCase):
    def test_cover_ok(self):
        code, out = run("cover", os.path.join(FIX, "closed.md"), os.path.join(FIX, "plan_ok.md"))
        self.assertEqual((code, out), (0, ""))

    def test_cover_gaps(self):
        code, out = run("cover", os.path.join(FIX, "closed.md"), os.path.join(FIX, "plan_gaps.md"))
        self.assertEqual(code, 1)
        self.assertIn("uncited S1.1\n", out)
        self.assertIn("task 2 cites nothing", out)
        self.assertIn("task 3 cites unknown S9", out)

    def test_cover_ignores_rejected(self):
        _, out = run("cover", os.path.join(FIX, "closed.md"), os.path.join(FIX, "plan_gaps.md"))
        self.assertNotIn("S1.2", out)

    def test_cover_parent_cited_covers_nothing_else(self):
        _, out = run("cover", os.path.join(FIX, "closed.md"), os.path.join(FIX, "plan_gaps.md"))
        self.assertEqual([l for l in out.splitlines() if l.startswith("uncited")], ["uncited S1.1"])


if __name__ == "__main__":
    unittest.main()
