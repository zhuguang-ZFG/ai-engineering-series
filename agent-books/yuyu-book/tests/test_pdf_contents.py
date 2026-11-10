"""Contents numbering must include rows on every continuation page."""
from pathlib import Path
import sys
import unittest

import fitz

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from yuyu_book.core import BuildError
from yuyu_book.pdf import _contents_start


class ContentsHeadingTests(unittest.TestCase):
    def test_continuation_row_containing_title_does_not_skip_first_page(self):
        with fitz.open() as doc:
            for text in ("Book cover", "Contents\nChapter 1\nChapter 2",
                         "Chapter 3\nWorking with Contents", "Contents\nBody text"):
                doc.new_page().insert_text((72, 90), text)
            self.assertEqual(_contents_start(doc, "Contents", before=3), 1)

    def test_substring_without_a_heading_is_rejected(self):
        with fitz.open() as doc:
            doc.new_page().insert_text((72, 90), "Working with Contents")
            with self.assertRaisesRegex(BuildError, "contents pages not found"):
                _contents_start(doc, "Contents", before=1)


if __name__ == "__main__":
    unittest.main()
