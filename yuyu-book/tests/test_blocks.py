"""Block markers: syntax, ownership, uniqueness, and fence safety.

The marker is a comment, so a malformed one is invisible in the rendered book
until a registry entry points at nothing. Validation therefore runs while the
unit is loaded, not when a reference happens to be consumed.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from yuyu_book.blocks import parse_blocks, validate_markers  # noqa: E402
from yuyu_book.core import BuildError  # noqa: E402

MARK = "<!-- block: {0} -->"


def doc(*lines: str) -> str:
    return "# Title\n\n" + "\n".join(lines) + "\n"


class Markers(unittest.TestCase):
    def test_marker_maps_to_its_following_block(self):
        text = doc("intro", "", MARK.format("ch01.agent-harness"),
                   "body", "", "tail")
        self.assertEqual(validate_markers(text, "ch01.md", "ch01"),
                         {"ch01.agent-harness": 5})

    def test_blank_lines_between_marker_and_block_are_allowed(self):
        text = doc(MARK.format("ch01.tool-call"), "", "", "body")
        self.assertEqual(validate_markers(text, "ch01.md", "ch01"),
                         {"ch01.tool-call": 3})

    def test_marker_inside_a_fence_is_an_example(self):
        text = doc("```md", MARK.format("ch01.not-real"), "```",
                   MARK.format("ch01.real"), "body")
        self.assertEqual(validate_markers(text, "ch01.md", "ch01"),
                         {"ch01.real": 6})

    def test_closing_fence_must_match_the_opening(self):
        text = doc("~~~", "code", "```", MARK.format("ch01.still-code"),
                   "~~~", MARK.format("ch01.real"), "body")
        self.assertEqual(validate_markers(text, "ch01.md", "ch01"),
                         {"ch01.real": 8})

    def test_malformed_marker_is_refused(self):
        text = doc("<!-- block ch01.typo -->", "body")
        with self.assertRaises(BuildError) as raised:
            validate_markers(text, "ch01.md", "ch01")
        self.assertIn("error block-marker ch01.md -", str(raised.exception))

    def test_marker_must_belong_to_its_unit(self):
        text = doc(MARK.format("ch02.elsewhere"), "body")
        with self.assertRaises(BuildError) as raised:
            validate_markers(text, "ch01.md", "ch01")
        self.assertIn("block-id", str(raised.exception))

    def test_slug_must_be_lowercase(self):
        text = doc(MARK.format("ch01.NotSlug"), "body")
        with self.assertRaises(BuildError):
            validate_markers(text, "ch01.md", "ch01")

    def test_duplicate_id_is_refused(self):
        text = doc(MARK.format("ch01.same"), "one", "",
                   MARK.format("ch01.same"), "two")
        with self.assertRaises(BuildError) as raised:
            validate_markers(text, "ch01.md", "ch01")
        self.assertIn("duplicate", str(raised.exception))

    def test_dangling_marker_is_refused(self):
        text = doc(MARK.format("ch01.dangling"))
        with self.assertRaises(BuildError) as raised:
            validate_markers(text, "ch01.md", "ch01")
        self.assertIn("not followed by a block", str(raised.exception))

    def test_two_markers_cannot_share_a_block(self):
        text = doc(MARK.format("ch01.one"), MARK.format("ch01.two"), "body")
        with self.assertRaises(BuildError) as raised:
            validate_markers(text, "ch01.md", "ch01")
        self.assertIn("same block", str(raised.exception))


class Parsing(unittest.TestCase):
    def spans(self, text):
        return [(b.kind, b.line, b.end_line, b.block_id, b.text)
                for b in parse_blocks(text, "ch01", "zh")]

    def test_paragraphs_split_on_blank_lines(self):
        text = "intro\nstill intro\n\nsecond\n"
        self.assertEqual([(k, a, b) for k, a, b, _, _ in self.spans(text)],
                         [("paragraph", 1, 2), ("paragraph", 4, 4)])

    def test_heading_is_a_citable_span(self):
        text = "## 3.1 Tool loop\ntext\n"
        kind, start, end, _, body = self.spans(text)[0]
        self.assertEqual((kind, start, end), ("heading", 1, 1))
        self.assertEqual(body, "## 3.1 Tool loop")

    def test_marker_attaches_to_the_following_span(self):
        text = "\n<!-- block: ch01.span -->\n\nbody\n"
        kind, start, end, block_id, _ = self.spans(text)[0]
        self.assertEqual((kind, start, end, block_id),
                         ("paragraph", 4, 4, "ch01.span"))

    def test_list_stays_one_span(self):
        text = "- one\n- two\n  continuation\n\nnext\n"
        self.assertEqual([(k, a, b) for k, a, b, _, _ in self.spans(text)],
                         [("list", 1, 3), ("paragraph", 5, 5)])

    def test_table_and_quote_are_distinct_spans(self):
        text = "> quote\n> more\n\n| a | b |\n| --- | --- |\n"
        self.assertEqual([(k, a, b) for k, a, b, _, _ in self.spans(text)],
                         [("quote", 1, 2), ("table", 4, 5)])

    def test_fence_keeps_its_blank_lines_and_markers_inside(self):
        text = "```md\n<!-- block: ch01.not-a-marker -->\n\n```\nafter\n"
        spans = self.spans(text)
        self.assertEqual([(k, a, b) for k, a, b, _, _ in spans],
                         [("fence", 1, 4), ("paragraph", 5, 5)])
        self.assertEqual(spans[0][3], "")

    def test_fence_closes_only_on_a_matching_token(self):
        text = "~~~\ncode\n```\n~~~\nafter\n"
        self.assertEqual([(k, a, b) for k, a, b, _, _ in self.spans(text)],
                         [("fence", 1, 4), ("paragraph", 5, 5)])


if __name__ == "__main__":
    unittest.main()
