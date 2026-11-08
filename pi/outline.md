# Pi 分册目录与证据表

状态标记：`已落盘` = 正文文件存在且按六要素写（当前全部 25 章与 5 个附录）。
没有"占位章"——每一行都指向真实正文；二稿与英文版另计。

篇名与章名暂定，落笔时可改；**证据锚点**列的是这一章必须读的上游文件（钉版 v1.5.0 的 `docs/` 与源码目录），
写正文时按锚点逐条核对，不靠记忆。

## 第一篇 · 认识这台机器

| 章 | 标题 | 证据锚点 | 状态 |
| --- | --- | --- | --- |
| 1 | 小而可改：Pi 到底是什么 | `README.md`（minimal / skips sub-agents and plan mode）、`docs/how-pi-works.md`、`docs/index.md` | 已落盘 |
| 2 | 装好，跑通第一圈 | `docs/quickstart.md`、`docs/windows.md`、`docs/terminal-setup.md`、`docs/cli.md` | 已落盘 |
| 3 | 模型、provider 与凭据 | `docs/models.md`、`docs/providers.md`、`docs/custom-provider.md`、`docs/models-configuration.md` | 已落盘 |

## 第二篇 · 每天怎么用

| 章 | 标题 | 证据锚点 | 状态 |
| --- | --- | --- | --- |
| 4 | 终端里的输入、@文件与排队转向 | `docs/usage.md`、`docs/keybindings.md`、`docs/slash-commands.md`、`docs/terminal-setup.md` | 已落盘 |
| 5 | 会话是一棵可以回退的树 | `docs/sessions.md`、`docs/session-format.md`、`docs/compaction.md` | 已落盘 |
| 6 | 上下文从哪来：系统提示、AGENTS.md、技能描述 | `docs/how-pi-works.md#context`、`docs/configuration.md`、`docs/skills.md` | 已落盘 |
| 7 | 压缩、分支摘要与"忘事" | `docs/compaction.md`、`docs/settings.md#compaction` | 已落盘 |
| 8 | 把结果带走：导出、print、JSON、RPC | `docs/usage.md#copy-export-or-share-results`、`docs/cli-integration.md`、`docs/json.md` | 已落盘 |

## 第三篇 · 内部原理

| 章 | 标题 | 证据锚点 | 状态 |
| --- | --- | --- | --- |
| 9 | 一次 turn 的生命周期 | `docs/how-pi-works.md#agent-loop`、`docs/message-types.md` | 已落盘 |
| 10 | 模型层：统一接口与流式事件 | `packages/ai`、`docs/models.md`、`docs/providers.md`、`docs/json.md` | 已落盘 |
| 11 | 工具层：内置、开关与自定义 | `docs/cli.md#tools`、`docs/extensions.md#custom-tools`、`pi --help` | 已落盘 |
| 12 | 会话格式与恢复 | `docs/session-format.md`、`docs/sessions.md`、`~/.pi/agent/sessions/` 实测 | 已落盘 |
| 13 | TUI：差分渲染、事件与主题 | `packages/tui`、`docs/tui.md`、`docs/themes.md`、`docs/keybindings.md` | 已落盘 |

## 第四篇 · 扩展与集成

| 章 | 标题 | 证据锚点 | 状态 |
| --- | --- | --- | --- |
| 14 | 扩展基础：加载、生命周期与事件 | `docs/extensions.md#writing-an-extension`、`docs/extensions.md#events` | 已落盘 |
| 15 | 扩展实战：工具、命令、快捷键与 UI | `docs/extensions.md#custom-tools`、`examples/extensions/` | 已落盘 |
| 16 | 技能：按需加载的指令包 | `docs/skills.md`、`examples/sdk/` | 已落盘 |
| 17 | 提示模板与主题 | `docs/prompt-templates.md`、`docs/themes.md`、`docs/tui.md` | 已落盘 |
| 18 | Pi 包：打包、安装与分发 | `docs/packages.md`、`package.json` 的 `pi` 字段 | 已落盘 |
| 19 | SDK 与 RPC：把 Pi 嵌进程序 | `docs/sdk.md`、`docs/rpc.md`、`docs/rpc-commands.md`、`examples/rpc-client.ts` | 已落盘 |

## 第五篇 · 实战

