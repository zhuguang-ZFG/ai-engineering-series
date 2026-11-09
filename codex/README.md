# Codex CLI：执行边界与工程实践

状态：完整中文初稿已写，包含前言、18 章和附录 A–D，约 2.9 万中文汉字。已完成固定 Windows CLI 的八项无模型检查。HTML、PDF、EPUB 由统一构建主线生成，产物状态见交付记录。

研究重点：Rust 运行时、审批、沙箱和可恢复执行。基线：rust-v0.167.0，提交 `086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a`。[上游固定版本](https://github.com/openai/codex/tree/086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a)，许可证 Apache-2.0，访问日期 2026-11-09。

[逐章目录](outline.md) · [统一任务表](../docs/agent-series/tasks.json) · [来源锁文件](../docs/agent-series/sources.lock.json) · [实验与范围](VERIFY.md)

按中文分册推进，英文版尚未启动。复用公共构建器，独立产物名为 `yuyu-codex-zh.html/.pdf/.epub`，最终放到主工作区 `yuyu-book/dist/`。

从[前言](00-前言.md)开始；插件重点见[第 12 章](ch12.md)，真实规则实验见[第 10 章](ch10.md)，自动化与客户端见[第 14 章](ch14.md)和[第 15 章](ch15.md)。[原创示例](examples/README.md)可独立运行。

首轮源码入口：

- [codex-rs/cli](https://github.com/openai/codex/tree/086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a/codex-rs/cli)
- [codex-rs/core](https://github.com/openai/codex/tree/086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a/codex-rs/core)
- [codex-rs/exec](https://github.com/openai/codex/tree/086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a/codex-rs/exec)
- [codex-rs/app-server](https://github.com/openai/codex/tree/086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a/codex-rs/app-server)
- [codex-rs/sandboxing](https://github.com/openai/codex/tree/086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a/codex-rs/sandboxing)
- [codex-rs/linux-sandbox](https://github.com/openai/codex/tree/086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a/codex-rs/linux-sandbox)
- [codex-rs/windows-sandbox-rs](https://github.com/openai/codex/tree/086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a/codex-rs/windows-sandbox-rs)


2026-11-10 已完成三种格式的本地构建与交付，见[成品记录](../docs/agent-series/local-publication-20261110.json)。
