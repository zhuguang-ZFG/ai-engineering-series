# Agent 专题分册

跨项目的内容分工与选读路线见[大模型与智能体工程系列](series/README.md)；新增[提示词工程分册](../prompt/README.md)已完成十八章中文技术试读版，离线练习和本地出版检查见[验证记录](../prompt/VERIFY.md)。

[任务表](agent-series/tasks.json) · [规格](superpowers/specs/2026-11-09-agent-ecosystem-volume.md) · [计划](superpowers/plans/2026-11-09-agent-ecosystem-volume.md)

每册均含前言、18 章和附录 A–D。它们共用电子书构建器，各自维护版本、来源、目录、阅读路径和索引。当前交付中文版，英文版尚未启动。原四册的任务记录见上方链接；新增 Kimi Code 的[规格](superpowers/specs/2026-11-10-kimi-code-volume.md)与[计划](superpowers/plans/2026-11-10-kimi-code-volume.md)单独维护。

| 分册 | 固定版本 | 内容重点 | 实验记录 |
| --- | --- | --- | --- |
| [OpenCode](../opencode/README.md) | v1.19.5 | 请求链、工具与权限、Hook、加载和缓存 | [Windows V1 宿主、10 个权限场景](../opencode/VERIFY.md) |
| [DeepSeek Harness](../deepseek/README.md) | fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159 | Cordis 注入与卸载、循环、工具和事件 | [20 个真实组件场景](../deepseek/VERIFY.md) |
| [Hermes Agent](../hermes/README.md) | v0.23.0 | 记忆快照、会话、技能、插件、cron 和 gateway | [隔离的记忆与会话实验](../hermes/VERIFY.md) |
| [Codex CLI](../codex/README.md) | rust-v0.167.0 | CLI/exec/app-server、规则、沙箱、skills 和 hooks | [固定 CLI 的规则与 schema 实验](../codex/VERIFY.md) |
| [Kimi Code](../kimi/README.md) | @moonshot-ai/kimi-code@2.5.2 | Skill、Agent、插件、Hook、MCP 与 ACP | [上游组件与真实 CLI 握手](../kimi/VERIFY.md) |

完整 commit、许可证和源码入口见 [sources.lock.json](agent-series/sources.lock.json)。Hermes、Codex 的 annotated tag 已解析到实际提交。官方滚动文档用于解释概念，具体版本行为以固定源码和对应实验为准。

在仓库根目录运行：

```bash
python scripts/bookctl.py build --product opencode --lang zh --pdf --epub
python scripts/bookctl.py build --product deepseek --lang zh --pdf --epub
python scripts/bookctl.py build --product hermes --lang zh --pdf --epub
python scripts/bookctl.py build --product codex --lang zh --pdf --epub
python scripts/bookctl.py build --product kimi --lang zh --pdf --epub
```

有 make 时也可使用 `make book-agents`。产物前缀分别是 `yuyu-opencode-zh`、`yuyu-deepseek-zh`、`yuyu-hermes-zh`、`yuyu-codex-zh`，输出到 `yuyu-book/dist/`。本机交付目录为 `D:\Users\claude\claude-code-book-main\yuyu-book\dist`。

实验没有调用外部付费模型。OpenCode 使用本地 SSE 替身驱动真实宿主；其余册的组件或 CLI 实验也保留明确边界。尚未实跑的模型效果、网络服务和跨平台行为列在各册验证记录中。旧 P6 视频媒体验收仍未完成。


## 当前版本

四册均已扩写连续工程案例和插件机制，使用各自的架构封面与章节配色。本轮补清首次练习、目录切换和跨章实例，并改善索引排版。当前 PDF 为 OpenCode 148 页、DeepSeek 129 页、Hermes 130 页、Codex CLI 146 页；EPUB 与 HTML 同步生成，见[当前交付记录](agent-series/local-publication-20261110-reader-path.json)。

新增 Kimi Code 分册为 84 页，含完整库存审查插件与独立靛蓝封面，提供 HTML、PDF、EPUB 及学习材料包。版本依据、实测范围和出版检查集中在 [Kimi 验证记录](../kimi/VERIFY.md)。

OpenCode 包含 19 项金额计算案例；DeepSeek 连续插件新增 13 项真实 Cordis 场景；Hermes 补足 Aurora 八步流程及记忆写入失败实验；Codex 增加 Hook、JSONL 与协议 schema 的离线练习。它们分别说明原创程序、真实组件和完整宿主的运行范围，不能互相替代。
