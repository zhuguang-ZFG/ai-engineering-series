# 卷十一 / 卷十二 第一部：交付记录

## 新增内容（`ai-engineering-series/agent-books`，未提交）

| 项 | Grok Build | Cursor CLI |
| --- | --- | --- |
| 卷 | 十一 | 十二 |
| 前言 + 第一部 | 前言、ch01–05、附录 A–D | 前言、ch01–05、附录 A–D |
| 示例 | `grok/examples/`：故障/修复版闸门 + 用例脚本 + 3 条单测（实测 3 绿） | 无（闭源，写作机未装 CLI） |
| 构建 | `yuyu-grok-zh.html` 0.3 MB | `yuyu-cursor-zh.html` 0.2 MB |

章节按子代理初稿 + 本人逐条核事实修订。核出并修正 4 处：

1. ch03（Cursor 会话）：`/pin`、`/archive` 在官方斜杠命令参考中不存在 → 改为 `/rename`、`/fork`、`/summarize`，来源改指 slash-commands 参考页。
2. ch04（Cursor 规则）：「无 frontmatter 的 .mdc 被忽略」不准确 → 按文档改为「纯 `.md` 因无 frontmatter 被忽略；`.mdc` 三字段全空时仅 `@` 提及才包含」，并补第四种组合。
3. ch05（Cursor 审批）：文档实际写明 `unrestricted` 在打印模式下与 `--force` 等价 → 表格与边界节同步更正。
4. 公开提交与内部 SOURCE_REV 混用：`559751…` 是内部单仓 SHA，GitHub 树链接 404；全部改为公开提交 `2bdd1d6a…`，`source_rev` 单列。
5. grok 前言/附录：优先级表「被谁压住」列错位 → 改为「谁在它之上」并补合并顺序句；安装命令与 README 逐字对齐。

## 注册与门禁

- `scripts/bookctl.py`：`AGENT_PRODUCTS` 增 `grok`、`cursor`（前缀 `yuyu-grok`/`yuyu-cursor`，zh-only）。
- `yuyu_book/registry.py`：FILES 按产品展开；两卷 `subject_index_registry` 为 null，故 FILES 不含 subject-index（修复了首跑 `subject-index-grok.json` 缺失的测试错误）。
- 6 份注册表 ×2（manifest/sources/glosses/notes/reading-paths/revisions）；glosses 走 `extra`+`mark:false`，2 个 core 词条带 why；`docs/agent-series/sources.lock.json` 增 grok 仓锁定（公开提交 2bdd1d6a，树内 SOURCE_REV 559751fd 另存为 source_rev）与 6 条官方文档记录。
- 两卷 README + 主 README「Agent 专题分册」新增段落（注明「第一部已成稿，未并入 series.json/合订本」）。

## 验证

- `check --fast`：8 步全过，575 测试 OK（修复 registry 缺件后复跑）。
- `build --product grok|cursor --lang zh`：均 OK；正文风格探针：对比句 0、破折号 0（前言 1 处已改冒号）、半角标点仅代码字面量。
- 新增 Python 全部过 ruff；agent-books 存量 47 处 lint 错误在未动文件中（含 bookctl 的 `json` F401，stash 验证为先于本次改动存在）。

## 未完成 / 边界

- 两卷第 2–4 部（Grok 20 章 / Cursor 18 章）未写；`series.json`、`scripts/collected.py`（ORDER/CN_NUMBERS 扩「十一/十二」）未动——待成书并产出 PDF 后再并入，否则合订本会因缺 PDF 直接失败。
- Grok 侧：`grok` 程序未安装，`--version`、TUI、`/rewind` 实际行为、检查点回滚入口均按文档/源码静态阅读标注，附录 C 逐条列明。
- Cursor 侧：安装脚本、`--help` 真实参数、审批拒绝退出码、三类规则冲突优先级均标注「需实测」。
- `task_verify` 仍为 `unverified`（无运维基线），不声称通过。
