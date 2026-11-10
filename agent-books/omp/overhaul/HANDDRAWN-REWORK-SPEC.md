# 手绘插画改造 SPEC（可执行计划）

> 版本：v1.0 · 2026-11-05 · 状态：已完成（B1–B6 全部落地）
> 依据：`OVERHAUL-SPEC.md` G3「手绘图英文错字清零」、`ILLUST-CHECKLIST.md`、`PYTHON-ILLUSTRATIONS.md`。

**Goal:** 把 `omp/images/` 中剩余的 86 张旧手绘 JPG 全部改成 `scripts/draw_omp_illustrations.py`
的 Pillow 绘制图：尺寸、配色、题注风格与已交付的六张入门图一致，画面文字为中文，
画完即由脚本重新生成，随时可复现。

**非目标:** 不改章节正文的知识结论；不重画已由 SVG 导出替换的 16 张（`visual-redesign/`）；
不改 Mermaid 图；不重排篇章。

## 约束

1. 单图编码后 ≤ `MAX_JPEG_BYTES`（300,000 字节，来自 `yuyu_book/art.py` 的 `PHOTO_BYTES`）。
   脚本在写盘前统一检查，超预算即失败。
2. 画布 1200×800 逻辑像素、`--scale 2`；沿用 `Drawing` 的调色板与 `header/footer/note/paper`
   组件，保证与已交付六张同一视觉语言。
3. 画面文字用中文；`retain`、`ast_edit`、`/fork` 一类命令与路径保留英文原样。
4. 语义以章节正文与图注为准，宁可少画一个箭头，不画错依赖方向。
5. 不改 `yuyu-book/dist/` 与缓存；源稿只有脚本、图注与文档。
6. 每批完成后跑 `audit_structure.py --check`、`audit_delivery.py`、单图预算与构建检查。

## 验收门禁

- `FIGURES` 覆盖 `omp/images/` 全部 92 张脚本图；`tests/test_omp_overhaul.py` 新增
  「每张手绘 JPG 都有生成源」回归：JPG 必须出现在 `FIGURES` 或 `visual-redesign` 映射里。
- `python scripts/draw_omp_illustrations.py --out-dir omp/images` 全量成功，无超预算。
- `python omp/overhaul/audit_structure.py --check` 33/33；`audit_delivery.py` 0 errors。
- `python scripts/bookctl.py check --fast` 绿；`make book-omp` 与 `make book-omp-pdf` 成功。
- 抽查每批至少两张成品，确认中文标签可辨、箭头方向正确、无裁切。
- `PYTHON-ILLUSTRATIONS.md`、`ILLUST-CHECKLIST.md`、`ACCEPTANCE.md` 同步本轮记录。

## 批次

每批一个提交；批内按下列顺序逐张实现，实现完一批再动下一批。

### B1 · 第 1–6 章（15 张）· 完成 0e920c2

| 图 | 画面要点 |
|---|---|
| fig1-3-harness-horse | 同一匹马、两副缰绳：左侧抄原文易错 6.7%，右侧 hashline 68.3% |
| fig2-2-tool-envelope | 模型只写信封；omp 拆信执行，再把结果信封塞回 |
| fig2-3-thinking-dial | 音量旋钮比喻；关/低/中/高，旁注「不是每个模型都有这颗旋钮」 |
| fig3-1-four-shells | TUI、`-p`、SDK、RPC/ACP 四个外壳，共用中间一台引擎 |
| fig3-2-package-map | 自上而下分层：CLI/SDK → TUI → runtime → 模型客户端 → Rust 原生 |
| fig3-3-natives-inplace | 左：每次 fork 外部 rg/bash；右：工具住在进程内，少一次出门 |
| fig4-1-install-tree | 五条安装路：curl、Homebrew、Bun（≥1.4.4）、Nix、PowerShell |
| fig4-2-bun-vs-binary | 安装脚本分叉：有 bun 走包；没有或 `--binary` 走校验过的二进制 |
| fig5-1-provider-board | 插座=供应商，插头=模型；禁用供应商=拔掉整排 |
| fig5-2-model-roles | 工位牌：主力/省钱/深想各就各位，`/model` 换人 |
| fig6-1-tui-zones | 四块地盘：对话区、工具卡片、输入框、状态栏 |
| fig6-2-tool-cards | 工具结果收成可扫读卡片，成功/失败标记分明 |
| fig6-3-preview-accept | proposed → Accept → 磁盘，中间可以反对 |
| fig6-4-ask-picker | 歧义时弹出结构化选项，人点一下 |
| fig6-5-first-project | 打开仓库 → 说需求 → 看卡片 → 验收 |

### B2 · 第 7–12 章（15 张）· 完成 523238a

| 图 | 画面要点 |
|---|---|
| fig7-1-session-git | 会话像分支：节点是历史条目，橙色 leaf 是下一步接点 |
| fig7-3-fresh-clear-new | 三种重开：`/fresh` 换后端句柄、`/clear` 清上下文、`/new` 白纸 |
| fig7-4-export-share | 导出是行李（整包带走），分享是明信片（发出去） |
| fig8-1-read-paths | 同一个 `path` 落成文件/目录/归档/网页/内部资源五种形态 |
| fig8-2-grep-glob | grep 问内容、glob 问名字；两边输出交给 read 定位 |
| fig8-3-ast-grep | 字符串匹配误伤注释；AST 规则只盯语法节点 |
| fig9-3-ast-edit-preview | 提案 → 预览 → Accept，结构改动不盲打 |
| fig10-1-bash-inprocess | 内嵌 brush shell：ls/sed/jq 尽量不 fork |
| fig10-2-pty-background | 前台、PTY 交互、后台 job、受监督服务四条跑法 |
| fig10-3-eval-kernel | 单元格共用变量背包，状态跨调用保留 |
| fig11-1-lsp-workbench | IDE 菜单变工具调用：诊断、跳转、符号、重命名 |
| fig11-2-debug-dap | DAP：断点 → 停下 → 堆栈/变量 → 单步 |
| fig11-3-write-then-diagnose | edit → 诊断波浪线 → 再修 |
| fig12-1-browser-eval | 浏览器窗口变成可调用工具面，Eval 驱动 |
| fig12-2-computer-desktop | 左 DOM 树、右窗口/键鼠/剪贴板；computer 不暴露 DOM |

