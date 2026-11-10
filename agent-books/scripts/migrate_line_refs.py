#!/usr/bin/env python3
"""Resolve `file:line` evidence to block spans and report the migration plan.

    python scripts/migrate_line_refs.py                    # JSON to stdout
    python scripts/migrate_line_refs.py --out plan.json    # to a file
    python scripts/migrate_line_refs.py --strict           # exit 2 on gaps

Read-only: markers are proposed, registries are untouched. P2.5 introduces the
dual reader and P2.6 applies the plan.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "yuyu-book"))

from yuyu_book import migrate, plain, registry  # noqa: E402


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--product", default="book",
                        help="which volume to migrate (book, omp); the bare "
                             "registry names belong to the book")
    parser.add_argument("--out", default="-",
                        help="JSON path, or - for stdout (default)")
    parser.add_argument("--strict", action="store_true",
                        help="exit 2 when any ref is ambiguous or missing")
    parser.add_argument("--equivalence", metavar="PATH",
                        help="stage markers, validate both ref forms, write "
                             "a line↔block consistency summary there")
    parser.add_argument("--write", action="store_true",
                        help="insert markers and rewrite registries in place")
    args = parser.parse_args(argv)
    names = plain.registry_names({"product": args.product})
    manifest = registry.load(names["manifest"])
    glosses = registry.load(names["glosses"])
    report = migrate.build_report(manifest, glosses)
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    dual = None
    if args.equivalence:
        dual = migrate.verify_dual(manifest, glosses,
                                   plain.load_plain(manifest)[1], report)
        payload = {"schema_version": 1, "summary": report["summary"],
                   "dual": dual}
        Path(args.equivalence).parent.mkdir(parents=True, exist_ok=True)
        Path(args.equivalence).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8", newline="\n")
    if args.out == "-":
        sys.stdout.write(text)
    else:
        Path(args.out).write_text(text, encoding="utf-8", newline="\n")
    if args.write:
        done = migrate.apply_migration(manifest, glosses, report)
        print(f"wrote {done['refs']} refs, inserted {done['markers']} "
              f"markers, rewrote {', '.join(done['registries'])}",
              file=sys.stderr)
    summary = report["summary"]
    print(f"refs {summary['refs']} ({summary['unique_refs']} unique): "
          f"mapped {summary['mapped']}, ambiguous {summary['ambiguous']}, "
          f"missing {summary['missing']}; blocks {summary['blocks']}",
          file=sys.stderr)
    if args.strict and (summary["ambiguous"] or summary["missing"]):
        return 2
    if dual and dual["mismatches"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
