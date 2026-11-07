#!/usr/bin/env python3
"""Generate the original printed-line sample used by the OCR lesson.

The image is generated locally with Pillow's bundled default font. It is not a
scan from a third-party manual and contains no personal data. Change --text to
make your own test line; the default is the line used in the measured smoke.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

DEFAULT_TEXT = "REPAIR WORKSHOP AT 10:00"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default="sample-line.png",
        help="PNG path to write (default: ./sample-line.png)",
    )
    parser.add_argument(
        "--text",
        default=DEFAULT_TEXT,
        help=f"printed line to render (default: {DEFAULT_TEXT!r})",
    )
    parser.add_argument("--font-size", type=int, default=44, help="font size in pixels (default 44)")
    parser.add_argument("--padding", type=int, default=24, help="white margin in pixels (default 24)")
    args = parser.parse_args()

    if not args.text.strip():
        parser.error("--text must not be empty")
    if args.font_size < 8:
        parser.error("--font-size must be at least 8")
    if args.padding < 0:
        parser.error("--padding must be non-negative")

    font = ImageFont.load_default(size=args.font_size)
    measurement = Image.new("RGB", (1, 1), "white")
    measure_draw = ImageDraw.Draw(measurement)
    left, top, right, bottom = measure_draw.textbbox((0, 0), args.text, font=font)
    text_width = max(1, right - left)
    text_height = max(1, bottom - top)
    width = text_width + args.padding * 2
    height = text_height + args.padding * 2

    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    draw.text(
        (args.padding - left, args.padding - top),
        args.text,
        fill="black",
        font=font,
    )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="PNG")
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    print(
        json.dumps(
            {
                "output": str(output),
                "text": args.text,
                "sha256": digest,
                "width": width,
                "height": height,
                "font": "Pillow bundled default font",
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
