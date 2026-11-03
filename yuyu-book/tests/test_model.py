"""The BookModel spine and the one diagnostic format.

Only the containers that exist are tested; terms, claims and video types join
when a product consumes them. The diagnostic format is a contract: every
builder phase prints the same five fields plus an optional hint.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from yuyu_book.model import (Block, BookModel, Diagnostic, Edition, Part,  # noqa: E402
                             Section, Unit)


class DiagnosticFormat(unittest.TestCase):
    def test_fields_are_space_separated(self):
        d = Diagnostic("error", "registry-version", "glosses.json", "-",
                       "schema_version 2 is newer than 1", "update yuyu-book")
        self.assertEqual(
            str(d),
            "error registry-version glosses.json - schema_version 2 is newer "
            "than 1 update yuyu-book")

    def test_empty_file_and_block_become_dashes(self):
        d = Diagnostic("warning", "unit-heading", "", "", "no H1")
        self.assertEqual(str(d), "warning unit-heading - - no H1")

    def test_hint_is_optional(self):
        d = Diagnostic("info", "check", "a.md", "ch01.intro", "done")
        self.assertEqual(str(d), "info check a.md ch01.intro done")

    def test_invalid_values_are_refused(self):
        with self.assertRaises(ValueError):
            Diagnostic("fatal", "code", "f", "-", "message")
        with self.assertRaises(ValueError):
            Diagnostic("error", "", "f", "-", "message")
        with self.assertRaises(ValueError):
            Diagnostic("error", "code", "f", "-", "")


class Spine(unittest.TestCase):
    def test_edition_part_unit_section_block_nest(self):
        block = Block("ch01", "zh", 12, "paragraph", "正文", "ch01.intro")
        section = Section(2, "第一节", 10, [block])
        unit = Unit("ch01", "chapter", "zh", "第一部分/01.md", "第一章",
                    [section])
        part = Part("p1", ["ch01"])
        edition = Edition("zh", [unit])
        model = BookModel({"zh": edition}, [part], [])
        self.assertIs(model.editions["zh"].units[0].sections[0].blocks[0],
                      block)
        self.assertEqual(model.parts[0].unit_ids, ["ch01"])
        self.assertEqual(block.block_id, "ch01.intro")

    def test_default_lists_are_not_shared(self):
        a, b = BookModel(), BookModel()
        a.parts.append(Part("p1"))
        a.diagnostics.append(Diagnostic("info", "x", "f", "-", "m"))
        self.assertEqual(b.parts, [])
        self.assertEqual(b.diagnostics, [])


if __name__ == "__main__":
    unittest.main()
