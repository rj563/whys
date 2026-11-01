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

    def test_lint_non_utf8_reports_line(self):
        with tempfile.NamedTemporaryFile("wb", suffix=".md", delete=False) as fh:
            fh.write(b"S1  ok. [owner]\nS2  caf\xe9. [owner]\n")
        try:
            code, out = run("lint", fh.name)
            self.assertEqual(code, 1)
            self.assertIn("L2: not UTF-8", out)
        finally:
            os.unlink(fh.name)

    def test_format_example_lints_clean(self):
        with open(os.path.join(ROOT, "skills", "drill", "format.md"), encoding="utf-8") as fh:
            block = fh.read().split("```")[1]
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as fh:
            fh.write(block)
        try:
            code, out = run("lint", fh.name)
            self.assertEqual(code, 0, out)
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
        self.assertNotIn("uncited S1.2", out)

    def test_cover_flags_citing_rejected_or_open(self):
        code, out = run("cover", os.path.join(FIX, "closed.md"), os.path.join(FIX, "plan_gaps.md"))
        self.assertIn("task 1 cites rejected S1.2", out)
        code, out = run("cover", os.path.join(FIX, "open.md"), os.path.join(FIX, "plan_open.md"))
        self.assertEqual(code, 1)
        self.assertIn("task 1 cites open S1.1", out)

    def test_cover_parent_cited_covers_nothing_else(self):
        _, out = run("cover", os.path.join(FIX, "closed.md"), os.path.join(FIX, "plan_gaps.md"))
        self.assertEqual([l for l in out.splitlines() if l.startswith("uncited")], ["uncited S1.1"])


class MissTest(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.mkdtemp()
        self.env = dict(os.environ, WHYS_HOME=os.path.join(self.home, "whys"))
        self.log = os.path.join(self.home, "whys", "misses.md")

    def tearDown(self):
        shutil.rmtree(self.home)

    def test_miss_creates_log(self):
        code, _ = run("miss", "proj", "S1.2", "edge-case", "lapped cars", env=self.env)
        self.assertEqual(code, 0)
        self.assertTrue(os.path.exists(self.log))

    def test_miss_appends_line_format(self):
        run("miss", "proj", "S1.2", "edge-case", "lapped cars", env=self.env)
        run("miss", "proj", "S1.3", "output", "column order", env=self.env)
        with open(self.log) as fh:
            lines = [l for l in fh.read().splitlines() if l.strip() and not l.startswith("#")]
        self.assertEqual(len(lines), 2)
        self.assertRegex(lines[0], r"^\d{4}-\d{2}-\d{2} \| proj \| S1\.2 \| edge-case \| lapped cars$")

    def test_miss_rejects_bad_id(self):
        code, _ = run("miss", "proj", "1.2", "edge-case", "x", env=self.env)
        self.assertEqual(code, 1)
        self.assertFalse(os.path.exists(self.log))

    def test_miss_normalizes_kind(self):
        run("miss", "p", "S1", "Edge Case", "a", env=self.env)
        _, out = run("kinds", env=self.env)
        self.assertTrue(any(l.startswith("edge-case 1") for l in out.splitlines()), out)

    def test_kinds_defaults_only(self):
        code, out = run("kinds", env=self.env)
        self.assertEqual(code, 0)
        kinds = [l.split()[0] for l in out.splitlines()]
        self.assertEqual(sorted(kinds), sorted(
            ["reference", "edge-case", "limits", "interaction", "output", "failure", "existing"]))

    def test_kinds_counts(self):
        run("miss", "p", "S1", "ui", "a", env=self.env)
        run("miss", "p", "S2", "ui", "b", env=self.env)
        run("miss", "p", "S3", "edge-case", "c", env=self.env)
        _, out = run("kinds", env=self.env)
        lines = out.splitlines()
        self.assertTrue(lines[0].startswith("ui 2"), out)
        self.assertTrue(any(l.startswith("edge-case 1") for l in lines), out)
        self.assertEqual(sum(l.split()[0] == "edge-case" for l in lines), 1)


if __name__ == "__main__":
    unittest.main()
