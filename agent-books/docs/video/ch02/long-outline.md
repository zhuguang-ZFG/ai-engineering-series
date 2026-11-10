# 第 02 章长讲大纲｜驭者·Agent Harness

> 成片目标：B 站横屏 15–20 分钟  
> 书稿来源：第一部分-基础篇/02-对话循环-Agent的心跳.md  
> 内部隐喻：心跳 / AsyncGenerator / 脉搏事件 / 考工记马车（沿用书感白描，非卡通）

## 时间轴总览

| 块 | 内容 | 预计 | 累计 |
|----|------|------|------|
| 1 | 开场钩子（心跳） | 0:50 | 0:50 |
| 2 | §2.1 异步生成器骨骼 | 4:30 | 5:20 |
| 3 | §2.2 一次 Turn 生命周期 | 5:30 | 10:50 |
| 4 | §2.3–2.4 依赖注入 + 状态机 | 5:00 | 15:50 |
| 5 | 实战练习要点 | 1:40 | 17:30 |
| 6 | 总结 + 片尾预告 | 1:00 | 18:30 |

预计总时长约 **18 分 30 秒**（落入 15–20 分钟）。

---

## 块 1｜开场钩子（约 50s）

**口播要点**
- 承接第 01 章：Harness 是整车；本集拆「发动机点火节奏」——对话主循环
- 隐喻：AsyncGenerator 是 Agent 的心跳；每次 yield 是一次脉搏
- 抛问：为什么不用回调、不用 Promise 链？

**画面 / 标记**
- [ANIM:heartbeat-loop] 心电图式循环：想→调→收→再想
- 系列条「驭者·Agent Harness」· 章号 02
- [QUIZ:guess-heartbeat] 猜一猜：Agent 的「心跳」对应源码里什么？

---

## 块 2｜§2.1 异步生成器：对话循环的骨骼（约 4.5min）

**口播要点**
1. async function*：可暂停、可恢复、可取消的「协程」
2. 三层能力：流式产出 / AbortSignal 取消 / 背压自动暂停
3. AsyncGenerator vs 回调 vs Promise vs Observable——「刚刚好」
4. 流式事件：stream_request_start / StreamEvent / Message / TombstoneMessage / ToolUseSummaryMessage
5. 消息类型：User / Assistant / System / Attachment / Progress（+ 墓碑与摘要）

**专有名词中英**
- 异步生成器 AsyncGenerator
- 流式事件 StreamEvent
- 墓碑消息 TombstoneMessage

**画面 / 标记**
- [ANIM:async-gen-layers] 三层：流式 / 取消 / 背压
- [ANIM:event-types] 五类事件卡片依次弹出
- [ANIM:message-types] 消息族谱简图
- [CODE:async-gen-signature] 函数签名伪代码（yield 联合类型 + Terminal）

---

## 块 3｜§2.2 一个完整 Turn 的生命周期（约 5.5min）

**口播要点**
1. Turn = 用户回车 → 模型响应 →（可选）工具 → 再决策
2. 五阶段：状态初始化 → 七步预处理 → API 流式收 → 工具执行 → 回填 continue
3. 七步管线：工具结果预算 → Snip → Microcompact → Context Collapse → 系统提示组装 → Autocompact → Token 阻断
4. 原则：压缩从轻到重，先最小代价
5. 十种终止原因：completed / aborted_* / max_turns / blocking_limit / …

**画面 / 标记**
- [ANIM:turn-five-phases] 五阶段环状流程图
- [ANIM:preprocess-7] 七步管线「压力梯」
- [ANIM:terminal-10] 终止原因清单
- [CODE:queryloop-skeleton] while(true) + continue 伪代码
- 马车意象：辔收得紧才是长途——上下文预算

---

## 块 4｜§2.3 依赖注入 + §2.4 状态转换（约 5min）

**口播要点**
1. QueryDeps：callModel / microcompact / autocompact / uuid——副作用边界
2. 为何函数式 async function* 而不是 class：闭包状态、背压、取消、yield* 组合
3. 三元模型：State + Continue + Terminal
4. 七种 Continue：next_turn / max_output_tokens_recovery / escalate / reactive_compact_retry / collapse_drain_retry / stop_hook_blocking / token_budget_continuation
5. transition reason = 调试「黑匣子」

**画面 / 标记**
- [ANIM:query-deps] 四个依赖插拔
- [ANIM:state-continue-terminal] 三元状态机
- [ANIM:continue-7] 七条 Continue 路径地铁图
- [CODE:anti-global-state] 反模式：全局/实例状态

---

## 块 5｜实战练习要点（约 1.5–2min）

**口播要点**
1. 追踪一次工具调用的四个日志点
2. 模拟 max_output_tokens：escalate → recovery
3. 没有 DI 时 mock 成本估算
4. 观察 Snip / Autocompact 触发时机

**画面 / 标记**
- [ANIM:trace-four-points] 四点探针
- [ANIM:token-recovery] escalate vs recovery

---

## 块 6｜总结 + 片尾（约 1min）

**口播要点**
1. 五句口诀：生成器是心跳；管线管上下文；状态可变但可追；DI 让测试活；终止要细粒度
2. 预告第 03 章：工具系统——Agent 的双手
3. **片尾固定句（verbatim）**：本系列基于开源书稿；系列「驭者·Agent Harness」；关注小电讲电路，合集里看目录更新。

**画面 / 标记**
- [ANIM:outro-series] 系列条 + 章号 02→03 + 开源书稿

---

## 动画 / 代码清单（供渲染）

| 编号 | 块 | 类型 |
|------|----|------|
| heartbeat-loop | 1 | ANIM |
| guess-heartbeat | 1 | QUIZ |
| async-gen-layers | 2 | ANIM |
| event-types | 2 | ANIM |
| message-types | 2 | ANIM |
| async-gen-signature | 2 | CODE |
| turn-five-phases | 3 | ANIM |
| preprocess-7 | 3 | ANIM |
| terminal-10 | 3 | ANIM |
| queryloop-skeleton | 3 | CODE |
| query-deps | 4 | ANIM |
| state-continue-terminal | 4 | ANIM |
| continue-7 | 4 | ANIM |
| anti-global-state | 4 | CODE |
| trace-four-points | 5 | ANIM |
| token-recovery | 5 | ANIM |
| outro-series | 6 | ANIM |
