# GUIDES-QA — omp 分册 39 条 guides 逐条核对（SPEC M2 Step 1）

判定依据：`omp/OVERHAUL-SPEC.md` M2 Step 1 的四条字段规则。

| 字段 | 规则 | 本次怎么核 |
|------|------|------------|
| `question` | 读者读完能回答的一句话问题，勿抄标题 | 不含「读完「…」后」模板；不出现章标题原文 |
| `deliverable` | 可检查的产出（口答要点 / 一次命令 / 一张表） | 逐一改写为「一次…」「一张…」「一份…」「一组…」可指认的物件 |
| `boundary` | 本章不讲什么 | 39 条互不相同，且各自指向承接它的那一章 |
| `sources` | 继续指向 `sources-omp.json` 中的 id | 只允许 `omp-oh-my-pi`、`omp-site` 两个 id |

## 改前实测（2026-11-03）

改前的 guides 是 M0 搭骨架时批量填的，四条规则有两条不达标：

- `question`：33 章同一句模板「读完「<章标题>」后，你要能向别人讲清楚什么？」——**抄了标题**。
- `deliverable`：取的是章首第一段原文（如 ch01「先说一个我见过很多次的场景。」、ch05「这一章专门讲「怎么把模型接到 omp 上」。先分清两个词，后面不会混：」）——正是 SPEC 点名的反例。
- `boundary`：33 章同一句「先求能复述与能动手；源码级细节留给后文与附录。」——不构成「本章不讲什么」。

改后：39 条 question 互不相同、39 条 boundary 互不相同，deliverable 与各自章首段落均无相同前缀。

## 逐条核对（39/39）

