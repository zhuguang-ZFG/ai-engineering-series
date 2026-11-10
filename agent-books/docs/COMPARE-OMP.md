# 对照阅读：《御舆》与《Omp 从入门到精通》

御舆侧的入口。同仓第二分册《Omp 从入门到精通：原理与实战》（下称 omp 分册）讲的是同一个题目域——
终端里的 agent harness——但**对象、钉版、读者起点都不同**。这本书不是那本书的简化版，那本也不是这本的剧透版。

逐章的对照关系只有一个真源：[`omp/overhaul/CROSSREF-MAP.md`](../omp/overhaul/CROSSREF-MAP.md)（33 行，
omp 章 → 御舆章 → 一句话同构点，并有机器校验）。本页只回答「我现在该读哪一本」，不复制那张表。
omp 分册自己的入口在 [`omp/README.md`](../omp/README.md)（书稿清单与写作进度），产物口径在
[`omp/BUILD.md`](../omp/BUILD.md)；双产品的机制与边界在 [`STRUCTURE.md`](../STRUCTURE.md) §3.6。

## 我该读哪一本

| 你的处境 | 先读 | 理由 |
|----------|------|------|
| 想知道 agent harness 为什么长成这样、想自己造一套 | 御舆 | 源码级解剖 + 第 15 章亲手装配一个最小 harness |
| 只想明天就能把 `omp` 用起来 | omp 分册 第一篇·第二篇 | 面向完全新手，先原理再实战，含安装、接模型、第一次对话 |
| 在用 Claude Code，想看它内部怎么转 | 御舆 | 御舆的对象就是 Claude Code 的 Agent Harness |
| 在用 `omp`（oh-my-pi），排障或读源码 | omp 分册 | 钉版是 `omp/18.15.0`，命令面与配置项按那本书查 |
| 两边都在用，想知道哪些概念是同构的 | 两本书的对应章（见下） | 同构点讲清，实现细节各自回自己那本 |
| 只想查一个术语的中文译名 | 见下面「译名分叉」 | 三处两本书不同名，抄错就串了 |

## 十个同构点（摘自对照地图，完整 33 行在原表）

| 概念 | 御舆 | omp 分册 | 同构在哪 |
|------|------|----------|----------|
| 模型 + 循环 + 工具 | 第 1 章 智能体编程的新范式 · 第 2 章 对话循环 | ch01 AI 编程 agent 到底在干什么 | 都在解释这一圈为什么不是补全 |
| 一次问答怎么跑完 | 第 2 章 对话循环 | ch06 第一次对话 | 一问一跑一拍，任务了结才停 |
| 写操作要过闸 | 第 4 章 权限管线 | ch09 改代码 · ch26 重构与大规模改动 | 大批量写操作的风险控制是同一层问题 |
| 上下文压缩 | 第 7 章 上下文管理 | ch15 压缩（compaction）与长任务 | 压缩阶梯是工作记忆的节流阀 |
| 长期记忆 | 第 6 章 记忆系统 | ch16 记忆系统 | 长期记忆与上下文窗口是两套东西 |
| 计划先行 | 第 14 章 Plan 模式 | ch13 计划与协作 · ch18 魔法关键词与模式 | 先规划后执行、主从分工 |
| 技能封装 | 第 11 章 技能系统与插件架构 | ch19 Skills | 能力封装单位的发现与加载 |
| 外部协议 | 第 12 章 MCP 集成与外部协议 | ch20 MCP | 同一份协议，不同的信任边界 |
| 生命周期扩展 | 第 8 章 钩子系统 | ch21 自定义工具与 Hooks | 钩子挂在同一层抽象上 |
| 把 harness 当接口 | 第 13 章 流式架构 · 第 15 章 构建你自己的 Agent Harness | ch28 SDK 与 RPC 入门 | 同一套循环，暴露成可编程入口 |

## 两本书不许互相搬的东西

对照地图开头写的铁律，这里重复一遍，因为它是最容易好心办坏事的地方：

- **御舆的数字不进 omp**：55 个工具、89 个 Flag、`QueryEngine` 这类实现名，都是御舆对自己对象的观察结果，
  写进 omp 就成了对 `omp` 的错误描述。互链只写「参见御舆第 N 章《标题》」。
- **omp 的专名不进御舆**：`hashline`、`mnemopi`、`acp`、`rpc`、`print-mode` 等 **21 个词只在 omp 的登记表里**
  （`yuyu-book/glosses-omp.json` 36 词，其中 15 个 id 与御舆重合）。审计口径见
  [`SHARED-TERMS.md`](yuyu-overhaul/SHARED-TERMS.md)：`glosses.json` 与 `notes.json` 里 `hashline`/`mnemopi`/`oh-my-pi`
  命中数 **0**；`manifest.json` 里那一条 `oh-my-pi` 是 ch04 导读引用的**来源 id** `gh-oh-my-pi`
  （钉 `v18.15.0` + 完整 commit），是引证，不是释义。
