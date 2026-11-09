"""The build report is release evidence, so its contents are pinned here.

``write_reports`` used to receive only ``destination/*.html`` from
``bookctl.py build``; printed editions and nested site assets never reached
``artifact-manifest.json``. These tests cover status aggregation, artifact
collection (PDF/EPUB/nested), report self-exclusion, and the degradation to
"unverified" when the same code runs outside a git checkout.

The optional browser probe is forced to fail fast: these tests are about the
report contract, not about launching a real browser.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import bookctl  # noqa: E402
import build_reports  # noqa: E402


def offline_probe():
    """Make the Playwright import fail immediately instead of launching."""
    return mock.patch.dict(sys.modules, {"playwright": None,
                                        "playwright.sync_api": None})


class BuildReports(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="build-reports-")
        self.addCleanup(temporary.cleanup)
        self.tmp = Path(temporary.name)

    def write(self, out, steps, artifacts=()):
        with offline_probe():
            return build_reports.write_reports(out, steps, artifacts)

    def manifest(self, out):
        return json.loads((out / "artifact-manifest.json").read_text(encoding="utf-8"))

    def report(self, out):
        return json.loads((out / "build-report.json").read_text(encoding="utf-8"))

    def test_status_passes_only_when_every_step_succeeds(self):
        passed = self.write(self.tmp / "passed", [
            {"name": "fast", "command": ["python", "x"], "returncode": 0,
             "seconds": 0.25}])
        self.assertEqual(passed["status"], "passed")
        self.assertEqual(self.report(self.tmp / "passed")["status"], "passed")
        self.assertAlmostEqual(passed["elapsed_seconds"], 0.25)

        failed = self.write(self.tmp / "failed", [
            {"name": "ok", "command": ["a"], "returncode": 0, "seconds": 0.1},
            {"name": "bad", "command": ["b"], "returncode": 3, "seconds": 0.2}])
        self.assertEqual(failed["status"], "failed")
        self.assertEqual(self.report(self.tmp / "failed")["status"], "failed")
        self.assertEqual(failed["steps"][1]["returncode"], 3)

        self.assertEqual(self.write(self.tmp / "empty", [])["status"], "failed")

    def test_manifest_records_pdf_epub_and_nested_files(self):
        out = self.tmp / "dist"
        (out / "assets").mkdir(parents=True)
        payloads = {
            "yuyu-agent-harness-zh.html": b"<!doctype html>",
            "yuyu-agent-harness-zh.pdf": b"%PDF-1.7 fake",
            "yuyu-agent-harness-en.epub": b"PK fake",
            "assets/cover.svg": b"<svg/>",
        }
        for name, payload in payloads.items():
            (out / name).write_bytes(payload)
        artifacts = bookctl.report_artifacts(out)
        self.assertEqual(len(artifacts), len(payloads))

        self.write(out, [{"name": "book", "command": ["python"],
                          "returncode": 0, "seconds": 1.0}], artifacts)
        recorded = {entry["path"]: entry
                    for entry in self.manifest(out)["artifacts"]}
        self.assertEqual(set(recorded), set(payloads))
        for name, payload in payloads.items():
            self.assertEqual(recorded[name]["bytes"], len(payload), name)
            self.assertEqual(recorded[name]["sha256"],
                             build_reports.digest(out / name), name)
            self.assertFalse(Path(name).is_absolute(), name)
            self.assertNotIn("\\", name)

    def test_reports_do_not_list_themselves_as_artifacts(self):
        out = self.tmp / "dist"
        out.mkdir()
        (out / "book.pdf").write_bytes(b"%PDF")
        self.write(out, [{"name": "book", "command": ["x"],
                          "returncode": 0, "seconds": 0.1}])

        # The second pass sees the first pass's reports; they must be skipped.
        artifacts = bookctl.report_artifacts(out)
        self.assertIn(out / "build-report.json", artifacts)
        self.assertIn(out / "artifact-manifest.json", artifacts)
        self.write(out, [{"name": "book", "command": ["x"],
                          "returncode": 0, "seconds": 0.1}], artifacts)
        names = {entry["path"]
                 for entry in self.manifest(out)["artifacts"]}
        self.assertEqual(names, {"book.pdf"})

    def test_identity_degrades_outside_a_git_checkout(self):
        fake_root = self.tmp / "checkout"
        (fake_root / "yuyu-book").mkdir(parents=True)
        (fake_root / "yuyu-book" / "manifest.json").write_text(
            '{"version": "9.9.9"}\n', encoding="utf-8")
        out = fake_root / "reports"
        with mock.patch.object(build_reports, "ROOT", fake_root), \
                mock.patch.dict(os.environ,
                                {"GIT_CEILING_DIRECTORIES": str(self.tmp)}), \
                offline_probe():
            report = build_reports.write_reports(out, [
                {"name": "fast", "command": ["x"], "returncode": 0,
                 "seconds": 0.0}])
        manifest = self.manifest(out)
        self.assertIsNone(manifest["commit"])
        self.assertIsNone(manifest["working_tree"])
        self.assertEqual(manifest["locks_sha256"], {})
        self.assertEqual(report["version"], "9.9.9")

    def test_bookctl_build_hands_every_built_file_to_the_report(self):
        out = self.tmp / "dist"

        def fake_run(_command):
            (out / "assets").mkdir(parents=True, exist_ok=True)
            (out / "book.html").write_text("<html/>", encoding="utf-8")
            (out / "book.pdf").write_bytes(b"%PDF")
            (out / "assets" / "cover.svg").write_text("<svg/>", encoding="utf-8")

        arguments = argparse.Namespace(
            product="book", lang="zh", mermaid="render", pdf=True,
            out_dir=str(out), check=False, no_plain=False, regen_index=False)
        with mock.patch.object(bookctl, "run", side_effect=fake_run), \
                mock.patch.object(build_reports, "write_reports") as writer:
            self.assertEqual(bookctl.build(arguments), 0)
        artifacts = writer.call_args.args[2]
        self.assertEqual({path.name for path in artifacts},
                         {"book.html", "book.pdf", "cover.svg"})


if __name__ == "__main__":
    unittest.main()
