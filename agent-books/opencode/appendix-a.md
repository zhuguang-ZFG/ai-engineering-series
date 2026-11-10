# 附录 A：固定版本与源码导航

<!-- block: opencode-apxa.b-opening -->
下表汇集了书中的主要源码入口，链接均固定到同一提交。查找具体机制时，可以从负责它的服务进入，再追踪调用者和状态归属，不必在持续变化的开发分支中寻找本书对应的实现。

## A.1 版本记录

| 项目 | 本书基线 |
| --- | --- |
| 上游 | anomalyco/opencode |
| 发布版本 | v1.19.5 |
| 提交 | 810c0eba1a7348036f8bdf61e6632d0c36c6876c |
| 许可证 | MIT |
| 实跑平台 | Windows x64 |
| 插件公共包 | @opencode-ai/plugin 1.19.5 |
| 本地模型 | OpenAI-compatible SSE 协议替身，无外部模型 |

ZIP 的官方摘要与下载文件核对一致，exe 摘要则来自该 ZIP 解压出的文件，两者对应不同文件。详细值保存在 facts 的宿主记录中，复现命令会在启动前核对。

## A.2 从哪几个文件读起

| 想解决的问题 | 固定源码入口 | 对应章节 |
| --- | --- | --- |
| serve 怎样启动 | [cli/cmd/serve.ts](https://github.com/anomalyco/opencode/blob/810c0eba1a7348036f8bdf61e6632d0c36c6876c/packages/opencode/src/cli/cmd/serve.ts) | 第 1、2 章 |
| 项目先初始化谁 | [project/bootstrap.ts](https://github.com/anomalyco/opencode/blob/810c0eba1a7348036f8bdf61e6632d0c36c6876c/packages/opencode/src/project/bootstrap.ts) | 第 2、9 章 |
| 配置在哪里合并 | [config/config.ts](https://github.com/anomalyco/opencode/blob/810c0eba1a7348036f8bdf61e6632d0c36c6876c/packages/opencode/src/config/config.ts) | 第 3 章 |
| 会话保存什么 | [session/session.ts](https://github.com/anomalyco/opencode/blob/810c0eba1a7348036f8bdf61e6632d0c36c6876c/packages/opencode/src/session/session.ts) | 第 4 章 |
| 请求怎样准备 | [session/llm/request.ts](https://github.com/anomalyco/opencode/blob/810c0eba1a7348036f8bdf61e6632d0c36c6876c/packages/opencode/src/session/llm/request.ts) | 第 5 章 |
| 工具怎样注册 | [tool/registry.ts](https://github.com/anomalyco/opencode/blob/810c0eba1a7348036f8bdf61e6632d0c36c6876c/packages/opencode/src/tool/registry.ts) | 第 6 章 |
| 权限怎样等待回复 | [permission/index.ts](https://github.com/anomalyco/opencode/blob/810c0eba1a7348036f8bdf61e6632d0c36c6876c/packages/opencode/src/permission/index.ts) | 第 7 章 |
| Hook 怎样执行 | [plugin/index.ts](https://github.com/anomalyco/opencode/blob/810c0eba1a7348036f8bdf61e6632d0c36c6876c/packages/opencode/src/plugin/index.ts) | 第 8 章 |
| 模块怎样加载 | [plugin/loader.ts](https://github.com/anomalyco/opencode/blob/810c0eba1a7348036f8bdf61e6632d0c36c6876c/packages/opencode/src/plugin/loader.ts) | 第 9、16 章 |
| MCP 如何连接 | [mcp/index.ts](https://github.com/anomalyco/opencode/blob/810c0eba1a7348036f8bdf61e6632d0c36c6876c/packages/opencode/src/mcp/index.ts) | 第 10 章 |
| 语言服务状态 | [lsp/lsp.ts](https://github.com/anomalyco/opencode/blob/810c0eba1a7348036f8bdf61e6632d0c36c6876c/packages/opencode/src/lsp/lsp.ts) | 第 11 章 |
| 子任务怎样派生 | [tool/task.ts](https://github.com/anomalyco/opencode/blob/810c0eba1a7348036f8bdf61e6632d0c36c6876c/packages/opencode/src/tool/task.ts) | 第 12 章 |
| 文件撤销怎样实现 | [snapshot/index.ts](https://github.com/anomalyco/opencode/blob/810c0eba1a7348036f8bdf61e6632d0c36c6876c/packages/opencode/src/snapshot/index.ts) | 第 13 章 |

## A.3 阅读 Effect 代码的几个线索

本书不把 Effect 当成入门前提。第一次读源码，可以先找 Service 的接口定义，再看 layer 中怎样实现它，最后看 node 中的依赖。`Effect.gen` 包含逐步执行逻辑，`yield*` 表示把某项效果接入当前计算；是否并发、如何捕获错误，需要继续看具体组合器。

生命周期通常要关注 Scope、InstanceState 和 finalizer。初始化函数返回了一个对象，不表示它的全部资源都由垃圾回收自动关闭；网络连接、事件订阅和子进程仍可能需要显式清理。遇到 `catch`、`ignore`、`orDie` 等分支，尤其要检查错误怎样传播到调用者。

函数名只能提供线索，具体行为还要沿调用链确认。例如 remove 可能只是移除注册，cleanup 可能清理历史消息，revert 才进入文件快照。
