# OpenCode：从原理到实战

中文首版含前言、18 章和附录 A–D，围绕请求、会话、工具、权限和插件生命周期展开。第 6–9 章从原创工具与 Hook 一直讲到加载顺序、缓存、清理和授权有效期；后半册讨论 MCP、LSP、子任务、快照、SDK 与工程调试。

基线为 v1.19.5，提交 `810c0eba1a7348036f8bdf61e6632d0c36c6876c`，上游许可证 MIT。源码观察与实跑结论分别标注；英文版尚未启动。

[完整目录](outline.md) · [前言](00-前言.md) · [可运行实验](examples/README.md) · [验证记录](VERIFY.md) · [来源锁](../docs/agent-series/sources.lock.json)

在仓库根目录生成三种格式：

```bash
python scripts/bookctl.py build --product opencode --lang zh --pdf --epub
```

输出为 `yuyu-book/dist/yuyu-opencode-zh.html`、`.pdf`、`.epub`。本机统一交付目录为 `D:\Users\claude\claude-code-book-main\yuyu-book\dist`。

实跑覆盖 8 项处理器检查、4 个 Windows V1 宿主场景，以及 10 个原创工具权限场景。模型协议使用本地替身；TUI、V2、真实模型效果和其他平台仍不属于已验证范围。


2026-11-10 已完成三种格式的本地构建与交付，见[成品记录](../docs/agent-series/local-publication-20261110.json)。
