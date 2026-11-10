#!/usr/bin/env python3
"""Fail when a published site loses an entry point or a local link target.

The release and Pages jobs publish duplicate files instead of HTTP redirects:
`index.html` is the portal and `book.html` is the Chinese edition. This check
keeps those aliases byte-identical and walks every local href/src so a moved
chapter or a stale product page cannot ship as a 404.

    python scripts/check_site_redirects.py site/
"""
from __future__ import annotations

import argparse
import sys
import urllib.parse
from html.parser import HTMLParser
from pathlib import Path

ALIASES = {
    "index.html": "portal.html",
    "book.html": "yuyu-agent-harness-zh.html",
}
REQUIRED = {
    "portal.html",
    "yuyu-agent-harness-zh.html",
    "yuyu-agent-harness-en.html",
    "beginner-reader.html",
    "beginner-reader.en.html",
    "illustration-gallery.html",
    "knowledge-cards.html",
    "knowledge-cards.en.html",
    "sample-chapter.html",
    "sample-chapter.en.html",
}
SKIP_SCHEMES = {"http", "https", "mailto", "data", "javascript", "tel"}


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids: set[str] = set()
        self.targets: list[str] = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"])
        for name in ("href", "src"):
            if values.get(name):
                self.targets.append(values[name])


def parse_html(path: Path) -> Links:
    parser = Links()
    parser.feed(path.read_text(encoding="utf-8", errors="replace"))
    return parser


def _inside(root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def check(site: Path) -> list[str]:
    failures: list[str] = []
    if not site.is_dir():
        return [f"{site}: not a directory"]
    for name in sorted(REQUIRED | set(ALIASES)):
        if not (site / name).is_file():
            failures.append(f"missing entry point: {name}")
    for alias, target in ALIASES.items():
        alias_path, target_path = site / alias, site / target
        if not alias_path.is_file():
            continue
        if not target_path.is_file():
            failures.append(f"{alias}: alias target {target} is missing")
        elif alias_path.read_bytes() != target_path.read_bytes():
            failures.append(f"{alias}: differs from {target}")

    parsed: dict[Path, Links] = {}
    for page in sorted(site.rglob("*.html")):
        links = parse_html(page)
        parsed[page.resolve()] = links
        for raw in links.targets:
            target = urllib.parse.urlsplit(raw)
            if target.scheme.lower() in SKIP_SCHEMES:
                continue
            relative = urllib.parse.unquote(target.path)
            destination = (page.parent / relative).resolve() if relative else page.resolve()
            if not _inside(site, destination):
                failures.append(f"{page.relative_to(site).as_posix()}: escapes site: {raw}")
                continue
            if relative and not destination.exists():
                failures.append(f"{page.relative_to(site).as_posix()}: missing {raw}")
                continue
            fragment = urllib.parse.unquote(target.fragment)
            if fragment and destination.suffix.lower() == ".html":
                document = parsed.get(destination)
                if document is None and destination.is_file():
                    document = parse_html(destination)
                    parsed[destination] = document
                if document is not None and fragment not in document.ids:
                    failures.append(
                        f"{page.relative_to(site).as_posix()}: missing anchor {raw}")
    return failures


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("site", type=Path)
    args = parser.parse_args(argv)
    failures = check(args.site)
    if failures:
        print("SITE CHECK FAILED:", file=sys.stderr)
        for failure in failures:
            print("  " + failure, file=sys.stderr)
        return 1
    print(f"site check: {args.site} entry points and local links valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
