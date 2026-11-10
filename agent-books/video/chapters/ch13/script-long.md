# 第13章：流式架构与性能优化



大家好，这里是小电讲电路。今天讲第13章：流式架构与性能优化。

QueryEngine 是有状态的查询生命周期管理者，通过 AsyncGenerator 实现流式消息传递，每个会话一个实例，状态在 turn 间持久保持。类的设计将状态封装为实例属性，避免了全局状态的内存泄漏和并发修改风险。

StreamingToolExecutor 做到了"流到即执行"，并发安全工具可以并行运行，非安全工具串行执行，结果按顺序缓冲输出。这种设计把顺序排在延迟前面 -- 宁可多等一个串行工具，也不冒险并行执行可能冲突的操作。

启动性能优化的核心思想是并行化：让 I/O 密集操作（MDM 读取、keychain 读取）与 CPU 密集操作（模块评估）并行。示意计算中，关键路径由 160ms 缩短到 65ms；真实收益需要注明机器、版本、缓存状态和计时终点后实测。

成本追踪采用两层函数设计：updateUsage 处理单条流式事件的增量数据（用 > 0 守卫防止增量数据覆盖真实值），accumulateUsage 跨消息累加总量。不同生命周期组件（QueryEngine vs forked agent）采用不同粒度的累加策略。

缓存优化需要字节级一致性：fork agent 必须与父请求共享完全相同的 system prompt、tools、model、messages prefix 和 thinking config，任何维度的偏差都会导致缓存断裂。缓存命中率的持续监控是 Agent 系统成本控制的基石。

流式架构不是优化，而是架构选择：它决定了系统的每一个组件都必须按照"增量、可中断、可组合"的原则设计，是整个 Agent Harness 的基石。从 QueryEngine 到 StreamingToolExecutor 到工具执行，流式思维贯穿始终。

工具输出的 token 成本往往比模型输出更值得关注：一个大型文件的读取可能产生 60K+ 的缓存创建 token，而模型一轮输出的 token 通常只有 1-5K。优化工具返回内容（如限制行数、过滤无关信息）比优化模型输出更有效。

13.1 流式 API 交互。Claude Code 的核心交互模型是流式的。QueryEngine 是查询生命周期和会话状态的拥有者，它将原本散布在查询函数中的核心逻辑抽取为独立类，本章讨论其 headless/SDK 路径的实现；REPL 复用属于后续阶段。

13.2 StreamingToolExecutor 的并发控制。StreamingToolExecutor 是 Claude Code 工具执行层的核心。它的设计目标是让工具在流式到达时立即启动执行，而不是等待所有工具调用块全部到达后再统一处理。

13.3 启动性能优化。Claude Code 的启动时间直接影响用户体验。命令行工具的心理学研究表明，超过 2 秒的启动延迟会让用户觉得工具"笨重"，超过 5 秒则会触发"是不是卡了"的焦虑。系统通过三类优化策略来缩短从命令行输入到首次响应的延迟：并行预取、延迟加载和惰性模块评估。

13.4 令牌成本追踪。Claude Code 的成本追踪建立在两个核心函数之上：updateUsage 和 accumulateUsage。

13.5 缓存优化策略。Anthropic API 的提示缓存（Prompt Caching）是降低成本和延迟的关键机制。缓存键由五个维度构成：system prompt、tools、model、messages prefix 和 thinking config。

13.6 流式与性能：常见翻车 / 正确做法。性能优化这一层的翻车，多半不是算错，而是优化错了对象。下表左列是最常见的写法，右列是本章给出的做法：

这一讲就到这里，下一讲见。
