"""Original book example: bounded, read-only inventory; no external requests.

This is ordinary in-process Python, not a sandbox against malicious plugins.
The caller should not mutate the directory tree concurrently with a scan.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

SCHEMA = {
    "name": "book_inventory",
    "description": "List Markdown files under the configured book workspace.",
    "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
}


def _linked(path: Path) -> bool:
    return path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction())


def _root_path(value: str | Path) -> Path:
    if not str(value).strip():
        raise ValueError("Configure a non-empty root directory first.")
    candidate = Path(value).expanduser().absolute()
    if any(_linked(part) for part in (candidate, *candidate.parents)):
        raise ValueError("Linked root directories are not accepted.")
    if not candidate.is_dir():
        raise ValueError("Configured root directory does not exist.")
    return candidate.resolve(strict=True)


def make_inventory_handler(root: str | Path, *, limit: int = 100, max_entries: int = 10000):
    """Validate configuration early, then build a standard Hermes tool handler."""
    if limit < 1 or max_entries < 1:
        raise ValueError("Scan limits must be positive.")
    configured = _root_path(root)

    def handler(params, **kwargs) -> str:
        if not isinstance(params, dict) or params:
            return json.dumps({"error": "This tool accepts an empty object only."})
        files: list[str] = []
        visited = 0

        def stop_on_error(error: OSError):
            raise error

        try:
            if _root_path(configured) != configured:
                raise ValueError("Configured root changed.")
            for current, directories, names in os.walk(
                configured, followlinks=False, onerror=stop_on_error
            ):
                parent = Path(current)
                directories[:] = sorted(
                    name for name in directories
                    if not name.startswith(".") and not _linked(parent / name)
                )
                visited += len(directories) + len(names)
                if visited > max_entries:
                    return json.dumps({"error": "Scan entry budget exceeded."})
                for name in sorted(names):
                    path = parent / name
                    if path.suffix.lower() != ".md" or _linked(path) or not path.is_file():
                        continue
                    resolved = path.resolve(strict=True)
                    if not resolved.is_relative_to(configured):
                        continue
                    if len(files) == limit:
                        return json.dumps({"files": files, "truncated": True}, ensure_ascii=False)
                    files.append(resolved.relative_to(configured).as_posix())
        except (OSError, ValueError):
            return json.dumps({"error": "Workspace scan failed; check root and permissions."})
        return json.dumps({"files": files, "truncated": False}, ensure_ascii=False)

    return handler


def register(ctx):
    handler = make_inventory_handler(ctx.get_config("root", ""))
    registration = ctx.register_tool(
        name="book_inventory", toolset="book_inventory", schema=SCHEMA, handler=handler
    )
    if registration is None:
        raise RuntimeError("book_inventory registration was not accepted by the host.")
