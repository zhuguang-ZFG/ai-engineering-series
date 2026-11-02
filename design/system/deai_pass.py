#!/usr/bin/env python3
"""Phase D · mechanical de-AI pass over book/book.md.

Evidence from scan_deai.py: the book's vocabulary is already clean (AI 高频词
0.16/1k, 套话 1.09/1k). What actually reads as machine-written is decoration —
13.68 bold spans and 1.69 emoji per 1000 汉字. So this pass touches emphasis
and ornament only. It never rewords a sentence, never touches a heading, code
fence, table, or figure.

Rules, in the order applied:
  R1  one emphasis per line: keep the first **span**, unwrap the rest
  R2  drop the ornaments that decorate a blockquote HEADER (`> **💡 核心问题**`).
      Only that form: a bare `> ⚠️ 注意` keeps its emoji, because there it marks
      the callout type, and ✅❌ always stay — in this book they mark the
      right/wrong example.
  R3  a line that is entirely bold and sits directly above a list is a fake
      heading: unwrap it, the list already carries the structure
  R4  drop decorative emoji sitting in the callout/bullet head slot
      (`> 💡 **学习指南**`, `- 🚀 先跑起来`); ⚠ℹ stay there because they name
      the severity of the box

Each rule removes `*` in whole pairs or not at all, so the per-line delta is
0 or a multiple of 4. An edit that breaks that invariant aborts the run instead
of writing half a bold marker — the bug the first draft had, which turned
`> **💡 标题**` into `> 标题**`.

    python design/system/deai_pass.py --selftest
    python design/system/deai_pass.py --dry-run
    python design/system/deai_pass.py
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fences  # noqa: E402  (CommonMark fence state, shared with scan_deai)

ROOT = Path(__file__).resolve().parents[2]
BOOK = ROOT / "book" / "book.md"

BOLD = re.compile(r"\*\*([^*\r\n]{1,24})\*\*")
# Two sets, because "is this emoji doing a job?" depends on where it sits.
# DECOR never carries meaning; SEVERITY (⚠ℹ) names the callout type when it
# heads a box, but is only ornament when it hides inside a bold title.
# ✅❌ are absent from both: here they mark the right/wrong example.
DECOR = (r"(?:\U0001F4A1|\U0001F4CA|\U0001F9D0|\U0001F6A8|\U0001F680|\U0001F4CC"
         r"|\U0001F3AF|\U0001F310|\U0001F4DD|\U0001F519|[\u25B8\u25B6]\uFE0F?)")
SEVERITY = r"(?:[\u2139\u26A0]\uFE0F?)"
ORN = r"(?:" + DECOR + "|" + SEVERITY + ")"
HEADER_LEAD = re.compile(r"^(\s*>\s*)(\*\*)((?:\s*" + ORN + r")+)\s*(?=\S)")
# R4: `> 💡 **标题**` / `- 🚀 正文` — decorative emoji in the callout head slot.
CALL_HEAD = re.compile(r"^(\s*(?:>\s*)?(?:[-*\d.)]\s+)?)(?:" + DECOR + r"\s*)+(?=\S)")


def split_fences(lines):
    """Yield (index, line, in_code) so code blocks are never rewritten.

    CommonMark rules, not a ``` XOR toggle: a line that merely starts with a
    fence inside an indented block, or a ```` fence wrapping ``` examples, used
    to flip the state and expose real code to the rewriter.
    """
    for i, (line, coded) in enumerate(zip(lines, fences.code_state(lines))):
        yield i, line, coded


def strip_header_emoji(line):
    """R2: `> **💡 标题**` -> `> **标题**`, ** markers untouched."""
    m = HEADER_LEAD.match(line)
    if not m:
        return line, 0
    return m.group(1) + "**" + line[m.end():], 1


def strip_callout_emoji(line):
    """R4: drop decorative emoji sitting in front of a callout / bullet."""
    m = CALL_HEAD.match(line)
    if not m:
        return line, 0
    head = re.match(r"^(?:\s*>\s*)?(?:[-*\d.)]\s+)?", line).group(0)
    return head + line[m.end():], 1


def keep_first_emphasis(text):
    """R1: at most one bold span per line; the rest become plain text."""
    hits = list(BOLD.finditer(text))
    if len(hits) < 2:
        return text, 0
    out, last, n = [], 0, 0
    for k, m in enumerate(hits):
        out.append(text[last:m.start()])
        out.append(m.group(0) if k == 0 else m.group(1))
        if k:
            n += 1
        last = m.end()
    out.append(text[last:])
    return "".join(out), n


def stars_removed(before, after):
    return before.count("*") - after.count("*")


def rewrite(line, nxt, stats):
    s = line.strip()
    if s.startswith("#") or s.startswith("|") or s.startswith("![") or s.startswith("<"):
        return line
    if "assets/handdraw/" in line or "assets/stacks/" in line:
        return line
    new = line

    new, hit = strip_header_emoji(new)
    stats["R2"] += hit
    new, hit = strip_callout_emoji(new)
    stats["R4"] += hit

    stripped = new.lstrip()
    if BOLD.fullmatch(stripped) and nxt is not None:
        if nxt.startswith("- ") or re.match(r"^\d+\.\s", nxt):
            new = new[: len(new) - len(stripped)] + stripped[2:-2].strip()
            stats["R3"] += 1

    new, cut = keep_first_emphasis(new)
    stats["R1"] += cut
    return new


def selftest():
    """Each rule fires on its case, meaning-emoji survive, and the star
    invariant catches a dropped opener."""
    cases = [
        ("> **\U0001F4A1 核心问题**", None, "> **核心问题**"),
        ("> **\U0001F4A1 \U0001F3AF 双装饰**", None, "> **双装饰**"),
        ("> **▸ \U0001F4A1 什么是新模式？**", None, "> **什么是新模式？**"),
        ("> \U0001F4A1 提示", None, "> 提示"),                   # R4: 💡 in the head slot goes
        ("> ⚠️ 注意", None, "> ⚠️ 注意"),                        # ⚠ℹ stay: they name the box
        ("> ✅ 这样写就对", None, "> ✅ 这样写就对"),
        ("> 💡 **学习指南**：本章无需编程基础", None, "> **学习指南**：本章无需编程基础"),
        ("- 🚀 先跑起来看看", None, "- 先跑起来看看"),
        ("可胜任**小工具**、**看板**、**小游戏**", None, "可胜任**小工具**、看板、小游戏"),
        ("**第一步**", "- 子项", "第一步"),
        ("**第一步**", "正文", "**第一步**"),
        ("- **术语**：解释", None, "- **术语**：解释"),
        ("# 标题 **粗**与**粗**", None, "# 标题 **粗**与**粗**"),
    ]
    for line, nxt, want in cases:
        got = rewrite(line, nxt, {"R1": 0, "R2": 0, "R3": 0, "R4": 0})
        if got != want:
            print(f"FAIL {line!r} -> {got!r} (want {want!r})")
            return 1
        if stars_removed(line, got) % 4:
            print(f"FAIL invariant {line!r} -> {got!r}")
            return 1
    if stars_removed("> **核心问题**", "> 核心问题**") % 4 == 0:
        print("FAIL: invariant cannot tell a dropped opener")
        return 1
    print("selftest ok · 11 rule cases + star invariant catches the dropped-opener bug")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--sample", type=int, default=12)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        sys.exit(selftest())

    raw = BOOK.read_text(encoding="utf-8")
    lines = raw.split("\n")
    tagged = list(split_fences(lines))
    stats = {"R1": 0, "R2": 0, "R3": 0, "R4": 0}
    out = list(lines)
    changed = 0
    shown = 0
    bad = []

    for pos, (i, line, in_code) in enumerate(tagged):
        if in_code or not line.strip():
            continue
        nxt = tagged[pos + 1][1].strip() if pos + 1 < len(tagged) else None
        new = rewrite(line, nxt, stats)
        if new == line:
            continue
        if stars_removed(line, new) % 4:
            bad.append((i + 1, line, new))
            continue
        out[i] = new
        changed += 1
        if shown < args.sample:
            shown += 1
            print("- " + line.strip()[:110])
            print("+ " + new.strip()[:110])

    print(f"\nR1 一行只留一处强调（拆掉多余粗体）: {stats['R1']}")
    print(f"R2 引言标题去掉装饰 emoji:            {stats['R2']}")
    print(f"R3 整行粗体且下面紧跟列表 → 拆掉:      {stats['R3']}")
    print(f"R4 引言/列表头部装饰 emoji:              {stats['R4']}")
    print(f"改动 {changed} 行 / 合计 {sum(stats.values())} 处")
    if bad:
        print(f"\n中止：{len(bad)} 处改动破坏粗体配对，未写入")
        for ln, before, after in bad[:5]:
            print(f"  L{ln}: {before.strip()[:70]!r} -> {after.strip()[:70]!r}")
        sys.exit(1)
    if args.dry_run:
        print("(dry-run, book.md untouched)")
        return
    BOOK.write_text("\n".join(out), encoding="utf-8")
    print("written")


if __name__ == "__main__":
    main()
