# DeepSeek Harness：插件化运行时

中文正文已齐：前言、18 章、附录 A–D，共约 4.8 万汉字，配有 14 张机制图。内容从配置入口、Cordis 依赖与清理，延伸到 Agent 循环、工具管线、会话恢复和插件交付。

源码基线：提交 `fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159`，根包 `0.2.2-rc.1`，vendored Cordis `4.1.0`。[上游固定版本](https://github.com/deepseek-ai/deepseek-harness/tree/fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159)，许可证 MIT，访问日期 2026-11-10。

[从前言开始](00-前言.md) · [完整目录](outline.md) · [实验说明](VERIFY.md) · [可复现实例](examples/README.md) · [来源锁文件](../docs/agent-series/sources.lock.json)

本地已经直接运行固定 Cordis 源码上的二十项组件场景：七项基础实验、十三项连续审查实例。后者贯穿双服务依赖、工具注册、策略、任务取消、延迟清理与提供者替换，并从实际 tarball 解包入口重跑通过。完整 dsh 宿主、外部模型、持久化恢复和平台沙箱尚未实跑；书中保留这一区别。

中文分册的独立构建配置已接入公共构建器，输出名称为 `yuyu-deepseek-zh.html/.pdf/.epub`。最终成品统一放到主工作区 `yuyu-book/dist/`；构建结果见下方交付记录。英文版尚未启动。

源码入口：

- [packages/core](https://github.com/deepseek-ai/deepseek-harness/tree/fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159/packages/core)
- [docs/architecture.md](https://github.com/deepseek-ai/deepseek-harness/tree/fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159/docs/architecture.md)

本地 1.1.1 已生成 HTML、PDF（125 页）和 EPUB，保留 14 张机制图。本次修订整理重复解释、改写报告式语气，并调整章节导读；示例代码、图示和来源保持原样。[当前文件与校验值](../docs/agent-series/local-publication-20261110-reading.json)。
