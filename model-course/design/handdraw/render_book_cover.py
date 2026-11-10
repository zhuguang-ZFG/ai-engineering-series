#!/usr/bin/env python3
"""Re-render `book/assets/cover.webp` from `book/assets/cover.svg`.

The SVG is the source of truth (token-aligned to design/system/tokens.css);
the webp is only a raster snapshot of it, same Chrome + Pillow pipeline as
render_ep01_covers.py.

    python design/handdraw/render_book_cover.py
"""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
ROOT = Path(__file__).resolve().parents[2]
SVG = ROOT / "book" / "assets" / "cover.svg"
WEBP = ROOT / "book" / "assets" / "cover.webp"
STILL = ROOT / "design" / "handdraw" / "renders" / "book-cover.png"
SIZE = (1600, 1000)


def main() -> None:
    STILL.parent.mkdir(parents=True, exist_ok=True)
    if STILL.exists():
        STILL.unlink()
    profile = tempfile.mkdtemp(prefix="book-cover-chrome-")
    subprocess.run(
        [
            CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
            "--disable-extensions", "--no-first-run", "--no-default-browser-check",
            "--force-device-scale-factor=1", f"--user-data-dir={profile}",
            f"--window-size={SIZE[0]},{SIZE[1]}", f"--screenshot={STILL}",
            "file:///" + str(SVG).replace(os.sep, "/"),
        ],
        capture_output=True,
        timeout=90,
    )
    if not STILL.exists() or STILL.stat().st_size < 10_000:
        raise SystemExit(f"chrome produced no screenshot for {SVG}")
    with Image.open(STILL) as im:
        if im.size != SIZE:
            raise SystemExit(f"book-cover.png: got {im.size}, want {SIZE}")
        im.convert("RGB").save(WEBP, "WEBP", quality=92, method=6)
    print(f"{SVG.name} -> {WEBP.relative_to(ROOT)} ({WEBP.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
