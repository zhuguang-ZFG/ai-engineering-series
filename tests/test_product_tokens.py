"""Every generated page paints from the one shared palette.

The portal, the two beginner readers, the gallery, the cards and the sample
chapter are separate generators that ship next to the book. Their copied
hexes used to drift by hand; this suite makes the shared `products.tokens`
module the only place a colour may be introduced and fails on a page that
invents one.

The sample chapter rehosts the book's own rendered chapter, so it embeds the
book's complete stylesheet. Its colours are therefore admitted from
`style_css` itself, and the same scan still fails if the sample adds one of
its own.
"""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "yuyu-book"))
from yuyu_book import style_css, style_tokens  # noqa: E402
from yuyu_book.products import tokens  # noqa: E402

PAGES = ("docs/portal.html", "docs/beginner-reader.html",
         "docs/beginner-reader.en.html", "docs/illustration-gallery.html",
         "docs/knowledge-cards.html", "docs/knowledge-cards.en.html")
SAMPLE_PAGES = ("docs/sample-chapter.html", "docs/sample-chapter.en.html")
GENERATORS = ("yuyu-book/yuyu_book/products/portal.py",
              "yuyu-book/yuyu_book/products/reader.py",
              "yuyu-book/yuyu_book/products/gallery.py",
              "yuyu-book/yuyu_book/products/cards.py",
              "yuyu-book/yuyu_book/products/sample.py")


class Palette(unittest.TestCase):
    def test_every_shipped_page_paints_only_shared_colours(self):
        for path in PAGES:
            page = (ROOT / path).read_text(encoding="utf-8")
            self.assertEqual(tokens.unregistered(page), set(), path)

    def test_the_sample_quotes_the_book_sheet_and_adds_no_colour(self):
        """The sample's own frame is the hero, the recap card and the foot;
        the chapter body and the book sheet are quoted verbatim, so only the
        frame is gated here."""
        for path in SAMPLE_PAGES:
            page = (ROOT / path).read_text(encoding="utf-8")
            self.assertIn(style_css.CSS, page,
                          f"{path}: does not embed the book stylesheet")
            rest = page.replace(style_css.CSS, "", 1)
            start = rest.index('<main class="sample-main">')
            article = rest.index('<article class="chapter"', start)
            recap = rest.index('<aside class="sp-recap"', article)
            own = rest[:article] + rest[recap:]
            self.assertEqual(tokens.unregistered(own), set(), path)

    def test_the_gate_catches_an_invented_colour(self):
        self.assertEqual(tokens.unregistered("a{color:#123456}"),
                         {"#123456"})
        self.assertEqual(tokens.unregistered("a{color:rgba(1,2,3,.4)}"),
                         {"#010203"})

    def test_the_book_and_the_products_share_their_tokens(self):
        css = style_tokens.TOKENS_CSS
        for name, prop in tokens.BOOK_MIRROR.items():
            match = re.search(rf"{re.escape(prop)}:\s*(#[0-9A-Fa-f]{{6}})", css)
            self.assertIsNotNone(match, f"{prop} missing from style_tokens")
            self.assertEqual(match.group(1).upper(), tokens.PALETTE[name].upper(),
                             f"{name} drifted from {prop}")


class SharedMarks(unittest.TestCase):
    def test_every_page_ships_the_seal_favicon_and_the_brush_rule(self):
        for path in PAGES + SAMPLE_PAGES:
            page = (ROOT / path).read_text(encoding="utf-8")
            self.assertIn(tokens.FAVICON, page, path)
            self.assertIn(tokens.BRUSH, page, path)

    def test_the_marks_are_written_once(self):
        """A generator that inlines the markup again is a second source of
        truth; it must ask the tokens module instead."""
        for path in GENERATORS:
            source = (ROOT / path).read_text(encoding="utf-8")
            self.assertIn("@@FAVICON@@", source, path)
            self.assertIn("@@BRUSH@@", source, path)
            self.assertNotIn('class="brush"', source, path)
            self.assertNotIn("data:image/svg+xml", source, path)

    def test_each_page_sets_the_shared_type_and_corner(self):
        portal = (ROOT / "docs/portal.html").read_text(encoding="utf-8")
        self.assertIn(f"font:16px/1.9 {tokens.SERIF_ZH}", portal)
        self.assertIn(f"border-radius:{tokens.RADIUS_CARD}", portal)
        zh = (ROOT / "docs/beginner-reader.html").read_text(encoding="utf-8")
        self.assertIn(f"font:16px/1.9 {tokens.SERIF_ZH}", zh)
        self.assertIn(f"border-radius:{tokens.RADIUS_STATION}", zh)
        en = (ROOT / "docs/beginner-reader.en.html").read_text(encoding="utf-8")
        self.assertIn(f"font:16px/1.8 {tokens.SERIF_EN}", en)
        gallery = (ROOT / "docs/illustration-gallery.html").read_text(
            encoding="utf-8")
        self.assertIn(f"font:14px/1.6 {tokens.SANS}", gallery)
        self.assertIn(f"border-radius:{tokens.RADIUS_CHIP}", gallery)
        zh_cards = (ROOT / "docs/knowledge-cards.html").read_text(
            encoding="utf-8")
        self.assertIn(f"font:15px/1.75 {tokens.SERIF_ZH}", zh_cards)
        self.assertIn(f"border-radius:{tokens.RADIUS_CARD}", zh_cards)
        self.assertIn(f"border-radius:{tokens.RADIUS_RESUME}", zh_cards)
        en_cards = (ROOT / "docs/knowledge-cards.en.html").read_text(
            encoding="utf-8")
        self.assertIn(f"font:15px/1.75 {tokens.SERIF_EN}", en_cards)
        for path, body_class in (("docs/sample-chapter.html", "lang-zh"),
                                 ("docs/sample-chapter.en.html", "lang-en")):
            sample = (ROOT / path).read_text(encoding="utf-8")
            self.assertIn(f'<body class="{body_class} sample">', sample, path)
            self.assertIn("font:400 17px/1.8 var(--serif)", sample, path)
            self.assertIn(f"border-radius:{tokens.RADIUS_STATION}", sample,
                          path)


if __name__ == "__main__":
    unittest.main()
