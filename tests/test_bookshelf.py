"""The versioned bookshelf must also work without ignored local artifacts."""
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("bookshelf", ROOT / "scripts/build_index.py")
bookshelf = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bookshelf)


class PortableBookshelf(unittest.TestCase):
    def prepare_root(self, root):
        (root / "series.json").write_bytes((ROOT / "series.json").read_bytes())
        (root / "assets").mkdir()
        (root / "assets/series-map.svg").write_bytes((ROOT / "assets/series-map.svg").read_bytes())

    def test_root_page_never_depends_on_optional_agent_outputs(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.prepare_root(root)
            paths = ["agent-books/prompt/README.md", "agent-books/yuyu-book/dist/yuyu-prompt-zh.html",
                     "agent-books/yuyu-book/dist/yuyu-prompt-zh.pdf"]
            for relative in paths:
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("fixture", encoding="utf-8")
            with patch.object(bookshelf, "ROOT", root):
                bookshelf.build()
            before = (root / "index.html").read_text(encoding="utf-8")
            self.assertIn((root / "assets/series-map.svg").read_text(encoding="utf-8"), before)
            self.assertIn('href="agent-books/prompt/README.md"', before)
            self.assertNotIn('href="agent-books/yuyu-book/dist/', before)
            for relative in paths[1:]:
                (root / relative).unlink()
            with patch.object(bookshelf, "ROOT", root):
                bookshelf.build()
            self.assertEqual(before, (root / "index.html").read_text(encoding="utf-8"))

    def test_distribution_links_to_collected_books_without_source_tree(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.prepare_root(root)
            path = root / "dist/agent-books/yuyu-prompt-zh.pdf"
            path.parent.mkdir(parents=True)
            path.write_bytes(b"fixture")
            with patch.object(bookshelf, "ROOT", root):
                bookshelf.build(distribution=True)
            page = (root / "dist/index.html").read_text(encoding="utf-8")
            self.assertIn('href="agent-books/yuyu-prompt-zh.pdf"', page)
            self.assertNotIn('href="agent-books/prompt/README.md"', page)
            self.assertNotIn('href="../', page)

    def test_collected_map_survives_copying_only_the_generated_page(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.prepare_root(root)
            diagram = (root / "assets/series-map.svg").read_text(encoding="utf-8")
            with patch.object(bookshelf, "ROOT", root):
                bookshelf.build(distribution=True)
            portable = root / "portable/index.html"
            portable.parent.mkdir()
            shutil.copyfile(root / "dist/index.html", portable)
            shutil.rmtree(root / "assets")
            page = portable.read_text(encoding="utf-8")
            self.assertIn(diagram, page)
            self.assertNotIn('src="assets/', page)
            self.assertNotIn('href="../', page)
            self.assertIn('tabindex="0" role="region"', page)
            self.assertIn("跨书选读不替代 C01–C30 的先修要求与阶段作业", page)

    def test_missing_authored_map_cannot_silently_produce_an_incomplete_page(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "series.json").write_bytes((ROOT / "series.json").read_bytes())
            with patch.object(bookshelf, "ROOT", root):
                with self.assertRaises(FileNotFoundError):
                    bookshelf.build(distribution=True)
            self.assertFalse((root / "dist/index.html").exists())

    def test_authored_map_is_accessible_and_has_no_external_dependencies(self):
        diagram = ElementTree.parse(ROOT / "assets/series-map.svg").getroot()
        namespace = "{http://www.w3.org/2000/svg}"
        self.assertEqual(diagram.tag, namespace + "svg")
        self.assertEqual(diagram.get("role"), "img")
        ids = {element.get("id"): element for element in diagram.iter() if element.get("id")}
        for reference in diagram.get("aria-labelledby").split():
            self.assertIn(reference, ids)
            self.assertTrue("".join(ids[reference].itertext()).strip())
        description = "".join(diagram.find(namespace + "desc").itertext())
        self.assertIn("原有先修要求", description)
        self.assertIn("只做文本任务可以直接核对依据", description)
        for element in diagram.iter():
            self.assertNotIn(element.tag, {namespace + "script", namespace + "image", namespace + "foreignObject"})
            for name, value in element.attrib.items():
                if name.rsplit("}", 1)[-1] in {"href", "src"}:
                    self.assertTrue(value.startswith("#"), value)
                if value.startswith("url("):
                    self.assertTrue(value.startswith("url(#"), value)
                    self.assertIn(value[5:-1], ids)