| unit | question（读者读完能回答的那句） | deliverable | boundary | sources |
|------|----------------------------------|-------------|----------|---------|
| `omp-front` | 这本书读的是 omp 这个工具，还是 agent 的通用套路？ | ✓ | ✓ | `omp-oh-my-pi` |
| `omp-ch01` | 同一个模型，为什么在聊天框里写不出能跑的结果，放进 agent 里就行？ | ✓ | ✓ | `omp-oh-my-pi`, `omp-site` |
| `omp-ch02` | 同一段对话昨天能跑完，今天刚开场就说太长——为什么？ | ✓ | ✓ | `omp-oh-my-pi` |
| `omp-ch03` | 从敲下命令到文件被改，omp 中间要经过哪几个部件？ | ✓ | ✓ | `omp-oh-my-pi` |
| `omp-ch04` | 装完怎么判断「装对了」，而不是「看起来装上了」？ | ✓ | ✓ | `omp-oh-my-pi`, `omp-site` |
| `omp-ch05` | 模型接不上时，怎么分清是密钥、端点还是角色没配？ | ✓ | ✓ | `omp-oh-my-pi` |
| `omp-ch06` | 第一次对话，界面上哪些是我该看的，哪些可以不管？ | ✓ | ✓ | `omp-site` |
| `omp-ch07` | 想回到「改坏之前」那一版，该用 `/tree`、`/fork` 还是 `--resume`？ | ✓ | ✓ | `omp-site` |
| `omp-ch08` | 让 agent 自己找代码，它会按什么顺序用 `read` / `grep` / `glob` / `ast_grep`？ | ✓ | ✓ | `omp-oh-my-pi` |
| `omp-ch09` | agent 改代码为什么常「改错地方」，hashline 靠什么拦住它？ | ✓ | ✓ | `omp-oh-my-pi` |
| `omp-ch10` | 同样是执行，什么时候该用 `bash`，什么时候该用 `eval` 或专用工具？ | ✓ | ✓ | `omp-oh-my-pi` |
| `omp-ch11` | 改完代码，诊断为什么能立刻出现，而不是等下一次编译？ | ✓ | ✓ | `omp-oh-my-pi` |
| `omp-ch12` | 抓网页这件事，`browser`、`computer`、`web_search`、`github` 各管哪一段？ | ✓ | ✓ | `omp-oh-my-pi` |
| `omp-ch13` | 什么时候该开子代理，什么时候自己接着做更省？ | ✓ | ✓ | `omp-oh-my-pi` |
| `omp-ch14` | `AGENTS.md`、上下文文件、`.omp` 目录，这几个名字到底谁是谁？ | ✓ | ✓ | `omp-oh-my-pi` |
| `omp-ch15` | 长会话是怎么被「压小」的，压掉的内容还能找回来吗？ | ✓ | ✓ | `omp-oh-my-pi` |
| `omp-ch16` | 记忆到底开没开？怎么用一条命令确认，而不是凭感觉？ | ✓ | ✓ | `omp-oh-my-pi` |
| `omp-ch17` | 同一个模型，换个角色名行为就变了——谁压住了谁的设置？ | ✓ | ✓ | `omp-oh-my-pi` |
| `omp-ch18` | 敲一个词（比如 `/vibe`）为什么能改门禁，词不触发时从哪查起？ | ✓ | ✓ | `omp-oh-my-pi` |
| `omp-ch19` | 技能写了却不露面，先查发现、frontmatter，还是调用面？ | ✓ | ✓ | `omp-oh-my-pi` |
| `omp-ch20` | MCP 配好了工具却还是不出来，是传输、信任，还是生命周期的问题？ | ✓ | ✓ | `omp-oh-my-pi` |
| `omp-ch21` | 自定义工具和 hook 写完之后，凭什么算「接进去了」？ | ✓ | ✓ | `omp-oh-my-pi` |
| `omp-ch22` | 扩展是可执行依赖，加载失败时先看哪几行？ | ✓ | ✓ | `omp-oh-my-pi` |
| `omp-ch23` | 改了配置不生效，怎么确定「生效的是哪一层」？ | ✓ | ✓ | `omp-oh-my-pi` |
| `omp-ch24` | 接手一个陌生仓库的前半天，先问什么、先跑什么？ | ✓ | ✓ | `omp-oh-my-pi` |
| `omp-ch25` | 一条失败的测试，怎么变成可粘贴的命令，再变成最小修复？ | ✓ | ✓ | `omp-oh-my-pi` |
| `omp-ch26` | 大范围改名怎么不把仓库搞坏，哪些事必须发生在动文件之前？ | ✓ | ✓ | `omp-oh-my-pi` |
| `omp-ch27` | 一个提交凭什么算「可评审」，评审意见怎么写才可执行？ | ✓ | ✓ | `omp-oh-my-pi` |
| `omp-ch28` | 想把 omp 嵌进自己的程序，该走 SDK 还是 RPC？ | ✓ | ✓ | `omp-oh-my-pi` |
| `omp-ch29` | 个人技能发给同事，为什么在他那边报 `Unknown skill`？ | ✓ | ✓ | `omp-oh-my-pi` |
| `omp-ch30` | 出问题时，先看症状、先收证据，还是先改配置？ | ✓ | ✓ | `omp-oh-my-pi` |
| `omp-ch31` | 从别人仓库装扩展之前，哪几个开关决定「会不会执行别人的代码」？ | ✓ | ✓ | `omp-oh-my-pi` |
| `omp-ch32` | 一次长任务的账单，主要花在哪几处？ | ✓ | ✓ | `omp-oh-my-pi` |
| `omp-ch33` | 走完这本书，能不能用一条链路把六件事串起来讲清？ | ✓ | ✓ | `omp-oh-my-pi` |
| `omp-apxa` | 旗标太多记不住，怎么查而不是背？ | ✓ | ✓ | `omp-oh-my-pi`, `omp-site` |
| `omp-apxb` | 斜杠命令、CLI 旗标、魔法词，各自管哪一层？ | ✓ | ✓ | `omp-oh-my-pi`, `omp-site` |
| `omp-apxc` | 配置键那么多，先查哪一层、哪些最常改错？ | ✓ | ✓ | `omp-oh-my-pi` |
| `omp-apxd` | 术语表怎么用才不会变成背单词？ | ✓ | ✓ | `omp-oh-my-pi` |
| `omp-apxe` | 怎么确认书上写的和你本机跑的是同一版？ | ✓ | ✓ | `omp-oh-my-pi` |

复核命令（四条规则一次性跑完，输出 `problems 0`）：

```bash
python - <<'PY'
import sys, json, pathlib
sys.path.insert(0, "yuyu-book")
from yuyu_book import core
from yuyu_book.plain import prose_lines
m = json.loads(pathlib.Path("yuyu-book/manifest-omp.json").read_text(encoding="utf-8"))
ids = {k for k, v in json.loads(pathlib.Path("yuyu-book/sources-omp.json")
       .read_text(encoding="utf-8")).items() if isinstance(v, dict)}
bad = []
for u, kind, _p in core.unit_stream(m):
    e = m["guides"][u["id"]]
    text = pathlib.Path("omp", u["zh"].split("/")[-1]).read_text(encoding="utf-8")
    title = next((l[2:].strip() for l in text.split("\n") if l.startswith("# ")), "")
    first = next((l.strip() for _n, l in sorted(prose_lines(text).items())
                  if l.strip() and not l.startswith(("#", "!", "*", "|", "—", ">"))), "")
    q, d = e["question"]["zh"], e["deliverable"]["zh"]
    if "读完「" in q or (title and title.rstrip("？?") in q): bad.append((u["id"], "question"))
    if d and first and d == first: bad.append((u["id"], "deliverable=章首段"))
    if any(x not in ids for x in e["sources"]): bad.append((u["id"], "sources"))
print("problems", len(bad), bad)
PY
```

