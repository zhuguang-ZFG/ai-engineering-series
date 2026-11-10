"""Transparent generated renders must not turn invisible RGB into black ink."""
import io
import sys
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from gen_ink_plates import to_plate  # noqa: E402


class TransparentRender(unittest.TestCase):
    def test_invisible_pixels_remain_paper_regardless_of_stored_rgb(self):
        masks = []
        for background in ((0, 0, 0, 0), (255, 255, 255, 0)):
            with self.subTest(background=background):
                image = Image.new("RGBA", (64, 64), background)
                ImageDraw.Draw(image).rectangle((24, 16, 40, 48),
                                                fill=(0, 0, 0, 255))
                source = io.BytesIO()
                image.save(source, "PNG")
                with Image.open(io.BytesIO(to_plate(source.getvalue(), 64))) as plate:
                    alpha = plate.getchannel("A")
                    masks.append(alpha.tobytes())
                    self.assertEqual(alpha.getpixel((0, 0)), 0,
                                     "transparent paper must not become ink")
                    self.assertEqual(alpha.getpixel((32, 32)), 255,
                                     "the opaque stroke must remain visible")
        self.assertEqual(masks[0], masks[1],
                         "invisible RGB must not change the rendered drawing")


if __name__ == "__main__":
    unittest.main()
