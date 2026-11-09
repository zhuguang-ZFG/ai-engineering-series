# OpenCode：从原理到实战

状态：已写第 8、9 章，完成处理器实验与 Windows 真实宿主插件实验。整书 HTML、PDF 和 EPUB 尚未生成。

研究重点：客户端/服务端、会话、插件与工具。基线：v1.19.5，提交 `810c0eba1a7348036f8bdf61e6632d0c36c6876c`。[上游固定版本](https://github.com/anomalyco/opencode/tree/810c0eba1a7348036f8bdf61e6632d0c36c6876c)，许可证 MIT，访问日期 2026-11-09。

[逐章提纲](outline.md) · [统一任务表](../docs/agent-series/tasks.json) · [来源锁文件](../docs/agent-series/sources.lock.json)

已写样章：[第 8 章：插件 Hook](ch08.md)、[第 9 章：插件加载、状态与 V1/V2](ch09.md)。[可运行示例](examples/README.md)及[验证记录](VERIFY.md)分别说明命令与边界。

按中文分册推进，英文版尚未启动。完成正文后将复用公共构建器，生成独立的 `yuyu-opencode-zh.html/.pdf/.epub`，最终放到主工作区 `yuyu-book/dist/`。

首轮源码入口：

- [packages/plugin/src/index.ts](https://github.com/anomalyco/opencode/tree/810c0eba1a7348036f8bdf61e6632d0c36c6876c/packages/plugin/src/index.ts)
- [packages/plugin/src/tool.ts](https://github.com/anomalyco/opencode/tree/810c0eba1a7348036f8bdf61e6632d0c36c6876c/packages/plugin/src/tool.ts)
- [packages/opencode/src/plugin/index.ts](https://github.com/anomalyco/opencode/tree/810c0eba1a7348036f8bdf61e6632d0c36c6876c/packages/opencode/src/plugin/index.ts)
- [packages/opencode/src/session/prompt.ts](https://github.com/anomalyco/opencode/tree/810c0eba1a7348036f8bdf61e6632d0c36c6876c/packages/opencode/src/session/prompt.ts)
- [packages/core/src/plugin.ts](https://github.com/anomalyco/opencode/tree/810c0eba1a7348036f8bdf61e6632d0c36c6876c/packages/core/src/plugin.ts)
