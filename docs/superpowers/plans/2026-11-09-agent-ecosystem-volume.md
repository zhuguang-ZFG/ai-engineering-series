# 实施计划：四本 Agent 分册

[规格](../specs/2026-11-09-agent-ecosystem-volume.md) · [任务状态](../../agent-series/tasks.json) · [研究入口](../../agent-series-research.md)

## S0：本次启动

- [x] 建立四个分册任务和独立产品身份。
- [x] 解析实际提交，区分标签对象与 commit。
- [x] 建立逐章提纲和源码入口。
- [x] 完成 OpenCode V1 插件样章、处理器实验及验证说明。
- [x] 完成内容、示例与仓库 Fast 检查；详情见 OpenCode VERIFY。

## S1：OpenCode（当前）

- [x] 在临时项目验证 Windows 发布版 CLI 的本地插件发现、加载和实例清理；四场景与复现命令见 OpenCode VERIFY。
- [x] 完成第 9 章，记录初始化失败、同进程模块复用、进程重启与 --pure 的实测边界。
- [ ] 追踪 V1/V2 入口与默认选择，分别记录兼容边界。
- [x] 跟踪一次 serve → 会话 → 本地模型替身 → 内置 read → 工具结果返回的只读路径。
- [ ] 跟踪一次读写任务的客户端、服务端、会话、模型请求和工具结果。
- [ ] 完成 Hooks、自定义工具、失败、资源释放、MCP 与权限专题。
- [ ] 按 [提纲](../../../opencode/outline.md) 完成正文和图示。
- [ ] 注册 opencode 产品，完成本地 HTML/PDF/EPUB、视觉复核及 CI。

## S2：DeepSeek Harness

- [ ] 从 Cordis 配置追到服务注入与插件初始化。
- [ ] 验证挂载、依赖缺失、卸载、重新挂载。
- [ ] 跟踪事件日志、提示词、工具与循环，实跑替换循环实验。
- [ ] 按 [提纲](../../../deepseek/outline.md) 完成正文、图示和实验。
- [ ] 注册 deepseek 产品，完成三种本地格式与 CI。

## S3：Hermes

- [ ] 核对 memory、skills、历史检索的保存位置与加载策略。
- [ ] 用隔离目录验证跨会话读取、修正和清理。
- [ ] 检查 cron/gateway 的任务身份、重复执行和凭据边界。
- [ ] 区分知识文件变化、请求变化和权重训练。
- [ ] 按 [提纲](../../../hermes/outline.md) 完成正文、图示和实验。
- [ ] 注册 hermes 产品，完成三种本地格式与 CI。

## S4：Codex CLI

- [ ] 对齐 release、Rust workspace、CLI/exec/app-server 入口。
- [ ] 用临时文件建立审批/沙箱矩阵，逐平台记录支持状态。
- [ ] 验证取消、工具失败、resume/fork 与磁盘副作用的关系。
- [ ] 核对 AGENTS.md、skills、MCP、hooks 的钉版接口。
- [ ] 按 [提纲](../../../codex/outline.md) 完成正文、图示和实验。
- [ ] 注册 codex 产品，完成三种本地格式与 CI。

执行顺序：源码核对 → 最小实验 → 样章 → 完整正文 → 装配 → 本地 PDF/EPUB → 视觉复核 → PR/CI。只勾实际完成项。

2026-11-10：V1 serve 已实跑；V2 仅源码核对，自动热重载未测。下一步沿第 6、7 章做自定义工具与权限允许/拒绝/询问实验，再补工具失败与取消路径。
