#!/usr/bin/env python3
"""Check visible product-page layout at narrow/wide sizes and retain screenshots."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'yuyu-book'))
from yuyu_book.pdf import _launch

PAGES = ('portal.html', 'beginner-reader.html', 'beginner-reader.en.html', 'illustration-gallery.html')


def check(directory: Path, destination: Path) -> list[str]:
    from playwright.sync_api import sync_playwright
    errors = []
    destination.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = _launch(playwright, None)
        try:
            for width in (320, 1280):
                for scheme in ('light', 'dark'):
                    context = browser.new_context(viewport={'width': width, 'height': 900}, color_scheme=scheme, reduced_motion='reduce', java_script_enabled=False)
                    try:
                        page = context.new_page()
                        for name in PAGES:
                            path = directory / name
                            if not path.is_file():
                                errors.append(f'{name}: missing product page')
                                continue
                            page.goto(path.resolve().as_uri(), wait_until='load')
                            page.evaluate('document.fonts.ready')
                            result = page.evaluate('''() => {
                                const clipped = [...document.querySelectorAll('h1,h2,.st-body,.st-art,.c,.bar')].filter(e => {
                                    const r=e.getBoundingClientRect();
                                    return r.width && (r.left < -1 || r.right > innerWidth + 1);
                                }).map(e=>e.tagName+'.'+e.className);
                                return {width:document.documentElement.scrollWidth, viewport:innerWidth, clipped,
                                    headings:[...document.querySelectorAll('h1')].map(e=>e.textContent.trim())};
                            }''')
                            if result['width'] > width + 1 or result['clipped']:
                                errors.append(f'{name}/{width}/{scheme}: clipped layout {result}')
                            if len(result['headings']) != 1 or not result['headings'][0]:
                                errors.append(f'{name}/{width}/{scheme}: missing readable title')
                            page.screenshot(path=str(destination / f'{Path(name).stem}-{width}-{scheme}.png'))
                    finally:
                        context.close()
        finally:
            browser.close()
    (destination / 'report.json').write_text(json.dumps({'errors':errors}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pages', type=Path, default=ROOT/'docs')
    parser.add_argument('--out-dir', type=Path, default=ROOT/'.scratch/visual-check')
    args = parser.parse_args(argv)
    errors = check(args.pages, args.out_dir)
    for error in errors:
        print(error, file=sys.stderr)
    print(f'visual layout: {len(errors)} failures; screenshots: {args.out_dir}')
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
