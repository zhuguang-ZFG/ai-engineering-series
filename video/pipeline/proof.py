"""Independent process rebuilds with byte inventories, not repeated serialization."""
from __future__ import annotations

import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path

from . import model


def inventory(directory: Path) -> dict[str, str]:
    return {path.relative_to(directory).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(directory.rglob("*")) if path.is_file()}


def compare_outputs(first: Path, second: Path) -> dict:
    one, two = inventory(first), inventory(second)
    missing_first = sorted(two.keys() - one.keys())
    missing_second = sorted(one.keys() - two.keys())
    changed = sorted(name for name in one.keys() & two.keys() if one[name] != two[name])
    return {"status": "identical" if one and one == two else "different",
            "changed": changed, "missing_first": missing_first,
            "missing_second": missing_second, "sha256": one}


def rebuild(chapter_id: str, *, config_only: bool = False) -> dict:
    """Each child reloads inputs and regenerates all chapter products from scratch."""
    with tempfile.TemporaryDirectory(prefix="yuyu-video-proof-") as temporary:
        destinations = [Path(temporary) / name for name in ("first", "second")]
        for destination in destinations:
            command = [sys.executable, str(Path(__file__).with_name("cli.py")),
                       "build", "--chapter", chapter_id, "--out-dir", str(destination)]
            if not config_only:
                command.append("--assets")
            result = subprocess.run(command, cwd=model.ROOT, capture_output=True,
                                    text=True, encoding="utf-8", errors="replace")
            if result.returncode:
                raise model.VideoError(f"{chapter_id}: independent rebuild failed: "
                                       f"{result.stderr.strip() or result.stdout.strip()}")
        result = compare_outputs(*(path / chapter_id for path in destinations))
    result["processes"] = 2
    result["inputs"] = inventory(model.CHAPTERS / chapter_id)
    result["scope"] = "source/configuration" if config_only else "declared assets"
    result["media"] = "unverified; independent rebuilds do not prove narration or rendered-video quality"
    return result
