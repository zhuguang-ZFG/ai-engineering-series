# 附录 C 配置项与环境变量

写作钉：`pi/1.5.0`。完整字段见 `docs/settings.md`、`docs/configuration.md`、`docs/environment-variables.md`；
本附录只列日常最常改的几组。

## C.1 文件位置

| 路径 | 作用 |
| --- | --- |
| `~/.pi/agent/settings.json` | 用户级设置 |
| `.pi/settings.json` | 项目级设置（要项目信任） |
| `~/.pi/agent/keybindings.json` | 键位 |
| `~/.pi/agent/mcp.json` | 全局 MCP 服务器 |
| `~/.pi/agent/models.json` | 兼容端点、模型、覆盖 |
| `~/.pi/agent/auth.json` | 凭据（**不要提交/分享**） |
| `~/.pi/agent/AGENTS.md` | 全局项目指令 |
| `~/.pi/agent/SYSTEM.md` | 覆盖系统提示 |
| `~/.pi/agent/APPEND_SYSTEM.md` | 追加系统提示 |
| `~/.pi/agent/extensions/` 等 | 资源目录 |

agent 目录可用 `PI_CODING_AGENT_DIR` 或 SDK 的 `agentDir` 改。

## C.2 常用设置

| 键 | 默认 | 说明 |
| --- | --- | --- |
| `defaultProvider` / `defaultModel` | 自动 | 启动 provider / 模型 |
| `defaultThinkingLevel` | `"medium"` | 启动思考档位 |
| `enabledModels` | 全部 | 启动选择与循环用的模型模式 |
| `defaultTools` | `["read","bash","edit","write"]` | 启动工具集；纯名字替换，`+`/`-` 增删 |
| `compaction.enabled` | `true` | 自动压缩 |
| `compaction.reserveTokens` | `16384` | 触发压缩的保留量 |
| `compaction.keepRecentTokens` | `20000` | 压缩时原样保留的近期 token |
| `branchSummary.skipPrompt` | `false` | 跳过分支摘要提示 |
| `theme` | `"system"` | 主题；可写 `light/dark` |
| `tuiMode` | `"fullscreen"` | `fullscreen` / `regular` |
| `quietStartup` | `false` | 隐藏启动头/资源列表 |
| `sessionDir` | agent 会话目录 | 会话存储；项目设置里的 `sessionDir` 会在信任前被读 |
| `defaultProjectTrust` | `"ask"` | `ask`/`always`/`never`；只能在 agent 设置里 |
| `shellPath` | 平台默认 | 自定义 shell 路径 |
| `packages` / `extensions` / `skills` / `prompts` / `themes` | `[]` | 资源与包声明 |
| `enableSkillCommands` | `true` | 技能是否注册为 `/skill:name` |
| `images.autoResize` | `true` | 发送前把图片缩到 2000×2000 内 |
| `markdown.mermaid` | `"streaming"` | Mermaid 渲染模式 |

设置合并规则：项目设置叠加在用户设置上；`+name`/`-name` 形式的工具列表是"改继承值"，纯名字是"整体替换"。

## C.3 常用环境变量

| 变量 | 作用 |
| --- | --- |
| `PI_CODING_AGENT_DIR` | agent 配置目录 |
| `PI_CODING_AGENT_SESSION_DIR` | 会话目录（`--session-dir` 优先） |
| `PI_OFFLINE` | `1/true/yes` 关闭启动网络操作 |
| `PI_PACKAGE_DIR` | 覆盖包目录（Nix/Guix） |
| `PI_SELF_UPDATE_COMMAND` | `pi update` 更新自身时执行的命令 |
| `PI_TELEMETRY` | 覆盖安装遥测（`1/true/yes` 或 `0/false/no`） |
| `PI_SHARE_VIEWER_URL` | `/share` 的查看地址 |

## C.4 Provider 凭据（节选）

| Provider | 变量 |
| --- | --- |
| Anthropic | `ANTHROPIC_API_KEY` / `ANTHROPIC_AUTH_TOKEN` / `ANTHROPIC_OAUTH_TOKEN` |
| OpenAI | `OPENAI_API_KEY` |
| DeepSeek | `DEEPSEEK_API_KEY` |
| NVIDIA NIM | `NVIDIA_API_KEY` |
| Google Gemini | `GEMINI_API_KEY` |
| Groq | `GROQ_API_KEY` |
| xAI | `XAI_API_KEY` |
| OpenRouter | `OPENROUTER_API_KEY` |
| Mistral | `MISTRAL_API_KEY` |
| Kimi | `KIMI_API_KEY` |

云凭据（Bedrock/Vertex）走 ambient 凭据或对应变量。完整清单以 `pi --help` 的 Environment Variables 段为准。

## C.5 优先级备忘

- 凭据：`--api-key` → `auth.json` → `models.json` 的 `apiKey` → 环境变量/ambient。
- 会话目录：`--session-dir` → `PI_CODING_AGENT_SESSION_DIR` → `sessionDir` 设置。
- 模型：`--model` / `--provider` → 设置里的 `defaultModel`/`defaultProvider` → 自动选择。
- 工具：命令行 `--tools`/`--no-tools` → `defaultTools` → 内置默认。

## C.6 三个安全提醒

1. `auth.json` 是明文凭据，别提交、别打包、别贴图。
2. 项目设置/扩展/技能要项目信任；信任只控制加载，不是沙箱。
3. `models.json` 的 `apiKey` 支持 `!command`，那会在请求时执行命令——只在你信任的配置里用。
