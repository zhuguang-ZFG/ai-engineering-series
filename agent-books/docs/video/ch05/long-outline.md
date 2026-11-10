# 第 05 章长讲大纲｜驭者·Agent Harness

> 成片目标：B 站横屏 15–20 分钟
> 书稿来源：第二部分-核心系统篇/05-设置与配置-Agent的基因.md
> 内部隐喻：六层沉积岩（挖开看层）/ 钥匙圈只挂不摘 / 盖了章的红头文件 / 别人家的告示牌钉你墙上 / 零件没上生产线 / 名字里写着丑话 / 砍到 34 行的「不」

## 时间轴总览

| 块 | 内容 | 预计 | 累计 |
|----|------|------|------|
| 1 | 开场钩子（改了怎么不生效） | 0:59 | 0:59 |
| 2 | §5.1 六层沉积岩与优先级链 + 三种分层实践 | 3:25 | 4:24 |
| 3 | §5.1 合并规则：数组/对象/标量 + 策略层例外 | 4:19 | 8:43 |
| 4 | §5.2 安全边界：那一层为什么不算 | 3:53 | 12:36 |
| 5 | §5.3 功能开关：编译时 vs 运行时 | 2:10 | 14:46 |
| 6 | §5.4 状态系统：34 行的「不」 | 3:30 | 18:16 |
| 7 | 实战 + 总结 + 片尾预告 06 | 1:09 | 19:25 |

预计总时长约 **19 分 25 秒**（落入 15–20 分钟，距上限余 35s）。

> 时长按 **2.89 汉字/秒** 推算——该速率由 ch02 实测配音反推（云扬 -10% / -5Hz，628s / 1811 汉字）。
> ch01–ch04 实测「成片时长 ÷ 纯口播时长」在 0.97–1.03 之间，即动画压在口播之下跑、不额外占时长，
> 所以口播字数基本等于成片时长。最坏情况（2.80 字/秒）为 20.0 min。

---

## 块 1｜开场钩子（约 1:00）

**口播要点**
- 承接：前四章装完了车——心跳、双手、护栏。但这些行为是谁定的？
- 痛点：你改了 `settings.json`，重启，还是老样子。不是改错了值，是改错了**层**
- 抛问：配置到底有几层？改哪一层才管用？
- 本章把「基因」挖开看：六层沉积岩

**画面 / 标记**
- [ANIM:edit-no-effect] 改 model→重启→数值弹回原样（红叉）
- [ANIM:rock-core-drill] 地质取芯：一根柱子抽出来，六条色带
- 系列条「驭者·Agent Harness」· 章号 05
- [QUIZ:guess-layers] 猜一猜：Claude Code 的配置有几层？

---

## 块 2｜§5.1 六层沉积岩与优先级链（约 4:10）

**口播要点**
1. 六层从低到高：pluginSettings → userSettings → projectSettings → localSettings → flagSettings → policySettings
2. 一层层对上人话：插件默认值 / 我的全局习惯 / 团队的公告牌（入 Git）/ 我的私人便签（不入 Git）/ 今天这一次的例外 / 公司盖章的红头文件
3. 后加载者覆盖前者——所以「改了不生效」＝你改的那层被上面盖住了
4. 关键：**盖住不是删掉**。每层都还在，只是被遮了。所以挑层比改值更要紧
5. 落到真实路径：`~/.claude/settings.json` / `.claude/settings.json` / `.claude/settings.local.json` / `--settings` / managed-settings.json
6. 隐藏的最低层 pluginSettings：它是合并的地基，不是第六层而是第零层

**专有名词中英**
- 六层配置源 Six-layer settings sources
- loadSettingsFromDisk / pluginSettings / policySettings

**画面 / 标记**
- [ANIM:six-strata] 六层岩自下而上堆叠，每层贴人话标签
- [ANIM:which-layer-wins] 同一个 `model` 字段在三层里打架 → 最上面那层亮起
- [ANIM:covered-not-deleted] 上层半透明盖下来，下层字仍在
- [CODE:settings-paths] 六层对应文件路径表
- [QUIZ:guess-layers-answer] 揭晓：六层（含第零层插件）

---

## 块 3｜§5.1 合并规则 + 策略层例外（约 3:50）

