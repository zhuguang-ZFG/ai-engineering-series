#!/usr/bin/env python3
"""Stage 1 of the de-AI workflow: measure defects before touching prose.

design/system/deai-rules.md forbids rewriting without a defect list, so this
script produces the list. It never edits anything; it counts and, with
--export, writes the exact sites so a rewrite pass can consume them.

Two families are counted by function, not by raw density, because the first
run of this scanner ranked the book on a false signal (see REVIEW O-06):
  D2  a bold span is a defect only when it is rhetorical. `**术语**：解释`,
      a bold at the start of a line/bullet, a latin label, a naming intro and
      an all-bold pseudo-heading line are textbook convention, not AI flavour.
  D1  an emoji is a defect only inside a sentence. At the head of a callout it
      names the callout type, and ✅❌ mark the right/wrong example — both stay.

    python design/system/scan_deai.py --selftest
    python design/system/scan_deai.py --top 15
    python design/system/scan_deai.py --export design/system/_sites.md
    python design/system/scan_deai.py --corpus 'videos/landscape/assets/voice/*.txt' --sites
"""
import argparse
import glob
import re
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fences  # noqa: E402  (CommonMark fence state, shared with deai_pass)

ROOT = Path(__file__).resolve().parents[2]
BOOK = ROOT / "book" / "book.md"

# Sentence-level families: plain regex over the joined prose.
PATTERNS = {
    "A-铺垫对比": [r"不是[^。，；]{1,24}[，、](而是|而是什么)", r"不仅[仅]?[^。，；]{1,20}[，、](更|还)", r"与其说[^。，]{1,20}不如", r"真正的[^，。]{1,16}是"],
    "C-AI高频词": [r"至关重要", r"无缝", r"赋能", r"闭环", r"总而言之", r"综上所述", r"值得注意的是", r"需要指出的是", r"不难发现", r"随着[^，。]{2,24}的发展", r"在[^，。]{2,20}的背景下", r"极大(地)?(提升|改善|丰富)"],
    "E-客服腔": [r"让我们", r"希望(这|本文|你)", r"你会发现", r"您可以", r"请记住", r"一起来", r"接下来我们", r"首先我们"],
    "F-中文套话": [r"进行(了)?[一-鿿]{2,4}", r"加以[一-鿿]{2,4}", r"予以[一-鿿]{2,4}", r"做出[一-鿿]{2,4}", r"通过[^，。]{2,24}实现", r"从而使得", r"起到了[^。]{2,12}的作用"],
}
# Emoji that do work in this book: ✅❌ = right/wrong example, ⚠ℹ = callout type.
SEMANTIC_EMOJI = re.compile(r"[✅❌⚠ℹ]")
ORNAMENT = re.compile(r"[\U0001F300-\U0001FAFF▸▶❗❓⭐✨✅❌]")
BOLD = re.compile(r"\*\*([^*\r\n]{1,24})\*\*")
NAME_BEFORE = re.compile(r"(叫作|叫做|称为|称作|简称|又名|也称|即|写作|记作|叫|称)\s*$")
CONJ = r"和|以及|并且|同时|此外|因此|然而|而且"
MOOD = r"啊|吧|呢|嘛|喔|啦|耶"
KEYS = list(PATTERNS) + ["D1-装饰表情", "D2-句中随手强调"]


def prose_lines(text):
    """Yield (line_no, text) for lines that are prose the author is responsible for."""
    lines = text.split("\n")
    for i, (line, coded) in enumerate(zip(lines, fences.code_state(lines)), 1):
        if coded:
            continue
        s = line.strip()
        if not s or s.startswith("#") or s.startswith("|") or s.startswith("---"):
            continue
        if s.startswith("<") or s.startswith("![") or s.startswith("> ["):
            continue
        yield i, s


def section_map(text):
    """Split the book at `### ` headings; return (title, start, end) 1-based lines."""
    lines = text.split("\n")
    coded = list(fences.code_state(lines))
    heads = [(i, l[4:].strip()) for i, l in enumerate(lines, 1)
             if l.startswith("### ") and not coded[i - 1]]
    out = []
    for k, (line, title) in enumerate(heads):
        end = heads[k + 1][0] - 1 if k + 1 < len(heads) else len(lines)
        out.append((title, line, end))
    return out


