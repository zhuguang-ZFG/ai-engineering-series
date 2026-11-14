# Cursor CLI：闭源 Agent 的可验证用法

独立中文分册（非官方）。第一部包含前言、第 1–5 章与附录 A–D：核对 `agent` 入口、打印模式与输出格式、三种模式、会话与 worktree、规则文件、全局配置与审批档位。后续章节续写中。

Cursor 为闭源产品：本书只写官方文档声明的行为与本机可复现的命令形态，引用页面均在 2026-11-13 访问；不写版本号，不把 beta 阶段的沙箱说成硬安全边界。

[从前言开始](00-前言.md)

## 目录（第一部）

| 章 | 内容 |
| --- | --- |
| [01](ch01.md) | 装好一个叫 agent 的命令 |
| [02](ch02.md) | Agent、Plan、Ask 三种模式 |
| [03](ch03.md) | 会话、目录与 worktree |
| [04](ch04.md) | 规则从哪里读 |
| [05](ch05.md) | 模型、全局配置与审批档位 |

[附录 A：命令与文件位置](appendix-a.md) · [附录 B：配置字段与权限令牌](appendix-b.md) · [附录 C：证据边界与复现](appendix-c.md) · [附录 D：术语与常见误解](appendix-d.md)

## 构建

在仓库根目录运行 `python scripts/bookctl.py build --product cursor --lang zh`。输出位于 `yuyu-book/dist/`，前缀为 `yuyu-cursor-zh`。

本书为独立教程，与 Anysphere 无隶属关系。书籍内容许可与第三方产品各自独立。
