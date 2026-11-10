"""Separate visible Markdown from examples before checking book requirements."""
from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
import re

import markdown

FENCE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")
INLINE_CODE = re.compile(r"(?<!`)(`+)(?!`)(.*?)(?<!`)\1(?!`)")


@dataclass
class MarkdownContent:
    prose: str
    blocks: list[tuple[str, str]]
    errors: list[str]


def scan_markdown(text: str) -> MarkdownContent:
    visible, blocks, errors = [], [], []
    fence, language, body, start = None, "", [], 0
    in_comment = False
    for number, line in enumerate(text.splitlines(), 1):
        if fence is not None:
            marker = FENCE.match(line)
            if (marker and marker[1][0] == fence[0]
                    and len(marker[1]) >= len(fence) and not marker[2].strip()):
                blocks.append((language, "\n".join(body)))
                fence = None
            else:
                body.append(line)
            visible.append("")
            continue

        fragments = []
        while line:
            if in_comment:
                _, closing, line = line.partition("-->")
                if not closing:
                    break
                in_comment = False
            else:
                comment_start = line.find("<!--")
                code = INLINE_CODE.search(line)
                if code and (comment_start < 0 or code.start() < comment_start):
                    fragments.append(line[:code.end()])
                    line = line[code.end():]
                    continue
                prefix, opening, line = line.partition("<!--")
                fragments.append(prefix)
                if not opening:
                    break
                in_comment = True
        prose = "".join(fragments)
        marker = FENCE.match(prose)
        if marker:
            fence, info = marker[1], marker[2].strip()
            language = info
            body, start = [], number
            visible.append("")
        else:
            visible.append(prose)

    if fence is not None:
        errors.append(f"line {start}: unclosed code fence")
    if in_comment:
        errors.append("unclosed HTML comment")
    return MarkdownContent("\n".join(visible), blocks, errors)


class ImageSources(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sources = []
        self.code_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("pre", "code"):
            self.code_depth += 1
        if tag == "img" and not self.code_depth:
            source = dict(attrs).get("src")
            if source:
                self.sources.append(source)

    def handle_endtag(self, tag):
        if tag in ("pre", "code") and self.code_depth:
            self.code_depth -= 1


def image_sources(prose: str) -> list[str]:
    parser = ImageSources()
    parser.feed(markdown.markdown(prose, extensions=["extra", "sane_lists"]))
    return parser.sources
