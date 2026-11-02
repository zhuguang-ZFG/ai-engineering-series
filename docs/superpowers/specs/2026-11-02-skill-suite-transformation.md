# Spec：skill 套件改造——stack-diagram / dsh-guizang-design / handraw-style

- 日期：2026-11-02
- 状态：草案 → 用户过目后按计划逐轮执行
- 用户原始指令（逐字）：安装 caru-ini/stack-diagram、op7418/dsh-guizang-design、yang0/handraw-style 三个仓库为 skills；使用这些 skills 彻底改造这个项目，改造前列出 specs；逐级迭代改进优化提升书籍视频质量；到达经典级趣味可读生动形象，简单易懂，过目不忘，由浅入深。

## 1. 已完成的安装（G1/G2）

仓库统一克隆在书仓外 `D:/Users/claude/skills-src/`（不进书仓，不碰 repo-rules 的资产红线）：

| 上游仓库 | 本地克隆 | 装入的 skill（global） | 形态备注 |
|---|---|---|---|
| caru-ini/stack-diagram | `skills-src/stack-diagram` | `stack-diagram` | 单 skill，脚本+模板在克隆内 |
| op7418/dsh-guizang-design | `skills-src/dsh-guizang-design` | `humanizer-zh`、`guizang-page-skill`、`guizang-social-card-skill`、`guizang-ppt-skill` | dsh 插件五 skill 中装四；`guizang-voice`（语气档案，学用户 DeepSeek 语料）在本环境无意义，跳过 |
| yang0/handraw-style | `skills-src/handraw-style` | `handraw-style-suite`（15 子 skill 路由层） | 已装的 `handdraw-style-prompter` 是本书定制精简版（styles/colors/book-contract），继续承担书内插图；suite 负责其范围外请求 |

## 2. 能力面 × 本书杠杆映射

### 2.1 handraw-style（handdraw-style-prompter + suite）

现状：33 份 SVG（章徽 ch01–ch15 + 篇题 p1–p4 + 附录 3 + front/cover/keeper）+ 7 幅章内内容图版（ch01-five-pillars、ch02-turn-loop、ch03-tool-bench/tool-pipeline、ch04-gate-steps、ch07-four-levels、ch08-hook-line），基准配方 FD-001 东亚墨线 + C-32 炭黑 + C-15 朱砂，全部过 `art.py` 硬契约。

杠杆：
- **R1 内容图版铺开**：尚无章内图版的章：ch05、ch06、ch09、ch10、ch11、ch12、ch13、ch14、ch15。用上游 `article-illustration-planner` 的「认知降负 + 高保真图替繁文 + 插入点规划」方法逐章规划 ≥1 幅内容图版（四红线：不摆拍、不拟人、不阉割知识、不做文字搬家；间距 400–1200 字）；隐喻与构图先登记 `references/book-contract.md`，再生图/手绘 SVG。
- **信息图版式**：上游 IG 系列（35 种信息图）为高密度表格→图版转译提供版式语汇，仍走本书硬契约（单 svg 根、currentColor、禁 script/style/id/href/url()、≤6000B）。
- **视频封面**：`article-cover-designer` 的视频封面模式（字幕/大纲 → 隐喻 → 网感封面）服务衍生视频物料。

### 2.2 dsh-guizang-design（四 skill）

- **humanizer-zh → 译腔清理**：31 条模式清单直接对打本书 translationese 积压（前轮记录 zh 132/162、en 554/801）。铁律：信息零增零漏、确定性零变——术语、版本号、页数、测试计数绝不动；标题层级不动（防锚点破坏）。
- **guizang-page-skill → 样章精排网页**：把代表性章节排成杂志风/瑞士风单页 HTML 作为传播物料；其 embed SVG 色彩规则（currentColor / var(--accent) / 禁写死色）与本书契约同构，经验可回流。
- **guizang-social-card-skill → 每章知识卡**：3:4 组图（章钩子 + 核心机制 + 一图流回收），宣传物料；产出进 `docs/` 或仓外，不进 `yuyu-book/dist/`。
- **guizang-ppt-skill → 演讲/视频脚手架**：章节横向翻页稿，作为视频分镜底稿。

