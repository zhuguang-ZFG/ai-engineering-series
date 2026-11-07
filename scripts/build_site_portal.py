#!/usr/bin/env python3
"""Generate the GitHub Pages portal (site index).

The page lives in yuyu_book.products.portal; this entry point keeps the
`python scripts/build_site_portal.py [out]` contract the Pages workflow uses.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "yuyu-book"))

from yuyu_book.products.portal import PAGE, write  # noqa: E402,F401


def main() -> None:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("docs/portal.html")
    print(f"{write(out)} ({len(PAGE)} bytes)")


if __name__ == "__main__":
    main()
