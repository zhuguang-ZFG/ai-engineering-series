# Plan：御舆项目彻底改造执行路线

对应规格：docs/superpowers/specs/2026-11-03-total-project-transformation.md

执行纪律：

- 每个阶段先补契约测试，再迁移实现。
- 每个 PR 只承担一种主要风险：数据迁移、行为重构、视觉改造或文件搬家。
- 正文改写与构建器核心重构分开。
- 所有删除先证明可重建，并保留迁移标签或清单。
- 当前未提交的 R4 改动不纳入本计划的任何平台 PR。

## P0：冻结基线与收口在途工作

- [x] P0.1 完成或独立保存当前 R4 衍生物料改动，保证平台改造从干净提交开始。
- [x] P0.2 生成 baseline.json：单元、章节、标题、锚点、术语、来源、图版、插画、HTML 体积、PDF 页数。
- [x] P0.3 保存 20 个关键 HTML 片段和 12 张关键页截图，覆盖封面、目录、正文、宽表、横版图、索引和暗色窄屏。
- [x] P0.4 建立 video 文件身份清单：source、config、review、generated、cache、third_party。
- [x] P0.5 建立 legacy 标签，记录最后一版旧构建器和视频目录。
- [x] Gate：现有 Fast 检查通过；完整依赖环境下 make check 通过；基线文件可重复生成（PR #6 → 06bd6fb）。

## P1：环境、依赖与统一 CLI

- [ ] P1.1 新增 pyproject.toml，登记 Python 3.12、包元数据、测试和工具配置。
- [ ] P1.2 引入 Python 锁文件；requirements.txt 改为从锁定环境导出或与锁文件一致性校验。
- [ ] P1.3 实现 bookctl doctor，检查 Python、Node、浏览器、字体、依赖、路径和写权限。
- [ ] P1.4 实现 bookctl check --fast，统一通用测试、构建器测试、内容检查和 Mermaid 检查。
- [ ] P1.5 Makefile 改为跨平台薄包装，clean 不再依赖 rm -rf。
- [ ] P1.6 CI 使用与本地相同的 bookctl 命令。
- [ ] Gate：全新环境的缺依赖错误在 doctor 中一次列全；Windows/Ubuntu 命令一致。

## P2：Schema、稳定 ID 与数据迁移

- [ ] P2.1 为 manifest、glosses、sources、notes、reading-paths、revisions、subject-index 定义 schema_version。
- [ ] P2.2 建立 BookModel 基础类型和统一 Diagnostic。
- [ ] P2.3 设计 block_id 语法与 Markdown 承载方式，先在 ch01、ch03、ch12 三章试点。
- [ ] P2.4 编写 line-ref → block-ref 迁移器，输出自动映射、歧义、缺失三类报告。
- [ ] P2.5 双读所有登记表，比较 line-ref 与 block-ref 指向文本是否一致。
- [ ] P2.6 全量迁移 20 个单元，加入“任意插入 50 行仍通过”的回归测试。
- [ ] P2.7 停止新增行号证据；shift_anchors.py 标记为迁移期工具。
- [ ] Gate：所有旧证据映射完成，歧义项为 0；正文插行不触发登记表 diff。

## P3：构建内核模块化

- [ ] P3.1 将 build.py 的 CLI、应用服务和产品装配拆开。
- [ ] P3.2 拆 core.py：I/O、路径、配置、模型、诊断。
- [ ] P3.3 拆 render.py：Markdown、HTML 变换、引用、图版、长名称。
- [ ] P3.4 拆 pages.py：前置页、正文单元、后置页、导航。
- [ ] P3.5 拆 style.py：令牌、屏幕、打印、组件、装饰 SVG；构建时合并内联。
- [ ] P3.6 定义 PrintManifest，让 PDF 后处理读取结构化元数据。
- [ ] P3.7 每完成一个模块，运行 legacy/v2 双构建并比较结构报告。
- [ ] P3.8 新内核成为默认后，保留旧入口一个阶段并输出弃用提示。
- [ ] Gate：结构等价报告全绿；HTML 离线、无脚本、PDF 契约全部保持。

## P4：产品生成器统一

- [ ] P4.1 建立共享设计令牌和组件语义，覆盖大书、portal、reader、gallery、cards、sample。
- [ ] P4.2 beginner reader 从读取 dist HTML 改为读取 BookModel。
- [ ] P4.3 illustration gallery、site portal、知识卡和样章改为产品适配器。
- [ ] P4.4 生成静态双语搜索索引、同段语言跳转表和概念关联表。
- [ ] P4.5 增加站点键盘、读屏、窄屏、暗色和 reduced-motion 测试。
- [ ] P4.6 对三个现有生成页执行统一视觉审计，保留御舆墨线体系。
- [ ] Gate：所有产品重跑无 diff；关闭脚本仍可完整阅读和导航。

## P5：事实与双语治理

