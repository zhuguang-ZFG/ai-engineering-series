# 五套 Agent CLI 的现场用法（草稿）

> **DRAFT —— 未进 `yuyu-book/manifest.json`，不进 HTML/PDF 产物，不作正文依据。**
> 生成方式：本机全量 `--help` 抓取 + 安装目录实地查看；Cursor 与 Qoder 的行为语义另读官方文档补齐（2026-11-01，Windows 11 / Git Bash）。每条断言属哪一级证据，见 §五。
> 落点已定（2026-11-01）：本页继续停在 C（不进 manifest），最值钱的那一格按 B 落进第 4 章 §4.3.6；页内其余用法清单仍是草稿，且 §二 的 Cursor 那格按 headless 页改过一次口径（见该条）。

## 一、这页想干什么

正文讲的是一套线束（Claude Code）怎么长成现在这样。这一页把另外五套摊开，看同一层边界在别人手里会长成什么形状——护栏是一条管线还是两个正交的轴，上下文能不能被显式手术，规划模型和执行模型能不能分开定价。

它是**对照面，不是依据**，与 `CREDITS.md` §三同一规矩。

## 二、本机实测环境

| 工具 | 版本 | 入口 | 配置根 | 仓库 / 许可 | 证据 |
| --- | --- | --- | --- | --- | --- |
| Kimi Code | 2.4.1 | `~/.kimi-code/bin/kimi.exe`（单文件 161 MB，旁带 `rg.exe` `fd.exe`） | `~/.kimi-code/`（`config.toml` `tui.toml` `agents/` `skills/` `sessions/` `AGENTS.md`） | `MoonshotAI/kimi-code`，MIT | A |
| Oh My Pi | 18.14.2 | `~/.bun/bin/omp.exe`（单文件 243 MB） | `~/.omp/`（`PI_CODING_AGENT_DIR` 默认 `~/.omp/agent`） | `can1357/oh-my-pi`，MIT（`@oh-my-pi/*` 各包均 MIT） | A |
| Codex | 0.166.0 | `%APPDATA%/npm/codex` | `~/.codex/`（`config.toml` `agents/`） | `openai/codex`，Apache-2.0（已登记 `gh-codex`） | A |
| Qoder CLI | 1.1.81 | `~/.qoder/bin/qodercli/qodercli` | `~/.qoder/`（`agents/`、settings） | 专有，无公开仓库 | A（旗标）/ C（语义） |
| Cursor（IDE 启动器） | 3.27.22 | `%LOCALAPPDATA%/Programs/cursor/…/bin/cursor` | `~/.cursor/` | 专有，无公开仓库 | A |
| Cursor Agent CLI | `2026.10.22-27dcf5f` | `~/AppData/Local/cursor-agent/agent.cmd`（本次经官方 `irm` 脚本装上） | 全局 `~/.cursor/cli-config.json`，项目 `<project>/.cursor/cli.json` | 专有 | A（`--help` 实测）+ B（文档） |

命令面大小：kimi 14 个长选项，Codex 24，qoder 47，Cursor `agent` **26 个长选项 + 18 行命令**（本机实测；文档页只列了 23 + 18），Cursor IDE 44，omp **62 个长选项 + 约 60 个子命令**。前四套是「一个 CLI」，omp 更像「一个装了 CLI 的平台」。

## 三、常用用法矩阵

