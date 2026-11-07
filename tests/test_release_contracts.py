"""Release preflight is cheap and must fail closed before anything is built.

A full ``assemble()`` compiles both editions and the videos, so these tests
cover only the guards that run before the first subprocess: a version that
disagrees with the canonical manifest and an already existing destination.
Both must return 2 and leave the filesystem untouched.
"""
from __future__ import annotations

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_reports  # noqa: E402
import release  # noqa: E402


def canonical_version() -> str:
    manifest = json.loads((ROOT / "yuyu-book/manifest.json")
                          .read_text(encoding="utf-8"))
    return manifest["version"]


def assemble(version, destination):
    with contextlib.redirect_stdout(io.StringIO()), \
            contextlib.redirect_stderr(io.StringIO()):
        return release.assemble(version, str(destination))


class ReleasePreflight(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="release-preflight-")
        self.addCleanup(temporary.cleanup)
        self.tmp = Path(temporary.name)

    def test_version_mismatch_returns_2_before_creating_anything(self):
        destination = self.tmp / "not-created" / "release"
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = release.assemble(canonical_version() + "-mismatch",
                                    str(destination))
        self.assertEqual(code, 2)
        self.assertIn("differs from canonical", stderr.getvalue())
        self.assertFalse(destination.exists())
        self.assertFalse(destination.parent.exists())
        self.assertEqual(list(self.tmp.iterdir()), [])

    def test_existing_destination_is_refused_without_touching_it(self):
        destination = self.tmp / "release"
        destination.mkdir()
        sentinel = destination / "keep.txt"
        sentinel.write_text("pre-existing", encoding="utf-8")
        self.assertEqual(assemble(canonical_version(), destination), 2)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "pre-existing")
        self.assertEqual([path.name for path in destination.iterdir()],
                         ["keep.txt"])
        self.assertEqual([path for path in self.tmp.iterdir()
                          if path.name.startswith("yuyu-release-")], [])

    def test_cli_refuses_a_mismatched_version(self):
        destination = self.tmp / "cli-release"
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/release.py"),
             "--version", canonical_version() + "-mismatch",
             "--out-dir", str(destination)],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("differs from canonical", result.stderr)
        self.assertFalse(destination.exists())


class ChecksumManifest(unittest.TestCase):
    def test_sha256sums_lines_are_sorted_and_well_formed(self):
        with tempfile.TemporaryDirectory(prefix="release-sums-") as tmp:
            staged = Path(tmp)
            (staged / "nested").mkdir()
            (staged / "empty").mkdir()
            payloads = {
                "b.pdf": b"%PDF-1.7",
                "a.html": b"<html/>",
                "nested/c.epub": b"PK",
            }
            for name, payload in payloads.items():
                (staged / name).write_bytes(payload)

            lines = release.checksum_lines(staged).splitlines()
            self.assertEqual([line[66:] for line in lines],
                             ["a.html", "b.pdf", "nested/c.epub"])
            for line in lines:
                self.assertRegex(line, r"^[0-9a-f]{64}  [^/\\].*$")
                self.assertEqual(line[:64],
                                 build_reports.digest(staged / line[66:]))

            empty = staged / "empty"
            self.assertEqual(release.checksum_lines(empty), "")


if __name__ == "__main__":
    unittest.main()
