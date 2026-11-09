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
  yuyu-pi-zh.pdf: 9.0 MB, 164 pages, 41 bookmarks, 18 index folios
OK
{"output": "...yuyu-pi-zh.epub", "images": 72, "rasterized_svg": 102,
 "navigation_entries": 251, "bytes": 1251055}
```

| 产物 | 字节 | 页数 / 书签 | SHA-256 |
| --- | ---: | --- | --- |
| `yuyu-pi-zh.html` | 1,279,493 | 31 单元 | `1f2277b9fb48b4118b2eadfefce1c53529b687d350377d45897e29bb29cd6119` |
| `yuyu-pi-zh.pdf` | 9,433,650 | 164 页 / 41 书签 / 18 索引页脚 | `038fd2ed0ba9a741407e1da7b61b79bc74c5ca6b5b2639623dee3824cd13b2b3` |
| `yuyu-pi-zh.epub` | 1,251,055 | 251 个导航项 / 72 图 | `f83cb61318828e78fcfe1a8715ce2e45f354c449b220d9e8cbd482735267be9e` |

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
英文版。它们不在本轮"完成"的范围内，正文相应位置已标"未验证"。中文 EPUB 的构建与校验已记在上表。

## 8. 插件专项复核（2026-11-09）

Pi 1.5.0、pi-purge 0.2.1（提交 `ffafeb940339d59fc6af4a05dc754019cef3a1ac`）、Node 24.14.0。未修改全局设置、凭据或用户会话。

| 检查 | 方法与结果 | 输出 |
| --- | --- | --- |
| 上游原测试 | 复制固定版本的必要文件到工作区临时目录，运行 `node test/pi-purge.test.mjs`；9 组通过 | [purge-upstream.txt](facts/plugins-20261109/purge-upstream.txt) |
| 与真实宿主提示词组合 | `node pi/examples/check-purge.mjs <purge-dir> <pi-package>`；12 组通过 | [purge-compatibility.txt](facts/plugins-20261109/purge-compatibility.txt) |
| Git 状态工具 | `node pi/examples/check-git-status.mjs <pi-package>`；临时 Git 仓库、真实宿主 exec，6 组通过 | [git-status-tool.txt](facts/plugins-20261109/git-status-tool.txt) |

受限 Windows 环境执行后两项时加 `--preserve-symlinks`，避免 Node 在用户目录做 realpath 时被拒绝；不改变全局运行配置。测试脚本与用法见 [examples/README.md](examples/README.md)。

关键差异已经写入第 18 章：

- `replace` 对 Pi 1.5.0 真实默认提示词的两处旧标记均匹配失败，返回内容等于前置追加。
- 文档声称存在 `/purge reload`，该提交实际返回未知子命令；重新 `source` 或 `on` 才会读文件。
- `append` 不更新切除诊断，显示可能过期；`strict` 的匹配诊断也不能用来判断宿主内容是否保留。
- 旧标记部分匹配时独立删除，来源切换失败会尝试重新读取旧来源。

这些检查直接调用注册的处理器，没有真实提供方请求或 TUI 驱动。网络安装、交互菜单与模型行为改善仍未实测；上游测试里的模拟 prompt 是旧格式，9 组通过不能代替与 Pi 1.5.0 的组合检查。第 14 章重载与事件链、第 15 章默认工具激活规则另外依据宿主 1.5.0 的文档与实现核对。

## 9. 插件修订版的本机构建（2026-11-09）

执行 `python scripts/bookctl.py build --product pi --lang zh --pdf --epub --out-dir <本地输出目录>`，得到 HTML、PDF 和 EPUB。PDF 为 174 页、41 个书签，未发现无文本页；EPUBCheck 5.4.0 返回 0。第 18 章的模式对照、版本差异和第 15 章代码页已打开抽查。

`python scripts/bookctl.py check --fast` 六步通过，包括通用测试 67 项、构建器测试 529 项。Git 工具示例另用宿主类型声明做 TypeScript 严格检查，通过。上述页数与旧版第 7 节是不同时间的构建记录，不能互相替换。

接入最新主分支时，Pi 的 41 个行号引用已迁移成稳定块标识，共插入 39 个不可见标记；迁移报告无缺失或歧义。构建入口统一为 `scripts/bookctl.py` / `python -m yuyu_book`。同时修正中文段落样式误入 Mermaid 标签导致的文字裁切，最终输出以下一轮构建为准。