| 要做的事 | Kimi | Oh My Pi | Codex | Qoder | Cursor |
| --- | --- | --- | --- | --- | --- |
| 进入交互 | `kimi`（query 只能走 `-p`，无位置参数） | `omp "第一条消息"`，`@file` `@image.png` 直接带上下文 | `codex` | `qodercli "query"`（唯一把 query 收成位置参数的） | `agent`（独立入口，非 `cursor agent`）；`agent "refactor the auth module"`；IDE 侧另有 `cursor --chat` 独立聊天窗 |
| 接住上次会话 | `-S [id]`（省 ID 就列表挑）/ `-c` | `-c` / `-r [id\|path]` / `--restore <session.jsonl>`（连上次中断的 turn 和它当时跑的子智能体一起接住） | `codex resume`（`--last`）/ `archive` / `fork` / `queue` | `-c` / `-r [id]` / `--fork-session` / `--list-sessions` / `--delete-session <index>` | `agent ls`（开旧会话挑一条）/ `agent resume`（最近一条）/ `--continue`（文档明写是 `--resume=-1` 的别名）/ `--resume [chatId]` / `agent create-chat`（先建空会话拿 ID） |
| 跑一条就退（脚本 / CI） | `-p` + `--output-format text\|stream-json` | `-p` + `--mode json`；`--max-time 10m`、`--max-cost 5` 兜底（超限 print 退 3） | `codex exec`（是子命令不是旗标）；`codex review` 专跑代码审查 | `-p` + `-o/--output-format` + `--no-session-persistence`（不落盘）；文档明写 **headless 下 `ask` 直接变 deny**——同一个 `ask` 在四种宿主里有四种消费法：TUI 询问、headless 自动拒绝、SDK 走 `canUseTool` 回调、ACP 发 `requestPermission` RPC | `-p/--print` + `--output-format text\|json\|stream-json` + `--stream-partial-output`；`--trust`（headless 下免询问直接信任工作区）。**文档两处明写 print 模式拿到 write 与 shell 的全量权限** |
| 风险阀门拧到哪 | `-y/--yolo`（常规自动、risky 仍问）/ `--auto`（全不问）/ `--plan` 起手即规划 | `--auto-approve` / `--approval-mode always-ask\|always-ask-cached\|write\|yolo` | **两个轴**：`-s read-only\|workspace-write\|danger-full-access`（能碰什么）×`-a on-request\|never`（何时喊人）；`--approve-for-me` 把审批交给自动评审并锁在 workspace-write | `--permission-mode` 五档语义各异：`default`（读和内部动作自动、敏感动作问）、`accept_edits`（只自动批准受信目录内的安全文件编辑，shell 与外部动作照旧问）、`auto`（交给分类器）、`bypass_permissions`（跳询问，但 `rm` 指向工作目录 / 家 / 根 / 顶级目录时仍问且无「总是允许」）、`dont_ask`（**该问的一律拒绝**）。别名 `yolo` / `bypassPermissions` 大小写不限；`--dangerously-skip-permissions` 与 `--yolo`、`--permission-mode bypass_permissions` **完全等价**，没有谁更强。非 default 档只在受信目录生效，否则回落 `default` | 三条独立的路：`--force`（`--yolo` 同义，除非被显式 deny 否则放行）、`--sandbox enabled\|disabled`（`agent sandbox run <cmd>` 还能单独给 `--allow-paths` `--readonly-paths` `--blocked-patterns` `--network`）、规则文件里的 `permissions.allow` / `deny` 五类 token：`Shell(base)` `Shell(cmd:args)` `Read(glob)` `Write(glob)` `WebFetch(domain)` `Mcp(server:tool)`，且 **deny 压过 allow**；另有 `--approve-mcps`。**本机实测多出一项文档没有的 `--auto-review`**：help 原文是「a server classifier auto-runs safe tool calls and prompts for the rest」——判定发生在服务侧 |
| 模型怎么选、怎么分工 | `-m <alias>`（alias 在 `config.toml`，`default_model` 兜底）；provider 走 `kimi provider` | `--model` 模糊（`opus`）或精确（`openai/gpt-5.2`）；分三角色 `--smol/--slow/--plan`；`--prewalk` 在计划的 todo 立起来后、第一次写文件时切便宜模型；`--plan-yolo` 起手只读规划、模型一 resolve 就自动批、再换 `--plan-yolo-into` 去写；`--thinking off..max\|auto` | `-m`；`--oss --local-provider lmstudio\|ollama` 整段换到本地开源栈 | `-m`（新模型用 name、自定义用 modelID）/ `--list-models` / `--reasoning-effort` / `--thinking` / `--thinking-budget <tokens>` / `--context-window` / `--max-output-tokens` | `--model` / `--list-models` / `agent models`；`--mode plan\|ask`（Ask 是只读探索）与 `--plan`。本机 `cli-config.json` 里已存着**按模型分开**的 `modelParameters`，旋钮名见到 `thinking` `reasoning` `effort` `context` `fast` 五种。help 还给了文档没写的一种写法：**参数化模型可用方括号覆盖**，例 `--model 'claude-opus-4-8[context=1m,effort=high,fast=false]'`；换推理网关则靠 `-e/--endpoint`（默认 `https://api2.cursor.sh`，可用 `CURSOR_API_ENDPOINT`）与 `bedrock` 子命令 |
| 往上加东西 | `--skills-dir`（可重复，顶掉自动发现的 user/project 目录）/ `--agent <name>` / `--agent-file <path>`；`kimi acp` 当 ACP server | `--hook` `-e` `--plugin-dir` `--skills <glob>` `--no-rules` `--no-context-files`（连 AGENTS.md、CLAUDE.md 都不吃）`--tools/--no-tools` `--no-lsp` `--no-pty` `--config <overlay>` `--profile`；子命令 `skill`（Skillshare registry）、`agents unpack`、`acp` | `codex mcp` / `codex plugin`；`-c key=value` 点 TOML 路径直接覆盖嵌套值；`--enable/--disable <FEATURE>` 拧 feature flag；`--strict-config` 让未知字段当场报错 | `--mcp-config <file\|inline>` + `--strict-mcp-config` + `--allowed-mcp-server-names` / `--agents <json>` / `--plugin-dir` / `--settings <json>` + `--setting-sources user,project,local` / `--system-prompt` `--append-system-prompt` `--output-style` | `agent mcp list\|enable\|disable\|list-tools\|login`（读 `.cursor/mcp.json` 或 `~/.cursor/mcp.json`，CLI 自动沿用编辑器配好的同一批 server）、`--plugin-dir <path>`（可重复）、`agent acp`；规则走 `.cursor/rules`，且 CLI 另读项目根的 `AGENTS.md` 与 `CLAUDE.md`，skills 从 `/` 菜单挑。IDE 侧还有 `cursor --add-mcp '<json>'` 把 server 定义写进 profile；本机 help 里另有 `agent plugin`（管插件与插件市场），文档参数页没这条 |
| 多智能体、并行、后台 | `kimi fork` / `session` / `export`（会话打成 ZIP） | 内置 `task` 工具；`omp cleanse`（加权并行子智能体扫诊断并修）；`--wait-async`（退出前等后台作业，每个结果把会话唤醒一次）；`ps`（daemon 监督的后台进程）；`session`（跨机移交 pack/unpack/moved/lease） | `codex agents`（共享本地 app-server daemon 上的全部会话）/ `queue`（往已存在会话排队发消息）/ `--remote ws://host:port` | `--worktree [name]` / `--remote [task]`（建云会话并回访问 URL）/ `--remote-session` / `--remote-control` | `-w/--worktree [name]`（落 `~/.cursor/worktrees/<reponame>/<name>`，配 `--worktree-base <branch>`、`--skip-worktree-setup`，setup 脚本读 `.cursor/worktrees.json`）；消息前加 `&` 把当前任务推给 Cloud Agent，之后在 web / mobile 接回；`agent worker start` 起私有 cloud worker（`--worker-dir` 可重复、`--pool` / `--pool-name`、`--label`、`--computer-use`、`--share-desktop view\|view_and_control`，help 还写清了 `--pool` 的门槛：不带它是个人 My Machines worker，带上就进团队 Self-Hosted Pool、要 Enterprise 计划加服务账号 key）；`agent persist` 让会话在终端断线后活下来（文档未列）；本机配置里 `exploreSubagentModel` 单列一项 |
| 读回别的工具 | `import-sessions`（导入 Claude Code 与 Codex 会话）/ `migrate`（旧 kimi-cli）/ `vis`（浏览器里看会话） | `--from-claude` / `--from-codex` | `codex apply`（把最新 diff 以 `git apply` 落回本地工作树） | `--attachment <file>` / `wiki`（给项目生成文档） | 未见「导入别家会话」的命令；它共享的是配置层——CLI 与编辑器同一份 `mcp.json`、同一个 `~/.cursor/worktrees/`，`agent generate-rule` 生成规则、`agent status\|about --format json` 把自身状态交给脚本 |