- [ ] P5.1 建立 Claim Ledger schema 和 claim_id 规则。
- [ ] P5.2 导入版本、价格、数量、默认行为、性能数据和功能标志等高风险断言。
- [ ] P5.3 中英文段落共享 claim_id，增加单边更新失败测试。
- [ ] P5.4 增加复查周期、过期告警和发布阻断级别。
- [ ] P5.5 为 15 章补齐最小可运行案例、练习、预期结果和版本锁。
- [ ] P5.6 把事实、推断、教学简化和作者建议的标记规则写入 CONTRIBUTING.md。
- [ ] Gate：正式发布模拟中，过期高风险 claim 为 0；双语事实差异为 0。

## P6：视频工厂重建

- [ ] P6.1 根级固定唯一 HyperFrames 版本，建立 video/pipeline/。
- [ ] P6.2 定义 episode schema、scene schema、voice/caption manifest。
- [ ] P6.3 抽出长版、短版、字幕、封面和音频检查的共享步骤。
- [ ] P6.4 迁移 ch01，完成旧新时间线、字幕、时长和关键帧比较。
- [ ] P6.5 迁移 ch02–ch05，删除章节级重复构建脚本和 package.json。
- [ ] P6.6 证明 transcript、chunks、vo-manifest、字幕 HTML、音频切片可重建后停止跟踪。
- [ ] P6.7 用统一内容包扩展 ch06–ch15。
- [ ] P6.8 增加字幕一致性、安全区、字号、停留时间、闪烁、响度和版权门禁。
- [ ] Gate：15 章配置可检查；ch01–ch05 完成兼容审阅；中间物不进入 Git。

## P7：CI 与发布系统

- [ ] P7.1 抽取公共环境准备 workflow/composite action。
- [ ] P7.2 建立 Fast、Full、Release 三层任务和路径过滤。
- [ ] P7.3 缓存 Python、npm、Playwright、Mermaid 和字体资源。
- [ ] P7.4 每次构建输出 build-report.json 与 artifact-manifest.json。
- [ ] P7.5 Release 生成双语 HTML/PDF、站点包、视频清单、SHA-256 和版本说明。
- [ ] P7.6 增加生成器幂等、关键页视觉回归、链接和重定向检查。
- [ ] P7.7 合并或删除重复 workflow，README 徽章与真实门禁一致。
- [ ] Gate：PR 只跑必要层；主分支与发布层稳定；产物能追溯到 commit 和依赖。

## P8：清理、文档与正式切换

- [ ] P8.1 删除旧 line-ref 写入、旧构建入口和失效兼容层。
- [ ] P8.2 清理 video/ 中已证明可重建的中间物和重复配置。
- [ ] P8.3 更新 STRUCTURE.md、CONTRIBUTING.md、README.md、en/README.md。
- [ ] P8.4 增加架构决策记录：稳定 ID、BookModel、PDF 边界、站点脚本边界、视频资产策略。
- [ ] P8.5 从干净 clone 完成 Windows 与 Ubuntu 双平台演练。
- [ ] P8.6 发布首个新架构版本并保留 legacy 标签与迁移说明。
- [ ] Gate：规格第 7 节全部验收；旧路径无调用者；正式发布产物可下载、可校验。

## 建议 PR 切片

| PR | 范围 | 主要风险 |
|---|---|---|
| 1 | P0 基线与视频身份清单 | 无行为变化 |
| 2 | pyproject、锁文件、doctor | 环境 |
| 3 | bookctl check 与 CI 对齐 | 工具入口 |
| 4 | Schema + BookModel 骨架 | 数据读取 |
| 5 | 三章稳定 ID 试点 | 证据绑定 |
| 6 | 全量稳定 ID 迁移 | 数据迁移 |
| 7–9 | 构建器按 core/render/style-pages 拆分 | 输出等价 |
| 10 | PDF PrintManifest | 分页与书签 |
| 11–12 | reader/gallery/portal/cards 统一 | 产品输出 |
| 13 | Claim Ledger | 内容治理 |
| 14–16 | 视频 ch01、ch02–05、ch06–15 | 媒体迁移 |
| 17 | CI 三层与发布清单 | 发布 |
| 18 | 删除兼容层与文档收官 | 清理 |

## 每个 PR 的完成定义

- [ ] Spec 对应条目有测试或可复核证据。
- [ ] 通用测试、构建器测试、内容检查、Mermaid 检查通过。
- [ ] 涉及输出时，生成器连续运行两次无 diff。
- [ ] 涉及双语内容时，中英文同批更新。
- [ ] 涉及视觉或 PDF 时，附关键页比较。
- [ ] 涉及删除时，附可重建证明和删除清单。
- [ ] 不提交 dist、缓存、中间媒体或第三方工具副本。
- [ ] 更新相关结构文档，不在修订账本中写无法重算的数字。

## 推荐执行顺序

先完成 P0–P2，消除环境和行号锚点这两个会放大后续改动成本的问题；随后执行 P3–P4，建立统一内核和产品适配器；再做 P5 内容治理与 P6 视频工厂；最后用 P7–P8 收拢 CI、发布和旧代码。P2 未完成前不开始大规模正文扩写，P3 未稳定前不做全站视觉换骨，P6 不与 PDF 内核迁移并行。

