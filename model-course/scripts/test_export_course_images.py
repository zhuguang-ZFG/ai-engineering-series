import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "llm"))
from export_course import image_name


class CourseImageCacheTests(unittest.TestCase):
    """A restyled figure must never be shadowed by an older render of the same stem."""

    def test_svg_name_changes_with_content(self):
        with tempfile.TemporaryDirectory() as folder:
            svg = Path(folder) / "context-selection.svg"
            svg.write_text('<svg stroke="#d3efd9"/>', encoding="utf-8")
            first = image_name(svg)
            svg.write_text('<svg stroke="#f0e9d8"/>', encoding="utf-8")
            second = image_name(svg)
        self.assertNotEqual(first, second)
        self.assertTrue(first.startswith("context-selection-") and first.endswith(".png"))

    def test_svg_name_is_stable_for_unchanged_content(self):
        with tempfile.TemporaryDirectory() as folder:
            svg = Path(folder) / "cover.svg"
            svg.write_text("<svg/>", encoding="utf-8")
            self.assertEqual(image_name(svg), image_name(svg))

    def test_raster_keeps_its_stem(self):
        with tempfile.TemporaryDirectory() as folder:
            png = Path(folder) / "photo.png"
            png.write_bytes(b"png")
            self.assertEqual(image_name(png), "photo.png")


if __name__ == "__main__":
    unittest.main()
