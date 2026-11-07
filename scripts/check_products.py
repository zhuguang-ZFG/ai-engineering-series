#!/usr/bin/env python3
"""Run product adapters twice, require exact content equality and valid local links."""
from __future__ import annotations

import hashlib
import subprocess
import sys
import urllib.parse
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATORS = ["build_beginner_reader.py", "build_illustration_gallery.py",
              "build_knowledge_cards.py", "build_sample_chapter.py",
              "build_site_indices.py", "build_site_portal.py"]
OUTPUTS = ["beginner-reader.html", "beginner-reader.en.html", "illustration-gallery.html",
           "knowledge-cards.html", "knowledge-cards.en.html", "sample-chapter.html",
           "sample-chapter.en.html", "search-index.json", "concept-map.json", "language-map.json",
           "portal.html"]


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.hrefs = set(), []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"])
        if tag == "a" and values.get("href"):
            self.hrefs.append(values["href"])


def main() -> int:
    snapshots = []
    for _pass in range(2):
        for name in GENERATORS:
            subprocess.run([sys.executable, str(ROOT / "scripts" / name)], cwd=ROOT, check=True)
        snapshots.append({name: hashlib.sha256((ROOT / "docs" / name).read_bytes()).hexdigest()
                          for name in OUTPUTS})
    changed = [name for name in OUTPUTS if snapshots[0][name] != snapshots[1][name]]
    if changed:
        raise ValueError(f"non-idempotent products: {changed}")
    parsed = {}
    for name in OUTPUTS:
        if name.endswith(".html"):
            document = Links()
            document.feed((ROOT / "docs" / name).read_text(encoding="utf-8"))
            parsed[name] = document
    failures = []
    for name, document in parsed.items():
        for href in document.hrefs:
            link = urllib.parse.urlsplit(href)
            if link.scheme or link.netloc:
                continue
            target_name = urllib.parse.unquote(link.path) or name
            if target_name in parsed:
                if link.fragment and urllib.parse.unquote(link.fragment) not in parsed[target_name].ids:
                    failures.append(f"{name}: missing target {href}")
            elif link.path and not (ROOT / "docs" / target_name).exists():
                # The deployment flattens built books beside product pages.
                published = {"yuyu-agent-harness-zh.html", "yuyu-agent-harness-en.html", "yuyu-omp-zh.html",
                             "yuyu-agent-harness-zh.pdf", "yuyu-agent-harness-en.pdf", "yuyu-omp-zh.pdf"}
                if target_name not in published and not target_name.startswith("../"):
                    failures.append(f"{name}: missing file {href}")
    if failures:
        raise ValueError("\n".join(failures))
    print(f"products: {len(OUTPUTS)} byte-identical outputs; local anchors checked")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"PRODUCT CHECK FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1)