def sentences(s):
    parts = re.split(r"[。！？!?；;]+", re.sub(r"\*\*|`|\*|_|\[|\]|\(|）", "", s))
    return [p.strip() for p in parts if len(p.strip()) >= 2]


def rhetorical_bold(line):
    """D2 sites: bold used as mid-sentence emphasis, not as a term marker."""
    s = line.strip()
    hits = list(BOLD.finditer(line))
    if not hits or BOLD.fullmatch(s):
        return []
    out = []
    for m in hits:
        content = m.group(1)
        after = line[m.end():m.end() + 1]
        before = line[max(0, m.start() - 4):m.start()]
        if after in ("：", ":"):
            continue                                   # **term**：definition
        if NAME_BEFORE.search(before):
            continue                                   # 这叫**上下文窗口**
        if re.search(r"[A-Za-z0-9]", content):
            continue                                   # latin label / number
        if m.start() == len(line) - len(s) or re.match(r"^(?:>\s*)?[-*\d.)]*\s*\*\*", s):
            continue                                   # bullet / line-lead term
        out.append((m.start(), content))
    return out


# An emoji that OPENS a block names the block type — `::: tip 💡 幂等性`,
# `👇 **动手点点看**：`, `> 🎯 **实用场景**：`. The book uses them as a legend,
# so they are never counted. An emoji buried INSIDE a bold pseudo-heading
# (`**🤔 为什么需要缓存**`) or sprinkled mid-sentence is ornament, and is.
CALLOUT_ICON = re.compile(r"^(?:>\s*)?:::\s*\w+\s+[\U0001F300-\U0001FAFF](?:[\U0001F3FB-\U0001F3FF]|\ufe0f)?\s*")
LEAD_LABEL = re.compile(r"^(?:>\s*)?(?:[-*\d.)]+\s*)?[\U0001F300-\U0001FAFF](?:[\U0001F3FB-\U0001F3FF]|\ufe0f)?\s*\*\*")


def ornament_emoji(line):
    """D1 sites: decorative emoji inside the sentence, not the callout marker."""
    s = line.strip()
    for marker in (CALLOUT_ICON, LEAD_LABEL):
        m = marker.match(s)
        if m:
            rest = s[m.end():]
            return [(i + m.end(), c) for i, c in enumerate(rest)
                    if ORNAMENT.match(c) and not SEMANTIC_EMOJI.match(c)]
    head = re.match(r"^(?:>\s*)?(?:\*\*)?(?:[-*\d.)]*\s*)", s)
    headlen = head.end() if head else 0
    return [(i, c) for i, c in enumerate(s) if i >= headlen
            and ORNAMENT.match(c) and not SEMANTIC_EMOJI.match(c)]


def measure(title, prose, start, end):
    counts = {k: 0 for k in KEYS}
    sites = []
    for ln, s in prose:
        ln += start - 1                        # preserve line numbers in the source file
        for _, content in rhetorical_bold(s):
            counts["D2-句中随手强调"] += 1
            sites.append((ln, "D2-句中随手强调", f"**{content}**", s))
        for _, c in ornament_emoji(s):
            counts["D1-装饰表情"] += 1
            sites.append((ln, "D1-装饰表情", c, s))
    for k, pats in PATTERNS.items():
        for ln, s in prose:
            for p in pats:
                for m in re.finditer(p, s):
                    counts[k] += 1
                    sites.append((ln + start - 1, k, m.group(0), s))
    joined = " ".join(s for _, s in prose)
    chars = len(re.findall(r"[一-鿿]", joined))
    lens = [len(x) for _, s in prose for x in sentences(s)]
    sd = statistics.pstdev(lens) if len(lens) > 2 else 0.0
    per1k = lambda n: round(1000.0 * n / chars, 2) if chars else 0.0  # noqa: E731
    return {
        "title": title, "start": start, "end": end, "chars": chars,
        "total": sum(counts.values()),
        "defects_per_1k": per1k(sum(counts.values())),
        "conj_per_1k": per1k(len(re.findall(CONJ, joined))),
        "mood_per_1k": per1k(len(re.findall(MOOD, joined))),
        "sd": round(sd, 2), "sents": len(lens), "sites": sites, **counts,
    }