**口播要点**
1. 合并不是一种规则，是三种：数组拼接去重 / 对象深度合并 / 标量后者直接盖
2. **钥匙圈隐喻**：`permissions.allow` 是钥匙圈。每层把自己的钥匙挂上去，谁也摘不掉别人的——权限只增不减
3. 为什么这么设计：若上层替换下层，上层就必须一次列全所有权限，漏一条就是个洞。拼接让每层只管自己要加什么
4. **反模式**：别想用空数组「撤销」下层权限——挂上去一个空的，什么也没发生。要撤销就用 `permissions.deny` 明说
5. 策略层是例外：不合并，走「首个非空源胜出」。远程 API > MDM > managed-settings.json > HKCU 注册表
6. **红头文件隐喻**：企业策略是盖了章的一整份文件，照着最高那一份执行，不把几份文件的段落剪贴在一起——剪贴会出现语义冲突（一份限模型、一份限权限，拼起来可能让人用受限模型绕开权限）

**专有名词中英**
- settingsMergeCustomizer / first source wins
- permissions.allow / permissions.deny

**画面 / 标记**
- [ANIM:three-merge-rules] 三条规则并列：拼接 / 深合 / 覆盖
- [ANIM:keyring-stack] 钥匙圈逐层挂钥匙，一把都没掉
- [ANIM:empty-array-noop] 空数组挂上去 → 什么也没变（灰）
- [ANIM:deny-explicit] 要撤销 → deny 明写（红）
- [ANIM:sealed-doc] 四份来源排队，第一份非空的盖章生效，其余不拆开
- [CODE:merge-example] 三层配置 → 合并结果（接书稿例子）
- [QUIZ:merge-drill] 互动：给三层配置，预测 allow 与 model

---

## 块 4｜§5.2 安全边界：那一层为什么不算（约 4:20）

**口播要点**
1. 收刀时刻：六层里有一层，在安全敏感的检查里**系统根本不读**——projectSettings
2. 为什么偏偏是它：三个属性只有它全占齐——来源不可信（别人仓库里的）、自动加载（进目录就生效）、可执行代码（hooks 能跑任意 shell）
3. **告示牌隐喻**：clone 一个陌生仓库，等于把别人家的告示牌钉在你自己墙上，还默认照着做
4. 真实攻击形状：`.claude/settings.json` 里埋一个 PreToolUse hook，每次工具调用把 API key、环境变量发到攻击者服务器
5. 所以源码里一致地排除它：`skipDangerousModePermissionPrompt`、`hasAutoModeOptIn()`、`getUseAutoModeDuringPlan()`、`getAutoModeConfig()`，注释都指向同一句——恶意项目本来可以自动绕过弹窗（RCE 风险）
6. 两道企业闸：`allowManagedHooksOnly` 只放行托管 hooks；`strictPluginOnlyCustomization` 选择性锁定 skills/agents/hooks/mcp 四个定制面
7. 原则：信任半径递减。自己写的可信，别人仓库里的不可信——与第 04 章护栏同一套纵深思路

**专有名词中英**
- 信任半径递减 Decreasing trust radius
- 供应链攻击 Supply chain attack
- allowManagedHooksOnly / strictPluginOnlyCustomization

**画面 / 标记**
- [ANIM:sign-on-your-wall] 陌生仓库的告示牌钉上自家墙，自动执行
- [ANIM:hook-exfil] hook 把 key 发走（红线飞出）
- [ANIM:three-properties] 三属性对照表，只有 projectSettings 三格全亮
- [ANIM:systematic-exclusion] 四个函数读配置时，projectSettings 格子灰掉
- [ANIM:trust-radius] 信任半径同心圆，星级递减
- [ANIM:two-enterprise-gates] 托管 hooks 闸 + 四面选择性锁
- [CODE:exclusion-comment] 源码注释：intentionally excluded -- RCE risk

---

## 块 5｜§5.3 功能开关：编译时 vs 运行时（约 2:40）

**口播要点**
1. 两层开关：编译时 `feature()` 与运行时 GrowthBook
2. **生产线隐喻**：编译时关掉＝这个零件根本没上生产线，成品里找不到它。运行时关掉＝零件装好了，开关留在外面，可以远程拨
3. 编译时赢在三处：不占包体积、热路径没有分支开销、没编进去的代码里的 bug 和漏洞也一起没了
4. 从标志名能读出架构走向：KAIROS（长驻会话）、DAEMON（后台守护）＝从「按需调用」走向「持续运行」；TEAMMEM、TEMPLATES ＝从「个人工具」走向「团队基础设施」
5. 运行时那层：`getFeatureValue_CACHED_MAY_BE_STALE`——**把丑话写进名字里**。值来自缓存、可能过时，调用者每次写下这个名字都被提醒一次。叫 `getFeatureValue` 反而会骗人
6. 实验标志用随机动物名（tengu_passport_quail 之类）：避免语义偏见，也不和编译时的 feature() 撞名

**专有名词中英**
- 死代码消除 Dead code elimination
- GrowthBook / feature flag