- **钉版不同**：御舆引 55 条来源、逐条钉 tag 或 commit；omp 分册只登记 2 条上游来源，写作钉 `omp/18.15.0`。
  发版很快，命令与数字以各自那本书的钉版为准，别拿一本的结论去回答另一本的问题。

## 译名分叉（三处，读跨书时最容易被绊到）

两本书的通俗层共用一套词，但下面三条的中文译名不一样。**各书在自己那一本里是自洽的**，
所以这里不改哪一本，只把分叉写明白：

| 登记表 id | 御舆 | omp 分册 | 怎么看 |
|-----------|------|----------|--------|
| `agent-harness` | 智能体**线束** | 智能体**外壳** | 「线束」取的是汽车线束那个词，跟前言「从造车到造 Agent」的比喻一路（书名「御舆」走的是车厢那一层）；「外壳」更直白。查词按你在读的那本 |
| `main-loop` | **主循环**（Main Loop） | **工作循环**（agent loop） | 同一圈「问一次模型、跑一轮工具、再问一次」，措辞不同，英文形式也不同（`Main Loop` vs `agent loop`） |
| `sub-agent` | 子智能体（`sub-agent`） | 子智能体（`subagent`） | 中文一致，只是英文连字符写法不同 |

其余 12 个共享 id 两侧 `term.zh` 与 `term.en` 完全一致（`context-window` 上下文窗口、`hook` 钩子、
`mcp-server` MCP 服务器、`memory` 记忆、`permission-pipeline` 权限管线、`plan-mode` 计划模式、
`prompt-cache` 提示缓存、`session` 会话、`skill` 技能、`snapshot` 快照、`system-prompt` 系统提示、
`tool-result` 工具结果）。逐词对照与复现命令在 [`SHARED-TERMS.md`](yuyu-overhaul/SHARED-TERMS.md)。

## 两本书的构建事实（同仓、两条独立入口）

| | 御舆 `product=book` | omp 分册 `product=omp` |
|--|--------------------|------------------------|
| 单元 | **20**（1 前言 + 15 章 + 4 附录） | **39**（1 前言 + 33 章 + 附录 A–E） |
| 语言 | 中英双语 | 仅中文（`langs: ["zh"]`，英文版延后） |
| 命令 | `make book` / `make book-pdf` | `make book-omp` / `make book-omp-pdf` |
| 产物 | `yuyu-agent-harness-{zh,en}.html/.pdf` | `yuyu-omp-zh.html/.pdf` |
| 通俗层 | 102 词条（core 44 / extra 58）、20 条按语、15 章档位表 | 36 词条（core 24 / extra 12）、39 条按语、33 章档位表 |
| 书末主题索引 | 有（`subject-index.json`） | **无**，`subject_index_registry` 显式写 `null` |
| 章徽 / 题刻 | 20 枚 / 4 枚（`yuyu-book/illustrations/` 43 张手写 SVG 可装配） | 0 / 0 —— 设计如此，且 `omp/illustrations/` 这个目录还不存在 |
| 门禁覆盖 | `make check`（`check --fast/--full`）验的就是它 | 不在 `check` 里；CI 走独立 `omp` job，不 `needs` 御舆 |

机制与边界见 [`STRUCTURE.md`](../STRUCTURE.md) §3.6；omp 侧构建口径与本机实测体积见
[`omp/BUILD.md`](../omp/BUILD.md)；两产品互不写文件的九条断言见
[`docs/yuyu-overhaul/TEST-CONTRACT.md`](yuyu-overhaul/TEST-CONTRACT.md)。

## 互链现在有多少

今天实测：`book → omp` **23** 条、`omp → book` **49** 条引用，坏链 **0**
（`python docs/yuyu-overhaul/check_crossrefs.py`）。注意「行数 / 引用条数 / HTML 短语出现次数」是
四个不同口径，别互相换算——原因与复现命令列在对照地图末尾那张四行表里。

## 两处已知缺口（写在这里免得被当成已存在）

1. 三份 SPEC 都把 `omp/FUSION-PLAN.md` 当作拍板依据引用，**该文件不在磁盘上**
   （`find . -iname "*FUSION-PLAN*"` 命中 0 条；注意别用 `*FUSION*` 去查，它会撞上 `video/**/error-diffusion.mjs`
   那类无关文件）。本页所有结论改从可量的地方取：两份 manifest、两份登记表、Makefile、workflow YAML、
   对照地图与护栏脚本的输出。
2. omp 侧的镜像入口 `omp/COMPARE-YUYU.md`（omp SPEC 的 M6 格）**尚未落盘**，所以这里不给链接，
   免得读者点开 404；它写好后与本文件互指即可。
