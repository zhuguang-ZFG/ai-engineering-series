# Pi 分册：版本钉与来源证据

本页登记的是**写作钉**和取到证据的那一次动作。书里出现的命令、旗标、路径、数字，都以这里的钉版为准；
与你机器上跑出来的不一样时，以你机器上的 `pi --version` 和附录 E 为准。

- 登记日期：2026-11-08（本机时间，Asia/Shanghai）
- 登记人：本书编辑（记录命令与原始输出，不改上游文件）
- 状态：**已核实**。核的是「这个钉存在、能拉、能跑」，不是「本书 25 章都写完」。

## 1. 身份

| 项目 | 值 |
| --- | --- |
| 产品名 | Pi（终端 AI 编程 agent，命令行 `pi`） |
| 官网 | <https://pi.dev/>（站点自称 "A terminal-based coding agent"） |
| 仓库 | <https://github.com/earendil-works/pi>（2026-11-08 的登记记录里，旧的 `badlogic/pi-mono` 链接会重定向到这里） |
| 包名 | `@earendil-works/pi-coding-agent`（monorepo 内目录 `packages/coding-agent`） |
| 作者 / 版权 | Mario Zechner（`package.json` 的 `author`）；站点页脚写 Earendil Inc. & Contributors |
| 许可 | MIT |
| 运行时要求 | Node.js **>= 22.19.0**（`package.json` 的 `engines`） |

**非官方声明**：本书与 Earendil Inc.、Pi 维护者及其贡献者**没有隶属关系**，也不是官方文档。
书里的判断、类比和练习都是本书作者写的；上游行为以上游钉版文档、源码和你的实测为准。

## 2. 写作钉

| 用途 | 值 | 取法 |
| --- | --- | --- |
| 写作钉（release tag） | `v1.5.0` | GitHub Releases 页当前最新的 release tag，发布 2026-11-02T11:05:31Z |
| 完整提交 | `f9a26365568127461c47a07a37dcb42c140a3ac5` | `git ls-remote https://github.com/earendil-works/pi.git refs/tags/v1.5.0` |
| npm 版本 | `1.5.0`（`latest` 标签） | `curl https://registry.npmjs.org/@earendil-works/pi-coding-agent` 读 `dist-tags` |
| 验收日期 | 2026-11-08 | 本条登记当天 |

`gitHead` 在 npm 元数据里是 `null`，所以**钉提交只能从仓库 tag 取**，不要拿 npm 包的哈希当提交。
`legacy-node20` 标签停在 `0.74.2`，那是给旧 Node 用的分支，不是本书的钉。

## 3. 本机复验（2026-11-08）

本机是 Windows，`pi` 位于 `%USERPROFILE%\.pi\agent\bin\pi`，
`pi --version` 打出 `1.5.0`，与写作钉一致。逐条命令与原始输出记在 [`VERIFY.md`](VERIFY.md)，
这里只留结论：

| 结论 | 证据 |
| --- | --- |
| 版本与 npm 一致 | `pi --version` → `1.5.0` |
| 顶层帮助可读，退出码 0 | `pi --help` |
| 8 个内置工具名；默认 4 个，另有 3 个默认关闭 | `pi --help` 末段列出 8 个名字；`docs/cli.md` 与源码 `DEFAULT_TOOL_NAMES` 写默认是 `read`、`bash`、`edit`、`write`；`grep`、`find`、`ls` 标 `off by default`；`powershell` 仅原生 Windows 可用，非默认 |
| 一次提示能跑完一整圈 | `pi --print --no-tools --no-session "只回复两个字：在线"` → stdout 仅一行 `在线`，退出码 0 |
| `--no-session` 真的不落盘 | 上条命令前后，`~/.pi/agent/sessions/--D--Temp-User--/` 文件数都 2 |
| 会话是 JSONL，首行是会话头 | `~/.pi/agent/sessions/<目录 slug>/<时间戳>_<id>.jsonl` 首行 `{"type":"session","version":3,...}`，随后是 `model_change`、`thinking_level_change` 等条目 |
| JSON 模式输出事件流 | `pi --mode json "..."` 首行就是那个会话头，之后逐行 `agent_start`、`turn_start`、`message_start`… |
| 模型目录可以离线查 | `pi --offline --list-models nvidia` 打印表格并退出 0 |
| 未知旗标明确报错 | `pi --nope` → `Error: Unknown option: --nope`，退出码 1 |

