# 附录 D：术语、来源和跨册对照

<!-- block: deepseek-apxd.b-opening -->
同一个词在不同代理中可能指向不同接口。遇到“插件”“上下文”“恢复”时，先确定对象和生命周期，再套用经验。本表给出本册使用的具体含义。

## D.1 组合与生命周期

| 术语 | 本册含义 | 主要章节 |
| --- | --- | --- |
| Harness | 连接模型、工具、循环、状态和执行环境的运行系统 | 1、17 |
| Context | Cordis 服务解析与注册的上下文 | 2 |
| Service | 按稳定名称提供的能力实例 | 2 |
| inject | 插件对服务的运行时依赖声明 | 2、4 |
| fiber | 一次插件挂载的生命周期句柄 | 3 |
| effect | 带撤销动作的受管注册或资源 | 3、4 |
| realm | 指定服务名的解析隔离域 | 2、12 |
| profile | 用户选择的有名字的应用组合 | 1、16 |
| bundle | 配置补丁行及相应代码的分发容器 | 1、16 |
| HMR | 协调配置或模块变化的热更新机制 | 4、16 |

## D.2 循环、日志与工具

| 术语 | 本册含义 | 主要章节 |
| --- | --- | --- |
| AgentFactory | 创建公共 Agent 实现的提供者 | 5 |
| AgentHandle | 拥有某次 Agent 清理责任的句柄 | 5、12 |
| Turn | 一次从认领工作到不再欠工作的任务边界 | 6 |
| Step | 一次模型请求及其工具工作 | 6 |
| inbox | 等待被认领的输入与上下文队列 | 6 |
| SessionEvent | 可持久记录、可投影的会话事实 | 7 |
| projection | 从事件形成特定消费者视图的过程 | 7、13 |
| canonical value | 工具成功返回的规范 JSON 值 | 10 |
| content | 面向模型的工具结果呈现 | 10 |
| waterfall | 用 next 组成的环绕调用链 | 11 |
| guard | 后续策略不能撤销的最终拒绝点 | 10、15 |
| ScopeKey | 按对象身份比较的注册作用域键 | 12 |
| prepareCall | 解析参数并绑定实际适配器的调用准备 | 9 |

## D.3 容易误解的对应关系

插件停止不等于副作用回滚；服务 realm 不等于操作系统沙箱；模型历史恢复不等于 Git 回退；工具隐藏不等于插件不能直接执行代码；规范值隐藏不等于只改显示文本；请求重试不等于工具可以重做。这些区别反复出现，是因为它们各自有不同的拥有者。

OpenCode 分册讨论 V1 Plugin/Hooks 与真实宿主发现，Pi 分册讨论扩展与极简 Agent 壳，Hermes 分册聚焦记忆与持续任务，Codex CLI 分册聚焦执行、审批与沙箱。它们适合在相同实验问题下比较，而不是以共享名称猜测实现。

## D.4 查证一条结论

先看该章末尾的固定 SHA 链接，确认文件职责；再看 VERIFY 和 facts 是否有对应运行记录。如果只有源码，就按源码结论理解；如果有组件实跑，检查组件是否就是你关心的宿主路径；如果是完整应用实验，还要检查平台、配置、模型替身与实际供应商的区别。

写自己的扩展说明时也可以采用这个方法。读者真正需要的是知道哪些结果可直接复现、哪些需要自己的环境，而不是看到一份把所有格子都勾满的表。

## 固定版本来源

- [docs/architecture.md](https://github.com/deepseek-ai/deepseek-harness/blob/fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159/docs/architecture.md)
- [docs/cordis-primer.md](https://github.com/deepseek-ai/deepseek-harness/blob/fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159/docs/cordis-primer.md)
- [docs/subsystems/scope.md](https://github.com/deepseek-ai/deepseek-harness/blob/fcc0ad462172522aaf5c93a7b2e01f6b9f0b0159/docs/subsystems/scope.md)
