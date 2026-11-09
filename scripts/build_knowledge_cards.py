#!/usr/bin/env python3
"""Regenerate docs/knowledge-cards.html and .en.html."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "yuyu-book"))

from yuyu_book.products.cards import main  # noqa: E402

if __name__ == "__main__":
    main()
