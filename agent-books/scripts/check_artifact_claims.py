#!/usr/bin/env python3
"""Both READMEs quote the printed book; this checks the quotes against a build.

Two of the numbers are the size of each single-file HTML — those come out the
same on every machine. The page counts are the CI/Noto CJK sheet count: a
build with another CJK face paginates differently (Microsoft YaHei on Windows
runs both editions longer), so to see this pass locally, point it at the
artifact directory CI produced, not at your own dist.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# doc, how the PDF sheet count is claimed, how the HTML size is claimed
CLAIMS = [
    ("README.md",
     re.compile(r"PDF（中文版 (\d+) 页 / [\d.]+ MB，英文版 (\d+) 页 / [\d.]+ MB）"),
     re.compile(r"单文件 HTML（中文版 ([\d.]+) MB / 英文版 ([\d.]+) MB）")),
    ("en/README.md",
     re.compile(r"PDF \((\d+) pages / [\d.]+ MB in Chinese, "
                r"(\d+) pages / [\d.]+ MB in English\)"),
     re.compile(r"HTML file \(([\d.]+) MB Chinese / ([\d.]+) MB English\)")),
]


def pages(pdf: Path) -> int:
    import fitz  # PyMuPDF, already a book-build dependency
    doc = fitz.open(str(pdf))
    try:
        return doc.page_count
    finally:
        doc.close()


def main(dist: Path) -> int:
    bad, missing = [], []
    for doc, pdf_rx, html_rx in CLAIMS:
        readme = (ROOT / doc).read_text(encoding="utf-8")

        m = pdf_rx.search(readme)
        if not m:
            missing.append(f"{doc}: no PDF page claim matches — the wording "
                           "changed; re-pin the pattern in this script")
        else:
            for lang, claimed in (("zh", int(m.group(1))),
                                  ("en", int(m.group(2)))):
                pdf = dist / f"yuyu-agent-harness-{lang}.pdf"
                if not pdf.exists():
                    missing.append(f"{pdf.name}: no PDF here — run "
                                   "`python scripts/bookctl.py build --lang both --pdf` "
                                   "or point this script at the CI artifact dir")
                    continue
                got = pages(pdf)
                print(f"  {doc}: {pdf.name} has {got} pages, README says "
                      f"{claimed}  [{'ok' if got == claimed else 'STALE'}]")
                if got != claimed:
                    bad.append(f"{doc} / {lang}: the book prints {got} pages, "
                               f"the README says {claimed}")

        m = html_rx.search(readme)
        if not m:
            missing.append(f"{doc}: no HTML size claim matches — the wording "
                           "changed; re-pin the pattern in this script")
        else:
            for lang, claimed in (("zh", m.group(1)), ("en", m.group(2))):
                html = dist / f"yuyu-agent-harness-{lang}.html"
                if not html.exists():
                    missing.append(f"{html.name}: no HTML here — build the "
                                   "book first")
                    continue
                got = f"{html.stat().st_size / 1e6:.1f}"
                print(f"  {doc}: {html.name} is {got} MB, README says "
                      f"{claimed}  [{'ok' if got == claimed else 'STALE'}]")
                if got != claimed:
                    bad.append(f"{doc} / {lang}: the reader HTML is {got} MB, "
                               f"the README says {claimed}")

    if missing:
        print("\n".join(["cannot check README's artifact claims:"] + missing))
        return 1
    if bad:
        print("\n".join(["README's artifact claims are stale:"] + bad))
        return 1
    print("both READMEs match the build: page counts and file sizes")
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "yuyu-book" / "dist"))
