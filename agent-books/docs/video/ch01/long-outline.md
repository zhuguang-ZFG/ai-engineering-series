# 第 01 章长讲大纲｜驭者·Agent Harness

> 成片目标：B 站横屏 15–20 分钟  
> 书稿源：第一部分-基础篇/01-智能体编程的新范式.md  
> 口播：沉稳男声；动画须带书稿真实模块名与数字

## 时间轴总览

| 块 | 标题 | 预估 | 累计 |
|----|------|------|------|
| 1 | 开场钩子 | 0:45 | 0:45 |
| 2 | §1.1 范式转移 | 4:00 | 4:45 |
| 3 | §1.2 全景架构 | 5:00 | 9:45 |
| 4 | §1.3 五大原则 | 6:00 | 15:45 |
| 5 | 实战练习速览 | 2:00 | 17:45 |
| 6 | 总结 + 片尾出处 | 1:00 | 18:45 |

预估总时长约 **18 分 45 秒**（落在 15–20 分钟区间）。

---

## 块 1｜开场钩子（约 45s）

**口播要点**
- 对比：Chatbot 时代人类当「胶水」——复制粘贴、切终端、把报错贴回对话框
- 对比：Agent 时代 LLM 自己编排工具调用
- 抛出本集问题：为什么不能只写一层 API 封装？为什么需要 Agent Harness？

**画面 / 标记**
- [ANIM:chatbot-glue] 左右分屏：左边人手工搬运 Prompt/Response；右边 Agent 自动调度工具
- 系列名条：驭者·Agent Harness · 第 01 讲
- 章号徽章：01

---

## 块 2｜§1.1 范式转移（约 4min）

**口播要点**
1. LLM 作为对话伙伴 vs 推理引擎（2023 → 2024 认知转变）
2. Tool Use（工具调用）打开边界；六大工程挑战：注册与发现、参数校验、权限管控、错误恢复、状态一致性、并发与调度
3. 简单封装 = while 循环假设理想世界；Harness = 流式、权限、上下文、恢复、持久化、可扩展
4. 一句话定义 Harness；反模式警告：裸 while 循环

**专有名词首次中英**
- 提示词 Prompt
- 工具调用 Tool Use
- Agent Harness（智能体缰绳 / 运行时框架）

**画面 / 标记**
- [ANIM:llm-roles] 参谋口述 vs 指挥官调度
- [ANIM:six-challenges] 六大挑战汇入 Harness 中心
- [ANIM:car-remote-vs-autonomous] 遥控器汽车 vs 整套自动驾驶系统
- [CODE:anti-pattern-while] 展示反模式伪代码 while(true){ callAPI; parse; execute }

---

## 块 3｜§1.2 全景架构（约 5min）

**口播要点**
1. AI 编程工具时间线（Copilot → ChatGPT → GPT-4 / Function Calling → Code Interpreter → Devin → Computer Use → Cursor Agent 与 MCP → Claude Code → 源码公开）
2. 规模锚点：**1,884** 个 TypeScript 文件 / **512,664** 行
3. 技术栈：Bun、React+Ink、Commander.js、Zod v4、@anthropic-ai/sdk
4. 五模块：Entry、QueryEngine、AsyncGenerator 主循环、工具类型、工具注册；55 个工具、权限四阶段

**画面 / 标记**
- [ANIM:ai-tools-timeline] 时间线节点滚动到「现在 ← 你在这里」
- [ANIM:scale-1884-512664] 大字数字弹出 + 与 VS Code 体量对比
- [ANIM:arch-layers] Entry → QueryEngine → Loop → Tools/Permission → Ext（MCP/子智能体/插件/Hook）
- [ANIM:tech-stack-table] 技术栈五格卡片
- [CODE:async-generator-steps] 主循环七步伪代码走读

---

## 块 4｜§1.3 五大原则（约 6min）

每条原则 **约 70s**，各配 1 个动画锚点：

| # | 原则 | 中英 | 动画锚点 |
|---|------|------|----------|
| 1 | 异步流式优先 | Async Generator First | [ANIM:principle-async] yield 事件流 + Ctrl+C 可中断 |
| 2 | 安全边界内嵌 | Security at the Perimeter | [ANIM:principle-security] 四阶段：可见性→校验→决策→运行时 |
| 3 | 缓存感知设计 | Cache-Aware Architecture | [ANIM:principle-cache] 系统 Prompt 稳定 / 子智能体共享缓存 |
| 4 | 渐进式能力扩展 | Progressive Capability | [ANIM:principle-progressive] Tool→Skill→Plugin→MCP 四级阶梯 |
| 5 | 不可变状态流转 | Immutable State Flow | [ANIM:principle-immutable] updater(prev)=>next + 快照传递 |

**口播要点**：每条讲清「为什么不选更简单方案 / 不这样会怎样」，避免念定义。

---

## 块 5｜实战练习速览（约 2min）

**口播要点**
1. 
npm install -g @anthropic-ai/claude-code → claude --version
2. /doctor：环境、权限、MCP、API、文件系统——渐进式出结果（呼应流式原则）
3. 一次工具调用：思考 → GlobTool(\*.ts\) → 回复；心中对照主循环模块

**画面 / 标记**
- [CODE:install-claude] 安装与版本命令
- [CODE:doctor-flow] /doctor 五项检查清单动画
- [ANIM:one-tool-call] 思考→工具名参数→结果→回复三阶段

---

## 块 6｜总结 + 片尾出处（约 1min）

**口播要点**
1. 四句收束：范式已转移；Harness 是工程系统；五模块是骨架；五原则是红线
2. 预告第 02 讲：对话主循环 AsyncGenerator
3. **片尾固定句（必须 verbatim 含关键词）**：本系列基于开源书稿；系列名驭者·Agent Harness；关注小电讲电路；合集与置顶目录见简介

**画面 / 标记**
- [ANIM:outro-series] 系列名条 + 「基于开源书稿」+ B 站合集引导 + 章号 01→02

---

## 动画 / 代码标记总表（供 Task 4 制作）

| 标记 | 所属块 | 类型 |
|------|--------|------|
| chatbot-glue | 1 | ANIM |
| llm-roles | 2 | ANIM |
| six-challenges | 2 | ANIM |
| car-remote-vs-autonomous | 2 | ANIM |
| anti-pattern-while | 2 | CODE |
| ai-tools-timeline | 3 | ANIM |
| scale-1884-512664 | 3 | ANIM |
| arch-layers | 3 | ANIM |
| tech-stack-table | 3 | ANIM |
| async-generator-steps | 3 | CODE |
| principle-async | 4 | ANIM |
| principle-security | 4 | ANIM |
| principle-cache | 4 | ANIM |
| principle-progressive | 4 | ANIM |
| principle-immutable | 4 | ANIM |
| install-claude | 5 | CODE |
| doctor-flow | 5 | CODE |
| one-tool-call | 5 | ANIM |
| outro-series | 6 | ANIM |
