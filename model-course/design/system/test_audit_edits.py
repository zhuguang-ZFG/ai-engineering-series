"""Audit real commits before and after the course moves into a parent repo."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import audit_edits


class HistoryPaths(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.course = self.root
        self.git("init", "--quiet")
        folder = self.root / "design/system"
        folder.mkdir(parents=True)
        source = Path(audit_edits.__file__).resolve().parent
        for name in ("audit_edits.py", "fences.py"):
            shutil.copyfile(source / name, folder / name)
        (self.root / "book").mkdir()
        self.write_book("original")
        self.commit("initial book")
        self.write_book("legacy edit")
        self.legacy = self.commit("deai: edit legacy code sample")

    def git(self, *args):
        return subprocess.run(
            ["git", "-c", "user.name=Audit fixture", "-c",
             "user.email=audit@example.invalid", "-c", "commit.gpgsign=false",
             "-c", "core.autocrlf=false", *args],
            cwd=self.root, capture_output=True, text=True,
            encoding="utf-8", check=True,
        ).stdout.strip()

    def write_book(self, sample):
        (self.course / "book/book.md").write_text(
            "# Heading\n\nOrdinary prose.\n\n```text\n" + sample + "\n```\n",
            encoding="utf-8",
        )

    def commit(self, subject):
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", subject)
        return self.git("rev-parse", "HEAD")

    def move_course(self):
        self.course = self.root / "model-course"
        self.course.mkdir()
        for folder in ("book", "design"):
            self.git("mv", folder, "model-course/" + folder)

    def run_audit(self, *commits):
        return subprocess.run(
            [sys.executable, "-B", str(self.course / "design/system/audit_edits.py"),
             *commits], cwd=self.root,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            capture_output=True, text=True, encoding="utf-8", check=False,
        )

    def assert_code_finding(self, result):
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("code 1 / table 0 / heading 0 / figure 0", result.stdout)
        self.assertIn("L6 [code]", result.stdout)

    def test_standalone_history_still_reports_protected_edit(self):
        self.assert_code_finding(self.run_audit(self.legacy))

    def test_old_and_prefixed_commits_work_after_directory_move(self):
        self.move_course()
        self.commit("move course")
        self.write_book("prefixed edit")
        current = self.commit("deai: edit moved code sample")
        for sha in (self.legacy, current):
            with self.subTest(sha=sha):
                self.assert_code_finding(self.run_audit(sha))

    def test_move_and_edit_compares_different_paths_in_parent_and_child(self):
        self.move_course()
        self.write_book("edited during move")
        moved = self.commit("deai: move and edit code sample")
        self.assert_code_finding(self.run_audit(moved))

    def test_default_discovery_finds_both_historical_paths(self):
        self.move_course()
        self.commit("move course")
        self.write_book("prefixed edit")
        current = self.commit("deai: edit moved code sample")
        result = self.run_audit()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(self.legacy[:7], result.stdout)
        self.assertIn(current[:7], result.stdout)
        self.assertEqual(result.stdout.count("L6 [code]"), 2)

    def test_bad_revision_cannot_report_a_clean_audit(self):
        result = self.run_audit("missing-revision")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("OK ", result.stdout)
        self.assertTrue(result.stderr)


if __name__ == "__main__":
    unittest.main()