**没有验证的**（本节写作时不宣称）：交互式 TUI 的键位与渲染、`/login` 各 provider 的授权流程、
扩展加载、技能加载、TUI 组件、SDK 与 RPC 的实际调用、容器化与 Gondolin 隔离。这些要等到对应章节
按各自的过程实跑，并各自留下证据文件；在跑通之前，正文只用上游文档的边界表述，不写成"我试过"。

## 4. 钉版仓库的包地图

v1.5.0 是 monorepo，`packages/` 下 12 个包（`git ls-tree packages/` + 各 `package.json`）：

| 目录 | 包名 | 一句话 |
| --- | --- | --- |
| `ai` | `@earendil-works/pi-ai` | 多 provider 统一 LLM 接口，含模型自动发现与 provider 配置 |
| `agent` | `@earendil-works/pi-agent-core` | agent 运行时：工具调用、状态管理、transport 抽象 |
| `coding-agent` | `@earendil-works/pi-coding-agent` | 本书主角：CLI、会话、资源、四种接口 |
| `tui` | `@earendil-works/pi-tui` | 终端 UI 库，差分渲染 |
| `durable` | `@earendil-works/pi-durable` | 持久化的会话、任务与文档运行时 |
| `env` | `@earendil-works/pi-env` | 给 Durable 用的远程执行环境守护进程 |
| `mcp` | `@earendil-works/pi-mcp` | 独立的 MCP 客户端 |
| `codemode` | `@earendil-works/pi-codemode` | 沙箱里跑 JavaScript，唯一能力是调用注入的函数 |
| `chord` | `@earendil-works/chord` | 插件宿主运行时：契约、复制状态、JSON 链路上的 RPC |
| `schema` | `@earendil-works/pi-schema` | 不用 eval 的 JSON Schema 校验 |
| `telemetry` | `@earendil-works/pi-telemetry` | 与厂商无关的遥测契约与类型化 schema |
| `evals` | `@earendil-works/pi-evals` | 评测工具（`package.json` 无 description） |

安装到本机 npm 全局包里的内容只有 `dist/`、`docs/`、`examples/`、`schemas/` 和几个 Markdown；
**源码树不进书仓**。要读源码请按第 2 节的 tag 自己拉。

## 5. 复现命令

```bash
# 1. 拿钉版提交
git ls-remote https://github.com/earendil-works/pi.git refs/tags/v1.5.0

# 2. 拿 npm 上的 latest 与包元数据
curl -s https://registry.npmjs.org/@earendil-works/pi-coding-agent | \
  python -c "import json,sys; d=json.load(sys.stdin); print(d['dist-tags'])"

# 3. 只取钉版的树，不下载全部历史
git clone --depth 1 --branch v1.5.0 --filter=blob:none --no-checkout \
  https://github.com/earendil-works/pi.git
cd pi && git rev-parse HEAD && git ls-tree --name-only HEAD packages/

# 4. 本机版本
pi --version
```

期望：第 1 步打出 `f9a26365568127461c47a07a37dcb42c140a3ac5`，第 2 步 `{'legacy-node20': '0.74.2', 'latest': '1.5.0'}`，
第 3 步 `HEAD` 与第 1 步一致，第 4 步是 `1.5.0`（或你装的其他版本——不一致就按附录 E 处理）。

## 6. 漂移与更新

Pi 发版很快（`v1.1.0` 发布于 2026-10-07，`v1.5.0` 发布于 2026-11-02，不到一个月），所以：

- 读任何一章前先跑 `pi --version`。
- 上游改了什么，看仓库 releases 与 `CHANGELOG.md`；本机 `pi update` 更新自己。
- 本书改钉时，**改这一页、改附录 E、改受影响章节的核对清单**，三处一起改；只改正文不改这里，等于没有钉。
- 上次核对：2026-11-08，钉 `v1.5.0`。
