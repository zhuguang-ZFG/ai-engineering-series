"""Filesystem anchors shared by the builder."""
from __future__ import annotations

from pathlib import Path

BOOK_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BOOK_DIR.parent
CACHE_DIR = BOOK_DIR / ".cache"
