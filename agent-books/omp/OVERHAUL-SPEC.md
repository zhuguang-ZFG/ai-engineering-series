# 《Omp 从入门到精通》彻底改造 SPEC（可执行计划）

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development`（推荐）或 `superpowers:executing-plans` 按任务逐项落地。步骤使用 checkbox（`- [ ]`）跟踪。  
> **版本**：v1.0 · 日期：2026-11-03（America/Adak）  
> **状态**：2026-11-05 本地可执行验收完成；box 镜像同步与本轮改动的远端 CI 未验，详见 `overhaul/ACCEPTANCE.md`。
> **依据**：`omp/FUSION-PLAN.md`（拍板）、`omp/VERIFY.md`、`omp/outline.md`、`omp/BUILD.md`、已出 `yuyu-omp-zh.html`/`.pdf`、用户拍板（同仓分册 · `yuyu-omp` · 先中文 · 双轨插画 · 仓名不变加 `omp/`）。

**Goal:** 把同仓第二分册 `omp/` 从「可出书的初稿」改造成「厚、透、易读、可核对、可 CI 绿、可与御舆对照」的正式中文分册，并预留英文与术语共享，但不在本 SPEC 执行期内强制 commit/push。

**Architecture:** 内容、插画、构建/CI、版本钉、术语共享五条线并行排队、按里程碑串行验收；御舆 `product=book` 契约冻结，omp 一律走 `product=omp` + `manifest-omp.json` + `output_prefix=yuyu-omp`。插画双轨：架构/流程补 Mermaid，概念漫画保留 FA-023 手绘。

**Tech Stack:** Markdown 书稿 · `yuyu-book` / `scripts/bookctl.py` · Makefile `book-omp`/`book-omp-pdf` · handraw-style FA-023 + C-25 · Mermaid · GitHub Actions（book/check-book/pages）· 本机 `omp/18.16.0`（Windows Bun）与写作钉 `omp/18.15.0` · Humanizer-zh

## Global Constraints

### 收尾口径（2026-11-05）

正文已有 13 张 Mermaid，七篇全部覆盖；16 张问题插画在 `1ec7749` 中已替换。
本轮按实际交付补验收记录，不重复扩写章节。M4 采用已有的独立 `book`/`omp` job，
不再为矩阵示例重排 workflow。英文只预留；`shared_with` 只作相关概念导航。
历史「未 commit/push」复选框记录原执行期，本轮不会用它们掩盖已经存在的提交。
box 镜像仍无访问通道，不能把未同步写成完成；远端 CI 需对应实际提交另行核验。

### 发布授权更新（2026-11-04）

用户已授权提交、推送、合并，待 CI 通过后继续完成所有 SPEC 目标。
本授权取代下文原执行期的「提交推送稍后」限制；旧验收记录保留为当时的事实。
剩余目标须有实际交付与验证后再勾选，不能以获准发布代替完成。

### 执行期修订（2026-11-03，用户拍板，优先级高于下文原文）

1. **M1 取消字数地板**：G1 的「各章 ≥ 4500」与「PDF 320–420 页」降级为观测指标，
   验收改为**结构门禁**（六要素齐 + 证据纪律），与御舆 SPEC M1「非盲目加字、禁止灌水」同一口径。
   契约见 `omp/overhaul/STRUCTURE-GATE.md`，判据脚本 `omp/overhaul/audit_structure.py`。
2. **本机命令实跑已授权**：M1 Step 4 / M5 Step 4 由执行者在本机 `omp/18.16.0` 直接跑，
   含带模型的命令；证据落 `omp/facts/live-18.16.0/`（含 `_manifest.tsv` 时间戳）。
3. **两份 SPEC 按主题交替执行**：M1+Y-M1 → M2+Y-M2 → M3+Y-M3 → M4+Y-M4 → M5/M6 →
   M6+Y-M7 → M7/M8 → Y-M5/M8/M9。共享代码（`plain.py` / workflow / Makefile）只回归一次。
4. **M2 需改构建代码**（原文低估）：`plain.load_plain()` / `load_notes()` 硬编码御舆文件名；
   `validate_plain` 对只有 `zh` 键的单元会 `KeyError`；zh 按语上限是 **36 字**（非原文写的 120 字），
   且「术语锁」要求按语含一个真正出现在该单元的已注册词形。详见 M2 执行注记。

1. **仓形态**：保持 `claude-code-book`；第二分册根目录仅 `omp/`；产物前缀仅 `yuyu-omp-*`。
2. **语言**：本 SPEC 范围内只交付中文 HTML/PDF；`en/omp/` 只建预留结构与 stub，不要求正文齐。
3. **插画**：双轨强制——每篇至少 1 张 Mermaid（架构/流程）；概念图继续手绘 JPG/SVG，经现有 data-URI 嵌入。
4. **钉版**：正文写作钉 `omp/18.15.0`；验证钉写清用户本机 `omp/18.16.0`（Windows · `%USERPROFILE%\.bun\bin\omp.exe`）；冲突以本机二进制为准，记入 `VERIFY.md` / 附录 E。
5. **隔离**：禁止把 Claude Code 专有数字（55 工具、89 Flag 等）贴进 omp 章；交叉引用只用「参见御舆第 N 章 / 参见 omp 第 M 章」。
6. **不迁入**：`omp-src/`、本机 token、`models.yml` 密钥字段、`.env`、handraw-style 整库（仅 CREDITS 记来源）。
7. **不破坏御舆**：任何改动后 `make book`（或等价 `bookctl build --product book --lang zh`）必须仍能通过；御舆测试断言 20 单元不得被 omp 单元污染。
8. **Git**：**提交推送稍后**——完成本 SPEC 各阶段落盘与本地验收即可；`git commit` / `git push` / 开 PR **不在本 SPEC 自动步骤内**，须用户另令。
9. **非官方声明**：封面/前言/manifest `notice` 保持「非官方、与 Stencil Labs / can1357 无隶属」。
10. **文风**：先场景后原理；禁空话套话；命令未实跑标「未验证」；终稿过 Humanizer-zh。

---

## 0. 目标 / 非目标

### 0.1 目标

| ID | 目标 | 可观察结果 |
|----|------|------------|
| G1 | 内容加厚到「资料书」密度 | 第三～五篇各章 ≥ 4500 汉字量级（或 ≥ 约 2.5× 现薄章）；第六～七篇与附录达到可跟做手册深度；全书中文 PDF 页数较现 238 页明显增厚（目标区间 320–420 页，以排版后为准） |
| G2 | 通俗层可用 | `plain_optional` 可关；omp 有独立 glosses 子集 + 按语 notes；罗盘 `guides` 的 question/deliverable/boundary 不再复用章首句 |
| G3 | 双轨插画齐 | Mermaid ≥ 每篇 1、全书 ≥ 12；手绘图英文错字清零清单关闭；图注中文统一 |
| G4 | 构建 / CI / PDF 稳态 | 本地 `make book-omp` + `make book-omp-pdf` 可重复；CI workflow 增加 omp product（zh）；御舆 job 不回归 |
| G5 | 版本钉与 VERIFY 可复跑 | `VERIFY.md` 含 box + 用户本机两套复验命令；附录 E 与页边一致 |
| G6 | 与御舆术语共享 | 核心词条共享表 + omp 增量词；对照阅读短文落盘 |
| G7 | 英文预留 | `en/omp/` stub + manifest 扩展点文档化；不阻塞中文 |

### 0.2 非目标（本 SPEC 明确不做）

1. **不**把 omp 33 章嵌进御舆 Part 1–4。
2. **不**默认交付「御舆+omp 合订 PDF」。
3. **不**自动追 omp 最新 release 改钉（只记漂移）。
4. **不**在本 SPEC 内执行 `git commit` / `git push` / 合并 PR（**提交推送稍后**）。
5. **不**上传 handraw-style 要求的外部站点内容（若 skill 有回传条款，仅记 CREDITS，不代执行）。
6. **不**在书稿或 VERIFY 写入 API key / token / models.yml 密钥。
7. **不**把手绘全部重绘成御舆 `currentColor` SVG（那是可选远期，非本 SPEC）。
8. **不**要求本阶段英文正文齐套。

---

## 1. 现状快照与缺口清单

### 1.1 已具备（勿推倒重来）

| 项 | 位置 / 证据 |
|----|-------------|
| 同仓 `omp/` 书稿 | 本机 `D:\Users\claude\claude-code-book-main\omp\`：前言 + ch01–33 + 附录 A–E + images/ + facts/ + VERIFY + outline |
| 构建闭环 | `make book-omp` / `make book-omp-pdf`；`bookctl --product omp`；`manifest-omp.json`（39 units，`langs=["zh"]`，`output_prefix=yuyu-omp`） |
| 产物 | `yuyu-book/dist/yuyu-omp-zh.html` ≈ 18.6–19.5 MB；`yuyu-omp-zh.pdf` ≈ 24.7–25.9 MB · 238 页 · 约 47 bookmarks |
| 手绘 | `omp/images/` 约 108 张 |
| 核对 | `VERIFY.md`：box `18.15.0`；用户本机 Windows Bun `18.16.0`，`omp -p` 已通 |
| 拍板 | 同仓分册 · 现名 · `yuyu-omp` · 先中文 · Mermaid+手绘 · 仓名不变 |

### 1.2 缺口（按改造优先级）

| ID | 缺口 | 证据 | 归属阶段 |
|----|------|------|----------|
| K1 | 第三～五篇偏薄（多章 2.0–3.9k 字符） | `ch10–13`、`ch15/17/20–23` 等 | M1 |
| K2 | 第六～七篇/附录「加厚过」但仍偏手册提纲感，缺失败案例与对照表 | 章长与实战深度 | M1 |
| K3 | `guides` 质量差：deliverable 常整段复制章首 | `manifest-omp.json` guides | M2 |
| K4 | 无 `glosses-omp` / `notes-omp`；`plain_optional=true` | 目录扫描 | M2 |
| K5 | Mermaid 几乎只有 1 处 | 全 `omp/*.md` 仅约 1 个 ````mermaid` | M3 |
| K6 | 手绘图偶发英文错字/箭头语义 | 历史图 1-1 等；需清单关闭 | M3 |
| K7 | CI 尚未纳入 omp product；改动仍本地未提交 | 分支 `p3-pages-split` 大量 `M`/`??`；workflow 无 omp matrix | M4 |
| K8 | 版本钉双轨说明分散，复跑清单可再结构化 | VERIFY 已有，需与附录 E/页边模板统一 | M5 |
| K9 | 与御舆术语/对照表未落仓 | FUSION §3 仅在方案 | M6 |
| K10 | 英文仅预留意图，无 `en/omp/` stub | 目录无 | M7 |
| K11 | AI 味终检未系统跑 | resources 列了 Humanizer-zh 未执行记录 | M1 末 / M2 |
| K12 | 书仓与 box `/workspace/omp-book` 双份，易漂移 | 两处并存 | 全程：以本机仓 `omp/` 为真源，box 作镜像 |

### 1.3 文件职责地图（改造时触碰范围）

```text
claude-code-book-main/
├── omp/                          # ★ 分册真源（内容、图、VERIFY）
│   ├── 00-前言.md, ch01–33.md, appendix-*.md
│   ├── images/, facts/
│   ├── VERIFY.md, outline.md, BUILD.md, OVERHAUL-SPEC.md(本文件)
│   └── README.md
├── en/omp/                       # M7 预留 stub
├── yuyu-book/
│   ├── manifest-omp.json         # units + guides
│   ├── sources-omp.json, revisions-omp.json
│   ├── glosses.json / glosses-omp.json   # M2/M6
│   ├── notes-omp.json                    # M2
│   ├── build.py, yuyu_book/*             # 仅修 omp 装载缺口时改
│   └── dist/yuyu-omp-zh.{html,pdf}
├── scripts/bookctl.py            # product=omp 已接；CI 对齐时改
├── Makefile                      # book-omp* 已有
├── .github/workflows/book.yml 等 # M4 加 matrix
├── README.md / CREDITS.md / STRUCTURE.md
└── （御舆目录禁止结构性改动）
```

box 镜像：`/workspace/omp-book/` 同步 SPEC 与关键 md；**不以 box 覆盖本机未拉取的改动**。

---

## 2. 分阶段里程碑总表

| 里程碑 | 名称 | 主要交付 | 依赖 | 本地验收命令（摘要） |
|--------|------|----------|------|----------------------|
| **M0** | 冻结基线 | 基线清单、页数/字数快照、禁 commit 确认 | — | 记录现 PDF 238 页与文件哈希 |
| **M1** | 内容加厚 | 薄章扩写 + 实战失败路径 + Humanizer 首轮 | M0 | 抽测章长；抽样实跑命令 |
| **M2** | 通俗层 | 重写 guides；glosses-omp；notes-omp；可关 plain_optional | M1 | `bookctl build --product omp --lang zh` 开 plain |
| **M3** | 插画管线 | ≥12 Mermaid；手绘错字清零；图注规范 | M1 | HTML 内 Mermaid 已渲染；图清单全绿 |
| **M4** | 构建/CI/PDF | workflow 含 omp；本地 PDF 复现；御舆不回归 | M2+M3 可部分并行 | `make book-omp-pdf`；御舆 smoke；**CI 绿灯留待提交后** |
| **M5** | 版本钉与 VERIFY | 统一模板；双环境复验；附录 E 对齐 | M1 | 按 VERIFY §复验命令跑通 |
| **M6** | 御舆术语共享 | 共享词表 + 对照短文 + sources 分区 | M2 | 词表无 CC 专名污染 omp |
| **M7** | 英文预留 | `en/omp/` stub + 文档 | M4 文档即可 | manifest 仍 `langs=["zh"]` |
| **M8** | 总验收 | 缺口表关闭；更新包；**仍不 commit/push** | 全部 | 清单签字 |

并行规则：M3 可与 M1 后半并行；M5 可与 M1 并行；M6 依赖 M2 词表形状；M4 的 workflow 改文件可先写好，**真正「CI 变绿」发生在用户稍后提交推送之后**——本 SPEC 只做到「推上去应能绿」的配置与本地等价检查。

---

## 3. 里程碑任务（可执行）

### Task M0: 冻结基线（不改内容）

**Files:**
- Create: `omp/overhaul/BASELINE.md`（本机仓；box 同步 `/workspace/omp-book/overhaul/BASELINE.md`）
- Modify: 无书稿正文

**Interfaces:**
- Produces: 基线页数、产物大小、git 脏文件列表、钉版字符串

- [x] **Step 1: 记录产物与钉版**（既有 `overhaul/BASELINE.md` 已含双版本、238 页与哈希）

在 `omp/overhaul/BASELINE.md` 写入（数值以本机当时为准，示例格式如下）：

```markdown
# Overhaul baseline

- Date: 2026-11-03 America/Adak
- Branch: p3-pages-split (dirty; no commit in this SPEC)
- Writing pin: omp/18.15.0
- Verified pin (user Windows Bun): omp/18.16.0
- HTML: yuyu-book/dist/yuyu-omp-zh.html (size bytes = …)
- PDF: yuyu-book/dist/yuyu-omp-zh.pdf (size bytes = …; pages = 238)
- Images: omp/images count = 108
- Mermaid fences in omp/*.md: 1
- plain_optional: true
- Commit/push: DEFERRED
```

- [x] **Step 2: 导出脏文件清单**（既有两份 baseline txt）

Run（本机 PowerShell，仓根）:

```powershell
git status -sb > omp/overhaul/git-status-baseline.txt
git diff --stat > omp/overhaul/git-diffstat-baseline.txt
```

Expected: 文件生成；可见 `omp/` 未跟踪与 `Makefile`/`bookctl` 等已改。

- [x] **Step 3: 验收**（基线文件齐；历史暂存偏差已在 BASELINE 记录）

- [x] `BASELINE.md` 存在且含双钉版
- [x] Git 状态已核对：历史暂存偏差保留，发布授权见 2026-11-04 更新；不再宣称全程零提交

**里程碑验收 M0:** 基线可复述；后续扩写以本机 `omp/` 为真源。

---

### Task M1: 内容加厚与去 AI 味（主工作量）

**Files:**
- Modify: `omp/ch08.md`–`omp/ch23.md`（优先薄章）；按需 `ch24`–`ch33`、`appendix-*.md`、`00-前言.md`
- Modify: `omp/outline.md`（章目标字数/图数更新）
- Create: `omp/overhaul/THICKEN-LOG.md`（每章扩写前后字数与新增小节）
- Create: `omp/overhaul/HUMANIZER-LOG.md`

**Interfaces:**
- Consumes: `facts/*.txt`、`VERIFY.md`、oh-my-pi docs（只读，不提交源码树）
- Produces: 加厚后的 md；每章固定结构见下

**每章扩写强制结构（缺一不可）:**

1. 开场具体场景或故障（≤ 2 段）  
2. 原理（用类比 + 一张手绘或 Mermaid）  
3. 最小可跟做实验（命令块；实跑标「本机已验/未验证」）  
4. 常见翻车与对照表  
5. 「与御舆同构点」（1 短段，无 CC 专有数字）  
6. 章末「版本核对清单」3–5 条  

**字数门槛（中文字符粗算，含标点；以 `THICKEN-LOG` 为准）:**

| 批次 | 章 | 目标最小字符 |
|------|----|--------------|
| B1 | ch08–ch13 | 各 ≥ 4500 |
| B2 | ch14–ch18 | 各 ≥ 4500 |
| B3 | ch19–ch23 | 各 ≥ 4500 |
| B4 | ch24–ch29 | 各 ≥ 5000（含失败路径） |
| B5 | ch30–ch33 + 附录 A–E | 附录表补全；E 与 VERIFY 同步 |

- [x] **Step 1: 建立字数脚本**

Create `omp/overhaul/count_chars.py`:

```python
from pathlib import Path
root = Path(__file__).resolve().parents[1]
rows = []
for p in sorted(root.glob("ch*.md")) + sorted(root.glob("appendix-*.md")):
    t = p.read_text(encoding="utf-8")
    rows.append((p.name, len(t), t.count("images/"), t.count("```mermaid")))
for name, n, img, mm in rows:
    print(f"{name}\t{n}\timg={img}\tmermaid={mm}")
```

Run: `python omp/overhaul/count_chars.py`  
Expected: 打印各章字符数；记入 `THICKEN-LOG.md`「扩写前」表。

- [x] **Step 2: 批次 B1 扩写 ch08–ch13**

对每一章：按强制结构补「实验 + 翻车表 + 同构点」；工具行为以 `facts/slice-*.txt` 与官方 docs 为准；**不编造**未验证旗标。

验收抽查：

```powershell
python omp/overhaul/count_chars.py | Select-String "ch0[89]|ch1[0-3]"
```

Expected: 六章均 ≥ 4500。

- [x] **Step 3: 批次 B2–B5** 同上，逐批更新 `THICKEN-LOG.md`。

- [x] **Step 4: 用户本机命令抽验（有模型）**

在用户机器（已通 `omp -p`）跑最小集，结果写入 `VERIFY.md` 新节「加厚期抽验」，**禁止**记录密钥：

```powershell
omp --version
omp -p "只回复两个字：在线" --no-session
# 按扩写章挑选 3 条真实命令（如 omp models、omp token --help）
```

Expected: 版本 `omp/18.16.0`；抽验命令与书中一致或记差异 ID。

- [x] **Step 5: Humanizer-zh 首轮**

对扩写章跑中文去 AI 味（保护 fenced code）；在 `HUMANIZER-LOG.md` 记录文件名与改动类型（删套话/改转折/保留术语）。  
不借机改命令语义。

- [x] **Step 6: 重建中文 HTML（不加 CI 提交）**

> 执行说明：本机无 `make`（Windows + pwsh 环境），改用等价命令
> `python scripts/bookctl.py build --product omp --lang zh`，即 `make book-omp` 的展开式。
> 结果：退出 0，`dist/yuyu-omp-zh.html` 19.7 MB / 39 units / 1 plates / 3 cited links / 0 缺失图；
> 御舆产物未被覆盖。

```powershell
make book-omp
```

Expected: 退出码 0；`yuyu-omp-zh.html` 更新；御舆文件未被覆盖。

**里程碑验收 M1:**

- [x] `THICKEN-LOG` 显示 B1–B5 达标  
- [x] 抽 3 章人工阅读：有场景、有实验、有翻车表  
- [x] `make book-omp` 绿（本机无 make，以 `bookctl.py build --product omp --lang zh` 等价验证，见 Step 6）  
- [x] **未** commit/push  

---

### Task M2: 通俗层（guides / glosses / notes）

**Files:**
- Modify: `yuyu-book/manifest-omp.json`（重写全部 `guides`）
- Create: `yuyu-book/glosses-omp.json`
- Create: `yuyu-book/notes-omp.json`（或仓内既有 notes 机制等价文件；以 `yuyu-book/PRODUCTS.md` / core 实际加载名为准）
- Modify: `yuyu-book/yuyu_book/core.py` / `build.py`（仅当 omp glosses/notes 路径未接线时）
- Modify: `manifest-omp.json`：`plain_optional` → `false`（在 glosses+notes 齐后）

**Interfaces:**
- Consumes: 御舆 `glosses.json` 核心词 id 列表（只读拷贝子集）
- Produces: omp 可读通俗层；HTML 含虚线术语与按语

- [x] **Step 1: 重写 guides 模板**

每条 guide 必须满足：

| 字段 | 规则 |
|------|------|
| `question` | 读者读完能回答的一句话问题（勿抄标题） |
| `deliverable` | 可检查的产出（口答要点 / 一次命令 / 一张表） |
| `boundary` | 本章不讲什么 |
| `sources` | 继续指向 `sources-omp.json` 中的 id |

反例（禁止）：deliverable = 章首第一段原文。

Create checklist `omp/overhaul/GUIDES-QA.md`，39 个 unit 全部勾选。

执行说明：改前 33 章的 `question` 是同一句模板（「读完「<章标题>」后…」，等于抄标题），
`deliverable` 取的是章首第一段原文，`boundary` 33 章同一句——两条反例都踩了。
2026-11-03 逐条重写 39 条；`GUIDES-QA.md` 记录改前实测、39/39 核对表与四条规则的复核命令
（实跑输出 `problems 0`）。

- [x] **Step 2: 建 glosses-omp**

`glosses-omp.json` 最小形状（字段名若与御舆不一致，以 core 解析器为准，实施时先读一个御舆词条抄结构）：

```json
{
  "version": 1,
  "product": "omp",
  "terms": [
    {
      "id": "agent-loop",
      "shared_with": "harness",
      "zh": "智能体循环",
      "en": "agent loop",
      "plain_zh": "模型想一步、调用工具、看结果、再想下一步，直到停。",
      "omp_only": false
    },
    {
      "id": "hashline",
      "shared_with": null,
      "zh": "哈希行锚定",
      "en": "hashline",
      "plain_zh": "改代码时用内容哈希钉住那一行，比纯字符串替换稳。",
      "omp_only": true
    }
  ]
}
```

首批至少：**共享 20 词** + **omp 增量 15 词**（hashline、mnemopi、smol/slow、omp -p、compaction、skill://、`--no-extensions` 等）。

执行说明：落地 36 词，沿用御舆 `glosses.json` 的词条形状
（`term` / `forms` / `plain` / `analogy` / `why` / `evidence`，证据用 `file:line`——omp 没有 `<!-- block: -->` 锚点）。
**「共享 20 + omp 增量 16」这句当时就核不上，2026-11-04 更正**：与御舆 `glosses.json`（102 条）按 id 逐条比对，
实际是**同 id 15 条 + omp 专有 21 条**；登记表里没有 `shared_with` / `omp_only` 字段，所以这个拆分目前只能靠跨文件比对得出
（`M6/M7` 那一步「`shared_with` 字段维护」还没做）。其中 `yolo` / `toks` / `skill-uri` / `trusted-extension` 四个词标了 `"mark": false`：
它们只以行内代码形态出现，而代码通道只给驼峰/下划线/数字加虚线，纯小写词标上会把正文变成一片虚线。
「四词仍留在附录 D 里可查」这句**当时是假的**——36 词里有 17 词在 `omp/appendix-D.md` 全文找不到。
2026-11-04 补齐 17 词后成立；同一天为了让附录 D 这一单元不超过 `plain.MAX_PANEL = 22`，
另把 12 个产品专有名降为 `priority: "extra"`，于是 36 词中**正文加虚线 20 个、只登记不标 16 个**，
全书签入虚线 317 → 242。细节与代价记在 `omp/overhaul/GUIDES-QA.md`、`omp/BUILD.md`。

- [x] **Step 3: 建 notes-omp**

为目标：前言 + 33 章 + 5 附录 = **39** 条按语（可分两批：先 20 条核心章，再补齐）。  
每条 ≤ 120 字；点明「边界/易混/钉版」之一。

执行说明：39 条一次写齐。实际按 `plain.py` 的 `NOTE_LIMITS`（zh ≤ 36 字）执行，比本条 120 字更严；
术语锁（每条按语必须咬住本章真实出现的一个已注册词形）逐条验过。

- [x] **Step 4: 接线并关闭 plain_optional**

确认 `build.py --manifest manifest-omp.json` 加载 glosses-omp / notes-omp 后：

```powershell
python scripts/bookctl.py build --product omp --lang zh
```

Expected: 成功；若缺文件应失败并报路径（先修接线再关 `plain_optional`）。

然后将 `manifest-omp.json` 中 `"plain_optional": true` 改为 `false`，再构建一次。

Expected: 仍成功；HTML 源码可搜到通俗层标记（具体 class 以 yuyu-book 为准）。

执行说明：接线断在两处，都在构建侧、没动正文——
(1) `scripts/bookctl.py` 的 omp 分支硬编码了 `--no-plain`，通俗层永远加载不到，已删；
(2) `yuyu_book/registry.py` 的登记表白名单只列了 `reading-paths.json`，没有 `reading-paths-omp.json`，
已于 `FILES` 补一行（`glosses-omp` / `notes-omp` 本来就在白名单里）。
先跑 `build.py --manifest manifest-omp.json` 让登记表逐项校验（缺档位文件时它确实报错），
再把 `plain_optional` 改成 `false`，两次构建都退出 0。产物：
`dist/yuyu-omp-zh.html` 20.0 MB / 39 units / 317 glosses / 39 lead bands / 381 tier chips / 39 keeper notes；
（这一行是 M2 收尾那一刻的日志，保留不改。**2026-11-04 复跑同一命令是 242 glosses**：附录 D 补回 17 个词条后
该单元超过 `plain.MAX_PANEL = 22`，12 个产品专有名降为 `extra`。`glosses ≥ 35 词` 这条验收仍然成立——
降的是「正文加不加虚线」，词条本身都还在登记表里。）
HTML 里可搜到 `class="gloss"`（带 `data-g`）、`gloss-pop`、`sec-tier t-start`。御舆产物未被覆盖。

**里程碑验收 M2:**

- [x] `GUIDES-QA.md` 39/39  
- [x] glosses ≥ 35 词；notes = 39  
- [x] `plain_optional=false` 构建通过  
- [x] **未** commit/push  

---

### Task M3: 插画管线（Mermaid + 手绘修图）

**Files:**
- Modify: 各篇代表章 md（插入 Mermaid）
- Modify/Create: `omp/images/*`（重画错字图）
- Create: `omp/overhaul/ILLUST-CHECKLIST.md`
- Modify: `yuyu-book/yuyu_book/art.py` 仅当 PNG/JPG 门禁误杀 omp 图时（最小改动 + 测御舆）

**Interfaces:**
- Produces: 双轨资产；HTML/PDF 可显示

**Mermaid 最低清单（≥12）:**

| ID | 建议落章 | 图主题 |
|----|----------|--------|
| MM01 | ch01 | agent 循环（模型→工具→观察→回模型） |
| MM02 | ch03 | 四入口共用引擎 |
| MM03 | ch04 | 安装路径选择 |
| MM04 | ch07 | 会话树 fork/resume |
| MM05 | ch09 | hashline 改写流程 |
| MM06 | ch13 | task 子代理 |
| MM07 | ch15 | compaction 阶梯 |
| MM08 | ch16 | retain/recall/reflect |
| MM09 | ch19 | skill 发现路径 |
| MM10 | ch20 | MCP 信任边界 |
| MM11 | ch28 | SDK vs RPC |
| MM12 | ch31 | 扩展加载与 `--no-extensions` |

手绘：保留 FA-023；修图优先「含英文标签的图」与「箭头语义错误」；图下题注一律中文。

- [x] **Step 1: 建清单**（`overhaul/ILLUST-CHECKLIST.md`）

`ILLUST-CHECKLIST.md` 列：文件名 · 问题 · 状态(open/fixed) · 负责人。

- [x] **Step 2: 插入 MM01–MM12**（既有正文共 13 张，七篇都有图）

示例（ch01）：

````markdown
```mermaid
flowchart LR
  U[用户] --> M[模型]
  M -->|工具请求| T[工具执行]
  T -->|观察结果| M
  M -->|最终答复| U
```
````

- [x] **Step 3: 修手绘错字**（16 张已知问题图已替换，见 checklist 与 visual-redesign 记录）

对 checklist 每条 open → 重生成或手工标注覆盖 → fixed。

- [x] **Step 4: 构建检查**（13/13 图版含 SVG，102 张位图内嵌；本轮 HTML/PDF 均通过）

```powershell
make book-omp
# 抽查 HTML：mermaid 已变成 SVG；images data-uri 仍在
```

Expected: 退出 0；`Select-String` 统计 md 内 ````mermaid` ≥ 12。

**里程碑验收 M3:**

- [x] Mermaid ≥ 12；已知问题图 checklist 全 fixed
- [x] PDF 抽 5 页图可辨、题注中文（47、101、192、213、260 页，截图见 ACCEPTANCE）
- [x] 御舆 `make book` smoke 仍过（本轮中文 HTML，20 units）
- [x] 本轮未 commit/push

---

### Task M4: 构建 / CI / PDF（配置先到位；推送后变绿）

**Files:**
- Modify: `.github/workflows/book.yml`（matrix `product: [book, omp]`；omp 仅 `lang: zh`）
- Modify: `.github/workflows/check-book.yml`（omp `check` 子集或 `--product omp`）
- Modify: `omp/BUILD.md`、`yuyu-book/PRODUCTS.md`
- Modify: 按需 `pages.yml` 双入口文案（可先 TODO 注释，站点改可放推送后）

**Interfaces:**
- Produces: 「推送后 CI 应绿」的 workflow；本地 PDF 可重复构建

- [x] **Step 1: 本地 PDF 复现**

```powershell
make book-omp-pdf
```

Expected: `yuyu-omp-zh.pdf` 生成；页数 ≥ 基线 238（加厚后应更高）；书签含前言/篇/附录。

执行说明：本机无 `make`，跑的是它的展开式 `python scripts/bookctl.py build --product omp --lang zh --pdf`。
2026-11-04 08:20 那次 exit 0，日志原话 `yuyu-omp-zh.pdf: 30.6 MB, 321 pages, 49 bookmarks, 0 index folios`。
页数 321 ≥ 238（基线 +83）。书签 49 条，用 PyMuPDF 取 `get_toc()` 核过结构：一级 16 条＝**前言 + 七篇 + 五附录 + 原理札记 / 按语集 / 来源与许可**，
「含前言 / 含篇 / 含附录」三项实测 True / True / 5。逐次构建的字节数与页数对照在 `docs/yuyu-overhaul/PDF-PAGES.md`。

- [x] **Step 2: 御舆不回归**（本轮中文渲染成功；共享 check 六步通过，46 + 515 项测试）

```powershell
python scripts/bookctl.py build --product book --lang zh --out-dir yuyu-book/.scratch/book-smoke
```

Expected: 成功；勿覆盖正式 `dist/yuyu-agent-harness-zh.*` 除非有意。

- [x] **Step 3: 编写 workflow 片段（先改文件，不推送）**（独立 omp job 已存在；本轮补结构、交付门禁及源稿装配）

`book.yml` 思路（实施时按现有 YAML 风格合并，勿发明不存在的 action API）：

```yaml
strategy:
  matrix:
    product: [book, omp]
    # omp: force zh-only in job steps when product==omp
```

omp job 步骤等价本地：

```text
python scripts/bookctl.py build --product omp --lang zh --pdf
```

artifact 名：`yuyu-omp-zh`。

- [x] **Step 4: 本地模拟 CI 脚本**（`ci-local.ps1` 已落盘，显式检查退出码，默认写到 `.scratch/`）

Create `omp/overhaul/ci-local.ps1`:

```powershell
$ErrorActionPreference = "Stop"
python scripts/bookctl.py build --product book --lang zh --out-dir yuyu-book/.scratch/ci-book
python scripts/bookctl.py build --product omp --lang zh --pdf
Write-Host "ci-local OK"
```

Run: `powershell -File omp/overhaul/ci-local.ps1`  
Expected: `ci-local OK`。

- [x] **Step 5: 文档声明**（`BUILD.md` 写明两个 job、本地脚本与远端运行的区别）

在 `BUILD.md` 增加一节「CI：提交推送稍后；推送后期望 book.yml matrix 含 omp zh」。

**里程碑验收 M4:**

- [x] 本地 `ci-local.ps1` 绿（332 页、49 书签，末行 `ci-local OK`）
- [x] workflow 已审阅并通过 YAML 解析
- [x] 远端范围已明确：既有 `1ec7749` 两项 CI 成功，本轮未提交改动尚无远端结果
- [x] 本轮未 push

---

### Task M5: 版本钉与 VERIFY 结构化

**Files:**
- Modify: `omp/VERIFY.md`
- Modify: `omp/appendix-E.md`
- Create: `omp/overhaul/PIN-POLICY.md`
- Modify: 章末「版本核对清单」模板统一（可脚本批量检查有无清单标题）

**Interfaces:**
- Produces: 可复跑核对；双环境表

- [x] **Step 1: 写 PIN-POLICY**（`overhaul/PIN-POLICY.md`）

```markdown
# 钉版策略
- 写作钉：omp/18.15.0（书中默认命令/文档切片）
- 验证钉：用户本机 omp/18.16.0（Windows Bun）
- 冲突：以验证环境二进制为准，差异记 VERIFY 差异表 + 附录 E
- 禁止：无 VERIFY 条目就改附录数字
- 发版：不自动追最新 upstream
```

- [x] **Step 2: VERIFY 增加「标准复验矩阵」表**（含 Windows 新复验与 box 历史记录，附录 E 同步字段）

列：环境 · 版本 · 安装 · 命令 · 期望 · 最近实跑日期(America/Adak)。

- [x] **Step 3: 扫描缺清单的章**（33/33，结构审计严格模式通过）

```powershell
Select-String -Path omp/ch*.md -Pattern "版本核对" -List
```

Expected: 33 章都有命中；缺则补。

- [x] **Step 4: 本机复跑**（用户机；UTC 2026-11-05 03:31，三条均 exit 0，摘要 `recheck-20261105.txt`）

```powershell
omp --version   # omp/18.16.0
omp --help | Select-Object -First 5
omp models | Select-Object -First 5
```

更新 VERIFY 日期戳；勿写 providers 密钥。

**里程碑验收 M5:**

- [x] PIN-POLICY + VERIFY 矩阵完整
- [x] 33 章均有版本核对清单
- [x] 本轮未 commit/push；既有发布授权与历史提交单独保留

---

### Task M6: 与御舆术语共享与对照

**Files:**
- Create: `omp/COMPARE-YUYU.md`（FUSION §3 精简读者版）
- Create/Modify: `yuyu-book/glosses-omp.json`（`shared_with` 字段维护）
- Modify: `yuyu-book/sources-omp.json`（对照面来源）
- Modify: 顶层 `README.md` 分册入口增加「对照阅读」链接（仅 omp 段）

**Interfaces:**
- Consumes: FUSION-PLAN 对照表  
- Produces: 读者可读对照；词表无 CC 专名泄漏

- [x] **Step 1: 落盘 COMPARE-YUYU.md**（阅读选择、十行同构点与实现边界）

含：何时先读御舆、何时只读 omp、10 行同构点、明确「不同实现勿混」。

- [x] **Step 2: 词表审计**（21 个有效 `shared_with`；定义污染 0；独立对照来源固定到完整 SHA）

脚本/人工检查 `glosses-omp.json`：不得出现「55 个工具」「QueryEngine」等御舆专有实现名作为 omp 定义。

- [x] **Step 3: README 入口**（中英文门面均补 Omp 对照与英文预留链接）

在第二分册段落加链接：`omp/COMPARE-YUYU.md`。

**里程碑验收 M6:**

- [x] 对照文存在；词表审计通过
- [x] 本轮未 commit/push

---

### Task M7: 英文预留（不翻译正文）

**Files:**
- Create: `en/omp/README.md`（说明 Translation pending；中文为权威）
- Create: `en/omp/.gitkeep` 或 `STATUS.md`
- Modify: `yuyu-book/PRODUCTS.md`（写明 `langs` 扩展步骤）
- Modify: `omp/BUILD.md`（英文开启条件清单）

- [x] **Step 1: 建 stub 目录与说明**（`en/omp/README.md`、`STATUS.md`，无汉字；开启步骤见 PRODUCTS/BUILD）

`en/omp/README.md` 内容要点：权威语言 zh；开启 en 需全量翻译 + 零汉字门禁 + manifest `langs` 含 `en`。

- [x] **Step 2: 确认 manifest 仍只有 zh**（交付审计与源码装配均通过）

`manifest-omp.json` → `"langs": ["zh"]` 不变。

**里程碑验收 M7:**

- [x] stub 存在；中文构建不受影响
- [x] 本轮未 commit/push

---

### Task M8: 总验收与移交（仍不提交）

**Files:**
- Create: `omp/overhaul/ACCEPTANCE.md`
- Modify: `omp/OVERHAUL-SPEC.md`（勾选里程碑）
- Sync: box `/workspace/omp-book/OVERHAUL-SPEC.md`

- [x] **Step 1: 核对缺口表 K1–K12**（K1–K11 本地关闭；K12 真源明确，box 镜像未验，逐项写入 ACCEPTANCE）

在 `ACCEPTANCE.md` 逐条：关闭证据路径 / 仍 open 原因。

- [x] **Step 2: 最终本地构建**（ci-local 与共享 check 通过，`chars-final.txt` 与脚本输出一致）

```powershell
powershell -File omp/overhaul/ci-local.ps1
python omp/overhaul/count_chars.py > omp/overhaul/chars-final.txt
```

- [x] **Step 3: 移交清单（给后续「提交推送」用）**（ACCEPTANCE 记录本轮建议分组；历史导入和插画提交不重复）

列出建议 commit 分组（**只建议，不执行**）：

1. `feat(omp): import volume + bookctl product`  
2. `docs(omp): thicken chapters …`  
3. `feat(omp): plain layer guides/glosses/notes`  
4. `feat(omp): mermaid + illustration fixes`  
5. `ci: matrix product omp zh`  

- [x] **Step 4: 再次确认 Git**（本轮只改工作树；既有两份未跟踪日志保留）

```powershell
git status -sb
```

Expected: 仍有改动；**无**新的「已推送」假设；**不**运行 commit/push。

**里程碑验收 M8:**

- [x] ACCEPTANCE 签字：Codex，2026-11-04 America/Adak（2026-11-05 Asia/Shanghai）
- [x] 已区分本地通过、既有提交的远端成功与本轮改动的远端未验
- [ ] box `/workspace/omp-book/` 镜像同步（当前无访问通道；本机真源不受影响）

---

## 4. 每阶段验收标准（汇总门禁）

| 门禁 | 标准 |
|------|------|
| 内容 | 薄章批次达标；强制结构六要素齐；Humanizer 日志存在 |
| 通俗层 | guides 39 条合格；glosses≥35；notes=39；`plain_optional=false` 可构建 |
| 插画 | Mermaid≥12；手绘 checklist 清零；图注中文 |
| 构建 | `make book-omp` / `make book-omp-pdf` 绿；御舆 smoke 绿；`ci-local.ps1` 绿 |
| CI 配置 | workflow 含 omp zh；**真绿留待稍后 push** |
| 钉版 | 写作 18.15.0 / 验证 18.16.0 双写；VERIFY 可复跑 |
| 术语 | COMPARE + 共享词无污染 |
| 英文 | stub only |
| Git | **全程无 commit/push（除非用户另令推翻本约束）** |

---

## 5. 风险与回滚

| 风险 | 可能性 | 影响 | 缓解 | 回滚 |
|------|--------|------|------|------|
| 改 `art.py`/`core.py` 弄红御舆 | 中 | 高 | 每次改后跑 book smoke；最小 diff | `git checkout --` 御舆相关文件（仍不 commit） |
| 关 `plain_optional` 后构建失败 | 中 | 中 | 先齐 glosses/notes 再关；保留开关回退 | 改回 `true` |
| 加厚引入未验证命令 | 高 | 高 | VERIFY 差异表；正文标未验证 | 删命令或改附录 |
| 双份 box/本机漂移 | 中 | 中 | 真源=本机 `omp/`；SPEC 同步两边 | 以本机覆盖 box |
| CI matrix 超时/字体 | 中 | 中 | omp 仅 zh；PDF 可分 job | matrix 去掉 omp 直至修复 |
| 页数暴涨导致 PDF 过大 | 中 | 低 | 图压缩；附录表勿贴长日志 | 降图分辨率 |
| 误 commit/push | 低 | 高 | SPEC 全局约束第 8 条；M0/M8 检查 | 用户侧 reset（勿 force 未商量） |
| handraw 授权回传 | 低 | 中 | 只记 CREDITS，不代传 | — |

---

## 6. 「提交推送稍后」专项说明

1. 本 SPEC **所有 Task 的 Step 均不得**包含必须执行的 `git commit` / `git push` / `gh pr create`。  
2. M4 只准备 workflow 与本地 `ci-local`；**GitHub Actions 变绿不是本 SPEC 的完成条件**。  
3. 用户之后若下令提交：按 M8 建议分组提交，先 push 再盯 `book.yml` / `check-book.yml`；若红，用本 SPEC 回滚表处理。  
4. 当前本机分支示例：`p3-pages-split` 已有御舆重构脏改动——**omp 提交策略需与用户确认是否同 PR 或另开 `feat/omp-volume`**（确认动作本身也可稍后）。

---

## 7. 自我审查（写作时已核对）

| SPEC 需求 | 对应任务 |
|-----------|----------|
| 内容加厚与通俗层 | M1, M2 |
| 插画管线 | M3 |
| 构建/CI/PDF | M4 |
| 版本钉与 VERIFY | M5 |
| 与御舆术语共享 | M6 |
| 英文预留 | M7 |
| 目标/非目标 | §0 |
| 现状缺口 | §1 |
| 验收标准 | §4 + 各里程碑 |
| 风险回滚 | §5 |
| 提交推送稍后 | Global Constraints §8 + §6 + M0/M8 |

占位符扫描：无 TBD/TODO 充当步骤；命令与路径均为仓内真实路径。

---

## 8. 执行交接

Plan 落盘位置：

- box：`/workspace/omp-book/OVERHAUL-SPEC.md`
- 本机：`D:\Users\claude\claude-code-book-main\omp\OVERHAUL-SPEC.md`

**推荐执行方式（用户确认后另开）：**

1. **Subagent-Driven**（推荐）— 每 Task 一个子代理 + 两段审查  
2. **Inline Execution** — 本会话按 `executing-plans` 批次推进  

**当前交付：本地执行与验收已完成，详见 `overhaul/ACCEPTANCE.md`。旧的「只写 SPEC」状态已被后续执行取代；box 镜像与本轮远端运行仍按实际状态保留。**

---

*完。*
