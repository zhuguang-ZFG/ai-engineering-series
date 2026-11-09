#!/usr/bin/env python3
"""Regenerate docs/beginner-reader.html and .en.html.

The page lives in yuyu_book.products.reader; this entry point stays at the old
path for the Pages workflow and the tests that quote the station counts.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "yuyu-book"))

from yuyu_book.products.reader import (APPENDIX_STATIONS, ART, LANGS,  # noqa: E402,F401
                                       ORDER, PLATES, build, main,
                                       page_for)

if __name__ == "__main__":
    main()
