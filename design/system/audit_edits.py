#!/usr/bin/env python3
"""Post-commit audit: did a de-AI edit reach inside a code block, a heading, a
table, or a figure? The appliers gate on fence state now, but the first batch
went in with a naive ``` toggle and two quoted terminal outputs lost their
emoji. This reads git history, so it can prove the current tree is clean.

    python design/system/audit_edits.py            # every de-AI commit
    python design/system/audit_edits.py 97e522b    # one commit
"""
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fences  # noqa: E402

BOOK = "book/book.md"
HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


def git(args):
    return subprocess.run(["git"] + args, capture_output=True, cwd=Path(__file__).parents[2]).stdout.decode("utf-8", "replace")


def protect_state(lines):
    """Tag every line with the structure a rewrite must not touch.

    Blockquotes are prose and are fair game (R2/R4 live in them); headings,
    tables, figure markup and code are data or anchors, so an edit there is a
    finding regardless of intent.
    """
    coded = list(fences.code_state(lines))
    state = []
    in_table = False
    for i, line in enumerate(lines):
        s = line.strip()
        if coded[i]:
            state.append("code")
            continue
        if s.startswith("|"):
            in_table = True
            state.append("table")
            continue
        if in_table and s:
            in_table = False
        if s.startswith("#"):
            state.append("heading")
        elif s.startswith(("!", "<")) or "assets/handdraw/" in line or "assets/stacks/" in line:
            state.append("figure")
        else:
            state.append("prose")
    return state


def audit(sha):
    parent = git(["show", f"{sha}^:{BOOK}"]).split("\n")
    state = protect_state(parent)
    diff = git(["diff", "-U0", "--no-color", f"{sha}^", sha, "--", BOOK]).split("\n")
    hits, removed = {k: 0 for k in ("code", "table", "heading", "figure")}, 0
    detail = []
    idx = -1
    for line in diff:
        if line.startswith(("--- ", "+++ ")):
            continue
        m = HUNK.match(line)
        if m:
            idx = int(m.group(1)) - 1
            continue
        if line.startswith("-"):
            removed += 1
            kind = state[idx] if 0 <= idx < len(state) else "prose"
            if kind != "prose":
                hits[kind] += 1
                detail.append((sha, idx + 1, kind, line[1:].strip()[:60]))
            idx += 1
    return removed, hits, detail


def main():
    shas = sys.argv[1:] or [
        l.split()[0]
        for l in git(["log", "--grep=deai", "--format=%h", "--", BOOK]).split("\n")
        if l
    ]
    if not shas:
        sys.exit("no commits matched (pass a sha, or use the deai subject prefix)")
    total = 0
    for sha in reversed(shas):
        removed, hits, detail = audit(sha)
        bad = sum(hits.values())
        flag = "OK " if bad == 0 else "!! "
        print(f"{flag}{sha} · {removed} 行改动 · 越界 {bad}"
              + (f"（code {hits['code']} / table {hits['table']}"
                 f" / heading {hits['heading']} / figure {hits['figure']}）" if bad else ""))
        for _, ln, kind, txt in detail[:6]:
            print(f"     L{ln} [{kind}] {txt!r}")
        total += bad
    print(f"\n合计越界 {total} 处")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
