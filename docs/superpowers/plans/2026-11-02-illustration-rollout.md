# 插图扩容实施计划（正文手绘 / 连续动图铺开）

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把正文手绘图版从 2 张（只有 ch03）扩到 7 张，覆盖 ch02／ch01／ch04／ch08／ch07 五个单元，并先补上「胶片只在屏幕上动」这一层的契约测试与锚点平移工具。

**Architecture:** 正文写一个 ` ```ill ` 围栏（一行画名）→ `core.extract_illustrations` 换成 `@@ILL:<hash>@@` 占位 → `render.drawing_slots` 取上方最近的 H2 作题注 → `render.plate_repl` 调 `art.drawing(name)` 把 `illustrations/<name>.svg` 原样内联 → `render.illu_figure` 包成 `<figure class="illu illu-{line|seq}">`。`style.py` 里那段 `@media screen and (prefers-reduced-motion: no-preference)` + `@supports (animation-timeline: view())` 决定它是否逐格滚动显影；打印与降级动态拿不到动画，PDF 里就是一条画完的静态胶片。锚点（`glosses.json` 408 条、`manifest.json` 158 条）用 `scripts/shift_anchors.py` 按行号平移，`plain.validate_plain()` 逐条复核。

**Tech Stack:** Python 3.13（标准库 only，`unittest`）、手写 SVG（单行、`currentColor`）、CSS scroll-driven animations、Node（仅 `npm run check:diagrams`）。

**Spec:** `docs/superpowers/specs/2026-11-01-yuyu-illustration-expansion.md`

## Global Constraints

- 单元数固定 20，不新增第 21 个单元；4 篇、附录 A–D 的结构不动。
- 单文件离线成品：不引入任何外部运行时资源、字体、图标或第三方素材；位图只允许 `art.photo()` 产出 `data:` URI（单张 300 KB 封顶），且必须先登记来源与许可（`CREDITS.md` §三，只收 MIT／Apache 一类）。
- 手写 SVG 由 `yuyu_book/art.py::_read` 把关：禁 `id=`、`href=`、`url()`、`<script>`／`<style>`／`<iframe>`；必须含 `currentColor`；根元素必须是带 `viewBox` 的单个 `<svg>`。图版体积上限 `art.PLATE_BYTES = 20000` 字节，章徽上限 6000 字节。
- 画名只允许 `[a-z0-9][a-z0-9._-]*`，一个围栏一个名字，名字之外不许有内容。
- 连续胶片由图自己声明：根元素 `class` 含 `seq`。`<g class="frame">` 必须是 `<svg>` 的前 1～6 个子元素，装饰性组一律排在帧组之后。带 `pathLength="100"` 的形状走 `ink-draw`；写了真实单位 `stroke-dasharray`（如 `3 5`、`6 13`）的元素不许再带 `pathLength`。悬停循环规则要排在 `nth-child` 滚动 range 规则之后，并同时写 `animation-timeline:auto` 与 `animation-range:normal`。
- 双语同步、一行换一行：中文版与英文版同一单元的行数与行号一一对应（本轮 5 个落点已逐行实测确认），插入块只落在两个文件的同一行号之后。
- 一张图版落进正文，固定是六行：引子一句、空行、` ```ill `、画名、` ``` `、空行；这六行的最后一行是下一个 `---` 或 H2 的前导空行——少了它，围栏会贴住分隔线被当作 setext 标题读。
- 凡写进 commit message 与 `revisions.json` 的数字，必须能当场重新测出来；测不出来的当错数处理，不复用。账本注释不许夹原始 `@@` 串（`test_pages.test_revision_notes_are_typeset_not_left_in_markdown`），反引号必须成对。
- Python：四空格缩进、`snake_case`；测试文件 `test_*.py`、方法 `test_*`。
- 五道闸全绿才算做完（见下）。不推送 `origin`，除非用户当次明确同意；`upstream` 永不推送。

**五道闸（本机无 make，逐条手跑）：**

```bash
python -X utf8 yuyu-book/build.py --check            # 装配 + 锚点复核
python -X utf8 yuyu-book/build.py --check --mermaid=source
python -X utf8 -m unittest discover -s yuyu-book/tests   # 构建器测试
python -X utf8 -m unittest discover -s tests             # 仓库测试
python -X utf8 scripts/check_book.py                     # 内容闸
npm run check:diagrams                                   # 320 张 Mermaid
```

2026-11-02 实测的当前基线（写进任务，是为了让每一步的「预期」都是可核对的，不是猜的）：

| 口径 | 当前值 |
| --- | --- |
| 手写 SVG | 28 份（其中正文图版 2 张，均在 ch03） |
| `ill` 围栏 | 4 个（zh 2 + en 2） |
| 构建器测试 | 440 项 |
| 仓库测试 | 27 项 |
| Mermaid | 320 张，0 错 |
| 每版 Mermaid 图版 | 160 张（中英合计 320） |
| `build.py --check` 报的 plates | 每版 162（160 Mermaid + 2 手绘） |
| 锚点 | `glosses.json` 408 条、`manifest.json` 158 条 |

## File Structure

| 文件 | 责任 | 本计划里的动作 |
| --- | --- | --- |
| `scripts/shift_anchors.py` | 把两份注册表里的 `file:line` 锚点按行号平移 | 新建（Task 1） |
| `tests/test_shift_anchors.py` | 钉住平移语义与「只改数字、不改格式」 | 新建（Task 1） |
| `yuyu-book/tests/test_build_contracts.py` | 样式与产物的契约 | 加 2 项（Task 2） |
| `yuyu-book/tests/test_docclaims.py` | 文档里每个数字对回数据 | 加 1 条英文图数声明（Task 2） |
| `en/README.md` | 英文版门面 | 「Twenty-six」改数字并被钉住（Task 2） |
| `yuyu-book/illustrations/<name>.svg` | 手绘图版本体 | 新建 5 份（Task 3–7） |
| `第一部分-…/0X-….md`、`en/Part-…/0X-….md` | 正文 | 各加一个六行块（Task 3–7） |
| `yuyu-book/glosses.json`、`yuyu-book/manifest.json` | 锚点注册表 | 各平移一次（Task 3–7） |
| `scripts/build_illustration_gallery.py` | 画廊的 `ORDER`／`WIDE`／双语题注 | 每图加一条（Task 3–7） |
| `README.md`、`STRUCTURE.md`、`CREDITS.md`、`en/README.md` | 图数声明 | 每图 +1（Task 3–7） |
| `yuyu-book/revisions.json` | 账本 | 每任务追加一条 zh＋en 注释（Task 2–7） |
| `docs/illustration-gallery.html` 等派生产物 | 画廊／入门读本／门户 | 重生成（Task 8） |

五个落点与它们的题注来源（H2 就是渲染时自动取的题注，所以图和标题必须本来就对得上——这五组已实测确认）。最后一列是这一处插入要平移的锚点条数，2026-11-02 直接从两份注册表数出来的，执行时对不上就要停下来查：

| 单元 | 落点行（zh/en 同行号） | 支配它的 H2 | 类型 | 画名 | 平移锚点 |
| --- | --- | --- | --- | --- | --- |
| ch02 对话循环 | 289（下一行是 `---`） | 2.2 一个完整 Turn 的生命周期 / The Lifecycle of a Complete Turn | seq | `ch02-turn-loop` | 28（glosses 26 + manifest 2） |
| ch01 五大原则 | 384（下一行是 `---`） | 1.3 Agent Harness 设计哲学的五大原则 / Five Principles of … | line | `ch01-five-pillars` | 0（该文件 >384 无锚点） |
| ch04 权限管线 | 170（下一行是 H2 4.2） | 4.1 权限管线的四个阶段 / The Four Stages of the Permission Pipeline | seq | `ch04-gate-steps` | 9（7 + 2） |
| ch08 钩子 | 528（下一行是 `---`） | 8.2 核心生命周期事件 / Core Lifecycle Events | seq | `ch08-hook-line` | 3（1 + 2） |
| ch07 四级压缩 | 241（下一行是 `---`） | 7.2 四级压缩策略 / The Four-Level Compression Strategy | seq | `ch07-four-levels` | 5（3 + 2） |

`manifest.json` 那 2 条来自该单元 `guides/<uid>/plain_evidence` 数组——zh 与 en 各有一条指向落点之后的句子，实测已核对（ch04 那条指向 `:209`）。ch01 之所以是 0，因为 1.3 之后正文只剩「实战练习」一节，注册表里没有引用它。

---

### Task 1: 锚点平移脚本

正文加六行，注册表里所有指向该文件更靠后位置的 `file:line` 都要 +6。这件事以前靠手改，改漏一条就是 `plain.validate_plain()` 报「evidence … is inside a code fence, blank, or past the end of the file」。脚本做的事只有一件：**只改数字，不改别的**（两份注册表一份是 1 空格缩进、一份是 2 空格缩进，都是 CRLF；`json.dumps` 重写会把整个文件炸成 diff）。

**Files:**
- Create: `scripts/shift_anchors.py`
- Test: `tests/test_shift_anchors.py`

**Interfaces:**
- Produces: `REF: re.Pattern`；`shift(text: str, files: frozenset[str], after: int, delta: int) -> tuple[str, list[tuple[str, int, int]]]`；`main(argv: list[str] | None = None) -> int`；`REGISTRY_NAMES: tuple[str, ...] = ("glosses.json", "manifest.json")`

- [ ] **Step 1: 写失败的测试**

Create `tests/test_shift_anchors.py`:

```python
"""Anchor arithmetic for a six-line plate: move the pointer, not the prose.

A shift is the one edit that can silently break the plain-language layer, so
the script that does it is pinned here four ways: which refs move, which do
not, that nothing on disk escapes the regex, and that the bytes outside the
digits are untouched.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import shift_anchors  # noqa: E402

ZH02 = "第一部分-基础篇/02-对话循环-Agent的心跳.md"
EN02 = "en/Part-1-Foundations/02-The-Dialog-Loop-Heartbeat-of-an-Agent.md"
OTHER = "第一部分-基础篇/03-工具系统-Agent的双手.md"


def doc(*refs: str) -> str:
    return '{\n "a": [\n' + "".join(f'  "{r}",\n' for r in refs) + " ]\n}\r\n"


class ShiftSemantics(unittest.TestCase):
    def test_only_refs_after_the_insert_move(self):
        text = doc(f"{ZH02}:100", f"{ZH02}:289", f"{ZH02}:290", f"{ZH02}:445")
        out, hits = shift_anchors.shift(text, frozenset({ZH02}), 289, 6)
        self.assertEqual([(ZH02, 290, 296), (ZH02, 445, 451)], hits)
        self.assertIn(f'"{ZH02}:100"', out)
        self.assertIn(f'"{ZH02}:289"', out)
        self.assertIn(f'"{ZH02}:296"', out)
        self.assertIn(f'"{ZH02}:451"', out)

    def test_other_files_are_left_alone(self):
        text = doc(f"{OTHER}:400", f"{EN02}:400")
        out, hits = shift_anchors.shift(text, frozenset({ZH02}), 289, 6)
        self.assertEqual([], hits)
        self.assertEqual(text, out)

    def test_both_languages_move_on_the_same_line(self):
        text = doc(f"{ZH02}:300", f"{EN02}:300")
        out, hits = shift_anchors.shift(
            text, frozenset({ZH02, EN02}), 289, 6)
        self.assertEqual(2, len(hits), out)

    def test_every_anchor_on_disk_is_matched(self):
        """If a registry ever stores a pointer the regex cannot see, the
        shift would silently leave it behind."""
        for name in shift_anchors.REGISTRY_NAMES:
            text = (ROOT / "yuyu-book" / name).read_text(encoding="utf-8")
            self.assertEqual(
                text.count(".md:"), len(shift_anchors.REF.findall(text)),
                f"{name}: an anchor the script cannot move")


class PreserveFormatting(unittest.TestCase):
    def test_a_zero_delta_rewrite_is_byte_identical(self):
        for name in shift_anchors.REGISTRY_NAMES:
            text = (ROOT / "yuyu-book" / name).read_text(
                encoding="utf-8", newline="")
            out, hits = shift_anchors.shift(text, frozenset({ZH02}), 0, 0)
            self.assertEqual([], hits)
            self.assertEqual(text, out, f"{name}: formatting drifted")

    def test_crlf_survives_a_write(self):
        src = ROOT / "yuyu-book" / shift_anchors.REGISTRY_NAMES[0]
        text = src.read_text(encoding="utf-8", newline="")
        self.assertIn("\r\n", text, "the fixture assumed CRLF registries")
```

- [ ] **Step 2: 跑到失败**

Run: `python -X utf8 -m unittest tests.test_shift_anchors -v`（工作目录 `claude-code-book-main`）
Expected: `ModuleNotFoundError: No module named 'shift_anchors'`

- [ ] **Step 3: 写实现**

Create `scripts/shift_anchors.py`:

```python
#!/usr/bin/env python3
"""Move every `file:line` anchor when the prose it points at moves down.

