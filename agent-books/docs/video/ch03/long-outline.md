# 第 03 章长讲大纲｜驭者·Agent Harness

> 成片目标：B 站横屏 15–20 分钟  
> 书稿来源：第一部分-基础篇/03-工具系统-Agent的双手.md  
> 内部隐喻：双手 / 锤子 vs 工具箱 / 五要素 DNA / 机场 fail-closed / 百科→目录索引 / 工厂工位并发分区 / 边吐字边开工 / 考工记马车（缰上活扣，书感白描）

## 时间轴总览

| 块 | 内容 | 预计 | 累计 |
|----|------|------|------|
| 1 | 开场钩子（锤子 vs 双手） | 0:55 | 0:55 |
| 2 | §3.1 五要素协议 + buildTool | 4:20 | 5:15 |
| 3 | §3.2 注册 / 延迟发现 / 过滤 | 3:40 | 8:55 |
| 4 | §3.3 核心工具深度（Bash / 文件三件套 / 搜索 / Agent） | 4:30 | 13:25 |
| 5 | §3.4 编排：并发分区 + StreamingToolExecutor | 4:20 | 17:45 |
| 6 | 实战要点 + 总结 + 片尾预告 04 | 1:30 | 19:15 |

预计总时长约 **19 分 15 秒**（落入 15–20 分钟）。

---

## 块 1｜开场钩子（约 55s）

**口播要点**
- 承接第 02 章：心跳有了；本集装「双手」——工具系统
- Maslow：只有锤子，一切都是钉子 → 只有 Bash，一切都是 shell
- 抛问：真双手是多塞几个函数，还是一套协议？

**画面 / 标记**
- [ANIM:hammer-vs-hands] 大锤砸「一切」→ 工具箱双手展开
- 系列条「驭者·Agent Harness」· 章号 03
- [QUIZ:guess-hands] 猜一猜：Agent「双手」在源码里最先对应什么？

---

## 块 2｜§3.1 工具定义协议（约 4.2min）

**口播要点**
1. Tool&lt;Input, Output, Progress&gt;：三泛型分离 = 三个类型空间
2. 五要素：名称与别名 / Zod Schema / 权限三层 / 执行+contextModifier / 六套 UI 渲染
3. 别名「只增不减」；Schema 双职：运行时验证 + API 说明书
4. buildTool：fail-closed 安全默认（机场安检类比）
5. 接口即架构：忘了实现？编译器当场拦

**专有名词中英**
- 五要素协议 Five-element Tool Protocol
- Zod Schema / buildTool / contextModifier
- fail-closed

**画面 / 标记**
- [ANIM:five-elements] 五卡串联 DNA
- [ANIM:perm-three-layers] validate → hasPermissions → 运行时属性
- [ANIM:ui-lifecycle] 生老病死六渲染
- [CODE:tool-generic] Tool&lt;Input,Output,Progress&gt; 伪签名
- [ANIM:buildtool-failclosed] 机场安检默认拦截

---

## 块 3｜§3.2 注册与动态发现（约 3.7min）

**口播要点**
1. getAllBaseTools：按类表（执行/文件/搜索/网络/Agent/任务/MCP…）+ 并发安全列
2. 死代码消除：条件导入，内部工具不进外部构建
3. ToolSearchTool 延迟发现：百科全书 vs 目录索引
4. 过滤管线：模式 → deny → enabled → 池组装排序（保 prompt 缓存）

**画面 / 标记**
- [ANIM:tool-catalog] 分类表翻页（点出 55）
- [ANIM:deferred-index] 百科砸桌 vs 目录索引
- [ANIM:filter-pipeline] 四段漏斗到 API
- [CODE:toolsearch-defer] 延迟判定伪代码

---

## 块 4｜§3.3 核心工具深度（约 4.5min）

**口播要点**
1. BashTool：最有力也最需约束——错误传播、中断语义、AST 语义、沙盒
2. 文件三件套：Read / Edit / Write；故意无 Delete；Edit 用精确串而非行号
3. 搜索双雄 Glob + Grep：专门化 &gt; 通用 Bash find/grep
4. AgentTool：子智能体入口；alwaysLoad；继承但不共享上下文

**画面 / 标记**
- [ANIM:bash-swiss] 瑞士军刀 + 安全网
- [ANIM:file-trio] CRUD 缺 D 的安全决策
- [ANIM:search-twins] Glob/Grep vs Bash
- [ANIM:agent-tool] 主驾派副驾
- [CODE:edit-old-new] old_string→new_string

---

## 块 5｜§3.4 编排引擎（约 4.2min）

**口播要点**
1. runTools 并发分区：连续安全工具一批并行；非安全单独串行
2. 例：[Read, Read, Bash, Read] → 三批次；为何 Read(c) 不能跟 Bash 同批
3. StreamingToolExecutor：边收 tool_use 边执行；四阶段 queued→executing→completed→yielded
4. 顺序保证 / Bash 错误传播 / 进度绕序即时 yield / 回退丢弃 / 层级取消
5. 与第 02 章心跳对接：阶段三边流边入队，阶段四跑工具

**画面 / 标记**
- [ANIM:partition-batches] 工厂工位：安全 ‖ / 非安全 →
- [ANIM:stream-executor-4] 四阶段状态机
- [ANIM:order-vs-parallel] 并行执行、顺序 yield
- [CODE:partition-example] 分区伪代码 + 例题序列
- [QUIZ:partition-drill] 互动：给序列划批次

---

## 块 6｜实战 + 总结 + 片尾（约 1.5min）

**口播要点**
1. 练习提要：自建工具 / 手动画分区 / 断点追四阶段 / 延迟发现省 token
2. 五句口诀：协议是 DNA；安全默认 fail-closed；分区换速度；流式零等待；类型契约可扩展
3. 预告第 04 章：权限管线——Agent 的护栏
4. **片尾固定句（verbatim）**：本系列基于开源书稿；系列「驭者·Agent Harness」；关注小电讲电路，合集里看目录更新。

**画面 / 标记**
- [ANIM:outro-series] 系列条 + 章号 03→04 + 开源书稿

---

## 动画 / 代码清单（供渲染）

| 编号 | 块 | 类型 |
|------|----|------|
| hammer-vs-hands | 1 | ANIM |
| guess-hands | 1 | QUIZ |
| five-elements | 2 | ANIM |
| perm-three-layers | 2 | ANIM |
| ui-lifecycle | 2 | ANIM |
| tool-generic | 2 | CODE |
| buildtool-failclosed | 2 | ANIM |
| tool-catalog | 3 | ANIM |
| deferred-index | 3 | ANIM |
| filter-pipeline | 3 | ANIM |
| toolsearch-defer | 3 | CODE |
| bash-swiss | 4 | ANIM |
| file-trio | 4 | ANIM |
| search-twins | 4 | ANIM |
| agent-tool | 4 | ANIM |
| edit-old-new | 4 | CODE |
| partition-batches | 5 | ANIM |
| stream-executor-4 | 5 | ANIM |
| order-vs-parallel | 5 | ANIM |
| partition-example | 5 | CODE |
| partition-drill | 5 | QUIZ |
| outro-series | 6 | ANIM |
