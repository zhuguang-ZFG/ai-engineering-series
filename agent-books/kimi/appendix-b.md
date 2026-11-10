# 附录 B：配置与源码导航

<!-- block: kimi-apxb.b-opening -->
配置文件描述运行选择，源码落点解释这些选择如何被解析和消费；引用时保留固定提交。

## B.1 本地文件各自负责什么

| 文件或目录 | 作用 |
| --- | --- |
| `config.toml` | provider、模型、权限、Hook 等运行设置 |
| `tui.toml` | 终端界面偏好 |
| `AGENTS.md` | Kimi 专用全局工作说明 |
| `agents/`、`skills/` | Kimi 专用用户角色与技能 |
| `plugins/installed.json` | 插件安装与启用状态 |
| `plugins/managed/` | 本地或 ZIP 插件的安装副本 |
| `sessions/` | 会话与 Agent 通信记录 |
| `logs/` | 诊断日志 |
| 项目 `.kimi-code/mcp.json` | 项目级 MCP 声明 |

除明确标为项目级的项目外，上表默认位于 `KIMI_CODE_HOME`。通用 `.agents` 资源仍按自身发现规则读取，不能认为修改 Kimi 数据根就隐藏了它们。

## B.2 沿一个问题找实现

以下路径均相对固定仓库根目录。

| 要核对的机制 | 源码落点 |
| --- | --- |
| ACP 子命令怎样进入服务 | `apps/kimi-code/src/cli/sub/acp.ts` |
| JSONL 消息形状 | `apps/kimi-code/src/cli/prompt-render.ts` |
| 非交互运行与错误输出 | `apps/kimi-code/src/cli/v2/run-v2-print.ts` |
| 插件清单与路径诊断 | `packages/agent-core-v2/src/app/plugin/manifest.ts` |
| 插件安装状态与更新 | `packages/agent-core-v2/src/app/plugin/manager.ts` |
| Agent frontmatter 解析 | `packages/agent-core-v2/src/workspace/workspaceAgentProfileLoader/internal/agentFile.ts` |
| Hook 匹配与并行 | `packages/agent-core-v2/src/features/externalHooks/internal/matchHooks.ts` |
| Hook 子进程与退出语义 | `packages/agent-core-v2/src/features/externalHooks/internal/runHook.ts` |
| MCP 配置字段 | `packages/agent-core-v2/src/mcpCore/config-schema.ts` |

表中路径是起点。确认运行行为还要看调用者与结果消费者，尤其是诊断级别、重载和会话生命周期。

## B.3 复核版本与来源

基线标签为 `@moonshot-ai/kimi-code@2.5.2`，提交为 `1c142a007c10e881602690def96057c23a2baa12`。源码 ZIP 摘要与关键文件摘要记录在 `facts/source-lock.json`；注册来源也使用这个完整提交。

标签提供可读名称，完整提交提供固定内容。若标签对应 annotated tag 对象，应继续解析到 commit；本次下载的 GitHub ZIP 注释直接给出提交标识，并另行核对了包版本与许可证。

## B.4 如何使用上游代码

上游采用 MIT 许可证，书籍采用仓库声明的内容许可。两者不应混成一份授权。本书链接并解释固定实现，原创练习另行维护；源码下载与编译产物放在忽略的实验目录中，不随书籍仓库提交。

依据：[固定源码根目录](https://github.com/MoonshotAI/kimi-code/tree/1c142a007c10e881602690def96057c23a2baa12)、[MIT 许可证](https://github.com/MoonshotAI/kimi-code/blob/1c142a007c10e881602690def96057c23a2baa12/LICENSE)。
