"""Stable block markers carried by the manuscript itself.

A citable block gets one HTML comment on its own line directly above it:

    <!-- block: ch03.tool-contract -->

The comment is invisible in the book, survives reflow and insertion, and keeps
the ID next to the prose it names. IDs are unit-scoped (`<unit-id>.<slug>`),
unique per unit, and shared by the Chinese and English editions so a registry
entry can name one block in both languages. A marker inside a code fence is an
example, not a marker; only prose counts.

This module validates the markers now. The line-ref → block-ref migration and
the block-boundary parser arrive in P2.4; both use `validate_markers()` to find
the IDs that already exist.
"""
from __future__ import annotations

import re

from .core import FENCE_RE, BuildError
from .model import Block, Diagnostic

MARKER = re.compile(
    r"^\s*<!--\s*block:\s*(?P<id>[a-z0-9][a-z0-9.-]*)\s*-->\s*$")
LOOSE = re.compile(r"<!--\s*block\b", re.I)
ID_RE = re.compile(
    # the unit segment may itself be hyphenated: a second volume's unit ids
    # carry their product prefix (`omp-ch33`), the book's do not (`ch03`)
    r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*\.[a-z0-9]+(?:-[a-z0-9]+)*$")
HEADING_RE = re.compile(r"^(#{1,6})\s+\S")
LIST_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
TABLE_RE = re.compile(r"^\s*\|")
QUOTE_RE = re.compile(r"^\s*>")


def _fail(code: str, file: str, block_id: str, message: str,
          hint: str = "") -> None:
    raise BuildError(str(Diagnostic("error", code, file, block_id, message,
                                    hint)))


def _fence_token(line: str):
    match = FENCE_RE.match(line)
    if not match:
        return None
    token, info = match.group(1), match.group(2).strip()
    return token, info


def validate_markers(text: str, file: str, unit_id: str) -> dict[str, int]:
    """Return {block_id: marker line} and fail on a malformed or dangling one."""
    lines = text.split("\n")
    found: dict[str, int] = {}
    fence = None
    for number, line in enumerate(lines, 1):
        token = _fence_token(line)
        if token:
            mark, info = token
            if fence is None:
                fence = mark
            elif mark[0] == fence[0] and len(mark) >= len(fence) and not info:
                fence = None
            continue
        if fence is not None or not LOOSE.search(line):
            continue
        match = MARKER.match(line)
        if not match:
            _fail("block-marker", file, "",
                  f"malformed block marker on line {number}",
                  "use <!-- block: <unit-id>.<slug> --> on a line of its own")
        block_id = match.group("id")
        if not block_id.startswith(f"{unit_id}.") or not ID_RE.match(block_id):
            _fail("block-id", file, block_id,
                  f"block id on line {number} does not belong to {unit_id}",
                  f"expected {unit_id}.<lowercase-slug>")
        if block_id in found:
            _fail("block-id", file, block_id,
                  f"duplicate block id (lines {found[block_id]} and {number})")
        next_line = number
        while next_line < len(lines) and not lines[next_line].strip():
            next_line += 1
        if next_line >= len(lines):
            _fail("block-marker", file, block_id,
                  "block marker is not followed by a block")
        if LOOSE.search(lines[next_line]):
            _fail("block-marker", file, block_id,
                  "two block markers point at the same block")
        found[block_id] = number
    return found


def strip_markers(text: str) -> str:
    """Remove marker lines outside fences before Markdown sees the source.

    The markers are resolution metadata, not content: an HTML comment between
    two list items makes Python-Markdown close one list and open another. The
    file on disk keeps them so `parse_blocks` can still name each span.
    """
    lines = text.split("\n")
    out: list[str] = []
    fence = None
    for line in lines:
        token = _fence_token(line)
        if token:
            mark, info = token
            if fence is None:
                fence = mark
            elif mark[0] == fence[0] and len(mark) >= len(fence) and not info:
                fence = None
            out.append(line)
            continue
        if fence is None and MARKER.match(line):
            continue
        out.append(line)
    return "\n".join(out)


def parse_blocks(text: str, unit_id: str, lang: str = "") -> list[Block]:
    """Split prose into citable spans, fence-aware and marker-aware.

    A span covers lines `line..end_line` (1-based, inclusive). Headings are
    spans because registry evidence sometimes cites a section heading; a list
    is one span even when items sit on consecutive lines, and a table is one
    span. Blank lines close a span; a marker line names the span that follows
    it, allowing blank lines in between. Code-fence contents never split.
    """
    lines = text.split("\n")
    out: list[Block] = []
    pending = None
    index = 0

    def add(start: int, end: int, kind: str) -> None:
        nonlocal pending
        body = "\n".join(lines[start:end])
        out.append(Block(unit_id, lang, start + 1, kind, body, pending or "",
                         end))
        pending = None

    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        if LOOSE.search(line):
            match = MARKER.match(line)
            if match:
                pending = match.group("id")
            index += 1
            continue
        token = _fence_token(line)
        if token:
            start, mark = index, token[0]
            index += 1
            while index < len(lines):
                close = _fence_token(lines[index])
                if (close and close[0][0] == mark[0]
                        and len(close[0]) >= len(mark) and not close[1]):
                    index += 1
                    break
                index += 1
            add(start, index, "fence")
            continue
        if HEADING_RE.match(line):
            add(index, index + 1, "heading")
            index += 1
            continue
        if QUOTE_RE.match(line):
            start = index
            while index < len(lines) and QUOTE_RE.match(lines[index]):
                index += 1
            add(start, index, "quote")
            continue
        if TABLE_RE.match(line):
            start = index
            while index < len(lines) and TABLE_RE.match(lines[index]):
                index += 1
            add(start, index, "table")
            continue
        if LIST_RE.match(line):
            start = index
            while index < len(lines) and lines[index].strip():
                current = lines[index]
                if (LOOSE.search(current) or FENCE_RE.match(current)
                        or HEADING_RE.match(current)
                        or QUOTE_RE.match(current)
                        or TABLE_RE.match(current)):
                    break
                index += 1
            add(start, index, "list")
            continue
        start = index
        while index < len(lines) and lines[index].strip():
            current = lines[index]
            if (LOOSE.search(current) or FENCE_RE.match(current)
                    or HEADING_RE.match(current)
                    or QUOTE_RE.match(current)
                    or TABLE_RE.match(current)
                    or LIST_RE.match(current)):
                break
            index += 1
        add(start, index, "paragraph")
    return out
