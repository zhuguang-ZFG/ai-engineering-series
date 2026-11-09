"""EPUB format validation cannot detect diagrams that rasterize as black blocks."""
from __future__ import annotations

import io
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_epub import build


class EpubPaint(unittest.TestCase):
    def test_svg_local_styles_survive_until_rasterization(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            source = folder / "fixture.html"
            output = folder / "fixture.epub"
            source.write_text('''<!doctype html><html lang="en"><head>
                <meta charset="utf-8"><title>Paint fixture</title></head><body><main>
                <h1 id="title">Paint fixture</h1><style>.extra{color:blue}</style>
                <figure><svg xmlns="http://www.w3.org/2000/svg" id="diagram"
                    viewBox="0 0 120 80" width="120" height="80">
                  <style>#diagram .node{fill:#e4ebf2;stroke:#4c7093}
                    #diagram .edge{fill:none;stroke:#4c7093;stroke-width:2}</style>
                  <rect class="node" x="10" y="10" width="100" height="60"/>
                  <path class="edge" d="M20 60 L60 20 L100 60"/>
                </svg><figcaption>Styled diagram</figcaption></figure>
                </main></body></html>''', encoding="utf-8")
            report = build(source, output, "en")
            self.assertEqual(report["rasterized_svg"], 1)
            with zipfile.ZipFile(output) as archive:
                images = [name for name in archive.namelist() if name.endswith(".png")]
                self.assertEqual(len(images), 1)
                image = Image.open(io.BytesIO(archive.read(images[0]))).convert("RGB")
                # A point in the V-shaped path's interior stays the pale node
                # color. If fill:none or the node fill is lost, it becomes black.
                x, y = int(image.width * .5), int(image.height * .65)
                self.assertEqual(image.getpixel((x, y)), (228, 235, 242))
                content = archive.read("EPUB/content.xhtml").decode("utf-8")
                self.assertNotIn("<style", content)
                self.assertNotIn(".node{", content)


if __name__ == "__main__":
    unittest.main()
