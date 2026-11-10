#!/usr/bin/env python3
"""Capture the P0 visual baseline: 20 HTML fragments and 12 page screenshots.

Fragments are byte-exact slices of the built HTML for the block types the
migration must not disturb (cover, contents, chapter head, plain-language
band, keeper note, new-terms card, wide table, landscape plate, sources,
subject index). Screenshots pin how those blocks sit on screen in light and
dark, wide and narrow viewports.

    python scripts/baseline_snapshot.py
    python scripts/baseline_snapshot.py --check     # fragments only

The fragment files are deterministic; the PNGs are environment snapshots
(browser version and font rasterisation), so --check only compares fragments.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DIST = ROOT / "yuyu-book" / "dist"
OUT = ROOT / "docs" / "baseline"

# (name, tag, required class tokens, optional id, optional anchor to start after)
FRAGMENTS = [
    ("cover", "section", ["front-page", "cover"], "cover", None),
    ("toc", "section", ["front-page", "toc"], "toc", None),
    ("chapter-head", "header", ["chapter-head"], None, "ch01"),
    ("lead-band", "div", ["lead-band"], None, "ch01"),
    ("keeper-note", "div", ["keeper"], None, "ch01"),
    ("new-terms", "aside", ["new-terms"], None, "ch01"),
    ("wide-table", "div", ["table-scroll"], None, None),
    ("landscape-plate", "figure", ["diagram", "wide", "landscape"], None,
     None),
    ("sources", "section", ["front-page", "sources"], "sources", None),
    ("subject-index", "section", ["front-page", "back-index"],
     "subject-index", None),
]

SHOTS = [
    # lang, name, selector, width, height, colour scheme, scroll block
    ("zh", "cover", "#cover", 1440, 900, "light", "start"),
    ("zh", "toc", "#toc", 1440, 900, "light", "start"),
    ("zh", "body", "#ch01 h1", 1440, 900, "light", "start"),
    ("zh", "wide-table", "div.table-scroll", 1440, 900, "light", "center"),
    ("zh", "landscape-plate", "figure.diagram.wide.landscape",
     1440, 900, "light", "center"),
    ("zh", "subject-index", "#subject-index", 1440, 900, "light", "start"),
    ("zh", "dark-narrow", "#ch01 h1", 390, 844, "dark", "start"),
    ("en", "cover", "#cover", 1440, 900, "light", "start"),
    ("en", "toc", "#toc", 1440, 900, "light", "start"),
    ("en", "body", "#ch05 h1", 1440, 900, "light", "start"),
    ("en", "wide-table", "div.table-scroll", 1440, 900, "light", "center"),
    ("en", "landscape-plate", "figure.diagram.wide.landscape",
     1440, 900, "light", "center"),
]

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}
TAG = re.compile(
    r"<!--.*?-->|<!\[CDATA\[.*?\]\]>|<!(?!--)[^>]*>"
    r"|<(?P<close>/)?(?P<name>[A-Za-z][\w:-]*)"
    r"(?P<attrs>(?:\"[^\"]*\"|'[^']*'|[^>\"'])*)>",
    re.S)


def class_tokens(attrs: str) -> list[str]:
    found = re.search(r'\bclass="([^"]*)"', attrs)
    return found.group(1).split() if found else []


def id_value(attrs: str) -> str | None:
    found = re.search(r'\bid="([^"]*)"', attrs)
    return found.group(1) if found else None


def find_element(html: str, tag: str, classes: list[str],
                 wanted_id: str | None,
                 after_id: str | None = None) -> tuple[int, int]:
    """Return the (start, end) slice of the first matching element."""
    tokens = list(TAG.finditer(html))
    floor = 0
    if after_id:
        marker = re.search(rf'\bid="{re.escape(after_id)}"', html)
        if not marker:
            raise SystemExit(f"anchor not found: {after_id}")
        floor = marker.start()
    for pos, token in enumerate(tokens):
        if token.start() < floor:
            continue
        name = token.group("name")
        if not name or name.lower() != tag or token.group("close"):
            continue
        attrs = token.group("attrs")
        if wanted_id and id_value(attrs) != wanted_id:
            continue
        if not set(classes).issubset(class_tokens(attrs)):
            continue
        depth = 1
        for later in tokens[pos + 1:]:
            later_name = later.group("name")
            if not later_name or later_name.lower() != tag:
                continue
            if later.group("close"):
                depth -= 1
            elif not later.group("attrs").rstrip().endswith("/"):
                depth += 1
            if depth == 0:
                return token.start(), later.end()
        raise SystemExit(f"unclosed <{tag}> for {classes} {wanted_id}")
    raise SystemExit(f"fragment not found: <{tag}> {classes} {wanted_id}")


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def extract(lang: str, dist: Path) -> dict:
    html = (dist / f"yuyu-agent-harness-{lang}.html").read_text(encoding="utf-8")
    entries = []
    target = OUT / "fragments" / lang
    target.mkdir(parents=True, exist_ok=True)
    for name, tag, classes, wanted_id, after_id in FRAGMENTS:
        start, end = find_element(html, tag, classes, wanted_id, after_id)
        fragment = html[start:end]
        path = target / f"{name}.html"
        path.write_text(fragment, encoding="utf-8", newline="\n")
        entries.append({
            "name": name,
            "selector": {"tag": tag, "classes": classes, "id": wanted_id},
            "file": str(path.relative_to(OUT)).replace("\\", "/"),
            "bytes": len(fragment.encode("utf-8")),
            "sha256": digest(fragment),
        })
        print(f"  fragment {lang}/{name}: {len(fragment.encode('utf-8'))} bytes")
    return {"language": lang, "fragments": entries}


def capture(lang: str, dist: Path) -> dict:
    from playwright.sync_api import sync_playwright

    url = (dist / f"yuyu-agent-harness-{lang}.html").resolve().as_uri()
    out_dir = OUT / "screenshots"
    out_dir.mkdir(parents=True, exist_ok=True)
    entries = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        try:
            for shot_lang, name, selector, width, height, scheme, block in SHOTS:
                if shot_lang != lang:
                    continue
                page = browser.new_page(
                    viewport={"width": width, "height": height},
                    device_scale_factor=1, color_scheme=scheme)
                try:
                    page.goto(url, wait_until="load")
                    page.add_style_tag(content=(
                        "*,*::before,*::after{animation:none!important;"
                        "transition:none!important;caret-color:transparent!important}"
                        "html{scroll-behavior:auto!important}"))
                    page.evaluate("() => document.fonts.ready.then(() => true)")
                    locator = page.locator(selector).first
                    if locator.count() == 0:
                        raise SystemExit(f"selector not found: {selector}")
                    locator.evaluate(
                        "(el, block) => el.scrollIntoView({block, inline: 'nearest'})",
                        block)
                    page.wait_for_timeout(120)
                    path = out_dir / f"{lang}-{name}.png"
                    page.screenshot(path=str(path))
                    entries.append({
                        "language": lang,
                        "name": name,
                        "file": str(path.relative_to(OUT)).replace("\\", "/"),
                        "selector": selector,
                        "viewport": [width, height],
                        "color_scheme": scheme,
                        "bytes": path.stat().st_size,
                        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    })
                    print(f"  screenshot {lang}/{name}: {path.stat().st_size // 1024} KB")
                finally:
                    page.close()
        finally:
            browser.close()
    return {"language": lang, "screenshots": entries}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dist", type=Path, default=DEFAULT_DIST)
    ap.add_argument("--check", action="store_true",
                    help="compare fragments with the committed copies")
    ap.add_argument("--skip-screenshots", action="store_true")
    args = ap.parse_args(argv)
    langs = ("zh", "en")
    if args.check:
        failures = 0
        for lang in langs:
            html = (args.dist / f"yuyu-agent-harness-{lang}.html").read_text(
                encoding="utf-8")
            for name, tag, classes, wanted_id, after_id in FRAGMENTS:
                start, end = find_element(html, tag, classes, wanted_id,
                                          after_id)
                fresh = html[start:end]
                path = OUT / "fragments" / lang / f"{name}.html"
                committed = (path.read_text(encoding="utf-8")
                             if path.exists() else "")
                # Figure ids are generated hashes; the frozen fragment keeps
                # the old build's value as provenance, while the slot itself is
                # what the visual gate protects.
                fresh = re.sub(r"fig-[0-9a-f]{12}", "fig-*", fresh)
                committed = re.sub(r"fig-[0-9a-f]{12}", "fig-*", committed)
                if committed != fresh:
                    print(f"fragment drift: {lang}/{name}", file=sys.stderr)
                    failures += 1
        if failures:
            return 1
        print("fragments match docs/baseline/fragments")
        return 0

    index = {"schema_version": 1, "fragments": [], "screenshots": []}
    for lang in langs:
        index["fragments"].append(extract(lang, args.dist))
    if not args.skip_screenshots:
        for lang in langs:
            index["screenshots"].append(capture(lang, args.dist))
    (OUT / "fragments" / "index.json").write_text(
        json.dumps({"schema_version": 1,
                    "languages": index["fragments"]},
                   ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n")
    if index["screenshots"]:
        (OUT / "screenshots" / "index.json").write_text(
            json.dumps({"schema_version": 1,
                        "languages": index["screenshots"]},
                       ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8", newline="\n")
    print(f"baseline snapshots -> {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
