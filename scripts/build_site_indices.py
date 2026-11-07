#!/usr/bin/env python3
"""Regenerate docs/search-index.json, language-map.json and concept-map.json."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "yuyu-book"))

from yuyu_book.products.indices import main  # noqa: E402

if __name__ == "__main__":
    main()
