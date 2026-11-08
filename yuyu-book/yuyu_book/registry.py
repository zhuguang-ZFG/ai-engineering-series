"""Versioned registry loading for the JSON files beside the manuscript.

Each registry declares its own `schema_version`. The loader is the only place
that knows how to read one, so a future shape change lands in a migration
function instead of a compatibility branch scattered through the builder.

`subject-index.json` is a list by nature: its version lives in an envelope
(`{"schema_version": 1, "entries": [...]}`), and `load()` hands callers the
list. Every other registry is an object; the loader strips the version key so
consumers never see it.

A missing `schema_version` is read as version 0 and migrated in memory. Files
are only rewritten by an explicit command (`build.py --regen-index`), never as
a side effect of loading.
"""
from __future__ import annotations

import json
from pathlib import Path

BOOK_DIR = Path(__file__).resolve().parent.parent
CURRENT = 1

FILES = (
    "manifest.json",
    "manifest-omp.json",
    "manifest-pi.json",
    "glosses.json",
    "glosses-omp.json",
    "glosses-pi.json",
    "sources.json",
    "sources-omp.json",
    "sources-pi.json",
    "notes.json",
    "notes-omp.json",
    "notes-pi.json",
    "reading-paths.json",
    "reading-paths-omp.json",
    "reading-paths-pi.json",
    "revisions.json",
    "revisions-omp.json",
    "revisions-pi.json",
    "subject-index.json",
)

SUBJECT_INDEX = "subject-index.json"


def _fail(message: str, *, code: str = "registry", file: str = "",
          block_id: str = "") -> None:
    # Imported lazily: core imports this module inside load_configs(), and a
    # module-level import here would close the cycle.
    from .core import BuildError
    from .model import Diagnostic
    raise BuildError(str(Diagnostic("error", code, file, block_id, message)))


def _migrate_v0(name: str, payload: dict) -> dict:
    """Version 0 is "no envelope": the payload is already the final shape."""
    return payload


MIGRATIONS = {0: _migrate_v0}


def migrate(name: str, data):
    """Return the payload for a parsed registry, applying migrations in memory."""
    if name == SUBJECT_INDEX and isinstance(data, list):
        data = {"schema_version": 0, "entries": data}
    if not isinstance(data, dict):
        _fail("registry must be a JSON object", code="registry-shape",
              file=name)
    version = data.get("schema_version", 0)
    if not isinstance(version, int) or isinstance(version, bool) or version < 0:
        _fail("schema_version must be a non-negative integer",
              code="registry-version", file=name)
    if version > CURRENT:
        _fail(f"schema_version {version} is newer than this builder "
              f"supports ({CURRENT}); update yuyu-book instead of editing "
              "the registry", code="registry-version", file=name)
    payload = {key: value for key, value in data.items()
               if key != "schema_version"}
    while version < CURRENT:
        migration = MIGRATIONS.get(version)
        if migration is None:
            _fail(f"no migration from schema_version {version}",
                  code="registry-version", file=name)
        payload = migration(name, payload)
        version += 1
    if name == SUBJECT_INDEX:
        entries = payload.get("entries")
        if not isinstance(entries, list):
            _fail("entries must be a JSON array", code="registry-shape",
                  file=name)
        return entries
    return payload


def load(name: str):
    """Read a registry from `yuyu-book/` and return its migrated payload."""
    if name not in FILES:
        _fail("unknown registry", code="registry-unknown", file=name)
    path = BOOK_DIR / name
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        _fail("registry is missing", code="registry-missing", file=name)
    except json.JSONDecodeError as exc:
        _fail(f"invalid JSON at line {exc.lineno}: {exc.msg}",
              code="registry-json", file=name)
    return migrate(name, data)


def wrap(name: str, payload):
    """Serialize a payload into the on-disk shape with the current version."""
    if name == SUBJECT_INDEX:
        return {"schema_version": CURRENT, "entries": payload}
    if not isinstance(payload, dict):
        _fail("payload must be a JSON object", code="registry-shape",
              file=name)
    return {"schema_version": CURRENT, **payload}
