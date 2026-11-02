# R1 内容图版九章铺开 —— 图替繁文首轮

日期：2026-11-02 ｜ 分支：`feat/skill-suite-transform` ｜ 前置：`1245caf`（skill 套件 spec/plan）、`7c5a5bc`（ch14 精读修正）

## 1. 目标与红线

九个尚无内容图版的章节（ch05/06/09/10/11/12/13/14/15）各得一幅 SVG 图版，
按 handraw-style `article-illustration-planner` Mode A 执行，四条红线不变：

1. 不摆微缩道具；2. 无拟人向导；3. **零知识阉割**——公式/阈值/术语必须入图，
   散文保留全部结论；4. 真图形隐喻，不做文字搬运。

场景映射沿用七类：公式→金字塔/天平、阶梯→台阶、漏斗→漏斗、系统→中心标注、
正反→双列、SOP→流程树、矩阵→标签卡。图版间距 ≥400 字 + ≥1 个小节标题。

## 2. 现状盘点（2026-11-02 实测）

`yuyu-book/illustrations/` 共 **33 份 SVG**：章徽 ch01–ch15（15）+ 篇题 p1–p4（4）
+ 附录 apxa–apxd（4）+ front/cover/keeper（3）+ 章内内容图版 7 幅
（ch01-five-pillars、ch02-turn-loop、ch03-tool-bench、ch03-tool-pipeline、
ch04-gate-steps、ch07-four-levels、ch08-hook-line）。
嵌入语法：` ```ill ` 围栏块 + 图版名；标题向上借（render.py `drawing_slots`）；
art.py 硬契约（单根 svg + viewBox、≥1 currentColor、禁 script/style/id=/href=/url(、≤6000B）。
`check_mermaid.mjs` 只数 ```mermaid 块（320），ill 块不入计。

## 3. 九图版登记表（scout 实测行号，插入点=小节末尾、下一标题前）

| # | 文件名 | zh 锚点 | en 锚点 | 场景 | 隐喻 |
|---|--------|---------|---------|------|------|
| 5-A | `ch05-trust-ladder` | 05 §5.2.4 末（≈:316） | 05 §5.2.4 末 | ②阶梯 | 信任半径递减阶梯 + 3 星闸门 |
| 6-A | `ch06-memory-funnel` | 06 §6.2.2 末（≈:251） | 06 §6.2.2 末 | ③漏斗 | MEMORY.md 双闸漏斗（200 行→25KB） |
| 9-A | `ch09-fork-pipeline` | 09 §9.3 末（≈:321） | 09 §9.3 末 | ⑥SOP | buildForkedMessages 四步管线 + 效率漏斗 |
| 10-A | `ch10-coordinator-fork` | 10 §10.7 末（≈:625） | 10 §10.7 末 | ⑤双列 | 建筑工地（中心化）vs 侦察队（去中心化） |
| 11-A | `ch11-skill-stairs` | 11 §11.3.1 末（≈:333） | 11 §11.3.1 末 | ②阶梯 | 技能来源优先权五级阶梯 |
| 12-A | `ch12-mcp-state-dial` | 12 §12.1.4 末（≈:281） | 12 §12.1.4 末 | 状态环 | 五态连接钟面（Connected 顶针） |
| 13-A | `ch13-concurrency-gate` | 13 §13.2.2 末（≈:223） | 13 §13.2.2 末 | ⑤双列 | isConcurrencySafe 闸门分出并行/串行两条带 |
| 14-A | `ch14-plan-gate` | 14 §14.1.1 末（≈:137） | 14 §14.1.1 末 | ⑤双列 | Plan 闸门把失误关进只读探索房 |
| 15-A | `ch15-harness-wheel` | 15 §15.2 引言末（≈:186） | 15 §15.2 引言末 | ④中心 | 对话循环为毂、五组件为辐 |

### 必须入图（红线 3 清单）

**图内零文字铁律**（33 份既有 SVG 实测唯一例外 `frame-no` 序号）：术语/数字一律转为
结构与数量——星数画成星形符号、闸数画成闸门、箭头向表覆盖方向、框数表层级；
同一 SVG 双语共用，语言文字不进图，散文保留全部数字与结论（零知识阉割由散文兜底）。
字节预算：内容图版 `PLATE_BYTES = 20000`（art.py），章徽才是 6000；目标 3–8KB。
每条 path 带 `pathLength="100"`（滚动描线动画依赖）。

- **5-A**：6 级星级（policy★★★★★→plugin★☆☆☆☆）、阈值「≥3 星」、闸门分可信/不可信区、
  projectSettings 标注「可能来自第三方仓库」。
- **6-A**：200 行→25KB 两道闸先后顺序、每条 ≤150 字符、超限末尾追加警告、
  「行数限护理解效率 / 字节限护上下文预算」。
- **9-A**：四步名（保留父消息→收集 tool_use→统一占位符→单条 user 消息）、
  占位符「Fork started -- processing in background」、186,000→62,600 token、省 66%。
- **10-A**：架构（中心化/去中心化）、缓存（不共享/字节级共享）、上下文（仅任务/完整父上下文）、
  心智模型（建筑工地/侦察队）四维对照。
- **11-A**：5 级来源与路径（managed/`.claude/skills/`/`~/.claude/skills/`/`{plugin-dir}/commands/`/内置编译）、
  覆盖方向箭头、`CLAUDE_CODE_DISABLE_POLICY_SKILLS`。
- **12-A**：五态名（Connected/Failed/NeedsAuth/Pending/Disabled）、指数退避 1s/2s/4s、
  最大重试、认证失败不盲目重试、Connected 掉出即工具移除。
- **13-A**：安全侧 Read/Grep/Glob/WebFetch、非安全侧 Bash/Edit/Write/NotebookEdit、
  `canExecuteTool` 三分支、fail-closed 原则。
- **14-A**：无闸四失误（错误功能/风格不一/重写/返工）vs 有闸四对照（零成本修正/先探模式/比 trade-off/枚举边界）、
  `Premature Action`、只读/可写两阶段。
- **15-A**：中心「对话循环 Step 1（AsyncGenerator）」、五辐 Step 2–6（工具/权限/上下文/记忆/钩子）、
  `buildTool`、四阶段短路、渐进式压缩、PreToolUse/PostToolUse。

第二轮候选（5-B/6-B/9-B/10-B/12-B/13-B/14-B/15-B）已在 scout 报告中备案，留给 R1.5。

## 4. 风险

- 行号漂移：en ch14 保留 1 行既有漂移；插入块 zh/en 各 +3 行，锚点用 `shift_anchors.py` 平移。
- 版面：图版借上方小节标题做图注，散文无需改写；图版与既有 mermaid 并存（mermaid 管结构，图版管意象）。
- 契约：每幅 ≤6000B；超限即精简路径/文案，不砍必须入图项。

## 5. 验收

1. `python yuyu-book/build.py --check` 与 `--mermaid=source` 绿；
2. 两套 unittest 全绿（账本 54 条注记含「构建器测试 N 项全绿」实数）；
3. `python scripts/check_book.py` 绿（文件数 96→98）；
4. `npm run check:diagrams` 320/0 不变；
5. 九章 HTML 中各出现 1 幅新图版，双语嵌入行号同步。
