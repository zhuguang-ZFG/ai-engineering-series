"""Mixed artwork keeps semantic small SVGs and validates generated large ink."""
import base64
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from yuyu_book import art  # noqa: E402
from yuyu_book.core import BuildError  # noqa: E402

SVG = '<svg viewBox="0 0 64 64"><path class="spin" stroke="currentColor" d="M10 20L50 40"/></svg>'


def png(rgb=(0, 0, 0), opaque=False):
    image = Image.new("RGBA", (16, 16), (*rgb, 255 if opaque else 0))
    image.putpixel((8, 8), (*rgb, 255))
    output = io.BytesIO()
    image.save(output, "PNG")
    return output.getvalue()


class MixedArtwork(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        for attribute, value in (("ART_DIR", self.root), ("OMP_ART_DIR", self.root / "omp")):
            override = patch.object(art, attribute, value)
            override.start()
            self.addCleanup(override.stop)

    def test_small_semantic_slots_do_not_lose_svg_to_a_same_named_png(self):
        for name, render in (("ch01", lambda: art.emblem("ch01")),
                             ("keeper", art.keeper),
                             ("ch01-five-pillars", lambda: art.drawing("ch01-five-pillars"))):
            with self.subTest(name=name):
                (self.root / f"{name}.svg").write_text(SVG, encoding="utf-8")
                (self.root / f"{name}.png").write_bytes(png())
                out = render()
                self.assertIn('class="spin"', out)
                self.assertNotIn("<img", out)

    def test_a_large_plate_is_embedded_with_its_original_pixels(self):
        raw = png()
        (self.root / "part-p1.png").write_bytes(raw)
        out = art.headpiece("p1")
        self.assertIn('class="pd-art"', out)
        self.assertIn(base64.b64encode(raw).decode("ascii"), out)
        self.assertIn('width="16" height="16"', out)
        self.assertEqual(art.missing(["part-p1"]), [])

    def test_invalid_large_ink_is_rejected_before_embedding(self):
        for label, raw in (("opaque", png(opaque=True)), ("coloured", png((200, 10, 0))),
                           ("truncated", png()[:24])):
            with self.subTest(label=label):
                (self.root / "part-p1.png").write_bytes(raw)
                with self.assertRaises(BuildError):
                    art.headpiece("p1")

    def test_large_plate_budget_is_enforced(self):
        (self.root / "part-p1.png").write_bytes(png() + b"x" * art.PLATE_RASTER_BYTES)
        with self.assertRaises(BuildError):
            art.headpiece("p1")

    def test_a_plate_states_what_it_shows(self):
        # the shipped pages require every <img> to carry a name; a decorative
        # frame does not excuse an empty alt
        (self.root / "part-p1.png").write_bytes(png())
        (self.root / "cover.png").write_bytes(png())
        (self.root / "part-omp-p1.png").write_bytes(png())
        zh, en = art.PLATE_ALT["zh"], art.PLATE_ALT["en"]
        self.assertIn(f'alt="{zh["p1"]}"', art.headpiece("p1"))
        self.assertIn(f'alt="{zh["cover"]}"', art.cover_plate())
        self.assertIn(f'alt="{en["p1"]}"', art.headpiece("p1", "en"))
        self.assertIn(f'alt="{en["cover"]}"', art.cover_plate("en"))
        self.assertNotIn('alt=""', art.headpiece("omp-p1", "en"))
        self.assertIn(f'alt="{art.PLATE_ALT_FALLBACK["en"]}"', art.headpiece("omp-p1", "en"))


if __name__ == "__main__":
    unittest.main()
