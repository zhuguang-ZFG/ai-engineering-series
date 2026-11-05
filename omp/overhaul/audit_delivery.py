"""Check Omp illustration coverage, glossary links and English reservation."""
from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

if __package__:
    from .markdown_scan import image_sources, scan_markdown
else:
    from markdown_scan import image_sources, scan_markdown

ROOT = Path(__file__).resolve().parents[2]


def load_json(root: Path, name: str) -> dict:
    try:
        data = json.loads((root / "yuyu-book" / name).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as error:
        raise ValueError(f"{name}: {error}") from error
    if not isinstance(data, dict):
        raise ValueError(f"{name}: registry must be a JSON object")
    return {key: value for key, value in data.items() if key != "schema_version"}


def check(root: Path = ROOT) -> list[str]:
    errors = []
    try:
        manifest = load_json(root, "manifest-omp.json")
        glossary = load_json(root, "glosses-omp.json")
        book_glossary = load_json(root, "glosses.json")
    except ValueError as error:
        return [str(error)]
    diagram_count = 0
    groups = [(manifest["front"]["id"], [manifest["front"]], False)]
    groups.extend((part["id"], part["units"], True) for part in manifest["parts"])
    groups.append(("appendices", manifest["appendices"], False))
    for group_id, units, requires_diagram in groups:
        part_count = 0
        for unit in units:
            manuscript = root / unit["zh"]
            try:
                text = manuscript.read_text(encoding="utf-8")
            except (OSError, UnicodeError) as error:
                errors.append(f"{unit['id']}: cannot read {unit['zh']}: {error}")
                continue
            content = scan_markdown(text)
            errors.extend(f"{unit['id']}: {error}" for error in content.errors)
            part_count += sum(language == "mermaid" for language, _ in content.blocks)
            for image in image_sources(content.prose):
                url = urlsplit(image)
                if url.scheme or url.netloc or not url.path:
                    continue
                if not (manuscript.parent / unquote(url.path)).is_file():
                    errors.append(f"{unit['id']}: missing image {image}")
        diagram_count += part_count
        if requires_diagram and not part_count:
            errors.append(f"{group_id}: no Mermaid diagram")
    if diagram_count < 12:
        errors.append(f"expected at least 12 Mermaid diagrams, got {diagram_count}")

    shared = 0
    for identifier, term in glossary.items():
        target = term.get("shared_with")
        if target is not None:
            if not isinstance(target, str) or not target:
                errors.append(f"{identifier}: shared_with must be a non-empty glossary ID")
            elif target not in book_glossary:
                errors.append(f"{identifier}: unknown shared glossary ID {target}")
            else:
                shared += 1
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
