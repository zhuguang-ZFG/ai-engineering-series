#!/usr/bin/env python3
"""Phase D stage 3: fan the defect sites out to rewriting agents, then apply.

Parallel agents must not edit book.md at the same time, so they edit nothing:
each gets a work order (its sections' defect sites) and returns a TSV of
replacements. This script splits the orders (--split) and applies them
(--apply) with per-patch verification, so a hallucinated old-string is
rejected and reported instead of corrupting the book.

TSV columns, one patch per line, no tabs or newlines inside a field:
    line_no <TAB> old <TAB> new

Verified before anything is written:
  * the line exists and `old` occurs in it exactly once
  * `old` and `new` carry the same number of `*` and backticks — an agent may
    reword prose but may not move emphasis, code spans or links around
  * a patch never targets a heading, table row, figure or code fence

    python design/system/deai_workorders.py --split --agents 12
    python design/system/deai_workorders.py --apply
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fences  # noqa: E402  (CommonMark fence state, shared with scan_deai)

ROOT = Path(__file__).resolve().parents[2]
BOOK = ROOT / "book" / "book.md"
SYS = ROOT / "design" / "system"

RULES = """你是中文技术书的文字编辑。只做一件事：消掉指定行的 AI 味，别的都不许动。

先读 `design/system/deai-rules.md`（口径），再按工单逐条处理。每条给你的是
`- L<行号> [<缺陷族>] <命中片段> ← <该行的前 88 字>`；行号是 `book/book.md` 的绝对行号。
用 Read（offset=行号-12, limit=30）取到完整上下文再改，不要凭命中的片段猜句子。

改法（按缺陷族）：
- `F-中文套话`：`进行了全面的介绍` → `介绍了一遍`；`加以记录` → `记下来`；`从而使得` → `于是`/直接删；
  `起到了…的作用` → 直接说它干了什么。动词优先，名词化删掉。
- `E-客服腔`：`让我们` → `我们`或直接开始动作；`你会发现` → 说清会发现什么；`您可以` → `你可以`。
- `C-AI高频词`：`至关重要` → 具体说明重要在哪，或改`重要`；`赋能/闭环/无缝` → 换成大白话；
  `随着 X 的发展` 这类开场直接砍掉，从事实开始。
- `A-铺垫对比`：`不是 A，而是 B` 若 B 本身就是重点，就直接写 B；`不仅…更…` 若两层等价就合并。
- `D2-句中随手强调`：句中 `**词**` 只是加重语气 → 去掉 `**`；若它是读者要复述的比喻或术语
  （如 `**项目经理**`、`**上下文窗口**`）→ **保留并在工单里注明 keep**，不要为了分数牺牲作者的声音。
- `D1-装饰表情`：句中表情符号（`写完后 🎉 会提示`）→ 删掉表情，必要时把句子写顺。

硬约束：
1. 事实、数字、代码、命令、URL、术语、章节锚点一律不改；不确定就不改。
2. 不新增原文没有的观点、限制、怀疑或裁决；不添油加醋，也不删信息。
3. `**`、反引号、`[]()` 链接的数量必须与原文完全一致（只动文字，不动标记）。
4. 标题行、表格行、`<figure>`/图片行、代码块内的内容一律不碰。
5. 保持作者的口吻：这本书是第二人称、短句、爱用具体比喻，改完不能变成书面翻译腔。
6. 中文标点，不加空格（中西文之间的既有空格保留）。

