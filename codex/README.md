# Codex CLI：执行边界与工程实践

状态：已立项，当前为提纲与源码研究阶段。整书 HTML、PDF 和 EPUB 尚未生成。

研究重点：Rust 运行时、审批、沙箱和可恢复执行。基线：rust-v0.167.0，提交 `086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a`。[上游固定版本](https://github.com/openai/codex/tree/086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a)，许可证 Apache-2.0，访问日期 2026-11-09。

[逐章提纲](outline.md) · [统一任务表](../docs/agent-series/tasks.json) · [来源锁文件](../docs/agent-series/sources.lock.json)

按中文分册推进，英文版尚未启动。完成正文后将复用公共构建器，生成独立的 `yuyu-codex-zh.html/.pdf/.epub`，最终放到主工作区 `yuyu-book/dist/`。

首轮源码入口：

- [codex-rs/cli](https://github.com/openai/codex/tree/086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a/codex-rs/cli)
- [codex-rs/core](https://github.com/openai/codex/tree/086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a/codex-rs/core)
- [codex-rs/exec](https://github.com/openai/codex/tree/086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a/codex-rs/exec)
- [codex-rs/app-server](https://github.com/openai/codex/tree/086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a/codex-rs/app-server)
- [codex-rs/sandboxing](https://github.com/openai/codex/tree/086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a/codex-rs/sandboxing)
- [codex-rs/linux-sandbox](https://github.com/openai/codex/tree/086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a/codex-rs/linux-sandbox)
- [codex-rs/windows-sandbox-rs](https://github.com/openai/codex/tree/086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a/codex-rs/windows-sandbox-rs)
