"""Large generated plates retain tonal ink and never crop the subject."""
import io
import sys
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "yuyu-book"))

import gen_ink_plates as generator  # noqa: E402
from yuyu_book import art  # noqa: E402


class TonalPlate(unittest.TestCase):
    def test_tonal_ink_keeps_light_middle_and_solid_strokes(self):
        image = Image.new("RGBA", (120, 80), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.rectangle((10, 10, 30, 70), fill=(192, 192, 192, 255))
        draw.rectangle((50, 10, 70, 70), fill=(128, 128, 128, 255))
        draw.rectangle((90, 10, 110, 70), fill=(0, 0, 0, 255))
        raw = io.BytesIO()
        image.save(raw, "PNG")
        with Image.open(io.BytesIO(generator.to_tonal_plate(raw.getvalue(), 120, 80))) as plate:
            self.assertEqual(plate.size, (120, 80))
            self.assertEqual(plate.getpixel((0, 0)), (0, 0, 0, 0))
            for x, expected in ((20, 63), (60, 127), (100, 255)):
                red, green, blue, alpha = plate.getpixel((x, 40))
                self.assertEqual((red, green, blue), (0, 0, 0))
                self.assertLessEqual(abs(alpha - expected), 5)

    def test_portrait_response_fits_landscape_without_losing_extremities(self):
        image = Image.new("RGBA", (60, 120), (0, 0, 0, 0))
        ImageDraw.Draw(image).rectangle((10, 4, 50, 115), fill=(0, 0, 0, 255))
        raw = io.BytesIO()
        image.save(raw, "PNG")
        with Image.open(io.BytesIO(generator.to_tonal_plate(raw.getvalue(), 200, 140))) as plate:
            alpha = plate.getchannel("A")
            left, top, right, bottom = alpha.getbbox()
            self.assertGreater(left, 0)
            self.assertLess(right, 200)
            self.assertGreater(top, 0)
            self.assertLess(bottom, 140)
            self.assertGreater(bottom - top, 120,
                               "both ends of the portrait subject must remain")


    def test_a_wide_plate_grades_coarser_before_it_breaks_the_budget(self):
        # grain defeats PNG's filters, so grading visibly moves the byte count;
        # the budget is measured from the finest grading rather than guessed
        random = __import__("random").Random(20261108)
        image = Image.new("RGBA", (900, 630))
        image.putdata([(v, v, v, 255)
                       for v in (random.randrange(256) for _ in range(900 * 630))])
        raw = io.BytesIO()
        image.save(raw, "PNG")
        finest = generator.to_tonal_plate(raw.getvalue(), 900, 630)
        plate, levels = generator.to_tonal_plate_within(
            raw.getvalue(), 900, 630, len(finest) - 1)
        self.assertLess(levels, 64, "an over-budget plate must buy bytes with grading")
        self.assertLessEqual(len(plate), len(finest) - 1)
        with Image.open(io.BytesIO(plate)) as decoded:
            self.assertEqual(decoded.size, (900, 630))
            self.assertEqual(decoded.getchannel("A").getextrema()[1], 255)

    def test_a_plate_that_fits_keeps_the_finest_grading(self):
        image = Image.new("RGBA", (60, 40), (0, 0, 0, 0))
        ImageDraw.Draw(image).rectangle((10, 5, 50, 35), fill=(90, 90, 90, 255))
        raw = io.BytesIO()
        image.save(raw, "PNG")
        plate, levels = generator.to_tonal_plate_within(
            raw.getvalue(), 60, 40, art.PLATE_RASTER_BYTES)
        self.assertEqual(levels, 64)
        self.assertEqual(plate, generator.to_tonal_plate(raw.getvalue(), 60, 40))

    def test_a_plate_that_cannot_fit_is_refused(self):
        image = Image.new("RGBA", (600, 420), (0, 0, 0, 255))
        raw = io.BytesIO()
        image.save(raw, "PNG")
        with self.assertRaises(ValueError):
            generator.to_tonal_plate_within(raw.getvalue(), 900, 630, 1024)


if __name__ == "__main__":
    unittest.main()
