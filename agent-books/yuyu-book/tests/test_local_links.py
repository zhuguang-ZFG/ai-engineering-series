"""Source links must remain usable in a single-file edition."""
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from yuyu_book.refs import RefLinker, process_links, resolve_local_links
from yuyu_book.render import prefix_ids


class OfflineLinks(unittest.TestCase):
    def test_cross_chapter_fragment_survives_current_chapter_prefix(self):
        doc = '<a href="ch18.md#tradeoffs">next</a><a href="#local">here</a>'
        targets = {"codex/ch18.md": "codex-ch18"}
        doc = resolve_local_links(doc, "codex/ch01.md", targets, Path.cwd(),
                                  chapters=False)
        doc = prefix_ids(doc, "codex-ch01")
        doc = resolve_local_links(doc, "codex/ch01.md", targets, Path.cwd(),
                                  chapters=True)
        self.assertIn('href="#codex-ch18-tradeoffs"', doc)
        self.assertIn('href="#codex-ch01-local"', doc)

    def test_repository_samples_get_published_urls_and_footnotes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "examples").mkdir()
            (root / "examples" / "probe.py").write_text("pass", encoding="utf-8")
            doc = resolve_local_links('<a href="../examples/probe.py">sample</a>',
                                      "codex/ch01.md", {}, root, chapters=False)
            external = []
            doc = process_links(doc, external)
            self.assertEqual(external, [
                "https://github.com/zhuguang-ZFG/ai-engineering-series/blob/main/agent-books/examples/probe.py"])
            self.assertIn('class="fnum"', doc)
            (root / "examples" / "说明 文档.md").write_text("# 用法", encoding="utf-8")
            for href, fragment in (
                    ("../examples/说明 文档.md#用法", "用法"),
                    ("../examples/%E8%AF%B4%E6%98%8E%20%E6%96%87%E6%A1%A3.md#%E7%94%A8%E6%B3%95",
                     "%E7%94%A8%E6%B3%95")):
                with self.subTest(href=href):
                    doc = resolve_local_links(f'<a href="{href}">说明</a>',
                                              "codex/ch01.md", {}, root, chapters=False)
                    self.assertEqual(doc,
                        '<a href="https://github.com/zhuguang-ZFG/ai-engineering-series/'
                        'blob/main/agent-books/examples/'
                        '%E8%AF%B4%E6%98%8E%20%E6%96%87%E6%A1%A3.md#'
                        + fragment + '">说明</a>')

        root = Path(__file__).resolve().parents[2]
        for relative in ("materials/notice-v1.md", "examples/full-request.json"):
            with self.subTest(prompt_source=relative):
                self.assertTrue((root / "prompt" / relative).is_file())
                doc = resolve_local_links(f'<a href="{relative}">练习材料</a>',
                                          "prompt/ch01.md", {}, root, chapters=False)
                external = []
                process_links(doc, external)
                self.assertEqual(external, [
                    "https://github.com/zhuguang-ZFG/ai-engineering-series/"
                    "blob/main/agent-books/prompt/" + relative])

    def test_external_anchor_and_missing_or_escaping_paths_stay_visible(self):
        for href in ("#source", "https://example.com/a.md", "mailto:a@b.test",
                     "https://github.com/zhuguang-ZFG/claude-code-book/"
                     "tree/1ec7749bdea31b96729eb307f69e12f446284b2e#source",
                     "missing.md", "../../outside.md", "//example.com/a.md"):
            doc = f'<a href="{href}">label</a>'
            for chapters in (False, True):
                self.assertEqual(resolve_local_links(doc, "codex/ch01.md", {},
                                                     Path.cwd(), chapters=chapters), doc)

    def test_repeated_citation_has_one_backlink_target(self):
        external = []
        doc = process_links('<a href="https://example.com">one</a>'
                            '<a href="https://example.com">two</a>', external)
        self.assertEqual(len(external), 1)
        self.assertEqual(re.findall(r'id="fnref-1"', doc), ['id="fnref-1"'])
        self.assertEqual(doc.count('href="#fn-1"'), 2)

    def test_product_references_reach_chapter_18_without_self_links(self):
        mapping = {"ch01": "codex-ch01", "ch18": "codex-ch18", "apxd": "codex-apxd"}
        doc = RefLinker(mapping, "codex-ch01", "zh").transform(
            "<p>第 1 章、第 18 章、附录 D、第 19 章。</p>")
        self.assertIn('href="#codex-ch18"', doc)
        self.assertIn('href="#codex-apxd"', doc)
        self.assertNotIn('href="#codex-ch01"', doc)
        self.assertEqual(doc.count('class="xref"'), 2)