A plate costs the prose six lines. The two registries that quote prose by line
number have to follow, or the plain-language layer's evidence pointers land on
a separator line — and `plain.validate_plain()` fails the build for it, which
is the loud version of a reader being shown the wrong sentence.

Only the digits are touched: glosses.json is written with one-space indent and
manifest.json with two, both with CRLF, and re-dumping either would bury a
six-line change under 500 lines of reformatting.

    python scripts/shift_anchors.py --after 289 --delta 6 <file> [<file> …]
    python scripts/shift_anchors.py --after 289 --delta 6 --write <file> …

Refs on the insert line itself and above it stay; the six new lines start at
after+1. Pass both language files together: they are line-for-line aligned, so
one number serves both.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY_NAMES = ("glosses.json", "manifest.json")
REF = re.compile(r'"(?P<path>[^"\n]+\.md):(?P<line>\d+)"')


def shift(text: str, files: frozenset[str], after: int,
          delta: int) -> tuple[str, list[tuple[str, int, int]]]:
    """Rewrite the refs that point into `files` past `after`; report them."""
    hits: list[tuple[str, int, int]] = []

    def repl(m: re.Match[str]) -> str:
        rel, line = m.group("path"), int(m.group("line"))
        if rel.replace("\\", "/") not in files or line <= after:
            return m.group(0)
        hits.append((rel, line, line + delta))
        return f'"{rel}:{line + delta}"'

    return REF.sub(repl, text), hits


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("files", nargs="+", help="prose file(s), repo-relative")
    ap.add_argument("--after", type=int, required=True,
                    help="the blank line the block goes under")
    ap.add_argument("--delta", type=int, default=6)
    ap.add_argument("--write", action="store_true",
                    help="save the registries (default: print the plan)")
    args = ap.parse_args(argv)

    targets = frozenset(f.replace("\\", "/") for f in args.files)
    missing = [f for f in targets if not (ROOT / f).exists()]
    if missing:
        print(f"no such prose file: {', '.join(missing)}", file=sys.stderr)
        return 2

    moved = 0
    for name in REGISTRY_NAMES:
        path = ROOT / "yuyu-book" / name
        text = path.read_text(encoding="utf-8", newline="")
        out, hits = shift(text, targets, args.after, args.delta)
        for rel, frm, to in hits:
            print(f"{name}: {rel}:{frm} -> {to}")
        moved += len(hits)
        if out != text and args.write:
            path.write_text(out, encoding="utf-8", newline="")
    print(f"{'written' if args.write else 'planned'}: {moved} anchors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: 跑到通过**

Run: `python -X utf8 -m unittest tests.test_shift_anchors -v`
Expected: `Ran 7 tests ... OK`（仓库测试总数从 27 → 34：`python -X utf8 -m unittest discover -s tests` 报 `Ran 34 tests`）

- [ ] **Step 5: 用一次真实干跑确认它对现状可用**

Run:
```bash
python -X utf8 scripts/shift_anchors.py --after 289 --delta 6 \
  "第一部分-基础篇/02-对话循环-Agent的心跳.md" \
  "en/Part-1-Foundations/02-The-Dialog-Loop-Heartbeat-of-an-Agent.md"
```
Expected（2026-11-02 实测）：26 行 `glosses.json: …:NNN -> NNN+6` 与 2 行 `manifest.json: …`，末行 `planned: 28 anchors`，且 `git diff --stat -- yuyu-book/` 为空（干跑不许写盘）。这 28 就是 Task 3 Step 4 该复现的数。

- [ ] **Step 6: 提交**

```bash
git add scripts/shift_anchors.py tests/test_shift_anchors.py
git commit -m "feat(book): 锚点平移脚本，正文插图落地时行号不再靠手改"
```

---

### Task 2: 补上胶片这一层的契约，并把三个没人钉的图数钉住

`test_build_contracts.py` 现在只钉了章徽那一层的「动画在两道闸里」；正文图版这一层（决策 2 的兑现处）没人钉，而下一轮就要连铺四张胶片。

顺带清三笔已经错了或马上要错的账（2026-11-02 实测）：

1. `en/README.md:113` 还写着「**Twenty-six** hand-drawn line illustrations」，磁盘上已经是 28 份——数字拼成英文单词，`\d+` 的正则根本抓不到它，所以没人发现；
2. `CREDITS.md:137` 的「**画风体系**：**28** 份插图（章徽、篇题刻、老驿卒、扉页车图、正文线描）」——同一个数在 `CREDITS.md:135` 被钉住了（`扉页一幅车图（共 (\d+) 份`），这一行没有；
3. `STRUCTURE.md:109` 的「+ **2** 幅正文插图」——同行开头的 `28 份手写 SVG` 被钉住了，这一个没有，而它恰恰是本计划要连改五次的数。

`test_docclaims.py` 的模块 docstring 里就写着上一回这类账怎么烂的（「a STRUCTURE row still saying "24 份图" after the twenty-fifth drawing shipped」）。这三处不钉，Task 3～7 每步都要靠人肉数数。

**Files:**
- Modify: `yuyu-book/tests/test_build_contracts.py`（`MotionGuards` 类，531 行之后）
- Modify: `yuyu-book/tests/test_docclaims.py`（`extract_illustrations` 的 import、`Data` 新方法 `body_plates`、`self.claims` 列表 126 行附近）
- Modify: `en/README.md:113`
- Modify: `yuyu-book/revisions.json`（`entries[0].zh` / `.en` 各追加一条）

**Interfaces:**
- Consumes: `CSS`（模块级字符串，测试类里已可用）、`ART.glob("*.svg")`、`yuyu_book.core.extract_illustrations(text, file) -> (body, ills)`
- Produces: `Data.body_plates(lang: str) -> int`（zh 侧当前返回 2）；构建器测试数 440 → 442（新增三条 claim 只是已有测试方法里的数据行，不新增测试），后续任务的账本注释都要写 442

- [ ] **Step 1: 写胶片动画层的失败测试**

在 `MotionGuards` 类内（`test_motion_stays_inside_its_guards` 之后）追加：

```python
    def test_the_filmstrip_only_moves_on_screen(self):
        """A sequential plate's stagger is the one promise the paper edition
        has to break: Chromium prints what it can compute, and a half-lit
        frame reads as a plate that failed to print. So every `.illu-seq` rule
        lives behind both guards, the hover layer resets the scroll range it
        inherits, and the hover rule comes last."""
        guarded_at = CSS.index("@supports (animation-timeline: view())")
        seq_at = CSS.index(".illu-seq .frame{")
        self.assertGreater(seq_at, guarded_at,
                           "the filmstrip staggers outside its guard")
        self.assertLess(CSS.index(".illu-seq .frame{", seq_at),
                        CSS.index(".illu-seq:hover .frame{"),
                        "the hover layer would beat the scroll ranges")
        hover = CSS[CSS.index(".illu-seq:hover .frame{"):][:120]
        self.assertIn("animation-timeline:auto", hover)
        self.assertIn("animation-range:normal", hover)
        print_block = CSS[CSS.index("@media print{"):]
        self.assertNotIn("ink-cycle", print_block,
                         "a runner survived into the print sheet")
        self.assertNotIn(".illu-seq", print_block)
```

该测试**当场就会通过**——2026-11-02 实测：`seq_at` 22138、`probe_at` 20133、`hover_at` 22851，打印块长 12581 字节且 `ink-cycle`／`.illu-seq`／`animation:` 三者皆无。这条测试钉的是「已经被遵守但没人看守」的规矩，而下一轮要在这个规矩上连铺四张胶片。所以证明它有效的手段不是看它红，而是变异：

```bash
# 变异 1：把胶片规则挪到 @supports 探针之前
python - <<'PY'
import re, pathlib
p = pathlib.Path("yuyu-book/yuyu_book/style.py")
t = p.read_text(encoding="utf-8")
p.with_suffix(".bak").write_text(t, encoding="utf-8")
PY
```
手工把 `style.py:728` 那两行 `.illu-seq .frame{…}` 剪到 `style.py:689` 的 `@media screen…` 之前，重跑本条测试必须红，然后 `mv yuyu-book/yuyu_book/style.py.bak yuyu-book/yuyu_book/style.py` 复原并确认转绿。变异 2：把 `.illu-seq:hover .frame{` 那段挪到 `nth-child` 之前，必须红于「the hover layer would beat the scroll ranges」。

- [ ] **Step 2: 写 shipped 胶片的帧序失败测试**

同文件末尾（`MotionGuards` 之外，新开一个 TestCase 类）追加：

```python
class FilmstripSource(unittest.TestCase):
    """A filmstrip's story is its frame order, and the CSS counts positions:
    `.illu-seq .frame:nth-child(1)` is only frame one if the groups really are
    the leading children. One nested `<g>` or one decorative group slipped in
    front, and the strip lights up out of order — invisibly, in print."""

    def test_every_shipped_filmstrip_puts_its_frames_first(self):
        art_dir = BOOK_DIR / "illustrations"
        seen = 0
        for path in sorted(art_dir.glob("*.svg")):
            svg = path.read_text(encoding="utf-8")
            root = svg[:svg.index(">")]
            if "seq" not in root:
                continue
            seen += 1
            groups = re.findall(r"<g\b[^>]*>", svg)
            frames = [g for g in groups if 'class="frame"' in g]
            self.assertGreaterEqual(len(frames), 4, f"{path.name}: a strip "
                                "of fewer than four frames is a line drawing")
            self.assertLessEqual(len(frames), 6, f"{path.name}: the CSS only "
                                "staggers six frames")
            first_other = next((i for i, g in enumerate(groups)
                                if 'class="frame"' not in g), len(groups))
            self.assertEqual(len(frames), first_other,
                             f"{path.name}: a frame sits after a "
                             "decorative group, so the scroll ranges "
                             "land on the wrong cells")
        self.assertGreaterEqual(seen, 1, "no filmstrip on disk to test")
```

`re` 与 `BOOK_DIR` 已在该文件顶部导入（`test_build_contracts.py:3` 与 `:11`），不必新增 import。类放在 `MotionGuards` 之后、`ChapterOpening`（555 行）之前。

Run: `python -X utf8 -m unittest yuyu-book.tests.test_build_contracts -k FilmstripSource -v`
Expected: PASS——`ch03-tool-pipeline.svg` 的组顺序是 `f,f,f,f,other,other`，`first_other` 数出 4，与帧数相等。变异验证：在它第一个帧组之后、第二个之前插一个 `<g opacity=".4">`，重跑必须红（`a frame sits after a decorative group`），撤掉转绿。

- [ ] **Step 3: 把三个没人钉的图数钉住**

**3a — `en/README.md:113` 的单词数改成数字，并说清正文图版。** 把

```
Twenty-six hand-drawn line illustrations — a four-horse chariot on the front page, one emblem per unit beside the chapter title, one engraving per part, a straw-hatted lantern-carrier at every chapter's end — are inked entirely in `currentColor`
```

替换成：

```
28 hand-drawn line illustrations — a four-horse chariot on the front page, one emblem per unit beside the chapter title, one engraving per part, a straw-hatted lantern-carrier at every chapter's end, and two plates inside the prose (a tool bench and a four-frame filmstrip) — are inked entirely in `currentColor`
```

**3b — 给 `Data` 加一个从正文取「正文图版数」的方法。** 这个数只能从正文取：货架上多出来的画不一定被点名，而 STRUCTURE 那一行列的是读者在章里读到的张数。`test_docclaims.py:20-21` 的 import 补上 `extract_illustrations`：

```python
from yuyu_book.core import (BOOK_DIR, REPO_ROOT, extract_illustrations,
                            extract_mermaid, load_json, read_text,
                            unit_stream)
```

`Data` 类内、`drawings()`（69 行）之后插入：

```python
    def body_plates(self, lang: str) -> int:
        """Plates the prose names, counted where they are named.

        The shelf holds the 26 fixed slots too (emblems, headpieces, cover,
        keeper); only a fence decides that a drawing is read inside a chapter,
        so STRUCTURE's count has to come off the manuscript, not the folder.
        """
        n = 0
        for rel in self.unit_path(lang):
            text = read_text(REPO_ROOT / rel)
            _body, ills = extract_illustrations(text, rel)
            n += len(ills)
        return n
```

2026-11-02 实测：zh 与 en 各返回 2，与 STRUCTURE.md 那行的「2 幅」一致。

**3c — 三条新 claim。** 在 `self.claims` 里，紧跟已有的 `("README.md", r"(\d+) 个主干术语的原理", ...)`（118 行）之后插入：

```python
            # three counts of the same figure went unpinned: an English number
            # spelled as a word, the style-system row, and the prose-plate row
            ("en/README.md", r"\b(\d+) hand-drawn line illustrations", [d]),
            ("CREDITS.md", r"\*\*画风体系\*\*：(\d+) 份插图", [d]),
            ("STRUCTURE.md", r"\+ (\d+) 幅正文插图",
             [str(self.body_plates("zh"))]),
```

Run: `python -X utf8 -m unittest yuyu-book.tests.test_docclaims -v`
Expected: 只改测试不改 `en/README.md` 时会红——`en/README.md: nothing matches '\\b(\\d+) hand-drawn line illustrations'`（这就是钉住的效力：单词式的数字对正则不可见）。三步都做完后 `OK`。

- [ ] **Step 4: 五道闸 + 计数确认**

```bash
python -X utf8 -m unittest discover -s yuyu-book/tests     # Expected: Ran 442 tests, OK
python -X utf8 -m unittest discover -s tests               # Expected: Ran 34 tests, OK
python -X utf8 yuyu-book/build.py --check                  # Expected: CHECK OK
python -X utf8 scripts/check_book.py                       # Expected: 0 errors
npm run check:diagrams                                     # Expected: 320 Mermaid diagrams, 0 errors
```

- [ ] **Step 5: 账本记一轮**

`yuyu-book/revisions.json` 的 `entries[0]["zh"]` 末尾追加（注意：反引号成对、不许出现 `@@`）：

```
"胶片这一层的契约补上了。章徽那层的「动画只活在三道闸里」早就钉住，正文图版这一层却没人管——下一轮要连铺四张逐格胶片，靠的正是同一批规则。现在两项测试把它钉死：`.illu-seq` 的每一条规则都必须排在 @supports 探针之后、悬停层必须显式清掉它继承来的滚动 range 且源序在后、打印块里不许出现 ink-cycle；另一项直接读磁盘上的画，要求凡是根元素标了 seq 的图，帧组必须是前 4～6 个子元素，装饰组只能排在后面。顺带清三笔旧账，都是同一个数在不同文档里各写一遍、只钉住了一遍：英文版 README 把插画数拼成英文单词 twenty-six，磁盘上其实 28 份；CREDITS 讲画风那一行也写着 28 份插图，没纳入契约；STRUCTURE 的「2 幅正文插图」同样是散数——现在它由正文里的 ill 围栏当场数出来，不再靠人记。构建器测试 442 项全绿。"
```

`entries[0]["en"]` 末尾追加对应英文，且必须以 `442 builder tests green.` 收尾：

```
"The filmstrip layer now has its own contract. The emblem layer's guards have been pinned for a while, but nothing checked the rules the body plates inherit — and four more strips are about to land on top of them. Two tests close it: every `.illu-seq` rule has to sit behind the @supports probe, the hover layer has to clear the scroll range it inherits and stay last in source order, and the print sheet may not carry ink-cycle; the other reads the drawings off disk and insists that any file whose root says seq puts its frame groups first, four to six of them. Three old debts are cleared alongside it, all the same failure — one figure written into several documents but pinned in only one: the English README spelled its illustration count as a word and had gone stale at twenty-six while the shelf held 28, the style-system row in CREDITS quotes the same 28 with nothing watching it, and STRUCTURE's count of plates inside the prose was a loose number that the build now recomputes from the ill fences themselves. 442 builder tests green."
```

Run: `python -X utf8 -m unittest yuyu-book.tests.test_docclaims -k suite -v` → `OK`

- [ ] **Step 6: 提交**

```bash
git add yuyu-book/tests/test_build_contracts.py yuyu-book/tests/test_docclaims.py en/README.md yuyu-book/revisions.json
git commit -m "test(book): 钉住逐格胶片的动画层与帧序，三个散落的图数纳入数字契约"
```

---

### Task 3: ch02 心跳四格胶片

对话循环是全书最讲顺序的一张图：提问 → 模型点工具 → 工具跑完 → 结果回填、再问一次。最后一格回头指到第一格，是这一节「循环」的全部论点。

**Files:**
- Create: `yuyu-book/illustrations/ch02-turn-loop.svg`
- Modify: `第一部分-基础篇/02-对话循环-Agent的心跳.md`（289 行之后插六行）
- Modify: `en/Part-1-Foundations/02-The-Dialog-Loop-Heartbeat-of-an-Agent.md`（289 行之后插六行）
- Modify: `yuyu-book/glosses.json`、`yuyu-book/manifest.json`（该两文件 >289 的锚点 +6）
- Modify: `scripts/build_illustration_gallery.py`、`README.md:113`、`STRUCTURE.md:109`、`CREDITS.md:135`、`en/README.md:113`、`yuyu-book/revisions.json`
- Test: 无新增（`test_docclaims` + 画廊守卫 + `build.py --check` 已覆盖）

**Interfaces:**
- Consumes: `Task 1` 的 `scripts/shift_anchors.py`
- Produces: 手写 SVG 29 份、正文图版 3 张、每版 plates 163（zh 与 en 各自）

- [ ] **Step 1: 画胶片本体**

Create `yuyu-book/illustrations/ch02-turn-loop.svg`（单行；`348×118`，比另几张高二十来像素，因为回环箭头要在卡片上方跑一条回头路；帧内 y 38～82，帧号基线 y 100）：

```xml
<svg class="a-turn seq" viewBox="0 0 348 118" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><g class="frame"><path d="M8 34q34-3 68 0q3 26 0 52q-34 3-68 0q-3-26 0-52" pathLength="100"/><path d="M16 44q24-2 48 0q2 9 0 18q-24 2-48 0q-2-9 0-18" pathLength="100"/><path d="M28 62l-3 8 10-6" pathLength="100"/><path d="M22 50h34" pathLength="100"/><path d="M22 56h26" pathLength="100"/><path d="M20 76h40" opacity=".55" stroke-width="1.2" pathLength="100"/><path d="M20 82h28" opacity=".35" stroke-width="1.2" pathLength="100"/><text class="frame-no" x="11" y="100" fill="currentColor" stroke="none">1</text></g><g class="frame"><path d="M96 34q34-3 68 0q3 26 0 52q-34 3-68 0q-3-26 0-52" pathLength="100"/><path d="M104 44q16-2 32 0q2 12 0 22q-16 2-32 0q-2-12 0-22" pathLength="100"/><path d="M112 52l-4 4 4 4" pathLength="100"/><path d="M126 52l4 4-4 4" pathLength="100"/><path d="M142 50h16" pathLength="100"/><path d="M142 58h12" pathLength="100"/><path d="M104 76h52" opacity=".55" stroke-width="1.2" pathLength="100"/><path d="M104 82h36" opacity=".35" stroke-width="1.2" pathLength="100"/><text class="frame-no" x="99" y="100" fill="currentColor" stroke="none">2</text></g><g class="frame"><path d="M184 34q34-3 68 0q3 26 0 52q-34 3-68 0q-3-26 0-52" pathLength="100"/><circle cx="206" cy="56" r="10" pathLength="100"/><circle cx="206" cy="56" r="3" fill="currentColor" stroke="none"/><path d="M206 41v5" pathLength="100"/><path d="M206 66v5" pathLength="100"/><path d="M191 56h5" pathLength="100"/><path d="M216 56h5" pathLength="100"/><path d="M232 40v44" opacity=".5" stroke-width="1.2" stroke-dasharray="3 5"/><path d="M240 52l4 4 8-9" pathLength="100"/><path d="M238 68h22" opacity=".55" stroke-width="1.2" pathLength="100"/><text class="frame-no" x="187" y="100" fill="currentColor" stroke="none">3</text></g><g class="frame"><path d="M272 34q34-3 68 0q3 26 0 52q-34 3-68 0q-3-26 0-52" pathLength="100"/><circle cx="280" cy="48" r="2" fill="currentColor" stroke="none"/><path d="M288 48h32" pathLength="100"/><circle cx="280" cy="58" r="2" fill="currentColor" stroke="none"/><path d="M288 58h26" pathLength="100"/><circle cx="280" cy="68" r="2" fill="currentColor" stroke="none"/><path d="M288 68h32" pathLength="100"/><path d="M278 80h44" opacity=".45" stroke-width="1.2" pathLength="100"/><text class="frame-no" x="275" y="100" fill="currentColor" stroke="none">4</text></g><g opacity=".45" stroke-width="1.3"><path d="M79 60h12" pathLength="100"/><path d="M89 58l3 2-3 2" pathLength="100"/><path d="M167 60h12" pathLength="100"/><path d="M177 58l3 2-3 2" pathLength="100"/><path d="M255 60h12" pathLength="100"/><path d="M265 58l3 2-3 2" pathLength="100"/></g><g opacity=".7" stroke-width="1.4"><path d="M306 34q2-20-16-21q-128-4-236 0q-18 1-16 21" pathLength="100"/><path d="M33 29l5 6 5-6" pathLength="100"/></g><g opacity=".16" stroke-width="6"><path d="M8 4h332" stroke-dasharray="6 13"/><path d="M8 108h332" stroke-dasharray="6 13"/></g></svg>
```

- [ ] **Step 2: 过 `art._read` 那道闸**

Run:
```bash
python -X utf8 -c "import sys;sys.path.insert(0,'yuyu-book');from yuyu_book import art;print(len(art.drawing('ch02-turn-loop')),'bytes inlined')"
```
Expected: `3011 bytes inlined`，无异常。（2026-11-02 已把计划里这段 XML 落进临时目录跑过一遍 `art.drawing`：3011 字节 < 20000 上限，`seq` 根元素、4 个帧组、装饰组都排在帧后。`>` 任何一条禁令都会抛 `BuildError`，那就按报错改画，别改闸门。）

- [ ] **Step 3: 双语各插六行**

两个文件都在 289 行（空行）之后插入。中文版：

```markdown
一个 Turn 走四拍：提问、模型点工具、工具跑完、结果回填再问。

```ill
ch02-turn-loop
```

```

英文版在同一行号之后插入：

```markdown
A turn runs on four beats: ask, the model picks a tool, the tool runs, the result goes back in and the loop asks again.

```ill
ch02-turn-loop
```

```

插入后自查。下面这些下标是按 2026-11-02 实测算出来的：`---` 原本在 290 行、`## 2.3` 原本在 292 行，六行块占掉 290～295，于是它们顺次落到 296 与 298 行（`splitlines()` 是 0 基，所以断言写成 `L[295]`／`L[297]`）；画名自己在第 293 行，即 `L[292]`：

```bash
python -X utf8 -c "
from pathlib import Path
for p in ['第一部分-基础篇/02-对话循环-Agent的心跳.md',
          'en/Part-1-Foundations/02-The-Dialog-Loop-Heartbeat-of-an-Agent.md']:
    L=Path(p).read_text(encoding='utf-8').splitlines()
    assert L[292]=='ch02-turn-loop', (p,293,L[292])
    assert sum(l=='ch02-turn-loop' for l in L)==1, p
    assert L[295].strip()=='---', (p,296,L[295])
    assert L[297].startswith('## 2.3'), (p,298,L[297])
    assert len(L)==451, (p,len(L))
print('both files: 445 -> 451 lines, one block each')
"
```

Expected: `both files: 445 -> 451 lines, one block each`。`sum(...)==1` 那条是防「同一围栏粘了两遍」——第一格插歪时，第二格往往还在。

- [ ] **Step 4: 平移锚点**

```bash
python -X utf8 scripts/shift_anchors.py --after 289 --delta 6 \
  "第一部分-基础篇/02-对话循环-Agent的心跳.md" \
  "en/Part-1-Foundations/02-The-Dialog-Loop-Heartbeat-of-an-Agent.md"
```
Expected：26 行 `glosses.json:` 加 2 行 `manifest.json:`，末行 `planned: 28 anchors`。与 Task 1 Step 5 一致后，把命令末尾补 `--write` 再跑一次。
Expected（写入后）：同样 28 行，末行 `written: 28 anchors`，`git diff --numstat -- yuyu-book/glosses.json yuyu-book/manifest.json` 报 `26 26` 与 `2 2`（一行改一行删，行数不变）。

若测出 28 以外的数，先停下：那说明注册表在计划写成之后又被改过，按当下的干跑数走，并把这个数同步进 Step 9 的中英账本注释。

- [ ] **Step 5: 让构建复核每一条锚点**

Run: `python -X utf8 yuyu-book/build.py --check`
Expected:
```
[zh]
  yuyu-agent-harness-zh.html: … 20 units, 163 plates, …
[en]
  yuyu-agent-harness-en.html: … 20 units, 163 plates, …
CHECK OK
```
只要有一条锚点没跟上，这里就会红：`… evidence … is inside a code fence, blank, or past the end of the file`。

- [ ] **Step 6: 挂进画廊**

`scripts/build_illustration_gallery.py`：
- `ORDER` 里把 `"ch02-turn-loop"` 插到 `"ch02"` 之后（第 24～28 行那段列表）；
- `WIDE` 改为 `WIDE = {"ch03-tool-bench": 300, "ch03-tool-pipeline": 330, "ch02-turn-loop": 330}`；
- `PLAIN` 加 `"ch02-turn-loop": "四格胶片：问一句、点工具、跑完、填回去再问",`；
- `PLAIN_EN` 加
```python
    "ch02-turn-loop": "A filmstrip: ask, pick a tool, run it, put the "
                      "result back and ask again",
```

Run: `python -X utf8 scripts/build_illustration_gallery.py`
Expected: `…\illustration-gallery.html (N bytes, 29 figures)`。（守卫 `on_disk != set(ORDER)` 会红，如果只画了图没登记。）

- [ ] **Step 7: 五处图数声明 +1**

Task 2 之后这些数全部被 `test_docclaims` 盯着，漏改一处就直接红——这一步的五个字符串都是 2026-11-02 实测的原文：

- `README.md:113`：`全书另有 28 份手写线描图` → `全书另有 29 份手写线描图`；同句破折号里的尾巴 `正文里一张工具台与一条四格胶片` → `正文里一组插图（一张工具台、一条四格胶片与一条心跳循环）`。括号从这一步就加上：往后的四步每步都要往这串列举里再加一项，不加括号它会和破折号外层的「扉页…、章徽…、题刻…」糊成同一条。
- `STRUCTURE.md:109`：`| 28 份手写 SVG` → `| 29 份手写 SVG`；同格内 `+ 2 幅正文插图` → `+ 3 幅正文插图`。
- `CREDITS.md:135`：`扉页一幅车图（共 28 份` → `扉页一幅车图（共 29 份`。
- `CREDITS.md:137`：`**画风体系**：28 份插图` → `**画风体系**：29 份插图`。
- `en/README.md:113`：`28 hand-drawn line illustrations` → `29 hand-drawn line illustrations`；`and two plates inside the prose (a tool bench and a four-frame filmstrip)` → `and three plates inside the prose (a tool bench, a scheduling filmstrip and a heartbeat loop)`。

Run: `python -X utf8 -m unittest yuyu-book.tests.test_docclaims -v` → `OK`

- [ ] **Step 8: 五道闸全跑**

```bash
python -X utf8 yuyu-book/build.py --check
python -X utf8 yuyu-book/build.py --check --mermaid=source
python -X utf8 -m unittest discover -s yuyu-book/tests   # Ran 442 tests, OK
python -X utf8 -m unittest discover -s tests             # Ran 34 tests, OK
python -X utf8 scripts/check_book.py                     # 0 errors
npm run check:diagrams                                   # 320 Mermaid, 0 errors
```

- [ ] **Step 9: 账本记一轮**

`entries[0]["zh"]` 末尾追加（以 `构建器测试 442 项全绿。` 收尾）：

```
"对话循环有了自己的四格胶片。2.2 这一节讲的是一句话进来、一句话出去，正文里原本只有一张终止条件的表，读者看得见状态、看不见节拍；现在四格并排：气泡里一行提问、模型交出的那段工具调用、齿轮在权限闸口前转一下、三条结果回填后再起一行，第四格上方有一条回头指第一格的弧线。图版落进正文是六行，注册表里指向 289 行之后的 28 条锚点因此各加六，这一步由刚写好的平移脚本做，构建时的白话层校验逐条复核——一条跟错就报错停止。中英两个文件行数继续一一对应（各 445 行变 451 行）。手写图 28→29 份，正文插图 2→3 张，每版图版 162→163 张。构建器测试 442 项全绿。"
```

`entries[0]["en"]` 末尾追加：

```
"The dialog loop now has its own four-frame strip. Section 2.2 is about one message in and one out, but the prose only carried a table of stop conditions: a reader could see the states and not the beat. Four cells now sit side by side — a question in a bubble, the tool call the model hands back, a gear turning once in front of the permission gate, three results written back before the next line — with an arc over the strip leading the fourth cell home to the first. A plate costs the prose six lines, so the 28 anchors in the two registries that point past line 289 each move by six; the shift script does the arithmetic and the build's plain-language check re-reads every one of them, failing the build if a single pointer lands wrong. The two language files stay line-for-line aligned (445 to 451 lines each). Hand-inked drawings 28 to 29, plates inside the prose 2 to 3, plates per edition 162 to 163. 442 builder tests green."
```

（账本注释里的反引号必须成对——`test_pages.test_revision_notes_are_typeset_not_left_in_markdown` 不许任何一个反引号落到页面上，落单的那个就是它抓的。上面两段各自只用了一处 code span。）

Run: `python -X utf8 -m unittest yuyu-book.tests.test_pages -k revision_notes -v` → `OK`

- [ ] **Step 10: 提交**

```bash
git add yuyu-book/illustrations/ch02-turn-loop.svg 第一部分-基础篇/02-对话循环-Agent的心跳.md en/Part-1-Foundations/02-The-Dialog-Loop-Heartbeat-of-an-Agent.md yuyu-book/glosses.json yuyu-book/manifest.json scripts/build_illustration_gallery.py README.md STRUCTURE.md CREDITS.md en/README.md yuyu-book/revisions.json docs/illustration-gallery.html
git diff --numstat -- 第一部分-基础篇 en/Part-1-Foundations
git commit -m "feat(book): ch02 对话循环四格胶片，正文图版第二张落在心跳那一节"
```
Expected（numstat）：两个 md 各 `6 0`（只加不删）。

---

### Task 4: ch01 五大原则的门廊

1.3 那一节是 ch01 最大的一块白墙（zh 2515 字符），五条原则各占一小节，读完只记住「有五条」。把它画成一道门廊：五样东西各自顶着同一根横梁。

**Files:**
- Create: `yuyu-book/illustrations/ch01-five-pillars.svg`
- Modify: `第一部分-基础篇/01-智能体编程的新范式.md`（384 行之后）
- Modify: `en/Part-1-Foundations/01-The-New-Paradigm-of-Agent-Programming.md`（384 行之后）
- Modify: `scripts/build_illustration_gallery.py`、`README.md`、`STRUCTURE.md`、`CREDITS.md`（135 与 137 两处）、`en/README.md`、`yuyu-book/revisions.json`
- 不动：`yuyu-book/glosses.json`、`yuyu-book/manifest.json`——实测这一处平移 0 条锚点（Step 4 会当场证明）

**Interfaces:**
- Consumes: Task 1 的脚本、Task 2 的两项测试（这张是 `line`，正好证明帧序测试只挑 seq、不误伤）
- Produces: 手写 SVG 30 份、正文图版 4 张

- [ ] **Step 1: 画门廊**

Create `yuyu-book/illustrations/ch01-five-pillars.svg`（`line`，非 seq；中心 x = 50/115/180/245/310，横梁 y 18/25，基线 y 96/102；五样东西从左到右依次是异步流式、边界内嵌、缓存分层、渐进扩展、不可变封存）：

```xml
<svg class="a-pillars" viewBox="0 0 340 120" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 18q162-4 324 0" pathLength="100"/><path d="M14 25q161-3 322 0" opacity=".55" stroke-width="1.2" pathLength="100"/><path d="M20 96q155-3 310 0" pathLength="100"/><path d="M24 102q151-2 302 0" opacity=".5" stroke-width="1.2" pathLength="100"/><g opacity=".45" stroke-width="1.2"><path d="M50 27v11" pathLength="100"/><path d="M115 27v11" pathLength="100"/><path d="M180 27v11" pathLength="100"/><path d="M245 27v11" pathLength="100"/><path d="M310 27v11" pathLength="100"/></g><g opacity=".92"><path d="M28 46q11-6 22 0t22 0" pathLength="100"/><path d="M28 60q11-6 22 0t22 0" pathLength="100"/><path d="M28 74q11-6 22 0t22 0" pathLength="100"/><path d="M70 70l5 4-5 4" pathLength="100"/><circle cx="39" cy="57" r="2" fill="currentColor" stroke="none"/></g><g opacity=".92"><path d="M93 44q22-4 44 0q4 22 0 44q-22 4-44 0q-4-23 0-44" pathLength="100"/><circle cx="115" cy="66" r="9" pathLength="100"/><circle cx="115" cy="66" r="2.4" fill="currentColor" stroke="none"/><path d="M115 40v6" opacity=".6" stroke-width="1.2" pathLength="100"/><path d="M115 88v6" opacity=".6" stroke-width="1.2" pathLength="100"/></g><g opacity=".92"><path d="M160 46q20-2 40 0q2 4 0 8q-20 2-40 0q-2-5 0-8" pathLength="100"/><path d="M160 60q20-2 40 0q2 4 0 8q-20 2-40 0q-2-5 0-8" pathLength="100"/><path d="M160 74q20-2 40 0q2 4 0 8q-20 2-40 0q-2-5 0-8" pathLength="100"/><path d="M172 49l4 4 8-9" pathLength="100"/><path d="M206 62q8 6 0 12" pathLength="100"/><path d="M203 72l3 4 4-3" pathLength="100"/></g><g opacity=".92"><path d="M223 86h13v-13h13v-13h13v-13h13" pathLength="100"/><path d="M268 52v-10" pathLength="100"/><path d="M265 45l3-4 3 4" pathLength="100"/></g><g opacity=".92"><path d="M288 46q22-3 44 0q3 22 0 44q-22 3-44 0q-3-22 0-44" pathLength="100"/><circle cx="310" cy="68" r="10" pathLength="100"/><path d="M305 68l4 4 8-9" pathLength="100"/><path d="M310 40v6" opacity=".6" stroke-width="1.2" pathLength="100"/></g><g opacity=".5" stroke-width="1.2"><path d="M60 92q6 3 12 0" pathLength="100"/><path d="M190 92q6 3 12 0" pathLength="100"/><path d="M256 92q6 3 12 0" pathLength="100"/></g><circle cx="34" cy="90" r="1.6" fill="currentColor" stroke="none" opacity=".6"/><circle cx="300" cy="90" r="1.6" fill="currentColor" stroke="none" opacity=".6"/></svg>
```

- [ ] **Step 2: 过闸**

```bash
python -X utf8 -c "import sys;sys.path.insert(0,'yuyu-book');from yuyu_book import art;print(len(art.drawing('ch01-five-pillars')),'bytes inlined')"
```
Expected: `2411 bytes inlined`，无异常（2026-11-02 实测：这一段跑过 `art.drawing`；根元素没有 `seq`，所以 `FilmstripSource` 会跳过它——这正是它在本批里的用处）。

- [ ] **Step 3: 双语各插六行**

中文版 384 行（空行）之后：

```markdown
五条原则撑起同一扇门：先流式、边界内嵌、缓存感知、能力渐进、状态不可变。

```ill
ch01-five-pillars
```

```

英文版同位置：

```markdown
Five principles hold up the same lintel: stream first, guard the perimeter, design for the cache, grow capability, keep state immutable.

```ill
ch01-five-pillars
```

```

自查。`---` 原本在 385 行、`## 实战练习：安装与初次诊断` 原本在 387 行；六行块占 385～390，于是它们落到 391 与 393 行。画名在第 388 行，即 `L[387]`：

```bash
python -X utf8 -c "
from pathlib import Path
for p in ['第一部分-基础篇/01-智能体编程的新范式.md',
          'en/Part-1-Foundations/01-The-New-Paradigm-of-Agent-Programming.md']:
    L=Path(p).read_text(encoding='utf-8').splitlines()
    assert L[387]=='ch01-five-pillars', (p,388,L[387])
    assert sum(l=='ch01-five-pillars' for l in L)==1, p
    assert L[390].strip()=='---', (p,391,L[390])
    assert L[392].startswith('## '), (p,393,L[392])
    assert len(L)==469, (p,len(L))
print('both files: 463 -> 469 lines, one block each')
"
```

Expected: `both files: 463 -> 469 lines, one block each`。英文版那一行是 `## Hands-On Exercise: Installation and Initial Diagnosis`，所以断言只钉 `## ` 前缀，不钉中文标题串。

- [ ] **Step 4: 平移锚点（这一处是零，仍然要跑）**

```bash
python -X utf8 scripts/shift_anchors.py --after 384 --delta 6 \
  "第一部分-基础篇/01-智能体编程的新范式.md" \
  "en/Part-1-Foundations/01-The-New-Paradigm-of-Agent-Programming.md"
```
Expected（2026-11-02 实测）：只有末行 `planned: 0 anchors`，一行明细都没有——两份注册表里没有一条锚点指向 ch01 的 384 行之后（1.3 之后只剩「实战练习」一节，注册表不引练习题）。**这一处不需要 `--write`**，而 `git diff -- yuyu-book/` 必须为空；跑出非零说明注册表在计划之后被改过，那就按当下的数写并同步 Step 9 的账本。

留这一步不是仪式：脚本对每个文件都跑一遍，0 与「脚本没找到这个文件」（返回 2 并打印 `no such prose file`）是两种不同的信号，只有跑过才分得开。

- [ ] **Step 5: 构建复核**

`python -X utf8 yuyu-book/build.py --check` → 每版 `164 plates`，`CHECK OK`

- [ ] **Step 6: 画廊**

`ORDER` 里把 `"ch01-five-pillars"` 插到 `"ch01"` 之后；`WIDE` 加 `"ch01-five-pillars": 300`；
`PLAIN` 加 `"ch01-five-pillars": "一道门廊：五条原则顶着同一根横梁",`；
`PLAIN_EN` 加 `"ch01-five-pillars": "A portico: five principles under one lintel",`。

Run: `python -X utf8 scripts/build_illustration_gallery.py` → `30 figures`

- [ ] **Step 7: 五处图数声明 +1**

- `README.md:113`：`全书另有 29 份手写线描图` → `全书另有 30 份手写线描图`；括号里 `一条四格胶片与一条心跳循环）` → `一条四格胶片、一条心跳循环与一道五柱门廊）`。
- `STRUCTURE.md:109`：`| 29 份手写 SVG` → `| 30 份手写 SVG`；`+ 3 幅正文插图` → `+ 4 幅正文插图`。
- `CREDITS.md:135`：`扉页一幅车图（共 29 份` → `扉页一幅车图（共 30 份`。
- `CREDITS.md:137`：`**画风体系**：29 份插图` → `**画风体系**：30 份插图`。
- `en/README.md:113`：`29 hand-drawn line illustrations` → `30 hand-drawn line illustrations`；`three plates inside the prose (a tool bench, a scheduling filmstrip and a heartbeat loop)` → `four plates inside the prose (a tool bench, a scheduling filmstrip, a heartbeat loop and a five-column portico)`。

Run: `python -X utf8 -m unittest yuyu-book.tests.test_docclaims -v` → `OK`

- [ ] **Step 8: 五道闸全跑**

```bash
python -X utf8 yuyu-book/build.py --check
python -X utf8 yuyu-book/build.py --check --mermaid=source
python -X utf8 -m unittest discover -s yuyu-book/tests   # Ran 442 tests, OK
python -X utf8 -m unittest discover -s tests             # Ran 34 tests, OK
python -X utf8 scripts/check_book.py                     # 0 errors（Markdown 文件数随计划文档变动，不作断言）
npm run check:diagrams                                   # 320 Mermaid diagrams, 0 errors
```

- [ ] **Step 9: 账本记一轮**

`entries[0]["zh"]` 末尾追加：

```
"1.3 那堵白墙有了形状。五大原则各占一小节，读完只记住「有五条」；现在它们是一道门廊：同一根横梁下五样东西——流水一样的三条波纹、嵌进边框的罗盘、三层带签的抽屉、一路向上的台阶、盖上印的封条。这一张是本批五张里唯一不逐格显影的：根元素没标 seq，所以它只描线、不滚动播放，也正因此能证明 Task 2 那条帧序测试只挑标了 seq 的画、不误伤单幅。落点在 384 行之后，注册表里没有一条锚点指向 ch01 这么靠后（平移脚本报 0），所以账本上这次的锚点数是零——脚本跑过才知道是零还是漏。中英各 463 行变 469 行。手写图 29→30 份，正文插图 3→4 张，每版图版 163→164 张。构建器测试 442 项全绿。"
```

`entries[0]["en"]` 末尾追加：

```
"Section 1.3 now has a shape. The five principles each own a subsection and readers came away remembering only "five of them"; they are a portico now, five objects under one lintel — three rippling strokes, a compass set into its own frame, a three-drawer stack with a tag, steps climbing one above the last, a sealed crate under its stamp. This is the only plate in the batch that never staggers: its root carries no seq, so it inks its lines and stops, which is also what proves the frame-order test from the previous round only picks up strips and leaves single drawings alone. The block lands after line 384, and the shift script reported zero anchors back of it — the registries never quote ch01 that far down, so this round's arithmetic is an honest 0, which only shows up as 0 if you run it. Both language files go from 463 to 469 lines. Hand-inked drawings 29 to 30, plates inside the prose 3 to 4, plates per edition 163 to 164. 442 builder tests green."
```

- [ ] **Step 10: 提交**

```bash
git add yuyu-book/illustrations/ch01-five-pillars.svg 第一部分-基础篇/01-智能体编程的新范式.md en/Part-1-Foundations/01-The-New-Paradigm-of-Agent-Programming.md scripts/build_illustration_gallery.py README.md STRUCTURE.md CREDITS.md en/README.md yuyu-book/revisions.json docs/illustration-gallery.html
git diff --numstat -- 第一部分-基础篇 en/Part-1-Foundations
git commit -m "feat(book): ch01 五大原则门廊图版，1.3 那堵白墙有了形状"
```
Expected（numstat）：两个 md 各 `6 0`。本任务不动两份注册表（Step 4 报 0），所以 `git add` 里没有它们——加上也不报错，但 diff 里出现 `glosses.json` 就说明有别的东西被改了，要查。

---

### Task 5: ch04 权限管线的四道门

4.1 讲四个阶段：validateInput 验形状、hasPermissionsToUseTool 匹配规则、checkPermissions 评估上下文、交互式提示问人。四格胶片正好一格一阶段，且第四格必须看出「一分为二：放行与拦截」。

**Files:**
- Create: `yuyu-book/illustrations/ch04-gate-steps.svg`
- Modify: `第一部分-基础篇/04-权限管线-Agent的护栏.md`（170 行之后）
- Modify: `en/Part-1-Foundations/04-The-Permission-Pipeline-Agent-Guardrails.md`（170 行之后）
- Modify: `yuyu-book/glosses.json`（7 条）、`yuyu-book/manifest.json`（2 条）
- Modify: `scripts/build_illustration_gallery.py`、`README.md`、`STRUCTURE.md`、`CREDITS.md`（135 与 137 两处）、`en/README.md`、`yuyu-book/revisions.json`

**Interfaces:**
- Consumes: Task 1 的脚本、Task 2 的帧序测试（这张是 seq，必须被它挑中并通过）
- Produces: 手写 SVG 31 份、正文图版 5 张、每版 plates 165

- [ ] **Step 1: 画四道门**

Create `yuyu-book/illustrations/ch04-gate-steps.svg`（`seq`，`348×106` 标准几何：卡片 y 15～72，帧号基线 y 84，走纸虚线 y 8／96，格间箭头 y 44）：

```xml
<svg class="a-gates seq" viewBox="0 0 348 106" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><g class="frame"><path d="M8 18q34-3 68 0q3 26 0 52q-34 3-68 0q-3-26 0-52" pathLength="100"/><path d="M18 26q20-2 40 0q2 15 0 29q-20 2-40 0q-2-14 0-29" pathLength="100"/><path d="M24 34h24" pathLength="100"/><path d="M24 42h20" pathLength="100"/><path d="M24 50h26" pathLength="100"/><path d="M50 60l4 4 8-9" pathLength="100"/><text class="frame-no" x="11" y="84" fill="currentColor" stroke="none">1</text></g><g class="frame"><path d="M96 18q34-3 68 0q3 26 0 52q-34 3-68 0q-3-26 0-52" pathLength="100"/><path d="M104 28h7v7h-7z" pathLength="100"/><path d="M104 40h7v7h-7z" pathLength="100"/><path d="M104 52h7v7h-7z" pathLength="100"/><path d="M116 32h30" pathLength="100"/><path d="M116 44h26" pathLength="100"/><path d="M116 56h32" pathLength="100"/><circle cx="107.5" cy="31.5" r="1.8" fill="currentColor" stroke="none"/><text class="frame-no" x="99" y="84" fill="currentColor" stroke="none">2</text></g><g class="frame"><path d="M184 18q34-3 68 0q3 26 0 52q-34 3-68 0q-3-26 0-52" pathLength="100"/><path d="M192 28q16-2 32 0q2 5 0 10q-16 2-32 0q-2-6 0-10" pathLength="100"/><path d="M192 40q16-2 32 0q2 5 0 10q-16 2-32 0q-2-6 0-10" pathLength="100"/><path d="M192 52q16-2 32 0q2 5 0 10q-16 2-32 0q-2-6 0-10" pathLength="100"/><circle cx="234" cy="38" r="9" pathLength="100"/><path d="M241 45l6 7" pathLength="100"/><text class="frame-no" x="187" y="84" fill="currentColor" stroke="none">3</text></g><g class="frame"><path d="M272 18q34-3 68 0q3 26 0 52q-34 3-68 0q-3-26 0-52" pathLength="100"/><path d="M280 22q24-2 48 0q2 7 0 14q-24 2-48 0q-2-7 0-14" pathLength="100"/><path d="M292 36l-3 7 9-5" pathLength="100"/><path d="M286 29h28" pathLength="100"/><path d="M282 50l4 4 8-9" pathLength="100"/><path d="M298 50h18" pathLength="100"/><path d="M284 58l7 7" pathLength="100"/><path d="M291 58l-7 7" pathLength="100"/><path d="M298 64h16" opacity=".6" stroke-width="1.2" pathLength="100"/><text class="frame-no" x="275" y="84" fill="currentColor" stroke="none">4</text></g><g opacity=".45" stroke-width="1.3"><path d="M79 44h12" pathLength="100"/><path d="M89 42l3 2-3 2" pathLength="100"/><path d="M167 44h12" pathLength="100"/><path d="M177 42l3 2-3 2" pathLength="100"/><path d="M255 44h12" pathLength="100"/><path d="M265 42l3 2-3 2" pathLength="100"/></g><g opacity=".16" stroke-width="6"><path d="M8 8h332" stroke-dasharray="6 13"/><path d="M8 96h332" stroke-dasharray="6 13"/></g></svg>
```

- [ ] **Step 2: 过闸**

```bash
python -X utf8 -c "import sys;sys.path.insert(0,'yuyu-book');from yuyu_book import art;print(len(art.drawing('ch04-gate-steps')),'bytes inlined')"
```
Expected: `2545 bytes inlined`，无异常（2026-11-02 实测：4 个帧组、装饰组都在帧组之后）。若报 `contains an id= attribute`，检查有没有误写 `data-id=`：`\bid\s*=` 会连它一起拦。

- [ ] **Step 3: 双语各插六行**

中文 170 行之后（这一处后面紧跟 `## 4.2`，所以是「落在 4.1 末尾」，题注取 4.1）：

```markdown
一次工具调用要过四道门：格式、规则、上下文，最后才是人。

```ill
ch04-gate-steps
```

```

英文：

```markdown
One tool call passes four gates: shape, rules, context — and only last, a human.

```ill
ch04-gate-steps
```

```

自查。`## 4.2 PermissionContext 的设计` 原本紧贴落点（171 行），六行块把它推到 177 行——这是五个落点里唯一一处「下一行就是 H2」，所以这道断言同时证明图没有把下一节的标题顶走：

```bash
python -X utf8 -c "
from pathlib import Path
for p in ['第一部分-基础篇/04-权限管线-Agent的护栏.md',
          'en/Part-1-Foundations/04-The-Permission-Pipeline-Agent-Guardrails.md']:
    L=Path(p).read_text(encoding='utf-8').splitlines()
    assert L[173]=='ch04-gate-steps', (p,174,L[173])
    assert sum(l=='ch04-gate-steps' for l in L)==1, p
    assert L[176].startswith('## 4.2'), (p,177,L[176])
    assert len(L)==566, (p,len(L))
print('both files: 560 -> 566 lines, 4.2 still opens on its own line')
"
```

Expected: `both files: 560 -> 566 lines, 4.2 still opens on its own line`

- [ ] **Step 4: 平移锚点**

```bash
python -X utf8 scripts/shift_anchors.py --after 170 --delta 6 \
  "第一部分-基础篇/04-权限管线-Agent的护栏.md" \
  "en/Part-1-Foundations/04-The-Permission-Pipeline-Agent-Guardrails.md"
```
Expected（2026-11-02 实测）：7 行 `glosses.json:` + 2 行 `manifest.json:`，末行 `planned: 9 anchors`。核对无误后补 `--write`，末行变成 `written: 9 anchors`，`git diff --numstat -- yuyu-book/glosses.json yuyu-book/manifest.json` 报 `7 7` 与 `2 2`。

- [ ] **Step 5: 构建复核**

Run: `python -X utf8 yuyu-book/build.py --check`
Expected: 两份日志各报 `20 units, 165 plates`，末行 `CHECK OK`。锚点跟错会在这里红：`… evidence … is inside a code fence, blank, or past the end of the file`。

- [ ] **Step 6: 挂进画廊**

`scripts/build_illustration_gallery.py`：
- `ORDER` 里把 `"ch04-gate-steps"` 插到 `"ch04"` 之后；
- `WIDE` 加一行条目，改完是 `WIDE = {"ch03-tool-bench": 300, "ch03-tool-pipeline": 330, "ch02-turn-loop": 330, "ch01-five-pillars": 300, "ch04-gate-steps": 330}`（按已落地的条目累积，此处只新增 `"ch04-gate-steps": 330`）；
- `PLAIN` 加 `"ch04-gate-steps": "四格胶片：验格式、比规则、看上下文、最后问人",`；
- `PLAIN_EN` 加
```python
    "ch04-gate-steps": "A filmstrip: check the shape, match a rule, "
                       "weigh the context, then ask",
```

Run: `python -X utf8 scripts/build_illustration_gallery.py`
Expected: `…\illustration-gallery.html (N bytes, 31 figures)`

- [ ] **Step 7: 五处图数声明 +1**

- `README.md:113`：`全书另有 30 份手写线描图` → `全书另有 31 份手写线描图`；括号里 `一条心跳循环与一道五柱门廊）` → `一条心跳循环、一道五柱门廊与四道权限门）`。
- `STRUCTURE.md:109`：`| 30 份手写 SVG` → `| 31 份手写 SVG`；`+ 4 幅正文插图` → `+ 5 幅正文插图`。
- `CREDITS.md:135`：`扉页一幅车图（共 30 份` → `扉页一幅车图（共 31 份`。
- `CREDITS.md:137`：`**画风体系**：30 份插图` → `**画风体系**：31 份插图`。
- `en/README.md:113`：`30 hand-drawn line illustrations` → `31 hand-drawn line illustrations`；`four plates inside the prose (a tool bench, a scheduling filmstrip, a heartbeat loop and a five-column portico)` → `five plates inside the prose (a tool bench, a scheduling filmstrip, a heartbeat loop, a five-column portico and four permission gates)`。

Run: `python -X utf8 -m unittest yuyu-book.tests.test_docclaims -v` → `OK`

- [ ] **Step 8: 五道闸全跑**

```bash
python -X utf8 yuyu-book/build.py --check
python -X utf8 yuyu-book/build.py --check --mermaid=source
python -X utf8 -m unittest discover -s yuyu-book/tests   # Ran 442 tests, OK
python -X utf8 -m unittest discover -s tests             # Ran 34 tests, OK
python -X utf8 scripts/check_book.py                     # 0 errors（Markdown 文件数随计划文档变动，不作断言）
npm run check:diagrams                                   # 320 Mermaid diagrams, 0 errors
```

- [ ] **Step 9: 账本记一轮**

`entries[0]["zh"]` 末尾追加：

```
"权限管线有了自己的四道门。4.1 把一次工具调用拆成 validateInput、hasPermissionsToUseTool、checkPermissions、交互式提示四段，正文是四段散文加一张表，读者读完知道有四步、不知道第四步会一分为二；现在四格并排，第四格里一条路线分出上下两笔——一笔打勾、一笔打叉，放行与拦截同格显影。落点选在 4.1 末尾、4.2 标题之前，图版占六行，原本紧贴落点的 `## 4.2` 顺次推到 177 行，注册表里指向 170 行之后的 9 条锚点各加六。中英各 560 行变 566 行。手写图 30→31 份，正文插图 4→5 张，每版图版 164→165 张。构建器测试 442 项全绿。"
```

`entries[0]["en"]` 末尾追加：

```
"The permission pipeline now shows its four gates. Section 4.1 splits one tool call into validateInput, hasPermissionsToUseTool, checkPermissions and the interactive prompt, but as four paragraphs and a table a reader learns there are four steps without seeing that the last one forks; in the strip's fourth cell a single route splits into two strokes — one check, one cross — so allow and block develop together. The plate sits at the end of 4.1, before the 4.2 heading, costing the prose six lines and pushing that heading to line 177; the 9 anchors in the two registries pointing past line 170 each move by six. Both language files go from 560 to 566 lines. Hand-inked drawings 30 to 31, plates inside the prose 4 to 5, plates per edition 164 to 165. 442 builder tests green."
```

Run: `python -X utf8 -m unittest yuyu-book.tests.test_pages -k revision_notes -v` → `OK`

- [ ] **Step 10: 提交**

```bash
git add yuyu-book/illustrations/ch04-gate-steps.svg 第一部分-基础篇/04-权限管线-Agent的护栏.md en/Part-1-Foundations/04-The-Permission-Pipeline-Agent-Guardrails.md yuyu-book/glosses.json yuyu-book/manifest.json scripts/build_illustration_gallery.py README.md STRUCTURE.md CREDITS.md en/README.md yuyu-book/revisions.json docs/illustration-gallery.html
git diff --numstat -- 第一部分-基础篇 en/Part-1-Foundations
git commit -m "feat(book): ch04 权限四道门胶片，第四格里放行与拦截一分为二"
```
Expected（numstat）：两个 md 各 `6 0`。

---

### Task 6: ch08 钩子接手的那一刻

8.2 罗列了二十来个生命周期事件，读者记不住名字，但能记住「事件响起、钩子把它挂住、脚本跑一段、下一步被改写」这四拍。第四格必须同时给出「放行」与「阻断」，否则图只讲了一半。

**Files:**
- Create: `yuyu-book/illustrations/ch08-hook-line.svg`
- Modify: `第二部分-核心系统篇/08-钩子系统-Agent的生命周期扩展点.md`（528 行之后）
- Modify: `en/Part-2-Core-Systems/08-The-Hook-System-Agent-Lifecycle-Extension-Points.md`（528 行之后）
- Modify: `yuyu-book/glosses.json`（1 条）、`yuyu-book/manifest.json`（2 条）
- Modify: `scripts/build_illustration_gallery.py`、`README.md`、`STRUCTURE.md`、`CREDITS.md`（135 与 137 两处）、`en/README.md`、`yuyu-book/revisions.json`

**Interfaces:**
- Consumes: Task 1 的脚本、Task 2 的帧序测试
- Produces: 手写 SVG 32 份、正文图版 6 张、每版 plates 166

- [ ] **Step 1: 画四拍**

Create `yuyu-book/illustrations/ch08-hook-line.svg`（`seq`，标准 `348×106` 几何）：

```xml
<svg class="a-hooks seq" viewBox="0 0 348 106" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><g class="frame"><path d="M8 18q34-3 68 0q3 26 0 52q-34 3-68 0q-3-26 0-52" pathLength="100"/><path d="M28 26q10-3 20 0q3 10 1 18q-11 3-22 0q-2-9 1-18" pathLength="100"/><path d="M26 45h24" pathLength="100"/><circle cx="38" cy="50" r="2" fill="currentColor" stroke="none"/><path d="M16 30q-4 8 0 16" opacity=".5" stroke-width="1.2" pathLength="100"/><path d="M60 30q4 8 0 16" opacity=".5" stroke-width="1.2" pathLength="100"/><path d="M20 62h36" opacity=".45" stroke-width="1.2" pathLength="100"/><text class="frame-no" x="11" y="84" fill="currentColor" stroke="none">1</text></g><g class="frame"><path d="M96 18q34-3 68 0q3 26 0 52q-34 3-68 0q-3-26 0-52" pathLength="100"/><path d="M100 46h56" stroke-width="2" pathLength="100"/><path d="M124 22v12q0 8 8 8h6" pathLength="100"/><path d="M136 38l4 4-6 3" pathLength="100"/><path d="M102 28h14" opacity=".55" stroke-width="1.2" pathLength="100"/><path d="M102 34h10" opacity=".55" stroke-width="1.2" pathLength="100"/><circle cx="152" cy="46" r="2.2" fill="currentColor" stroke="none"/><text class="frame-no" x="99" y="84" fill="currentColor" stroke="none">2</text></g><g class="frame"><path d="M184 18q34-3 68 0q3 26 0 52q-34 3-68 0q-3-26 0-52" pathLength="100"/><path d="M192 24q16-2 32 0q2 14 0 26q-16 2-32 0q-2-14 0-27" pathLength="100"/><path d="M198 32l5 4-5 4" pathLength="100"/><path d="M207 36h12" pathLength="100"/><circle cx="200" cy="48" r="1.8" fill="currentColor" stroke="none"/><circle cx="206" cy="48" r="1.8" fill="currentColor" stroke="none"/><circle cx="212" cy="48" r="1.8" fill="currentColor" stroke="none"/><path d="M196 58h26" opacity=".55" stroke-width="1.2" pathLength="100"/><text class="frame-no" x="187" y="84" fill="currentColor" stroke="none">3</text></g><g class="frame"><path d="M272 18q34-3 68 0q3 26 0 52q-34 3-68 0q-3-26 0-52" pathLength="100"/><circle cx="284" cy="42" r="3" fill="currentColor" stroke="none"/><path d="M290 40q14-8 30-6" pathLength="100"/><path d="M318 32l6 2-3 6" pathLength="100"/><path d="M300 26h20" opacity=".55" stroke-width="1.2" pathLength="100"/><path d="M290 46q12 8 26 8" pathLength="100"/><path d="M318 52l7 7" pathLength="100"/><path d="M325 52l-7 7" pathLength="100"/><path d="M276 60q10 6 24 4" opacity=".5" stroke-width="1.2" stroke-dasharray="2 4"/><text class="frame-no" x="275" y="84" fill="currentColor" stroke="none">4</text></g><g opacity=".45" stroke-width="1.3"><path d="M79 44h12" pathLength="100"/><path d="M89 42l3 2-3 2" pathLength="100"/><path d="M167 44h12" pathLength="100"/><path d="M177 42l3 2-3 2" pathLength="100"/><path d="M255 44h12" pathLength="100"/><path d="M265 42l3 2-3 2" pathLength="100"/></g><g opacity=".16" stroke-width="6"><path d="M8 8h332" stroke-dasharray="6 13"/><path d="M8 96h332" stroke-dasharray="6 13"/></g></svg>
```

- [ ] **Step 2: 过闸**

```bash
python -X utf8 -c "import sys;sys.path.insert(0,'yuyu-book');from yuyu_book import art;print(len(art.drawing('ch08-hook-line')),'bytes inlined')"
```
Expected: `2918 bytes inlined`，无异常（2026-11-02 实测：4 帧，装饰组在帧后）。

- [ ] **Step 3: 双语各插六行**（528 行之后；下一行是 `---`）

中文：

```markdown
钩子在四个时刻接手：事件响起、规则挂上、脚本跑完、下一步被改写。

```ill
ch08-hook-line
```

```

英文：

```markdown
A hook takes over at four moments: the event rings, a matcher hooks it, the script runs, the next step gets rewritten.

```ill
ch08-hook-line
```

```

自查。`---` 原本 529 行、`## 8.3 钩子响应协议` 原本 531 行；六行块占 529～534，于是它们落到 535 与 537 行。画名在第 532 行，即 `L[531]`：

```bash
python -X utf8 -c "
from pathlib import Path
for p in ['第二部分-核心系统篇/08-钩子系统-Agent的生命周期扩展点.md',
          'en/Part-2-Core-Systems/08-The-Hook-System-Agent-Lifecycle-Extension-Points.md']:
    L=Path(p).read_text(encoding='utf-8').splitlines()
    assert L[531]=='ch08-hook-line', (p,532,L[531])
    assert sum(l=='ch08-hook-line' for l in L)==1, p
    assert L[534].strip()=='---', (p,535,L[534])
    assert L[536].startswith('## 8.3'), (p,537,L[536])
    assert len(L)==1065, (p,len(L))
print('both files: 1059 -> 1065 lines, 8.3 opens where it should')
"
```

Expected: `both files: 1059 -> 1065 lines, 8.3 opens where it should`

- [ ] **Step 4: 平移锚点**

```bash
python -X utf8 scripts/shift_anchors.py --after 528 --delta 6 \
  "第二部分-核心系统篇/08-钩子系统-Agent的生命周期扩展点.md" \
  "en/Part-2-Core-Systems/08-The-Hook-System-Agent-Lifecycle-Extension-Points.md"
```
Expected（2026-11-02 实测）：1 行 `glosses.json:` + 2 行 `manifest.json:`，末行 `planned: 3 anchors`；补 `--write` 后 `written: 3 anchors`。

- [ ] **Step 5: 构建复核**

Run: `python -X utf8 yuyu-book/build.py --check`
Expected: 两份日志各报 `20 units, 166 plates`，末行 `CHECK OK`。

- [ ] **Step 6: 挂进画廊**

`scripts/build_illustration_gallery.py`：
- `ORDER` 里把 `"ch08-hook-line"` 插到 `"ch08"` 之后；
- `WIDE` 加条目 `"ch08-hook-line": 330`；
- `PLAIN` 加 `"ch08-hook-line": "四格胶片：铃响、挂住、跑脚本、改写下一步",`；
- `PLAIN_EN` 加
```python
    "ch08-hook-line": "A filmstrip: the event rings, a hook catches it, "
                      "the script runs, the path changes",
```

Run: `python -X utf8 scripts/build_illustration_gallery.py`
Expected: `…\illustration-gallery.html (N bytes, 32 figures)`

- [ ] **Step 7: 五处图数声明 +1**

- `README.md:113`：`全书另有 31 份手写线描图` → `全书另有 32 份手写线描图`；括号里 `一道五柱门廊与四道权限门）` → `一道五柱门廊、四道权限门与一声钩响）`。
- `STRUCTURE.md:109`：`| 31 份手写 SVG` → `| 32 份手写 SVG`；`+ 5 幅正文插图` → `+ 6 幅正文插图`。
- `CREDITS.md:135`：`扉页一幅车图（共 31 份` → `扉页一幅车图（共 32 份`。
- `CREDITS.md:137`：`**画风体系**：31 份插图` → `**画风体系**：32 份插图`。
- `en/README.md:113`：`31 hand-drawn line illustrations` → `32 hand-drawn line illustrations`；`five plates inside the prose (… and four permission gates)` → `six plates inside the prose (a tool bench, a scheduling filmstrip, a heartbeat loop, a five-column portico, four permission gates and a hook line)`。

Run: `python -X utf8 -m unittest yuyu-book.tests.test_docclaims -v` → `OK`

- [ ] **Step 8: 五道闸全跑**

```bash
python -X utf8 yuyu-book/build.py --check
python -X utf8 yuyu-book/build.py --check --mermaid=source
python -X utf8 -m unittest discover -s yuyu-book/tests   # Ran 442 tests, OK
python -X utf8 -m unittest discover -s tests             # Ran 34 tests, OK
python -X utf8 scripts/check_book.py                     # 0 errors（Markdown 文件数随计划文档变动，不作断言）
npm run check:diagrams                                   # 320 Mermaid diagrams, 0 errors
```

- [ ] **Step 9: 账本记一轮**

`entries[0]["zh"]` 末尾追加：

```
"8.2 列了二十来个生命周期事件，名字记不住，节拍记得住。四格这样排：一只钟在两堵弧墙之间响起（事件），一根横梁上垂下钩子把它挂住（matcher 匹配），一格脚本跑三行输出打点（handler 执行），第四格从一个点分出两条路——上面一条实线继续走、下面一条虚线被截住，放行与阻断同时显影。这一格的分叉和 4.1 那张不是一回事：那里分的是一次调用「过」还是「拦」，调用本身没变；这里分的是下一步被换成了哪条路，所以钩子那两弧墙之间的钟，最后动的是路线。落点在 528 行之后、`## 8.3` 之前，图版占六行，`## 8.3` 落到 537 行，注册表里 3 条指向 528 行之后的锚点各加六。中英各 1059 行变 1065 行。手写图 31→32 份，正文插图 5→6 张，每版图版 165→166 张。构建器测试 442 项全绿。"
```

`entries[0]["en"]` 末尾追加：

```
"Section 8.2 lists some twenty lifecycle events; a reader forgets the names and keeps the beat. The four cells are: a bell ringing between two curved walls (the event), a hook dropping from a crossbar to catch it (the matcher), a script running three lines and printing dots (the handler), and a fourth cell where one point forks into two — a solid line going on above, a dashed line cut short below. The fork in that last cell is not the one Chapter 4 drew: there a single call splits into allowed or blocked and the call itself stays the same, here the fork chooses which next step happens, so the route is what moves. The block lands after line 528, before `## 8.3`, costing six lines of prose and pushing that heading to 537; 3 anchors pointing past 528 move by six. Both language files go from 1059 to 1065 lines. Hand-inked drawings 31 to 32, plates inside the prose 5 to 6, plates per edition 165 to 166. 442 builder tests green."
```

Run: `python -X utf8 -m unittest yuyu-book.tests.test_pages -k revision_notes -v` → `OK`

- [ ] **Step 10: 提交**

```bash
git add yuyu-book/illustrations/ch08-hook-line.svg 第二部分-核心系统篇/08-钩子系统-Agent的生命周期扩展点.md en/Part-2-Core-Systems/08-The-Hook-System-Agent-Lifecycle-Extension-Points.md yuyu-book/glosses.json yuyu-book/manifest.json scripts/build_illustration_gallery.py README.md STRUCTURE.md CREDITS.md en/README.md yuyu-book/revisions.json docs/illustration-gallery.html
git diff --numstat -- 第二部分-核心系统篇 en/Part-2-Core-Systems
git commit -m "feat(book): ch08 钩子四拍胶片，第四格把放行与阻断画成分叉"
```
Expected（numstat）：两个 md 各 `6 0`。

---

### Task 7: ch07 四级压缩的轻重次序

7.2 的四级是按「代价」排的：Snip 剪掉、MicroCompact 压紧、Collapse 折起、AutoCompact 整段重写。胶片要让读者一眼看出「越来越重」，第四格还要留出压缩边界那一条虚线。

**Files:**
- Create: `yuyu-book/illustrations/ch07-four-levels.svg`
- Modify: `第二部分-核心系统篇/07-上下文管理-Agent的工作记忆.md`（241 行之后）
- Modify: `en/Part-2-Core-Systems/07-Context-Management-Agent-Working-Memory.md`（241 行之后）
- Modify: `yuyu-book/glosses.json`（3 条）、`yuyu-book/manifest.json`（2 条）
- Modify: `scripts/build_illustration_gallery.py`、`README.md`、`STRUCTURE.md`、`CREDITS.md`（135 与 137 两处）、`en/README.md`、`yuyu-book/revisions.json`

**Interfaces:**
- Consumes: Task 1 的脚本、Task 2 的帧序测试
- Produces: 手写 SVG 33 份、正文图版 7 张、每版 plates 167

- [ ] **Step 1: 画四级**

Create `yuyu-book/illustrations/ch07-four-levels.svg`（`seq`，标准几何；第四格右下方的虚线是压缩边界标记）：

```xml
<svg class="a-squeeze seq" viewBox="0 0 348 106" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><g class="frame"><path d="M8 18q34-3 68 0q3 26 0 52q-34 3-68 0q-3-26 0-52" pathLength="100"/><path d="M18 28h40" pathLength="100"/><path d="M18 36h44" pathLength="100"/><path d="M18 44h36" pathLength="100"/><circle cx="44" cy="64" r="3" pathLength="100"/><circle cx="54" cy="64" r="3" pathLength="100"/><path d="M45 60l8-14" pathLength="100"/><path d="M53 60l-8-14" pathLength="100"/><path d="M60 30h10" opacity=".45" stroke-width="1.2" stroke-dasharray="2 4"/><text class="frame-no" x="11" y="84" fill="currentColor" stroke="none">1</text></g><g class="frame"><path d="M96 18q34-3 68 0q3 26 0 52q-34 3-68 0q-3-26 0-52" pathLength="100"/><path d="M112 24q14-2 28 0q2 14 0 26q-14 2-28 0q-2-14 0-27" pathLength="100"/><path d="M118 32h16" opacity=".6" stroke-width="1.2" pathLength="100"/><path d="M118 40h12" opacity=".6" stroke-width="1.2" pathLength="100"/><path d="M102 38h6" pathLength="100"/><path d="M106 36l3 2-3 2" pathLength="100"/><path d="M150 38h-6" pathLength="100"/><path d="M146 36l-3 2 3 2" pathLength="100"/><path d="M112 60h28" pathLength="100"/><path d="M112 66h20" opacity=".5" stroke-width="1.2" pathLength="100"/><text class="frame-no" x="99" y="84" fill="currentColor" stroke="none">2</text></g><g class="frame"><path d="M184 18q34-3 68 0q3 26 0 52q-34 3-68 0q-3-26 0-52" pathLength="100"/><path d="M192 26q14-2 28 0q2 4 0 8q-14 2-28 0q-2-5 0-9" pathLength="100"/><path d="M192 38q14-2 28 0q2 4 0 8q-14 2-28 0q-2-5 0-9" pathLength="100"/><path d="M192 50q14-2 28 0q2 4 0 8q-14 2-28 0q-2-5 0-9" pathLength="100"/><path d="M224 30l4 3-4 3" pathLength="100"/><path d="M224 42l4 3-4 3" pathLength="100"/><path d="M236 46v10" pathLength="100"/><path d="M233 53l3 4 3-4" pathLength="100"/><text class="frame-no" x="187" y="84" fill="currentColor" stroke="none">3</text></g><g class="frame"><path d="M272 18q34-3 68 0q3 26 0 52q-34 3-68 0q-3-26 0-52" pathLength="100"/><path d="M278 28h18" opacity=".55" stroke-width="1.2" pathLength="100"/><path d="M278 34h16" opacity=".55" stroke-width="1.2" pathLength="100"/><path d="M278 40h18" opacity=".55" stroke-width="1.2" pathLength="100"/><path d="M278 46h14" opacity=".55" stroke-width="1.2" pathLength="100"/><path d="M300 37h8" pathLength="100"/><path d="M306 35l3 2-3 2" pathLength="100"/><path d="M312 34h20" pathLength="100"/><path d="M312 44h16" pathLength="100"/><circle cx="320" cy="56" r="7" pathLength="100"/><circle cx="320" cy="56" r="2" fill="currentColor" stroke="none"/><path d="M276 66h44" opacity=".45" stroke-width="1.2" stroke-dasharray="3 5"/><text class="frame-no" x="275" y="84" fill="currentColor" stroke="none">4</text></g><g opacity=".45" stroke-width="1.3"><path d="M79 44h12" pathLength="100"/><path d="M89 42l3 2-3 2" pathLength="100"/><path d="M167 44h12" pathLength="100"/><path d="M177 42l3 2-3 2" pathLength="100"/><path d="M255 44h12" pathLength="100"/><path d="M265 42l3 2-3 2" pathLength="100"/></g><g opacity=".16" stroke-width="6"><path d="M8 8h332" stroke-dasharray="6 13"/><path d="M8 96h332" stroke-dasharray="6 13"/></g></svg>
```

- [ ] **Step 2: 过闸**

```bash
python -X utf8 -c "import sys;sys.path.insert(0,'yuyu-book');from yuyu_book import art;print(len(art.drawing('ch07-four-levels')),'bytes inlined')"
```
Expected: `3178 bytes inlined`，无异常（2026-11-02 实测：4 帧，装饰组在帧后，第四格那条虚线是压缩边界）。
- [ ] **Step 3: 双语各插六行**（241 行之后；下一行是 `---`）

中文：

```markdown
四级压缩从轻到重：剪掉、压紧、折起、整段重写。

```ill
ch07-four-levels
```

```

英文：

```markdown
The four levels run light to heavy: snip, squeeze, fold, then rewrite the whole span.

```ill
ch07-four-levels
```

```

自查。`---` 原本 242 行、`## 7.3 压缩提示工程` 原本 244 行；六行块占 242～247，于是它们落到 248 与 250 行。画名在第 245 行，即 `L[244]`：

```bash
python -X utf8 -c "
from pathlib import Path
for p in ['第二部分-核心系统篇/07-上下文管理-Agent的工作记忆.md',
          'en/Part-2-Core-Systems/07-Context-Management-Agent-Working-Memory.md']:
    L=Path(p).read_text(encoding='utf-8').splitlines()
    assert L[244]=='ch07-four-levels', (p,245,L[244])
    assert sum(l=='ch07-four-levels' for l in L)==1, p
    assert L[247].strip()=='---', (p,248,L[247])
    assert L[249].startswith('## 7.3'), (p,250,L[249])
    assert len(L)==484, (p,len(L))
print('both files: 478 -> 484 lines, 7.3 opens where it should')
"
```

Expected: `both files: 478 -> 484 lines, 7.3 opens where it should`。英文版那一行是 `## 7.3 Compression Prompt Engineering`，断言只钉 `## 7.3` 前缀。

- [ ] **Step 4: 平移锚点**

```bash
python -X utf8 scripts/shift_anchors.py --after 241 --delta 6 \
  "第二部分-核心系统篇/07-上下文管理-Agent的工作记忆.md" \
  "en/Part-2-Core-Systems/07-Context-Management-Agent-Working-Memory.md"
```
Expected（2026-11-02 实测）：3 行 `glosses.json:`（zh `:472→478`、zh `:352→358`、en `:352→358`）+ 2 行 `manifest.json:`（中英各一条 `:282→288`），末行 `planned: 5 anchors`；补 `--write` 后 `written: 5 anchors`，`git diff --numstat -- yuyu-book/glosses.json yuyu-book/manifest.json` 给出 `3 3` 与 `2 2`。

- [ ] **Step 5: 构建复核**

Run: `python -X utf8 yuyu-book/build.py --check`
Expected: 两份日志各报 `20 units, 167 plates`，末行 `CHECK OK`。

- [ ] **Step 6: 挂进画廊**

`scripts/build_illustration_gallery.py`：
- `ORDER` 里把 `"ch07-four-levels"` 插到 `"ch07"` 之后；
- `WIDE` 加条目 `"ch07-four-levels": 330`；
- `PLAIN` 加 `"ch07-four-levels": "四格胶片：剪一刀、压一压、折三层、整段重写",`；
- `PLAIN_EN` 加
```python
    "ch07-four-levels": "A filmstrip: snip a tail, squeeze, fold in "
                        "three, rewrite the whole span",
```

Run: `python -X utf8 scripts/build_illustration_gallery.py`
Expected: `…\illustration-gallery.html (N bytes, 33 figures)`

- [ ] **Step 7: 五处图数声明 +1**

- `README.md:113`：`全书另有 32 份手写线描图` → `全书另有 33 份手写线描图`；括号里 `四道权限门与一声钩响）` → `四道权限门、一声钩响与四级压缩）`。
- `STRUCTURE.md:109`：`| 32 份手写 SVG` → `| 33 份手写 SVG`；`+ 6 幅正文插图` → `+ 7 幅正文插图`。
- `CREDITS.md:135`：`扉页一幅车图（共 32 份` → `扉页一幅车图（共 33 份`。
- `CREDITS.md:137`：`**画风体系**：32 份插图` → `**画风体系**：33 份插图`。
- `en/README.md:113`：`32 hand-drawn line illustrations` → `33 hand-drawn line illustrations`；`six plates inside the prose (a tool bench, a scheduling filmstrip, a heartbeat loop, a five-column portico, four permission gates and a hook line)` → `seven plates inside the prose (a tool bench, a scheduling filmstrip, a heartbeat loop, a five-column portico, four permission gates, a hook line and four levels of compaction)`。

Run: `python -X utf8 -m unittest yuyu-book.tests.test_docclaims -v` → `OK`

- [ ] **Step 8: 五道闸全跑**

```bash
python -X utf8 yuyu-book/build.py --check
python -X utf8 yuyu-book/build.py --check --mermaid=source
python -X utf8 -m unittest discover -s yuyu-book/tests   # Ran 442 tests, OK
python -X utf8 -m unittest discover -s tests             # Ran 34 tests, OK
python -X utf8 scripts/check_book.py                     # 0 errors（Markdown 文件数随计划文档变动，不作断言）
npm run check:diagrams                                   # 320 Mermaid diagrams, 0 errors
```

- [ ] **Step 9: 账本记一轮**

`entries[0]["zh"]` 末尾追加：

```
"7.2 把压缩排成四级，读起来最难的是「到底差在哪」。四格按代价从轻到重：第一格三行字还在，一把剪刀只剪掉尾巴，剪口用短虚线标出；第二格整段被压紧，两侧各一支箭头往里收，字数没减多少、行距先塌了；第三格折成三层，每层只剩一道檐口和一支向下的箭头，内容收进纸里；第四格最重，左边四行淡掉的旧字、右边两行新写的实线，中间一支粗箭头，右下角一条短虚线标出压缩边界：旧对话断在这里，新会话从它下面重新起步。前三格讲的都还是同一篇对话（剪完还在、压完还在、折起来也还在），第四格已经把内容换成新写的两行——四级之间真正的差不是少写几行，而是换一次记忆。落点在 241 行之后、`## 7.3` 之前，图版占六行，`## 7.3` 落到 250 行，注册表里 5 条指向 241 行之后的锚点各加六。中英各 478 行变 484 行。手写图 32→33 份，正文插图 6→7 张，每版图版 166→167 张。这一批铺完，20 个正文单元里仍只有 6 个带画（01、02、03、04、07、08），剩下的 14 面白墙记进下一轮。构建器测试 442 项全绿。"
```

`entries[0]["en"]` 末尾追加：

```
"Section 7.2 ranks compaction in four levels; what a reader cannot get from the prose is how the cost differs. The four cells go light to heavy: in the first, three lines still stand and a pair of scissors takes off only the tail, the cut marked by a short dash; in the second the whole span is squeezed, an arrow pushing in from each side, the text barely shorter but its leading collapsed; in the third it folds into three layers, each left with nothing but a eave and a downward arrow, the content tucked inside the paper; the fourth is the heaviest — four faded lines on the left, two freshly inked ones on the right, a thick arrow between them, and a short dashed line under them marking the compaction boundary, where the old conversation snaps and a new session starts below. The first three cells are still the same conversation, cut, squeezed and folded; the fourth has already swapped its content for two new lines, and that is the real difference between the levels: not fewer lines written, but a different memory. The block lands after line 241, before `## 7.3`, costing six lines of prose and pushing that heading to 250; 5 anchors pointing past 241 move by six. Both language files go from 478 to 484 lines. Hand-inked drawings 32 to 33, plates inside the prose 6 to 7, plates per edition 166 to 167. Six of the twenty prose units now carry a drawing; the other fourteen are the next round's debt. 442 builder tests green."
```

两则都必须成对用反引号：这一页不允许任何裸反引号落到渲染结果里（`test_pages.test_revision_notes_are_typeset_not_left_in_markdown`）。

Run: `python -X utf8 -m unittest yuyu-book.tests.test_pages -k revision_notes -v` → `OK`

- [ ] **Step 10: 提交**

```bash
git add yuyu-book/illustrations/ch07-four-levels.svg 第二部分-核心系统篇/07-上下文管理-Agent的工作记忆.md en/Part-2-Core-Systems/07-Context-Management-Agent-Working-Memory.md yuyu-book/glosses.json yuyu-book/manifest.json scripts/build_illustration_gallery.py README.md STRUCTURE.md CREDITS.md en/README.md yuyu-book/revisions.json docs/illustration-gallery.html
git diff --numstat -- 第二部分-核心系统篇 en/Part-2-Core-Systems
git commit -m "feat(book): ch07 四级压缩胶片，把代价的轻重排成一列"
```
Expected（numstat）：两个 md 各 `6 0`。

---

### Task 8: 全站派生产物与肉眼验收

前五步的绿是脚本的绿。这一轮的产物第一次让读者在同一页里看到 6 张正文图，所以要在浏览器里把「屏幕、暗色、纸面」三张脸都看过一遍才算完。

**Files:**
- Regenerate: `docs/illustration-gallery.html`、`docs/beginner-reader.html`、`docs/beginner-reader.en.html`、`docs/portal.html`（门户）
- Modify: `docs/superpowers/specs/2026-11-01-yuyu-illustration-expansion.md`（§4 表格勾掉已落地行，状态改成「正文手绘与连续动图已铺开 5 张，实物位图待做」）

**Interfaces:**
- Consumes: Task 3–7 的全部产物
- Produces: 无代码接口；一份「看过什么」的记录进账本

- [ ] **Step 1: 重生成三个派生产物**

```bash
python -X utf8 scripts/build_illustration_gallery.py   # 33 figures
python -X utf8 scripts/build_beginner_reader.py
python -X utf8 scripts/build_site_portal.py
```
Expected: 各自打印一行输出文件与体积，无 SystemExit。（三个产物的插图数都不必手改：`scripts/build_beginner_reader.py:20` 的 `PLATES = len(list(ART.glob("*.svg")))` 当场数磁盘，门户 `docs/portal.html` 与两份入门读本都从这一个常量取值。）

- [ ] **Step 2: 构建两份 HTML**

```bash
python -X utf8 yuyu-book/build.py            # 不加 --check，真产物
```
Expected: 两份 `dist/*.html`，日志里 `167 plates`。

- [ ] **Step 3: 浏览器逐格看**

用 chrome-devtools 打开 `yuyu-book/dist/yuyu-agent-harness-zh.html`，对五个新落点各做四件事，并记进账本：

1. 滚动到该图，确认 `.illu-seq` 的四格是**逐格显影**而不是同时亮起；
2. 悬停，确认走马灯一样**从左到右**循环（帧序错了就是装饰组插到了前面，Task 2 的测试应当已经红过）；
3. 切暗色（`prefers-color-scheme: dark`），确认 `currentColor` 自动换墨，无一块留在纸色上；
4. 打印预览（`Ctrl+P`）或 `@media print` 模拟，确认四格**全部画完且并排可读**——这一条就是设计稿决策 2 的兑现证明。

另外确认 `ch01-five-pillars` 是 `illu-line`：只有描线、没有循环提示（`悬停播放` 那行字只属于 seq）。

- [ ] **Step 4: 画廊对照**

打开 `docs/illustration-gallery.html`，确认 33 张卡片都在、五张新图的双语题注显示正常、点击能重播。（画廊的守卫保证少登记一张就直接红，所以这一步主要是看题注通不通顺。）

- [ ] **Step 5: 五道闸再跑一遍 + 变异自检**

```bash
python -X utf8 yuyu-book/build.py --check
python -X utf8 yuyu-book/build.py --check --mermaid=source
python -X utf8 -m unittest discover -s yuyu-book/tests    # 442
python -X utf8 -m unittest discover -s tests             # 34
python -X utf8 scripts/check_book.py                     # 0 errors
npm run check:diagrams                                   # 320 / 0
```
变异自检（证明测试真的在管）：把 `ch04-gate-steps.svg` 第三个帧组之后插入一个 `<g class="frame">`（凑成 5 帧但 CSS 只排到 6），重跑 `FilmstripSource` 应仍绿；再把装饰组挪到帧组之前，必须红。撤掉变异。

- [ ] **Step 6: 更新设计稿状态并提交**

```bash
git add docs/illustration-gallery.html docs/beginner-reader.html docs/beginner-reader.en.html docs/portal.html docs/superpowers/specs/2026-11-01-yuyu-illustration-expansion.md yuyu-book/revisions.json
git commit -m "docs(book): 重生成画廊与门户，插图扩容设计稿记下已落地的五张"
```

## 下一轮（不在本计划范围内，先记账）

1. **剩余 14 个单元正文仍无画**（20 个单元里，ch03 已有 2 张，本轮补 ch01/ch02/ch04/ch07/ch08，凑成 6 个带画的单元）。ch12 与 ch13 是最先该补的两块白墙。
2. **文字迭代仍按一个脚本口径**：`python scripts/measure_translationese.py`。2026-11-02 实测基线 `zh 132 行 / 162 处 / 术语式样 15`、`en 554 行 / 801 处 / 系词 54`；最集中的是 zh ch12 14 行、ch07 13 行、ch13 11 行，en ch12 51 行、ch02 50 行、ch03 42 行、ch11 40 行。具体目标之一：`en/Part-1-Foundations/03-The-Tool-System-Agent-Hands.md:289-292` 那条并发编号列表仍是被动语态。
3. **实物位图（扉页 + 4 幅篇题刻）**要另立设计稿与计划：`render.inline_images` 与 `art.photo()` 通道已存在（`.illu-photo` 样式也已就位），缺的是有来源有许可的图，以及扉页／题刻接受位图的那一个槽位。
4. README 的 PDF 页数声明（zh 483／en 514 一类）只能引 CI 的 Noto CJK 实测值，不许从本机 Edge 的 `--pdf` 结果回抄。
