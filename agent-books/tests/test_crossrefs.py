"""Cross-volume references resolve visible headings after stable block markers."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "crossrefs_audit", ROOT / "docs/yuyu-overhaul/check_crossrefs.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class ChapterReferences(unittest.TestCase):
    def test_stable_marker_before_heading_keeps_reference_resolvable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            chapter = root / "ch16.md"
            chapter.write_text("<!-- block: omp-ch16.heading -->\n# 第16章 记忆系统\n", encoding="utf-8")
            book = root / "book.md"
            book.write_text("参见 omp 分册第 16 章《记忆系统》。\n", encoding="utf-8")
            with patch.object(audit, "ROOT", root), patch.object(audit, "BOOK_FILES", [book]):
                self.assertEqual(audit.check_book_to_omp(audit.titles([chapter])), ([], 1))

    def test_example_and_commented_headings_cannot_supply_missing_chapter(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            chapter = root / "example.md"
            chapter.write_text("<!--\n# 第16章 记忆系统\n-->\n```md\n# 第16章 记忆系统\n```\n", encoding="utf-8")
            book = root / "book.md"
            book.write_text("参见 omp 分册第 16 章《记忆系统》。\n", encoding="utf-8")
            with patch.object(audit, "ROOT", root), patch.object(audit, "BOOK_FILES", [book]):
                errors, count = audit.check_book_to_omp(audit.titles([chapter]))
            self.assertEqual(count, 1)
            self.assertEqual(errors, ["book.md:1 omp 无第 16 章"])


if __name__ == "__main__":
    unittest.main()
