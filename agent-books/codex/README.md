# Codex CLI：执行边界与工程实践

中文 0.2.2 阅读修订版包含前言、18 章和附录 A–D，约 5.2 万汉字。用一份运费边界错误串起 AGENTS.md、技能/插件、规则、exec、失败恢复与交付；第 12 章详细解释十四个 Hook 事件、匹配、输入输出、并发与信任。

研究重点：Rust 运行时、审批、沙箱和可恢复执行。基线：rust-v0.167.0，提交 `086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a`。[上游固定版本](https://github.com/openai/codex/tree/086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a)，许可证 Apache-2.0，访问日期 2026-11-09。

[逐章目录](outline.md) · [统一任务表](../docs/agent-series/tasks.json) · [来源锁文件](../docs/agent-series/sources.lock.json) · [实验与范围](VERIFY.md)

按中文分册推进，英文版尚未启动。复用公共构建器，独立产物名为 `yuyu-codex-zh.html/.pdf/.epub`，最终放到主工作区 `yuyu-book/dist/`。

从[前言](00-前言.md)开始；插件重点见[第 12 章](ch12.md)，真实规则实验见[第 10 章](ch10.md)，自动化与客户端见[第 14 章](ch14.md)和[第 15 章](ch15.md)。[原创示例](examples/README.md)可独立运行。

跟做入口：[运费模板](examples/workshop/AGENTS.md)、[插件包](examples/plugin-example/README.md)、[离线练习驱动](examples/check_workshop.py)、[静态协议校验](examples/check_protocol.py)。八项固定 CLI 检查、十三项原创离线检查和十一项 schema 检查分别记录，不把它们写成模型或插件宿主实跑。

首轮源码入口：

- [codex-rs/cli](https://github.com/openai/codex/tree/086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a/codex-rs/cli)
- [codex-rs/core](https://github.com/openai/codex/tree/086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a/codex-rs/core)
- [codex-rs/exec](https://github.com/openai/codex/tree/086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a/codex-rs/exec)
- [codex-rs/app-server](https://github.com/openai/codex/tree/086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a/codex-rs/app-server)
- [codex-rs/sandboxing](https://github.com/openai/codex/tree/086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a/codex-rs/sandboxing)
- [codex-rs/linux-sandbox](https://github.com/openai/codex/tree/086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a/codex-rs/linux-sandbox)
- [codex-rs/windows-sandbox-rs](https://github.com/openai/codex/tree/086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a/codex-rs/windows-sandbox-rs)

本地 0.2.2 已生成 HTML、PDF（146 页）和 EPUB。本轮补清练习入口、工作目录和跨章衔接，索引改为术语与章节引用分行显示。[当前成品记录](../docs/agent-series/local-publication-20261110-reader-path.json)。
