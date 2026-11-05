# omp 章稿写作门禁（M1 执行契约）

本文件是 `OVERHAUL-SPEC.md` M1 的执行期修订，由用户 2026-11-03 拍板：
**取消每章字数地板，改为结构门禁；禁止为凑厚灌水**（与御舆 SPEC M1「非盲目加字」同一口径）。
SPEC 里「各章 ≥ 4500」「PDF 320–420 页」降级为**观测指标**，写进 `THICKEN-LOG.md`，不作为通过条件。

## 一、六要素（缺一即该章未过门禁）

判据脚本：`python omp/overhaul/audit_structure.py`（基线快照 `audit-baseline.tsv`，
当前快照 `audit-current.tsv`，由 `audit_structure.py --csv > audit-current.tsv` 重生成）。

CI 使用 `python omp/overhaul/audit_structure.py --check`：章数不是 33、六要素缺项，
或未标记验证状态时返回非零。`--csv --check` 同样执行门禁；不带 `--check` 保留报告模式。
2026-11-05 修正了旧脚本「只打印缺项但仍 exit 0」的问题，并移除开场检查的全局可变列表。
回归测试在 `tests/test_omp_overhaul.py`，覆盖空目录、缺要素与连续检查不同章节。

| # | 要素 | 合格判据 | 基线缺口 | 当前缺口（2026-11-04 复跑） |
|---|------|----------|----------|------------------------------|
| 1 | 开场具体场景或故障（≤2 段） | H1 之后、第一个 `##` 之前有散文段落，写的是**一个人撞上的一件事**，不是术语定义 | 9 章缺 | 0 |
| 2 | 原理（类比 + 一张图） | 章内有 `images/` 引用或 ` ```mermaid ` 围栏 | 0 章缺 | 0 |
| 3 | 最小可跟做实验 | 有 `sh`/`bash`/`ps1` 代码块且块内出现真实 `omp` 命令行；正文点明怎么算成功 | 26 章缺 | 0 |
| 4 | 常见翻车与对照表 | 小节标题含「翻车/对照/误区/陷阱/失败/排障」**且该小节内有 markdown 表格** | 33 章全缺 | 0 |
| 5 | 与御舆同构点 | 章内出现「御舆」短段，只写同构关系，**无 CC 专有数字** | 33 章全缺 | 0 |
| 6 | 章末版本核对清单 | 含「版本核对」 | 0 章缺 | 0 |

**六要素齐 33/33 章**。`mark_verified` 是 **31/33 Y**：ch21、ch22 两章正文里明写了「未验证」
（全局约束 10 要求的诚实标记，不是缺陷，脚本记作 `~`）；ch24 原先两类标记都没有，2026-11-04 已按
`omp -p "只回复两个字：在线" --no-session` 与 `omp read omp/ch06.md:1-3` 的实跑输出补上「本机已验」段
（证据 `omp/facts/live-18.16.0/ch24-ping-no-session.txt`），由 `n` 变 `Y`。上一版这一列
写的是「5 / 0 / 20 / 23 / 23 / 0 章缺」，那是 M1 加厚做到一半时的快照，之后一直没回写；
`audit-current.tsv` 同样停在 10/33。数字本身没有失效判据，只是没人复跑，现在两处都跟着脚本
重生成了一遍。

**判据脚本自己的 bug（已修）**：`audit_structure.py` 的 `TABLE_ROW` 原本没有
`re.MULTILINE`，而它是 `.search()` 在一个「以标题行开头」的小节串上——于是普通
`## 16.9 翻车对照` + 表格**永远**判不出，只有标题里自己带竖线才过。ch01–05 与
ch16–20 一度被改成 `## | 16.9 翻车对照 | 七种安静失败` 这种畸形标题去迁就脚本。
2026-11-03 加 `re.M` 修好判据，并把那 10 个标题归一回 `## 16.9 翻车对照：七种安静失败`。
**今后一律用归一后的写法**：小节标题 `## N.M 翻车对照：<短句>`，不要出现前导竖线。