**画面 / 标记**
- [ANIM:assembly-line] 零件没上线（成品里空位）vs 装好留开关
- [ANIM:flag-table] 九个标志按作用域排开，KAIROS/DAEMON 与 TEAMMEM/TEMPLATES 两条箭头
- [ANIM:ugly-name] 函数名逐字浮现，_CACHED_MAY_BE_STALE 高亮
- [CODE:feature-vs-growthbook] 两种写法对照
- [QUIZ:which-switch] 猜一猜：发布后还想改 → 用哪种开关？

---

## 块 6｜§5.4 状态系统：34 行的「不」（约 2:30）

**口播要点**
1. 配置是基因（启动前写定），状态是神经系统（运行中实时传）
2. Store 只有 34 行：getState / setState / subscribe。没有 reducer 样板、没有 action 类型、没有中间件、没有 DevTools
3. **每一个被砍掉的功能，都是一个想清楚了的「不」**。Agent CLI 不是 Web 应用：状态变更是秒级不是毫秒级、单用户单会话、不需要时间旅行调试
4. 不可变更新：`setState` 收 `(prev) => T`，用 `Object.is` 比引用。**换了新对象才算变**，在老对象上改字段不算
5. 把「有没有变」的判断权交给调用者：约定「返回新引用＝变了」，而不是提供 hasChanged 回调
6. `AppState` 标了 DeepImmutable：编译期就拦住直接改字段——让正确的事容易，让错的事不可能
7. 订阅要精确：只订自己真用到的那一片；只写不读就用 `useSetAppState()`，它永不重渲染

**专有名词中英**
- 不可变状态 Immutable state
- Store / Object.is / DeepImmutable / useSyncExternalStore

**画面 / 标记**
- [ANIM:gene-vs-nerve] 基因（启动前）与神经（运行中）两条线
- [ANIM:cut-to-34] 一排功能被逐个划掉，剩 34 行
- [ANIM:object-is] 换新盒子＝算变（亮）/ 在老盒子里改＝不算（灰）
- [ANIM:subscribe-precise] 订整棵树 vs 订一片叶子的重渲染差别
- [CODE:store-34] Store 三方法伪代码

---

## 块 7｜实战 + 总结 + 片尾（约 1:00）

**口播要点**
1. 练习提要：预测合并结果 / 当企业管理员锁两件事 / 给 20 人团队分层
2. 五句口诀：配置是六层不是一个文件；挑层比改值要紧；钥匙只挂不摘；别人仓库的那层不算；丑话写进名字里
3. 预告第 06 章：记忆系统——Agent 的长期记忆
4. **片尾固定句（verbatim）**：本系列基于开源书稿；系列「驭者·Agent Harness」；关注小电讲电路，合集里看目录更新。

**画面 / 标记**
- [ANIM:outro-series] 系列条 + 章号 05→06 + 开源书稿

---

## 动画 / 代码清单（供渲染）

| 编号 | 块 | 类型 |
|------|----|------|
| edit-no-effect | 1 | ANIM |
| rock-core-drill | 1 | ANIM |
| guess-layers | 1 | QUIZ |
| six-strata | 2 | ANIM |
| which-layer-wins | 2 | ANIM |
| covered-not-deleted | 2 | ANIM |
| settings-paths | 2 | CODE |
| guess-layers-answer | 2 | QUIZ |
| three-patterns | 2 | ANIM |
| three-merge-rules | 3 | ANIM |
| keyring-stack | 3 | ANIM |
| empty-array-noop | 3 | ANIM |
| deny-explicit | 3 | ANIM |
| sealed-doc | 3 | ANIM |
| merge-example | 3 | CODE |
| merge-drill | 3 | QUIZ |
| sign-on-your-wall | 4 | ANIM |
| hook-exfil | 4 | ANIM |
| threat-compare | 4 | ANIM |
| three-properties | 4 | ANIM |
| systematic-exclusion | 4 | ANIM |
| trust-radius | 4 | ANIM |
| two-enterprise-gates | 4 | ANIM |
| exclusion-comment | 4 | CODE |
| assembly-line | 5 | ANIM |
| flag-table | 5 | ANIM |
| ugly-name | 5 | ANIM |
| feature-vs-growthbook | 5 | CODE |
| which-switch | 5 | QUIZ |
| gene-vs-nerve | 6 | ANIM |
| cut-to-34 | 6 | ANIM |
| tearing-read | 6 | ANIM |
| object-is | 6 | ANIM |
| subscribe-precise | 6 | ANIM |
| store-34 | 6 | CODE |
| outro-series | 7 | ANIM |
