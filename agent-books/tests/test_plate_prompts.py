"""Manual selection and offline raster conversion boundaries."""
import io
import os
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "yuyu-book"))

from gen_ink_plates import ART_DIR, plates, to_plate  # noqa: E402
from yuyu_book import art  # noqa: E402

from PIL import Image, ImageDraw  # noqa: E402


class Manual(unittest.TestCase):
    def setUp(self):
        self.jobs = plates()

    def test_the_manual_yields_every_book_plate_and_no_other(self):
        names = [job["name"] for job in self.jobs]
        self.assertEqual(len(names), 26)
        self.assertEqual(len(set(names)), 26)
        self.assertIn("ch01", names)
        self.assertIn("cover", names)
        self.assertNotIn("ch01-five-pillars", names)


    def test_no_prompt_names_an_artist(self):
        """The channel answers 400 content_policy_violation for a similarity to a
        named living artist, so the manual's index tag must not survive parsing."""
        for job in self.jobs:
            self.assertNotIn("参考作者", job["prompt"], job["name"])
            self.assertNotIn("Yuko", job["prompt"], job["name"])



class Plate(unittest.TestCase):
    def _render(self, size=(768, 768)) -> bytes:
        image = Image.new("L", size, 245)
        draw = ImageDraw.Draw(image)
        draw.ellipse((96, 96, 672, 672), outline=20, width=18)
        draw.line((384, 140, 384, 628), fill=20, width=16)
        draw.ellipse((344, 344, 424, 424), fill=20)
        buffer = io.BytesIO()
        image.save(buffer, "PNG")
        return buffer.getvalue()

    def test_a_sample_comes_out_transparent_with_ink_and_paper(self):
        raw = to_plate(self._render(), 512)
        with Image.open(io.BytesIO(raw)) as plate:
            self.assertEqual(plate.mode, "RGBA")
            self.assertEqual(plate.size, (512, 512))
            alpha = plate.getchannel("A")
            low, high = alpha.getextrema()
            self.assertEqual((low, high), (0, 255), "ink and paper both survive")

    def test_ink_survives_a_narrow_plate(self):
        # a part headpiece is drawn wide: the same paper must still carry lines
        raw = to_plate(self._render((1024, 683)), 900)
        with Image.open(io.BytesIO(raw)) as plate:
            self.assertLessEqual(len(raw), art.PLATE_RASTER_BYTES)
            alpha = plate.getchannel("A")
            ink = sum(1 for value in alpha.get_flattened_data() if value > 127)
            self.assertGreater(ink / (plate.width * plate.height), 0.01)



class Command(unittest.TestCase):
    def test_a_dry_run_needs_no_credentials(self):
        keep = {k: os.environ.pop(k, None) for k in ("NEWAPI_URL", "NEWAPI_KEY")}
        try:
            import gen_ink_plates
            self.assertIsNone(gen_ink_plates.credentials())
            self.assertEqual(gen_ink_plates.main(["--dry-run", "--only", "ch01"]), 0)
        finally:
            for key, value in keep.items():
                if value is not None:
                    os.environ[key] = value


if __name__ == "__main__":
    unittest.main()
