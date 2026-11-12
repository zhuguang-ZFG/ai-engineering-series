"""The collected edition must merge every shipped book without rewriting it."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import re
import zipfile

import fitz

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("series_collected",
                                              ROOT / "scripts/collected.py")
collected = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(collected)


def tiny_pdf(path: Path, title: str, pages: int = 2, headings=("第一篇 · 起点",)) -> None:
    """A stand-in book: cover page, body pages and its own outline."""
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = fitz.open()
    font = fitz.Font("cjk")
    for index in range(pages):
        page = doc.new_page(width=420, height=595)
        writer = fitz.TextWriter(page.rect)
        writer.append((40, 80), f"{title} 第 {index + 1} 页", font=font, fontsize=12)
        writer.write_text(page)
    toc = [[1, heading, 1] for heading in headings]
    toc.append([2, f"{title} 小节", 2])
    doc.set_toc(toc)
    doc.save(path)
    doc.close()


def tiny_epub(path: Path, title: str, *, ghost: bool = False) -> None:
    """A stand-in EPUB3: nav, two chapters and one stylesheet."""
    path.parent.mkdir(parents=True, exist_ok=True)
    opf = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" '
        'unique-identifier="book-id">\n'
        '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">'
        '<dc:identifier id="book-id">urn:uuid:fixture</dc:identifier>'
        f'<dc:title>{title}</dc:title><dc:language>zh</dc:language></metadata>\n'
        '<manifest>'
        '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>'
        '<item id="ch1" href="ch1.xhtml" media-type="application/xhtml+xml"/>'
        '<item id="ch2" href="ch2.xhtml" media-type="application/xhtml+xml"/>'
        '<item id="css" href="book.css" media-type="text/css"/>'
        '</manifest>\n'
        f'<spine><itemref idref="ch1"/><itemref idref="{"ghost" if ghost else "ch2"}"/></spine>\n'
        '</package>\n')
    page = ('<?xml version="1.0" encoding="utf-8"?>\n'
            '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh"><head>'
            '<title>%s</title><link rel="stylesheet" href="book.css"/></head>'
            '<body><h1>%s</h1></body></html>\n')
    nav = ('<?xml version="1.0" encoding="utf-8"?>\n'
           '<html xmlns="http://www.w3.org/1999/xhtml" '
           'xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="zh"><head>'
           '<title>目录</title></head><body><nav epub:type="toc"><ol>'
           '<li><a href="ch1.xhtml">第一章</a></li></ol></nav></body></html>\n')
    container = ('<?xml version="1.0" encoding="utf-8"?>\n'
                 '<container version="1.0" '
                 'xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
                 '<rootfiles><rootfile full-path="EPUB/package.opf" '
                 'media-type="application/oebps-package+xml"/></rootfiles></container>\n')
    files = [("mimetype", "application/epub+zip"),
             ("META-INF/container.xml", container),
             ("EPUB/package.opf", opf),
             ("EPUB/nav.xhtml", nav),
             ("EPUB/ch1.xhtml", page % ("一", "第一章")),
             ("EPUB/ch2.xhtml", page % ("二", "第二章")),
             ("EPUB/book.css", "body{font-family:serif}\n")]
    with zipfile.ZipFile(path, "w") as archive:
        for name, data in files:
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = (zipfile.ZIP_STORED if name == "mimetype"
                                  else zipfile.ZIP_DEFLATED)
            archive.writestr(info, data)


class CollectedTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        shutil.copyfile(ROOT / "series.json", self.root / "series.json")
        self.catalog = json.loads((self.root / "series.json").read_text(encoding="utf-8"))
        for book in self.catalog["books"]:
            pdf = self.book_path(book)
            self.book_path(book).parent.mkdir(parents=True, exist_ok=True)
            tiny_pdf(pdf, book["title"])
            tiny_epub(pdf.with_suffix(".epub"), book["title"])

    def book_path(self, book) -> Path:
        if book["project"] == "agent-books":
            return (self.root / "agent-books" / "yuyu-book" / "dist"
                    / f'{book["artifact_prefix"]}-zh.pdf')
        return self.root / "model-course" / "deliverables" / "llm-course.pdf"

    def build(self):
        return collected.build_pdf(self.root, lang="zh", date="2026-11-12")

    def test_every_volume_is_merged_behind_its_own_divider(self):
        manifest = self.build()
        self.assertEqual([volume["no"] for volume in manifest["volumes"]],
                         list(f"{collected.volume_label(i)}" for i in range(10)))
        pages = [volume["source_pages"] for volume in manifest["volumes"]]
        expected = manifest["front_pages"] + sum(1 + count for count in pages)
        self.assertEqual(manifest["total_pages"], expected)

        output = fitz.open(self.root / "dist" / manifest["output"])
        self.addCleanup(output.close)
        self.assertEqual(output.page_count, expected)
        for volume in manifest["volumes"]:
            divider = output[volume["divider_page"] - 1]
            text = divider.get_text()
            self.assertIn(volume["no"], text)
            self.assertIn(volume["title"], text)
            self.assertIn(volume["title"], output[volume["content_start"] - 1].get_text())

    def test_contents_and_outline_point_at_the_merged_pages(self):
        manifest = self.build()
        output = fitz.open(self.root / "dist" / manifest["output"])
        self.addCleanup(output.close)

        outline = output.get_toc()
        self.assertEqual(outline[0][0], 1)
        self.assertEqual(outline[0][2], manifest["volumes"][0]["divider_page"])
        self.assertEqual(sum(1 for entry in outline if entry[0] == 1), 10)
        self.assertEqual(sum(1 for entry in outline if entry[0] == 2), 10)
        self.assertEqual(sum(1 for entry in outline if entry[0] == 3), 10)

        links = []
        for number in range(1, manifest["front_pages"]):
            links.extend(page_link["page"] for page_link in output[number].get_links()
                         if page_link.get("kind") == fitz.LINK_GOTO)
        self.assertEqual(sorted(links),
                         sorted(volume["divider_page"] - 1 for volume in manifest["volumes"]))

        contents = "".join(output[number].get_text() for number in range(1, manifest["front_pages"]))
        for volume in manifest["volumes"]:
            self.assertIn(volume["title"], contents)

    def test_manifest_records_sources_and_stays_byte_stable(self):
        first = self.build()
        second = self.build()
        self.assertEqual(first["sha256"], second["sha256"])
        for record in first["volumes"]:
            source = self.root / record["source"]
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            self.assertEqual(record["source_sha256"], digest)
            self.assertGreater(record["content_start"], record["divider_page"])
        stored = json.loads((self.root / "dist" / first["output"].replace(".pdf", ".json"))
                            .read_text(encoding="utf-8"))
        self.assertEqual(stored["sha256"], first["sha256"])
        self.assertEqual(len(stored["volumes"]), 10)

    def test_merged_epub_keeps_every_book_package(self):
        manifest = collected.build_epub(self.root, lang="zh", date="2026-11-12")
        path = self.root / "dist" / manifest["output"]
        checked = collected.verify_epub(path)
        self.assertEqual(checked["volumes"], 10)
        self.assertEqual(manifest["spine_items"], 32)
        self.assertEqual(checked["spine_items"], 32)
        with zipfile.ZipFile(path) as archive:
            self.assertEqual(archive.namelist()[0], "mimetype")
            self.assertIn("EPUB/v01/EPUB/ch1.xhtml", archive.namelist())
            self.assertIn("EPUB/v10/EPUB/book.css", archive.namelist())
            package = archive.read("EPUB/package.opf").decode("utf-8")
        self.assertIn("十卷合订本", package)
        self.assertEqual(package.count('properties="nav"'), 1)
        spine = re.findall(r'<itemref idref="([^"]+)"/>', package)
        self.assertEqual(spine[2], "divider01")
        self.assertEqual(spine[3], "v01-ch1")
        self.assertEqual(spine[spine.index("divider02") + 1], "v02-ch1")
        self.assertEqual(spine[-1], "v10-ch2")

    def test_merged_epub_is_byte_stable(self):
        first = collected.build_epub(self.root, lang="zh", date="2026-11-12")
        second = collected.build_epub(self.root, lang="zh", date="2026-11-12")
        self.assertEqual(first["sha256"], second["sha256"])

    def test_missing_epub_names_the_book(self):
        missing = self.catalog["books"][-1]
        self.book_path(missing).with_suffix(".epub").unlink()
        with self.assertRaises(FileNotFoundError) as caught:
            collected.build_epub(self.root, lang="zh", date="2026-11-12")
        self.assertIn(missing["id"], str(caught.exception))

    def test_verifier_rejects_a_dangling_spine_reference(self):
        path = self.root / "broken.epub"
        tiny_epub(path, "损坏的册", ghost=True)
        with self.assertRaises(ValueError) as caught:
            collected.verify_epub(path)
        self.assertIn("ghost", str(caught.exception))

    def test_nav_may_only_link_spine_items(self):
        manifest = collected.build_epub(self.root, lang="zh", date="2026-11-12")
        path = self.root / "dist" / manifest["output"]
        collected.verify_epub(path)
        with zipfile.ZipFile(path) as archive:
            entries = [(info, archive.read(info.filename)) for info in archive.infolist()]
            nav = archive.read("EPUB/nav.xhtml").decode("utf-8")
        self.assertNotIn("本卷目录", nav)
        self.assertNotIn("nav.xhtml", nav)
        poisoned = nav.replace("</ol>", '<li><a href="v01/EPUB/book.css">样式</a></li></ol>', 1)
        data = {info.filename: payload for info, payload in entries}
        data["EPUB/nav.xhtml"] = poisoned.encode("utf-8")
        broken = path.with_name("poisoned.epub")
        with zipfile.ZipFile(broken, "w") as archive:
            for info, payload in entries:
                archive.writestr(info, data[info.filename])
        with self.assertRaises(ValueError) as caught:
            collected.verify_epub(broken)
        self.assertIn("not in spine", str(caught.exception))

    def test_verifier_reads_the_merged_pdf_back(self):
        manifest = self.build()
        checked = collected.verify_pdf(self.root / "dist" / manifest["output"], manifest)
        self.assertEqual(checked["pages"], manifest["total_pages"])
        self.assertEqual(checked["volumes"], 10)
        tampered = dict(manifest, total_pages=manifest["total_pages"] + 1)
        with self.assertRaises(ValueError):
            collected.verify_pdf(self.root / "dist" / manifest["output"], tampered)

    def test_missing_artifact_names_the_book_to_build(self):
        missing = self.catalog["books"][0]
        self.book_path(missing).unlink()
        with self.assertRaises(FileNotFoundError) as caught:
            self.build()
        self.assertIn(missing["id"], str(caught.exception))

    def test_language_without_edition_is_rejected(self):
        with self.assertRaises(ValueError) as caught:
            collected.build_pdf(self.root, lang="en", date="2026-11-12")
        self.assertIn("en", str(caught.exception))

    def test_link_action_rebuilds_internal_named_links(self):
        names = {"ch01": {"page": 3, "to": (12.0, 34.0)}}
        link = {"kind": fitz.LINK_NAMED, "nameddest": "ch01"}
        self.assertEqual(collected._link_action(link, names), ("goto", 3))
        missing = {"kind": fitz.LINK_NAMED, "nameddest": "nope"}
        self.assertEqual(collected._link_action(missing, names), ("delete", 0))
        launch = {"kind": fitz.LINK_LAUNCH, "file": "c:/tmp/x.html"}
        goto_file = {"kind": fitz.LINK_GOTOR, "file": "c:/tmp/x.html"}
        self.assertEqual(collected._link_action(launch, names), ("delete", 0))
        self.assertEqual(collected._link_action(goto_file, names), ("delete", 0))
        self.assertIsNone(collected._link_action(
            {"kind": fitz.LINK_URI, "uri": "https://example.com"}, names))

    def test_merged_pdf_keeps_no_machine_local_file_links(self):
        manifest = self.build()
        output = fitz.open(self.root / "dist" / manifest["output"])
        self.addCleanup(output.close)
        kinds = [link["kind"] for page in output for link in page.get_links()]
        self.assertNotIn(fitz.LINK_GOTOR, kinds)
        self.assertNotIn(fitz.LINK_LAUNCH, kinds)
        self.assertEqual(manifest["file_links_removed"], 0)

if __name__ == "__main__":
    unittest.main()

    def test_link_action_rebuilds_internal_named_links(self):
        names = {"ch01": {"page": 3, "to": (12.0, 34.0)}}
        link = {"kind": fitz.LINK_NAMED, "nameddest": "ch01"}
        self.assertEqual(collected._link_action(link, names), ("goto", 3))
        missing = {"kind": fitz.LINK_NAMED, "nameddest": "nope"}
        self.assertEqual(collected._link_action(missing, names), ("delete", 0))
        launch = {"kind": fitz.LINK_LAUNCH, "file": "c:/tmp/x.html"}
        goto_file = {"kind": fitz.LINK_GOTOR, "file": "c:/tmp/x.html"}
        self.assertEqual(collected._link_action(launch, names), ("delete", 0))
        self.assertEqual(collected._link_action(goto_file, names), ("delete", 0))
        self.assertIsNone(collected._link_action(
            {"kind": fitz.LINK_URI, "uri": "https://example.com"}, names))

    def test_merged_pdf_has_no_machine_local_file_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_fixture(root)
            manifest = collected.build_pdf(root, lang="zh", date="2026-11-12")
            path = root / "dist" / manifest["output"]
            doc = fitz.open(path)
            try:
                kinds = [link["kind"] for page in doc for link in page.get_links()]
                self.assertNotIn(fitz.LINK_GOTOR, kinds)
                self.assertNotIn(fitz.LINK_LAUNCH, kinds)
                self.assertEqual(manifest["file_links_removed"], 0)
            finally:
                doc.close()
            checked = collected.verify_pdf(path, manifest)
            self.assertGreaterEqual(checked["pages"], 1)
