"""The lock file is only useful if the exported pins still match it.

`uv lock` pins the toolchain; `uv export` writes the same pins into
yuyu-book/requirements.txt, which is what CI installs. Editing one half by hand
would let a runner build the book with versions no one tested locally, so the
two files are compared here and by `python scripts/bookctl.py doctor`.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import bookctl  # noqa: E402


class DependencyLock(unittest.TestCase):
    def test_requirements_export_matches_the_lock(self):
        self.assertEqual(bookctl.dependency_problems(), [])

    def test_every_direct_dependency_is_pinned_to_the_exported_version(self):
        pins, problems = bookctl.read_requirements()
        self.assertEqual(problems, [])
        self.assertTrue(bookctl.direct_requirements())
        for spec in bookctl.direct_requirements():
            match = bookctl.NAME.match(spec)
            self.assertIsNotNone(match, f"direct dependency is not pinned: {spec}")
            name = bookctl.norm(match.group("name"))
            self.assertIn(name, pins, spec)
            self.assertEqual(pins[name], match.group("version"), spec)

    def test_the_lock_does_not_pretend_the_book_is_an_installed_package(self):
        self.assertNotIn(bookctl.norm(bookctl.project_name()), bookctl.read_lock())


if __name__ == "__main__":
    unittest.main()
