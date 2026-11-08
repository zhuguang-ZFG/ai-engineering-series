# Pi 分册：本机验证记录

- 机器：Windows（原生，非 WSL），工作目录 `D:\Temp\User`（除特别注明）
- 环境：Node `v24.14.0`，npm `11.9.0`，Pi `1.5.0`
- 时间：2026-11-08 20:4x（Asia/Shanghai），对应 UTC `12:4x`
- 原则：**只记录真跑过的命令和真看到的输出**。没跑的一律进第 5 节，不写成"已验证"。
- 原始输出切片：`facts/pi-1.5.0/`（版本、帮助工具段、print、JSON 头、模型目录、错误行为）；
  正文引用这些结论时，以切片文件为准。

## 1. 身份与环境

```console
$ pi --version
1.5.0

$ which pi
/c/Users/<user>/.pi/agent/bin/pi   # 用户名已隐去

$ node --version
v24.14.0

$ npm --version
11.9.0
```

`which pi` 指向 `~/.pi/agent/bin/pi` 的包装脚本（本机路径），不是 npm 全局 bin。
这与写作钉一致；`PIN.md` 第 3 节引用的就是这次输出。

## 2. 帮助与内置工具

```console
$ pi --help; echo "exit=$?"
...（略）
Built-in Tool Names:
  read       - Read file contents
  bash       - Execute bash commands
  powershell - Execute PowerShell commands on Windows
  edit       - Edit files with find/replace
  write      - Write files (creates/overwrites)
  grep       - Search file contents (read-only, off by default)
  find       - Find files by glob pattern (read-only, off by default)
  ls         - List directory contents (read-only, off by default)
exit=0
```

结论：帮助末段列 **8** 个内置工具名。默认启用的只有 **4** 个（`read`、`bash`、`edit`、`write`，
见 `docs/cli.md` 与源码 `packages/coding-agent/src/core/settings-manager.ts` 的 `DEFAULT_TOOL_NAMES`）；
`grep`、`find`、`ls` 标 `off by default`；`powershell` 只在原生 Windows 进程下可用，但不在默认列表里。

## 3. 请求与输出

### 3.1 文本模式，最短一圈

```console
$ ls ~/.pi/agent/sessions/--D--Temp-User-- | wc -l
2

$ pi --print --no-tools --no-session "只回复两个字：在线"; echo "exit=$?"
在线
exit=0

$ ls ~/.pi/agent/sessions/--D--Temp-User-- | wc -l
2
```

结论：stdout 只有 `在线`，stderr 为空；`--no-session` 前后会话文件数都是 2，确实没落盘。

### 3.2 JSON 模式

```console
$ pi --mode json --no-session --no-tools "只回复两个字：在线" 2>/dev/null | head -3
{"type":"session","version":3,"id":"01a1bb36-8a11-7077-9c3a-d582d9e06af7","timestamp":"2026-11-08T12:51:16.113Z","cwd":"D:\\Temp\\User"}
{"type":"agent_start"}
{"type":"turn_start"}
```

结论：JSON 模式**先打一条 session 协议头**，再打 agent/turn 事件；`--no-session` 只影响持久化，
不影响这条头。第 8 章据此展开事件流，不许把它写成"结果 JSON"。

### 3.3 会话落盘

去掉 `--no-session` 跑一次后（同一工作目录），sessions 目录多出一个文件：

```console
$ ls -t ~/.pi/agent/sessions/--D--Temp-User-- | head -1
2026-11-08T12-41-25-629Z_01a1bb2d-877c-77eb-af77-8ac80e10efa3.jsonl

$ head -2 <该文件>
{"type":"session","version":3,"id":"01a1bb2d-877c-77eb-af77-8ac80e10efa3","timestamp":"2026-11-08T12:41:25.629Z","cwd":"D:\\Temp\\User"}
{"type":"model_change","id":"17029d73","parentId":null,"timestamp":"2026-11-08T12:41:26.520Z","provider":"nvidia","modelId":"nvidia/nemotron-3.5-super-vl-120b-a12b"}
```

结论：文件按工作目录分目录；首行是会话头（`version: 3`），第二行是 `model_change`，之后还有
`thinking_level_change` 等条目（完整条目类型留给第 12 章）。默认模型是本次运行环境里配好的
`nvidia/nemotron-3.5-super-vl-120b-a12b`，不是本书推荐值。

## 4. 命令行错误行为

| 命令 | 实际输出 | 退出码 |
| --- | --- | --- |
| `pi --nope` | `Error: Unknown option: --nope` | 1 |
| `pi --model`（漏值） | `Error: Unknown option: --model` | 1 |
| `pi --provider nonexistent-provider "hi"` | `Error: --provider requires --model (for example: --provider nonexistent-provider --model <pattern>)` | 1 |
| `pi --print --no-tools --model definitely-not-a-model "hi"` | `Error: Model "definitely-not-a-model" not found. Use --list-models to see available models.` | 1 |
| `pi --list-models zzzznotfound` | `No models matching "zzzznotfound"` | **0** |
| `pi --thinking bogus --print ...` | `Warning: Invalid thinking level "bogus". Valid values: off, minimal, low, medium, high, xhigh, max`，随后正常回复 | **0** |

