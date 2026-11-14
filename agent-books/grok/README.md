# Grok Build：开源编码 Agent 的 Harness

独立中文分册（非官方）。第一部包含前言、第 1–5 章与附录 A–D：确认程序、复现发布闸门的三处错误、七层配置优先级、项目规则与记忆、会话与检查点。后续章节续写中。

源码固定为 `xai-org/grok-build` 的公开提交 `2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8`（树内 `SOURCE_REV 559751fd` 记录其对应的内部单仓提交，Apache-2.0）。写作机器未安装发布的 `grok` 程序，凡未实测的命令均在正文与附录 C 注明「按文档」。

[从前言开始](00-前言.md) · [示例说明](examples/README.md)

## 目录（第一部）

| 章 | 内容 |
| --- | --- |
| [01](ch01.md) | 先确认跑的是哪个程序 |
| [02](ch02.md) | 让发布闸门先错一次 |
| [03](ch03.md) | 配置的七层优先级 |
| [04](ch04.md) | 项目规则与记忆放在哪 |
| [05](ch05.md) | 会话、恢复与检查点 |

[附录 A：命令与运行目录](appendix-a.md) · [附录 B：配置与源码导航](appendix-b.md) · [附录 C：实验记录与复现边界](appendix-c.md) · [附录 D：术语与常见误解](appendix-d.md)

## 构建

在仓库根目录运行 `python scripts/bookctl.py build --product grok --lang zh`。输出位于 `yuyu-book/dist/`，前缀为 `yuyu-grok-zh`。

本书为独立教程，与 SpaceXAI 无隶属关系。上游代码与书籍内容采用各自许可；示例只用 Python 标准库。
