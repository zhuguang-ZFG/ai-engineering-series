# omp 实装核对记录

- **日期**：2026-11-02 23:46 America/Adak（HST，UTC-10）
- **写作钉版本（书 / omp-src）**：18.15.0
- **用户本机验证版本**：18.16.0（见下文「用户本机核对」）
- **box 实验室版本**：`omp/18.15.0`（`omp --version`）
- **box 安装路径**：`/home/box/.local/bin/omp`（约 276785328 字节）
- **安装命令**：`curl -fsSL https://omp.sh/install | sh -s -- --binary --ref v18.15.0`（成功；未改用 bun）
- **PATH**：需含 `/home/box/.local/bin`
- **事实源**：本机二进制 + `omp-src/docs`（cli-reference、secrets、sdk、rpc）
- **原则**：文档与二进制不一致时，**以二进制行为为准**

## 1. box 实验室冒烟

| 命令 | 结果 |
|------|------|
| `omp --version` | `omp/18.15.0` |
| `omp --help` | 打印 USAGE / FLAGS / COMMANDS / 环境变量说明 |
| `omp completions bash` | 生成 bash 补全脚本（含 `_omp_root`） |
| `omp completions zsh` | 生成 zsh `#compdef omp` 脚本 |
| `omp --license` | 打印 MIT 与第三方声明开头 |
| `omp models` | `No models available. Set API keys…`（无密钥，预期） |
| `omp -p "ping" --no-session` | **阻塞**：无默认模型；提示 `/login` 或设置 `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` / `GEMINI_API_KEY` 等，或写 `~/.omp/agent/models.yml`。环境无相关 API key。**未编造跑通。** |

## 2. 扩展旗标

| 项 | 结果 |
|----|------|
| `--no-extensions` | 出现在 `--help`；与 `-p` 联用可解析到「无默认模型」阶段（本地 CLI 接受） |
| `--trusted-extension` | **不在** `--help` 正文；缺值报错：`Error: --trusted-extension requires a non-empty, non-flag value` → 二进制认识 |
| cli-reference | 记载白名单语义：可重复绝对路径；禁用环境发现；不可与 `-e`/`--extension`/`--hook` 同用 |
| RPC + `--no-extensions` | `omp --mode rpc --no-session --model openai/gpt-4o --no-extensions` 仍能打出 `{"type":"ready",…}`（无需有效 API key 即可握手） |

## 3. secrets（文档行为，未写出口令）

对照 `docs/secrets.md` 与书第31章 / 附录 C、D：

- 默认关闭；`config.yml` 中 `secrets.enabled: true`
- 模式：`obfuscate`（默认可逆）/ `replace`（不可逆）
- 路径：全局活动 agent 目录 `secrets.yml`（常 `~/.omp/agent/secrets.yml`）；项目 `<cwd>/.omp/secrets.yml`
- **无** `omp secrets` 子命令（输入后落入主帮助/无模型提示）；取凭据用 `omp token <provider>`（有独立 `--help`）
- 本书相关表述与 secrets.md 一致；本机未启用、未写入真实密钥

## 4. SDK / RPC

| 项 | 结果 |
|----|------|
| SDK | `docs/sdk.md`：`createAgentSession` 自 `@oh-my-pi/pi-coding-agent`；Quick start 形态与 ch28 一致。源码树存在导出与 examples。本机**未** `bun install` 跑通嵌入（无 API key；跳过联网模型） |
| RPC | `omp --mode rpc --no-session --model openai/gpt-4o` 输出 ready 帧：`protocolVersion:1`，`supportedProtocolVersions:[1,2]`。无 `--model` 且无密钥时可能直接「No default model selected」 |
| `--mode` 帮助摘要 | `text` / `json` / `rpc` / `rpc-ui` |
| `--mode acp` | 帮助未列；二进制接受并进入类 RPC 就绪帧；亦有子命令 `omp acp`。cli-reference Output modes 表含 `acp` |

## 5. cli-reference 旗标 vs `--help`

二进制**接受**但 `--help` **未列**（或仅间接出现）的抽样：

| 旗标 | 探针 |
|------|------|
| `--fork` | 与 `--no-session`：`Error: --fork requires session persistence`（与书附录 A「需持久化」一致） |
| `--session`（resume 别名） | 与 `--no-session`：映射为 resume 持久化错误 |
| `--provider-session-id` / `--prompt-cache-key` | 可过解析，落到「无默认模型」 |
| `--trusted-extension` | 见上 |

附录 A 表中的 continue/resume/restore/fork 约束与二进制探针一致。

## 6. 差异条目与是否改书

