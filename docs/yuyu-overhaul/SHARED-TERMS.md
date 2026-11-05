# 丛书共享词表（御舆 ↔ Omp）

SPEC M7 Step 2 的产物。回答三个问题：**哪些词两本书都在用**、**同一个词在两本书里译成了什么**、
**哪些词是 omp 专名、不许进御舆的释义**。

采用「若暂不接线构建」那条路线：本文件是 `docs/yuyu-overhaul/` 下的人工对照表，**不是**
`yuyu-book/glosses-shared.json`。两本书的构建器各读自己的登记表（御舆 `glosses.json`、
omp `glosses-omp.json`，由 `plain.registry_names()` 按 `manifest.product` 选名），
词表没有第三份文件参与装配，所以改这里不会动任何产物 —— 也意味着这里的一致性要靠跑下面的审计。

## 一、总数（2026-11-04 实测）

| | 御舆 | omp |
|---|---|---|
| 登记表 | `yuyu-book/glosses.json` | `yuyu-book/glosses-omp.json` |
| gloss id 条数 | **102** | **36** |

两边 id 的重叠：**15 条共享**、御舆独有 **87 条**、omp 独有 **21 条**。
共享的 15 条里，中英两个字段（`term.zh` 与 `term.en`）完全一致的有 **12 条**，有分歧的 **3 条**。

## 二、共享词（≥20）

「概念」行按 SPEC 点名的词优先。前 15 行两本用的是同一个 gloss id；后 7 行同一个概念在两本书里
登记成了两个不同的 id，所以两列都写出来。

| # | 概念 | 御舆 gloss id | omp gloss id | 御舆译名（zh / en） | omp 译名（zh / en） | 状态 |
|---|---|---|---|---|---|---|
| 1 | agent-harness | `agent-harness` | `agent-harness` | 智能体线束 / Agent Harness | 智能体外壳 / Agent Harness | 分歧 · 见 §四 |
| 2 | main-loop | `main-loop` | `main-loop` | 主循环 / Main Loop | 工作循环 / agent loop | 分歧 · 见 §四 |
| 3 | subagent | `sub-agent` | `sub-agent` | 子智能体 / sub-agent | 子智能体 / subagent | 分歧（仅 en 拼写）· 见 §四 |
| 4 | context-window | `context-window` | `context-window` | 上下文窗口 / context window | 上下文窗口 / context window | 一致 |
| 5 | hook | `hook` | `hook` | 钩子 / hook | 钩子 / hook | 一致 |
| 6 | skill | `skill` | `skill` | 技能 / skill | 技能 / skill | 一致 |
| 7 | mcp | `mcp-server` | `mcp-server` | MCP 服务器 / MCP server | MCP 服务器 / MCP server | 一致 |
| 8 | permission | `permission-pipeline` | `permission-pipeline` | 权限管线 / permission pipeline | 权限管线 / permission pipeline | 一致 |
| 9 | system-prompt | `system-prompt` | `system-prompt` | 系统提示 / system prompt | 系统提示 / system prompt | 一致 |
| 10 | tool-result | `tool-result` | `tool-result` | 工具结果 / tool result | 工具结果 / tool result | 一致 |
| 11 | plan-mode | `plan-mode` | `plan-mode` | 计划模式 / plan mode | 计划模式 / plan mode | 一致 |
| 12 | memory | `memory` | `memory` | 记忆 / memory | 记忆 / memory | 一致 |
| 13 | session | `session` | `session` | 会话 / session | 会话 / session | 一致 |
| 14 | prompt-cache | `prompt-cache` | `prompt-cache` | 提示缓存 / prompt cache | 提示缓存 / prompt cache | 一致 |
| 15 | snapshot | `snapshot` | `snapshot` | 快照 / snapshot | 快照 / snapshot | 一致 |
| 16 | compaction | `auto-compact` | `compaction` | 自动压缩 / auto-compact | 压缩 / compaction | 两个 id · 各书自洽 |
| 17 | permission（档位） | `permission-mode` | `yolo` / `approval` | 权限模式 / permission mode | 全放开模式 / yolo mode；审批 / approval | 两个 id · 不同切分 |
| 18 | permission（判断者） | `permission-classifier` | `approval` | 分类器 / classifier | 审批 / approval | 两个 id · 别混用 |
| 19 | transcript | `transcript` | `session` | 会话记录 / transcript | 会话 / session | 两个 id · 御舆把记录与会话分开 |
| 20 | 项目说明文件 | `claude-md` | `agents-md` | CLAUDE.md / CLAUDE.md | 项目说明文件 / AGENTS.md | 两个 id · 指不同文件，**不可互译** |
| 21 | 扩展 | `plugin` | `extension` | 插件 / plugin | 扩展 / extension | 两个 id · 各书自洽 |
| 22 | token 计数 | `token-budget` | `toks` | Token 预算 / token budget | token 计数 / toks | 两个 id · 说的是两件事 |

