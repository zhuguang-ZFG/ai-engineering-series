#!/usr/bin/env python3
"""Check repository Markdown links, fences, Mermaid display pitfalls and the
plate spacing the book promises its readers.

This dependency-free check does not replace Mermaid parsing or visual review.
"""
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]

# video/ is a local production workspace: renders, scratch scripts and vendored
# toolchains that ship their own already-broken Markdown. Authored video docs
# live in docs/video/ and stay checked.
SKIP_ROOTS = {'video'}

# How long a reader may go without a picture. A wall is the running prose
# between two visual breaks (a plate, a table, a fenced block); these ceilings
# are the worst wall each edition actually measures today, so the check goes
# red the moment a wall grows or a new one opens up. The fix is a plate; a
# raised ceiling needs a reason in the commit message.
WALL_CEILING = {'zh': 2885, 'en': 8049}
WALL_REPORT = 3
WALL_PROSE = re.compile(r'[一-鿿A-Za-z0-9]')
WALL_MARKUP = re.compile(r'[#*`>|\[\]()!:\s]')


def book_units(root):
    """Every assembled unit path, per language, straight from the manifest."""
    manifest = json.loads(
        (root / 'yuyu-book' / 'manifest.json').read_text(encoding='utf-8'))
    out = {'zh': [], 'en': []}
    front = manifest.get('front')
    groups = [*manifest['parts'],
              {'units': [front] if isinstance(front, dict) else front or []},
              {'units': manifest.get('appendices', [])}]
    for group in groups:
        for unit in group.get('units', []):
            for lang in ('zh', 'en'):
                if unit.get(lang):
                    out[lang].append(unit[lang])
    return out


def prose_walls(lines):
    """(chars, first_line, last_line, heading) for each unbroken prose wall."""
    walls = []
    chars, start, heading = 0, None, ''
    fence = None
    for number, line in enumerate(lines, 1):
        marker = re.match(r'^\s*(`{3,}|~{3,})(.*)$', line)
        if marker:
            token, info = marker.groups()
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence) \
                    and not info.strip():
                fence = None
            if chars:
                walls.append((chars, start, number - 1, heading))
                chars, start = 0, None
            continue
        if fence:
            continue
        if re.match(r'^\s*\|', line):
            if chars:
                walls.append((chars, start, number - 1, heading))
                chars, start = 0, None
            continue
        if WALL_PROSE.search(line) is None:
            continue
        if chars == 0 and start is None:
            start = number
        head = re.match(r'^#{2,4}\s+(.*)', line)
        if head:
            heading = head.group(1).strip()
        chars += len(WALL_PROSE.findall(WALL_MARKUP.sub('', line)))
    if chars:
        walls.append((chars, start, len(lines), heading))
    return walls


def wall_errors(root):
    """Over-long walls, plus the longest of each language for the next round."""
    errors, longest = [], []
    for lang, paths in book_units(root).items():
        rows = []
        for rel in paths:
            path = root / rel
            if not path.is_file():
                continue
            lines = path.read_text(encoding='utf-8').splitlines()
            for chars, first, last, heading in prose_walls(lines):
                rows.append((chars, lang, rel, first, last, heading))
                if chars > WALL_CEILING[lang]:
                    errors.append(
                        f'{rel}:{first}-{last}: {chars} characters of prose '
                        f'with no plate between the breaks (limit '
                        f'{WALL_CEILING[lang]}, section {heading!r}) -- '
                        f'draw a diagram, do not raise the ceiling')
        rows.sort(key=lambda row: -row[0])
        longest += rows[:WALL_REPORT]
    return errors, longest


def check(root=ROOT):
    errors = []
    files = sorted(
        path for path in root.rglob('*.md')
        if not any(part.startswith('.') or part == 'node_modules'
                   for part in path.relative_to(root).parts)
        and path.relative_to(root).parts[0] not in SKIP_ROOTS
    )
    diagrams = 0
    for path in files:
        if any(part.startswith('.') for part in path.relative_to(root).parts):
            continue
        fence = None
        visible = []
        mermaid = False
        for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
            marker = re.match(r'^\s*(`{3,}|~{3,})(.*)$', line)
            if marker:
                token, info = marker.groups()
                if fence is None:
                    fence = token
                    mermaid = info.strip() == 'mermaid'
                    diagrams += int(mermaid)
                elif token[0] == fence[0] and len(token) >= len(fence) and not info.strip():
                    fence = None
                    mermaid = False
                continue
            if fence:
                if mermaid and r'\n' in line:
                    errors.append(f'{path.relative_to(root)}:{number}: literal \\n in Mermaid; use <br/>')
                continue
            visible.append((number, line))
        if fence:
            errors.append(f'{path.relative_to(root)}: unclosed code fence')
        for number, line in visible:
            links = re.findall(r'\]\(([^\s)]+)(?:\s+"[^"]*")?\)', line)
            links += re.findall(r'(?:src|href|srcset)="([^"]+)"', line)
            for link in links:
                url = urlsplit(link.strip('<>'))
                if url.scheme or url.netloc or not url.path:
                    continue
                target = (path.parent / unquote(url.path)).resolve()
                if not target.exists():
                    errors.append(f'{path.relative_to(root)}:{number}: missing target {link}')
    walls, longest = wall_errors(root)
    errors += walls
    return files, diagrams, errors, longest


if __name__ == '__main__':
    files, diagrams, errors, longest = check()
    for error in errors:
        print(error)
    for chars, lang, rel, first, last, heading in longest:
        print(f'  longest wall [{lang}] {chars}: {rel}:{first}-{last} {heading}')
    print(f'{len(files)} Markdown files, {diagrams} Mermaid diagrams, {len(errors)} errors')
    sys.exit(bool(errors))
