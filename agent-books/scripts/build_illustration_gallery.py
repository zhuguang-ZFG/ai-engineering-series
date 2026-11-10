#!/usr/bin/env python3
"""Regenerate docs/illustration-gallery.html.

The page lives in yuyu_book.products.gallery; this entry point stays at the
old path for the Pages workflow and the docs that reference it.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "yuyu-book"))

from yuyu_book.products.gallery import main  # noqa: E402

if __name__ == "__main__":
    main()