最后一行值得单独看一眼：**会话已经是可跨工具搬运的资产**了。两家不同的 CLI 都实现了「导入 Claude Code 的会话」，正文第 2 章（对话循环）和第 6 章（记忆）讲的持久化格式，在这里第一次露出「别人会来读」的后果。

## 四、每套的性格，以及它回扣哪一章

- **Codex → 第 4 章 权限管线。** 它是唯一把「能不能碰磁盘」和「什么时候喊人」拆成两个正交轴的（3 × 2）。正文里 Claude Code 的护栏是一条管线，Codex 说明同一层边界也可以摊成矩阵——矩阵的好处是能单独收紧一轴。
- **Oh My Pi → 第 7 章 上下文管理 + 第 14 章 Plan 模式。** `--no-context-files`、`compress`（把文本压成稠密 prompt 语域并报告丢了什么）、`find`（描述行为→返回实现它的文件与行段）、`toks`（多个离线 tokenizer 同时计数）全是对上下文的显式手术；`--prewalk` / `--plan-yolo` 则把「规划用哪个模型、执行用哪个模型」写成了命令行旗标——第 14 章的 Plan 模式在这里变成了定价决策。
- **Kimi → 第 5 章 设置与配置 + 第 11 章 技能与插件。** 命令面最小（14 个长选项），却把 `config.toml` 的模型 alias 表、`--skills-dir`、`--agent-file` 三个扩展位留得干干净净：一套「小核心 + 外插」的取向。
- **Qoder → 第 4 章 + 第 8 章，是五家里护栏层写得最厚的一本。** 三件事值得抄进正文：其一，钩子插在判定管线里两个点上，且 `PreToolUse` 返回 `deny` 的优先级**高于一切权限模式**——`bypass_permissions` 也拦得住，这正是第 8 章「扩展点」在安全上的兑现；其二，`auto` 档把授权交给一个两阶段分类器（第一阶段只能放行，只有第二阶段能判拦），连续拦截到上限触发熔断才恢复询问，而分类器不可达时**判拒而不是转人工**；其三，`autoMode` 的自定义规则只从用户全局设置读取，工作区里的同名文件一律忽略，文档给的理由是「仓库随 checkout 一起来，能往分类器里加 allow 项就等于把危险动作往放行上带」——第 5 章讲配置来源优先级时，这是一个把信任边界画在文件来源而不是字段上的实例。另外它把路径形态（UNC 网络位置、备用数据流 `file.txt:stream`、8.3 短名、设备路径、`CON` / `NUL`）当作**独立于规则的第二条轴**单独处理，网络位置的确认还不给「总是允许」。（`--agents <json>` 在命令行上直接定义子智能体、`--output-style` 只能改语气结构而改不动身份与安全约束，这两条仍可回扣第 11 章与第 15 章。）
- **Cursor → 第 4 章 权限管线，而且是目前最尖锐的那个对照。** 它的 CLI 入口是独立的 `agent`（`curl https://cursor.com/install -fsS | bash` / Windows 用 `irm 'https://cursor.com/install?win32=true' | iex`），**不是** `cursor agent`——后者是 IDE 的 shim，所以本机探针全打空。两处值得落字：其一，permissions 页原话是 "Print mode can use write and shell tools"——这句说的是 print 模式的工具集没被裁掉，不等于改动会落盘：headless 页另写 "Without `--force`, changes are only proposed, not applied"，两页在「无人值守的写」这一格上不口径一致，正文取后一句，因为它说得出实际后果。反制手段是 deny 优先的规则表和 `--trust` 这个显式开关；其二，它把「工具 × 路径 / 参数 glob」（`Shell(curl:*)`、`Read(.env*)`、`Write(**/*.key)`、`WebFetch(*.example.com)`、`Mcp(datadog:*)`）而不是「能力档位 × 审批时机」当成护栏的主语——与 Codex 的 3 × 2 矩阵正好是同一层的两种解法。另有 `--mode ask` 提供 Plan 之外的第二个只读档，可回扣第 14 章。

