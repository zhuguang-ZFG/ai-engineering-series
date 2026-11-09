# 四本 Agent 分册：研究入口

[任务表](agent-series/tasks.json) · [规格](superpowers/specs/2026-11-09-agent-ecosystem-volume.md) · [计划](superpowers/plans/2026-11-09-agent-ecosystem-volume.md)

| 对象 | 写作基线 | 书稿与提纲 | 阶段 |
| --- | --- | --- | --- |
| OpenCode | v1.19.5 | [OpenCode](../opencode/README.md) | 第 8、9 章；处理器与 Windows 宿主实验 |
| DeepSeek Harness | fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159 | [DeepSeek](../deepseek/README.md) | 规划，待宿主实验 |
| Hermes Agent | v0.23.0 | [Hermes](../hermes/README.md) | 规划，待宿主实验 |
| Codex CLI | rust-v0.167.0 | [Codex CLI](../codex/README.md) | 规划，待宿主实验 |

完整提交、许可证、访问时间和源码入口见 [sources.lock.json](agent-series/sources.lock.json)。它是研究锁文件，暂不注册进电子书构建器。Hermes、Codex 的 annotated tag 已解析到实际 commit。

## 已核对与待核对

| 观察 | 证据层级 | 范围 |
| --- | --- | --- |
| OpenCode V1 Plugin 返回 Hooks；工具事件为 (input, output)，返回 Promise<void> | 钉版类型声明 | packages/plugin/src/index.ts |
| V1 trigger 顺序调用处理器，共享 output，不使用回调返回值 | 钉版源码 | packages/opencode/src/plugin/index.ts 的 trigger |
| V1 注册了事件取消订阅与 dispose 清理 | 钉版源码、宿主实跑 | Windows serve 的实例清理触发了 B/A dispose；其他退出路径未测 |
| 显式 B 和目录发现 A 按顺序调用，read 结果返回模型请求 | 宿主实跑 | 模型协议用本地替身，插件、内置工具与 SDK 日志为真实实现 |
| 实例重建再次初始化，但同进程复用旧模块；重启后读取新源码 | 宿主实跑 | 文件监听关闭，不代表自动热重载行为 |
| 坏插件初始化失败不阻断 B/A；--pure 跳过外部插件 | 钉版源码、宿主实跑 | 不推及其他 Hook 异常或全部内置插件 |
| v1.19.5 另有 V2 PluginV2，以 Scope 管理注册 | 钉版源码 | packages/core/src/plugin.ts |
| DeepSeek 将循环、会话、提示词、工具分成包 | 钉版目录 | packages/core；运行行为待验证 |
| Hermes 有会话状态、技能、cron、gateway 子系统 | 钉版目录、官网研究线索 | 加载策略和记忆预算待追踪 |
| Codex 有 CLI、exec、app-server 和平台沙箱模块 | 钉版目录、官方文档 | 所钉二进制尚未实跑 |

回调单测不等于完整 CLI 加载；提示词改变不等于权限改变；记忆文件更新不等于模型权重训练。

上游原文、源码、日志放在忽略的 .scratch/upstream 与 .scratch/agent-series。提交原创分析、样例、复现命令和脱敏摘要。第一份结果见 [OpenCode VERIFY](../opencode/VERIFY.md)。
