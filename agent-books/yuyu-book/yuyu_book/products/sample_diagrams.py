"""Reviewed sample plates: source-bound SVGs, independent of host font metrics."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .. import mermaid
from ..core import BuildError, read_text
from ..paths import BOOK_DIR

DIRECTORY = BOOK_DIR / 'sample-diagrams'


def source_digest(block) -> str:
    return hashlib.sha256(block.src.encode('utf-8')).hexdigest()


def load(blocks, captions, directory: Path = DIRECTORY):
    path = directory / 'manifest.json'
    if not path.is_file():
        raise BuildError('sample diagrams missing; run scripts/build_sample_chapter.py --refresh-diagrams')
    manifest = json.loads(read_text(path))
    entries = manifest.get('diagrams', {})
    result = {}
    for block in blocks:
        entry = entries.get(block.uid, {})
        if entry.get('source_sha256') != source_digest(block):
            raise BuildError(f'sample diagram {block.uid}: source changed; regenerate and review plates')
        svg_path = directory / f'{block.uid}.svg'
        if not svg_path.is_file():
            raise BuildError(f'sample diagram {block.uid}: SVG missing')
        svg = read_text(svg_path)
        if hashlib.sha256(svg.encode('utf-8')).hexdigest() != entry.get('svg_sha256'):
            raise BuildError(f'sample diagram {block.uid}: reviewed SVG digest mismatch')
        result[block.uid] = (captions[block.uid], svg)
    return result


def refresh(editions, directory: Path = DIRECTORY):
    entries = {}
    directory.mkdir(parents=True, exist_ok=True)
    for blocks, captions in editions:
        rendered = mermaid.render_all(blocks, captions)
        for block in blocks:
            svg = rendered[block.uid][1]
            (directory / f'{block.uid}.svg').write_text(svg, encoding='utf-8', newline='\n')
            entries[block.uid] = {'source_sha256': source_digest(block),
                                  'svg_sha256': hashlib.sha256(svg.encode('utf-8')).hexdigest()}
    manifest = {'schema_version':1, 'purpose':'Reviewed chapter-2 sample plates; source changes require regeneration and review.', 'diagrams':entries}
    (directory/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