把它和另外两家并排看，这页最值钱的一格就出来了：**「没有人按键时，一个待确认的动作怎么办？」三家给了相反的答案。** Cursor 的 `-p` 留着 write 与 shell 这两个工具，但改动只出提议、不落盘（permissions 页那句讲的是工具集，不是落盘权限）；Qoder 的 `-p` 把所有 `ask` 判成 deny；Codex 的 `-a never` 既不放开也不一律拒，而是把边界交给同时指定的 `-s` 沙箱档位（它的 help 只说「执行失败立刻回给模型」）。同一个空白，三种填法。

更要紧的是 Cursor 一家就摆了四个开关：`-p` 只收提议、`--force`（`--yolo`）是「除非命中 deny 否则放」、`--auto-review` 把每次工具调用交给**服务端**分类器判（help 原文：safe tool calls 自动跑，其余照旧问）、`--sandbox enabled` 又换成沙箱划界。把它和 Qoder 的 `auto` 对着看更有意思：两家都把「谁来判」外包给一个分类器，可一个跑在服务侧、一个跑在本地模型侧，连失败行为都相反——Qoder 在分类器不可达时判拒，Cursor 的分类器既然在远端，判不了会怎样文档没说。这一格没有公认答案，而正文第 4 章目前是按「一条管线」写的。

