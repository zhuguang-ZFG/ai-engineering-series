#!/usr/bin/env python3
"""Regenerate docs/sample-chapter.html and .en.html.

The body is chapter 2 as the book's pipeline rendered it, so build the book
first (`python yuyu-book/build.py --lang both`).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "yuyu-book"))

from yuyu_book.products.sample import main  # noqa: E402

if __name__ == "__main__":
    main()
