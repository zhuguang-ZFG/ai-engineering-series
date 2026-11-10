#!/usr/bin/env python3
"""Typeset the book cover with real simplified Chinese font glyphs.

The cover shares the book's design system: a lacquer-ink (C-32 charcoal)
header band, the chariot engraving mapped as a paper-to-ink duotone so the
plate reads as inked on the same warm sheet as the book, and cinnabar (C-15)
as the single accent. Requires Pillow and installed CJK fonts; per-platform
candidates are probed so the same command runs on macOS and Windows. The
unlettered artwork is kept separately so every run builds the same cover
without painting over previous text.
"""
import argparse
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]

# the book's tokens, mirrored from yuyu-book/yuyu_book/style.py
LACQUER = '#26221B'   # C-32 charcoal: the header band the title sits on
PAPER = '#FBF7EF'     # the warm sheet
INK = '#26221B'       # footer text ink
CINNABAR = '#B4472F'  # C-15: the single accent (the rule under the plate)

FONT_CANDIDATES = {
    # serif CJK for the two-character title
    'title': ['/System/Library/Fonts/Supplemental/Songti.ttc',
              'C:/Windows/Fonts/simsun.ttc',
              'C:/Windows/Fonts/STZHONGS.TTF',
              '/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc'],
    # sans for the eyebrow and subtitle lines
    'sans': ['/System/Library/Fonts/STHeiti Medium.ttc',
             'C:/Windows/Fonts/msyh.ttc',
             'C:/Windows/Fonts/msyhbd.ttc',
             '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'],
    'footer': ['/System/Library/Fonts/Hiragino Sans GB.ttc',
               'C:/Windows/Fonts/msyh.ttc',
               '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'],
}
FONT_INDEX = {'title': 0, 'sans': 0, 'footer': 0}


def resolve_font(kind: str) -> tuple[str, int]:
    """First installed font for the role, so one command works on any OS."""
    for candidate in FONT_CANDIDATES[kind]:
        if Path(candidate).exists():
            return candidate, FONT_INDEX[kind]
    flag = {'title': '--font', 'sans': '--sans-font', 'footer': '--footer-font'}[kind]
    raise SystemExit(f'no installed CJK font found for {kind}; pass {flag}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT / 'scripts/assets/cover-art.png')
    parser.add_argument('--image', type=Path, default=ROOT / 'cover.png')
    parser.add_argument('--font', default=None, help='override the title serif')
    parser.add_argument('--font-index', type=int, default=None)
    parser.add_argument('--sans-font', default=None, help='override the sans')
    parser.add_argument('--sans-font-index', type=int, default=None)
    parser.add_argument('--footer-font', default=None, help='override the footer face')
    parser.add_argument('--footer-font-index', type=int, default=None)
    args = parser.parse_args()

    def pick(kind: str):
        path = {'title': args.font, 'sans': args.sans_font,
                'footer': args.footer_font}[kind]
        index = {'title': args.font_index, 'sans': args.sans_font_index,
                 'footer': args.footer_font_index}[kind]
        if path is None:
            path, default_index = resolve_font(kind)
            index = default_index if index is None else index
        return path, (0 if index is None else index)

    if args.source.resolve() == args.image.resolve():
        raise SystemExit('The artwork source and cover output must be separate files')
    with Image.open(args.source) as source:
        image = source.convert('RGB')
    if image.size != (1024, 1536):
        raise SystemExit('Expected the 1024 × 1536 unlettered cover artwork')

    # where the engraving begins: the first row that is almost entirely paper
    gray = image.convert('L')
    px = gray.load()
    artwork_top = 0
    for y in range(image.height):
        row_bright = sum(1 for x in range(0, image.width, 8) if px[x, y] > 235)
        if row_bright / (image.width / 8) > .9:
            artwork_top = y
            break

    # the plate re-inks onto the book's sheet: paper highlights, charcoal line
    plate = image.crop((0, artwork_top, image.width, image.height)).convert('L')
    plate = ImageOps.autocontrast(plate, cutoff=1)
    image.paste(ImageOps.colorize(plate, black=INK, white=PAPER), (0, artwork_top))
    # the header band goes to plain lacquer, matching the book's --ink
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, image.width, artwork_top), fill=LACQUER)

    title_path, title_index = pick('title')
    sans_path, sans_index = pick('sans')
    footer_path, footer_index = pick('footer')
    title_font = ImageFont.truetype(title_path, 252, index=title_index)

    def sans(size):
        return ImageFont.truetype(sans_path, size, index=sans_index)

    def footer(size):
        return ImageFont.truetype(footer_path, size, index=footer_index)

    def text_at(text, face, left, top, color):
        x0, y0, x1, y1 = draw.textbbox((0, 0), text, font=face)
        if left < 0 or top < 0 or left + x1 - x0 > image.width or top + y1 - y0 > image.height:
            raise SystemExit(f'Text falls outside the cover: {text}')
        draw.text((left - x0, top - y0), text, font=face, fill=color)

    # Shared left alignment connects the title block and footer. The illustration
    # retains its own generous width between these two typographic anchors.
    text_at('AGENT HARNESS ENGINEERING', sans(20), 84, 66, PAPER)
    text_at('\u5fa1\u8206', title_font, 78, 130, PAPER)  # 御舆 (simplified 舆).
    text_at('解码 Agent Harness', footer(48), 84, 415, PAPER)
    draw.line((84, 1358, 940, 1358), fill=CINNABAR, width=2)
    text_at('Claude Code 架构深度剖析', footer(40), 84, 1388, INK)
    text_at('LinTsinghua', footer(34), 84, 1462, INK)

    image.save(args.image, optimize=True)
    print(f'Typeset 御舆 using {title_font.getname()}: {args.image}')


if __name__ == '__main__':
    main()