## 一·补 本机事实与官方文档的冲突（写正文前必读）

以下都在 `omp/18.16.0`（Windows）实跑确认。凡正文与此冲突处，**按本机事实改写并带版本字样**；
`VERIFY.md` 已登记为 D 组差异。

| # | 官方文档 / 旧稿说法 | 本机实际 | 正文写法 |
|---|--------------------|----------|----------|
| C-01 | 「41 个 COMMANDS」 | 顶层 `--help` 的 COMMANDS 表有 **51** 条，51 个子命令的 `--help` 已全部采集 | 不要写死条数；要写就写「`omp --help` 的 COMMANDS 表为准」 |
| C-02 | `omp models find <无匹配>` 退出 1 | 退出 **0**，只是没有行 | 翻车表里按 exit 0 写 |
| C-03 | `omp config get modelRoles.default`（`docs/settings.md` 把 `modelRoles.smol` 一类点路径写成可寻址） | `Unknown setting`，exit **1**；只有整个 `modelRoles` 对象可取 | 明确「点路径能不能取以实跑为准」 |
| C-04 | `memory.backend` 默认 `off` | 本机返回 `mnemopi` | 写「默认值以本机 `omp config get memory.backend` 为准」 |
| C-05 | ch16 旧稿：根 URL 一定不解析 | `omp read memory://root` 在 `mnemopi` 后端下确实 exit **1** | 保留，但注明后端 |
| C-06 | 放对位置的项目级技能可读 | `.omp/skills/hello/SKILL.md` 已就位，shell 侧 `omp read skill://hello` 仍 `Unknown skill: hello` | 机制标**未验证**，不要解释成因 |
| C-07 | ch20「具体旗标为准」、ch16 的 CLI 形 `/memory` 行 | `omp --help` 里**没有** MCP 旗标，也**没有** `omp mcp` / `omp memory` 子命令 | 删掉不存在的命令形状 |
| C-08 | ch17 的 8 行角色表、文档点名的 `judge` 角色 | 本机 `modelRoles` 有 **13** 个键（含 `memory`、`chore_worker`、`scout_worker`、`designer`…），无 `judge` | 表格按本机键集重排，或写「以 `omp config get modelRoles` 为准」 |
| C-09 | ch18：审批模式即门禁 | `tools.approval: bash allow` 会**盖过** `tools.approvalMode: always-ask` | 写清两层关系 |
| C-10 | 「命令拼错会报错」 | shell 文案分两种：PowerShell「无法将"omp"项识别为…」，cmd.exe「不是内部或外部命令」——旧稿混为一谈 | 分开写 |
| C-11 | 未知输入必有错误码 | `omp notasubcommand`、`omp --model`（缺值）**不报错**，整句被当提示词进模型并 `Working...` 挂住；未知**旗标**才 exit 2 | 翻车表必列 |


## 二、证据纪律（最高优先级）

**只有三类话可以写进正文。**

1. **本机已验** —— 我在 `omp/18.16.0`（Windows）实跑过、输出存进 `omp/facts/live-18.16.0/` 的命令。
   写法：命令块下方一句「本机 `omp/18.16.0` 实跑，输出 `在线`（见 `VERIFY.md`）」
   或表格里标「本机已验」。
2. **文档所述** —— `omp/facts/doc-*.txt` / `slice-*.txt` / 官方 docs 明确写了的。
   写法：句末给文档名，如「以 `docs/settings.md` 的权威表为准」。
3. **未验证** —— 合理但未跑到、或本机版本与写作钉 v18.15.0 行为可能不同的。
   写法：沿用仓内既有说法「未验证」（`ch11.md:60`、`ch18.md:64` 是范例），
   并写清楚「用什么命令自查」。**严禁把未验证命令写成真理。**

已有可引用证据（2026-11-03 本机采集，无密钥）：