### 2.3 stack-diagram（约束最重）

能力：官方 logo + 白底图块 + 正交箭头的云架构图，HTML/PNG 输出。**品牌 logo 是商标、AWS 图标包再分发受限**——repo-rules 明令不嵌未授权第三方资产。因此：书内一律不用 stack-diagram 产物；它服务于作者侧的架构推演草稿（如部署/CI 拓扑自查）与可自有化的示意图设计参考。书内架构图继续 Mermaid + 本书 SVG。

## 3. 不做什么

- 不把三个仓库的脚本、图库、模板塞进书仓。
- 不改 `yuyu-book/yuyu_book/` 构建渲染管线与五道闸契约。
- 不用 stack-diagram 的 logo 产物入书；不把未授权第三方图嵌入任何随仓物料。
- humanizer-zh 不动 front matter、锚点行、表格数据、代码块。

## 4. 逐级迭代路线（G4，每轮一个 PR）

每轮固定节奏：范围内实现 → 五道闸（`build.py --check` + `--mermaid=source`、unittest 442+35、`check_book.py`、`npm run check:diagrams`）→ 账本 `revisions.json` 双语追加（末条含 `构建器测试 N 项全绿` / `N builder tests green`，N 以实际为准）→ 计划勾选 → 提交 → push → PR → CI 绿 → merge → README CI 槽位对齐（PDF 页数只认 CI 实测）。

- **R1 内容图版铺开（生动形象）**：ch01–ch15 每章 ≥1 幅章内图版；article-illustration-planner 出规划（插入点/隐喻/构图），FD-001 基准 + 逐章实时研判；`docs/illustration-prompts.md` 双语提示词同步扩充；art 审计 33→48+ 份。
- **R2 译腔清扫（简单易懂）**：humanizer-zh 逐段编辑 zh 全书（命中基线 132），en 随后（基线 554）；只修表达不动事实；锚点行数变化用 `scripts/shift_anchors.py --after N --delta M`（先 dry-run）；en 维持既有 1 行漂移约定。
- **R3 记忆点工程（过目不忘/由浅入深）**：每章开头一句话钩子、章尾三句回收（由深回浅）；术语首现即 glossary 联动；难度梯度在篇/章导语显式化。文字行数变化集中在本轮，锚点一次性平移。
- **R4 衍生物料（趣味可读）**：每章 3:4 知识卡 + 样章精排单页 HTML + 视频封面草案；自有 SVG 元素复用，零第三方 logo。
- **R5 复盘与终验（经典级）**：五道闸全绿 + 双语行级同步 + 账本完整 + 阅读性抽查；回归本轮全部验收条目。

## 5. 验收标准（终态）

| 目标维度 | 可验收证据 |
|---|---|
| 生动形象 | 每章 ≥1 章内图版，全部过 art 契约与 diagrams 审计 |
| 简单易懂 | translationese 命中显著下降（目标 zh <30、en <200，复查工具计数为准）；术语首现有解释 |
| 过目不忘 | 每章有钩子 + 回收结构；章徽-图版-回收三者隐喻互指 |
| 由浅入深 | 篇章导语写明前置依赖与难度梯度 |
| 趣味可读 | 衍生知识卡/样章网页成套，可离线打开 |
| 经典级 | 五道闸全绿、双语行级同步、账本齐、CI 长期绿 |

## 6. 风险与对策

- **PDF 页数漂移**：任何正文增删行都会顶页界（本轮教训：en 526→527）。对策：每轮 merge 后重对 README CI 槽位，数字只取 CI 日志。
- **锚点断裂**：文字/图版插入改变行号。对策：`shift_anchors.py` dry-run 先行；manifest 锚点与 gloss 锚点分区核对。
- **行级同步破坏**：zh/en 段落错位。对策：每轮双语同批编辑；check_book 的行级断言兜底。
- **物料版权**：只用本书自有 SVG 元素与上游 MIT 授权的版式思想，不嵌第三方商标位图。
