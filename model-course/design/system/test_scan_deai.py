"""Exercise the scanner CLI with real files, including short narration inputs."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import scan_deai


SCRIPT = Path(scan_deai.__file__).resolve()


class CorpusTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def put(self, path, text, encoding="utf-8"):
        file = self.root / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(text, encoding=encoding)
        return file

    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args], cwd=self.root,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            capture_output=True, text=True, encoding="utf-8", check=False,
        )

    def test_zero_chinese_inputs_do_not_crash_or_change_sources(self):
        for name, text in [("empty.txt", ""), ("english.txt", "Read the log.\n"),
                           ("code.md", "```text\n至关重要\n```\n")]:
            with self.subTest(name=name):
                path = self.put(name, text)
                before = path.read_bytes()
                result = self.run_cli("--corpus", name, "--sites")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("0 汉字，缺陷 0 处", result.stdout)
                self.assertNotIn("nan", result.stdout.lower())
                self.assertNotIn("inf", result.stdout.lower())
                self.assertEqual(path.read_bytes(), before)

    def test_same_names_preserve_source_and_original_line_numbers(self):
        self.put("one/voice.md", "# 标题\n```text\n至关重要\n```\n赋能。\n")
        self.put("two/voice.md", "普通正文。\n至关重要。\n")
        result = self.run_cli("--corpus", "**/voice.md", "--sites", "--export", "sites.md")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("one/voice.md:5 C-AI高频词 赋能", result.stdout)
        self.assertIn("two/voice.md:2 C-AI高频词 至关重要", result.stdout)
        self.assertNotIn("voice.md:3", result.stdout)
        exported = (self.root / "sites.md").read_text(encoding="utf-8")
        self.assertIn("one/voice.md", exported)
        self.assertIn("two/voice.md", exported)
        self.assertIn("L5 [C-AI高频词] 赋能", exported)

    def test_glob_ignores_directories(self):
        (self.root / "folder.txt").mkdir()
        self.put("voice.txt", "赋能。")
        result = self.run_cli("--corpus", "*.txt")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("voice.txt", result.stdout)
        self.assertNotIn("folder.txt", result.stdout)

    def test_no_matching_files_reports_actionable_error(self):
        (self.root / "folder.txt").mkdir()
        result = self.run_cli("--corpus", "*.txt")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("matched no files", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_sort_and_top_limit_table_but_not_summary(self):
        self.put("a.txt", "赋能。")
        self.put("b.txt", "至关重要。无缝。" + "记录当天的观察结果。" * 15)
        result = self.run_cli("--corpus", "*.txt", "--sort", "total", "--top", "1")
        self.assertEqual(result.returncode, 0, result.stderr)
        table, summary = result.stdout.split("汇总：", 1)
        self.assertIn("b.txt", table)
        self.assertNotIn("a.txt", table)
        self.assertIn("缺陷 3 处", summary)

    def test_invalid_sort_and_negative_top_are_cli_errors(self):
        self.put("voice.txt", "赋能。")
        for option in [("--sort", "missing"), ("--top", "-1")]:
            with self.subTest(option=option):
                result = self.run_cli("--corpus", "*.txt", *option)
                self.assertEqual(result.returncode, 2)
                self.assertNotIn("Traceback", result.stderr)

    def test_bom_short_text_is_measured_without_book_size_gate(self):
        self.put("voice.txt", "赋能。", encoding="utf-8-sig")
        result = self.run_cli("--corpus", "voice.txt", "--sites")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("voice.txt:1 C-AI高频词 赋能", result.stdout)
        self.assertIn("2 汉字，缺陷 1 处", result.stdout)

    def test_book_sites_keep_absolute_line_numbers(self):
        text = "# 书\n\n### 检查\n赋能。\n" + ("雨落在窗前，读者翻开笔记，写下当天观察到的事情。" * 4 + "\n") * 12
        rows = scan_deai.scan(text)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["sites"], [(4, "C-AI高频词", "赋能", "赋能。")])


if __name__ == "__main__":
    unittest.main()