输出：只写一个 TSV 文件到指定路径，制表符分隔三列：`行号<TAB>原文片段<TAB>修改后片段`。
`原文片段` 必须是该行里逐字出现、且只出现一次的子串（含它周围 2~6 个字以保证唯一）。
不需要改的行就别写。文件里不要写注释、表头或解释文字。
"""


def sites_from_export(path):
    """Parse _sites.md into {line_no: [(family, hit, preview)], section_title}."""
    out, section = {}, None
    for line in Path(path).read_text(encoding="utf-8").split("\n"):
        m = re.match(r"^## (.+?)  \(L(\d+)-(\d+)", line)
        if m:
            section = (m.group(1), int(m.group(2)), int(m.group(3)))
            out.setdefault("_sections", []).append(section)
            continue
        m = re.match(r"^- L(\d+) \[([^\]]+)\] (.*?) ← (.*)$", line)
        if m and section:
            out.setdefault(int(m.group(1)), []).append((m.group(2), m.group(3), section[0]))
    return out


def split(agents):
    data = sites_from_export(SYS / "_sites.md")
    sections = sorted(data["_sections"], key=lambda s: s[1])   # _sites.md ranks by defect rate
    per_line = {k: v for k, v in data.items() if k != "_sections"}
    total = sum(len(v) for v in per_line.values())
    quota = max(1, -(-total // agents))
    groups, cur = [], []
    for l in sorted(per_line):
        cur.append(l)
        if sum(len(per_line[x]) for x in cur) >= quota:
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)
    wrote = []
    for idx, group in enumerate(groups, 1):
        n = sum(len(per_line[l]) for l in group)
        touched = [s for s in sections if any(s[1] <= l <= s[2] for l in group)]
        p = SYS / f"_wo_{idx:02d}.md"
        body = [f"<!-- 工单 {idx}：L{group[0]}-{group[-1]} · {n} 个缺陷点 · 跨 {len(touched)} 节 -->",
                RULES, "", "## 你负责的章节（行号范围）"]
        for s in touched:
            body.append(f"- {s[0]}  (L{s[1]}-{s[2]})")
        body += ["", "## 缺陷点位（按行号）"]
        for l in group:
            for fam, hit, _ in per_line[l]:
                body.append(f"- L{l} [{fam}] {hit}")
        p.write_text("\n".join(body), encoding="utf-8")
        wrote.append((p.name, n, len(touched)))
    print(f"{total} sites over {len(sections)} sections -> {len(wrote)} work orders")
    for name, n, secs in wrote:
        print(f"  {name}: {n} sites / {secs} sections")


def apply(dry=True):
    lines = BOOK.read_text(encoding="utf-8").split("\n")
    coded = list(fences.code_state(lines))
    patches = []
    for f in sorted(SYS.glob("_patches_*.tsv")):
        for raw in Path(f).read_text(encoding="utf-8").split("\n"):
            if not raw.strip():
                continue
            cols = raw.split("\t")
            if len(cols) != 3:
                patches.append((f.name, raw[:60], None, "不是三列")); continue
            ln_s, old, new = cols
            if not ln_s.isdigit() or old == new:
                continue
            ln = int(ln_s)
            if not (1 <= ln <= len(lines)):
                patches.append((f.name, ln_s, None, "行号越界")); continue
            cur = lines[ln - 1]
            s = cur.strip()
            if s.startswith(("#", "|", "!", "<", "```")) or cur.startswith("```"):
                patches.append((f.name, ln_s, None, "越权：标题/表格/figure/代码")); continue
            if coded[ln - 1]:
                patches.append((f.name, ln_s, None, "越权：代码块内部")); continue
            if "assets/handdraw/" in cur or "assets/stacks/" in cur:
                patches.append((f.name, ln_s, None, "越权：figure")); continue
            c = cur.count(old)
            if c == 0:
                patches.append((f.name, ln_s, None, "old 不在该行")); continue
            if c > 1:
                patches.append((f.name, ln_s, None, f"old 出现 {c} 次，不够唯一")); continue
            why = None
            if any(old.count(ch) != new.count(ch) for ch in "*`"):
                why = "改动了 **/` 标记数量"
            elif old.count("[") != new.count("[") or old.count("](") != new.count("]("):
                why = "改动了链接结构"
            if why:
                patches.append((f.name, ln_s, None, why)); continue
            patches.append((f.name, ln, (old, new, cur)))

    ok = [p for p in patches if isinstance(p[2], tuple)]
    bad = [p for p in patches if not isinstance(p[2], tuple)]
    out = list(lines)
    for f, ln, (old, new, _) in ok:
        out[ln - 1] = out[ln - 1].replace(old, new, 1)
    print(f"valid {len(ok)} / rejected {len(bad)} from {len(set(p[0] for p in patches))} patch files")
    from collections import Counter
    for reason, n in Counter(p[3] for p in bad).most_common():
        print(f"  reject · {reason}: {n}")
    for f, raw, _, reason in bad[:8]:
        print(f"    {f} {raw}: {reason}")
    han_before = len(re.findall(r"[一-鿿]", "\n".join(lines)))
    han_after = len(re.findall(r"[一-鿿]", "\n".join(out)))
    print(f"汉字 {han_before:,} -> {han_after:,} ({han_after - han_before:+,})")
    if abs(han_after - han_before) > 0.03 * han_before:
        sys.exit("中止：汉字增减超过 3%，先查工单是否删了信息")
    if dry:
        print("(dry-run, book.md untouched)")
        return
    BOOK.write_text("\n".join(out), encoding="utf-8")
    print("written")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", action="store_true")
    ap.add_argument("--agents", type=int, default=12)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--write", action="store_true", help="actually write book.md on --apply")
    args = ap.parse_args()
    if args.split:
        split(args.agents)
    elif args.apply:
        apply(dry=not args.write)
    else:
        sys.exit("use --split or --apply")


if __name__ == "__main__":
    main()