SPEC 点名的 10 词里，`tool-call` **两边都没有这个 id**（0 命中）。最近的登记是共享的
`tool-result`（工具结果）与御舆独有的 `deferred-tool-discovery`。这一格留空而不是硬凑一个 id：
「工具调用」在御舆是第 2、3 章的行文用词，没进通俗层登记表；omp 同理。

## 三、omp 专名：不许进御舆的释义（21 条）

下面这些 id 只在 `glosses-omp.json` 里。御舆的 gloss 条目拿它们当「本词释义」就是污染 —— 读者手上是御舆，
`hashline`、`mnemopi`、`toks` 这些名字对他没有上下文。

`acp`（编辑器协议）、`agents-md`（项目说明文件）、`approval`（审批）、`background-task`（后台任务）、
`compaction`（压缩）、`context-file`（上下文文件）、`diagnostics`（诊断）、`extension`（扩展）、
`hashline`（哈希行锚）、`mnemopi`（本地记忆库）、`modelroles`（模型角色）、`print-mode`（打印模式）、
`profile`（配置档）、`rpc`（帧协议接口）、`secrets-mask`（秘密遮罩）、`skill-uri`（技能读取地址）、
`slash-command`（斜杠命令）、`subcommand`（子命令）、`toks`（token 计数）、`trusted-extension`（可信扩展）、
`yolo`（全放开模式）。

反向清单同样成立但不列在这里：御舆独有的 87 条（`async-generator`、`backpressure`、`circuit-breaker` 一类
计算机科学词，和 `claude-md`、`permission-classifier` 一类实现名）不得成为 omp 章的释义。
omp 侧的口径写在各分册的门禁里，两边各管各的登记表。

## 四、三处分歧：本轮不定夺

分歧只在 `term` 字段，两本书内部各自前后一致，产物里不会自相打架。所以这不是 bug，是一个待拍板的选择：
要不要为「丛书读起来像一套话」把译名对齐（改哪一本、还是给同一 gloss 加别名）。
下面每行都抄两边登记表里的原文，可对着 §六 的命令复核。

1. **agent-harness** —— 中文「智能体线束」（御舆）/「智能体外壳」（omp），`term.en` 两边都是 `Agent Harness`。
   通俗层释义也各自扣了不同角度：御舆写「把模型包在中间的那层程序：接需求、发工具、收结果」，
   omp 写「模型外面那圈程序：递工具、管上下文、跑循环」。「线束」扣布线、「外壳」扣包裹，两个都比直译好，也都能自圆。
   标记点：御舆在前言与第 1 章（`front.b-e3677d71`、`ch01.agent-harness`），omp 在 `omp/ch01.md:51`。
2. **main-loop** —— 御舆「主循环 / Main Loop」且 `forms` 里中英文都同时收着带大写和不带大写两种写法
   （`Main Loop`、`main loop`），标记点在前言、第 2 章、附录 D；omp「工作循环 / agent loop」，
   `forms.zh` 只有「工作循环」一项，标记点在 `omp/ch01.md:21`。
   这是三处里语义差别最大的一处：御舆讲的是它自己那圈「问一次 → 跑一轮工具 → 再问一次」的装配次序，
   omp 用的是它那个实现里帮助文本里的说法。
3. **sub-agent** —— 中文两边 `term.zh` 都是「子智能体」，只有 `term.en` 不同（`sub-agent` vs `subagent`）。
   御舆的 `forms.en` 收了 `sub-agent` / `Sub-agent` / `sub-agents` / `Sub-Agent` 四种，**不含连写形式**；
   omp 的 `forms.zh` 另收「子代理」。所以「对齐」不是改一个字段：真改要连 forms 一起过一遍，否则正文命中会掉。
   这条最接近可以关掉，但目前没人管它，`check` 也不管。

我的建议（供你拍板，不自行执行）：**保持各书自洽**，把三处分歧就按上面这样写进对照表。
理由是这三处反映的是两本书各自的描述对象，强行统一会让某一本书的正文用词和它的 gloss 打对台。

## 五、污染审计（M7 Step 3）

Python 一条命令跑全部三边（口径和 SPEC 给的 `Select-String` 一致，但 PowerShell 的引号转义在这台机器上不可靠）：

```bash
cd claude-code-book-main
python - <<'PY'
import json, pathlib, re
rx = re.compile("hashline|mnemopi|oh-my-pi", re.I)
hits = lambda p: [f"{n}:{l}" for n, l in enumerate(
    pathlib.Path(p).read_text(encoding="utf-8").splitlines(), 1) if rx.search(l)]
for f in ("glosses.json", "notes.json", "manifest.json", "sources.json", "revisions.json"):
    print(f, len(hits("yuyu-book/" + f)), hits("yuyu-book/" + f)[:1])
PY
```