def scan(text):
    rows = []
    for title, start, end in section_map(text):
        body = text.split("\n")[start - 1:end]
        prose = list(prose_lines("\n".join(body)))
        if len(prose) < 12:
            continue
        if len(re.findall(r"[一-鿿]", " ".join(s for _, s in prose))) < 600:
            continue
        rows.append(measure(title, prose, start, end))
    return rows


HEADER = (f"{'def/1k':>7} {'A铺垫':>5} {'C高频':>5} {'D1表情':>6} {'D2粗体':>6} "
          f"{'E客服':>5} {'F套话':>5} {'conj/1k':>7} {'mood/1k':>7} {'SD':>5}  title")


def export(rows, path):
    rows = [r for r in rows if r["total"]]
    seen = sum(len(set((ln, f, h) for ln, f, h, _ in r["sites"])) for r in rows)
    lines = [f"<!-- scan_deai.py · {len(rows)} 节 · {seen} 个独立缺陷点 · 按行号排序 -->"]
    for r in rows:
        lines.append(f"\n## {r['title']}  (L{r['start']}-{r['end']} · {r['chars']} 汉字 · {r['total']} 处 · {r['defects_per_1k']}/1k)")
        for ln, fam, hit, s in sorted(set((ln, f, h, x) for ln, f, h, x in r["sites"])):
            lines.append(f"- L{ln} [{fam}] {hit} ← {s[:88]}")
    Path(path).write_text("\n".join(lines), encoding="utf-8")
    print(f"exported {seen} unique sites across {len(rows)} sections -> {path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--sort", default="defects_per_1k",
                    choices=["defects_per_1k", "total", "chars", "conj_per_1k",
                             "mood_per_1k", "sd", "sents", *KEYS])
    ap.add_argument("--export", metavar="PATH")
    ap.add_argument("--selftest", action="store_true", help="prove the scanner fires on a loaded sample")
    ap.add_argument("--corpus", metavar="GLOB",
                    help="measure a small corpus instead of the book (one file = one row, "
                         "no size gate); used for narration scripts")
    ap.add_argument("--sites", action="store_true", help="list every matched site with its source")
    args = ap.parse_args()

    if args.selftest:
        sys.exit(selftest())
    if args.top < 0:
        ap.error("--top must be zero or greater")

    if args.corpus:
        rows = []
        paths = sorted({Path(path) for path in glob.glob(args.corpus, recursive=True)
                        if Path(path).is_file()})
        for path in paths:
            try:
                body = path.read_text(encoding="utf-8-sig")
            except (OSError, UnicodeError) as error:
                ap.error(f"cannot read {path}: {error}")
            n = len(body.split("\n"))
            rows.append(measure(path.as_posix(), list(prose_lines(body)), 1, n))
        if not rows:
            ap.error(f"--corpus matched no files for {args.corpus}")
    else:
        text = BOOK.read_text(encoding="utf-8")
        rows = scan(text)
        if not rows:
            sys.exit("scan_deai: no sections met the minimum prose size")
        print(f"sections measured: {len(rows)}  (prose >=600 汉字, >=12 行)")

    rows.sort(key=lambda r: r[args.sort], reverse=True)
    print(HEADER)
    for r in rows[:args.top]:
        print(f"{r['defects_per_1k']:>7} {r['A-铺垫对比']:>5} {r['C-AI高频词']:>5} {r['D1-装饰表情']:>6} "
              f"{r['D2-句中随手强调']:>6} {r['E-客服腔']:>5} {r['F-中文套话']:>5} {r['conj_per_1k']:>7} "
              f"{r['mood_per_1k']:>7} {r['sd']:>5}  {r['title']}")
    if args.sites:
        print("\n--- sites ---")
        for r in rows:
            for ln, kind, hit in sorted(set((ln, k, h) for ln, k, h, _ in r["sites"])):
                print(f"{r['title']}:{ln} {kind} {hit}")
    report(rows)
    if args.export:
        export(rows, args.export)


