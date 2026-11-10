# 提示词工程：从提问到 Agent 协作

“大模型与智能体工程”系列的通用方法册，中文技术试读版 0.1.1。前言、四篇十八章和附录 A–D 已完成，配套原创材料、离线程序、独立修复练习和三幅手绘图。在线模型 A/B、跨模型迁移和独立读者试读尚未完成。

从一份活动通知开始，练习把需求说清楚、选择材料、检查依据，再判断一次修改是否值得保留。使用的“青禾工作坊”及其人物、活动和回执均为原创虚构教学材料。

从[前言](00-前言.md)选择路线。

| 篇 | 章节 |
| --- | --- |
| 把需求变成能检查的任务 | [1 明确交付](ch01.md) · [2 必要追问](ch02.md) · [3 输出与检查](ch03.md) · [4 示例选择](ch04.md) |
| 把材料组织成可用上下文 | [5 指令与原文](ch05.md) · [6 连续修改](ch06.md) · [7 选择材料](ch07.md) · [8 会话交接](ch08.md) |
| 让 Agent 的行动符合任务 | [9 中间结果](ch09.md) · [10 工具回执](ch10.md) · [11 审查与修复](ch11.md) · [12 规则与 Skill](ch12.md) · [13 多 Agent 分工](ch13.md) · [14 提示注入](ch14.md) |
| 判断改动是否值得保留 | [15 冻结评测](ch15.md) · [16 配对比较](ch16.md) · [17 环境迁移](ch17.md) · [18 独立交付](ch18.md) |
| 附录 | [A 任务与交接样稿](appendix-a.md) · [B 实验记录](appendix-b.md) · [C 工具入口](appendix-c.md) · [D 术语与资料](appendix-d.md) |

[材料版本](materials/CHANGELOG.md)、[离线练习](examples/README.md)和[验证记录](evidence/README.md)分别保留原文、操作与实际结果。出版检查及复做命令见 [VERIFY.md](VERIFY.md)。

第 1 章不用编程。第 7 章可以手工整理，也可以运行脚本。第 16 章补充文件、JSON、退出码和评审记录的操作。程序仅使用 Python 标准库，不需要模型服务或账户。

第 10–11 章的独立修复副本可以这样开始：

```bash
python prompt/examples/exercise.py prepare --out .scratch/prompt-repair
python prompt/examples/exercise.py check --project .scratch/prompt-repair --receipt .scratch/prompt-before.json
```

生成中文 HTML、PDF、EPUB 与随书练习包：

```bash
python scripts/bookctl.py build --product prompt --lang zh --pdf --epub
python scripts/package_prompt.py --output yuyu-book/dist/yuyu-prompt-zh-examples.zip
```

产物前缀为 `yuyu-prompt-zh`，位于 `yuyu-book/dist/`；不覆盖其他分册。英文版尚未编写。拿到练习 ZIP 的读者按[包内说明](PACKAGE-README.md)解压即可独立运行，无须安装构建器。

准备模型对照时，只将导出的 `request.txt` 交给待测模型。不要把全仓库、判据目录或实验根目录作为它的可读工作区。这里的目录分离便于操作，并不构成文件访问权限隔离。

与其他书的衔接见[系列定位](../docs/series/README.md)：大模型课程负责模型原理、应用实现与训练；本册展开任务与材料的连续修改；具体 Agent 的安装、权限和运行机制查对应工具分册。