2026-11-04 的读数：

| 位置 | 命中 | 判定 |
|---|---|---|
| `yuyu-book/glosses.json` | **0** | 通过 —— 御舆的释义层没有 omp 专名 |
| `yuyu-book/notes.json` | **0** | 通过 |
| 御舆正文（`00-前言.md`、四个篇章目录、`附录/`、`en/`）里 `hashline` / `mnemopi` | **0** | 通过 |
| `yuyu-book/manifest.json:436` | 1 | 合法 —— 是来源 id `gh-oh-my-pi`（不是词表项） |
| `yuyu-book/sources.json:932–938` | 6 | 合法 —— 登记 `https://github.com/can1357/oh-my-pi`，钉版本、MIT |
| `yuyu-book/revisions.json` | 6 | 合法 —— 0.3.x 修订说明里记的对照面回填事实 |

后三行正是 SPEC 留的那个口子（「仅在明确『对照』字段」）：`oh-my-pi` 作为**被引用的上游项目**注册进来源表、
被第 4 / 7 / 14 章的罗盘引用，这和拿 `hashline` 当御舆某个词的释义是两回事。
正文里 `oh-my-pi` 出现在 6 个文件（中英各 3 章：第 4、7、14 章），全部是 §4.3.6 / §7.x / §14.1.1 那几段对照面。

## 六、复现本表的数字

```bash
cd claude-code-book-main
python - <<'PY'
import json, pathlib
P = pathlib.Path("yuyu-book")
def terms(n):
    r = json.loads((P / n).read_text(encoding="utf-8"))
    return {k: v for k, v in r.items() if k != "schema_version"}
gb, go = terms("glosses.json"), terms("glosses-omp.json")
sh = sorted(set(gb) & set(go))
ident = [i for i in sh if gb[i]["term"] == go[i]["term"]]
print(len(gb), len(go), "shared", len(sh), "identical", len(ident),
      "diverge", len(sh) - len(ident), "omp-only", len(go) - len(sh))
for i in sh:
    b, o = gb[i]["term"], go[i]["term"]
    print(("SAME" if b == o else "DIFF"), i,
          b.get("zh"), "/", b.get("en"), "|", o.get("zh"), "/", o.get("en"))
PY
```

登记表是**扁平 dict 按 id 键**（除 `schema_version` 外每个键就是一条 gloss，字段为
`term` / `forms` / `plain` / `priority` / `evidence` / `analogy` / `why` / `why_evidence`）——
按 `groups → terms` 去读会拿到空表，我第一次就这么读错了。

## 七、如果以后要接成第三份登记表

把本表变成 `yuyu-book/glosses-shared.json` 需要同步改四处，缺一个就是哑火或红灯：

1. `yuyu-book/yuyu_book/registry.py:24` 的 `FILES` 白名单 —— 不在里面的文件名 `registry.load()` 直接拒（`registry.py:95`）。
2. `yuyu-book/yuyu_book/plain.py:72` `registry_names()` 只派生 `-omp` 同名字，没有「第三产品」的位置；
   真接的时候要让两本书各自的装配路径多读一份，而不是改 `product` 的取值。
3. `yuyu-book/tests/test_product_isolation.py` —— 现在有一条断言是「除这两份 manifest 外没有别的测试读 omp 清单」，
   新登记表面向两个产品，这条扫描口径要跟着定清楚。
4. `yuyu-book/tests/test_docclaims.py` 的套件数护栏 —— 新增测试会把条数抬起来，
   同一轮必须改 `revisions.json` 最新条里的「构建器测试 N 项全绿」与 `N builder tests green`。

在那之前，本文件的审计口径靠 §五 那条命令复核。**目前没有自动化断言管「御舆 gloss 的释义里出现 omp 专名」这件事**：
M6 的 `test_product_isolation.py` 九条断言管的是单元数、登记表名、产物名、清单里的 `langs` 与
`subject_index_registry`，与词表内容无关；`test_plain.py` 管通俗层自己的形状（标记、章末面板、阅读档位）；
`test_docclaims.py` 只钉 `README.md` / `en/README.md` / `STRUCTURE.md` / `CREDITS.md` 四份文档里报出的数字，
`docs/yuyu-overhaul/` 下的文件不在它的清单内 —— 也就是说本文件开头那两个条数（102 / 36）**没有护栏**，
改了登记表要自己回来对。这一层现在是「命令可复现 + 人工 review」，写在这里就是为了下一轮不用重新猜口径。
