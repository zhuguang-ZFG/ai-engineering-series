"""Package the prompt volume's offline exercises without caches or local runs."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FOLDERS = ("materials", "cases", "evaluation", "examples", "prompts", "evidence", "illustrations")
EXTENSIONS = {".md", ".json", ".txt", ".py", ".svg"}


def package(output):
    paths = [ROOT / "LICENSE", ROOT / "prompt/PACKAGE-README.md"]
    paths.extend(sorted((ROOT / "prompt").glob("*.md")))
    for folder in FOLDERS:
        paths.extend(sorted(path for path in (ROOT / "prompt" / folder).glob("*")
                            if path.is_file() and path.suffix in EXTENSIONS))
    paths.extend(ROOT / "tests" / name for name in
                 ("test_prompt_workshop.py", "test_prompt_exercise.py"))
    files = {"README.md": (ROOT / "prompt/PACKAGE-README.md").read_bytes()}
    for path in sorted(set(paths)):
        name = path.relative_to(ROOT).as_posix()
        files[name] = path.read_bytes()
    edition = json.loads((ROOT / "yuyu-book/manifest-prompt.json").read_text(encoding="utf-8"))
    manifest = {"version": edition["version"], "kind": "offline_teaching_sources",
                "sha256": {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}}
    files["package-manifest.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=output.parent, suffix=".zip", delete=False) as stream:
        temporary = Path(stream.name)
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name, data in sorted(files.items()):
                info = zipfile.ZipInfo(name, date_time=(2026, 11, 10, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, data)
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)
    return {"path": str(output), "files": len(files), "bytes": output.stat().st_size,
            "sha256": hashlib.sha256(output.read_bytes()).hexdigest()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(package(args.output), ensure_ascii=False, indent=2))
