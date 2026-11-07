#!/usr/bin/env python3
"""yuyu-book: assemble the offline single-file editions of《御舆》.

Usage through the repository entry point:
    python scripts/bookctl.py build --product book --lang both
    python scripts/bookctl.py build --product book --lang en --pdf
    python scripts/bookctl.py check --fast
"""
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

from . import claims, plain, registry
from .app import build_edition, glossary_to_index
from .core import (BOOK_DIR, REPO_ROOT, BuildError, dump_json, load_configs,
                   read_text, unit_stream)




def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--lang", default="both", choices=["zh", "en", "both"])
    ap.add_argument("--pdf", action="store_true")
    ap.add_argument("--check", action="store_true",
                    help="build into a temp dir and only validate")
    ap.add_argument("--out-dir", default=str(BOOK_DIR / "dist"))
    ap.add_argument("--browser", default=None,
                    help="explicit msedge/chrome executable for mermaid & PDF")
    ap.add_argument("--edge", default=None, help="PDF browser executable")
    ap.add_argument("--mermaid", default="render", choices=["render", "source"])
    ap.add_argument("--no-autolink", action="store_true")
    ap.add_argument("--no-plain", action="store_true",
                    help="skip the plain-language layer (marks, panels, lead "
                         "bands, tier chips, principle notes, keeper notes)")
    ap.add_argument("--regen-index", action="store_true")
    ap.add_argument("--manifest", default="manifest.json",
                    help="registry filename under yuyu-book/")
    ap.add_argument("--sources", default="sources.json",
                    help="sources registry filename under yuyu-book/")
    args = ap.parse_args(argv)

    try:
        manifest, sources = load_configs(args.manifest, args.sources)
        if (manifest.get("product") or "book") == "book":
            for warning in claims.validate(
                    claims.load(), claims.manuscript_texts(manifest), sources,
                    release=not args.check):
                print(f"warning: {warning}", file=sys.stderr)
        glosses, paths = ({}, {}) if args.no_plain else plain.load_plain(manifest)
        notes = {} if args.no_plain else plain.load_notes(manifest)
        if not args.no_plain:
            plain.validate_plain(glosses, paths, manifest)
            if notes:
                langs = plain.manifest_langs(manifest)
                unit_texts = {u["id"]: {lang: read_text(REPO_ROOT / u[lang])
                                        for lang in langs if lang in u}
                              for u, _k, _p in unit_stream(manifest)}
                plain.validate_notes(notes, glosses, unit_texts, langs)
        if args.regen_index:
            entries = glossary_to_index(manifest)
            dump_json(BOOK_DIR / "subject-index.json",
                      registry.wrap("subject-index.json", entries))
            zh_n = sum(1 for e in entries if e["zh"]["refs"])
            en_n = sum(1 for e in entries if e["en"]["refs"])
            print(f"subject index: {len(entries)} terms ({zh_n} zh refs, "
                  f"{en_n} en refs)")
            if args.lang == "both" and not args.check:
                pass  # index-only run still produces files; build continues
        langs = ["zh", "en"] if args.lang == "both" else [args.lang]
        out_dir = Path(args.out_dir)
        if args.check:
            out_dir = Path(tempfile.mkdtemp(prefix="yuyu-check-"))
        for lang in langs:
            print(f"[{lang}]")
            build_edition(lang, manifest, sources, mode=args.mermaid,
                          browser=args.browser, autolink=not args.no_autolink,
                          out_dir=out_dir, do_pdf=args.pdf and not args.check,
                          edge=args.edge, glosses=glosses, paths=paths,
                          notes=notes, plain_layer=not args.no_plain)
        print("OK" if not args.check else "CHECK OK")
    except BuildError as e:
        print(f"BUILD FAILED: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
