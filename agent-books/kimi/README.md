# Kimi Code：从插件到审查助手

独立中文分册，包含前言、18 章和附录 A–D。以澄明库存案例串起配置、工具、会话、Skill、自定义 Agent、插件、Hook、MCP、ACP 和失败恢复。英文版尚未启动。

固定 `MoonshotAI/kimi-code` 的 `@moonshot-ai/kimi-code@2.5.2`，提交 `1c142a007c10e881602690def96057c23a2baa12`，MIT。不要与旧 Python 项目 `kimi-cli` 混用。

[从前言开始](00-前言.md) · [示例说明](examples/README.md) · [验证记录](VERIFY.md) · [源码摘要](facts/source-lock.json)

## 目录

| 章 | 内容 | 章 | 内容 |
| --- | --- | --- | --- |
| [01](ch01.md) | 程序与第一处错误 | [10](ch10.md) | 只读 Agent |
| [02](ch02.md) | 请求经过的层次 | [11](ch11.md) | 插件装配 |
| [03](ch03.md) | 配置与模型别名 | [12](ch12.md) | Hook 输入与失败 |
| [04](ch04.md) | 工作区与业务规则 | [13](ch13.md) | MCP 规则服务 |
| [05](ch05.md) | 工具反馈循环 | [14](ch14.md) | ACP 客户端 |
| [06](ch06.md) | 权限与 Plan | [15](ch15.md) | 子 Agent 委派 |
| [07](ch07.md) | 会话恢复与分叉 | [16](ch16.md) | JSONL 脚本集成 |
| [08](ch08.md) | 上下文压缩 | [17](ch17.md) | 中断与排错 |
| [09](ch09.md) | 审查 Skill | [18](ch18.md) | 完整项目交付 |

[附录 A：命令](appendix-a.md) · [附录 B：配置与源码](appendix-b.md) · [附录 C：实验](appendix-c.md) · [附录 D：术语](appendix-d.md)

## 构建

在仓库根目录运行 `python scripts/bookctl.py build --product kimi --lang zh --pdf --epub`。输出位于 `yuyu-book/dist/`，前缀为 `yuyu-kimi-zh`。

本书为独立教程，与 Moonshot AI 无隶属关系。上游代码与书籍内容采用各自许可；源码下载与本地生成物不提交 Git。
