# GUIDES-QA — 御舆分册 20 条 guides 逐条核对（Y-M2 Step 1）

判定依据：`docs/YUYU-OVERHAUL-SPEC.md` Y-M2 的 guides 规则表。

| 字段 | 规则 | 本次怎么核 |
|------|------|------------|
| `question` | 读者读完能回答；勿抄章标题 | 不含「读完「…」后」模板；不出现章标题原文 |
| `deliverable` | 可检查产出（口答要点 / 一张表 / 指出源码符号） | 都是「一张…图 / 一份…表 / 一个…文件」这类可指认的物件 |
| `boundary` | 本章不讲什么 | 20 条互不相同，各自点明留给哪一章 |
| `plain` / `analogy` | 中英都有；`plain_evidence` 落在散文 | 每条的 `plain` 中英齐全，`analogy` 中英齐全，证据是 `block id` 或 `unit.gloss-id` |
| `sources` | 指向 `sources.json` 已有 id | 55 个 id 里逐条比对，无悬空 |

## 实测结论

20 条 guides 在本轮审计前就已经是逐条手写的，不是模板批量填的：`question` 20 条互不相同、`deliverable` 20 条互不相同、`boundary` 20 条互不相同，三条反例（抄标题、deliverable = 章首第一段、boundary 一句话套全篇）一条都没踩。所以本轮**没有改任何 guide 的文字**，只做了两件收尾：

1. 证据去重：`ch01`、`ch05`、`apxc`、`apxd` 四条 guide 的 `plain_evidence` 里有重复条目（同一 block id 写了两次），去掉重复后分别从 8/8/8/6 变成 7/7/6/4，指向的语言集合不变。
2. 逐条比对 `sources` 与 `sources.json`，全部命中。

## 逐条核对（20/20）

| unit | question（读者读完能回答的那句） | deliverable | boundary | plain+evidence | sources |
|------|----------------------------------|-------------|----------|----------------|---------|
| `front` | 会聊天的模型为什么远远不够？Agent 为什么非得有 Harness 这一层？ | ✓ | ✓ | ✓ | ✓ |
| `ch01` | 从 Chatbot 到自主智能体，Claude Code 的骨架怎么搭？五大原则各落在哪？ | ✓ | ✓ | ✓ | ✓ |
| `ch02` | 对话主循环为何选异步生成器？一次 Turn 如何从请求流转到终止？ | ✓ | ✓ | ✓ | ✓ |
| `ch03` | 55 个工具如何靠同一份类型契约注册、发现、并发调度，而不改动引擎代码？ | ✓ | ✓ | ✓ | ✓ |
| `ch04` | 一次工具调用怎么穿过四道关？效率和安全各让了什么？ | ✓ | ✓ | ✓ | ✓ |
| `ch05` | 六层配置源按什么优先级合并成 Agent 的“基因”，安全边界又划在哪里？ | ✓ | ✓ | ✓ | ✓ |
| `ch06` | 哪些信息值得跨会话长期保存？后台提取又怎么在提示缓存的红线下干活？ | ✓ | ✓ | ✓ | ✓ |
| `ch07` | 上下文逼近窗口上限时，四级压缩按何顺序介入，各自付出多少成本？ | ✓ | ✓ | ✓ | ✓ |
| `ch08` | 22 个生命周期事件上，五种钩子类型如何观察、拦截并改写 Agent 的行为？ | ✓ | ✓ | ✓ | ✓ |
| `ch09` | 一次对话装不下的大任务，Claude Code 怎样拆给子智能体，又不让 token 与缓存失控？ | ✓ | ✓ | ✓ | ✓ |
| `ch10` | 当子任务彼此依赖、发现需要共享、工人还会失败时，谁来当那个项目经理？ | ✓ | ✓ | ✓ | ✓ |
| `ch11` | 怎样把一段反复粘贴的提示词，变成可分发、可覆盖、可控权限的能力包？ | ✓ | ✓ | ✓ | ✓ |
| `ch12` | 当工具、资源或 IDE 都在 Claude Code 之外，怎样安全接进来并管住权限？ | ✓ | ✓ | ✓ | ✓ |
| `ch13` | 模型还在吐字，工具为何已能开跑？延迟、并发与 token 成本之间怎么权衡？ | ✓ | ✓ | ✓ | ✓ |
| `ch14` | 如何让 Agent 先想清楚再动手，并把「想清楚」变成可读回、可审批、可定时的资产？ | ✓ | ✓ | ✓ | ✓ |
| `ch15` | 抛开 Claude Code 从零起步，一个最小可用的 Agent Harness 需要哪几根承重梁，按什么顺序搭？ | ✓ | ✓ | ✓ | ✓ |
| `apxa` | 要改一个不熟的功能：它归哪个模块、上下游依赖谁、数据实际怎么流过？ | ✓ | ✓ | ✓ | ✓ |
| `apxb` | 想确认某工具是否存在，或它是只读、破坏性、可并行，还是被标志关在门外？ | ✓ | ✓ | ✓ | ✓ |
| `apxc` | 某个能力在你的构建里不见了——是编译时没打进去，还是运行时门控没放行？ | ✓ | ✓ | ✓ | ✓ |
| `apxd` | 读到一半对某个名词失焦，或要确认本书中英译名是否统一、该词在哪章首次展开？ | ✓ | ✓ | ✓ | ✓ |

复核脚本（跑完输出 `problems 0`）：

```bash
python - <<'PY'
import sys, json, pathlib
sys.path.insert(0, "yuyu-book")
from yuyu_book import core
from yuyu_book.plain import prose_lines
m = json.loads(pathlib.Path("yuyu-book/manifest.json").read_text(encoding="utf-8"))
src = {k for k, v in json.loads(pathlib.Path("yuyu-book/sources.json")
       .read_text(encoding="utf-8")).items() if isinstance(v, dict)}
bad = []
for u, kind, _p in core.unit_stream(m):
    e = m["guides"][u["id"]]
    text = pathlib.Path(u["zh"]).read_text(encoding="utf-8")
    title = next((l[2:].strip() for l in text.split("\n") if l.startswith("# ")), "")
    first = next((l.strip() for _n, l in sorted(prose_lines(text).items())
                  if l.strip() and not l.startswith(("#", "!", "*", "|", "—", ">"))), "")
    q, d = e["question"]["zh"], e["deliverable"]["zh"]
    if "读完「" in q or (title and title.rstrip("？?")[:12] in q): bad.append((u["id"], "question"))
    if first and (d == first or (len(d) > 8 and d[:10] == first[:10])): bad.append((u["id"], "deliverable"))
    if set(e.get("plain", {})) != {"zh", "en"}: bad.append((u["id"], "plain"))
    if not e.get("plain_evidence"): bad.append((u["id"], "evidence"))
    if any(x not in src for x in e["sources"]): bad.append((u["id"], "sources"))
print("problems", len(bad), bad)
PY
```

实测输出：`problems 0`。
