#!/usr/bin/env python3
"""Regenerate docs/sample-chapter.html and .en.html.

The body is chapter 2 rendered from canonical sources through the shared
edition pipeline; no prebuilt dist directory is required.
"""
import sys
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "yuyu-book"))

from yuyu_book.products.sample import main  # noqa: E402

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh-diagrams", action="store_true",
                        help="regenerate source-bound SVG plates; review them before committing")
    args = parser.parse_args()
    if args.refresh_diagrams:
        from yuyu_book import mermaid
        from yuyu_book.core import load_configs, load_unit, read_text, unit_stream
        from yuyu_book.products import sample_diagrams
        manifest, _sources = load_configs()
        editions = []
        for lang in ("zh", "en"):
            for definition, kind, _part in unit_stream(manifest):
                if definition["id"] == "ch02":
                    unit = load_unit(definition, kind, lang, ROOT)
                    editions.append((unit.blocks, mermaid.captions_for(
                        read_text(ROOT / unit.path), unit.blocks)))
        sample_diagrams.refresh(editions)
    main()
