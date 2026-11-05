"""Check Omp illustration coverage, glossary links and English reservation."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_json(root: Path, name: str) -> dict:
    data = json.loads((root / "yuyu-book" / name).read_text(encoding="utf-8"))
    return {key: value for key, value in data.items() if key != "schema_version"}


def check(root: Path = ROOT) -> list[str]:
    errors = []
    manifest = load_json(root, "manifest-omp.json")
    diagram_count = 0
    for part in manifest["parts"]:
        part_count = 0
        for unit in part["units"]:
            manuscript = root / unit["zh"]
            text = manuscript.read_text(encoding="utf-8")
            part_count += len(re.findall(r"(?m)^```mermaid\s*$", text))
            for image in re.findall(r"!\[[^\]]*\]\((images/[^)]+)\)", text):
                if not (manuscript.parent / image).is_file():
                    errors.append(f"{unit['id']}: missing image {image}")
        diagram_count += part_count
        if not part_count:
            errors.append(f"{part['id']}: no Mermaid diagram")
    if diagram_count < 12:
        errors.append(f"expected at least 12 Mermaid diagrams, got {diagram_count}")

    glossary = load_json(root, "glosses-omp.json")
    book_glossary = load_json(root, "glosses.json")
    shared = 0
    for identifier, term in glossary.items():
        target = term.get("shared_with")
        if target:
            shared += 1
            if target not in book_glossary:
                errors.append(f"{identifier}: unknown shared glossary ID {target}")
        definition = json.dumps({key: term.get(key) for key in ("plain", "why", "analogy")}, ensure_ascii=False)
        if re.search(r"QueryEngine|55\s*个?工具|89\s*(?:个\s*)?Flags?", definition, re.I):
            errors.append(f"{identifier}: book implementation leaked into Omp definition")
    if shared < 20:
        errors.append(f"expected at least 20 related glossary entries, got {shared}")
    if manifest.get("langs") != ["zh"]:
        errors.append("Omp English reservation must keep langs=['zh']")
    for name in ("README.md", "STATUS.md"):
        path = root / "en" / "omp" / name
        if not path.is_file():
            errors.append(f"missing English reservation: {name}")
        elif re.search(r"[\u4e00-\u9fff]", path.read_text(encoding="utf-8")):
            errors.append(f"untranslated Chinese in en/omp/{name}")
    return errors


def main() -> int:
    errors = check()
    for error in errors:
        print(error)
    print(f"Omp delivery audit: {len(errors)} errors")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
