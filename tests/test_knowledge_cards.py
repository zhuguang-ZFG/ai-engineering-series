"""The knowledge cards keep the book's own words and the shared marks.

Each deck is three 3:4 cards cut from one chapter: the door-opener quote, the
plain mechanism and the three-sentence recap. This suite proves the shipped
pages match the generators and that no card invents a sentence.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "yuyu-book"))
from yuyu_book.labels import esc  # noqa: E402
from yuyu_book.products import cards  # noqa: E402
from yuyu_book.products.chapter_copy import hook, recap  # noqa: E402
from yuyu_book.products.loader import load_repo_model  # noqa: E402

OUT = {lang: ROOT / "docs" / name for lang, name in cards.OUT.items()}


class Cards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.models = {lang: load_repo_model([lang]) for lang in cards.OUT}

    def test_every_chapter_ships_three_cards(self):
        for lang, out in OUT.items():
            page = out.read_text(encoding="utf-8")
            self.assertEqual(page.count('<article class="kcard'), 45,
                             f"{out}: three cards per chapter")
            self.assertEqual(page.count('<section class="ch"'), 15,
                             f"{out}: one deck per chapter")

    def test_the_shipped_cards_match_their_generators(self):
        for lang, out in OUT.items():
            committed = out.read_text(encoding="utf-8")
            self.assertEqual(cards.page_for(self.models[lang], lang), committed,
                             f"{out}: regenerate the cards after a chapter edit")

    def test_every_quote_is_the_chapters_own_text(self):
        for lang, out in OUT.items():
            page = out.read_text(encoding="utf-8")
            for unit in self.models[lang].editions[lang].units:
                if unit.kind != "chapter":
                    continue
                self.assertIn(esc(hook(unit, lang)), page,
                              f"{out}: {unit.id} hook missing")
                for item in recap(unit, lang):
                    self.assertIn(esc(item), page,
                                  f"{out}: {unit.id} recap item missing")

    def test_the_cards_stay_offline_and_scriptless(self):
        for lang, out in OUT.items():
            page = out.read_text(encoding="utf-8")
            self.assertNotIn("<script", page, out)
            self.assertNotIn('src="http', page, out)
            self.assertIn("aspect-ratio:3/4", page, out)
            self.assertIn("@media print", page, out)
            self.assertIn("prefers-reduced-motion", page, out)
            self.assertIn("<title>", page, out)


if __name__ == "__main__":
    unittest.main()
