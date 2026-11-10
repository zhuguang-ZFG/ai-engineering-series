from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_site_portal  # noqa: E402

REDUCE = "@media screen and (prefers-reduced-motion: reduce)"


class PortalReducedMotion(unittest.TestCase):
    def test_card_entrance_animation_stops_for_reduced_motion(self):
        page = build_site_portal.PAGE
        self.assertIn("animation:card-in", page)
        self.assertIn(REDUCE, page)
        guard = page[page.index(REDUCE):page.index("</style>")]
        self.assertIn("a.card{animation:none", guard)
        self.assertIn("a.card:hover{transform:none}", guard)

    def test_the_committed_portal_matches_its_generator(self):
        committed = (ROOT / "docs" / "portal.html").read_text(encoding="utf-8")
        self.assertEqual(committed, build_site_portal.PAGE)

    def test_the_front_door_quotes_the_counts_the_builders_derive(self):
        """Cards advertise the readers and the gallery; a stale number is the
        first thing a visitor checks against the page it links to."""
        import build_beginner_reader as reader
        self.assertNotIn("@@", build_site_portal.PAGE, "unfilled token in the portal")
        self.assertIn(f"{reader.LANGS['zh']['total']} 站看图入门",
                      build_site_portal.PAGE)
        self.assertIn(f"{reader.LANGS['en']['total']}-station picture walk",
                      build_site_portal.PAGE)
        self.assertIn(f"{reader.PLATES} 幅手绘插图", build_site_portal.PAGE)


if __name__ == "__main__":
    unittest.main()
