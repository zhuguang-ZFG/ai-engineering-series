# omp 对照面扩容设计：把 Oh My Pi 落进第 7、14 章

日期：2026-11-02　状态：已采纳，随实施计划执行
负责人：正文与构建器同仓演进，无独立分支

## 1. 要解决的问题

oh-my-pi（omp）目前只在第 4 章 §4.3.6 占了一格（`--approval-mode` 四值 +
`--auto-approve`），素材源 `docs/notes/agent-cli-field-guide-draft.md` 里它最有性格的
两组能力仍停在草稿层，读者看不到：

| 能力组 | 草稿条目 | 回扣章 |
| --- | --- | --- |
| 上下文的显式手术 | `--no-context-files`、`compress`（重写进稠密 prompt 语域并报告丢了什么）、`find`（描述行为→返回文件与行段）、`toks`（多套离线 tokenizer 同时计数） | 第 7 章 上下文管理 |
| 规划／执行模型分离 | `--smol/--slow/--plan` 三角色、`--prewalk`（todo 立起后首次写文件切便宜模型）、`--plan-yolo`（起手只读规划→首次 resolve 自动批→`--plan-yolo-into` 去写） | 第 14 章 Plan 模式 |

草稿 §四 自己已论证这两组分别回扣第 7、14 章；本轮把它们按草稿 §六 定下的
「只搬那一格、不整页搬运」纪律落进正文。

## 2. 证据基础（2026-11-02 重验）

- 本机 omp 已从 18.14.2 升到 **18.15.0**。草稿全部 omp 断言在 18.15.0 的
  `--help` 上重抓核验：`--approval-mode` 四值、`--auto-approve`、`--smol/--slow/--plan`、
  `--prewalk`、`--plan-yolo`、`--plan-yolo-into`、`--no-context-files` 与
  `compress`／`find`／`toks` 子命令全部仍在，help 原文与草稿口径一致。
- 两处口径随新版收紧：`--thinking` 的档位细化为
  `off|minimal|low|medium|high|xhigh|max|auto`（草稿写 `off..max`）；新版另有
  `--no-prewalk`。两者本轮都不进正文，避免为不引用的细节扩面。
- GitHub tag `v18.15.0`（轻量标签，直指 commit）
  → `3fedf8d53267e32a6d7521ce725fdcc4a36fdc67`，MIT。登记按规矩重钉。

## 3. 已定的决策

1. **落点三处，全是对照面身份**：
   - 第 7 章 §7.5 末尾（多文件项目策略表之后、实战练习分隔线之前）加小节
     「对照面：把压缩做成手上的刀」：一段正文 + ch04 §4.3.6 同款的「对照面的
     身份」引语框。要点：四级压缩是装在循环里的自动防线，omp 把同一层的几刀
     做成用户手上的显式工具；「报告丢了什么」与 §7.3 的双阶段输出同一自觉。
   - 第 14 章 §14.1.1 末尾（「没有 Plan 模式会怎样」表之后、14.1.2 之前）加
     对照段 + 引语框。要点：Claude Code 的 Plan 模式是权限状态机里的档位，
     omp 把「规划用哪个模型、执行用哪个模型」写成定价决策——先规划后执行
     在这家宿主里同时是权限决策和成本决策。
   - 第 4 章 §4.3.6 的 omp 条目只把版本号 18.14.2 换成 18.15.0（断言重验未变）。
2. **登记重钉并扩 scope**：`sources.json` 的 `gh-oh-my-pi` 换
   tag `v18.15.0` + commit `3fedf8d5…`，`accessed`／`snapshot` 改 2026-11-02，
   `scope` 扩为「第 4 章 §4.3.6、第 7 章 §7.5、第 14 章 §14.1.1 的对照面之一，
   本机 omp 18.15.0 实测」。`CREDITS.md` §三 同步该行。
3. **双语逐行镜像**：两处新增块的中英行数一致，插入点两侧同行号
   （ch07 表格尾均在 L420，ch14 表格尾均在 L32）；锚点注册表用
   `scripts/shift_anchors.py` 按文件平移。
4. **草稿注记**：field-guide 草稿头部补一行执行记录，标明哪两组能力哪天落进
   哪章，保持草稿与正文的落点状态一致。

## 4. 不做的事

- 不整页搬运用法矩阵；每处只搬草稿 §四 点名的那一格。
- 不新开 unit；20 单元、guides、插图数、章徽全部不动。
- `--external-thinking` 不进正文：帮助文本自述
  "providers have flagged this request shape as abuse"，与本书主题无扣，
  写进去只剩风险本身；草稿 §七-3 的条件（连风险提示一起写）满足与否都
  不改变「价值为零」这个判断。
- `--thinking` 八档、`--no-prewalk`、`--prewalk-into` 默认值等细节不进正文。
- Qoder／Cursor 的同类素材不跟进：无登记仓库，许可口径不放宽（草稿 §五-C）。