- `omp/facts/live-18.16.0/help-<子命令>.txt` —— **51 个子命令**的 `--help` 原文，
  与 `help-top.txt` 的 COMMANDS 表逐条对过（`anonymize` / `auth-gateway` / `grep`
  三条是 2026-11-03 补齐的；`help-section-counts.txt` 不是子命令）
- `omp/facts/live-18.16.0/help-top.txt` —— 顶层 `--help`（含全部旗标与 EXAMPLES）
- `omp/facts/live-18.16.0/print-mode-online.txt` —— `omp -p "只回复两个字：在线" --no-session` → `在线`，exit 0
- `omp/facts/live-18.16.0/fail/*.txt` —— 四条真实翻车：
  `--nopt` → `Error: unknown flag: --nopt`，exit 2；
  `-p "hi" --model 不存在` → `Model "..." not found` + 提示 `omp models find <pattern>`，exit 1；
  **`omp notasubcommand` 与 `omp --model`（缺值）不报错，而是把整句当提示词进模型，`Working...` 挂住**（本机 90s 超时截断）
- `omp/facts/live-18.16.0/models-list.txt` —— `omp models` 输出。**这份含用户私有网关名，只作形状参考，禁止把表贴进书稿或 VERIFY**
- `omp/facts/live-18.16.0/toks-self.txt`、`completions-bash.txt`、`_manifest.tsv`

要新命令：自己跑，把输出追加进 `live-18.16.0/` 并在 `_manifest.tsv` 记一行；跑不出来就标未验证。
`omp token` / `omp auth` / `omp usage` **禁止真跑**（会打印凭据或账号信息），只读它们的 `--help`。

## 三、文风

范例（当前最好的一章）：`omp/ch06.md` 开头 + `6.1`。要学的：

- 短句，第二人称，「你」；先给动作再给名词
- 每段一个意思；粗体只打在读者必须记住的词上，不装饰
- 具体到文件名、键名、界面位置；不说「一般来说」「值得注意的是」
- 承认不确定性（「通常能看到」「以文档为准」）比假装全知更像人写的

禁用清单（Humanizer-zh 会扫）：

- 空话起手：「值得注意的是」「需要指出的是」「总的来说」「在当今…时代」「不难发现」
- 三段式排比凑数（「高效、稳定、易用」这类三联形容词）
- 「首先/其次/最后」机械骨架 + 「通过…实现了…」名词化
- 每章都长一样的小节名（「概述 / 核心概念 / 实践建议 / 小结」套壳）
- 结尾复述本节内容

**不要新增 `<!--deepen-vN-->` 块**（仓内 **17** 处是上一轮灌水遗留：ch16–ch22 各 2、ch23 3，
`grep -rc 'deepen-v' omp/*.md` 可复现；无代码读取，保持原样不动。上一版这里写 23 处，对不上）。
若某章已有空洞「深挖/实操笔记」段，把它**替换**成真正的翻车对照表或实验，而不是在旁边再叠一段。

## 四、隔离

- 禁止把 Claude Code 专有数字（55 工具、89 Flag 等）或御舆的实现名（QueryEngine 等）贴进 omp 章
- 交叉引用只用 `CROSSREF-MAP.md` 的「参见御舆第 N 章《标题》」格式，1 短段，讲同构关系不讲对方命令
- 不动 `images/` 路径与题注语言（题注保持中文）；M3 才处理图
- 保留每章已有的 `版本核对清单` 行，可在其下补 3–5 条可勾项

## 五、交付与自检

改完必须自检：

```bash
python omp/overhaul/audit_structure.py          # 你负责的章 e1–e6 应全 Y
python omp/overhaul/count_chars.py              # 只记录，不卡线
```

**不要**跑 `make book-omp`（会写正式 dist，多代理并发会互相覆盖）——构建由主线在每个批次结束后统一跑。
**严禁** `git add` / `commit` / `push`。