## 五、证据等级

- **A（本机原文可核）**：五套 CLI 的 `--help` 全量文本、命令路径、配置目录、包内元数据。Codex 的 Apache-2.0 直接读自 `%APPDATA%/npm/node_modules/@openai/codex/package.json`；Cursor 的 `agent` 是本次用官方安装脚本装上的 `2026.10.22-27dcf5f`，`~/.cursor/cli-config.json` 里 `permissions` 的五类 token、按模型分开的 `modelParameters`、`approvalMode` 与 `sandbox` 键一并算 A 级。
- **文档会落后于二进制。** 官方参数页列 23 个全局选项，本机 `agent --help` 实测 **26**，多出来的是 `-e/--endpoint`（默认 `https://api2.cursor.sh`）、`--add-dir`、`--auto-review`；命令表里本机另多 `persist`、`plugin`、`team`、`bedrock`，而文档列出的 `sandbox`、`acp` 在本机 help 里是隐藏项。所以「某个旗标存不存在」以二进制为准，文档只用来核语义。
- **B（仓库与许可经 GitHub API 核对；引用前须钉 tag→完整 SHA）**：`MoonshotAI/kimi-code` MIT，tag `@moonshot-ai/kimi-code@2.4.1` → `2c73f3f50af4fa7f2540ca0d2e33b07a1408e3a7`；`can1357/oh-my-pi` MIT，tag `v18.14.2` → `7efd77219374ca4e8767979809835e4aa90666ba`。另有 `MoonshotAI/kimi-cli`（Apache-2.0，Python，**已于 2026-09-22 归档**），那是 `kimi migrate` 提到的旧前身，不是现役 CLI——登记时别混。
- **C（专有、无公开仓库）**：Qoder CLI 与 Cursor 都没有仓库可登记——`CREDITS.md` §三只收 MIT / Apache-2.0 一类的宽松许可，这两家进不了。Cursor 的旗标面已升到 A 级（本机 help），但权限规则的**语义**——deny 压过 allow、五类 token 各自怎么匹配、`WebFetch` 的域名通配——只有官方文档写着（`/docs/cli/overview`、`/docs/cli/using`、`/docs/cli/reference/parameters`、`/docs/cli/reference/permissions`，访问日 2026-11-01），那半个问题仍是文档证据；若要按 §二 的 docs 族登记，得先决定「非 Anthropic 家官方文档」是否允许进依据链（现在 §二 的 21 条全是 `code.claude.com/docs`），我的判断是：允许登记，但 `scope` 必须写死「第 4 章的对照面」，否则就破了「对照面不是依据」这条规矩。
- Qoder 的权限语义取自官方 `docs.qoder.com/cli/permissions`（访问日 2026-11-01，正文全文读过一遍，不是二手转述）。同一页里有两处自身不一致，落字前必须挑明：模式表说 `default` 是「安全读与内部动作自动跑、敏感动作才确认」，下方的 Mode-Configuration 表却把 `default` 写成「每个动作都弹确认」；小标题写「8-Layer Priority」，表里只列到第 7 层，第 8 层大约指段末那句组织策略 `allowManagedPermissionRulesOnly`（这句是推断，不是文档原文）。
- 抓取 Cursor 文档时踩到一个和 `CREDITS.md` §七 同一类的问题：官方 `llms.txt` 给出的链接带 `.md` 后缀，`/docs/cli/overview.md` 与 `/docs/cli/using.md` 能取到，`/docs/cli/reference/parameters.md` 与 `/docs/cli/reference/permissions.md` 却 **404**，去掉后缀才 200。登记时按跳转后可读的规范 URL 记，别照抄 sitemap 里的字符串。
- 两个已经踩过的坑，记下来免得再踩：npm 全局里的 `cursor-cli@1.0.0`（MIT）是 `tal7aouy/cursor-cli`，一个「切换终端光标显隐」的库，和 Cursor 无关；`cursor agent --help` 打的是 IDE usage、`cursor agent -p` 把参数交给 Electron——那不代表 Cursor CLI 的能力面，只代表 IDE 的 shim。

