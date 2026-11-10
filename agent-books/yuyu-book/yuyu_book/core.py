"""Compatibility facade for the builder's core primitives.

The implementation now lives in focused modules: paths, io, diagnostics,
text, config and units. Existing callers may keep importing ``core``.
"""
from __future__ import annotations

from .config import (GUIDE_FIELDS, MIRRORED_FIELDS, SOURCE_ID_RE,
                     SOURCE_REQUIRED, expected_ids, load_configs,
                     unit_stream, validate_configs)
from .diagnostics import BuildError
from .io import dump_json, load_json, read_text
from .paths import BOOK_DIR, CACHE_DIR, REPO_ROOT
from .text import FENCE_RE, HAN_RE, INDEX_CN_LETTER
from .units import (EN_PATTERNS, ILL_NAME_RE, ZH_PATTERNS, IllusBlock,
                    MermaidBlock, Unit, extract_illustrations,
                    extract_mermaid, load_unit, normalize_h1)

__all__ = [
    "BOOK_DIR", "REPO_ROOT", "CACHE_DIR",
    "GUIDE_FIELDS", "SOURCE_REQUIRED", "SOURCE_ID_RE", "MIRRORED_FIELDS",
    "HAN_RE", "INDEX_CN_LETTER", "FENCE_RE",
    "BuildError", "read_text", "load_json", "dump_json",
    "MermaidBlock", "IllusBlock", "Unit",
    "ZH_PATTERNS", "EN_PATTERNS", "ILL_NAME_RE",
    "extract_mermaid", "extract_illustrations", "normalize_h1", "load_unit",
    "expected_ids", "unit_stream", "validate_configs", "load_configs",
]