| 章 | 标题 | 证据锚点 | 状态 |
| --- | --- | --- | --- |
| 20 | 第一次真实交付：从需求到 diff | 本机实跑案例（不得使用未验证的 prompt 当证据） | 已落盘 |
| 21 | 无头自动化：print / JSON / RPC 进 CI | `docs/cli-integration.md`、`docs/cli.md`、`docs/containerization.md` | 已落盘 |
| 22 | 不可信仓库：信任、沙箱与凭据边界 | `docs/security.md`、`docs/containerization.md`、`docs/mcp.md` | 已落盘 |
| 23 | 排错与诊断 | `docs/usage.md#collect-diagnostic-information`、`docs/cli.md#prompts-and-process` | 已落盘 |

## 第六篇 · 精通

| 章 | 标题 | 证据锚点 | 状态 |
| --- | --- | --- | --- |
| 24 | 源码地图：12 个包怎么分工 | `packages/` 的 12 个 `package.json`、`docs/how-pi-works.md` | 已落盘 |
| 25 | 三册对照：同构点与不能借用的数字 | `PIN.md`、御舆 `README.md`、`omp/README.md` | 已落盘 |

## 附录

| 附录 | 内容 | 证据锚点 | 状态 |
| --- | --- | --- | --- |
| A | 命令行参数速查 | `docs/cli.md`、`pi --help` | 已落盘 |
| B | 斜杠命令与键位速查 | `docs/slash-commands.md`、`docs/keybindings.md` | 已落盘 |
| C | 配置项与环境变量 | `docs/settings.md`、`docs/configuration.md`、`docs/environment-variables.md` | 已落盘 |
| D | 术语表 | 全书统一用词 | 已落盘 |
| E | 版本追踪 | releases、`CHANGELOG.md`、`PIN.md` | 已落盘 |

## 每章必须有的六样东西

沿用两册既有规格（`omp/OVERHAUL-SPEC.md` 的六要素，本册不另立标准）：

1. **开场场景**：一个具体的、有后果的处境（≤ 2 段），不是定义。
2. **原理**：类比 + 至少一张图（Mermaid 或手绘 SVG）；Pi 分册**只用自绘 SVG / Mermaid，不调用生图 API**。
3. **可运行实验**：命令 + 预期输出 + 失败时怎么办；实跑标"本机已验"，没跑标"未验证"。
4. **翻车对照表**：至少一行"看起来对但会坏"的做法。
5. **同构点**：与御舆 / Omp 对照一小段，不搬对方数字。
6. **版本核对清单**：章末 3–5 条，写清钉在哪、升级后怎么复验。

另外：**来源**不是第七个要素，而是每一章的证据纪律——命令、数字、路径都要能落回
`PIN.md`、`VERIFY.md`、`facts/` 或钉版文档。

## 写作纪律

- 中文正文用全角标点，中英文之间留半角空格，代码块标语言。
- 数字只有两种来源：**钉版源码/文档**或**本机实测并留证据**。两者都没有的，写成"未验证"。
- 不把 `omp` 的旗标、数字、默认值当 Pi 的；不把 Claude Code 的权限模型当 Pi 的。
- 涉及第三方商标时保留"非官方"表述。

## 三册逐章对照（初稿）

| 主题 | 御舆（Claude Code） | Omp | Pi |
| --- | --- | --- | --- |
| 执行循环 | 对话循环 + 工具 | 同构 | `agent` 包 + `coding-agent` 的 turn |
| 工具 | 内置 + MCP + 插件 | 30+ 内置 | 4 个默认内置 + 3 个默认关闭 + 扩展 |
| 权限 | 权限管线（hooks/审批） | 审批 + 沙箱 | **无内置权限系统**；靠操作系统隔离与容器 |
| 上下文 | 记忆 + 上下文管理 | 记忆系统 | 系统提示 + 上下文文件 + 技能描述 + 压缩 |
| 扩展 | hooks / skills / 插件 | Skills / MCP / 扩展 | 扩展、技能、提示模板、主题、包 |
| 多 agent | 子智能体 / 协调器 | 内置子代理 | **不自带**，靠扩展或外部编排 |
| 编程接口 | SDK | SDK / RPC | SDK / RPC / JSON / print |

这张表是**阅读地图**，不是事实表；每一格进正文前都要回到钉版文档确认，第 25 章才做定稿。
