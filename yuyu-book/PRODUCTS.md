# yuyu-book products

| product | 书 | manifest | 产物前缀 | bookctl |
|---------|----|----------|----------|---------|
| `book` | 《御舆：解码 Agent Harness》 | `manifest.json` | `yuyu-agent-harness-*` | `build --product book`（现网；`make book`） |
| `omp` | 《Omp 从入门到精通：原理与实战》 | `manifest-omp.json` | `yuyu-omp-*` | `build --product omp --lang zh`（`make book-omp` / `make book-omp-pdf`） |
| `pi` | 《Pi Agent：从原理到实战》 | `manifest-pi.json` | `yuyu-pi-*` | `build --product pi --lang zh`（`make book-pi` / `book-pi-all`） |

三个 product 各有一套通俗层登记表：`plain.registry_names()` 按 manifest 的 `product` 字段
取同名兄弟文件——御舆用裸名（`glosses.json` / `notes.json` / `reading-paths.json`），
omp 用 `-omp` 后缀，pi 用 `-pi` 后缀（`glosses-pi.json` / `notes-pi.json` / `reading-paths-pi.json`），
写第二分册的通俗层不会顺手改到第一分册。`omp` 过去走 `--no-plain` 整层跳过，M2 之后已不传该
开关；`--no-plain` 仍是 `build.py` 的正式开关，留着出「无通俗层」对照排版。插画双轨：正文
`omp/images/` 手绘嵌入 + Mermaid 管道。不要用 `make book` 编 omp。

## Omp 英文开启条件

`en/omp/` 当前只有预留说明，`manifest-omp.json` 保持 `langs=["zh"]`。
开启英文需按以下顺序完成：

1. 翻译前言、33 章和五篇附录，为 39 个 unit 增加真实的 `en` 源路径。
2. 补齐 guides、glosses、notes、reading-paths 的英文内容及插画标签；核对双语结构与引用，检查未翻译汉字。
3. 将 manifest 的 `langs` 扩为 `['zh', 'en']`，同时更新产品隔离测试中「仅中文」的明确断言。
4. 对 omp 跑双语 `--check` 与 HTML/PDF 构建，再扩 CI 的语言覆盖；御舆仍保留自己的 20 单元契约。

`shared_with` 是 omp 词条到御舆词条的对照 ID，不参与正文替换，也不让构建器合并两册登记表。
对照面来源独立登记，不能用它支撑 omp 的 CLI 行为。

## Pi 分册

`pi` 是第三分册，31 个 unit（1 前言 + 25 章 + 5 附录），中文单语，写作钉 **pi/1.5.0**。
它与另两册共用构建器，但登记表、插画托盘（`yuyu-book/illustrations-pi/`，43 份）和产物前缀都是自己的：
`make book-pi` 只编 pi，`make book` / `make book-omp` 不会碰它。

通俗层已经接入：12 个词条、31 条 lead band、31 条眉批、156 枚档位芯片、218 处虚线术语标记。
不排主题索引（`subject_index_registry: null`）。英文版尚未开始；`langs` 只有 `zh`。
构建口径、页数与体积见 `pi/README.md` 与 `pi/VERIFY.md`，接入改动清单见 `pi/BUILD-PLAN.md`。
