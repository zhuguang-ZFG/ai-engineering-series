#!/usr/bin/env python3
"""Fence state that matches CommonMark, not a backtick toggle.

The first Phase D scanner toggled on every line whose strip() began with ``` —
which mis-reads the book in both directions: a markdown example that *shows* a
fenced block inside a wider block (```` … ````) closed the outer fence early, so
real code was handed to rewriting agents as prose, and real prose was skipped.
"""
import re
import sys

FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")


def code_state(lines):
    """Yield bool per line: True when the line is inside (or is) a code fence."""
    open_fence = None  # (char, length)
    for line in lines:
        m = FENCE.match(line)
        info = m.group(2).strip() if m else ""
        if open_fence is None:
            if m:
                open_fence = (m.group(1)[0], len(m.group(1)))
                yield True
                continue
            yield False
        else:
            char, length = open_fence
            closes = bool(m) and m.group(1)[0] == char and len(m.group(1)) >= length and info == ""
            yield True
            if closes:
                open_fence = None


def in_code(lines, index):
    """True if line `index` (0-based) is inside a code block."""
    for state, i in zip(code_state(lines), range(len(lines))):
        if i == index:
            return state
    return False


def selftest():
    lines = [
        "prose one",                       # 0 False
        "```python",                       # 1 True (open)
        "print('hi')",                     # 2 True
        "```",                             # 3 True (close)
        "prose two",                       # 4 False
        "````markdown",                    # 5 True (open, 4 backticks)
        "example:",                        # 6 True
        "```sh",                           # 7 True — 3 backticks must NOT close a 4
        "npm test",                        # 8 True
        "```",                             # 9 True
        "````",                            # 10 True (close)
        "prose three",                     # 11 False
        "   ```",                          # 12 True (3-space indent still a fence)
        "indented code",                   # 13 True
        "   ```",                          # 14 True (close)
        "prose four",                      # 15 False
        "``` ",                            # 16 True (trailing space, empty info)
        "```",                             # 17 True (close)
        "prose five",                      # 18 False
        "~~~",                             # 19 True
        "tilde code",                      # 20 True
        "~~~",                             # 21 True
        "prose six",                       # 22 False
    ]
    want = [False, True, True, True, False, True, True, True, True, True, True,
            False, True, True, True, False, True, True, False, True, True, True, False]
    got = list(code_state(lines))
    if got != want:
        for i, (g, w) in enumerate(zip(got, want)):
            if g != w:
                print(f"  line {i+1}: got {g} want {w}  {lines[i]!r}")
        sys.exit(f"selftest FAIL ({len([1 for g, w in zip(got, want) if g != w])} mismatches)")
    if not in_code(lines, 8):
        sys.exit("selftest FAIL: in_code() disagrees with code_state()")
    if in_code(lines, 11):
        sys.exit("selftest FAIL: nested fence leaked prose")
    print(f"selftest OK · {len(lines)} fixture lines, {sum(want)} marked code")


if __name__ == "__main__":
    selftest()