| ID | 差异 | 是否需改书 | 处置 |
|----|------|------------|------|
| D1 | `--help` 为常用摘要，漏列若干 launch 旗标；cli-reference 更全；二进制仍解析 | 是 | 已改 `appendix-A.md`：冲突原则、漏列说明、A.5/A.6/A.7/A.8 |
| D2 | 第31章开篇强调「信任扩展」但未写 `--trusted-extension` 白名单 | 是 | 已改 `ch31.md`：开篇、31.2 段落后补白名单、清单与版本核对 |
| D3 | `--mode`：帮助四值 vs cli-ref/`--mode acp` | 是（附录） | 已写入 `appendix-A.md` A.6 |
| D4 | `omp -p` 需鉴权 | 否（环境） | 记录阻塞；跳过需联网模型项 |
| D5 | secrets / SDK Quick start / `--no-extensions` 语义 | 否 | 与 omp-src 及二进制一致 |

## 7. 复验命令

```sh
export PATH="$HOME/.local/bin:$PATH"
omp --version                    # box 期望 omp/18.15.0；用户本机见下节 18.16.0
omp --help | head
omp completions bash | head
omp -p 'ping' --no-session       # 无密钥时期望 No default model…
omp --trusted-extension          # 期望 requires a non-empty…
omp --fork x -p y --no-session   # 期望 requires session persistence
omp --mode rpc --no-session --model openai/gpt-4o --no-extensions
# Ctrl+C 于 ready 帧后；期望首行 type=ready
```

鉴权具备后可再验：`omp -p "只回复 pong" --no-session`；SDK Quick start（ch28）。

## 8. 改动文件清单

- `appendix-A.md`（核对修订）
- `ch31.md`（核对修订）
- `VERIFY.md`（本文件，新建）
- 压缩包：`/workspace/omp-book-full.tar.gz`（排除 `omp-src`、`handraw-style`）

---

## 用户本机核对（Windows · 朱光 desktop）

- **日期**：2026-11-02 晚 America/Adak（对应 UTC 2026-11-03）
- **环境**：Windows · PowerShell；**未**使用 curl/install.ps1 预编译脚本路径
- **安装形态**：Bun 全局包装（`bun install -g @oh-my-pi/pi-coding-agent` 一类）；Bun **1.4.4**
- **可执行文件路径**：`%USERPROFILE%\.bun\bin\omp.exe`（展开就是本机 `C:\Users\<用户名>\.bun\bin\omp.exe`；本机账户名不入书稿）
- **版本**：`omp/18.16.0`（高于本书写作钉 **18.15.0**；页边以本机为准）
- **配置目录**：`~/.omp/agent` 已配置（含 models / skills / extensions 等；**不记录** models.yml 内容与任何 API key）
- **providers（`omp models`，可写名）**：可见 `<私有网关甲>`、`<私有网关乙>`、`<私有网关乙-Anthropic>` 等（完整列表以本机为准）

### 实跑命令

| 命令 | 结果 |
|------|------|
| `omp --version` | `omp/18.16.0` |
| `omp models` | 正常列出上述等 providers |
| `omp token --help` / `omp auth --help` | 与书中 CLI 叙述一致 |
| `omp -p "只回复两个字：在线"` | 输出「在线」（已通；需本机已配模型/鉴权） |

### 与写作钉 / 实验室核对的关系

| 环境 | 版本 | 安装 | 联网模型 |
|------|------|------|----------|
| 书写作树 `omp-src` + 附录钉 | 18.15.0 | 文档事实源 | — |
| box 实验室（上文各节） | 18.15.0 | curl `--binary --ref v18.15.0` → `~/.local/bin/omp` | 无 key，`-p` 阻塞 |
| **用户本机（本节）** | **18.16.0** | **Bun 全局 → `.bun\bin\omp.exe`** | **`-p` 已通** |

升级说明：阅读本书实验时，优先记录本机 `omp --version`；若为 18.16.x 而书页仍写 18.15.0，属预期漂移，差异记附录 E 页边，**冲突以本机二进制为准**。

### 复验（PowerShell）

```powershell
omp --version
Get-Command omp | Format-List *
omp models
omp -p "只回复两个字：在线"
```

勿把 API key、`models.yml` 密钥字段、token 原文写入本书或本文件。

---

## 加厚期抽验（2026-11-03 · 改造 SPEC M1 Step 4）

执行者直接在本机跑（Bun 全局 `omp.exe`），全部原始输出落盘
`omp/facts/live-18.16.0/`，索引 `_manifest.tsv`（命令 · 退出码 · 字节 · UTC）。
采集脚本 `omp/overhaul/harvest_live.sh` 可重跑。

