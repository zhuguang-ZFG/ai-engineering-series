# Hermes Agent：记忆、技能与持续任务

中文初稿已写齐：前言、18 章、附录 A–D。正文从独立配置与 Agent 循环讲起，重点解释记忆快照、技能修订、历史检索、插件注册与卸载，后半册讨论定时任务、网关、隔离和长期项目。

[完整目录](outline.md) · [本地验证](VERIFY.md) · [可运行示例](examples/README.md)

基线是 [Hermes v0.23.0](https://github.com/NousResearch/hermes-agent/tree/2bd378ed1b8d6bf2192cb26e0a55ff3091e6bd19)，提交 `2bd378ed1b8d6bf2192cb26e0a55ff3091e6bd19`，上游许可证 MIT。来源访问日期为 2026-11-10。

已实际运行记忆与技能元数据组件实验；完整模型、插件宿主、网关和调度实验的边界写在验证记录中。原创资料清单插件附带离线检查，读者可以从它继续做完整宿主实验。

本册使用公共构建器，产品名为 `hermes`，输出文件名为 `yuyu-hermes-zh.html`、`yuyu-hermes-zh.pdf` 与 `yuyu-hermes-zh.epub`。最终成品由主任务统一生成到主工作区 `yuyu-book/dist/`。英文版尚未启动。


2026-11-10 已完成三种格式的本地构建与交付，见[成品记录](../docs/agent-series/local-publication-20261110.json)。
