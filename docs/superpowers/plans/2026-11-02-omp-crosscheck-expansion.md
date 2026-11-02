# omp 对照面扩容实施计划（第 7、14 章落字 + 登记重钉）

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 field-guide 草稿里 oh-my-pi 的两组能力按对照面身份落进第 7 章 §7.5 与第 14 章 §14.1.1（双语），第 4 章 §4.3.6 条目版本号跟登记一起换到 18.15.0，登记重钉 tag `v18.15.0`。

**Architecture:** 纯正文轮次，无插图、无构建器改动。两处新增块各为「空行 + 小节题／正文段 + 空行 + 引语框」结构，ch04 §4.3.6 同款；双语插入点同行号，`glosses.json`／`manifest.json` 锚点用 `scripts/shift_anchors.py` 平移后由 `build.py --check` 复核。

**Tech Stack:** Markdown 双语正文、`sources.json`／`CREDITS.md` 登记、Python 3.13 标准库脚本。

**Spec:** `docs/superpowers/specs/2026-11-02-omp-crosscheck-expansion.md`

## Global Constraints

- 对照面身份：新增文字不支撑本章任何技术论断，每处带「对照面的身份」引语框（与 ch04 §4.3.6 同款）。
- 全部 omp 断言以本机 `omp/18.15.0` 的 `--help` 重验为据，登记钉 tag `v18.15.0` + commit `3fedf8d53267e32a6d7521ce725fdcc4a36fdc67`。
- 双语同步：两处新增块中英行数一致，插入点两侧同行号；中文全角标点、中英之间半角空格；行内反引号成对。
- 账本注释（`revisions.json`）不许落单反引号、不许夹原始 `@@` 串；文件保持 LF。
- 不动插图、不动 guides、不动 manifest 单元结构；派生四页（画廊／双读本／门户）本轮无磁盘 SVG 变化，不重切。
- 凡写进 commit message 与账本的数字必须能当场重测。
- 五道闸全绿才算做完；不推送 `origin`，除非用户当次明确同意；`upstream` 永不推送。

**五道闸（本机无 make，逐条手跑）：**

```bash
python -X utf8 yuyu-book/build.py --check
python -X utf8 yuyu-book/build.py --check --mermaid=source
python -X utf8 -m unittest discover -s yuyu-book/tests
python -X utf8 -m unittest discover -s tests
python -X utf8 scripts/check_book.py
npm run check:diagrams
```

**当前基线（2026-11-02，HEAD `efaafd8` 实测）：**

| 口径 | 当前值 |
| --- | --- |
| 单元 | 20 |
| 手写 SVG／正文图版 | 磁盘 167 份；HTML 内联 167 plates（中英同） |
| 锚点 | `glosses.json` 408 条、`manifest.json` 158 条 |
| sources.json | 34 条（`gh-oh-my-pi` 钉 v18.14.2） |
| 三处落点行号 | ch07 zh/en 表格尾 L420；ch14 zh/en 表格尾 L32；ch04 omp 条目 zh/en L341 |

## Task 1：设计稿与计划入库

- [ ] Step 1：提交 spec + plan 两份文档（本计划与
  `docs/superpowers/specs/2026-11-02-omp-crosscheck-expansion.md`）。

```bash
git add docs/superpowers/specs/2026-11-02-omp-crosscheck-expansion.md docs/superpowers/plans/2026-11-02-omp-crosscheck-expansion.md
git commit -m "docs(book): omp 对照面扩容的设计稿与实施计划"
```

## Task 2：正文双语落字 + 锚点平移

- [ ] Step 1：ch07 zh 在 L420（表格行）后插 6 行对照小节；en 同位置插同 6 行。
- [ ] Step 2：ch14 zh 在 L32 后插 4 行对照段 + 引语框；en 同位置插同 4 行。
- [ ] Step 3：ch04 zh/en L341 的「oh-my-pi 18.14.2」→「oh-my-pi 18.15.0」（en 同）。
- [ ] Step 4：锚点平移并复核计划（先 dry-run 再 `--write`）：

```bash
python -X utf8 scripts/shift_anchors.py 第二部分-核心系统篇/07-上下文管理-Agent的工作记忆.md en/Part-2-Core-Systems/07-Context-Management-Agent-Working-Memory.md --after 420 --delta 6
python -X utf8 scripts/shift_anchors.py 第四部分-工程实践篇/14-Plan模式与结构化工作流.md en/Part-4-Engineering-Practice/14-Plan-Mode-and-Structured-Workflows.md --after 32 --delta 4
```

- [ ] Step 5：核对双语行数增量一致（ch07 两版 484→490，ch14 两版 821/822→825/826）。

## Task 3：登记重钉 + 草稿注记

- [ ] Step 1：`sources.json` 的 `gh-oh-my-pi`：tag `v18.15.0`、commit `3fedf8d53267e32a6d7521ce725fdcc4a36fdc67`、`snapshot`／`accessed` 改 2026-11-02、`scope` 扩为三章对照面（zh ≤180 字、en ≤300 字符上限内）。
- [ ] Step 2：`CREDITS.md` §三 `gh-oh-my-pi` 行同步 tag/commit/描述。
- [ ] Step 3：field-guide 草稿头部追加执行注记（哪两组能力、哪两章、何时、重验口径）。

## Task 4：闸门 + 账本 + 提交

- [ ] Step 1：五道闸全绿（预期：build --check 双版 CHECK OK 167 plates；unittest 442+35；check_book 92 files/0 errors；diagrams 320/0）。
- [ ] Step 2：`revisions.json` entries[0] 双语各补一条账本（无反引号、无 `@@`），跑
  `python -X utf8 -m unittest yuyu-book.tests.test_pages -k revision_notes` 复核。
- [ ] Step 3：提交正文与登记：

```bash
git add -A
git commit -m "feat(book): oh-my-pi 对照面落进第 7、14 章，登记重钉 v18.15.0"
```

- [ ] Step 4：勾掉本计划全部勾，单独提交：

```bash
sed -i '3,$s/^- \[ \]/- [x]/' docs/superpowers/plans/2026-11-02-omp-crosscheck-expansion.md
git add docs/superpowers/plans/2026-11-02-omp-crosscheck-expansion.md
git commit -m "docs(book): omp 对照面计划的勾打上"
```

- [ ] Step 5：提交后窄复核：`check_book.py` 仍 0 errors；`git status` 干净。
