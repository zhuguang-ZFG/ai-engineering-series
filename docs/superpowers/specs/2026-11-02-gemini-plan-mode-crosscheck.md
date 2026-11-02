# 设计稿：gh-gemini-cli 对照面补落第 14 章

日期：2026-11-02。状态：已批准（用户选定「补正文，走完整流程」）。

## 背景

`gh-gemini-cli` 于 2026-10-26（`e0c8870`）登记入册，scope 自述落点为「第 14 章的对照面」，但中英两版第 14 章正文从未出现 Gemini 字样（`git log -S "Gemini"` 对两文件全史为空）——登记先行、正文未落。本轮把缺口补上。

## 复核基座（2026-11-02 实测）

- latest release **v0.66.0**（2026-10-27 发布），轻量 tag 直接指向 commit `970413207732f5d4d8c50540c7fc359c44fdaaf2`；仓库 108,672 star，`pushed_at` 2026-11-02T01:22Z——「仓库仍在活跃提交」仍真。
- README 顶部 NOTE 仍声明：未付费档与 Google One 用户自 2026-06-18 起由 **Antigravity CLI** 承接；且「Gemini CLI 未针对 Gemini 4 Argon 优化」——「官方入口已迁」仍真。
- `docs/cli/plan-mode.md` 在登记钉的 v0.65.0 即已存在（raw 探测 200），v0.66.0 仍在：Plan Mode 为只读规划环境、**默认开启**；入口三条——启动旗标 `--approval-mode=plan`、`Shift+Tab` 在 Default→Auto-Edit→Plan 循环、`/plan [goal]` 或自然语言触发 `enter_plan_mode` 工具（YOLO 档无此工具）；规划期**显式工具白名单**（read_file/list_directory/glob/grep_search/google_web_search/get_internal_docs/研究子代理；web_fetch 须单独确认）；计划落成 plans 目录的 Markdown 文件，Ctrl+X 开外部编辑器改步骤、留行内评论，CLI 察觉改动重审后再送批；批准即退出 Plan Mode 开始实施。
- 本机未装 gemini：**所有 claims 以 tag 内文档为准**，不引本机行为。

## 决定

1. **唯一落点**：第 14 章 §14.1.1 末尾、omp 对照段（zh/en L34）之后、身份引语框之前，各插一段双语对照（各 +2 行）。角度：Claude Code 的 Plan 模式是权限状态机的档位，Gemini CLI 把这档位做成默认开启的入口、把「规划期只读」写成显式工具白名单、把计划本身做成一份可协作编辑的落盘文档——与 omp 的「权限决策 × 成本决策」互为两翼。
2. **身份引语框扩名**：「oh-my-pi」→「oh-my-pi 与 Gemini CLI」，中英同步（一段身份框覆盖两段对照）。
3. **登记重钉**：`gh-gemini-cli` v0.65.0 → **v0.66.0** + commit `970413207732f5d4d8c50540c7fc359c44fdaaf2`；`accessed`/`snapshot` 记 2026-11-02（README NOTE 与 plan-mode.md 当日复核）；scope 重写为上述具体机制（zh ≤180 字符、en ≤400）；`CREDITS.md` 表行同步 tag/commit/描述，§三叙事补一句记 2026-11-02。
4. 锚点：dry-run 实测 `--after 34 --delta 2` 双语各平移 **5 条**（先 dry-run 再 `--write`）。

## 不做的事

- 不新增小节或单元；不铺图版（plate 数 167 不变）。
- 不展开 gemini 全部 CLI 旗标/子命令矩阵。
- Antigravity 迁移只在登记与对照身份层面留一句「产品位置会变」，不展开商业细节。
- 不改 `docs/notes/` 草稿（该草稿执行记录只记 omp 路由，gemini 不在其 §四 清单内）。

## 验收

五道闸全绿（unittest 442+35、双版 CHECK OK 167 plates、check_book 94 files/320 diagrams/0 errors、diagrams 320/0）；账本末条按契约带套件数收尾；推送 → PR → CI 绿 → 合并 → 本地 PDF 重建。
