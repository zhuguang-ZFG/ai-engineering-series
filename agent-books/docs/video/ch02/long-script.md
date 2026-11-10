# 第 02 章长讲口播脚本｜驭者·Agent Harness

> 用途：B 站横屏长讲配音底稿（沉稳男声 · 云扬）  
> 对应大纲：`docs/video/ch02/long-outline.md`  
> 标记说明：ANIM:id / CODE:id / QUIZ:id 行不计入朗读。

---

## 块 1｜开场钩子

大家好，这里是小电讲电路。驭者·Agent Harness 第 02 讲。上一集我们说清楚：Harness 不是 API 套壳，是能跑、能停、能诊断的整车。这一集拆开发动机的点火节奏——对话主循环。书稿给它起了个名字：Agent 的心跳。

[ANIM:heartbeat-loop]

[QUIZ:guess-heartbeat]

先停三秒想一下：如果你在源码里找「心跳」，它最可能是什么？回调地图？Promise 链？还是一个 async function 星号？答案写在本章标题里——异步生成器 AsyncGenerator。每一次 yield，就像一次脉搏：把「正在发生的事」推给 UI，而不是等整场手术做完才开门。

---

## 块 2｜§2.1 异步生成器：对话循环的骨骼

书稿第二节开篇就说：Claude Code 的对话主循环，是一个由 async function 星号驱动的异步生成器。它不是普通函数跑完再返回，而是一条可暂停、可恢复、可取消的「心」。

[ANIM:async-gen-layers]

三层能力叠在一起。第一层，流式产出：每次 yield 推送一次结构化事件，UI 不用干等。第二层，取消语义：AbortSignal 或迭代器的 return，能走到 finally，把资源收干净——对应你按 Ctrl+C。第三层，背压：消费者跟不上时，生成器自动暂停，事件不会在内存里无限堆。这三层，正好对应 Agent 真需求：边想边画、随时能停、工具狂奔时别把内存撑爆。

为什么不选回调？回调会把逻辑撕碎在各个注册点。为什么不选 Promise 链？Promise 只能 resolve 一次，装不下一路涌出的增量事件。Observable 很强，但学习与类型成本更高。AsyncGenerator 刚刚好：原生语法、类型友好、取消路径清晰。

[CODE:async-gen-signature]

函数签名本身就是契约。Yield 出来的是联合类型事件；真正的终局用 Terminal 表达；参数则收成一个结构体——消息历史、系统提示、权限检查、工具执行上下文、压缩策略入口，都从这里进，不在散落的全局里偷拿。

[ANIM:event-types]

流式事件可以分成五类脉搏。stream_request_start：每次 API 将发未发，UI 可以亮「正在思考」。StreamEvent：Anthropic 原始流，文本增量、thinking、tool_use，像视频的每一帧。Message：结构化消息，助手、用户、系统，相当于剪辑好的镜头。TombstoneMessage：流式回退时的墓碑，告诉 UI 某段历史作废。ToolUseSummaryMessage：一批工具跑完后的折叠摘要，长会话才不至于被输出淹没。

[ANIM:message-types]

消息族谱也要心里有数。UserMessage 既是用户输入，也承载 tool_result——在 API 协议里工具结果必须以 user 角色回灌，这是协议约束，不是命名任性。AssistantMessage 可以同时带文本和 tool_use，边说边动手。SystemMessage 不进 API，只做第四面墙。Attachment 与 Progress 分别承载附件通知和工具进度。记住：事件是脉搏，消息是可归档的病历。

---

## 块 3｜§2.2 一个完整 Turn 的生命周期

什么叫一轮 Turn？从用户按下回车，到模型答完、可能调工具、再决定继续或收束——这就是一次心跳周期。书稿用医学比喻：模型是医生，先问诊再开检查，拿到化验单再复诊。

[ANIM:turn-five-phases]

[CODE:queryloop-skeleton]

queryLoop 是一个 while true。每一圈大致五阶段。阶段一，状态初始化：从上一拍的 State 解构只读视图，再准备本圈可写容器——读和写之间有清晰边界。阶段二，上下文预处理，七步管线。阶段三，注入的 callModel 发起流式请求，边收边 yield，同时收集助手消息与工具块；若开启流式工具执行，甚至可以在响应未完成时先跑工具。阶段四，权限检查、并发分区、执行工具。阶段五，附件注入、打包新 State、continue 回阶段一。没有工具则走终止判定。

