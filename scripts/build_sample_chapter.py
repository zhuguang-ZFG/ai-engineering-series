#!/usr/bin/env python3
"""Regenerate docs/sample-chapter.html and .en.html.

The body is chapter 2 rendered from canonical sources through the shared
edition pipeline; no prebuilt dist directory is required.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "yuyu-book"))

from yuyu_book.products.sample import main  # noqa: E402

if __name__ == "__main__":
    main()