## 六、三个落点，和各自的契约成本

当前口径：`manifest.json` 共 **20 个 unit** = `front` + `ch01`…`ch15` + `apxa`…`apxd`；`guides` 里正好 **20 条**，每条 **7 个必填字段**（`question` `deliverable` `boundary` `sources` `plain` `analogy` `plain_evidence`），而 `sources` 只能指向 `CREDITS.md` 登记过的 ID。

| 落点 | 动什么 | 代价 |
| --- | --- | --- |
| **A 新开第 21 个 unit**（如「附录 E：五套 CLI 现场手册」） | `test_build_contracts.py:668` 的 `assertIn("20 units", out)`；`scripts/build_beginner_reader.py:40` 的双语「四份附录」路线说明；`manifest.start_reading` 第四张卡「使用四份附录…」；新增一条含 `plain_evidence` 行锚的 `guides`；中英两侧同步；CI 用 Noto 重测页数 | 最高。且 Qoder / Cursor 无可登记仓库 ID——要么这两家不进正文，要么放宽 `CREDITS.md` 的许可口径（不建议） |
| **B 并进 `ch15` 末尾一小节** | unit 数保持 20、`guides` 不动；只在文件末尾追加，不搬动任何已有 `glosses.json` 行锚；仍需中英同步、页数重钉、五道闸 | 中。但 ch15 的收束语气是「拆自己」，插一节横向竞品对照会岔开它 |
| **C 留在 `docs/notes/`（现状）** | 什么都不动 | 零。代价是它不进 HTML/PDF，读者看不到，只对后续写作当素材 |

**建议已采纳（2026-11-01）：草稿停在 C，那一格按 B 落进第 4 章。** 触发条件这一页就凑齐了——第 4 章手上现在有三个现成实例：Codex 把能碰什么与何时喊人拆成两轴，Qoder 让 `PreToolUse` 的 `deny` 压过 `bypass_permissions`，Cursor 在 print 模式里把写降成一份不落盘的提议。动第 4 章时按 B 落进那一章，不新开 unit——这一条已经执行，正文里只搬那一格，一整页说明书式的对照留在本页。落的时候有两件事要先定：`sources` 得能指向已登记 ID（`gh-codex` 现成，kimi-code / oh-my-pi 可按 §三 的规矩新增，Qoder 与 Cursor 只能走 §五 提出的「非 Anthropic 官方文档是否进依据链」这一步）；以及一整页说明书式的对照不能整段搬进正文，只搬那一格「没人按键时怎么办」。

## 七、还缺什么

1. **Cursor 分类器的送达范围。** `agent` 已装，旗标层是 A 级；但 `--auto-review` 那句「server classifier」到底把哪些字段送出机器，help 与文档都没写，不能替它假设。`agent models` / `--list-models` 需要登录，本次未认证故未核——正文若要列 Cursor 的可用模型，得先由用户点头登录。
2. **Qoder 文档没写的两处。** `--setting-sources` 三个取值的确切语义未见说明；`security` 子命令按文档属服务侧分析、需要联网，但「具体哪些源码离开本机」没写。若进正文，只能落成「会把代码交给扫描服务，范围未见于文档」，不能替它补一个更干净的说法。
3. **omp 的 `--external-thinking`**：help 自己写了「providers have flagged this request shape as abuse」。若这条进正文，风险提示必须一起写，不能只留旗标名。
4. **`gh-codex` 落后一个 minor**：登记表钉 `rust-v0.164.0`，本机是 0.166.0。任何「某行为从哪个版本起才有」的句子都得先重钉，否则引用的是旧版能力面。
