# 附录 A：固定版本与源码导航

<!-- block: deepseek-apxa.b-opening -->
本册源码基线是 DeepSeek Harness 提交 `fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159`。根包版本 `0.2.2-rc.1`，vendored Cordis 包版本 `4.1.0`，项目采用 MIT 许可证。本文不将主分支当前内容当成这份快照的证据。

## A.1 按责任找文件

| 问题 | 首先读取 | 继续追踪 |
| --- | --- | --- |
| 启动了什么应用 | apps/cli/README.md | packages/boot/app-boot |
| 插件为什么没激活 | vendor/cordis/src/registry.ts | fiber.ts、reflect.ts |
| 服务怎么解析 | vendor/cordis/src/context.ts | service.ts、reflect.ts |
| 清理何时完成 | vendor/cordis/src/fiber.ts | effect、await、dispose |
| next 怎样返回 | vendor/cordis/src/events.ts | waterfall 与 called 标记 |
| Agent 入口归谁 | packages/core/agent/src/index.ts | agent-loop 的工厂 |
| 一轮任务如何执行 | packages/core/agent-loop/README.md | src/agent.ts、inbox.ts |
| 工具从哪注册 | packages/core/tools/src/index.ts | pipeline.ts、schema.ts |
| 提示词如何排序 | packages/core/system-prompt/src/index.ts | section、context、assemble |
| 单 Agent 能力范围 | packages/core/scope/src/index.ts | store.ts、ScopedLayers |
| 配置保存与生效 | packages/boot/plugin-manager/README.md | app-boot 与 HMR |

## A.2 三种证据怎样读

源码契约说明在指定实现里调用会沿哪条分支走；官方文档说明公开接口的意图和边界；组件实跑说明本机实际执行了什么。三者互相补充，却不能互相冒名顶替。若文档写“支持热重载”，而实验关闭文件监听，本次结果就不能算热重载验收。

本册把完整运行记录放在 facts，公开摘要不含个人路径、账号或网络凭据。原始上游文件只下载到 .scratch，未作为书籍源码提交。读者复现时应核对 commit 和文件散列，再运行代码。下载失败就停止，不要用另一份“差不多”的文件替代。

## A.3 阅读源码的顺序

先读职责文档，确定边界，再读公共接口，最后追执行器。以工具为例，先看 tools 的注册与管线契约，再看调用身份、参数快照、策略和结果归一化；不要一开始陷入某个具体文件工具的路径处理。

日志与状态字段要追到写入方。看到 UI 使用 status，不表示 UI 拥有该状态；看到某个包导出 Agent 类型，也不表示这个包实现模型循环。沿着“谁创建、谁变更、谁清理”寻找源码，通常比按文件名猜职责更快。

编译通过也不是最终事实。类型可能没表达外部副作用、取消时机和失败后遗留资源。本书七项组件实验专门补这些运行关系，下一步完整应用实验应继续围绕同一责任边界展开。

## 固定版本来源

- [docs/architecture.md](https://github.com/deepseek-ai/deepseek-harness/blob/fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159/docs/architecture.md)
- [vendor/cordis/package.json](https://github.com/deepseek-ai/deepseek-harness/blob/fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159/vendor/cordis/package.json)
- [vendor/cordis/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159/vendor/cordis/src/index.ts)