### B3 · 第 13–18 章（10 张）· 完成 f4e5c74

| 图 | 画面要点 |
|---|---|
| fig13-1-todo-board | 任务板分栏，状态推进有顺序 |
| fig13-2-ask-options | 先问再改：选项、后果、再落笔 |
| fig13-3-task-subagent | 子代理分叉干活，结果回主线 |
| fig14-1-agents-md | 仓库里的说明书被读取成规则 |
| fig14-2-foreign-configs | 外来配置映射进同一套规则 |
| fig15-2-branch-summary | 分支上的摘要保留去向 |
| fig16-2-sqlite-store | 本地 SQLite 存储，读写都在本机 |
| fig17-2-advisor | 第二模型监督，高风险才开 |
| fig18-1-magic-keywords | `ultrathink` 触发隐藏推理说明 |
| fig18-2-approval | 审批门禁按档位放行 |

### B4 · 第 19–23 章（11 张）· 完成 a265c40

| 图 | 画面要点 |
|---|---|
| fig19-1-skill-layout | Skill 目录：元数据与正文分层 |
| fig19-3-skill-vs-ext | skill 是说明书，extension 是代码 |
| fig20-1-mcp-trust | MCP 管道与信任边界 |
| fig20-3-mcp-review | 打开陌生仓库先审查 MCP 配置 |
| fig21-2-hooks | 钩子点在工具执行前后 |
| fig21-3-hook-approve | 审批与钩子串联的顺序 |
| fig22-1-extension-factory | 扩展工厂：import → factory → initialize → events |
| fig22-3-reload | 热重载只换扩展，不重启会话 |
| fig23-2-theme | 主题配置作用于界面 |
| fig23-3-keys | 密钥分层与隔离 |
| fig23-3-profile | profile 叠加在基础配置之上 |

### B5 · 第 24–28 章（18 张）· 完成 fda8d02

| 图 | 画面要点 |
|---|---|
| fig24-1-unknown-repo | 陌生仓库地图：先定位再动手 |
| fig24-1-project-flow | 项目流程从入口到验收 |
| fig24-2-agents-seed | 给仓库种下 AGENTS 规则 |
| fig24-2-arch-sketch | 先画架构草图再改 |
| fig24-3-handoff-checklist | 交付清单逐项勾 |
| fig24-3-loop | 探索—确认—交付的回路 |
| fig25-1-bug-hunt | 抓 bug：症状到根因 |
| fig25-1-repro-first | 先复现再修 |
| fig25-2-debug-session | 断点调查现场 |
| fig25-2-debug-tools | 调试工具分工 |
| fig25-3-red-green | 红绿循环：失败测试变通过 |
| fig26-1-ast-refactor | AST 重构按结构改 |
| fig26-2-task-shards | 子代理分片各管一段 |
| fig26-3-batch-rollback | 批量改动与回滚 |
| fig27-2-atomic-commit | 一次提交只做一件事 |
| fig27-3-pr-body | PR 正文结构 |
| fig28-2-sdk-events | SDK 事件订阅顺序 |
| fig28-3-rpc-frames | RPC 帧往返 |

### B6 · 第 29–33 章与附录 E（17 张）· 完成 b9ec3d1

| 图 | 画面要点 |
|---|---|
| fig29-1-team-pack | 团队包分发 |
| fig29-2-ext-tool | 扩展注册工具 |
| fig29-3-distribute-trust | 分发与信任链 |
| fig30-1-symptom-index | 症状索引到排查入口 |
| fig30-2-auth-provider | 鉴权失败的分层定位 |
| fig30-3-session-stuck | 会话卡住先看 streaming |
| fig31-1-trust-load | 信任加载：先读后跑 |
| fig31-2-no-extensions | 无扩展复现 |
| fig31-3-secrets | 秘密遮罩与边界 |
| fig32-1-token-flow | Token 流向与计费面 |
| fig32-2-role-cost | 角色与成本档位 |
| fig32-3-cache-compact | 缓存命中与压缩 |
| fig33-1-callchain | 调用链自下而上看 |
| fig33-2-from-launch | 从启动入口追到工具 |
| figE-1-pin-version | 钉版本 |
| figE-2-docs-vs-bin | 文档与二进制冲突时以本机为准 |
| figE-3-margin-notes | 页边笔记记漂移 |

## 交付记录

- B1–B6 与上游截图（12d0b0b）均已提交；92 张脚本图全量重生成通过，最大 271,877 字节，无一超 300,000。
- `IllustrationCoverageTests` 断言 112 张 JPG 全部有来源（92 脚本 / 16 SVG / 4 上游截图），三类互斥。
- `audit_structure.py --check` 33/33；`audit_delivery.py` 0 errors；构建与 PDF 记录见 `ACCEPTANCE.md`。
