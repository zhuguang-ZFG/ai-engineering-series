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

    def test_build_report_only_claims_the_product_that_was_built(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            for name in ("yuyu-pi-zh.html", "yuyu-codex-zh.epub"):
                (folder / name).write_text("fixture", encoding="utf-8")
            with mock.patch.object(bookctl, "run"), \
                    mock.patch.object(build_reports, "write_reports") as writer:
                self.assertEqual(bookctl.build(self.arguments(folder, epub=False)), 0)
            self.assertEqual([path.name for path in writer.call_args.args[2]],
                             ["yuyu-pi-zh.html"])
            with mock.patch.object(bookctl, "run"), \
                    mock.patch.object(build_reports, "write_reports") as writer:
                self.assertEqual(bookctl.build(self.arguments(folder, check=True)), 0)
            self.assertEqual(writer.call_args.args[2], [])

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

    def test_agent_volumes_keep_their_own_manifest_and_epub_prefix(self):
        for product in ("opencode", "deepseek", "hermes", "codex"):
            with self.subTest(product=product), tempfile.TemporaryDirectory() as temporary:
                folder = Path(temporary)
                commands = []

                def fake_run(command):
                    commands.append(command)
                    if "scripts/build_epub.py" in command:
                        output = Path(command[command.index("--output") + 1])
                        output.write_bytes(b"PK fixture")
                    else:
                        (folder / f"yuyu-{product}-zh.html").write_text("<html/>")

                with mock.patch.object(bookctl, "run", side_effect=fake_run), \
                        mock.patch.object(build_reports, "write_reports"):
                    self.assertEqual(bookctl.build(self.arguments(folder, product=product)), 0)
                self.assertEqual(len(commands), 2)
                self.assertIn(f"manifest-{product}.json", commands[0])
                self.assertIn(f"sources-{product}.json", commands[0])
                self.assertEqual(commands[0][commands[0].index("--lang") + 1], "zh")
                self.assertIn(str(folder / f"yuyu-{product}-zh.epub"), commands[1])

    def test_agent_volumes_reject_unavailable_english_before_running(self):
        for product in ("opencode", "deepseek", "hermes", "codex"):
            with self.subTest(product=product), mock.patch.object(bookctl, "run") as run:
                self.assertEqual(bookctl.build(self.arguments("unused", product=product, lang="en")), 2)
                run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
