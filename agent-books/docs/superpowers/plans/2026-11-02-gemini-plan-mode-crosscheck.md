# 实施计划：gh-gemini-cli 对照面补落第 14 章

日期：2026-11-02。设计稿：`docs/superpowers/specs/2026-11-02-gemini-plan-mode-crosscheck.md`。

## 基线（2026-11-02 实测）

- `第四部分-工程实践篇/14-Plan模式与结构化工作流.md` 825 行；`en/Part-4-Engineering-Practice/14-Plan-Mode-and-Structured-Workflows.md` 826 行（既有 1 行漂移，容忍不动）。
- 两版 §14.1.1 的 omp 对照段均在 **L34**，L36 为身份引语框，L38 为 `### 14.1.2`。落点：L34 后插空行 + 对照段（各 +2 行）。
- 锚点 dry-run：`--after 34 --delta 2` 双语各 **5 条**（zh/en manifest 426→428、665→667 / 427→429、666→668 等，含 glosses）。
- 登记现值：`gh-gemini-cli` tag v0.65.0，commit `6006c14a4decfe4b891c6263ad6ad5992e404b5b`，accessed/snapshot 2026-10-26。
- 目标钉：**v0.66.0**，commit `970413207732f5d4d8c50540c7fc359c44fdaaf2`（轻量 tag，`git/commits/<sha>` 实取）。

## Task 1：设计稿 + 本计划入库

`docs/superpowers/specs/2026-11-02-gemini-plan-mode-crosscheck.md` + 本文件，一笔提交：`docs(book): gemini-cli 对照面补落的设计稿与实施计划`。

## Task 2：正文双语落段 + 锚点平移

- [x] 1. zh ch14 L34 后插对照段（无锚版内容见设计稿决定 1 的角度，旗标名照抄 v0.66.0 文档：`--approval-mode=plan`、`Shift+Tab`、`/plan`、`enter_plan_mode`）；en 同位同义。
- [x] 2. 身份引语框（zh/en L36，插行后 L38）：「oh-my-pi」→「oh-my-pi 与 Gemini CLI」/「oh-my-pi and Gemini CLI」。
- [x] 3. `scripts/shift_anchors.py --after 34 --delta 2` 先双版 dry-run 核对 5 条集合，再 `--write`。
- [x] 4. 验证：`grep -ci gemini` 双版 ch14 ≥1；`python yuyu-book/build.py --check` OK。

## Task 3：登记重钉 + CREDITS

- [x] 1. `yuyu-book/sources.json` `gh-gemini-cli`：pinned.tag→v0.66.0、commit→`970413207732f5d4d8c50540c7fc359c44fdaaf2`、accessed/snapshot→2026-11-02、scope 重写（zh ≤180 字符、en ≤400）。
- [x] 2. `CREDITS.md`：`gh-gemini-cli` 表行 tag/commit/日期/描述同步；§三叙事补 2026-11-02 记一句。
- [x] 3. 验证：`python -m json.tool yuyu-book/sources.json`；docclaims 相关测试。

## Task 4：五道闸 + 账本 + 提交

- [x] 1. 五道闸：`build.py --check`（含 `--mermaid=source` 一轮）、unittest 442+35、`check_book.py`（94 files/320/0）、`npm run check:diagrams`（320/0）。
- [x] 2. 账本 `revisions.json` entries[0] 中英各加第 53 条，**末句带 `构建器测试 442 项全绿` / `442 builder tests green`**；LF、无孤反引号、无 `@@`。
- [x] 3. 提交：`feat(book): gemini-cli 对照面落进第 14 章，登记重钉 v0.66.0`。
- [x] 4. 计划勾打满，`docs(book): gemini 对照面计划的勾打上`。

## Task 5：发布链

推送分支（origin fork；`env -u GITHUB_TOKEN gh`）→ PR → 等 ~20s → `pr checks --watch` 双绿 → merge → main 三工作流绿 → `build.py --lang both --pdf` 本地重建（README 的 CI 槽位数字不动，Windows 对照句位按新本机 PDF 刷新）。

## 验收

PR 双 check 绿；merge 后 main 三工作流绿；本地 PDF 更新；grep 双版 ch14 均见 Gemini 且引语框点名两家；账本 53+53 条。
