# 《Omp 从入门到精通：原理与实战》全书大纲（草案 v0.1）

> Omp = oh-my-pi（命令 `omp`），开源终端 AI 编程 agent，作者 Can Bölük（can1357），Stencil Labs 出品，fork 自 Mario Zechner 的 Pi。仓库：https://github.com/can1357/oh-my-pi ，官网 https://omp.sh 。写作钉版本 v18.15.0（2026-11-01，依据当时 omp-src/docs）。用户本机验证 v18.16.0（Windows · Bun 全局，见 VERIFY.md）。项目迭代极快（600+ 个 release），书中数字、命令以写作钉为准并对照本机 `omp --version`；每章末附“版本核对清单”。
>
> 配图统一用 handraw-style 画风 FA-023（极简钢笔线 + 留白）+ 主题色 C-25 爱马仕橙；概念图走手绘，截图与表格保持真实。每章约 3–6 张图。

## 第一篇 打地基：先弄懂 agent 是什么（原理）
**第1章 AI 编程 agent 到底在干什么**（样章）
- 聊天机器人 vs agent：差别在“能动手”
- Agent = 模型 + 工具 + 循环；一轮对话里发生的事
- 为什么同一个模型换个“壳”（harness）成绩差很多：omp 的 edit 格式实验数据
- omp 在家族谱里的位置：Pi → oh-my-pi
- 配图：agent 循环图；聊天 vs agent 对比图；harness 与模型的“骑手和马”图

**第2章 大模型的最小必要知识**
- token、上下文窗口、为什么会“忘”；推理强度（thinking）
- 工具调用的本质：模型输出一段结构化请求，程序替它执行
- 配图：上下文窗口当书桌；工具调用信封往返

**第3章 omp 的整体架构**
- 四种入口：TUI、`omp -p`、SDK、RPC/ACP——同一个引擎
- monorepo 拆解：pi-ai / pi-agent-core / pi-coding-agent / pi-tui / natives(Rust)
- 为什么把 grep、glob、shell、AST 解析做成进程内原生实现
- 配图：引擎与四个外壳；包依赖手绘地图

## 第二篇 上手：从安装到第一次让它改代码
**第4章 安装与环境**：curl 脚本 / Homebrew / Bun / Nix / Windows PowerShell；Bun ≥1.4.4；Windows 上 Bun 全局常见路径 `%USERPROFILE%\.bun\bin\omp.exe`；shell 补全；常见安装失败（Alpine 缺 libstdc++ 等）。配图：安装路线选择树。
**第5章 接上模型**：60+ provider、订阅制 coding plan、本地模型（llama.cpp 等）、自定义 OpenAI 兼容端点；`/model` 切换。配图：provider 插座板。
**第6章 第一次对话**：TUI 界面逐区讲解、工具卡片、edit 预览后再落盘、`ask` 选项框。实战：让它给一个小项目加一个函数和测试。配图：TUI 标注图（真实截图 + 手绘批注）。
**第7章 会话管理**：会话树、fork、resume、export/share、`/fresh`。配图：会话像 git 分支。

## 第三篇 工具箱：逐个吃透内置工具（原理 + 小实验）
**第8章 读与找**：read（文件/目录/PDF/URL/ssh://）、grep、glob、ast_grep
**第9章 改代码**：edit 的 hashline（按内容哈希锚定）原理、为什么比 str_replace 稳；ast_edit
**第10章 跑起来**：bash（进程内 coreutils、PTY、后台任务）、eval（持久 Python/JS 内核）
**第11章 像 IDE 一样懂代码**：lsp（写入即诊断）、debug（DAP 断点单步）
**第12章 浏览器、桌面与联网**：browser、computer、web_search、github
**第13章 计划与协作**：todo、ask、task 子代理、wait
- 每章配图：工具“工作台”手绘；hashline 锚点示意；子代理分叉图

## 第四篇 让它更聪明：上下文、记忆与模型路由
**第14章 上下文文件与规则**：AGENTS.md 等、自动继承 .claude/.cursor/.codex 等目录配置
**第15章 压缩（compaction）与长任务**
**第16章 记忆系统**：retain/recall/reflect、mnemopi 本地 SQLite
**第17章 模型角色路由**：default / smol / slow / plan / commit / vision / task / advisor / tiny；advisor 第二模型监督
**第18章 魔法关键词与模式**：ultrathink、orchestrate、workflowz；/vibe；plan 模式；审批模式

## 第五篇 扩展：把 omp 改成你的形状
**第19章 Skills**：SKILL.md 结构、发现规则（skills/<name>/SKILL.md 一层）、`skill://`、`/skill:<name>`
**第20章 MCP**：配置、传输方式、项目级 .mcp.json 与信任
**第21章 自定义工具与 Hooks**
**第22章 Extensions**：TypeScript 工厂函数、注册工具/命令/快捷键、`/reload-plugins`、marketplace
**第23章 配置与 profile**：~/.omp/agent、项目 .omp、`--profile`、环境变量、主题与快捷键

## 第六篇 实战项目（每章一个完整案例，从需求到交付）
**第24章** 接手陌生代码库：读懂、画架构、写文档
**第25章** 修一个真实 bug：复现 → debug 工具断点 → 修复 → 测试
**第26章** 重构与大规模改动：ast_edit + 子代理并行
**第27章** 代码评审与 `omp commit` 原子提交
**第28章** 用 SDK / RPC 把 omp 嵌进自己的程序
**第29章** 写一个团队用的 skill + extension 并发布

## 第七篇 精通：排错、安全与成本
**第30章** 排错手册：安装、认证、provider 报错（429/配额）、LSP 不工作、会话卡住（按症状索引）
**第31章** 安全与信任边界：打开仓库会加载哪些东西、`--no-extensions`、密钥管理
**第32章** 成本与性能：token 统计（omp-stats）、模型选择、缓存
**第33章** 读源码：从入口追一轮对话的完整调用链

## 附录
A 命令行参数速查 · B 斜杠命令速查 · C 配置项速查 · D 术语表（中英对照）· E 版本变更追踪方法

## 写作规范（去 AI 味）
- 每节先给一个具体场景/故障，再讲原理；不写“总之”“值得注意的是”“不仅…更…”类套话
- 所有命令在真机上跑过再写，跑不通的标“未验证”
- 用 humanizer / Humanizer-zh 做终稿自检
