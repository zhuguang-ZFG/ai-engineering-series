# 《Pi Agent：从原理到实战》

> **丛书第三分册 · 插件章节已扩写** · 与《御舆：解码 Agent Harness》《Omp 从入门到精通》并列
> 写作钉：**pi/1.5.0**（提交 `f9a2636`），证据与复现命令见 [PIN.md](PIN.md)
> **非官方**：本书与 Earendil Inc.、Pi 维护者及贡献者无隶属关系。

Pi（命令 `pi`，官网 [pi.dev](https://pi.dev)，仓库 [earendil-works/pi](https://github.com/earendil-works/pi)）是一个"可以做小"的终端 AI 编程 agent：
内置工具少，其余能力交给扩展、技能、提示模板和包。本分册讲两件事：**它怎么运转**，以及**你怎么把它改成自己的样子**。

## 现在的状态

| 部分 | 状态 |
| --- | --- |
| 身份与版本钉（PIN.md） | 已核实，2026-11-08 |
| 目录与证据表（outline.md） | 已落盘，25 章 + 附录 A–E 的骨架 |
| 前言 + 25 章 + 附录 A–E | 已落盘；v0.2.0-wip 扩写第 14、15、18 章 |
| 通俗层（词条 / 眉批 / 档位 / lead band） | 已接入：12 词、31 条眉批、156 枚芯片、218 处标记 |
| 主题索引 | 已接入：37 个词条，新增 pi-purge |
| 插画 | 48 份手绘 SVG（31 枚单元章徽 + 6 幅篇题刻 + 11 幅正文长图） |
| 构建（HTML / PDF / EPUB / CI） | 已接入：`make book-pi` / `-pdf` / `-epub` / `-all`；CI 有独立 `pi` job |
| 英文版 | 未开始（`langs: ["zh"]`） |

31 个单元已成稿，构建、主题索引和离线产物已跑通。第 14、15、18 章已补充插件实战，其余章节仍需继续修订；英文版尚未开始。
没有占位章节——`outline.md` 里每一行都指向真实正文。

## 和另两册的关系

| | 《御舆》 | 《Omp》 | 本册（Pi） |
| --- | --- | --- | --- |
| 对象 | Claude Code 的 harness（源码级解剖） | 开源 `omp`（oh-my-pi）入门 → 精通 | 上游 Pi 的机制与改造 |
| 章数 | 15 章 + 4 附录（契约冻结） | 33 章 + 附录 A–E | 25 章 + 附录 A–E（初稿） |
| 语言 | 中英 | 先中文 | 先中文（英文未开始） |
| 版本钉 | 见该册 README | omp/18.15.0 | **pi/1.5.0** |
| 起点 | 已有 agent 使用经验 | 完全新手 | 会用一个 agent，想弄懂并改造它 |

三册共享的是**问题清单**（循环怎么转、工具怎么执行、上下文怎么装、权限边界在哪、扩展挂在哪），
不是实现细节。不要把御舆里的 Claude Code 数字、Omp 里的 `omp` 旗标搬到 Pi 上；Pi 连"内置权限系统"
都没有，这一条就足以让很多类比失效。逐章对照见 `outline.md` 最后一节。

## 怎么读

1. **第一篇（1–3 章）**先认识这台机器：它砍掉了什么、装好之后第一圈怎么转、模型和凭据从哪来。
2. **第二篇（4–8 章）**是每天都要用的：输入、会话树、上下文来源、压缩、把结果带走。
3. **第三篇（9–13 章）**往下拆：一次 turn、模型层、工具层、会话格式、TUI。
4. **第四篇（14–19 章）**动手改：扩展事件链、可运行工具、技能、模板与主题、包、SDK 与 RPC。[第 18 章](ch18.md) 完整讲 pi-purge 的安装、三种提示词模式、版本差异、关闭与移除。
5. **第五篇（20–23 章）**是实战：真实交付、无头自动化、不可信仓库、排错。
6. **第六篇（24–25 章）**收束：源码地图、三册对照。

附录 A–E 是速查：命令行、斜杠命令与键位、配置与环境变量、术语、版本追踪。

## 本目录包含

- [PIN.md](PIN.md)：钉版、来源、包地图、复现命令
- [VERIFY.md](VERIFY.md)：本机逐条验证记录（命令 → 原始输出 → 结论）
- [outline.md](outline.md)：篇 / 章 / 节骨架与每章的证据锚点
- [BUILD-PLAN.md](BUILD-PLAN.md)：接入 yuyu-book 的改动清单与构建记录
- [examples/](examples/README.md)：Git 状态扩展与 pi-purge 离线复现实验
- [facts/](facts/README.md)：`VERIFY.md` 引用的原始输出切片
- [00-前言.md](00-前言.md)
- [ch01.md](ch01.md) … [ch25.md](ch25.md) · [appendix-A.md](appendix-A.md) … [appendix-E.md](appendix-E.md)

## 本目录不包含

- `pi-src/` 源码树（按 [PIN.md](PIN.md) 的 tag 自己拉，不进书仓）
- 上游许可证之外的第三方素材、生成的插画、API key、本机绝对路径
- 英文稿与人工二稿

## 构建与产物

```bash
make book-pi        # yuyu-book/dist/yuyu-pi-zh.html
make book-pi-pdf    # 再加 yuyu-pi-zh.pdf
make book-pi-epub   # 再加 yuyu-pi-zh.epub
make book-pi-all    # HTML + PDF + EPUB
```

本机 2026-11-09 实测：HTML 1.4 MB；PDF 9.33 MB、174 页、41 个书签、18 个索引页脚；EPUB 1.31 MB（EPUBCheck 0 错误）；31 个 unit、34 张图（23 Mermaid + 11 手绘长图）、
221 处术语标记、31 条 lead band、156 枚档位芯片、31 条眉批。构建口径与改动清单见 [BUILD-PLAN.md](BUILD-PLAN.md)，
逐条验证记录见 [VERIFY.md](VERIFY.md)。

## 许可

正文随本仓 [CC BY-NC-SA 4.0](../LICENSE)。Pi 名称、标识与 CLI 界面的引用不改变"非官方"声明。