| 命令 | 结果 | 退出码 | 证据文件 |
|------|------|--------|----------|
| `omp --version` | `omp/18.16.0` | 0 | `version.txt` |
| `omp --help` | 全旗标 + EXAMPLES + **51** 个 COMMANDS | 0 | `help-top.txt` |
| `omp <子命令> --help`（**51** 条，逐条对过 COMMANDS 表） | 与 `help-top` 命令表一致 | 0 | `help-*.txt` |
| `omp -p "只回复两个字：在线" --no-session` | `Working...` → `在线` | 0 | `print-mode-online.txt`（UTC 11:06:08Z） |
| `omp models` | 正常列出 providers 与模型表 | 0 | `models-list.txt` **含私有网关名，仅本机留存，禁止入书稿** |
| `omp toks omp/README.md` | 离线分词计数 | 0 | `toks-self.txt` |
| `omp completions bash` | 打印补全脚本 | 0 | `completions-bash.txt` |

### 新登记的差异条目（翻车路径，18.16.0 实测）

| # | 命令 | 实际行为 | 与书页叙述的关系 |
|---|------|----------|------------------|
| D-01 | `omp --nopt` | `Error: unknown flag: --nopt` + `Run \`omp --help\` for available flags.` | 未知**旗标**会明确报错并退出 |
| D-02 | `omp -p "hi" --model definitely-not-a-model-xyz --no-session` | `Model "definitely-not-a-model-xyz" not found` + 提示 `omp models find <pattern>` | 未知**模型名**在发请求前就挡住 |
| D-03 | `omp notasubcommand` | **不报错**：整句被当作提示词送进模型，停在 `Working...`（本机 90s 超时截断） | 易被误读成「没有这个子命令」，实际是 positional MESSAGES 语义 |
| D-04 | `omp --model`（缺值） | **不报错**：同 D-03，`Working...` 挂住 | 缺值旗标被吞进提示词，是本机最值得写进翻车表的一条 |

D-03 / D-04 属行为语义而非 bug 断言：本节只记录「本机跑出什么」，
不推断上游是否有意为之。书稿引用这两条时须写「本机 18.16.0 实测」，
不得写成对 18.15.0 的断言。原始输出见 `fail/bad-command.txt`、`fail/missing-value.txt`。

### 加厚期第二批新登记（M1 · ch01–05 / ch16–20 实跑）

| # | 命令 | 实际行为 | 与书页/文档叙述的关系 |
|---|------|----------|------------------------|
| D-05 | `omp models find nomatch-xyz` | 退出 **0**，无输出行 | 书页若写「找不到就非零」需改；`--help` 未声明退出码语义 |
| D-06 | `omp config get modelRoles.default` | `Unknown setting: ...`，退出 **1** | `docs/settings.md` 把 `modelRoles.<role>` 写成可寻址点路径；本机只有整个 `modelRoles` 对象可取 |
| D-07 | `omp config get modelRoles` | 退出 0，**13** 个键（含 `memory`、`chore_worker`、`scout_worker`、`designer`…） | ch17 原表 8 行、文档点名的 `judge` 角色在本机不存在 |
| D-08 | `omp config get memory.backend` | 本机 `mnemopi` | 文档默认值写 `off`；页边须带「以本机为准」 |
| D-09 | `omp read memory://root` | 退出 **1** | 与 ch16 叙述一致，但成因是当前后端为 `mnemopi` |
| D-10 | `omp read skill://hello`（`.omp/skills/hello/SKILL.md` 已就位） | `Unknown skill: hello` | 项目级技能在 shell 侧的解析时机**未验证**，正文不得解释成因 |
| D-11 | `omp --help` 的 COMMANDS 全表 | **没有** `omp mcp` / `omp memory` 子命令，也没有 MCP 旗标 | ch20「具体旗标为准」与 ch16 的 CLI 形 `/memory` 行是错误命令形状，已删 |
| D-12 | `omp config get tools.approval` / `tools.approvalMode` | `tools.approval: bash allow` 会盖过 `tools.approvalMode: always-ask` | ch18 原「审批模式即门禁」不成立 |
| D-13 | 在 PowerShell 与 cmd.exe 分别敲 `omp-not-a-real-command-zzz` | PowerShell：`无法将"omp"项识别为…`；cmd：`…不是内部或外部命令` | ch04 原文把两种文案混为一谈，已分开 |
| D-14 | `omp -p … --no-tools` | 未能确定语义 | 正文标 **未验证**，并给读者自查命令 |

以上退出码与文案均出自本机 `omp/18.16.0`；原始输出在 `omp/facts/live-18.16.0/`
（含 `fail/` 子目录）与 `_manifest.tsv`。**任何一条都不得写成对 18.15.0 的断言**，
上游若改行为，以读者本机为准。

### 复跑（Git Bash / PowerShell 两版）

```bash
bash omp/overhaul/harvest_live.sh            # 重采 help 与只读命令
omp -p "只回复两个字：在线" --no-session      # 带模型，会产生 API 消耗
```

仍**禁止**把 `omp token` / `omp auth` / `omp usage` 的真实输出写进本节或书稿；
它们的 `--help` 已采集（`help-token.txt` 等），够正文引用。