def report(rows):
    if not rows:
        print("\n汇总：没有可测文本")
        return
    tot = lambda k: sum(r[k] for r in rows)  # noqa: E731
    chars = tot("chars")
    print(f"\n汇总：{chars:,} 汉字，缺陷 {sum(r['total'] for r in rows):,} 处")
    for k in KEYS:
        density = 1000.0 * tot(k) / chars if chars else 0.0
        print(f"  {k:<12} {tot(k):>6} 处  ({density:.2f}/1k)")
    print(f"  连词密度   均值 {sum(r['conj_per_1k'] for r in rows) / len(rows):.2f}/1k，人写 13、AI 36")
    print(f"  语气词密度 均值 {sum(r['mood_per_1k'] for r in rows) / len(rows):.2f}/1k，人写 16、AI 3")
    print(f"  句长 SD   均值 {sum(r['sd'] for r in rows) / len(rows):.2f}，人写 15.15、AI 12.84")


def selftest():
    """The gate must fire on a known-bad sample and stay silent on clean prose."""
    bad = ("**🤔 核心启示**：构建工具至关重要。我们不仅要理解它，更要掌握它。"
           "通过配置实现自动化，从而使得效率得到极大的提升，并且它无缝衔接了开发与部署，"
           "同时提供了闭环能力，此外还能赋能团队。你会发现您可以一起进步。"
           "这一步💡省不掉，我们对这个问题进行了深入的讨论，并加以记录。")
    bad_line = "这一步**非常关键**，跳过它你会在后面付出代价。"
    good = "构建工具不是黑魔法。它出错时，日志会指到具体的 loader。"
    good_lines = ["构建工具不是黑魔法。它出错时，日志会指到具体的 loader。",
                  "- **npm**：装包的那一个",
                  "**上下文窗口**：模型一次能记住多少内容",
                  "我们把这块区域设为 `#fbfaf6`，它代表纸面。",
                  # the legend forms: an emoji that NAMES the block stays put,
                  # so the scanner must never rank a section for carrying them
                  "> ::: tip 💡 幂等性",
                  "👇 **动手点点看**：依次点击命令按钮，观察文件在三个区域之间的流转。",
                  "> 🎯 **实用场景**：当你需要 AI 帮你分析一个网页的布局问题。",
                  "> ::: warning 🛡️ 三道防线"]
    counts = {k: sum(len(re.findall(p, bad)) for p in pats) for k, pats in PATTERNS.items()}
    counts["D1-装饰表情"] = len(ornament_emoji(bad))
    counts["D2-句中随手强调"] = len(rhetorical_bold(bad_line))
    hit = sum(counts.values())
    all_pats = [p for pats in PATTERNS.values() for p in pats]
    clean_regex = sum(len(re.findall(p, l)) for p in all_pats for l in good_lines)
    clean_mark = sum(len(rhetorical_bold(l)) + len(ornament_emoji(l)) for l in good_lines)
    clean = clean_regex + clean_mark
    ornament_bad = len(ornament_emoji(bad))
    print("selftest bad-sample defects:", counts, "->", hit)
    print("selftest clean-sample defects:", clean_regex, "+", clean_mark)
    if hit < 12:
        sys.exit(f"selftest FAILED: scanner caught only {hit} of a deliberately loaded sample")
    if ornament_bad != 2:
        sys.exit(f"selftest FAILED: D1 should fire twice on the bad sample (bold-heading emoji "
                 f"+ mid-sentence emoji), got {ornament_bad}")
    if clean > 0:
        sys.exit(f"selftest FAILED: scanner flags clean prose ({clean}) — too blunt to rank sections")
    print("selftest OK")
    return 0


if __name__ == "__main__":
    main()
