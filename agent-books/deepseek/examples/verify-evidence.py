"""Check the normalized text digests used by the DeepSeek component experiment."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def normalized_sha256(path: Path) -> str:
    text = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n").rstrip("\n") + "\n"
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path,
                        help="Directory containing the pinned Cordis src/*.ts files")
    args = parser.parse_args()
    examples = Path(__file__).resolve().parent
    facts_dir = examples.parent / "facts"
    facts = json.loads((facts_dir / "cordis-20261110.json").read_text(encoding="utf-8"))
    review_facts = json.loads((facts_dir / "review-lab-20261110.json").read_text(encoding="utf-8"))
    if review_facts["source"]["commit"] != facts["source"]["commit"]:
        raise SystemExit("The two experiment records must reference the same source commit")
    checked = 0
    for directory, records in ((args.source_root, facts["source_sha256"]),
                               (examples, facts["example_sha256"]),
                               (examples, review_facts["example_sha256"])):
        for name, expected in records.items():
            actual = normalized_sha256(directory / name)
            if actual != expected:
                raise SystemExit(f"Digest mismatch: {name}; expected {expected}, got {actual}")
            checked += 1
    print(f"Verified {checked} source/example digests at {facts['source']['commit']}")


if __name__ == "__main__":
    main()
