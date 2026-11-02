#!/usr/bin/env python3
"""Stage 1 of the de-AI workflow: measure defects before touching prose.

design/system/deai-rules.md forbids rewriting without a defect list, so this
script produces the list. It never edits anything; it only counts.

    python design/system/scan_deai.py --top 15
"""
import argparse
import re
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BOOK = ROOT / "book" / "book.md"

# Pattern families, named after the groups in design/system/deai-rules.md.
PATTERNS = {
    "A-铺垫对比": [r"不是[^。，；]{1,24}[，、](而是|而是什么)", r"不仅[仅]?[^。，；]{1,20}[，、](更|还)", r"与其说[^。，]{1,20}不如", r"真正的[^，。]{1,16}是"],
    "C-AI高频词": [r"至关重要", r"无缝", r"赋能", r"闭环", r"总而言之", r"综上所述", r"值得注意的是", r"需要指出的是", r"不难发现", r"随着[^，。]{2,24}的发展", r"在[^，。]{2,20}的背景下", r"极大(地)?(提升|改善|丰富)"],
    "D1-emoji装饰": [r"✅", r"❌", r"⚠", r"ℹ", r"💡", r"🤔", r"📊", r"🚨", r"🚀", r"📌", r"🎯"],
    "D2-粗体轰炸": [r"\*\*[^*\r\n]{1,24}\*\*"],
    "E-客服腔": [r"让我们", r"希望(这|本文|你)", r"你会发现", r"您可以", r"请记住", r"一起来", r"接下来我们", r"首先我们"],
    "F-中文套话": [r"进行(了)?[一-鿿]{2,4}", r"加以[一-鿿]{2,4}", r"予以[一-鿿]{2,4}", r"做出[一-鿿]{2,4}", r"通过[^，。]{2,24}实现", r"从而使得", r"起到了[^。]{2,12}的作用"],
}
CONJ = r"和|以及|并且|同时|此外|因此|然而|而且"
MOOD = r"啊|吧|呢|嘛|喔|啦|耶"


def prose_lines(text):
    """Yield (line_no, text) for lines that are prose the author is responsible for."""
    fence = False
    for i, line in enumerate(text.split("\n"), 1):
        if line.strip().startswith("```"):
            fence = not fence
            continue
        if fence:
            continue
        s = line.strip()
        if not s or s.startswith("#") or s.startswith("|") or s.startswith("---"):
            continue
        if s.startswith("<") or s.startswith("![") or s.startswith("> ["):
            continue
        yield i, s


def section_map(text):
    """Split the book at `### ` headings; return (title, start_line) boundaries."""
    heads = [(i, l[4:].strip()) for i, l in enumerate(text.split("\n"), 1) if l.startswith("### ")]
    out = []
    for k, (line, title) in enumerate(heads):
        end = heads[k + 1][0] - 1 if k + 1 < len(heads) else len(text.split("\n"))
        out.append((title, line, end))
    return out


def sentences(s):
    parts = re.split(r"[。！？!?；;]+", re.sub(r"\*\*|`|\*|_|\[|\]|\(|）", "", s))
    return [p.strip() for p in parts if len(p.strip()) >= 2]


def scan(text):
    rows = []
    for title, start, end in section_map(text):
        body = text.split("\n")[start - 1:end]
        prose = list(prose_lines("\n".join(body)))
        if len(prose) < 12:
            continue
        joined = " ".join(s for _, s in prose)
        chars = len(re.findall(r"[一-鿿]", joined))
        if chars < 600:
            continue
        counts = {k: sum(len(re.findall(p, joined)) for p in pats) for k, pats in PATTERNS.items()}
        lens = [len(x) for _, s in prose for x in sentences(s)]
        sd = statistics.pstdev(lens) if len(lens) > 2 else 0.0
        conj = len(re.findall(CONJ, joined))
        mood = len(re.findall(MOOD, joined))
        per1k = lambda n: round(1000.0 * n / chars, 2)  # noqa: E731
        total = sum(counts.values())
        rows.append({
            "title": title, "lines": f"{start}-{end}", "chars": chars,
            "defects_per_1k": per1k(total), "total": total,
            "conj_per_1k": per1k(conj), "mood_per_1k": per1k(mood),
            "sd": round(sd, 2), "sents": len(lens), **counts,
        })
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--sort", default="defects_per_1k")
    ap.add_argument("--selftest", action="store_true", help="prove the scanner fires on a loaded sample")
    args = ap.parse_args()

    text = BOOK.read_text(encoding="utf-8")
    rows = scan(text)
    if not rows:
        sys.exit("scan_deai: no sections met the minimum prose size")

    rows.sort(key=lambda r: r[args.sort], reverse=True)
    print(f"sections measured: {len(rows)}  (prose >=600 汉字, >=12 行)")
    print(f"{'def/1k':>7} {'A铺垫':>5} {'C高频':>5} {'D1表情':>6} {'D2粗体':>6} {'E客服':>5} {'F套话':>5} {'conj/1k':>7} {'mood/1k':>7} {'SD':>5}  title")
    for r in rows[:args.top]:
        print(f"{r['defects_per_1k']:>7} {r['A-铺垫对比']:>5} {r['C-AI高频词']:>5} {r['D1-emoji装饰']:>6} "
              f"{r['D2-粗体轰炸']:>6} {r['E-客服腔']:>5} {r['F-中文套话']:>5} {r['conj_per_1k']:>7} "
              f"{r['mood_per_1k']:>7} {r['sd']:>5}  {r['title'][:40]}")

    tot = lambda k: sum(r[k] for r in rows)  # noqa: E731
    chars = tot("chars")
    print(f"\n全书汇总：{chars:,} 汉字，缺陷 {sum(r['total'] for r in rows):,} 处")
    for k in PATTERNS:
        print(f"  {k:<10} {tot(k):>6} 处  ({1000.0 * tot(k) / chars:.2f}/1k)")
    print(f"  连词密度   均值 {sum(r['conj_per_1k'] for r in rows) / len(rows):.2f}/1k，人写 13、AI 36")
    print(f"  语气词密度 均值 {sum(r['mood_per_1k'] for r in rows) / len(rows):.2f}/1k，人写 16、AI 3")
    print(f"  句长 SD   均值 {sum(r['sd'] for r in rows) / len(rows):.2f}，人写 15.15、AI 12.84")



def selftest():
    """The gate must fail on a known-bad sample, or its green means nothing."""
    bad = ("💡 **核心启示**：构建工具至关重要。我们不仅要理解它，更要掌握它。"
           "通过配置实现自动化，从而使得效率得到极大的提升，并且它无缝衔接了开发与部署，"
           "同时提供了闭环能力，此外还能赋能团队。你会发现您可以一起进步。")
    good = "构建工具不是黑魔法。它出错时，日志会指到具体的 loader。"
    counts = {k: sum(len(re.findall(p, bad)) for p in pats) for k, pats in PATTERNS.items()}
    hit = sum(counts.values())
    clean = sum(sum(len(re.findall(p, good)) for p in pats) for pats in PATTERNS.values())
    print("selftest bad-sample defects:", counts, "->", hit)
    print("selftest good-sample defects:", clean)
    if hit < 10:
        sys.exit(f"selftest FAILED: scanner caught only {hit} of a deliberately loaded sample")
    if clean > 2:
        sys.exit(f"selftest FAILED: scanner flags plain prose ({clean}) — it is too blunt to rank sections")
    print("selftest OK")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    main()