最后一行值得单独记：**"查不到"不是错误**，退出码仍是 0。脚本里用 `--list-models` 做能力探测时，
不能只看 `$?`。

## 5. 未验证清单

以下项目本次**没有**跑，正文里只按上游文档的边界描述，不宣称实测：

- 交互式 TUI：键位、鼠标、图片内联、`/hotkeys`、`/debug` 的实际输出
- `/login` / `/logout` 的 OAuth 与 API-key 流程（本机凭据是环境变量已配好的状态）
- `pi --continue` / `--resume` / `/tree` / `/fork` / `/clone` 的交互行为
- 扩展、技能、提示模板、主题的加载与生效
- SDK、RPC、JSON 事件流的完整消费
- 容器化、Gondolin、OpenShell 隔离
- 卸载与 `pi update`（没有在验证机上做破坏性操作）

这些在对应章节动笔前要各自补跑，并在这里追加"第 6 节：章节专项验证"。

## 6. 复跑方法

```bash
# 身份
pi --version && node --version && which pi

# 帮助与工具
pi --help | tail -12

# 最短一圈（不落盘）
pi --print --no-tools --no-session "只回复两个字：在线"

# JSON 协议头
pi --mode json --no-session --no-tools "只回复两个字：在线" | head -3

# 命令行错误
pi --nope; echo "exit=$?"
pi --model; echo "exit=$?"
pi --list-models zzzznotfound; echo "exit=$?"

# 非法思考档位（只 warning）
pi --thinking bogus --print --no-tools --no-session "只回复：OK"
```

复跑时若任一输出与上表不符，先记录实际输出与版本，再决定是改正文还是改钉版；
不要只改一处就宣布"验证过"。


## 7. 构建与成品（2026-11-08）

```console
$ python scripts/bookctl.py build --product pi --lang zh --pdf
[zh]
  yuyu-pi-zh.html: 1.2 MB, 31 units, 28 plates, 2 cited links, 218 glosses,
  31 lead bands, 156 tier chips, 31 emblems, 6 headpieces, 31 keeper notes
  yuyu-pi-zh.pdf: 9.0 MB, 161 pages, 41 bookmarks, 18 index folios
OK
{"output": "...yuyu-pi-zh.epub", "images": 67, "rasterized_svg": 97,
 "navigation_entries": 251, "bytes": 1048415}
```

| 产物 | 字节 | 页数 / 书签 | SHA-256 |
| --- | ---: | --- | --- |
| `yuyu-pi-zh.html` | 1,256,189 | 31 单元 | `df9f951fb05e49fd794f854db77db485e9ce26681e0084f69b3810804432509d` |
| `yuyu-pi-zh.pdf` | 9,053,128 | 161 页 / 41 书签 / 18 索引页脚 | `4f39e72f2b5fa58816821480849aa12bcbf1092748582cad6a5a6de58bc204f8` |
| `yuyu-pi-zh.epub` | 1,048,415 | 251 个导航项 / 67 图 | `89c38c19ef175c7773c44ccc401d2412201a2d26dfc27e4d71eedc44c058775d` |

- EPUB 走 `scripts/build_epub.py`：67 张图（含 97 个 SVG 光栅化）、251 个导航项；EPUBCheck 5.4.0：0 错误 0 警告。
- 28 张图 = 22 张 Mermaid + 6 张 ```ill 手绘长图；31 枚章徽 + 6 幅篇题刻由
  `scripts/draw_pi_illustrations.py` 生成，43 份全部通过 `art._read` 的字节/禁用项/currentColor 检查。
- 产品测试：`test_product_isolation`（14）+ `test_pi_product`（7）= 21 项通过；
  本分支全量：`yuyu-book/tests` 528 项、`tests` 67 项均 OK。
- PDF 首轮曾因路线图多出附录一行而触发空页门禁；print CSS 把 `.route-map .itinerary` 收到 88% 后，
  路线图与列表回到同一张纸。该规则对其他两册同样生效，属于排版修复而非 pi 特判。

主题索引：36 个词条，按附录 D 的章节列生成，`subject-index-pi.json` 与御舆的 `subject-index.json` 分开。

视觉抽查（程序化）：43 份 SVG 在 640×360 画布上均非空白，墨迹覆盖率 2.0%–8.1%，
边界框全部落在画布内；31 枚章徽与 6 幅正文长图在元素数（7–40）上有明显层级。
另用视觉模型复核了拼版图：6 幅正文长图的结构复杂度明显高于章徽，可读性通过；章徽有 5 处
线宽/对齐的小问题已在本轮修掉（钥匙齿、书脊折线、流水线居中、地图节点、天平底座）。

共享排版回归：同一 CSS 改动后重建 Omp 中文 PDF 为 **343 页 / 49 书签**（与此前记录一致）；
御舆双语本机为 518 / 569 页（README 的 520 / 559 是 CI Noto 口径，字体不同，不能直接对比），
三次构建都没有触发空页门禁。

**仍未验证**：交互式 TUI 键位、真实 `/login` OAuth、扩展项目信任交互、SDK/RPC 实跑、容器隔离、
英文版与 EPUB。它们不在本轮"完成"的范围内，正文相应位置已标"未验证"。
