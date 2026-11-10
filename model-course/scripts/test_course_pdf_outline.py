import sys
import tempfile
import unittest
from pathlib import Path

import fitz
from lxml import etree

sys.path.insert(0, str(Path(__file__).resolve().parent / "llm"))
from export_course import find_outline_page, print_with_pages, repair_outline_titles


class CourseOutlineTests(unittest.TestCase):
    def body(self, headings):
        body = etree.Element("body")
        for level, title in headings:
            etree.SubElement(body, f"h{level}").text = title
        return body

    def document(self, headings):
        document = fitz.open()
        self.addCleanup(document.close)
        document.new_page()
        document.new_page()
        document.set_toc([
            [level, title, 1 + index % 2, {"kind": fitz.LINK_GOTO, "page": index % 2, "to": fitz.Point(20, 40 + index)}]
            for index, (level, title) in enumerate(headings)
        ])
        return document

    def test_linux_repeated_titles_keep_every_destination_and_level(self):
        headings = [(1, "怎么读这本书"), (2, "一条线，五种读法"), (1, "目录"), (1, "全书地图"), (1, "S1 会使用")]
        generated = [(level, title * (2 if index in {0, 2, 3} else 1)) for index, (level, title) in enumerate(headings)]
        document = self.document(generated)
        before = document.get_toc(simple=False)
        self.assertEqual(repair_outline_titles(document, self.body(headings)), 3)
        after = document.get_toc(simple=False)
        self.assertEqual([row[1] for row in after], [title for _, title in headings])
        self.assertEqual([(row[0], *row[2:]) for row in after], [(row[0], *row[2:]) for row in before])
        self.assertEqual(len(document), 2)
        self.assertEqual(find_outline_page(document.get_toc(), "全书地图"), 2)

    def test_legitimate_repetition_is_not_shortened_and_nested_titles_are_repaired(self):
        headings = [(1, "看看"), (2, "再试一次"), (3, "A B")]
        document = self.document([(1, "看看"), (2, "再试一次" * 3), (3, "A B A B")])
        self.assertEqual(repair_outline_titles(document, self.body(headings)), 2)
        self.assertEqual(document.get_toc(), [[1, "看看", 1], [2, "再试一次", 2], [3, "A B", 1]])
        self.assertEqual(repair_outline_titles(document, self.body(headings)), 0)

    def test_wrapped_heading_requires_the_complete_rendered_first_line_at_its_destination(self):
        first_line = "C03 Check: Why plausible"
        expected = first_line + " can still be wrong"
        document = self.document([(1, first_line + expected)])
        document[0].insert_text((20, 70), first_line + "\ncan still be wrong", fontsize=12)
        document.set_toc_item(0, kind=fitz.LINK_GOTO, pno=1, to=fitz.Point(21, 60))
        before = document.get_toc(simple=False)[0][2:]
        self.assertEqual(repair_outline_titles(document, self.body([(1, expected)])), 1)
        self.assertEqual(document.get_toc()[0][1], expected)
        self.assertEqual(document.get_toc(simple=False)[0][2:], before)

        for actual, point in [
            ("C03 Check:" + expected, fitz.Point(21, 60)),
            (first_line + expected, fitz.Point(21, 200)),
            (first_line + expected.replace("wrong", "right"), fitz.Point(21, 60)),
        ]:
            with self.subTest(actual=actual, point=point):
                document.set_toc_item(0, title=actual, kind=fitz.LINK_GOTO, pno=1, to=point)
                before = document.get_toc(simple=False)
                with self.assertRaises(AssertionError):
                    repair_outline_titles(document, self.body([(1, expected)]))
                self.assertEqual(document.get_toc(simple=False), before)

    def test_unexpected_titles_levels_or_missing_headings_fail_before_any_repair(self):
        source = [(1, "目录"), (2, "概念")]
        for generated in [
            [(1, "目录目录"), (2, "错误标题")],
            [(1, "目录目录"), (1, "概念")],
            [(1, "目录目录")],
            [(1, "目录目录"), (2, "概念概")],
        ]:
            with self.subTest(generated=generated):
                document = self.document(generated)
                before = document.get_toc(simple=False)
                with self.assertRaises(AssertionError):
                    repair_outline_titles(document, self.body(source))
                self.assertEqual(document.get_toc(simple=False), before)

    def test_printed_contents_converge_and_repaired_bookmarks_are_saved(self):
        body = self.body([(1, "目录"), (1, "全书地图")])
        etree.SubElement(body, "span", {"data-toc-id": "map"}).text = "000"
        fixture = self.document([(1, "目录目录"), (1, "全书地图全书地图")]).tobytes()

        class BrowserPage:
            def goto(self, uri):
                pass

            def evaluate(self, script):
                return True

            def pdf(self, **options):
                Path(options["path"]).write_bytes(fixture)

        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "book.html"
            target = Path(directory) / "book.pdf"
            pages, passes, total = print_with_pages(
                BrowserPage(), "测试书", body, source, target,
                [{"id": "map", "heading": "全书地图"}],
            )
            self.assertEqual((pages, passes, total), ({"map": 2}, 2, 2))
            self.assertEqual(body.xpath('.//*[@data-toc-id="map"]')[0].text, "2")
            with fitz.open(target) as document:
                self.assertEqual(document.get_toc(), [[1, "目录", 1], [1, "全书地图", 2]])


if __name__ == "__main__":
    unittest.main()
