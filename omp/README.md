# 《Omp 从入门到精通：原理与实战》

> **丛书分册（施工中）** · 与同仓《御舆：解码 Agent Harness》并列  
> 产物前缀约定：`yuyu-omp-*`（HTML/PDF；Book CI 已有独立 `omp` job，见 [BUILD.md](BUILD.md)）  
> **非官方**：本书与 oh-my-pi / Stencil Labs / can1357 **无隶属关系**，亦不代表 Claude / Anthropic。

Omp（命令 `omp`）是开源终端 AI 编程 agent，源自 [oh-my-pi](https://github.com/can1357/oh-my-pi)（官网 [omp.sh](https://omp.sh)）。本分册面向**完全新手**，路线是**先原理、再实战**：讲透 agent = 模型 + 工具 + 循环，再带你从安装用到扩展、排错与读源码。

## 与《御舆》的关系

| | 《御舆》 | 本分册（Omp） |
|--|---------|---------------|
| 对象 | Claude Code 的 Agent Harness（源码级解剖） | 开源 `omp` 的入门 → 精通教程 |
| 章数 | 15 章 + 4 附录（构建契约冻结） | 33 章 + 附录 A–E（独立修订） |
| 插画 | 车舆矢量 + Mermaid | **双轨**：架构图补 Mermaid；概念漫画保留 handraw 手绘 |
| 语言（当前） | 中英 | **先只中文**；英文 `en/omp/` 延后 |
| 构建 | `make book` / `make book-pdf` → `yuyu-agent-harness-*` | `make book-omp` → `yuyu-omp-zh.html`；`make book-omp-pdf` 多出 A4 PDF；等价命令 `python scripts/bookctl.py build --product omp --lang zh [--pdf]`，见 [BUILD.md](BUILD.md) |

概念上可对照阅读（循环、工具、权限、记忆、MCP、Skills…），但**实现与钉版不同**：不要把御舆里的 Claude Code 数字原样当成 omp 行为。
对照表在仓内，不在仓库外：逐章关系是 [`omp/overhaul/CROSSREF-MAP.md`](overhaul/CROSSREF-MAP.md)（33 行，可机器校验），
读者入口是 [`docs/COMPARE-OMP.md`](../docs/COMPARE-OMP.md)，逐词共享表是 [`docs/yuyu-overhaul/SHARED-TERMS.md`](../docs/yuyu-overhaul/SHARED-TERMS.md)。

## 版本钉

| 用途 | 版本 | 说明 |
|------|------|------|
| 写作钉 | **omp/18.15.0** | 书中默认命令与数字以此为准 |
| 本机核对 | **omp/18.16.0** | 作者 Windows · Bun 全局 `%USERPROFILE%\.bun\bin\omp.exe` 已冒烟；见 [VERIFY.md](VERIFY.md) |

发版很快，读任何一章前先跑 `omp --version`，并以附录 E / VERIFY 为准。

## 目录（稿件落盘）

章节文件暂与 `images/` **同级**（正文里图片路径是 `images/fig…`，先不拆篇目录以免断链）。篇结构以 [outline.md](outline.md) 为准。

### 第一篇 · 打地基（原理）

- [第01章](ch01.md) · [第02章](ch02.md) · [第03章](ch03.md)

### 第二篇 · 上手

- [第04章](ch04.md) · [第05章](ch05.md) · [第06章](ch06.md) · [第07章](ch07.md)

### 第三篇 · 工具箱

- [第08章](ch08.md) … [第13章](ch13.md)

### 第四篇 · 上下文与记忆

- [第14章](ch14.md) … [第18章](ch18.md)

### 第五篇 · 扩展

- [第19章](ch19.md) … [第23章](ch23.md)

### 第六篇 · 实战

- [第24章](ch24.md) … [第29章](ch29.md)

### 第七篇 · 精通

- [第30章](ch30.md) … [第33章](ch33.md)

### 附录

- [A 命令行参数](appendix-A.md) · [B 斜杠命令](appendix-B.md) · [C 配置项](appendix-C.md) · [D 术语表](appendix-D.md) · [E 版本追踪](appendix-E.md)

### 元数据

- [outline.md](outline.md) · [VERIFY.md](VERIFY.md) · [resources.md](resources.md) · [BUILD.md](BUILD.md) · `facts/`（摘录切片，非全书）

## 本目录不包含

- `omp-src/` 源码树（用 sources / 上游仓库钉 tag，不进书仓）
- `handraw-style` skill 整树（配图已导出在 `images/`；署名见 CREDITS 后续补区）
- API key、`secrets.yml`、本机绝对路径隐私

## 许可

默认随本仓 [CC BY-NC-SA 4.0](../LICENSE)。第三方商标与 CLI 再现不影响「非官方」声明。