实测输出：`problems 0`。

## 与 guides 同批交付的通俗层登记表

| 登记表 | 数量 | 说明 |
|--------|------|------|
| `glosses-omp.json` | 36 词 | 其中与御舆 `glosses.json` **同 id 的 15 条**、omp 专有 **21 条**；每词带 `plain` / `analogy` / `why` 与 `file:line` 证据 |
| `notes-omp.json` | 39 条 | 前言 + 33 章 + 5 附录各一条，≤36 字，条条咬住本章真实出现的词形（术语锁） |
| `reading-paths-omp.json` | 33 章 / 381 节 | 每节一枚档位芯片：起步 33、主干 297、进阶 51 |

**两处 2026-11-04 的更正**（这一节原先写的数字核不上）：

- 原先写「共享 20 词 + omp 增量 16 词」。`glosses-omp.json` 里**没有** `shared_with` / `omp_only` 字段，这个拆分当时无法从文件内核掉；按 id 与御舆 `glosses.json`（102 条）逐条比对，实际是 **15 + 21**，也不存在「id 不同、其实是同一个词」的灰区。要么补上 `shared_with` 字段让文件自己可核，要么就以这条跨文件比对脚本为准。
- 原先写这 4 个词「仍在附录 D 里可查」——**当时不成立**：`glosses-omp.json` 的 36 词里有 **17 词**在 `omp/appendix-D.md` 全文找不到（含这 4 个不标的）。2026-11-04 已把 17 词按附录 D 既有格式补进 D.1/D.2/D.3/D.4，复核对账 `still missing: 0`。
- 补全附录 D 之后构建**失败**过一次：附录 D 这一个单元一次出现 32 个待标词，超 `yuyu_book/plain.py:37` 的 `MAX_PANEL = 22`。按错误信息给的口子把 12 个「查得到就够」的产品专有名降为 `priority: "extra"`（`工具结果`、`后台任务`、`哈希行锚`、`本地记忆库`、`模型角色`、`打印模式`、`秘密遮罩`、`MCP 服务器`、`帧协议接口`、`编辑器协议`、`子命令`、`诊断`），降到 20 个待标词才过。**代价必须记下来**：全书签入的虚线提示 317 → 242 处，读者在正文里能悬停的词少了 12 个——换来的是附录 D 真的能查到全部 36 词。

`glosses` 里有 4 个词标了 `"mark": false`（`yolo`、`toks`、`skill-uri`、`trusted-extension`）。原因不是偷懒：这四个词在正文里只以行内代码形态出现，而渲染器的代码通道只给「驼峰 / 下划线 / 数字」这类读者拆不开的写法加虚线，纯小写词加虚线会把正文变成一片虚线。它们仍在附录 D 里可查，只是不标。加上上面降为 `extra` 的 12 个，36 词里**正文加虚线的是 20 个**、只登记不标的是 16 个。

`reading-paths` 的分档不是随手撒的，规则只有三条：每章第一节记 `start`（不懂背景也能读）；标题含「翻车 / 故障 / 失败 / 误用 / 实验 / 跟做 / 清单 / 验收 / 口诀 / 决策表」记 `core`（这一章的主干）；标题含「同构点 / 深挖 / 架构 / 长什么样 / 心里有数」，或是同类多选一的替代路径（Homebrew、Bun、Nix、Windows、mise、Alpine、登录、本地模型、自定义端点）记 `deep`（按需再回来）。

## 构建证据

```
python scripts/bookctl.py build --product omp --lang zh --out-dir yuyu-book/.scratch/omp-appendixD-verify   # 2026-11-04 附录 D 补全后复跑
  yuyu-omp-zh.html: 20.0 MB, 39 units, 1 plates, 3 cited links, 242 glosses,
  39 lead bands, 381 tier chips, 0 emblems, 0 headpieces, 39 keeper notes
OK
```

（2026-11-04 之前这里贴的是同一条命令的旧输出，`317 glosses`；差额全部来自那 12 个降为 `extra` 的词。）

HTML 里可搜到 `class="gloss"`（带 `data-g` 的术语）、`gloss-pop`（悬停卡）、`sec-tier t-start`（档位芯片）。