[ANIM:preprocess-7]

七步预处理是上下文的「压力梯」，顺序刻意从轻到重。一，工具结果预算，超长输出先截断或外置。二，Snip，按消息级裁历史。三，Microcompact，缓存友好的轻量压缩，尽量别把 API 侧已缓存 token 整段作废。四，Context Collapse，把一段对话收成更高密度的摘要图。五，系统提示组装，稳定前缀才能保住缓存命中。六，Autocompact，阈值触发的全量摘要，是重量级最后手段之一。七，Token 阻断检查，触硬顶就本地失败，别把注定失败的请求打出去。原则就一句：先付最小代价。

马车意象也在这里：辔绳收得住，长途才跑得远。上下文窗口就是舆的载重；乱堆不压缩，车轴会断。

[ANIM:terminal-10]

终止不是含糊的 error。书稿列了十种原因：completed 正常完成；aborted_streaming 与 aborted_tools 对应用户在流式或工具期中断；max_turns、blocking_limit、prompt_too_long、model_error、stop_hook_prevented、hook_stopped、image_error 覆盖循环上限、硬顶、恢复失败、API 异常、Hook 拦截与图片格式问题。细分终止，是为了调试时第一眼就知道「心跳停在哪」。

---

## 块 4｜§2.3 依赖注入 + §2.4 状态转换模型

主循环能测，是因为副作用被收进 QueryDeps。

[ANIM:query-deps]

四个依赖特别关键：callModel、microcompact、autocompact、uuid。测试时塞假实现，不必在每个文件里 spyOn 模块。书稿原话大意：今天光 callModel 和 autocompact，就在六到八个测试文件里重复样板。依赖注入把「和外部世界打交道」的边界钉死，循环内部才能专心做状态机。

为什么坚持函数式生成器，而不是 class？每次对话一个新闭包，没有实例字段串味；yield 自带背压；return 走 finally；yield 星号把子循环的事件与终值一起委托上来。反模式警告写在这里：

[CODE:anti-global-state]

别把对话状态塞进全局变量或长寿命实例字段。全局杀并发测试，实例字段让多会话互相踩。闭包是最安全的舆厢。

[ANIM:state-continue-terminal]

状态机三元模型：State、Continue、Terminal。State 可变但可控，每次 continue 造新对象，transition 字段记下「为什么继续」。Continue 是继续信号，带原因与附件。Terminal 是终止信号，带原因交还给调用方。类型系统逼你把路走清楚。

[ANIM:continue-7]

七条 Continue 路径要能叫出名字。next_turn：工具跑完，历史扩展，最常见。max_output_tokens_escalate：首次截断先抬输出上限。max_output_tokens_recovery：仍截断就注入恢复消息，最多再试三次。reactive_compact_retry：预防性压缩挡不住溢出时的紧急刹车。collapse_drain_retry：更细粒度的折叠排水恢复。stop_hook_blocking：Stop hook 拦停后把信息注回，让模型有机会换策略。token_budget_continuation：预算提醒，不是粗暴掐断。每条路径写清 transition reason，异常时就是黑匣子。

---

## 块 5｜实战练习要点

练习可以很具体。第一，追一次工具调用：在 stream_request_start、首个 tool_use 到达、runTools 启动、continue 前打四个点，看事件如何从 API 流进执行再回到下一轮。第二，在测试里注入「半截就截断」的假模型，观察 escalate 与 recovery 怎么切换。第三，估算没有 DI 时，七条 Continue 加十种终止要写多少模块级 mock。第四，故意喂一串吃上下文的任务，看 Snip 与 Autocompact 谁先亮灯。

[ANIM:trace-four-points]

[ANIM:token-recovery]

细节实现后面核心篇还会拆压缩；本章先把心跳的节律听熟。

---

## 块 6｜总结 + 片尾

收五句。一，AsyncGenerator 是 Agent 循环的骨架，不是「也可以用」的语法糖。二，预处理管线从轻到重，守住 token 预算。三，状态可变，转换可追。四，QueryDeps 让测试成为工程而不是苦行。五，终止原因要细，失败也要体面。

下一集第 03 章，我们转去工具系统——Agent 的双手：编排、并发分区、渲染与权限如何接上这颗心跳。

[ANIM:outro-series]

本系列基于开源书稿。系列名：驭者·Agent Harness。关注小电讲电路，合集里看目录更新。我们下集见。
