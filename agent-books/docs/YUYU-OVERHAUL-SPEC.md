# 《御舆：解码 Agent Harness》彻底改造 SPEC（可执行计划）

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development`（推荐）或 `superpowers:executing-plans` 按任务逐项落地。步骤使用 checkbox（`- [ ]`）跟踪。  
> **版本**：v1.0 · 日期：2026-11-03（America/Adak）  
> **状态**：仅 SPEC；**提交 / 推送稍后做**（本文件明确禁止在未获另令前 `git commit` / `git push`）。  
> **姊妹 SPEC**：`omp/OVERHAUL-SPEC.md`（Omp 分册改造；与本文件同等级、可并行，但互不覆盖对方真源）。  
> **依据**：本机仓 `STRUCTURE.md`、`README.md`、`CONTRIBUTING.md`、`yuyu-book/`（含 `PRODUCTS.md`、`manifest.json`、`glosses.json`、`notes.json`、`reading-paths.json`）、`.github/workflows/{book,check-book,pages}.yml`、`scripts/bookctl.py`、`docs/{portal,beginner-reader,illustration-gallery}*`、`omp/FUSION-PLAN` 拍板（同仓第二分册 · `yuyu-omp` · 先中文 · Mermaid+手绘 · **不伤 `make book`**）、分支 `p3-pages-split` 本地脏改动快照。

**Goal:** 把主分册《御舆》从「已可双语出书的成熟稿」推进到「通俗层真正降低门槛、插画/站点/测试契约与 omp 分册长期并存、构建器本地重构可稳态交付」的正式状态；**全程保证 `product=book` / `make book` 不回归**；本 SPEC 执行期内**不**强制 commit/push。

**Architecture:** 内容通俗化、插画与入门分册、构建器/CI 契约、站点双入口、与 omp 术语/互链五条线按里程碑串行验收、允许标明的并行；御舆继续钉 **20 单元**契约与 `yuyu-agent-harness-*` 产物前缀；omp 一律走 `product=omp` + `manifest-omp.json` + `yuyu-omp-*`，不得污染御舆单测断言。

**Tech Stack:** 双语 Markdown（zh 四部分+附录 / `en/` 镜像）· `yuyu-book` / `scripts/bookctl.py` · Makefile `book`/`book-pdf` · Mermaid 预渲染 + `illustrations/*.svg`（`currentColor`）· `glosses.json` / `notes.json` / `reading-paths.json` · GitHub Actions（`book.yml` / `check-book.yml` / `pages.yml`）· `docs/beginner-reader*.html` · `scripts/measure_translationese.py` · 姊妹分册 `omp/`

## Global Constraints

### 姊妹分册收尾复验（2026-11-05）

Omp M3–M8 的本地交付已补齐，记录见 `omp/overhaul/ACCEPTANCE.md`。
本轮御舆中文 HTML 渲染成功，20 单元契约不变；共享 `check --fast` 六步通过，
通用测试 46 项、构建器测试 515 项。跨册引用与双语结构检查均通过。
旧验收记录与 M0 暂存偏差保留为历史，不用本轮结果改写当时发生的事。

### 发布授权更新（2026-11-04）

用户已授权提交、推送、合并，待 CI 通过后继续完成所有 SPEC 目标。
本授权取代下文原执行期的「提交推送稍后」限制；旧验收记录保留为当时的事实。
剩余目标须有实际交付与验证后再勾选，不能以获准发布代替完成。

1. **仓形态**：保持 `claude-code-book`；主分册路径与 20 单元 id（`front`/`ch01`–`ch15`/`apxa`–`apxd`）不得无迁移方案地改名；第二分册仅 `omp/`。
2. **产物前缀**：御舆仅 `yuyu-agent-harness-{zh,en}.{html,pdf}`；omp 仅 `yuyu-omp-*`。禁止混写进对方 dist 文件名或 README 数字宣称。
3. **不伤 `make book`**：任何里程碑结束后，本地必须能：
   - `python scripts/bookctl.py build --product book --lang zh`（至少）成功；
   - 推荐全量：`make book` 或 `bookctl build --product book --lang both`；
   - 御舆相关单测（`yuyu-book/tests/` 中钉 20 单元 / notes / plain / docclaims 的断言）不得被改成「含 omp 单元」。
4. **语言**：本 SPEC **必须**维护中英两侧契约（与 omp「先中文」不同）；改 guides/notes/glosses 时两侧证据与字数门禁同时过。
5. **插画契约**：章徽/题刻/扉页继续走 `art.py` 的 `currentColor` SVG 门禁；正文架构图继续 Mermaid。不把 omp 手绘 JPG 灌进御舆 `illustrations/`。概念漫画增强优先落在 `docs/illustration-gallery` / 入门分册，不破坏整书 SVG 体积上限。
6. **内容真源**：构建器只读书稿；禁止用脚本「美化」后回写正文（`STRUCTURE.md` 两层契约）。行号证据迁移走既有 `migrate.py` 流程，不得手改悬空 `file:line`。
7. **与 omp 隔离数字**：御舆可保留 55 工具 / 89 Flag 等**已有**钉版论述；**禁止**为了「对称」把 omp 命令表塞进 01–15 章正文。交叉引用只用「参见 omp 分册第 M 章」短链 + `omp/COMPARE-YUYU.md`（或本 SPEC 落地的对照文）。
8. **Git**：**提交推送稍后**——完成本 SPEC 各阶段落盘与本地验收即可；`git commit` / `git push` / 开 PR **不在本 SPEC 自动步骤内**，须用户另令。当前分支 `p3-pages-split` 已有大量未提交重构，提交策略与 omp 是否同 PR **稍后确认**。
9. **非官方声明**：Claude Code 为 Anthropic 产品；本书独立分析、非官方。封面/前言/README 既有声明保持。
10. **文风**：由浅入深；先场景/故障再源码；禁空话；中文过 translationese 门（`被`+汉字等）；英文禁夹汉字（notes 既有门禁）。

---

## 0. 目标 / 非目标

### 0.1 目标

| ID | 目标 | 可观察结果 |
|----|------|------------|
| G1 | 通俗门槛下降 | 入门阅读路线（前言三条路径）可实操；`docs/beginner-reader.html` 与正文 guides/plain 对齐；抽 5 章「开场两段」可让零基础读懂「这章解决什么」 |
| G2 | 通俗层可审计 | 20 条 guides 的 question/deliverable/boundary/plain/analogy 经 QA 清单；glosses 证据无悬空；notes 20/20 术语锁通过；`--no-plain` 与开 plain 双构建均绿 |
| G3 | 插画与入门分册同步 | 42 枚 SVG 契约不破；gallery / prompts / beginner-reader 与当前章一致（`git diff --exit-code docs/` 在再生后为干净，或有意差异写入验收例外表）；Mermaid zh/en 围栏数继续对齐（现各 160） |
| G4 | 构建 / CI / PDF 稳态 | 本地重构（`deco.py`/`labels.py`/`style_css.py` 等）收敛后 `make book` + `make book-pdf`（或 bookctl 等价）可重复；workflow **配置**写好 product 隔离与 paths；**真绿留待稍后 push** |
| G5 | 站点双入口 | `docs/portal.html` / README 明确「御舆 · Omp」双书；pages 构建步骤文档化；**不**要求本阶段 omp 已进 pages matrix（可与 omp SPEC M4 对齐后另令） |
| G6 | 测试契约硬化 | 20 单元断言不被 omp 污染；新增或加固「product=book 只看见 20 units」测试；`test_docclaims` / `test_notes` / `test_plain` 全绿 |
| G7 | 与 omp 协同 | 共享术语表落盘；互链短文；STRUCTURE/README/PRODUCTS 描述双产品；改共享构建代码时两边 smoke |
| G8 | 双语质量 | `measure_translationese.py` 基线入库；中英结构对拍（标题/围栏数/罗盘字段）；EN notes 零汉字 |

### 0.2 非目标（本 SPEC 明确不做）

1. **不**把 omp 33 章嵌进御舆 Part 1–4，不改 15 章叙事弧为「omp 教程」。
2. **不**默认交付「御舆+omp 合订 PDF」。
3. **不**在本 SPEC 内执行 `git commit` / `git push` / 合并 PR（**提交推送稍后**）。
4. **不**把 omp 手绘 FA-023 风格整套迁入御舆章徽体系。
5. **不**自动追 Claude Code / Anthropic 最新 release 改钉；漂移记入 revisions / 验收例外，不 silently 改数字。
6. **不**删除或关闭通俗层；`--no-plain` 仅作对照开关，不是默认交付。
7. **不**在书稿或 CI 日志写入 API key / 私有源码路径 / 本机绝对路径作为「读者必做步骤」。
8. **不**要求本阶段重写全部 15 章正文（以通俗化补丁 + 薄弱段加强为主，见 M1 批次表）。

---

## 1. 现状快照与缺口清单

### 1.1 已具备（勿推倒重来）

| 项 | 位置 / 证据（本机 `D:\Users\claude\claude-code-book-main`，2026-11-03 扫描） |
|----|-------------|
| 20 单元双语书稿 | `00-前言.md` + 四部分 15 章 + 附录 A–D；`en/` 一一对应 |
| 章长已厚 | 多数章 17k–44k 字符（UTF-8）；非 omp 式「薄初稿」问题 |
| Mermaid | zh 160 / en 160 围栏 |
| 通俗层 | `glosses.json` ≈ 102 词条；`notes.json` 20 单元；`reading-paths.json`；manifest `guides` 20 |
| 插画 | `yuyu-book/illustrations/` 42 文件（章徽/题刻/正文板/keeper/cover） |
| 构建产物 | `dist/yuyu-agent-harness-{zh,en}.{html,pdf}` 已存在；README 宣称约 zh 505 页 / en 536 页（CI Noto）—以本机实机构建日志为准重钉 |
| 入门分册 / 站点素材 | `docs/beginner-reader.html`、`.en.html`、`illustration-gallery.html`、`portal.html`、`illustration-prompts.md` |
| CI | `book.yml`（双语 PDF + docclaims）、`check-book.yml`、`pages.yml`（再生 reader/gallery 并 `git diff --exit-code docs/`） |
| 测试 | `yuyu-book/tests/` 大量契约测；根 `tests/`（star_history 等） |
| 分册脚手架 | `omp/` 已入仓未提交；`make book-omp` / `book-omp-pdf`；`PRODUCTS.md`；**`make book` 仍只编御舆** |
| 分支 | `p3-pages-split`；大量 `M`（bookctl/yuyu_book 重构）+ `?? omp/` + `?? OVERHAUL-SPEC.md`（根上误放的是 **omp** SPEC 副本，御舆 SPEC 应落 `docs/YUYU-OVERHAUL-SPEC.md`） |

### 1.2 缺口（按改造优先级）

| ID | 缺口 | 证据 | 归属阶段 |
|----|------|------|----------|
| K1 | 零基础友好度不足：源码密度高，开场偏「已经懂 agent」 | 章首常直接进实现；入门分册与整书 guides 可能漂移 | M1 |
| K2 | guides/plain 质量未做「omp 式」反抄袭 QA | 字段齐全但缺 `GUIDES-QA` 清单；deliverable 是否可检查未统一 | M2 |
| K3 | glosses 证据 / why_evidence 随正文改动易悬空 | 本地大改 render/plain 后需全量 `validate_plain` | M2 |
| K4 | 插画再生与 prompts 手册可能过期 | pages.yml 依赖 `git diff --exit-code docs/`；本地脏树时站点契约未跑 | M3 |
| K5 | `STRUCTURE.md` / README 未完整描述双 product；README 仍写 omp「尚未接入 make book」过时 | README「第二分册」段 vs 已有 `book-omp` | M5 |
| K6 | CI paths / matrix **未**含 `omp/`；pages 未部署 omp 产物 | `book.yml` paths 无 `omp/**`；无 product matrix | M4（配置）+ 稍后 push |
| K7 | 本地 yuyu-book 重构未收敛验收（`deco.py`/`labels.py`/`style_css.py` 等 `??`） | `git status` | M4 |
| K8 | 测试未显式隔离 `product=omp` | 现有测试默认 book；存在 omp 装载后误扩 unit 数风险 | M6/M8 |
| K9 | 与 omp 术语共享 / 互链未落御舆侧 | 仅 FUSION / omp SPEC 提及 | M7（互链章号已按 `CROSSREF-MAP` 校正，见 Step 0；共享词表仍未落） |
| K10 | translationese 基线未写入 overhaul 验收 | 有 `measure_translationese.py`，缺 BASELINE 数字 | M1 / M8 |
| K11 | 根目录 `OVERHAUL-SPEC.md` 内容实为 **omp** SPEC，易误导执行者 | 文件头 Goal 写 omp | M0：归档说明 + 本文件为准 |
| K12 | 提交推送与 CI 真绿未做 | 用户拍板稍后 | §6 + M9 |

### 1.3 文件职责地图（改造时触碰范围）

```text
claude-code-book-main/
├── 00-前言.md
├── 第一部分-基础篇/ … 第四部分-工程实践篇/   # ★ 御舆正文真源（M1 谨慎改）
├── 附录/ A–D.md
├── en/                                      # ★ 英文镜像（与 zh 同步改）
├── docs/
│   ├── YUYU-OVERHAUL-SPEC.md                # ★ 本文件（本机真源之一）
│   ├── portal.html / beginner-reader*.html / illustration-gallery.html
│   └── illustration-prompts.md
├── docs/yuyu-overhaul/                      # M0+ 基线与清单（本 SPEC 创建）
├── yuyu-book/
│   ├── manifest.json / glosses.json / notes.json / reading-paths.json
│   ├── sources.json / revisions.json / subject-index.json
│   ├── illustrations/                       # currentColor SVG
│   ├── PRODUCTS.md                          # book | omp
│   ├── manifest-omp.json …                  # 只读协同；内容归 omp SPEC
│   └── yuyu_book/*                          # 重构收敛（M4）；改后必跑 book 测
├── scripts/bookctl.py / build_beginner_reader.py / build_illustration_gallery.py
├── scripts/build_site_portal.py / check_book.py / measure_translationese.py
├── .github/workflows/book.yml / check-book.yml / pages.yml
├── Makefile                                 # book* 保留；book-omp* 不动语义
├── STRUCTURE.md / README.md / CREDITS.md / CONTRIBUTING.md
└── omp/                                     # 姊妹分册；本 SPEC 只加互链与共享词，不改 omp 章正文
```

box 备份：`/workspace/omp-book/YUYU-OVERHAUL-SPEC.md`（及可选 `docs/` 镜像）。**真源优先级**：本机仓 `docs/YUYU-OVERHAUL-SPEC.md` > box 备份；不以 box 覆盖本机未拉取改动。

---

## 2. 分阶段里程碑总表

| 里程碑 | 名称 | 主要交付 | 依赖 | 本地验收命令（摘要） |
|--------|------|----------|------|----------------------|
| **M0** | 冻结基线 | 基线页数/字数/测例、错置 SPEC 说明、禁 commit 确认 | — | 记录 dist 体积页数；`git status` 快照 |
| **M1** | 通俗化与薄弱段 | 开场改写批次、失败对照表、translationese 基线、Humanizer/润色日志 | M0 | 抽章阅读；`measure_translationese.py` |
| **M2** | 通俗层审计 | GUIDES-QA；glosses/notes/reading-paths 修复；双开关构建 | M1 | `build.py` 开/关 plain；相关 unittest |
| **M3** | 插画与入门分册 | 再生 gallery/reader；prompts 对齐；Mermaid 对拍 | M1 可并行 | `build_*` 脚本；`git diff docs/` 解释 |
| **M4** | 构建器收敛与 CI 配置 | 重构文件收束；`make book`/`book-pdf`；workflow 隔离 omp；**不 push** | M2+M3 部分可并行 | `ci-local-yuyu.ps1`；omp smoke 不破 book |
| **M5** | 站点与文档双入口 | portal/README/STRUCTURE/PRODUCTS | M4 文档可先 | 人工打开 portal；链接无 404 |
| **M6** | 测试契约硬化 | product 隔离测；20 unit 钉死；docclaims 绿 | M4 | `python -m unittest discover -s yuyu-book/tests` |
| **M7** | 与 omp 协同 | 共享词表、互链、COMPARE 御舆侧入口 | M2 词表形状 | 词表无 omp 专名污染御舆定义 |
| **M8** | 双语质量收口 | EN/ZH 结构对拍；translationese 阈值达标 | M1+M2 | measure 脚本 + 抽译 |
| **M9** | 总验收 | 缺口关闭；移交提交分组建议；**仍不 commit/push** | 全部 | ACCEPTANCE 签字 |

并行规则：M3 可与 M1 后半并行；M5 文案可与 M4 并行；M7 与 omp SPEC 的 M6 对齐；M4 workflow **真绿 = 稍后 push 之后**。

---

## 3. 里程碑任务（可执行）

### Task M0: 冻结基线（不改书稿正文）

**Files:**
- Create: `docs/yuyu-overhaul/BASELINE.md`
- Create: `docs/yuyu-overhaul/git-status-baseline.txt`（导出）
- Create: `docs/yuyu-overhaul/NOTE-ROOT-OVERHAUL-SPEC.md`（说明根 `OVERHAUL-SPEC.md` 实为 omp 副本）
- Modify: 无书稿正文

**Interfaces:**
- Produces: 可复述的数字与脏树清单；明确本文件路径

- [x] **Step 1: 写入 BASELINE.md**（文件已存在，2026-11-03 21:41 落盘；2026-11-04 复核并补齐：
  dist 表拆成「M0 快照」+「当前值」两张，`git-diffstat` 的 11 → **13**，脏树一节写明当前 324 个已暂存文件，
  mermaid `zh=160 en=160` 重数通过）

```markdown
# Yuyu (御舆) overhaul baseline

- Date: 2026-11-03 America/Adak
- Branch: p3-pages-split (dirty; no commit in this SPEC)
- Product: book · output_prefix: yuyu-agent-harness
- Units: 20 (front + ch01–15 + apxa–apxd)
- Glosses terms (excl schema): ~102
- Notes units: 20
- Mermaid fences: zh=160 en=160
- Illustrations files: 42
- Dist (record actual bytes/pages from local build logs or file props):
  - yuyu-agent-harness-zh.html / .pdf
  - yuyu-agent-harness-en.html / .pdf
- Omp sibling present: omp/ (untracked or dirty) · make book-omp exists
- Root OVERHAUL-SPEC.md: CONTENT IS OMP SPEC — authority for 御舆 is docs/YUYU-OVERHAUL-SPEC.md
- Commit/push: DEFERRED
```

用本机实际 `Get-Item yuyu-book\dist\*` 填体积；若有 PDF 页数工具则写入，否则写「页数以下次 `make book-pdf` 日志为准」。

- [x] **Step 2: 导出脏文件清单**（两份 txt 都在 `docs/yuyu-overhaul/`：status 24 行、diffstat 13 改 + 汇总行；
  实测可见 `yuyu-book/yuyu_book/*` 已改、`omp/` 未跟踪、根 `OVERHAUL-SPEC.md` 存在 —— Expected 命中。
  注意快照口径是 11-03 21:41，当前树况见 `BASELINE.md`「脏树快照」一节）

本机 PowerShell，仓根：

```powershell
git status -sb | Out-File -Encoding utf8 docs/yuyu-overhaul/git-status-baseline.txt
git diff --stat | Out-File -Encoding utf8 docs/yuyu-overhaul/git-diffstat-baseline.txt
```

Expected: 可见 `yuyu-book/yuyu_book/*` 已改、`omp/` 未跟踪、根 `OVERHAUL-SPEC.md` 存在。

- [x] **Step 3: 错置 SPEC 说明**（`docs/yuyu-overhaul/NOTE-ROOT-OVERHAUL-SPEC.md` 已存在；
  根文件未删除。2026-11-04 复核：两份 SPEC 已分叉（`omp/` 那份回写了进度复选框），
  该结论记在 `omp/overhaul/BASELINE.md`，以 `omp/OVERHAUL-SPEC.md` 为 omp 侧真源）

`NOTE-ROOT-OVERHAUL-SPEC.md` 写清：根文件与 `omp/OVERHAUL-SPEC.md` 同源主题（omp）；御舆执行者只打开 `docs/YUYU-OVERHAUL-SPEC.md`。**本步不删除根文件**（避免未提交误伤）；删除/改名留待用户稍后提交策略。

- [x] **Step 4: 验收**

- [x] `BASELINE.md` 存在（`docs/yuyu-overhaul/BASELINE.md`，2026-11-03 21:41 落盘、11-04 复核补齐）  
- [ ] **未**执行 `git add` / `commit` / `push` —— **commit / push 这条是真的**（`git rev-list --count
  --left-right HEAD...origin/p3-pages-split` = `0 0`，`git log -1` 仍是 `951c0ef`，见 M9 Step 4）；
  但「一次 `git add` 都没跑」**不能这么写**：`git-status-baseline.txt` 里 `OVERHAUL-SPEC.md` 与
  `docs/YUYU-OVERHAUL-SPEC.md` 当时都是 `??`，现在两个都是 `A` —— M0 之后确实有某个窗口 `git add` 过
  （从暂存面看是 omp 那一侧的轮次，不是御舆正文/文档轮次干的）。
  当时躺着 **324 个已暂存文件**（293 `A` + 31 `AM`；更早记的 296/28 是同一批的旧读数，
  总数一致，`A→AM` 的位移就是那一轮又改了其中几份）。
  用户已就「暂存索引 + `models-list.txt` 泄漏面」拍板并处置：`omp/facts/live-18.16.0/models-list.txt`
  已 `git restore --staged` 摘出索引（文件本体未动，5118 字节），并在 `.gitignore:85` 补了忽略规则；
  顺带把 89 条一次性探针产物所在的 `/.scratch/` 也忽略了（`.gitignore:91`）。
  摘完这一条，索引降到 **323 个**（13:5x 实测 292 `A` + 31 `AM`，工作区脏项合计 477）；
  14:5x 再数是 **293 `A` + 30 `AM`**——总数与脏项都没动，变的只是分布：脱敏后必须 `git add`
  刷 index blob，`omp/ch29.md` 就从 `AM` 转成了 `A`（这条机制记在 `ACCEPTANCE.md` 第 5 节第 8 条）。
  **这一格仍保持不勾**，但理由换了：不再是「等拍板」，而是「M0 之后确实有窗口 `git add` 过、
  且剩下 323 条仍在索引里」——勾了就成了文档与磁盘不一致。分布与处置选项见
  `omp/overhaul/BASELINE.md`；御舆侧的拦路清单与卸载命令见 `docs/yuyu-overhaul/ACCEPTANCE.md` 第 3 节。
  还有一个漏面归 omp 分册：`C:\Users\<用户名>` 出现在 `omp/ch04.md:115`、`omp/ch07.md:202`、
  `omp/ch29.md:3`、`omp/VERIFY.md:106` 与它引用的 `omp/facts/live-18.16.0/config-path.txt:1`，
  五处互为引用，要么一起改要么都不改。按分工它「不由御舆轮次代笔」，**14:2x 用户点头后已五处改齐**
  （`omp/ch29.md` 的时间戳 14:27 可查）：四条正文改走 `%USERPROFILE%` 或占位，那份 capture 按仓内
  `*-redacted.txt` 的先例保住输出形状与 `exit=0` 再抹账户名。这是御舆轮次唯一一次动 omp **正文**，
  且只动隐私、不动论点；14:5x 又动了同分册 4 份**证据 capture**（63 处转义路径，同样只碰隐私，
  见本节 M9 Step 3 那段）。逐条改法见 `ACCEPTANCE.md` 第 3 节拦路第 3 条。

  **17:1x 数到 483，17:5x 再数是 484**（覆盖上面 13:5x / 14:5x 两个读数，484 才是当前值）：`git status --porcelain | wc -l` = **483**，逐桶相加正好收口——`A ` **293** + `AM` **30** + ` M` **60** + `??` **100** = 483；**17:5x 复数 484**——为了追附录 D 那道汉字闸改了 `yuyu-book/tests/test_docclaims.py`（26,920 → 27,484 B，由干净转为 ` M`），于是 ` M` 60 → **61**、其余三桶不动：`A ` **293** + `AM` **30** + ` M` **61** + `??` **100** = **484**，`git log --oneline -1` 仍是 `951c0ef`、ahead/behind 仍是 `0 0`；`git log --oneline -1` 仍是 `951c0ef`，`git rev-list --count --left-right HEAD...origin/p3-pages-split` 仍是 `0 0`，也就是**这一整段御舆轮次一个 commit 都没落**，索引面自 14:5x 以来只多了工作区脏项。要提醒下一个接手的人：这 **100** 条 `??` 里躺着账本本身——`docs/yuyu-overhaul/ACCEPTANCE.md`、`PDF-PAGES.md`、`ILLUST-SYNC.md`、`BASELINE.md`、`SHARED-TERMS.md` 都还是未跟踪态，`git add` 漏了它们，提交完这份 SPEC 的历史就只剩对话记忆。复现命令：`git status --porcelain | cut -c1-2 | sort | uniq -c`。
  **18:5x 三度复数 = 486**（取代上面 484 那条「当前值」的说法）：`A ` **293** + `AM` **30** + ` M` **62** + `??` **101** = 486，`git status -sb` 非空行数 **487** = 1 行分支头 + 486 条。**这一轮 `--porcelain` 与 `--porcelain -uall` 又不同数了**（486 vs **492**，`??` 101 → 107），因为 `yuyu-book/illustrations-omp/` 是整目录未跟踪、被折叠成一条——16:49 与 17:5x 那两条「折叠情形不复存在」的说法到此作废，脏区里只要新增一个目录就会重新折叠，数文件必须带 `-uall`（7 幅 SVG 就是被这一条挡在 486 之外的）。` M` 61 → **62**：本轮写过的六个文件里，`art.py`、`test_docclaims.py`、`revisions.json`、`STRUCTURE.md`、`docs/illustration-prompts.md` 在 17:5x 已经是 ` M`，翻牌的是 `yuyu-book/tests/test_art.py`（18:31 写入）——这是**排除法**归因，17:5x 那条没留文件名清单，不算当时的对证。`docs/**` 仍 **47**、`omp/**` 仍 **366**（新增的七个文件在 `yuyu-book/**` 下，不在 docs 也不在 omp），`docs/yuyu-overhaul/logs/` 仍 **18 份**（本轮日志写在仓库外）。`git log --oneline -1` 仍是 `951c0ef`、`git rev-list --count --left-right HEAD...origin/p3-pages-split` 仍是 `0 0`——**零 commit、零 push 到 18:5x 依然成立**。
  **20:0x 四度复数 = 486（取代上面 18:5x 那条「当前值」的说法）**：`A ` **293** + `AM` **30** + ` M` **62** + `??` **101** = **486**，四个桶与 18:5x 逐桶相同，`git status -sb` 非空行数仍是 **487** = 1 行分支头 + 486。**这一轮往仓库里放了 39 个新文件（`yuyu-book/illustrations-omp/omp-*.svg` 章徽），脏项总数却一条没动**——它们落进的是一个本来就整目录未跟踪的目录，git 继续只报 `?? yuyu-book/illustrations-omp/` 那一行。于是 18:5x 那条「只要往仓库放一个新目录，折叠就回来」要补上第二半：**放在已有未跟踪目录里的文件，连折叠都不发生**。两个口径因此再次分开：`--porcelain` **486** vs `--porcelain -uall` **531**（`??` 101 → **146** = 101 − 1 条目录行 + 46 份 SVG，即 7 幅篇题刻 + 39 枚章徽；492 → 531 差的 **39** 正好是这轮新增的枚数）。` M` 之所以不翻牌：本轮写过的 **10** 个已有文件此前全都已在各自桶里——` M` 三条（`STRUCTURE.md`、`yuyu-book/revisions.json`、`docs/illustration-prompts.md`）、`AM` 三条（`omp/BUILD.md`、`docs/yuyu-overhaul/BASELINE.md`、本文件）、`??` 四条（`docs/yuyu-overhaul/ILLUST-SYNC.md`、`PDF-PAGES.md`、`ACCEPTANCE.md`、`yuyu-book/tests/test_product_isolation.py`）；那条新加的 `test_every_omp_unit_opens_with_its_own_emblem` 写在未跟踪文件内部，桶也不变。`docs/**` 用 pathspec 现数是 **47**、`omp/**` 是 **366**、`yuyu-book/**` 是 **27**，`logs/` 仍 **18 份**（本轮日志照旧写在仓库外）。这里再撞一次 `docs/yuyu-overhaul/ACCEPTANCE.md` 第 4 节早已写明的引号陷阱：`git status --porcelain | grep -c ' omp/'` 本轮现数是 **365**，比 pathspec 少 **1**，漏的还是 `A  "omp/00-前言.md"`——**数目录一律带 pathspec**（`git status --porcelain -- omp/ | wc -l`），别拿 grep 前缀当准。`git log --oneline -1` 仍是 `951c0ef`、`git rev-list --count --left-right HEAD...origin/p3-pages-split` 仍是 `0 0`——**这一整段御舆轮次到 20:0x 仍然一个 commit 都没落**。复现命令：`git status --porcelain | cut -c1-2 | sort | uniq -c`、`git status --porcelain -uall | wc -l`、`git status --porcelain -uall -- yuyu-book/illustrations-omp/ | wc -l`（= 46）。

**里程碑验收 M0:** 基线可复述；后续以本机御舆路径为真源。

---

### Task M1: 通俗化与薄弱段加强（非盲目加字）

**Files:**
- Modify（按批）: `00-前言.md`；`第一部分-基础篇/01–04*.md`；按需 `05–08`、`15`；对应 `en/**`
- Create: `docs/yuyu-overhaul/PEDAGOGY-LOG.md`
- Create: `docs/yuyu-overhaul/TRANSLATIONESE-BASELINE.txt`
- Create: `docs/yuyu-overhaul/HUMANIZER-LOG.md`

**Interfaces:**
- Consumes: 现有 callout / 练习框格式；`reading-paths.json` 起步路径
- Produces: 更易读的开场 + 翻车表；字数允许 ±10%，**禁止**为凑厚而灌水

**每章补丁强制结构（在现有结构上增量，缺则补）：**

1. 开场 ≤2 段：具体场景或故障（零基础能懂）  
2. 「读完你能干什么」三颗子弹（可与 compass deliverable 对齐，勿整段复制）  
3. 至少一张「常见翻车 / 正确做法」对照表  
4. 可选 1 短段「参见 omp 分册第 M 章」（无 omp 命令细节）  
5. 不破坏既有 `<!-- block: ... -->` 标记与 gloss 表面词形

**批次：**

| 批次 | 范围 | 目标 |
|------|------|------|
| B1 | 前言 + ch01–ch04 | 心智模型零基础可读 |
| B2 | ch05–ch08 | 子系统开场降噪 |
| B3 | ch09–ch12 | 组合模式先故事后协议 |
| B4 | ch13–ch15 + 附录 A 导读段 | 工程篇可跟做；附录 A 加「先看哪张图」 |

- [x] **Step 1: translationese 基线**

```powershell
python scripts/measure_translationese.py | Tee-Object docs/yuyu-overhaul/TRANSLATIONESE-BASELINE.txt
```

Expected: 退出 0；数字写入 PEDAGOGY-LOG「改前」。

- [x] **Step 2: 批次 B1 改写**

中英同步改；改后对触及的 gloss 表面词跑一次构建 plain 校验（见 M2 可暂用 `--no-plain` 出 HTML 做阅读预览，但合并前必须开 plain）。

- [x] **Step 3: B2–B4** 同上，更新 `PEDAGOGY-LOG.md`（章、改动类型、是否动 en）。

- [x] **Step 4: 润色日志**

对改写段去套话；记录于 `HUMANIZER-LOG.md`。不借机改 docclaims 钉住的数字。

- [x] **Step 5: 预览构建**

```powershell
python scripts/bookctl.py build --product book --lang zh --out-dir yuyu-book/.scratch/yuyu-m1
```

Expected: 退出 0；不覆盖正式 dist 除非有意。

**里程碑验收 M1:**

- [x] B1–B4 在 PEDAGOGY-LOG 勾完  
- [x] 抽 3 章：开场场景 + 翻车表存在  
- [x] translationese 基线文件存在  
- [x] **未** commit/push  

---

### Task M2: 通俗层审计（guides / glosses / notes / paths）

**Files:**
- Modify: `yuyu-book/manifest.json`（`guides`）
- Modify: `yuyu-book/glosses.json` / `notes.json` / `reading-paths.json`（仅修证据与不合格句）
- Create: `docs/yuyu-overhaul/GUIDES-QA.md`
- Create: `docs/yuyu-overhaul/PLAIN-FIX-LOG.md`

**Interfaces:**
- Consumes: `plain.validate_plain` / `validate_notes` 规则（STRUCTURE § plain.py）  
- Produces: 可关可开的健全通俗层

**guides 规则（20/20）：**

| 字段 | 规则 |
|------|------|
| `question` | 读者读完能回答；勿抄章标题 |
| `deliverable` | 可检查产出（口答要点/一张表/指出源码符号） |
| `boundary` | 本章不讲什么 |
| `plain` / `analogy` | 中英都有；`plain_evidence` 落在散文 |
| `sources` | 指向 `sources.json` 已有 id |

反例：deliverable = 章首第一段原文。

- [x] **Step 1: 建 GUIDES-QA.md**

为 `front`+`ch01`–`ch15`+`apxa`–`apxd` 共 20 行勾选；每行记 question 是否合格。

执行说明：`docs/yuyu-overhaul/GUIDES-QA.md` 已建，20/20 逐条记录 question / deliverable /
boundary / plain+evidence / sources 五项。实测：20 条本来就是逐条手写的，两组各 20 条互不相同，
反例（抄标题、deliverable = 章首第一段、boundary 套全篇）一条没踩。

- [x] **Step 2: 修不合格 guides**

改 `manifest.json` 后：

```powershell
python -m unittest yuyu-book.tests.test_manifest yuyu-book.tests.test_plain -v
```

（若模块路径不同，改用仓内惯用：`python -m unittest discover -s yuyu-book/tests -p "test_plain.py"` 等。）

Expected: PASS。

- [x] **Step 3: glosses / notes 悬空修复**

```powershell
python yuyu-book/build.py --lang both --check
```

Expected: 无 `BuildError` from plain/notes；失败则按报错 `file:line` 修证据或改词形，记入 `PLAIN-FIX-LOG.md`。

执行说明：首跑即 `CHECK OK`（zh 296 glosses / en 303 glosses / 20 keeper notes / 105 tier chips），
没有悬空证据、没有词形对不上、没有缺按语，所以没有「按报错修」这一项。只做了一处主动收尾：
`ch01` / `ch05` / `apxc` / `apxd` 四条 guide 的 `plain_evidence` 里有重复 block id，去重后分别
8→7、8→7、8→6、6→4，指向的语言集合不变，`manifest.json` 的 diff 只有 6 行删除。重跑仍 `CHECK OK`。
详见 `PLAIN-FIX-LOG.md`。

- [x] **Step 4: 双开关构建**

```powershell
python yuyu-book/build.py --lang zh --no-plain --out-dir yuyu-book/.scratch/yuyu-no-plain
python yuyu-book/build.py --lang zh --out-dir yuyu-book/.scratch/yuyu-plain
```

Expected: 两次均成功；plain 版 HTML 含 gloss / compass；no-plain 版可抽查无导读带。

执行说明：两次都退出 0。抽查真实标签（不数 CSS 里的同名类）：
`no-plain` 版 `class="lead-band"`=0、`class="keeper"`=0、`class="gloss"`=0、`id="keeper-notes"`=0；
`plain` 版 =20 / 20 / 296 / 1。对照表在 `PLAIN-FIX-LOG.md`。

**里程碑验收 M2:**

- [x] GUIDES-QA 20/20  
- [x] `--check` both 绿  
- [x] **未** commit/push  

---

### Task M3: 插画管线与入门分册同步

**Files:**
- Modify: `docs/illustration-prompts.md`（过期提示词）
- Regenerate: `docs/beginner-reader.html`、`beginner-reader.en.html`、`illustration-gallery.html`
- Modify: 仅当 SVG 违约时改 `yuyu-book/illustrations/*.svg`（保持 `currentColor`、无 `id=`/`script`）
- Create: `docs/yuyu-overhaul/ILLUST-SYNC.md`

**Interfaces:**
- Produces: docs 与 dist 提取一致；pages 契约可本地模拟

- [x] **Step 1: 先建书再重生 reader**

```powershell
python scripts/bookctl.py build --product book --lang both
python scripts/build_beginner_reader.py
python scripts/build_illustration_gallery.py
```

Expected: 脚本退出 0。

实跑 exit 0：reader **zh 24 站 / en 24 站**，gallery **42 figures**。
「先建书」这一格由 12:21 起跑的 `ci-local-yuyu.ps1` 内那条
`build --product book --lang both --pdf` 承担（dist zh 12:33 / en 12:41），
所以读的是新 dist：`build_beginner_reader.py:411` 取的正是这份 dist，
而 `:341` 那句「anchors missing in dist」硬检查没有抛——本轮改过的 35 个正文文件里，
reader 要抓的锚点一个没丢。

- [x] **Step 2: 记录 docs diff**

```powershell
git diff --stat docs/ | Tee-Object docs/yuyu-overhaul/ILLUST-SYNC.md -Append
```

若有 diff：审视为「正文已变、docs 应更新」则保留新文件待稍后提交；**本 SPEC 不 commit**。

结果与这条 Step 预设的方向相反，所以值得写清楚：**三份再生品重跑后 `git diff` 为空**
（mtime 全推到 12:43，`git diff --stat docs/` 里根本没有它们）。
**「逐字节相同」这个说法在 13:20 复查时被更正**：盘上大小 89227 / 87773 / 197677 各比 HEAD blob
（88756 / 87298 / 197368）多出等于自身行数的字节——本机 `core.autocrlf=true`，生成器
`write_text()` 默认写 CRLF 而仓里存 LF，相同的是**行尾归一后的内容**。CI 在 Linux 上两端都是 LF，
所以这条门禁不会因此红；细节与根治办法见 `ILLUST-SYNC.md` 第二节的更正框。
`docs/` 的 7 项已跟踪改动全是人写的账与 M5 的门面产物。
「正文改了 668 行而 reader 为何一字不变」的取证在 `ILLUST-SYNC.md` 第二节：
`manifest.json` 本轮 **0 增 6 删**，删的全是块 ID 引用，
`question`/`deliverable`/`boundary`/`plain` 四个字段一行没动 —— reader 取材的面
不在这次改的面上，这是**幂等**，不是漏跑。
落盘用 `git diff --stat docs/` 直写（PS 5.1 的 `Tee-Object` 编码坑已在 M8 登记，不重复踩）。

- [x] **Step 3: Mermaid 对拍**

```powershell
python -c "from pathlib import Path; import re; root=Path('.');
for label, patterns in [('zh',['第一部分-基础篇','第二部分-核心系统篇','第三部分-高级模式篇','第四部分-工程实践篇','附录','00-前言.md']),('en',['en'])]:
  n=0
  paths=[]
  for p in patterns:
    P=root/p
    paths += list(P.rglob('*.md')) if P.is_dir() else ([P] if P.exists() else [])
  for f in paths: n+=len(re.findall(r'```mermaid', f.read_text(encoding='utf-8')))
  print(label, n)"
```

Expected: zh==en==160（若 M1 增删图，更新 BASELINE 并保证双语同增同减）。

实测 **zh 160（20 文件）/ en 160**，两种口径都跑过：SPEC 原式把 `en/README.md` 也算进
`en/` 那一支（21 文件，它一条围栏都没有），排掉 README 的单元口径同样是 160。
**`BASELINE.md` 的「zh=160 en=160」不需要改数**，M1 确实没增删图。
第三道独立印证：M8 建的 `check_bilingual_parity.py` 逐 unit 数出来的 160/160
用的是另一套围栏状态机，两个实现撞上。

- [x] **Step 4: art 契约测**

```powershell
python -m unittest discover -s yuyu-book/tests -p "test_art.py" -v
python -m unittest discover -s yuyu-book/tests -p "test_illustrations.py" -v
```

Expected: PASS。

**Ran 15 tests OK** 与 **Ran 18 tests OK**。另对 42 张 SVG 直接量了 `art.py` 那三条硬契约
（`currentColor` 齐 / 无 `id=` / 无 `script`）：**违约 0 张**。
所以 Files 里那句「仅当 SVG 违约时改 `illustrations/*.svg`」的条件不成立，
**本轮一张 SVG 都没动**。

**里程碑验收 M3:**

- [x] ILLUST-SYNC 有记录；reader/gallery 已再生  
- [x] Mermaid 双语计数一致  
- [x] **未** commit/push  

补记两件这一格真正改掉的东西：

1. `docs/illustration-prompts.md` 过期的是**计数边界，不是提示词本身**：标题写「26 份」，
   盘上 42 张 `.svg`，差额是 16 张章内插图（`ch01-five-pillars` 到 `ch15-harness-wheel`），
   它们不走「生图提示词 → 手写 SVG」这条管线，而手册既无条目也无一句说明。
   新增一节登记 16 个文件名、26+16=42 的对齐、取舍记录所在
   （`.superpowers/sdd/2026-11-02-illustration-rollout/`）、两类图共用的 `art.py` 契约
   与本次 42/0 的实测，并在开篇那句后加了指向该节的指针；**净改动 +26 行 / 删 0 行**。
   **没有**替那 16 张编造双语提示词——编就是凭空造真源。
2. `pages.yml:79` 的 `git diff --exit-code docs/`，本地能证的只有「重建幂等」这半边（已证）；
   路径级检查在提交之前必红，且这个红是设计使然（CI 跑到那一步时工作树是干净的）。
   **没有**为凑绿把它的判据放宽成「只看三份 html」。见 `ILLUST-SYNC.md` 第五、七节。

---

### Task M4: 构建器收敛、PDF 与 CI 配置（先配置，后推送）

**Files:**
- Modify: `yuyu-book/yuyu_book/{style,deco,labels,style_css,render,pages,frontmatter,pdf,core,registry,art}.py`（仅收敛已有脏改，禁止无关大重构）
- Modify: `.github/workflows/book.yml`、`check-book.yml`（paths 增加 `omp/**` **或** 明确 omp 另 job；**御舆 job 仍 `product=book`**）
- Modify: `.github/workflows/pages.yml`（文档化双入口；omp 产物部署可标 `TODO` 与 omp SPEC M4 对齐）
- Create: `docs/yuyu-overhaul/ci-local-yuyu.ps1`
- Modify: `yuyu-book/PRODUCTS.md`、`STRUCTURE.md`（构建器双 product 段落）

**Interfaces:**
- Produces: 本地可重复的御舆 PDF；「推送后 CI 应绿」的 YAML；**omp 构建失败不得红御舆 job**（分 job 或 continue 策略在 YAML 注释写清）

- [x] **Step 1: 御舆全量本地**（2026-11-04 跑齐，证据两份日志）

```powershell
python scripts/bookctl.py doctor
python scripts/bookctl.py check --fast
python scripts/bookctl.py build --product book --lang both --pdf
```

Expected: doctor 无缺件；check fast 绿；HTML+PDF 写出；日志页数记入 `docs/yuyu-overhaul/PDF-PAGES.md`。

实测：`doctor: 9 ok, 0 failed` → 退出 0；`check fast: 6 steps passed`（内含 501 项构建器单测 OK、
169 份 Markdown / 321 张 Mermaid 0 errors —— 321 是 `check_book.py` 的**全仓**口径，含 `omp/` 与两份 SPEC 自己的围栏；
御舆正文是 `BASELINE.md` 记的 zh=160 / en=160，两个口径别混用）→ 退出 0；构建 exit 0，
`zh 5.8 MB / 518 pages / 28 bookmarks`、`en 5.9 MB / 569 pages / 28 bookmarks`，数字已进 PDF-PAGES 表。
日志：`docs/yuyu-overhaul/logs/doctor-checkfast-after-xref.log`、
`docs/yuyu-overhaul/logs/rebuild-book-pdf-after-xref.log`。
单独复跑两套单测也留了退出码：`logs/unittest-after-xref.log`（`tests` 39 OK=0、`yuyu-book/tests` 501 OK=0）。
本步只到「本地全绿」，**未 commit/push**，CI 真绿要等推送之后。

- [x] **Step 2: 不回归 omp 入口、不伤 book**（2026-11-04 09:23–09:31 两条命令实跑，退出码 0/0）

```powershell
python scripts/bookctl.py build --product book --lang zh --out-dir yuyu-book/.scratch/book-smoke
python scripts/bookctl.py build --product omp --lang zh --out-dir yuyu-book/.scratch/omp-smoke
```

Expected: 两次成功；book smoke **无** omp 章节标题；omp smoke **无**「御舆」15 章正文。

实测（日志 `docs/yuyu-overhaul/logs/smoke-both-after-xref.log`）：

| 命令 | 退出 | 构建打印 | 产物 |
|------|------|----------|------|
| `book --lang zh` → `.scratch/book-smoke` | 0 | `yuyu-agent-harness-zh.html: 5.8 MB, **20 units**, 176 plates, 296 glosses, 20 keeper notes` + `OK` | 5,781,074 B @09:29 |
| `omp --lang zh` → `.scratch/omp-smoke` | 0 | `yuyu-omp-zh.html: 20.0 MB, **39 units**, 1 plates, 242 glosses, 381 tier chips, 39 keeper notes` + `OK` | 19,974,200 B @09:31 |

20 / 39 两个单元数就是「不伤 book / 不回归 omp 入口」的硬指标：御舆的 20 单元契约没被 omp 的 39 单元污染，
反之亦然。再加一条更硬的：`.scratch/omp-smoke/yuyu-omp-zh.html` 与 `dist/yuyu-omp-zh.html`
**sha256 一字不差**（`34bbe379cbddbd3b…`）——08:19 那次 omp 构建之后，omp 入口的产物没有漂过。
标题串扰另跑了一次比对：拿 `omp/*.md` 的 44 个 H1 去撞 book smoke 的 34 个 `<h1>` → **0 命中**；
拿御舆 19 份正文（15 章 + 4 附录）的章名去撞 omp smoke 全文（剥标签后）→ **0 命中**。两条 Expected 都实测到 0。

一个容易误读的点记在这里：book smoke 是 **5,781,074 B**，`dist/` 里那份是 **5,781,712 B**，
差的 638 B **不是**内容变化，也不是半成品——本步这条命令没带 `--pdf`，
主题索引里 238 个 `<span class="page-ref idx-ref">` 的空槽在 `--pdf` 构建里会被填上页码，
238 处页码数字正好 638 个字符（实测两条 index 行的字节差 = 56,067 − 55,429 = 638）。
同一份 zh 书稿，`--pdf` 与否就差这一截；详见 `PDF-PAGES.md`。
本轮所有产物的机器生成读数（stat + sha256 + 页/书签 + spoke 位宽 + 索引页码填充数 + 三道护栏退出码）
合成一份日志：`docs/yuyu-overhaul/logs/consistency-sweep-2026-11-04.log`。

- [x] **Step 3: ci-local-yuyu.ps1**（2026-11-04 转绿；落盘脚本与本节代码块**故意不同**，原因见下）

```powershell
$ErrorActionPreference = "Stop"
python scripts/bookctl.py check --fast
python scripts/bookctl.py build --product book --lang both --pdf
python scripts/check_artifact_claims.py
Write-Host "ci-local-yuyu OK"
```

Run: `powershell -File docs/yuyu-overhaul/ci-local-yuyu.ps1`  
Expected: `ci-local-yuyu OK`。（若 `check_artifact_claims` 因页数漂移失败：先更新 README 宣称或 BASELINE 例外表，**禁止**谎报。）

实测（后台分离进程跑满，日志 `docs/yuyu-overhaul/logs/ci-local-yuyu-20261104-100401.log`，4,820 B、严格 UTF-8、
0 个 U+FFFD）：`check --fast` → `-> exit 0`；`build --product book --lang both --pdf` → `-> exit 0`；
`check_artifact_claims.py` → `-> exit 1`，差异**全部**是「本机雅黑 518/569 页 vs README 写 CI/Noto 505/536 页」这一类，
共 4 条（`README.md` 与 `en/README.md` 各 2 条）；脚本按例外表放行后打印 `EXCEPTION: 放行 4 条页数差异…`，
末行 `ci-local-yuyu OK`。README 一字未改（仍是 CI 口径），改的是 BASELINE 例外表这一侧 —— 上面那条「禁止谎报」按字面执行。

为什么落盘脚本不是上面这 5 行：本机 PowerShell 5.1 有三个坑，每一个都会让「测试其实过了」显示成红。
① `$ErrorActionPreference="Stop"` 下，原生命令的 stderr 经 `2>&1` 变成 `ErrorRecord` 并**终止**执行 ——
`check --fast` 那次 39 个单测全过，脚本却 exit 1（首跑日志 `logs/ci-local-yuyu-20261104-095428.log` 就是那一版留下的）。
`Step` 函数在调用期间降到 `Continue`，只按 `$LASTEXITCODE` 判定。
② 空的 stderr 行 `ErrorRecord.ToString()` 会打印成 `System.Management.Automation.RemoteException`，
所以记日志前先取 `.Exception.Message`。
③ `Tee-Object` / `Add-Content` 默认 UTF-16/ANSI，中文日志会花；日志改写用
`[System.IO.File]::AppendAllText(..., UTF8Encoding($false))`，并设 `PYTHONUTF8` / `[Console]::OutputEncoding`。
`.ps1` 里有中文，文件必须带 UTF-8 BOM。放行条件本身也是护栏：README 里 505 或 536 一旦找不到就 throw，
`[STALE]` 行里出现非页数类差异也 throw，**一条都没报红同样 throw**（那说明本机已变 CI 口径或 README 被动过）。

- [x] **Step 4: 编辑 workflow（不推送）**（2026-11-04 改完并机器校验，未 push）

`book.yml` 要求：

1. 御舆 job 保持现网：`bookctl check --full` 或等价 + 双语产物；  
2. 若加入 omp：必须 **独立 job** `omp`（`runs-on ubuntu-latest`），步骤仅 `build --product omp --lang zh`（±pdf）；`paths` 含 `omp/**` 时不要让 omp 失败 `needs` 挡住御舆 unless 用户另令；  
3. artifact 名分开：`yuyu-book-dist` vs `yuyu-omp-dist`。

实测（`python -c "import yaml; …"` 解析同一份文件，不是目测）：`jobs=['book','omp']`、
`jobs.omp.needs` 为 `None`（要求 2 达成：omp 红不挡御舆）、`True.push.paths` 含 `omp/**`、
两个 upload-artifact 名分别是 `yuyu-book-dist` / `yuyu-omp-dist`（要求 3 达成）、
omp job 只跑 `build --product omp --lang zh --pdf` 一条构建命令（要求 2 达成）、
`book.yml` 语法过 PyYAML。要求 1 未动御舆 job 的任何一步。
**15:14 复算出一条省眼的事实**（`yaml.safe_load` 后逐 step 比 JSON）：两个 job 有 **7 步逐字节相同**
——`actions/checkout@v4`、`setup-node@v4`（node 22 + npm cache）、`setup-python@v5`（3.12）、`npm ci`、
`pip install -r yuyu-book/requirements.txt`、`Install CJK fonts`（12 分钟上限）、`Install Chromium`（15 分钟上限）；
`runs-on` 与 `timeout-minutes: 45` 也一致。差集只有四步：omp 侧 `Build the omp edition (zh + PDF)` +
一份 `upload-artifact`（名 `yuyu-omp-dist`、path `yuyu-book/dist/yuyu-omp-*`），
book 侧 `check --full` + `The README numbers match the built book` + 另一份 `upload-artifact`（名 `yuyu-book-dist`、
path `yuyu-book/dist/*`）。也就是说目视面实际只有这四步加两段注释，其余是复制。
`pages.yml` 只在 `Assemble the site` 前加了一段注释说明双入口为什么不 `cp` omp 产物进单工件站点
（要么独立 workflow，要么先停在 `yuyu-omp-dist` 工件），构建与部署步骤一字未改；
`pages.yml` 的 `paths` 不含 `omp/**`，与这段注释同向。

**GitHub 真绿仍然要等 commit/push**，而 `omp/` 至今不在 HEAD（`git ls-tree HEAD omp/` 空）：
推送后 `omp` job 第一次跑才有意义，在那之前这条 job 在设计上就是红的（检出里没有 `omp/`）。

- [x] **Step 5: STRUCTURE 补「双产品」一小节**（2026-11-04）

写明：`product=book` 默认；`product=omp` 见 `omp/BUILD.md`；20 单元契约仅 book。

落点不是新开一章，而是 `STRUCTURE.md` 加 **§3.6 双产品：`book` 与 `omp`**（七行对照表 + 三条边界），
理由：§1–§7 的编号被别处按号引用过，插一节会逼着改一串号；机制本身属于 §3 构建器。
三条边界分别是：**20 单元契约只属于 book**（第 2 节表 / `notes.json` 20 条 / 主题索引 / `illustrations/`；
而第 6 节的 HTML 契约数的是各自单元数，对两个产品都成立）、**omp 的 `0 emblems, 0 headpieces` 是设计而非漏画**
（`build.py:269` 期望值 = 单元数 − 磁盘上缺的图数）、**`check --fast/--full` 不含 omp**
（`bookctl.check()` 没有 product 参数）。表里每条都带代码位置：`bookctl.py:285`、`plain.py:70`、
`build.py:190` / `:294`。

同一轮顺手补掉三处「文档说现状、磁盘不是现状」的空洞，它们本来就是这一节的邻居：
`--manifest` / `--sources` 之前不在 §3.1 那张「参数就是它实际接受的那些」表里（`build.py:469`/`:471` 早就收了）；
§3.4 生成物与 §1 顶层地图都没有 `omp/` 与 omp 产物；§4 的 workflow 表少了 `pages.yml`（磁盘上 4 份，表里 3 份），
`book.yml` 那行也没提新增的 omp job。§7 速查加一行「改第二分册」。
`yuyu-book/PRODUCTS.md` **不改**：它已经是双产品对照表（两张登记表、产物前缀、`make book-omp`），
且用的也是 `plain.registry_names()` 这个真名，STRUCTURE §3.6 反过来指它，避免两处各抄一份数字。

反向纠错一处：`omp/BUILD.md:39` 原写「这些文件名由 `yuyu_book/registry.py` 按 product 给出」——
`registry.py` 只有 13 个名字的白名单（不在表里报 `unknown registry`），真正按 product 派生 `-omp` 兄弟名的是
`plain.py:70 registry_names()`，`revisions` / 主题索引走 manifest 键，骨架与来源走命令行。
「不是 `build.py` 里的分支判断」那半句是对的，予以保留。

验证（改的是被测试盯着的文档，所以不能只靠读）：`test_docclaims` 9 项 OK、
`test_build_contracts` 71 项 OK（内含一次真实 `build.py --check --mermaid=source`）、
`scripts/check_book.py` 169 份 Markdown / 321 张 Mermaid / **0 errors**；
新表 9 行列数一致（3 列）由脚本数过。

**里程碑验收 M4:**

- [x] `ci-local-yuyu.ps1` 绿（2026-11-04 10:04–10:29 实跑，末行 `ci-local-yuyu OK`；
        日志 `logs/ci-local-yuyu-20261104-100401.log`）  
- [x] YAML 经人工目视 —— **15:49 用户回「同意继续」，本格打勾**（15:14 交出目视面；机器已过 PyYAML 并逐条断言（Step 4），这一格要的是用户眼睛，现在有了）。
        **15:14 目视面已交出**：`book.yml:101–146`（新增 omp job，含 6 行说明注释）、`book.yml:14` / `:30`
        两行 `omp/**`、`pages.yml:85–91` 七行注释；对 HEAD 是 **+56 / −0**，纯增量、没有删改任何原有步骤。
        同一轮复算的机器口径（不是抄 Step 4）：`git diff HEAD --stat -- .github/workflows/` 给 49 + 7 = 56 行，
        PyYAML 给 `jobs=['book','omp']`、`jobs.omp.needs=None`、`timeout-minutes=45`、9 步，
        其中 `run` 只有 `npm ci` / `pip install -r yuyu-book/requirements.txt` / apt 字体 / playwright chromium /
        `build --product omp --lang zh --pdf` 五条，工件名 `yuyu-omp-dist`；`pages.yml` 的 `push.paths` 不含 `omp/**`。
        **要人拍的并不是语法**：`book.yml` 自己就在 `paths` 里，而 `omp/` 至今不在 HEAD
        （`git ls-tree HEAD omp/` 实测 **0** 条，索引里 `git ls-files omp/` = 301 条），
        所以引入这个 job 的那次 push / PR 会在 Book CI 上挂一格**设计上就红**的 `omp`。
        三条路：① 接受（注释里已把「前置条件：得先 commit」写明）；② 给 omp job 加 `if:` 守 `omp/` 存在；
        ③ 让 job 与 `omp/` 在同一次 commit 里进。**15:49 起走的是 ①**：YAML 一字未改，
        「推送前 `omp` 那格设计上红」由 `book.yml:105–106` 的注释承担说明责任，
        而 `omp/` 与 6 份 omp 配置进仓本来就是第 6、7 组的事（见 `ACCEPTANCE` 第 3 节）——
        真到推送窗口时改选 ② 或 ③ 也都还来得及，两条都不需要回改这一步之前的任何东西。
        打勾与否不改变另一条：本轮不 push。  
- [x] **明确：GitHub CI 真绿 = 稍后 commit/push 之后**（记在 Step 4 正文：`omp/` 不在 HEAD，
        检出里没有 `omp/`，那条 job 在推送前设计上就是红的）  
- [x] **本阶段不 push** —— 机器可查：`git log -1` 仍是 `951c0ef`（2026-11-03 16:50），
        HEAD reflog 最后一条是 11-03 21:41 的 `reset: moving to HEAD`；所有 `refs/remotes/*` 的 reflog
        在 **2026-11-04 一条都没有**（逐条 grep 过），最后一次 `update by push` 是 `origin/p3-pages-split@{2026-11-03T16:50:04+08:00}`。
        注意 M0 Step 4 那格「未执行 git add」仍是**不勾**的（写这段时索引里躺着 324 个已暂存文件，
        等用户拍板；11-04 下午摘掉泄漏那份后为 323，仍不勾，理由见 M0 Step 4），
        本格只声明 M4 这一段没 push，两格口径不同，不是矛盾  

---

### Task M5: 站点双入口与门面文档

**Files:**
- Modify: `docs/portal.html`（或经 `scripts/build_site_portal.py` 再生）
- Modify: `README.md` / `en/README.md`（更正 omp「尚未接入 make book」→ 已有 `make book-omp`；双入口）
- Modify: `STRUCTURE.md` 顶层地图加入 `omp/`、`docs/YUYU-OVERHAUL-SPEC.md`
- Create: `docs/yuyu-overhaul/SITE-LINKS.md`（链接检查表）
- Create: `docs/yuyu-overhaul/check_site_links.py`（同一轮加的门禁：发布清单从 pages.yml 解析，见 Step 3）

**Interfaces:**
- Produces: 读者从门户能进御舆整书与 omp 分册说明页

- [x] **Step 1: 更新 README 第二分册段**（2026-11-04）

必含：`make book` = 御舆；`make book-omp` = omp 中文；链接 `omp/README.md`、`omp/BUILD.md`；写作钉提示指向 `omp/VERIFY.md`。

`README.md` 那段原本写着 omp「**尚未接入** make book」—— 磁盘上不是这样（`make book-omp` /
`make book-omp-pdf` 在 Makefile 里，`bookctl build --product omp` 已跑通），所以删掉那句，改成：
`make book` / `make book-pdf` = 御舆双语；`make book-omp` / `make book-omp-pdf` = omp 中文；
等价命令行 `python scripts/bookctl.py build --product omp --lang zh [--pdf]`；两本都落 `yuyu-book/dist/`、
前缀不同；链接 `omp/README.md`、`omp/BUILD.md`、写作钉提示 `omp/VERIFY.md`、口径出处 `STRUCTURE.md` §3.6；
并保留两条边界（`check --fast/--full` 不含 omp；CI 里 omp job 不 `needs` 挂御舆，且在 `omp/` 进 HEAD 之前设计上就是红的）。

`en/README.md` 的问题不是写错，是**整段没有**：中文有一份第二分册段，英文一份都没提。新增
`## Second volume · Omp (in progress)` 同内容英文版（第一分册写作 "Yù Yú"，第二分册书名保留汉字，
链接走 `../omp/…` 与 `../STRUCTURE.md`）。

机器口径：`README.md` 36 处相对链接全部落在磁盘实体上、11 处外链、0 死链；`en/README.md` 37 处 / 10 处 / 0 死链；
`test_docclaims` 9 项 OK。一个诚实的保留：`omp/README.md` 这条链接**在工作树里是活的、在 GitHub 上是 404**
（`omp/` 只进了索引、没进 HEAD，`git ls-tree HEAD omp/` 为空）—— 这是「本阶段不 push」的直接后果，
不是链接写错，push 之后自动愈合。

- [x] **Step 2: portal 双卡**（2026-11-04，经 `scripts/build_site_portal.py` 再生成 `docs/portal.html`）

门户至少两张卡：御舆（HTML/PDF/入门分册）· Omp（omp/README + 本地产物说明）。无死链。

现在是 **5 张卡**：御舆（`div.card`，`.go` → `book.html`，卡内另给 `yuyu-agent-harness-en.html` 英文入口）、
**第二分册 Omp**（`div.card`，故意整张不给链接）、入门分册中/英各一张（`a.card`）、插画画廊（`a.card`）。
Omp 那张为什么是 `div` 而不是链接：omp 产物只在 Book CI 的 `yuyu-omp-dist` 工件里、站点上没有，
`omp/` 又还没进 HEAD —— 两条路都会造死链，所以卡上写「施工中」+ 本地命令 `make book-omp` / `make book-omp-pdf`，
并说明书稿在仓库内的 `omp/` 目录。这与 G5「本阶段不要求 omp 已进 pages matrix」同向。
`.sub` 与 `og:description` 同步声明「本站只发布御舆；同仓第二分册仍在施工中」。

改这一张卡时抓到并修掉一个**原本就存在**的缺陷：御舆卡原来是 `<a class="card">`（指向 `book.html`），卡内又嵌
了一个指向 `yuyu-agent-harness-en.html` 的 `<a>` —— HTML 不允许 `a` 套 `a`，解析器提前闭合外层，
浏览器 DOM 探针显示英文链接的父节点是 `.cards` 而不是卡片。改成 `div.card` + 显式 `.go` 链接后
复测：`nested <a> inside <a>` = 0、5 张卡全在网格上（真实浏览器截图 3+2 两行）。
同时删掉卡上写死的「318 张图版」（构建统计行是每份 **176 plates**，见 `logs/ci-local-yuyu-20261104-100401.log:58`），
按仓库规则 derive-or-omit 选择省略；保留的 `@@PLATES@@` 是另一个数 42（手绘插图，来自 `build_beginner_reader.PLATES`）。
`tests/test_site_portal.py` 3 项 OK（它把提交副本钉成与生成器一致，所以这些改动必须走脚本再生成）。

- [x] **Step 3: SITE-LINKS 勾选**（2026-11-04）

手工打开 `docs/portal.html`（file://）勾选。

前提修正：本步点名的 `docs/yuyu-overhaul/SITE-LINKS.md` 在 Files 里是 *Create*，而此前**全仓不存在**
（`grep -rl SITE-LINKS` 只命中本 SPEC 自己）。本轮把它建出来，内容就是上面那张逐条引用表。

手工 `file://` 那一跑照做（真浏览器）：页面渲染成 3+2 两行卡片，控制台报 3 个 `ERR_FILE_NOT_FOUND` ——
`cover.png` / `book.html` / `yuyu-agent-harness-en.html`。**这不是缺陷**：部署时门户在站点根
（pages.yml:103 `python scripts/build_site_portal.py site/index.html`），那三个名字分别在 pages.yml:102/95/97
被 `cp` 进 `site/`；相对 `docs/` 解析才会缺。为把这条判据固定下来，另建护栏
`docs/yuyu-overhaul/check_site_links.py`：发布清单**从 pages.yml 自己解析**（现测 9 个名字），
门户里任何本地引用没有发布者即 exit 1；同时盯 `@@TOKEN@@` 漏开、`<a>` 套 `<a>`、卡片数、
以及 `README.md` / `en/README.md` / `STRUCTURE.md` / `omp/BUILD.md` 的相对链接落不落得在磁盘上。
正例 exit 0；四条负例（假发布目标 / 改回嵌套锚点 / 塞未展开 token / README 指向不存在的 `omp/README-NOPE.md`）
都是实跑 exit 1，README 临时改完已还原（逐字节比对相同）。
`--online` 会对外链发 HEAD，实测那条 handraw-style 200。

**里程碑验收 M5:**

- [x] README / STRUCTURE / portal 一致描述双书 —— 三处现在都说同一件事：两本、两套命令、两种产物前缀、
        `check` 不覆盖 omp、omp 卡/段落标注施工中。本轮共修掉四条「文档说现状、磁盘不是现状」：
        README 的「尚未接入 make book」、`en/README.md` 缺整段、`omp/BUILD.md:39` 指错模块、
        门户卡上写死的 318；STRUCTURE §1 顶层地图补 `omp/` 与 `docs/`（含本 SPEC 的位置）  
- [x] **未** commit/push —— `git log -1` 仍是 `951c0ef`（2026-11-03 16:50），`refs/remotes/*` 的 reflog
        在 2026-11-04 **零条**（逐条 grep），最后一次 `update by push` 是 11-03T16:50:04；
        M0 Step 4 那格「未执行 git add」仍不勾（写这段时 324 个已暂存文件等用户拍板，现已处置为 323），
        口径差别见 M4 验收注  

---

### Task M6: 测试契约硬化（20 单元 × product 隔离）

**Files:**
- Create: `yuyu-book/tests/test_product_isolation.py`
- Modify: 仅当现有测试误加载 omp manifest 时最小修复
- Create: `docs/yuyu-overhaul/TEST-CONTRACT.md`

**Interfaces:**
- Produces: 失败即红的隔离断言

- [x] **Step 1: 写隔离测试**（`yuyu-book/tests/test_product_isolation.py`，9 条，2026-11-04）

```python
# yuyu-book/tests/test_product_isolation.py
import json
import unittest
from pathlib import Path

BOOK = Path(__file__).resolve().parents[1]

class ProductIsolation(unittest.TestCase):
    def test_book_manifest_unit_count_is_20(self):
        m = json.loads((BOOK / "manifest.json").read_text(encoding="utf-8"))
        # front + 4 parts' chapters + appendices — mirror core loader if available
        from yuyu_book.core import load_manifest  # adjust if API differs
        # Fallback if load_manifest needs product arg:
        units = []
        if "front" in m:
            units.append("front")
        for part in m.get("parts", []):
            units.extend(u["id"] for u in part.get("units", part.get("chapters", [])))
        units.extend(a["id"] for a in m.get("appendices", []))
        # If structure uses nested shape, prefer bookctl/core helper:
        self.assertEqual(len(set(units)), 20)

    def test_omp_manifest_does_not_share_book_output_prefix(self):
        omp_path = BOOK / "manifest-omp.json"
        if not omp_path.exists():
            self.skipTest("omp manifest not present")
        omp = json.loads(omp_path.read_text(encoding="utf-8"))
        prefix = omp.get("output_prefix") or omp.get("product") or ""
        self.assertNotIn("yuyu-agent-harness", str(omp))
        self.assertTrue("omp" in str(omp.get("output_prefix", "yuyu-omp")).lower() or True)

if __name__ == "__main__":
    unittest.main()
```

实施时：**先读** `yuyu_book.core` 真实加载 API，把上面 fallback 换成仓内函数；测试必须在现树可运行。

按这条指示落地（2026-11-04），代码与本节示例**有意不同**，四处是改强不是改写：

1. `from yuyu_book.core import load_manifest` —— 仓里没有这个函数。真实入口 `core.load_configs(manifest_name, sources_name)`
   （内部 `registry.load` + `core.validate_configs`）、单元序列 `core.expected_ids()`、
   登记表名 `plain.registry_names()`、语言 `plain.manifest_langs()`。测试不再手扒 manifest 的嵌套形状。
2. 示例的 `assertTrue(... or True)` 是永真式，删掉；示例的 `skipTest("omp manifest not present")`
   会在 omp 清单消失时把断言变成 no-op，删掉 —— 现在 omp 清单缺失直接 `registry.load` 报错变红。
3. 示例只数「20」，现树再加一条同量级的：omp 必须**显式**声明 `"subject_index_registry": null`。
   这一条是隔离里最容易无声烂掉的一处 —— `build.py:190` 的默认值就是御舆的 `subject-index.json`，
   键一旦被删，omp 构建会去给御舆的主题索引盖页码，而产物看起来完全正常。
4. 断言九条而不是两条，每条各挡一种「两本书互相写」的事故；清单与理由见
   `docs/yuyu-overhaul/TEST-CONTRACT.md` §3，含一条**故意不写**的断言（两个产品的单元 id 不许相同 ——
   它们是两份独立 HTML，锚点命名空间本就该各自独立）。

**变异表**（`docs/yuyu-overhaul/TEST-CONTRACT.md` §4，用 `registry.load` 内存包装注入缺陷、不落盘）：
十条注入**全部**按预期变红 —— 御舆少一附录 `19 != 20`、重复登记 `21 != 20`、omp 少一章 `38 != 39`、
omp 抢前缀 / 抢主题索引 / 抢登记表名 / 声称有英文版 / guides 漏一格 / 御舆默认路径漂向 omp、
以及在 `yuyu-book/tests/` 放一个只提 `manifest-omp` 的临时探针文件（探针当场删除）。

一个 SPEC 没写、但落地时撞上的连带义务：加测试会**改掉 `revisions.json` 里那条 note 的数字**。
`test_docclaims.py:212` 的 `test_the_revision_note_closes_with_the_suite_it_shipped` 拿实时 `discover` 的
`countTestCases()` 去撞最新一条 note 的「构建器测试 (\d+) 项全绿」/「(\d+) builder tests green」。
本文件加 9 条 → 501 变 510 → 该测立刻红（后台那一跑 `Ran 501 tests` + `FAILED (failures=1)`，
日志 `.scratch/ut-yuyu.log`，即「旧数字 vs 新发现数」的原始证据）。处置就是把 `yuyu-book/revisions.json`
`entries[0]`（0.3.5，仍是当前 shipping 版本）的 zh 与 en 两处 501 改成 510 —— 这是该测设计的用法，
不是为凑绿改口径：改完的 510 由下面 Step 2 的全量跑证明为真。

- [x] **Step 2: 跑测**（2026-11-04）

```powershell
python -m unittest discover -s yuyu-book/tests -v
```

Expected: 全绿；若因重构失败，先修产品代码再改测试期望。

实测：`Ran 510 tests in 250.774s` / `OK`（退出 0，日志 `.scratch/ut-yuyu2.log`）；
`python -m unittest discover -s tests` → `Ran 39 tests` / `OK`。
`Modify: 仅当现有测试误加载 omp manifest 时最小修复` 这一格是**空操作**：全仓 grep 过，
除新建的这个文件以外没有第二个测试读 `manifest-omp.json`（`test_no_other_test_loads_the_omp_manifest`
把这条现状钉成了断言，以后谁误加载就红）。

- [x] **Step 3: 文档化契约**（2026-11-04）

`TEST-CONTRACT.md` 列出：notes=20、guides=20、illustrations 装配数、docclaims、product isolation。

落盘 `docs/yuyu-overhaul/TEST-CONTRACT.md`。数字全部现量（不是抄旧文档）：
`notes.json` 20 / `notes-omp.json` 39；guides 20 / 39（`validate_configs` 要求覆盖全部单元）；
`reading-paths.json` **15** 个键（只覆盖 15 章，前言与附录没有小节 —— 不是 20，SPEC 这句容易读歪）、
omp 那份 33；`glosses.json` 102 = core 44 + extra 58、`glosses-omp.json` 36 = 20 + 12 + 4（`mark=false`）；
`illustrations/*.svg` 磁盘 42 枚、对 20 个单元 id `art.missing()` = 0 → 章徽期望 20、题刻期望 4；
`sources.json` 55 / `sources-omp.json` 2。外加 §5「与既有护栏的分工」表，说明为什么这些数不在
`check_crossrefs` / `check_block_markers` / `check_site_links` / `check_artifact_claims` 里重复钉。

**里程碑验收 M6:**

- [x] unittest 全绿 —— 510 + 39 两套 `OK`（退出 0）  
- [x] TEST-CONTRACT 存在 —— `docs/yuyu-overhaul/TEST-CONTRACT.md`  
- [x] **未** commit/push —— 同 M4/M5 口径：`git log -1` 仍是 `951c0ef`，`refs/remotes/*` 在 2026-11-04 零条 reflog  

---

### Task M7: 与 omp 分册协同（共享术语 · 互链）

**Files:**
- Create: `docs/COMPARE-OMP.md`（读者向；御舆侧入口）
- Create: `yuyu-book/glosses-shared.json`（或 `docs/yuyu-overhaul/SHARED-TERMS.md` 若暂不接线构建）
- Modify: `README.md` 御舆段加「对照 Omp」链接
- Modify: `附录/D-术语表.md` 仅增加「丛书共享词」短节（可选，勿炸 subject-index 除非跑 `--regen-index`）
- Sync expectation: omp SPEC M6 的 `omp/COMPARE-YUYU.md` 与本文对指

**Interfaces:**
- Consumes: FUSION-PLAN §3 对照表  
- Produces: 双向入口；共享词 ≥20；御舆 gloss 定义不出现 hashline/mnemopi 等 omp 专名作「本词释义」

- [x] **Step 0（2026-11-04 先行做掉）：正文互链按对照表校正**

  御舆正文 32 条 omp 互链里有 14 条是坏的：6 条把本 SPEC 记号里的变量 `M` 当正文写了出去
  （「参见 omp 分册第 M 章」），8 条把**御舆自己的章号和题名**当成 omp 的（zh ch05–ch08、en ch05–ch08）。
  已按 `omp/overhaul/CROSSREF-MAP.md` 反查表逐条填号，中文 16 行现可机器校验（脚本在该文件末尾，跑出一条不匹配即红）。
  明细与取号理由见 `omp/overhaul/CROSSREF-MAP.md`「反查表落地审计」。

- [x] **Step 1: 落盘 COMPARE-OMP.md** —— `docs/COMPARE-OMP.md`（2026-11-04）

含：何时先读御舆、何时只读 omp、10 行同构点、不同实现勿混、指向 `omp/README.md`。

  落地形态：`## 我该读哪一本` 6 行、`## 十个同构点（摘自对照地图，完整 33 行在原表）` **10 行**（逐行取号自
  `omp/overhaul/CROSSREF-MAP.md`，即 Step 0 那份反查表，本文件是其声明的消费者之一）、
  `## 两本书不许互相搬的东西`（含钉版不同）、`## 译名分叉（三处…）` 3 行、
  `## 两本书的构建事实（同仓、两条独立入口）` 7 行（单元 20/39、语言、命令、产物名、通俗层条数、来源 55/2、CI）、
  再往后是 `## 互链现在有多少` 与 `## 两处已知缺口（写在这里免得被当成已存在）`。
  「指向 `omp/README.md`」这条第一稿漏了（只指到 `omp/BUILD.md`），已补进开头那句入口指引。
  缺口按事实记为缺口，不虚构文件：
  **`omp/FUSION-PLAN.md` 在三份 SPEC 里被当作 §3 对照表的出处，但仓库里没有这个文件**；
  **`omp/COMPARE-YUYU.md` 尚未写**，所以御舆侧这一份不放指向它的链接（放了就是死链），
  只在文中说明对指关系等 omp 侧落地后补。

- [x] **Step 2: 共享词表** —— `docs/yuyu-overhaul/SHARED-TERMS.md`（22 行 ≥ 20）

至少 20 词：agent-harness、main-loop、tool-call、permission、compaction、mcp、hook、subagent、skill、context-window … 每词列：御舆 gloss id · omp gloss id（可先空）· 中文译名锁定。

  取的是 SPEC 允许的「若暂不接线构建」那条路线：**没有**新建 `glosses-shared.json`，理由与接线代价写在文件 §七
  （要改 `registry.FILES` 白名单、`plain.registry_names()` 只派生 `-omp` 同名字、M6 隔离测试与套件数护栏要跟着动）。
  表体 22 行 = 15 行两边同 id + 7 行同概念不同 id（`auto-compact`↔`compaction`、`permission-mode`↔`yolo`/`approval`、
  `permission-classifier`↔`approval`、`transcript`↔`session`、`claude-md`↔`agents-md`、`plugin`↔`extension`、
  `token-budget`↔`toks`）。实测基数：御舆 **102** 条、omp **36** 条，共享 id **15**（`term.zh`+`term.en` 全同 **12**、
  分歧 **3**）、omp 独有 **21**、御舆独有 **87**。SPEC 点名的 `tool-call` **两边都没有这个 id**，
  最近的是共享的 `tool-result` —— 该格留空并写明，没有硬凑。
  「中文译名锁定」一列对 3 处分歧**没有替用户拍板**：文件 §四 只把两本各自的 `plain` 释义、`forms` 与标记点
  （御舆 `front.b-e3677d71`/`ch01.agent-harness`、omp `omp/ch01.md:51` 等）抄出来，给出「保持各书自洽」的建议并等确认。
  数字全部由文件 §六 那条命令复现，已跑：`102 36 shared 15 identical 12 diverge 3 omp-only 21`。

- [x] **Step 3: 污染审计** —— 通过（0 / 0 / 0）

```powershell
Select-String -Path yuyu-book/glosses.json -Pattern "hashline|mnemopi|oh-my-pi" -SimpleMatch
```

Expected: 无命中（或仅在明确「对照」字段且 plain 不拿来当定义）。

  本机用 Python 跑的等价口径（PS 的引号转义在这台机器不可靠，见 M5 记的三条坑），命令抄在 `SHARED-TERMS.md` §五，
  2026-11-04 读数：`glosses.json` **0**、`notes.json` **0**、御舆正文（`00-前言.md` + 四个篇章目录 + `附录/` + `en/`）
  里 `hashline|mnemopi` **0**。命中的三处都在「明确对照」那一侧，属 Expected 允许的那半句：
  `manifest.json:436` 的 `gh-oh-my-pi` 是**来源 id**（钉 `v18.15.0` → commit `3fedf8d5`）、
  `sources.json:932–938` 是它的登记（`https://github.com/can1357/oh-my-pi`，MIT）、
  `revisions.json` 6 条是 0.3.x 修订说明里记下的对照面事实。
  正文侧 `oh-my-pi` 出现在 6 个文件 = 中英各 3 章（第 4、7、14 章），全部是 §4.3.6 / §7.x / §14.1.1 的对照段。

**里程碑验收 M7:**

- [x] COMPARE + 共享词存在；审计通过 —— 两份文件都在盘上；审计 0/0/0，允许项逐条给出 `file:line`  
- [x] README 御舆段加「对照 Omp」链接 —— `README.md` 第二分册节新增一句，链 `docs/COMPARE-OMP.md` 与
      `docs/yuyu-overhaul/SHARED-TERMS.md`；顺带把 `docs/COMPARE-OMP.md` 加进 `check_site_links.py` 的
      `FRONT_DOOR`（4 → 5 份门文档）。这一步是**被自己的错逼出来的**：初稿两处链接的圆括号里只写了文件名，
      于是从 `docs/` 解析就指向不存在的 `docs/SHARED-TERMS.md`（正确写法要带目录 `yuyu-overhaul/`）；
      修路径的同时补了负例 —— 临时在 `docs/` 下塞一份探针文件，写一条只带文件名、不带目录的相对链接
      → 报 `dead relative link`，删掉后 `front_door_problems()` 回到 `[]`，
      实跑 `check_site_links OK`（exit 0）。`SITE-LINKS.md` 的负例数随之从四条改为五条
- [x] `附录/D-术语表.md` 的「丛书共享词」短节：**这一格当初写「本轮没做」，16:0x 确实把它做了**，
      现在按盘上事实改勾。中英两侧同轮落笔（`附录/D-术语表.md:302` 与
      `en/Appendices/D-Glossary.md:302`「Series-wide shared terms」，两份 mtime 都是 16:05:59，
      `git status` 两边都是 ` M`）。短节只干一件事：把 **3** 条分歧词摆成一张表并交代清楚 ——
      共享 **15** 条、其中 **12** 条两边完全一致、**3** 条各有主张、omp 专有 **21** 条不入本书释义；
      取舍理由指向 `docs/yuyu-overhaul/SHARED-TERMS.md` 第六节（那组 15/12/3/21 跟着两份登记表走，
      复现命令写在那里），逐章对照指向 `docs/COMPARE-OMP.md` 与 `omp/overhaul/CROSSREF-MAP.md`。
      当初列的三个顾虑逐个量过，没有一个炸：
      ① 标记点与锚点——短节插在原「W-Z」表之后、书末那条 `> **注**` 之前，其后没有条目，
      且新短节自身不带 `<!-- block: … -->`，只有一张表和三段散文；
      ② 字墙——`python scripts/check_book.py` 17:0x 实跑 **176 份 Markdown、321 幅 Mermaid、0 errors**，
      最长的三堵墙仍是 `00-前言.md:106-186`（2,809 字）、`01-…:230-323`（2,555）、`04-…:259-323`（2,221），
      没有一条是新短节；
      ③ 主题索引——因此**不需要** `--regen-index`。
      这三条是 17:0x 那一次量出来的，当时只跑了 `check_book.py` 就去勾，勾早了：
      `yuyu-book/tests` 那 510 个用例里有两道闸不归 `check_book.py` 管，全套跑完才红。
      **没勾掉的是那 3 条分歧本身**：Agent Harness（智能体线束 / 智能体外壳）、Main Loop
      （主循环 / 工作循环，且 omp 侧英文写作 agent loop）、Subagent（sub-agent / subagent）
      现在只是「登记 + 各自正文自洽」，要不要统一仍是你的拍板项——短节把差异写进书里，
      没有替你把差异抹平。
      **17:1x–17:4x 追加：这一格第一次勾早了，红的正是英文那半边。**
      全套跑完是 `FAILED (failures=1)`：
      `test_manifest.ShippedConfigIsSelfConsistent.test_english_manuscript_has_no_untranslated_han_fragments`
      ——`en/**` 正文不许出现裸汉字，唯一豁免是 `apxd` 里「恰好 5 个单元格、且只有第 2 格带汉字」的那一行
      （`test_manifest.py:23` 的 `HAN_RX`、`:56-60` 的豁免条件），而 16:0x 初稿那张对照表是 **4 列、两列带中文**，
      末段还写了一个「第六节」的「六」。改法是把表压成规则认得的形状：汉字全收进第 2 格
      （`智能体线束 / 智能体外壳`），第 3/4/5 格只留英文（`Field at stake` / `This book` / `Omp volume`），
      「第六节」写成「section 6」；中文那半边不动——豁免只管 `en`，`附录/D-术语表.md:306` 仍是 4 列。
      **两侧表格列数从此不一样，是这条闸逼的，不是笔误**，别顺手「修平」。
      **紧接着被第二道闸逮住**：`test_docclaims` 数「术语表有多少条」用的是
      「appendix D 里 ≥5 格且首格带 ASCII 字母的行」（`test_docclaims.py:48` `glossary_rows`），
      新表恰好 5 格、首格是 `Agent Harness`，于是 `en/README.md:109` 那句 **122 bilingual term definitions**
      被顶成 125。同一份书稿三种口径的盘上实测：as-shipped zh 122 / en 125；
      在分歧表处截断 → zh 122 / en **122**；要求末格写「第 N 章」→ 116 / 116（这个口径本身就连原文都对不上）。
      选截断：**那 3 行不是术语条目**，把 README 改成 125 才是把假数写进读者看到的门文档，
      SPEC 明令不许为了变绿动宣称数。为此改了度量本身（`glossary_rows` 遇到
      `## Series-wide shared terms` / `## 丛书共享词` 就停），闸没有放松，只是不再把非条目行数进条目里——
      **本轮唯一一次改测试代码，只此一处**，`yuyu-book/tests/test_docclaims.py` 26,920 → 27,484 B，
      由干净转为 ` M`。
      复测（17:4x 一整套，全在这条格里报清）：`test_manifest` **32 tests OK**、`test_docclaims` **9 tests OK**、
      `python scripts/bookctl.py check --fast` **六步全绿 exit 0**（内部那步就是 510 tests **OK**）、
      四条离线护栏 `check_site_links` / `check_block_markers` / `check_crossrefs` /
      `check_bilingual_parity` 各 **exit 0**（parity 那行 `apxd 17 17 0 2 2`——新标题两边同时多一个，没破对齐）、
      根目录套件 **39 tests OK**、`check_book.py` **176 份 Markdown、321 幅 Mermaid、0 errors**；
      `check_artifact_claims.py` 仍 **exit 1**，报的是 CI(Noto) 505/536 与本机雅黑 518/569 之差，
      这条红是设计如此（见 `PDF-PAGES.md`），不改 README 凑绿。
      书稿一改，16:2x 那两份 en 产物就不再同源，所以 17:35–17:44 按 `PDF-PAGES.md:7` 那条命令重跑了一遍：
      `dist/yuyu-agent-harness-zh.html` **5,783,290 B**（与 16:16 那份同字节，zh 书稿这轮没动）、
      `-en.html` **5,911,611 B**（+58 B）、两份 PDF PyMuPDF 实测 **518 / 569 页、28 / 28 书签、14 index folios**
      ——一个页号都没动，README:116 的 CI 那对与本机那对**全部仍然成立**，
      明细与字节增量记在 `PDF-PAGES.md` 17:35/17:36/17:43/17:44 四行。
- [x] omp 侧同步（「Sync expectation」那一格的可做部分）—— `omp/COMPARE-YUYU.md` 仍归 omp SPEC M6，本轮不代写；
      改的是 `omp/README.md` 里三处与磁盘不符的旧话：「Phase 2 再接流水线」（Book CI 的独立 `omp` job
      已在 `book.yml:107`，产物名 `yuyu-omp-dist`）、「Phase 1 **未接入** `make book`」
      （`make book-omp` / `book-omp-pdf` 在 `Makefile:48` / `:51`）、「对照表见仓库外方案文档」
      （对照表已在仓内，改指 `omp/overhaul/CROSSREF-MAP.md` + 这两份新文档）。
      顺带 `omp/BUILD.md:54` 的套件数：原文引 M2 那条日志写 501，本轮重跑是 **39 + 510**，
      已把「当下读数」与「日志那一刻」分开写清，没有把历史日志改数
- [x] 收尾门禁（2026-11-04，M7 文档落地后重跑）—— **`python scripts/bookctl.py check --fast` 六步全绿、exit 0**：
      deps → `build.py --check --mermaid source`（`CHECK OK`）→ `tests` **39 OK** → `yuyu-book/tests` **510 OK**（241.546s）→
      `check_book.py` 173 Markdown / 321 Mermaid / **0 errors** → `npm run check:diagrams` 321 / 0 errors。
      这是 M0 那条红灯（`manifest-omp.json` 缺 `schema_version`）之后**第一次把这条闸门整条跑绿**，
      而它中间红过一次：`content` 步报 5 条 `missing target`，全是本轮新文档自己写的
      （`SITE-LINKS.md` 门户缺陷那一段贡献 2 条、本文件的验收段贡献 3 条；当时记作
      `SITE-LINKS.md:43`、本文件 `:620`/`:839`/`:841`——那是中途工作树的行号，本文件之后被反复补字，
      索引里存的还是 777 行的旧版，这三个号已无从复现，只能按内容找）—— `check_book.py:146–147` 连行内反引号里的
      href 属性赋值与「方括号紧跟圆括号」的链接写法一起扫，只跳代码围栏。改写这三处后归零，**没有放宽闸门**。
      记这笔账的时候，本文件与 `BASELINE.md` 又各自把同一种写法抄了回去，被这条闸门当场再抓一遍 ——
      同一类错误在一轮里复发两次，说明它值得写进护栏的说明文字，而不只是修掉了事。
      另跑：`check_site_links OK`（门文档 5 份，含新加的 `docs/COMPARE-OMP.md`）、
      `check_crossrefs` book→omp 23 / omp→book 49、0 bad、`check_block_markers` 40 文件 OK、
      `omp/overhaul/audit_structure.py` 33 章六要素齐（exit 0）
- [x] **未** commit/push —— 同 M4/M5/M6 口径：`git log -1` 仍是 `951c0ef`，本轮只写文件，零 `git add`

---

### Task M8: 双语质量收口

**Files:**
- Modify: 不合格的 `en/**` 段落与 `notes.json` en  
- Create: `docs/yuyu-overhaul/BI-AUDIT.md`
- Update: `TRANSLATIONESE-BASELINE.txt` → `TRANSLATIONESE-FINAL.txt`

**Interfaces:**
- Produces: 结构对拍 + 指标不差于基线（或解释例外）

- [x] **Step 1: 结构对拍脚本**

对每一 unit：zh/en 文件存在；H2 数量差 ≤ 阈值（自定 ≤2，记入 BI-AUDIT）；mermaid 数相等。

实测 `docs/yuyu-overhaul/check_bilingual_parity.py`（新建，127 行）exit 0：20 单元
`missing` 全空，**H2 差与 mermaid 差逐个单元都是 0**（合计 zh 164/164、mermaid 160/160，
160 与 `BASELINE.md:10` 独立吻合）；阈值 2 的定法与「收紧到 0 仍绿」的实跑记在
`BI-AUDIT.md` 第一节，变异证明（mermaid 不等 / 文件缺失 / H2 差 3）三类都能判红。
G8 的第三维「罗盘字段」不在这里重复实现：`manifest.json` 无 `langs` 键，
`core.py:337` 因此恒按 `(zh, en)` 校 `question/deliverable/boundary`，
实测 20/20 单元三字段非空，证据位置写进 BI-AUDIT。
这条脚本**没有**加进 `check --fast`（六步是被 README/STRUCTURE/revisions 钉住的宣称），
改串进 `ci-local-yuyu.ps1` 新增的离线护栏段，与另外三条同段。

2026-11-04 续做：双语结构检查已作为独立步骤接入 `book.yml` 与
`check-book.yml`；Book CI 的 push / pull_request 路径过滤同时覆盖检查脚本。
本地复测 20 单元通过，并用内存替换验证缺文件、H2 差 3、Mermaid 不等均判失败。
这项补全不改变 `check --fast` 六步；GitHub Actions 的实际结果留待获准推送后核验。

- [x] **Step 2: 再跑 translationese**

```powershell
python scripts/measure_translationese.py | Tee-Object docs/yuyu-overhaul/TRANSLATIONESE-FINAL.txt
```

Expected: 不差于 BASELINE；变差必须在 BI-AUDIT 写明原因与是否回滚。

实际落盘用的是 Python 侧重定向（PS 5.1 的 `Tee-Object` 默认 UTF-16/ANSI，
中文表头会花；这个坑在 `ci-local-yuyu.ps1` 头部注释里已登记），
产物 `docs/yuyu-overhaul/TRANSLATIONESE-FINAL.txt`（CRLF、UTF-8、exit 0）。
**BASELINE 没有删**，只并置：它是 Y-M1 中途的工作树快照，不是「改造前」，
可比的「改造前」是 HEAD。三点读数（HEAD 15/16/42 ↔ NOW 15/16/42 ↔ BASELINE 19/20/42，
zh HEAD 0/13/13 ↔ BASELINE 2/15/13）逐 unit 列在 BI-AUDIT 第二节。

变差确实发生过一次并已修：M8 起手测到 en `21 行 / 23 处`。BI-AUDIT 用
「`git diff -U0 HEAD` 里这 6 行只出现在 `+` 侧 + HEAD 同一行号是完全不同的材料」
证明 6 行全是本轮新写的英文 prose，逐条改主动（ch06:18、ch07:20/23、
ch08:20/29、ch13:12），改后与中文原句对过意思。**未回滚**，也无需登记例外。
zh 侧 BASELINE 那 2 行（ch10、ch11）在 HEAD 里不存在，属本轮 B3 自伤的愈合，
BI-AUDIT 明写「不许当作战果宣称」。

- [x] **Step 3: notes 英门禁**

```powershell
python -m unittest discover -s yuyu-book/tests -p "test_notes.py" -v
```

Expected: PASS（英无汉字、字数、术语锁）。

实跑 **Ran 14 tests in 0.019s，OK，exit 0**（`BI-AUDIT.md` 第三节把三条点名断言
对应到具体测试名）。因此 `notes.json` 的 en 侧**一字未改**：出厂数据本来就过自己的闸
（`test_the_shipped_notes_pass_their_own_gate`）；Files 清单里那条
「Modify: 不合格的 `en/**` 段落与 `notes.json` en」只落了前半——不合格的是
`en/**` 那 6 行，`notes.json` 不合格的部分为零。

**里程碑验收 M8:**

- [x] BI-AUDIT 勾完  
- [x] notes 测绿  
- [x] **未** commit/push  

收尾门禁实跑（写完 BI-AUDIT 与 BASELINE 的两处 173→174 修正之后）：
`check_site_links` / `check_block_markers` / `check_crossrefs` /
`check_bilingual_parity` 四条 exit 0；`check_book.py` **174 Markdown files,
321 Mermaid diagrams, 0 errors**。BI-AUDIT 里另登记四条「仍缺的证据」，
包括中途 21/23 那一瞬没有机器快照。双语结构护栏的 GitHub Actions
配置已在 2026-11-04 续做时补齐，远端运行结果仍待推送后核验。

---

### Task M9: 总验收与移交（仍不提交）

**Files:**
- Create: `docs/yuyu-overhaul/ACCEPTANCE.md`
- Modify: `docs/YUYU-OVERHAUL-SPEC.md`（勾选里程碑）
- Sync: box `/workspace/omp-book/YUYU-OVERHAUL-SPEC.md`

**Interfaces:**
- Produces: 关闭 K1–K12；提交分组**建议**

- [x] **Step 1: 关闭缺口表**

ACCEPTANCE 逐条：关闭证据路径 / 仍 open 原因。

> 已写：`docs/yuyu-overhaul/ACCEPTANCE.md` 第 1 节那张 K1–K12 表。口径是「关闭 = 门禁可被一条
> 可复跑的证据回答」，不是「做了点什么」。**按设计仍 open 的三格**：K6 的 Actions 真绿（§6.2）、
> K11 的根 `OVERHAUL-SPEC.md` 去留（§6.5，提交窗口决定）、K12 的提交推送（用户拍板稍后）。
> **部分关闭一格**：K9 的 `附录/D-术语表.md`「丛书共享词」那格标的是可选，本轮有意不做——
> 记在哪一格不看行号（M7 Step 2 那个不勾的 box，起头是「`附录/D-术语表.md` 的「丛书共享词」短节：**本轮没做**」），
> 本文件被反复补字，行号一路在漂，`ACCEPTANCE.md` 早期写的 `:884` 已经不复现。
> 另有一条本机不可执行：M9 `Files` 里的 `Sync: box /workspace/omp-book/…` —— 该路径在这台机器上不存在
> （`ls -d` 无此目录），SPEC `:124` 已定「本机仓 > box」，`BASELINE.md:100` 也记了未同步。

- [x] **Step 2: 最终本地**

```powershell
powershell -File docs/yuyu-overhaul/ci-local-yuyu.ps1
python scripts/bookctl.py build --product omp --lang zh --out-dir yuyu-book/.scratch/omp-final-smoke
```

Expected: 御舆 ci-local 绿；omp smoke 绿（证明共存）。

> 两条都绿，进程退出码都是 **0**（2026-11-04 12:52→13:13 ci-local，13:16 omp smoke）。
> ci-local 结论行 `ci-local-yuyu OK`，日志 `docs/yuyu-overhaul/logs/ci-local-yuyu-20261104-125209.log`：
> 4 个护栏 exit 0、`check --fast` 6 步过（39 tests OK、**510 tests OK** in 215.388s、
> 175 Markdown files / 321 diagrams / 0 errors）、build 出两份 HTML + **518 / 569 页**两份 PDF，
> 页数宣称那步 exit 1 按字体口径放行 4 条。
> omp smoke 出 `yuyu-omp-zh.html`（20.0 MB、**39 units**、242 glosses）到指定 out-dir，
> 且**没碰御舆**：跑前跑后 `dist/yuyu-agent-harness-zh.html` 的 md5 都是 `2118bdbd4332`；
> `dist/yuyu-omp-zh.html` 的 mtime 仍停在 08:19 —— `--out-dir` 真的把两本书的产物隔开了。
> 附带一条：smoke 那份与 08:19 那份 **md5 相同**（`3d1d23e6…`），omp 构建是确定的。
> 「共存」不是靠两条都绿推出来的，是靠这两条 md5/mtime 证出来的 —— 细节在 `ACCEPTANCE.md` 第 2 节。

- [x] **Step 3: 建议 commit 分组（只建议，不执行）**

1. `refactor(yuyu-book): converge style/deco/labels split`  
2. `docs(yuyu): pedagogy pass B1–B4`  
3. `fix(plain): guides/glosses/notes evidence`  
4. `docs(site): portal dual entry + STRUCTURE products`  
5. `test: product isolation`  
6. `ci: isolate omp job`（可与 omp SPEC 同一推送窗口，仍另令）  
7. `docs(omp): …` 归 omp SPEC 移交清单  

> 已给：`ACCEPTANCE.md` 第 3 节，七组逐组装什么、为什么这堆能自成一个 commit，并把 567 条脏项
> 拆到组里（`omp/**` 367 · `docs/**` 43 · `.scratch/**` 89 · `en/` 18 · `yuyu_book/*.py` 12 · …）。
> 两处与 SPEC 原设想不同，按实测写：第 3 组「guides/glosses/notes evidence」里御舆那三份登记表
> **与 HEAD 零差异**（M2 的结论是验过、不必改），真正变的只有 `manifest.json` `reading-paths.json`
> `revisions.json`；第 4 组不含 `CONTRIBUTING.md`（本轮没动它）。
> **另立「提交前必须先处理」拦路清单**：写这段时三条都还开着 —— `omp/facts/live-18.16.0/models-list.txt`
> 已在索引里（私有网关名 + 模型清单，`.gitignore` 新规则盖不住已入索引文件）、根 `.scratch/` 未跟踪
> 且未被忽略（89 条）、以及「不要 `git add -A`」。前两条**用户 13:5x 点头后已办**：
> `git restore --staged` 摘掉那份（文件仍在盘上、一个字节没删），`.gitignore` 补 `:85`
> `omp/facts/live-*/models-list.txt` 与 `:91` `/.scratch/`（后者写成带斜杠的形式，只盖仓库根那一份，
> `yuyu-book/.scratch/` 继续由 `:11` 管）。索引 324 → **323**、脏区 567 → **477**。
> **同一次扫描又查出一条，14:2x 用户点头后办了**：`C:\Users\<用户名>` 写在 omp 正文 4 处 + capture 1 处
> （`omp/ch04.md:115`、`omp/ch07.md:202`、`omp/ch29.md:3`、`omp/VERIFY.md:106`、
> `omp/facts/live-18.16.0/config-path.txt:1`）—— 属第二分册的书稿与钉版证据，改法只碰隐私不碰论点，
> 且必须五处同改（capture 与 `ch07.md` 互为引用）。清单在 `ACCEPTANCE.md` 第 3 节拦路第 3 条。
> 一个反直觉的机制：改完工作树，索引里那 5 份仍是**带泄漏的旧 blob**，`git status` 却显示为「已暂存」；
> 不 `git add` 刷新 blob，一次 commit 就会把账户名原样发出去。所以这一轮为脱敏**确实跑了 `git add`**
> （只那 5 条显式路径），索引分布因此从 292 `A` + 31 `AM` 变成 **293 `A` + 30 `AM`**。
> **同一条词也在御舆这一侧，这条是本轮自己造的**：`git grep -l` 扫出本文件 2 处、`BASELINE.md` 1 处
> 把我自己抄进去的字面路径带了进去（两个文件都已在索引里），M9 已全部改写为 `C:\Users\<用户名>` 占位，
> 改写后 `docs/*.md` 与 `docs/yuyu-overhaul/*.md` 复扫 0 命中。
> **还扫出 `docs/yuyu-overhaul/logs/` 14 份里 7 份未跟踪的带它、共 23 处**（解释器与 Node 把自身绝对路径
> 打进 stdout 的副产品），已在索引那 2 份 0 命中 —— 这推翻了第 4 组原写的「14 份 `logs/`」，
> 当时给了两条路（不入仓 / 加忽略规则）。**走的是第三条**：就地把 `Users\<账户名>` 换成
> `Users\<用户名>`，一处文件字节数与退出码都不动，23 处日志 + omp 侧 3 处（`omp/overhaul/logs/`
> 1、`omp/facts/live-18.16.0/plugin-doctor.txt` 1、`tiny-models-list.txt` 1）= **26 处改完**。
> **14:57 又扫出第四面、比这 26 处多一倍半**：同目录 4 份 JSON capture 共 **63 处**
> （`skill-list-json` 54、`agents-unpack-json` 7、`plugin-doctor-json` 1、`ps-json` 1），
> 写的是转义形态 `Users\\<账户名>`（两个分隔符），而我前面三次扫描的模式都只容得下一个字符，
> 于是整批漏报——连「HEAD 里到底几处」也被同一个坑少算了 4 处（下面那条已改）。
> 四份 capture 被 4 份 omp 正文引用 10 次，所以同样就地替换、保留转义形状，改完仍是合法 JSON。
> 机器输出两批合计 **89 处**；可提交面（索引 1086 ∪ 未跟踪未忽略 96 = 1182 个路径）因此
> 从 77 处降到 **13 处**，剩下 13 处全在与 HEAD 逐字节相同的旧文档里，本轮提交面不新增暴露。
> 选它是因为被脱敏的那 7 份日志被 5 份文档引用了 **22 次**（14:4x 实测：`SPEC` 7、`BASELINE` 7、
> `ACCEPTANCE` 5、`PDF-PAGES` 2、`SITE-LINKS` 1；这几本账后来自己又提了一次，14:5x 复数 23——
> 引用数会随记账涨，别当契约），加忽略规则会让「见 `logs/xxx.log`」变成空指向，
> 不入仓则等于把证据面留在本地；而日志的价值是退出码与计数，不是解释器装在哪。
> 改完第 4 组那句「14 份 `logs/`」重新成立，整目录 add 不再有泄漏风险。
> **15:3x 补**：`logs/` 现在 **16 份**（15:1x 两份构建日志，各 1 处、同样就地脱敏），
> 面上的形状命中复扫仍是 13 处 / 6 份，新两份贡献 0。
> 反直觉的一条：这个词**已经在 HEAD 里**（**6 份** video 侧文档共 **13 处**；上一版这里写的「4 份 9 处」
> 是被分隔符坑少算的，`git -c core.quotepath=off grep -c -E "Users[/\\\\:]{1,3}$(现取账户名)" HEAD` 可复算），
> 所以下面的脱敏是**止损、不是首次暴露**；真要清干净得改历史，那是与本 SPEC 无关的另一件事。

- [x] **Step 4: 确认 Git**

```powershell
git status -sb
```

Expected: 仍有改动；**不** commit/push。

> 实跑 `git status -sb`：**479** 行折叠条目（`-uall` 展开是 567），分支行是
> `## p3-pages-split...origin/p3-pages-split`，**不带 `[ahead]`/`[behind]`** ——
> `git rev-list --count --left-right HEAD...origin/p3-pages-split` = `0 0`，
> 与 `git log --oneline -1` 仍是 `951c0ef` 一起构成「零 commit / 零 push」的证据
> （比记忆可靠）。**14:4x 复跑同一对命令：`git status -sb` 478 行（去掉分支行是 477 条），`--porcelain -uall`
> 也是 477 条**——折叠与展开这次不打架了，因为原来被目录折叠的 `.scratch/` 那 89 条已被新规则挡在脏区外。
> 索引里带 `A`/`AM` 的 324 条是**之前某个窗口** `git add` 留下的；本轮对索引一共动过两次手：
> 13:5x 把 `omp/facts/live-18.16.0/models-list.txt` 摘出索引并给它加忽略规则（324 → 323，文件仍在盘上），
> 14:2x 为刷新脱敏后的 index blob 对 5 个显式 omp 路径跑 `git add`（**条数不变**，分布 292 `A` + 31 `AM`
> → 293 `A` + 30 `AM`）。除这 6 条路径外没碰过索引，也仍然没有 commit/push。
> **15:3x 为「生成本地pdf」那轮之后第三次复跑**：`git status -sb` 480 行（去掉分支行 **479** 条）、
> `--porcelain` 与 `--porcelain -uall` 同为 **479** 条，索引 `A`/`AM` 仍是 **323**（293 + 30，一条没动）——
> 构建不碰索引这条是实测出来的，不是推的。涨的 2 条 = `docs/yuyu-overhaul/logs/rebuild-{book,omp}-pdf-20261104-151751.log`
> （`docs/**` 43 → 45），两份日志各 1 处解释器自报路径已就地脱敏。
> `git rev-list --count --left-right HEAD...origin/p3-pages-split` 复跑仍 `0 0`、`git log -1` 仍 `951c0ef`。
> 里面那条隐私问题记在 `ACCEPTANCE.md` 第 3 节拦路清单第 1 条。

**里程碑验收 M9:**

- [x] ACCEPTANCE 签字（日期 America/Adak + 执行者）  
  `docs/yuyu-overhaul/ACCEPTANCE.md`：**2026-11-03 America/Adak**（本机墙钟 2026-11-04 13:2x CST；
  Adak 比上海晚 17 小时 —— `zoneinfo` 实测 11-04 12:57 CST = 11-03 18:57 HST Tue，
  与 SPEC 头部 `v1.0 · 日期：2026-11-03`、`BASELINE.md:3` 同一个日子，不是笔误）。
  执行者：Qoder CLI（`zhuguang-ZFG` 的机器、分支 `p3-pages-split`）。
  注：Git Bash 里 `TZ=America/Adak date` 会退回 `GMT`（本机无 tzdata 可读），别用它定日期；
  用 `python -c "from zoneinfo import ZoneInfo..."` 才是真 Adak。
- [x] 用户已知：提交推送稍后；CI 真绿在推送之后  
  本轮已把「推送之后才会成立的两件事」和「提交前必须先处理的拦路清单」写在 `ACCEPTANCE.md` 第 3 节；
  其中隐私那条（`omp/facts/live-18.16.0/models-list.txt` 当时已在索引里）是**拦路**而非建议，
  用户点头后已摘出索引并补了忽略规则（同一节第 1 条记着前后两个数）。
  第 7 组还留着一个会咬人的细节：6 份 `yuyu-book/*-omp.json` **不在 `omp/` 底下**，
  只 `git add omp/` 会漏掉它们，而 `book.yml` 的 omp job 正靠 `manifest-omp.json`/`sources-omp.json`
  才起得来；`reading-paths-omp.json` 至今还是 `??`，连索引都没进。  

---

## 4. 每阶段验收标准（汇总门禁）

| 门禁 | 标准 |
|------|------|
| 通俗化 | B1–B4 日志齐；抽章有场景+翻车表 |
| 通俗层 | GUIDES-QA 20/20；plain/notes check 绿；双开关可构建 |
| 插画/入门 | reader/gallery 已再生；Mermaid 双语计数一致；art 测绿 |
| 构建 | `ci-local-yuyu.ps1` 绿；`make book` 语义不伤；omp smoke 共存 |
| CI 配置 | 御舆 job 独立；omp 若加入则分 job；**真绿留待稍后 push** |
| 测试 | unittest 绿；product isolation 存在 |
| 协同 | COMPARE-OMP + 共享词；gloss 无 omp 专名污染 |
| 双语 | BI-AUDIT + translationese 不劣于基线 |
| Git | **全程无 commit/push（除非用户另令推翻）** |

---

## 5. 风险与回滚

| 风险 | 可能性 | 影响 | 缓解 | 回滚 |
|------|--------|------|------|------|
| 重构 style/pdf 弄红排版 | 高 | 高 | 每步 `check --fast`；小步差 | 还原 `yuyu_book/*.py` 到基线（仍不 commit） |
| 改 guides 弄红 plain 证据 | 中 | 中 | 先证据后文案；`--check` | 回退 manifest/glosses 字段 |
| 再生 docs 与 pages 契约冲突 | 中 | 中 | ILLUST-SYNC 记录；推送前再 regen | 恢复 docs 旧文件 |
| omp job 拖红整条 CI | 中 | 高 | 分 job、互不 needs | YAML 去掉 omp job |
| 互链导致读者混钉版 | 中 | 中 | COMPARE 文首警告；正文不贴 omp 命令表 | 删互链段 |
| 误把根 omp SPEC 当御舆执行 | 中 | 高 | M0 NOTE；本文件路径 | — |
| 误 commit/push | 低 | 高 | Global §8；M0/M9 检查 | 用户侧 reset（勿未商量 force） |
| docclaims 与 README 页数漂移 | 中 | 中 | 以 CI 字体为准更新宣称 | 恢复数字或修 check 脚本例外 |

---

## 6. 「提交推送稍后」专项说明

1. 本 SPEC **所有 Task 的 Step 均不得**包含必须执行的 `git commit` / `git push` / `gh pr create`。  
2. M4 只准备 workflow 与本地 `ci-local-yuyu`；**GitHub Actions 变绿不是本 SPEC 完成条件**。  
3. 用户之后若下令提交：按 M9 分组；建议与 omp SPEC 移交清单协调是否同 PR（`p3-pages-split` 已脏）。  
4. pages.yml 的 `git diff --exit-code docs/` 将在推送后强制 docs 与生成器一致——推送前再跑一遍 M3 再生。  
5. 根目录 `OVERHAUL-SPEC.md`（omp 内容）的去留在提交窗口处理，避免与 `docs/YUYU-OVERHAUL-SPEC.md` 混淆。

---

## 7. 与 `omp/OVERHAUL-SPEC.md` 协同矩阵

| 主题 | 御舆 SPEC | omp SPEC | 同步点 |
|------|-----------|----------|--------|
| 仓 / 前缀 | `product=book` · `yuyu-agent-harness-*` | `product=omp` · `yuyu-omp-*` | `PRODUCTS.md` |
| 通俗层 | 强化现有 glosses/notes | 新建 glosses-omp/notes-omp | 共享词表 M7↔M6 |
| 插画 | currentColor SVG + Mermaid | 手绘 + Mermaid | 不混装载器 |
| CI | 保 book job | 加 omp job | 分 job、分 artifact |
| 对照文 | `docs/COMPARE-OMP.md` | `omp/COMPARE-YUYU.md` | 互链 |
| Git | 稍后 | 稍后 | 同一推送窗口另令 |
| `make book` | **必须绿** | 不得改其语义 | 每次共享代码后 smoke |

---

## 8. 自我审查（写作时已核对）

| SPEC 需求 | 对应任务 |
|-----------|----------|
| 通俗层 / 入门可读 | M1, M2, M3 |
| 插画 | M3 |
| 双语 | M1, M8 |
| 构建 / 站点 / 测试契约 | M4, M5, M6 |
| 与 omp 协同 | M7 + §7 |
| 目标/非目标 | §0 |
| 现状缺口 | §1 |
| 验收 | §4 + 各里程碑 |
| 风险回滚 | §5 |
| 提交推送稍后 | Global §8 + §6 + M0/M9 |

占位符扫描：无「TBD 以后再说」充当步骤；命令与路径均为仓内真实路径（隔离测试实施时须对齐 `core` 真实 API）。

---

## 9. 执行交接

Plan 落盘位置：

- box 备份：`/workspace/omp-book/YUYU-OVERHAUL-SPEC.md`
- 本机：`D:\Users\claude\claude-code-book-main\docs\YUYU-OVERHAUL-SPEC.md`

**推荐执行方式（用户确认后另开）：**

1. **Subagent-Driven**（推荐）— 每 Task 一个子代理 + 两段审查  
2. **Inline Execution** — 本会话按 `executing-plans` 批次推进  

**与 omp 改造的关系：** 可双线并行，但改 `yuyu_book/*.py` / workflow 时必须跑 §7 smoke；内容编辑互不改对方章节真源。

**当前用户已定：御舆也要彻底改造 SPEC；提交推送稍后。故此处停止在文档交付，不启动 M1，除非另令。**

---

*完。*
