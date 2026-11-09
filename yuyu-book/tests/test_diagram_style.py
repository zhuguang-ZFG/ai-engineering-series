"""Prose decoration must not reduce a Mermaid label's measured text area."""
import sys
import unittest
from pathlib import Path

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from playwright.sync_api import sync_playwright
from yuyu_book.pdf import _launch
from yuyu_book.style_css import CSS


class DiagramLabelStyle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.browser = _launch(cls.playwright, None)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def test_chinese_quote_border_does_not_apply_to_diagram_labels(self):
        page = self.browser.new_page()
        try:
            page.set_content('<html><head><style>' + CSS + '</style></head>'
                '<body class="lang-zh"><article><div class="chapter-body">'
                '<p id="prose">正文</p><blockquote id="quote">引用</blockquote>'
                '<figure class="diagram"><div class="diagram-frame">'
                '<svg width="300" height="100"><foreignObject width="200" height="60">'
                '<div xmlns="http://www.w3.org/1999/xhtml">'
                '<span class="nodeLabel"><p id="label">before_agent_start</p></span>'
                '</div></foreignObject></svg></div></figure></div></article></body></html>')
            for media in ("screen", "print"):
                page.emulate_media(media=media)
                values = page.evaluate('''() => Object.fromEntries(
                    ['prose','quote','label'].map(id => {
                        const style = getComputedStyle(document.getElementById(id));
                        return [id, {border: parseFloat(style.borderInlineStartWidth),
                                     padding: parseFloat(style.paddingInlineStart)}];
                    }))''')
                for name in ("prose", "label"):
                    self.assertEqual(values[name], {"border": 0, "padding": 0},
                                     f"{media}: {name} acquired a quote gutter")
                self.assertGreater(values["quote"]["border"], 0)
        finally:
            page.close()


if __name__ == "__main__":
    unittest.main()
