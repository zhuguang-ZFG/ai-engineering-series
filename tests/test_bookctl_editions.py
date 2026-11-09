"""Edition selection must stay consistent between HTML/PDF and EPUB passes."""
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import bookctl
import build_reports


class EditionBuild(unittest.TestCase):
    def arguments(self, folder, **overrides):
        values = dict(product="pi", lang="both", mermaid="source", pdf=True,
                      epub=True, out_dir=str(folder), check=False,
                      no_plain=False, regen_index=False)
        values.update(overrides)
        return argparse.Namespace(**values)

    def test_chinese_only_product_builds_one_epub_and_reports_it(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            commands = []

            def fake_run(command):
                commands.append(command)
                if "scripts/build_epub.py" in command:
                    output = Path(command[command.index("--output") + 1])
                    output.write_bytes(b"PK fixture")
                else:
                    (folder / "yuyu-pi-zh.html").write_text("<html/>")
                    (folder / "yuyu-pi-zh.pdf").write_bytes(b"%PDF fixture")

            with mock.patch.object(bookctl, "run", side_effect=fake_run), \
                    mock.patch.object(build_reports, "write_reports") as writer:
                self.assertEqual(bookctl.build(self.arguments(folder)), 0)
            self.assertEqual(len(commands), 2)
            for command in commands:
                self.assertEqual(command[command.index("--lang") + 1], "zh")
            self.assertEqual({path.suffix for path in writer.call_args.args[2]},
                             {".html", ".pdf", ".epub"})

    def test_epub_failure_cannot_report_a_successful_build(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            (folder / "yuyu-pi-zh.html").write_text("<html/>")

            def fake_run(command):
                if "scripts/build_epub.py" in command:
                    raise subprocess.CalledProcessError(7, command)

            with mock.patch.object(bookctl, "run", side_effect=fake_run), \
                    mock.patch.object(build_reports, "write_reports") as writer:
                self.assertEqual(bookctl.build(self.arguments(folder)), 7)
                writer.assert_not_called()

    def test_check_does_not_convert_a_stale_html_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            with mock.patch.object(bookctl, "run") as run, \
                    mock.patch.object(build_reports, "write_reports"):
                self.assertEqual(bookctl.build(self.arguments(temporary, check=True)), 0)
            self.assertEqual(run.call_count, 1)
            self.assertIn("--check", run.call_args.args[0])

    def test_unavailable_english_pi_edition_fails_before_running(self):
        with mock.patch.object(bookctl, "run") as run:
            self.assertEqual(bookctl.build(self.arguments("unused", lang="en")), 2)
            run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
