"""EPUB format validation cannot detect diagrams that rasterize as black blocks."""
from __future__ import annotations

import io
from html.parser import HTMLParser
from pathlib import Path
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_epub import build
from yuyu_book import plain
from yuyu_book.app import build_edition
from yuyu_book.core import load_configs
from yuyu_book.style import page


class AuthorMetadata(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.authors = []
        self.feed(source)

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == "meta" and attrs.get("name") == "author":
            self.authors.append(attrs)


class EditionAuthors(unittest.TestCase):
    def test_page_keeps_default_author_and_escapes_explicit_names(self):
        original, _sources = load_configs("manifest.json", "sources.json")
        arguments = ("zh", "Author fixture", "", "", "<h1>Title</h1>", "", "")
        self.assertEqual(AuthorMetadata(page(*arguments)).authors,
                         [{"name": "author", "content": original["author"]}])
        author = '作者 "A&B" <团队> \'署名\''
        source = page(*arguments, author=author)
        self.assertIn('content="作者 &quot;A&amp;B&quot; &lt;团队&gt; &#x27;署名&#x27;"',
                      source)
        self.assertEqual(AuthorMetadata(source).authors,
                         [{"name": "author", "content": author}])

    def test_prompt_html_and_epub_use_the_registered_author(self):
        manifest, sources = load_configs("manifest-prompt.json", "sources-prompt.json")
        glosses, paths = plain.load_plain(manifest)
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            source = build_edition(
                "zh", manifest, sources, mode="source", browser=None,
                autolink=True, out_dir=folder, do_pdf=False, edge=None,
                glosses=glosses, paths=paths, notes=plain.load_notes(manifest))
            self.assertEqual(AuthorMetadata(source.read_text(encoding="utf-8")).authors,
                             [{"name": "author", "content": manifest["author"]}])
            output = folder / "prompt.epub"
            build(source, output, "zh")
            with zipfile.ZipFile(output) as archive:
                metadata = ET.fromstring(archive.read("EPUB/package.opf"))
                creators = metadata.findall(".//{http://purl.org/dc/elements/1.1/}creator")
                self.assertEqual([creator.text for creator in creators], [manifest["author"]])


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
