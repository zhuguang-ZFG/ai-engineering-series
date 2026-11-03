#!/usr/bin/env python3
"""Regenerate docs/beginner-reader.html (+ .en.html) — the plain-language
on-ramp.

一本真正浅显易懂的入门分册：每站 = 一幅手绘插图 + 大书里现成的
「一句话讲明白」与「打个比方」，按四篇由浅入深排站（底色随篇目加深，
"由浅入深"因此被画出来），每站一枚链接跳回大书对应章。正文零改动——
所有句子都取自作者自己的通俗层（zh 从中文 dist 提取，en 从英文 dist）。

Run after `python yuyu-book/build.py [--lang en]` (reads the built HTML for
the plain-language layer; anchors link back into it).
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "yuyu-book" / "illustrations"
# Hand-inked plates on disk; the gallery and the readers quote this count.
PLATES = len(list(ART.glob("*.svg")))
# The reader is a derivative of the book, so it quotes the book's own edition —
# bumping the version must not need a hand edit here.
BOOK_VERSION = json.loads(
    (ROOT / "yuyu-book" / "manifest.json").read_text(encoding="utf-8")
)["version"]

YT_CHANNEL = "https://www.youtube.com/@anthropic-ai"
YT_SEARCH = "https://www.youtube.com/results?search_query="
B_SEARCH = "https://search.bilibili.com/all?keyword="

STRIP = re.compile(r"<[^>]+>")

# 由浅入深：四篇的底色一层比一层深，深浅即顺序
PARTS = [
    ("第一部分 · 基础篇", "起步", "#FBF6EC", ["ch01", "ch02", "ch03", "ch04"]),
    ("第二部分 · 核心系统篇", "进阶", "#F3EAD8", ["ch05", "ch06", "ch07", "ch08"]),
    ("第三部分 · 高级模式篇", "深入", "#EADFC7", ["ch09", "ch10", "ch11", "ch12"]),
    ("第四部分 · 工程实践篇", "实战", "#E0D4B8", ["ch13", "ch14", "ch15"]),
]
# The four appendices are stations in both editions; apxd closes the walk and
# the keeper's note follows it as an unnumbered hero.
APPENDIX_STATIONS = ("apxa", "apxb", "apxc", "apxd")
ORDER = ["front"] + [u for _, _, _, us in PARTS for u in us] + list(APPENDIX_STATIONS)
WIDTH = {u: 148 for u in ORDER}

CAPTIONS = {
    "front": "一张古地图：整本书就是一条路",
    "ch01": "罗盘：从「陪聊」到「干活」，换一种瞄准方式",
    "ch02": "心跳：一句话进、一句话出的对话循环",
    "ch03": "螺母：Agent 的双手——工具越多，本事越大",
    "ch04": "闸门：危险操作先过一道勾选的护栏",
    "ch05": "千层饼：配置像基因，一层层定性格",
    "ch06": "折角笔记本：Agent 的长期记忆记在这里",
    "ch07": "仪表盘：脑子里工作台还剩多少位置",
    "ch08": "挂钩：在人生节点上，给它装上小动作",
    "ch09": "分叉路：派几个小助手分头去办",
    "ch10": "指挥家：一个主编排，四方小队听调",
    "ch11": "技能卡：把说明书装进兜里，随取随用",
    "ch12": "外接线：一根线，用上全世界的工具",
    "ch13": "漏斗：回答像水一样，一边流一边看",
    "ch14": "小红旗：先画路线再出发，插旗为证",
    "ch15": "辘轳：亲手摇一架，你也造一个 Agent",
    "apxd": "小词典：生词太多？翻这一册",
    "apxa": "藏宝图：源码去哪儿翻，一图定位",
    "apxb": "工具清单：所有家当，逐项打勾",
    "apxc": "开关排：哪些功能开着，一眼看清",
    "keeper": "老驿卒：每章结尾替你守夜总结的人",
    "cover": "四马古车：书名「御舆」——驾驭一辆车，也驾驭一个 Agent",
}

TRANSITIONS = {
    "ch01": "先站上起点：模型动手后的门槛在工程侧——装修再好，也得先布线。",
    "ch02": "起点看清了，先听 Agent 的心跳——像收发室：登记、寄出、等回执。",
    "ch03": "回执有章法了，后厨也得有出单规矩——只读的成批跑，动火的排队来。",
    "ch04": "菜做出来了，能不能上桌得过审批——四道关，显式拒绝压过一切。",
    "ch05": "闸门立好，回头看性格从哪来——像公告栏，新通知一层层压旧通知。",
    "ch06": "性格定了，还得记住相处的每件事——像目录柜，只登记书在哪层架。",
    "ch07": "记的多了，白板写满就得擦——像库房腾货架，腾地方分四级。",
    "ch08": "白板管住了，还想在节点上插手——像小区门禁，保安不盖楼但能拦。",
    "ch09": "一个脑子忙不过来——像复印同一份会议底稿，分身各写各的结论。",
    "ch10": "分身多了要有人调度——像酒席总厨，自己从不颠勺。",
    "ch11": "人手齐了，手艺要可复制——像墙上的菜谱卡，一叠一叠分层。",
    "ch12": "店里的家当够用了，外面的世界像快递驿站——送一次就能取。",
    "ch13": "点单齐了，上菜要快——厨房喊一道先端一道。",
    "ch14": "大席面开炉之前，先像搬家列清单——老板签字才叫车。",
    "ch15": "各章手艺都齐了——照邻居厨房搭你自己的灶，六步开火。",
    "apxd": "路上的生词，都在这本小词典里。",
    "apxa": "附录是随书的工具——先用藏宝图把源码的路认一遍。",
    "apxb": "工具清单按类查——家当一件件对。",
    "apxc": "功能开关速查——哪些门开着，为什么。",
}

# 带走这一句：只复述当页已有的比方与白话，不新增任何技术断言
TAKEAWAYS = {
    "ch01": "记住：门槛在工程侧——一层运行时，加五条原则。",
    "ch02": "记住：心跳就是收发室——能暂停、能取消，续跑七条路。",
    "ch03": "记住：后厨出单——只读的成批跑，改东西的单独排队。",
    "ch04": "记住：四道关——验格式、查规则、自审、人点头，拒绝压过一切。",
    "ch05": "记住：公告栏六层覆盖——新压旧，安全项只增不减。",
    "ch06": "记住：目录柜只记位置——你是谁、你纠正过什么、为何这么定。",
    "ch07": "记住：白板写满就擦——先并箱、再打包、最后誊台账。",
    "ch08": "记住：门禁保安——能拦、能改输入、能补上下文。",
    "ch09": "记住：分身拿同一份底稿——并行干活不浪费 token。",
    "ch10": "记住：总厨只派活——备料单共享，谁倒下马上补位。",
    "ch11": "记住：菜谱卡同名听级别高的，用时报名字就抽得出。",
    "ch12": "记住：驿站——任何商家只送一次，取件先验码。",
    "ch13": "记住：先端先上、按序报号；一道洒了，同批先停。",
    "ch14": "记住：清单可读回、可审批、可定时——收进抽屉下次接着用。",
    "ch15": "记住：六步搭灶、反复回改，最后能自己开火。",
    "apxd": "记住：生词不查词典，路会越走越糊涂。",
    "apxa": "记住：概念图不是文件清单——顺着数据流走一遍才记得住。",
    "apxb": "记住：工具按分类查——并行、破坏性、标志，三问定位。",
    "apxc": "记住：能力不见，先查门控。",
}

VIDEOS = {
    "front": [("YouTube · Anthropic 官方频道", YT_CHANNEL),
              ("YouTube · Mastering Claude Code in 30 minutes（官方，已核验）",
               "https://www.youtube.com/watch?v=6eBSHbLKuN0"),
              ("官方课程 · Claude Code 101（已核验）", "https://academy.claude.com/courses/claude-code-101")],
    "ch01": [("B 站 · Claude Code 教程（社区，已核验）",
              "https://www.bilibili.com/video/BV1uS9UBQEuH"),
             ("YouTube · Mastering Claude Code in 30 minutes（官方，已核验）",
              "https://www.youtube.com/watch?v=6eBSHbLKuN0")],
    "ch02": [("B 站 · 搜「Claude Code 对话」", B_SEARCH + "Claude%20Code%20%E5%AF%B9%E8%AF%9D")],
    "ch03": [("B 站 · 搜「Claude Code 工具」", B_SEARCH + "Claude%20Code%20%E5%B7%A5%E5%85%B7")],
    "ch04": [("B 站 · 搜「Claude Code 权限」", B_SEARCH + "Claude%20Code%20%E6%9D%83%E9%99%90")],
    "ch05": [("B 站 · 搜「Claude Code 配置」", B_SEARCH + "Claude%20Code%20%E9%85%8D%E7%BD%AE"),
             ("官方课程 · Claude Code 101（已核验）", "https://academy.claude.com/courses/claude-code-101")],
    "ch06": [("B 站 · 搜「Claude Code 记忆」", B_SEARCH + "Claude%20Code%20%E8%AE%B0%E5%BF%86")],
    "ch07": [("B 站 · 搜「Claude Code 上下文」", B_SEARCH + "Claude%20Code%20%E4%B8%8A%E4%B8%8B%E6%96%87"),
             ("官方课程 · Claude Code 101（已核验）", "https://academy.claude.com/courses/claude-code-101")],
    "ch08": [("B 站 · 搜「Claude Code Hooks」", B_SEARCH + "Claude%20Code%20Hooks"),
             ("官方课程 · Claude Code 101（已核验）", "https://academy.claude.com/courses/claude-code-101")],
    "ch09": [("B 站 · 搜「Claude Code 子智能体」", B_SEARCH + "Claude%20Code%20%E5%AD%90%E6%99%BA%E8%83%BD%E4%BD%93"),
             ("官方课程 · Claude Code 101（已核验）", "https://academy.claude.com/courses/claude-code-101")],
    "ch10": [("YouTube · Anthropic 官方频道（多智能体）", YT_CHANNEL)],
    "ch11": [("B 站 · 搜「Claude Skills」", B_SEARCH + "Claude%20Skills")],
    "ch12": [("B 站 · MCP 教程（社区，已核验）", "https://www.bilibili.com/video/BV1qkHrzHEh4"),
             ("B 站 · 搜「MCP 教程」", B_SEARCH + "MCP%20%E6%95%99%E7%A8%8B"),
             ("YouTube · Anthropic 官方频道（MCP）", YT_CHANNEL),
             ("官方课程 · Claude Code 101（已核验）", "https://academy.claude.com/courses/claude-code-101")],
    "ch13": [("B 站 · 搜「Claude Code 流式」", B_SEARCH + "Claude%20Code%20%E6%B5%81%E5%BC%8F")],
    "ch14": [("B 站 · 搜「Claude Code Plan」", B_SEARCH + "Claude%20Code%20Plan")],
    "ch15": [("YouTube · Anthropic 官方频道（agent 深讲）", YT_CHANNEL)],
    "keeper": [("YouTube · Code w/ Claude 开发者大会全场合集（官方）",
                "https://www.youtube.com/playlist?list=PLf2m23nhTg1P5BsOHUOXyQz5RhfUSSVUi")],
}

# 每站的 YouTube 搜索词（官方内容以英文为主，搜索直达）
TOPICS_EN = {
    "front": "Claude Code overview",
    "ch01": "Claude Code paradigm shift",
    "ch02": "Claude Code conversation loop",
    "ch03": "Claude Code tools",
    "ch04": "Claude Code permissions",
    "ch05": "Claude Code settings",
    "ch06": "Claude Code memory",
    "ch07": "Claude Code context management",
    "ch08": "Claude Code hooks",
    "ch09": "Claude Code sub-agents",
    "ch10": "Claude Code multi-agent orchestration",
    "ch11": "Claude Code skills",
    "ch12": "Claude Code MCP",
    "ch13": "Claude Code streaming",
    "ch14": "Claude Code plan mode",
    "ch15": "build a Claude Code agent",
    "apxd": "Claude Code glossary",
}

# ---------------- English edition ----------------
PARTS_EN = [
    ("Part I · Foundations", "Start", "#FBF6EC", ["ch01", "ch02", "ch03", "ch04"]),
    ("Part II · Core Systems", "Core", "#F3EAD8", ["ch05", "ch06", "ch07", "ch08"]),
    ("Part III · Advanced Patterns", "Deep", "#EADFC7", ["ch09", "ch10", "ch11", "ch12"]),
    ("Part IV · Engineering Practice", "Practice", "#E0D4B8", ["ch13", "ch14", "ch15"]),
]
ORDER_EN = (["front"] + [u for _, _, _, us in PARTS_EN for u in us]
            + list(APPENDIX_STATIONS))

CAPTIONS_EN = {
    "front": "An old map: the whole book is one road",
    "ch01": "Compass: from chatbot to co-worker — a new way to aim",
    "ch02": "Heartbeat: the loop of one message in, one out",
    "ch03": "Nut: the agent's hands — more tools, more skill",
    "ch04": "Gate: risky actions pass a checked guardrail first",
    "ch05": "Layer cake: settings are genes, layer by layer",
    "ch06": "Folded notebook: where long-term memory lives",
    "ch07": "Gauge: how much workbench is left in mind",
    "ch08": "Hooks: small actions wired into life's milestones",
    "ch09": "Fork: send small helpers to work in parallel",
    "ch10": "Conductor: one orchestrator, four squads on call",
    "ch11": "Skill cards: the manual in your pocket",
    "ch12": "Jacks: one line to the world's tools",
    "ch13": "Funnel: answers flow like water, watchable as they pour",
    "ch14": "Flag: draw the route first, plant the flag as proof",
    "ch15": "Windlass: crank one yourself — build an agent of your own",
    "apxa": "Treasure map: where the source lives, located",
    "apxb": "Tool inventory: every belonging, ticked off",
    "apxc": "Switch bank: which flags are on, at a glance",
    "apxd": "Pocket dictionary: too many new words? Look here",
    "keeper": "The old courier: summarizing at every chapter's end",
    "part-p1": "The great compass: foundations, aim first",
    "part-p2": "The chest: core systems locked inside",
    "part-p3": "Mountain path: advanced patterns, the hill shortcut",
    "part-p4": "Gateway: engineering practice, the road out of town",
    "cover": "The four-horse chariot: Yù Yú — drive a chariot, drive an agent",
}

TRANSITIONS_EN = {
    "ch01": "Stand at the start: once a model can act, the hard part moves to engineering — wiring first, no matter how good the appliance.",
    "ch02": "Aim set, listen for the heartbeat — a mail room: log it, send it, wait for the receipt.",
    "ch03": "Receipts have rules; the kitchen needs ticket discipline — reads run in batches, writes queue up.",
    "ch04": "Before a dish leaves the kitchen it passes approval — four gates, and an explicit no beats every yes.",
    "ch05": "Gate up, look where the character comes from — an office bulletin board, new notices stacked on old.",
    "ch06": "Character set, it must remember what you share — a card catalog that only logs the shelf.",
    "ch07": "More to remember means a full whiteboard — clearing it is a four-step warehouse shuffle.",
    "ch08": "The board is managed; now touch the milestones — a lobby guard who never builds, only checks.",
    "ch09": "One brain is busy — photocopy the minutes, let copies write their own conclusions.",
    "ch10": "Copies need a head chef who never cooks — tickets out, one shared prep list.",
    "ch11": "Staffed, the craft must scale — recipe cards on the wall, stacked by layer.",
    "ch12": "In-house tools are set; the outside world arrives like a parcel station — delivered once, picked up with a code.",
    "ch13": "Orders in, serve fast — the kitchen calls a dish as soon as it's ready.",
    "ch14": "Before the banquet, plan like moving house — list, appraise, sign, then book the truck.",
    "ch15": "Every craft is in hand — build your own stove after the neighbor's kitchen, six steps.",
    "apxd": "New words on the road all live in this little dictionary.",
    "apxa": "The appendices are the book's own toolkit — walk the source map first.",
    "apxb": "The tool inventory, sorted by class — every belonging, ticked.",
    "apxc": "Flag quick reference — when a capability vanishes, check the gate first.",
}

# Take one sentence home: restates only the analogy already on the page
TAKEAWAYS_EN = {
    "ch01": "Remember: the gate is on the engineering side — one runtime, five principles.",
    "ch02": "Remember: the heartbeat is a mail room — pausable, cancellable, seven ways to resume.",
    "ch03": "Remember: kitchen tickets — reads batched, writes queued.",
    "ch04": "Remember: four gates — format, rules, self-review, human sign-off; an explicit no beats all.",
    "ch05": "Remember: six covering layers like a bulletin board — new over old, safety only grows.",
    "ch06": "Remember: the card catalog logs the shelf — who you are, what you corrected, why.",
    "ch07": "Remember: whiteboard full? Consolidate, pack, then transcribe to a ledger.",
    "ch08": "Remember: the lobby guard — block, redirect, or add a note to the log.",
    "ch09": "Remember: forks get the same minutes — parallel work, no token waste.",
    "ch10": "Remember: the head chef only assigns — shared prep list, instant backfill.",
    "ch11": "Remember: recipe cards — same name defers to the higher layer.",
    "ch12": "Remember: the parcel station — delivered once, pickup always verified.",
    "ch13": "Remember: serve as called, report in order; one spills, its batch pauses.",
    "ch14": "Remember: the list can be re-read, approved and scheduled — filed for next time.",
    "ch15": "Remember: six steps, repeated visits — and the stove finally cooks.",
    "apxd": "Remember: un-checked words make the road confusing.",

    "apxa": "Remember: the concept map isn't a file list — walk one data flow end to end.",
    "apxb": "Remember: tools sorted by class — parallel, destructive, flag-gated.",
    "apxc": "Remember: capability missing? Check the flag gate first.",}

VIDEOS_EN = {
    "front": [("YouTube · Anthropic official channel", YT_CHANNEL),
              ("YouTube · Mastering Claude Code in 30 minutes (official, verified)",
               "https://www.youtube.com/watch?v=6eBSHbLKuN0"),
              ("Official course · Claude Code 101 (verified)", "https://academy.claude.com/courses/claude-code-101")],
    "ch01": [("Bilibili · Claude Code tutorial (community, verified)",
              "https://www.bilibili.com/video/BV1uS9UBQEuH"),
             ("YouTube · Mastering Claude Code in 30 minutes (official, verified)",
              "https://www.youtube.com/watch?v=6eBSHbLKuN0")],
    "ch02": [("YouTube · search “Claude Code conversation loop”", YT_SEARCH + "Claude+Code+conversation+loop")],
    "ch03": [("YouTube · search “Claude Code tools”", YT_SEARCH + "Claude+Code+tools")],
    "ch04": [("YouTube · search “Claude Code permissions”", YT_SEARCH + "Claude+Code+permissions")],
    "ch05": [("YouTube · search “Claude Code settings”", YT_SEARCH + "Claude+Code+settings")],
    "ch06": [("YouTube · search “Claude Code memory”", YT_SEARCH + "Claude+Code+memory")],
    "ch07": [("YouTube · search “Claude Code context”", YT_SEARCH + "Claude+Code+context"),
             ("Official course · Claude Code 101 (verified)", "https://academy.claude.com/courses/claude-code-101")],
    "ch08": [("YouTube · search “Claude Code hooks”", YT_SEARCH + "Claude+Code+hooks")],
    "ch09": [("YouTube · search “Claude Code sub-agents”", YT_SEARCH + "Claude+Code+subagents"),
             ("Official course · Claude Code 101 (verified)", "https://academy.claude.com/courses/claude-code-101")],
    "ch10": [("YouTube · Anthropic official channel (multi-agent)", YT_CHANNEL)],
    "ch11": [("YouTube · search “Claude Skills”", YT_SEARCH + "Claude+Skills")],
    "ch12": [("Bilibili · MCP tutorial (community, verified)", "https://www.bilibili.com/video/BV1qkHrzHEh4"),
             ("YouTube · search “MCP tutorial”", YT_SEARCH + "Model+Context+Protocol+tutorial"),
             ("YouTube · Anthropic official channel (MCP)", YT_CHANNEL),
             ("Official course · Claude Code 101 (verified)", "https://academy.claude.com/courses/claude-code-101")],
    "ch13": [("YouTube · search “Claude Code streaming”", YT_SEARCH + "Claude+Code+streaming")],
    "ch14": [("YouTube · search “Claude Code plan mode”", YT_SEARCH + "Claude+Code+plan+mode")],
    "ch15": [("YouTube · Anthropic official channel (agent deep dive)", YT_CHANNEL)],
    "keeper": [("YouTube · Code w/ Claude full conference (official)",
                "https://www.youtube.com/playlist?list=PLf2m23nhTg1P5BsOHUOXyQz5RhfUSSVUi")],
}

STRIP = re.compile(r"<[^>]+>")


GLOSS = json.load(open(ROOT / "yuyu-book" / "glosses.json", encoding="utf-8"))
GLOSS.pop("schema_version", None)


def glossify(text: str, lang: str, limit: int = 3,
             book_link: str = "") -> str:
    """Wrap the first few glossary terms with a hover definition.

    作者在 glosses.json 里为每个术语写好了白话释义——分册直接借用，
    不新增任何解释。最长形态优先、互不重叠、每站限量，避免满屏虚线。
    """
    if not text:
        return text
    forms = []
    for gid, g in GLOSS.items():
        d = g["plain"].get(lang, "")
        if not d:
            continue
        for f in g["forms"].get(lang, []):
            f = f.strip()
            if len(f) >= (2 if lang == "zh" else 4):
                forms.append((f, d))
    forms.sort(key=lambda x: -len(x[0]))
    taken = []
    for f, d in forms:
        start = 0
        while True:
            i = text.find(f, start)
            if i < 0:
                break
            end = i + len(f)
            if all(end <= a or i >= b for a, b, _, _ in taken):
                taken.append((i, end, f, d))
                if len(taken) >= limit:
                    break
            start = i + len(f)
        if len(taken) >= limit:
            break
    for i, end, f, d in sorted(taken, reverse=True):
        safe = d.replace('"', "'")
        tag = (f'<a class="gl" href="{book_link}" title="{safe}">{f}</a>'
               if book_link else
               f'<span class="gl" title="{safe}">{f}</span>')
        text = text[:i] + tag + text[end:]
    return text


def extract_units(html: str, uids: list) -> dict:
    marks = {u: html.find(f'id="{u}"') for u in uids}
    missing = [u for u, pos in marks.items() if pos < 0]
    if missing:
        raise SystemExit(f"beginner reader: anchors missing in dist: {missing} "
                         "(run yuyu-book/build.py first)")
    order = sorted(marks.items(), key=lambda kv: kv[1])
    units = {}
    for i, (uid, pos) in enumerate(order):
        stop = order[i + 1][1] if i + 1 < len(order) else len(html)
        seg = html[pos:stop]
        title_m = re.search(r"<h1[^>]*>(.*?)</h1>", seg, re.S)
        title = STRIP.sub("", title_m.group(1)).strip() if title_m else uid
        plain_m = re.search(r'class="lb-plain">(.*?)</p>', seg, re.S)
        analogy_m = re.search(r'class="lb-a-tag">[^<]*</span>(.*?)</p>', seg, re.S)
        question_m = re.search(r'class="cc-tag">[^<]*</h4><p>(.*?)</p>', seg, re.S)
        deliver_m = re.search(r'compass-card deliverable"><h4 class="cc-tag">[^<]*</h4><p>(.*?)</p>', seg, re.S)
        boundary_m = re.search(r'compass-card boundary"><h4 class="cc-tag">[^<]*</h4><p>(.*?)</p>', seg, re.S)
        keeper_m = re.search(r'class="keeper-note">(.*?)</p>', seg, re.S)
        units[uid] = {
            "title": title,
            "plain": STRIP.sub("", plain_m.group(1)).strip() if plain_m else "",
            "analogy": STRIP.sub("", analogy_m.group(1)).strip() if analogy_m else "",
            "question": STRIP.sub("", question_m.group(1)).strip() if question_m else "",
            "deliver": STRIP.sub("", deliver_m.group(1)).strip() if deliver_m else "",
            "boundary": STRIP.sub("", boundary_m.group(1)).strip() if boundary_m else "",
            "note": STRIP.sub("", keeper_m.group(1)).strip() if keeper_m else "",
        }
    return units


def station(uid: str, num: str, unit: dict, svg: str, tier: str, part: str,
            bg: str, width: int, t) -> str:
    gloss_link = t["book"] + "#apxd"
    ana_txt = glossify(unit.get("analogy", ""), t["lang"], 2, gloss_link) if unit.get("analogy", "") else ""
    analogy = (f'<p class="st-ana">{t["analogy_label"]}{ana_txt}</p>'
               if unit.get("analogy", "") else "")
    plain_txt = glossify(unit.get("plain", ""), t["lang"], 3, gloss_link) if unit.get("plain", "") else ""
    plain = (f'<p class="st-plain">{plain_txt}</p>' if unit.get("plain", "") else "")
    trans = t["transitions"].get(uid, "")
    trans_html = f'<p class="st-trans">{trans}</p>' if trans else ""
    vids = "".join(f'<a class="st-vid" href="{url}" target="_blank"'
                   f' rel="noopener" title="{t["verified_note"]}">📺 {label}</a>'
                   for label, url in t["videos"].get(uid, []))
    vids_html = f'<p class="st-vids">{vids}</p>' if vids else ""
    take = t["takeaways"].get(uid, "")
    take_html = f'<p class="st-take">🔖 {take}</p>' if take else ""
    gain = unit.get("deliver", "")
    gain_html = (f'<p class="st-gain">{t["gain_label"]}{gain}</p>'
                 if gain else "")
    bound = unit.get("boundary", "")
    bound_html = (f'<p class="st-bound">{t["bound_label"]}{bound}</p>'
                  if bound else "")
    note = unit.get("note", "")
    note_html = (f'<details class="st-note"><summary>{t["note_label"]}'
                 f'</summary><p>{note}</p></details>') if note else ""
    question = unit.get("question", "")
    quiz_html = (f'<details class="st-quiz"><summary>{t["quiz_label"]}'
                 f'</summary><p>{question}</p></details>') if question else ""
    return f"""<article class="st" style="background:{bg}">
  <div class="st-art" style="width:{width}px" tabindex="0" role="button"
       aria-label="{t["replay_label"].format(name=unit.get("title", ""))}">{svg}</div>
  <div class="st-body">
    <p class="st-part">{t["station_word"].format(num=num, total=t["total"])} · {part} · <b class="st-tier">{tier}</b></p>
    <h2>{unit.get("title", "")}</h2>
    <p class="st-cap">{t["captions"].get(uid, "")}</p>
    {trans_html}{plain}{analogy}{take_html}{gain_html}{bound_html}{quiz_html}{note_html}{vids_html}
    <a class="st-go" href="{t["book"]}#{uid}">{t["go_deeper"]}</a>
  </div>
</article>"""


def build(lang: str) -> tuple[str, int]:
    t = LANGS[lang]
    dist = ROOT / "yuyu-book" / "dist" / t["dist"]
    html = dist.read_text(encoding="utf-8")
    svgs = {u: (ART / f"{u}.svg").read_text(encoding="utf-8").strip()
            for u in t["order"] + ["cover", "keeper",
                                   "part-p1", "part-p2", "part-p3", "part-p4"]
            if (ART / f"{u}.svg").exists()}
    part_meta = {}
    for pn in ("p1", "p2", "p3", "p4"):
        i = html.find(f'id="{pn}"')
        if i < 0:
            continue
        seg = html[i:i + 12000]

        def grab(cls, seg=seg):
            m = re.search(cls + r'">([^<]*)', seg)
            return m.group(1).strip() if m else ""
        part_meta[pn] = {"no": grab("pd-no"), "title": grab("pd-title"),
                         "motto": grab("pd-motto"),
                         "goal": re.sub(r"<[^>]+>", "", grab("pd-goal"))}
    units = extract_units(html, t["order"])

    stations = [f"""<article class="st st-hero" style="background:#FBF6EC">
  <div class="st-art" style="width:200px">{svgs.get("cover", "")}</div>
  <div class="st-body">
    <p class="st-part">{t["hero_tag"]}</p>
    <h2>{t["hero_h2"]}</h2>
    <p class="st-cap">{t["captions"]["cover"]}</p>
    <p class="st-plain">{t["hero_plain"]}</p>
    <a class="st-go" href="{t["book"]}#front">{t["hero_link"]}</a>
  </div>
</article>"""]

    num = 0
    for pi, (part, tier, bg, us) in enumerate(t["parts"]):
        pn = f"p{pi + 1}"
        pm = part_meta.get(pn)
        plate = svgs.get(f"part-{pn}", "")
        if pm and plate:
            goal_txt = glossify(pm["goal"], t["lang"], 2,
                                t["book"] + f"#{pn}")
            stations.append(f"""<article class="st st-divider" id="st-{pn}"
                style="background:{bg}">
  <div class="st-art" style="width:300px">{plate}</div>
  <div class="st-body">
    <p class="st-part">{pm["no"]} · <b class="st-tier">{tier}</b></p>
    <h2>{pm["title"]}</h2>
    <p class="st-motto">{pm["motto"]}</p>
    <p class="st-plain">{goal_txt}</p>
    <a class="st-go" href="{t["book"]}#{pn}">{t["part_link"].format(part=pm["no"])}</a>
  </div>
</article>""")
        for uid in us:
            num += 1
            topic = TOPICS_EN.get(uid, "")
            if topic and "YouTube · 搜" not in "".join(
                    l for l, _ in t["videos"].get(uid, [])):
                t["videos"].setdefault(uid, []).append(
                    ("YouTube · 搜「" + topic + "」",
                     YT_SEARCH + topic.replace(" ", "+")))
            stations.append(station(uid, num,
                                    units.get(uid, {"title": uid}),
                                    svgs.get(uid, ""), tier, part, bg,
                                    t["widths"].get(uid, 148), t))

    for uid in APPENDIX_STATIONS[:3]:
        num += 1
        stations.append(station(uid, num, units.get(uid, {"title": uid}),
                                svgs.get(uid, ""), t["appendix_tier"],
                                t["appendix_part"], "#DDD2B8", 148, t))
    num += 1
    vids_keep = "".join(
        f'<a class="st-vid" href="{url}" target="_blank" rel="noopener">📺 {label}</a>'
        for label, url in t["videos"].get("keeper", []))
    stations.append(f"""<article class="st" style="background:#FBF6EC">
  <div class="st-art" style="width:148px">{svgs.get("apxd", "")}</div>
  <div class="st-body">
    <p class="st-part">{t["station_word"].format(num=num, total=t["total"])} · {t["appendix_tag"]} · <b class="st-tier">{t["appendix_tier"]}</b></p>
    <h2>{t["appendix_h2"]}</h2>
    <p class="st-cap">{t["captions"]["apxd"]}</p>
    <p class="st-plain">{t["appendix_plain"]}</p>
    <a class="st-go" href="{t["book"]}#apxd">{t["appendix_link"]}</a>
  </div>
</article>
<article class="st st-hero" style="background:#FBF6EC">
  <div class="st-art" style="width:148px">{svgs.get("keeper", "")}</div>
  <div class="st-body">
    <p class="st-part">{t["keeper_tag"]}</p>
    <h2>{t["keeper_h2"]}</h2>
    <p class="st-cap">{t["captions"]["keeper"]}</p>
    <p class="st-plain">{t["keeper_plain"]}</p>
    <p class="st-vids">{vids_keep}</p>
    <a class="st-go" href="{t["book"]}">{t["keeper_link"]}</a>
  </div>
</article>""")

    if num != t["total"]:
        raise SystemExit(f"beginner reader: {num} numbered stations, but the "
                         f"edition declares {t['total']}")

    def fill(text: str) -> str:
        return (text.replace("@@STATIONS@@", str(t["total"]))
                .replace("@@PLATES@@", str(PLATES))
                .replace("@@BASELINE@@", BOOK_VERSION))

    page = fill(t["page_head"]) + "\n".join(stations) + fill(t["page_tail"])
    out = ROOT / "docs" / t["out"]
    out.write_text(page, encoding="utf-8")
    return out, len(stations)


PAGE_HEAD_ZH = """<!doctype html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Ccircle cx='16' cy='16' r='12' fill='none' stroke='%23B4472F' stroke-width='3'/%3E%3Ccircle cx='16' cy='16' r='4' fill='%23B4472F'/%3E%3C/svg%3E">
<title>御舆 · 入门分册 — 看图读懂 Agent Harness</title>
<meta property="og:title" content="御舆 · 入门分册 — 看图读懂 Agent Harness">
<meta property="og:description" content="人人可读的 @@STATIONS@@ 站看图入门：每站一幅手绘插图、一句白话、一个比方、一句记忆、一道自测、一段视频。">
<meta property="og:type" content="website">
<meta property="og:image" content="cover.png">
<style>
body{margin:0;font:16px/1.9 "Noto Serif SC","Source Han Serif SC","思源宋体","Songti SC","SimSun",Georgia,serif;background:#F5F0E6;color:#26221B}
header{padding:34px 30px 10px;max-width:820px;margin:0 auto}
h1{font-size:24px;margin:0 0 6px;font-weight:650}
.brush{width:190px;height:9px;color:#B4472F;display:block;margin:2px 0 8px}
.sub{color:#5C5448;font-size:13.5px}
.hint{color:#6E6353;font-size:12.5px;margin:10px 0 0}
main{max-width:820px;margin:0 auto;padding:6px 30px 50px}
.st{border:1.5px solid rgba(38,34,27,.3);border-radius:12px 7px 11px 8px/8px 11px 7px 12px;
    padding:26px 30px 24px;margin:0 0 26px;display:flex;gap:26px;align-items:center;
    box-shadow:2px 3px 0 rgba(38,34,27,.08)}
.st-hero{flex-direction:column;text-align:center;gap:10px;padding-top:34px}
.st-hero .st-body{text-align:center}
.st-art{flex:0 0 auto;line-height:0}
.st-art svg{width:100%;height:auto}
.st-body{flex:1}
.st-part{margin:0 0 6px;font-size:12px;letter-spacing:.14em;color:#5C5448}
.st-tier{color:#B4472F}
h2{font-size:21px;margin:0 0 8px}
.st-cap{margin:0 0 10px;font-size:13px;color:#9C3A26;letter-spacing:.02em}
.st-trans{margin:0 0 8px;font-size:13.5px;color:#5C5448}
.st-plain{margin:0 0 8px;font-size:15.5px}
.st-ana{margin:0 0 10px;font-size:14px;color:#5C5448}
.st-take{margin:0 0 10px;font-size:13.5px;color:#8A4A34}
.st-bound{margin:0 0 10px;font-size:12.5px;color:#8A7D68}
.st-note summary{cursor:pointer;font-size:12.5px;color:#675F4F}
.st-note p{margin:6px 0 0;font-size:13px;color:#5C5448;
  border-inline-start:2px solid rgba(180,71,47,.35);padding-inline-start:8px}
.st-navrow{display:flex;justify-content:space-between;gap:8px;margin-top:14px;
  border-top:1px dashed rgba(38,34,27,.25);padding-top:9px;font-size:12.5px}
.st-navrow a{color:#3A5A78;text-decoration:none}
.st-navrow a:hover{color:#B4472F}
.st-navrow .st-non{color:#8A7D68}
.prog{position:fixed;top:0;left:0;height:3px;background:#B4472F;z-index:100;width:0}
.st-gain{margin:0 0 10px;font-size:13.5px;color:#3E5A4C}
.gl{border-bottom:1px dashed #8A7D68;cursor:help;color:inherit;text-decoration:none}
.st-vids{margin:0 0 10px;font-size:12.5px}
.st-vids .st-vid{display:inline-block;margin-right:14px;color:#3A5A78;
  text-decoration:none;border-bottom:1px dashed rgba(76,112,147,.5)}
.st-vids .st-vid:hover{color:#B4472F;border-bottom-color:#B4472F}
.st-go{font-size:13.5px;color:#26221B;text-decoration:none;border-bottom:1.5px solid #B4472F;
       padding-bottom:1px;transition:color .16s ease}
.st-go:hover{color:#B4472F}
.st-art{cursor:pointer;transition:transform .25s cubic-bezier(.34,1.56,.64,1)}
.st-art:hover{transform:scale(1.03)}
.resume{position:fixed;left:18px;bottom:16px;z-index:98;display:flex;gap:10px;align-items:center;background:#FFFDF8;border:1.5px solid #B4472F;color:#26221B;font-size:12.5px;padding:9px 13px;border-radius:6px 3px 7px 4px/4px 7px 3px 6px;box-shadow:2px 3px 0 rgba(38,34,27,.18)}
.resume b{color:#B4472F}
.resume button{padding:5px 11px;font-size:12px}
.resume .ghost{border-color:#8A7D68;color:#675F4F;box-shadow:none}
.st-art:hover{transform:scale(1.03)}
.st-art:focus-visible{outline:2px solid #B4472F;outline-offset:4px}
.st,.st-body,.st-cap,.st-plain,.st-ana{animation:ink-rise .8s cubic-bezier(.22,.9,.3,1) both;
  animation-timeline:view();animation-range:cover 0% cover 46%}
.st-art svg path,.st-art svg circle{animation:ink-draw 1.1s ease-out both;
  animation-timeline:view();animation-range:cover 0% cover 55%}
@media screen and (prefers-reduced-motion: reduce){
  .st,.st-body,.st-cap,.st-plain,.st-ana,.st-art svg path,.st-art svg circle{animation:none}}
footer{max-width:820px;margin:0 auto;padding:0 30px 46px;color:#675F4F;font-size:12.5px}
footer a{color:inherit}
@keyframes ink-rise{from{opacity:0;transform:translateY(12px)}}
@media print{
  .resume,.replay-badge,.bar,.st-vids,.st-go{display:none!important}
  .st,.st-body,.st-cap,.st-plain,.st-ana,.st-trans,.st-take,.st-gain,
  .st-art svg path,.st-art svg circle{animation:none!important}
  .st{break-inside:avoid;box-shadow:none}
  body{background:#fff}
  .dark-strip,.dark-wrap{background:#fff}
}
@keyframes ink-draw{from{stroke-dashoffset:100}}
</style>
</head>
<body>
<header>
  <h1>御舆 · 入门分册</h1>
  <svg class="brush" viewBox="0 0 190 10" aria-hidden="true"><path d="M4 6q30-4.5 62-2.5t72-1q24 .2 46 1.8" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" opacity=".85"/><path d="M152 5.6q10-.6 20-.2" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" opacity=".45"/><circle cx="178" cy="5.8" r="1.5" fill="currentColor" stroke="none"/></svg>
  <p class="sub">看图读懂 Agent Harness —— 一站一个概念，一句一句说清楚</p>
  <p class="hint">每一站的句子都取自大书作者自己的通俗层；底色一层比一层深，就是"由浅入深"的顺序；句中带虚线的词，悬停出白话释义、点击跳术语表。某站看懂了，就推开「想深入」的门，去大书里读完整的原理。</p>
</header>
<main>
"""

PAGE_TAIL_ZH = """</main>
<footer>
本分册由大书的通俗层与 <a href="illustration-gallery.html">@@PLATES@@ 幅手绘插图</a> 组成；
画风体系来自 <a href="https://github.com/yang0/handraw-style">yang0/handraw-style</a>
（MIT with Attribution）。大书：<a href="yuyu-agent-harness-zh.html">御舆：解码 Agent Harness</a>。
<br>📺 页内视频为官方频道与社区资源，属<b>非规范来源</b>（仅核验存在性，
核验日期 2026-10-31）；一切技术事实以大书正文及其规范来源为准。本分册对应大书 v@@BASELINE@@ 构建基线。
</footer>
<div class="resume" id="resume" style="display:none">
  <span>上次读到第 <b id="resume-station"></b> 站</span>
  <button id="resume-go">继续读 →</button>
  <button id="resume-no" class="ghost">从头开始</button>
</div>
<script>
/* click or Enter re-inks the drawing — the reader takes part in it */
document.querySelectorAll(".st-art").forEach(art => {
  const fig = art.closest(".st");
  const replay = (cx, cy) => {
    const svg = art.querySelector("svg");
    if (!svg) return;
    svg.querySelectorAll("path, circle").forEach(el => {
      el.style.strokeDasharray = "100 100";
      const a = el.animate([{strokeDashoffset:"100"},{strokeDashoffset:"0"}],
        {duration:700, delay:Math.random()*250, fill:"both", easing:"ease-out"});
      a.onfinish = () => { el.style.strokeDasharray = ""; };
    });
    if (cx !== undefined) {
      for (let i = 0; i < 8; i++) {
        const sp = document.createElement("i");
        sp.style.cssText = "position:fixed;width:6px;height:6px;border-radius:60% 40% 55% 45%;pointer-events:none;z-index:99;background:" + (i % 3 ? "#26221B" : "#B4472F");
        sp.style.left = cx + "px"; sp.style.top = cy + "px";
        document.body.appendChild(sp);
        const ang = (i / 8) * Math.PI * 2, d = 16 + Math.random() * 22;
        const an = sp.animate([{transform:"translate(0,0) scale(1)",opacity:1},
          {transform:`translate(${Math.cos(ang)*d}px,${Math.sin(ang)*d+8}px) scale(.25)`,opacity:0}],
          {duration:460, easing:"cubic-bezier(.34,1.56,.64,1)", fill:"both"});
        an.onfinish = () => sp.remove();
      }
    }
  };
  art.addEventListener("click", e => replay(e.clientX, e.clientY));
  art.addEventListener("keydown", e => {
    if (e.key !== "Enter" && e.key !== " ") return;
    e.preventDefault();
    const r = art.getBoundingClientRect();
    replay(r.left + r.width / 2, r.top + r.height / 2);
  });
});
</script>
<script>
(function () {
  const KEY = "yy-reader-zh";
  let saved = 0;
  try { saved = +localStorage.getItem(KEY) || 0; } catch (e) {}
  let lastSave = 0;
  window.addEventListener("scroll", () => {
    const now = Date.now();
    if (now - lastSave < 800) return;
    lastSave = now;
    try { localStorage.setItem(KEY, String(window.scrollY)); } catch (e) {}
  }, {passive: true});
  if (saved > 600) {
    const banner = document.getElementById("resume");
    banner.style.display = "flex";
    const st = document.querySelectorAll(".st");
    let idx = 0;
    st.forEach((el, i) => {
      if (el.getBoundingClientRect().top + window.scrollY <= saved) idx = i;
    });
    document.getElementById("resume-station").textContent = idx + 1;
    document.getElementById("resume-go").onclick = () => {
      window.scrollTo({top: saved, behavior: "smooth"});
      banner.style.display = "none";
    };
    document.getElementById("resume-no").onclick = () => {
      try { localStorage.removeItem(KEY); } catch (e) {}
      banner.style.display = "none";
    };
  }
})();
</script>
<script>
/* 站间导航与阅读进度：教材的翻页体验 */
(function () {
  const en = document.documentElement.lang === "en";
  const L = en ? {prev: "← prev", next: "next →"} : {prev: "← 上一站", next: "下一站 →"};
  const arts = Array.from(document.querySelectorAll("main .st"));
  arts.forEach((a, i) => {
    if (!a.id) a.id = "st-" + i;
    const nav = document.createElement("p");
    nav.className = "st-navrow";
    nav.innerHTML =
      const prev = i > 0 ? arts[i - 1] : null;
      const next = i < arts.length - 1 ? arts[i + 1] : null;
      (prev ? `<a href="#${prev.id}">${L.prev}</a>` : '<span></span>')
      + `<span class="st-non">${i + 1} / ${arts.length}</span>`
      + (next ? `<a href="#${next.id}">${L.next} →</a>` : '<span></span>');
    a.appendChild(nav);
  });
  const bar = document.createElement("div");
  bar.className = "prog";
  document.body.appendChild(bar);
  const upd = () => {
    const h = document.documentElement;
    const max = h.scrollHeight - h.clientHeight;
    bar.style.width = (max > 0 ? Math.min(100, h.scrollTop / max * 100) : 0) + "%";
  };
  window.addEventListener("scroll", upd, {passive: true});
  window.addEventListener("resize", upd); upd();
})();
</script>
</body>
</html>
"""

PAGE_TAIL_EN = """</main>
<footer>
This reader is assembled from the full book's plain-language layer and the
<a href="illustration-gallery.html">@@PLATES@@ hand-inked figures</a>; the style system comes
from <a href="https://github.com/yang0/handraw-style">yang0/handraw-style</a>
(MIT with Attribution). Full book: <a href="yuyu-agent-harness-en.html">Yù Yú: Decoding Agent Harness</a>.
<br>📺 Videos are official-channel and community resources — <b>non-normative</b>
(existence verified 2026-10-31); every technical fact defers to the book and its
normative sources. This reader tracks book baseline v@@BASELINE@@.
</footer>
<div class="resume" id="resume" style="display:none">
  <span>You stopped at station <b id="resume-station"></b> 站</span>
  <button id="resume-go">Continue →</button>
  <button id="resume-no" class="ghost">Start over</button>
</div>
<script>
/* click or Enter re-inks the drawing — the reader takes part in it */
document.querySelectorAll(".st-art").forEach(art => {
  const fig = art.closest(".st");
  const replay = (cx, cy) => {
    const svg = art.querySelector("svg");
    if (!svg) return;
    svg.querySelectorAll("path, circle").forEach(el => {
      el.style.strokeDasharray = "100 100";
      const a = el.animate([{strokeDashoffset:"100"},{strokeDashoffset:"0"}],
        {duration:700, delay:Math.random()*250, fill:"both", easing:"ease-out"});
      a.onfinish = () => { el.style.strokeDasharray = ""; };
    });
    if (cx !== undefined) {
      for (let i = 0; i < 8; i++) {
        const sp = document.createElement("i");
        sp.style.cssText = "position:fixed;width:6px;height:6px;border-radius:60% 40% 55% 45%;pointer-events:none;z-index:99;background:" + (i % 3 ? "#26221B" : "#B4472F");
        sp.style.left = cx + "px"; sp.style.top = cy + "px";
        document.body.appendChild(sp);
        const ang = (i / 8) * Math.PI * 2, d = 16 + Math.random() * 22;
        const an = sp.animate([{transform:"translate(0,0) scale(1)",opacity:1},
          {transform:`translate(${Math.cos(ang)*d}px,${Math.sin(ang)*d+8}px) scale(.25)`,opacity:0}],
          {duration:460, easing:"cubic-bezier(.34,1.56,.64,1)", fill:"both"});
        an.onfinish = () => sp.remove();
      }
    }
  };
  art.addEventListener("click", e => replay(e.clientX, e.clientY));
  art.addEventListener("keydown", e => {
    if (e.key !== "Enter" && e.key !== " ") return;
    e.preventDefault();
    const r = art.getBoundingClientRect();
    replay(r.left + r.width / 2, r.top + r.height / 2);
  });
});
</script>
<script>
(function () {
  const KEY = "yy-reader-en";
  let saved = 0;
  try { saved = +localStorage.getItem(KEY) || 0; } catch (e) {}
  let lastSave = 0;
  window.addEventListener("scroll", () => {
    const now = Date.now();
    if (now - lastSave < 800) return;
    lastSave = now;
    try { localStorage.setItem(KEY, String(window.scrollY)); } catch (e) {}
  }, {passive: true});
  if (saved > 600) {
    const banner = document.getElementById("resume");
    banner.style.display = "flex";
    const st = document.querySelectorAll(".st");
    let idx = 0;
    st.forEach((el, i) => {
      if (el.getBoundingClientRect().top + window.scrollY <= saved) idx = i;
    });
    document.getElementById("resume-station").textContent = idx + 1;
    document.getElementById("resume-go").onclick = () => {
      window.scrollTo({top: saved, behavior: "smooth"});
      banner.style.display = "none";
    };
    document.getElementById("resume-no").onclick = () => {
      try { localStorage.removeItem(KEY); } catch (e) {}
      banner.style.display = "none";
    };
  }
})();
</script>
<script>
/* 站间导航与阅读进度：教材的翻页体验 */
(function () {
  const en = document.documentElement.lang === "en";
  const L = en ? {prev: "← prev", next: "next →"} : {prev: "← 上一站", next: "下一站 →"};
  const arts = Array.from(document.querySelectorAll("main .st"));
  arts.forEach((a, i) => {
    if (!a.id) a.id = "st-" + i;
    const nav = document.createElement("p");
    nav.className = "st-navrow";
    nav.innerHTML =
      const prev = i > 0 ? arts[i - 1] : null;
      const next = i < arts.length - 1 ? arts[i + 1] : null;
      (prev ? `<a href="#${prev.id}">${L.prev}</a>` : '<span></span>')
      + `<span class="st-non">${i + 1} / ${arts.length}</span>`
      + (next ? `<a href="#${next.id}">${L.next} →</a>` : '<span></span>');
    a.appendChild(nav);
  });
  const bar = document.createElement("div");
  bar.className = "prog";
  document.body.appendChild(bar);
  const upd = () => {
    const h = document.documentElement;
    const max = h.scrollHeight - h.clientHeight;
    bar.style.width = (max > 0 ? Math.min(100, h.scrollTop / max * 100) : 0) + "%";
  };
  window.addEventListener("scroll", upd, {passive: true});
  window.addEventListener("resize", upd); upd();
})();
</script>
</body>
</html>
"""

PAGE_HEAD_EN = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Ccircle cx='16' cy='16' r='12' fill='none' stroke='%23B4472F' stroke-width='3'/%3E%3Ccircle cx='16' cy='16' r='4' fill='%23B4472F'/%3E%3C/svg%3E">
<title>Yù Yú · Beginner Reader — Agent Harness in Pictures</title>
<meta property="og:title" content="Yù Yú · Beginner Reader — Agent Harness in Pictures">
<meta property="og:description" content="A picture walk through Agent Harness in @@STATIONS@@ stations — plain language, shallow to deep, one sketch at a time.">
<meta property="og:type" content="website">
<meta property="og:image" content="cover.png">
<style>
body{margin:0;font:16px/1.8 "Iowan Old Style",Palatino,Georgia,"Noto Serif SC",serif;background:#F5F0E6;color:#26221B}
header{padding:34px 30px 10px;max-width:820px;margin:0 auto}
h1{font-size:24px;margin:0 0 6px;font-weight:650}
.brush{width:190px;height:9px;color:#B4472F;display:block;margin:2px 0 8px}
.sub{color:#5C5448;font-size:13.5px}
.hint{color:#6E6353;font-size:12.5px;margin:10px 0 0}
main{max-width:820px;margin:0 auto;padding:6px 30px 50px}
.st{border:1.5px solid rgba(38,34,27,.3);border-radius:12px 7px 11px 8px/8px 11px 7px 12px;
    padding:26px 30px 24px;margin:0 0 26px;display:flex;gap:26px;align-items:center;
    box-shadow:2px 3px 0 rgba(38,34,27,.08)}
.st-hero{flex-direction:column;text-align:center;gap:10px;padding-top:34px}
.st-hero .st-body{text-align:center}
.st-art{flex:0 0 auto;line-height:0}
.st-art svg{width:100%;height:auto}
.st-body{flex:1}
.st-part{margin:0 0 6px;font-size:12px;letter-spacing:.14em;color:#5C5448}
.st-tier{color:#B4472F}
h2{font-size:21px;margin:0 0 8px}
.st-cap{margin:0 0 10px;font-size:13px;color:#9C3A26;letter-spacing:.02em}
.st-trans{margin:0 0 8px;font-size:13.5px;color:#5C5448}
.st-plain{margin:0 0 8px;font-size:15.5px}
.st-ana{margin:0 0 10px;font-size:14px;color:#5C5448}
.st-take{margin:0 0 10px;font-size:13.5px;color:#8A4A34}
.st-bound{margin:0 0 10px;font-size:12.5px;color:#8A7D68}
.st-note summary{cursor:pointer;font-size:12.5px;color:#675F4F}
.st-note p{margin:6px 0 0;font-size:13px;color:#5C5448;
  border-inline-start:2px solid rgba(180,71,47,.35);padding-inline-start:8px}
.st-gain{margin:0 0 10px;font-size:13.5px;color:#3E5A4C}
.gl{border-bottom:1px dashed #8A7D68;cursor:help;color:inherit;text-decoration:none}
.st-vids{margin:0 0 10px;font-size:12.5px}
.st-vids .st-vid{display:inline-block;margin-right:14px;color:#3A5A78;
  text-decoration:none;border-bottom:1px dashed rgba(76,112,147,.5)}
.st-vids .st-vid:hover{color:#B4472F;border-bottom-color:#B4472F}
.st-go{font-size:13.5px;color:#26221B;text-decoration:none;border-bottom:1.5px solid #B4472F;
       padding-bottom:1px;transition:color .16s ease}
.st-go:hover{color:#B4472F}
.st-art{cursor:pointer;transition:transform .25s cubic-bezier(.34,1.56,.64,1)}
.st-art:hover{transform:scale(1.03)}
.resume{position:fixed;left:18px;bottom:16px;z-index:98;display:flex;gap:10px;align-items:center;background:#FFFDF8;border:1.5px solid #B4472F;color:#26221B;font-size:12.5px;padding:9px 13px;border-radius:6px 3px 7px 4px/4px 7px 3px 6px;box-shadow:2px 3px 0 rgba(38,34,27,.18)}
.resume b{color:#B4472F}
.resume button{padding:5px 11px;font-size:12px}
.resume .ghost{border-color:#8A7D68;color:#675F4F;box-shadow:none}
.st-art:hover{transform:scale(1.03)}
.st-art:focus-visible{outline:2px solid #B4472F;outline-offset:4px}
.st,.st-body,.st-cap,.st-plain,.st-ana{animation:ink-rise .8s cubic-bezier(.22,.9,.3,1) both;
  animation-timeline:view();animation-range:cover 0% cover 46%}
.st-art svg path,.st-art svg circle{animation:ink-draw 1.1s ease-out both;
  animation-timeline:view();animation-range:cover 0% cover 55%}
@media screen and (prefers-reduced-motion: reduce){
  .st,.st-body,.st-cap,.st-plain,.st-ana,.st-art svg path,.st-art svg circle{animation:none}}
footer{max-width:820px;margin:0 auto;padding:0 30px 46px;color:#675F4F;font-size:12.5px}
footer a{color:inherit}
@keyframes ink-rise{from{opacity:0;transform:translateY(12px)}}
@media print{
  .resume,.replay-badge,.bar,.st-vids,.st-go{display:none!important}
  .st,.st-body,.st-cap,.st-plain,.st-ana,.st-trans,.st-take,.st-gain,
  .st-art svg path,.st-art svg circle{animation:none!important}
  .st{break-inside:avoid;box-shadow:none}
  body{background:#fff}
  .dark-strip,.dark-wrap{background:#fff}
}
@keyframes ink-draw{from{stroke-dashoffset:100}}
</style>
</head>
<body>
<header>
  <h1>Yù Yú · Beginner Reader</h1>
  <svg class="brush" viewBox="0 0 190 10" aria-hidden="true"><path d="M4 6q30-4.5 62-2.5t72-1q24 .2 46 1.8" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" opacity=".85"/><path d="M152 5.6q10-.6 20-.2" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" opacity=".45"/><circle cx="178" cy="5.8" r="1.5" fill="currentColor" stroke="none"/></svg>
  <p class="sub">Understanding Agent Harness in pictures — one concept per station, one sentence at a time</p>
  <p class="hint">Every sentence comes from the book's own plain-language layer; the paper darkens station by station — that is the shallow-to-deep order. Dotted terms show a plain-language definition on hover and link to the glossary. When a station clicks, push open the “go deeper” door and read the full principle in the book.</p>
</header>
<main>
"""


LANGS = {
    "zh": {
        "dist": "yuyu-agent-harness-zh.html",
        "book": "yuyu-agent-harness-zh.html",
        "out": "beginner-reader.html",
        "order": ORDER, "parts": PARTS,
        "total": sum(len(us) for _, _, _, us in PARTS) + len(APPENDIX_STATIONS),
        "widths": WIDTH,
        "lang": "zh",
        "captions": CAPTIONS, "transitions": TRANSITIONS, "videos": VIDEOS,
        "takeaways": TAKEAWAYS,
        "part_link": "想深入？翻开大书{part} →",
        "quiz_label": "自测一下 · 答案在大书这一章",
        "appendix_part": "附录",
        "gain_label": "读完你能：",
        "bound_label": "本站不展开：",
        "note_label": "驿卒按语 · 作者章末总结",
        "replay_label": "重播「{name}」的手绘过程",
        "verified_note": "链接存在性核验 2026-10-31（非规范来源）",
        "station_word": "第 {num} / {total} 站",
        "go_deeper": "想深入？翻开大书这一章 →",
        "hero_tag": "开卷 · 人人可读",
        "hero_h2": "这本书在讲一件什么事？",
        "hero_plain": ("大模型很聪明，但让它真正替你干活，还需要一整套“驾车”的装备"
                       "——这本书把这套装备拆开给你看。不用先懂编程，跟着图往下走就行。"),
        "hero_link": "想深入？翻开前言 →",
        "appendix_tag": "附录", "appendix_tier": "随身",
        "appendix_h2": "路上遇到生词？",
        "appendix_plain": "术语表、源码地图、工具清单、功能开关——都在附录里，随时折回去查。",
        "appendix_link": "想深入？翻开附录 D →",
        "keeper_tag": "到站 · 老驿卒的话",
        "keeper_h2": "路走完了，接下来呢？",
        "keeper_plain": ("这本分册只是地图，真正的风景在大书里——每站都有「想深入」的门，"
                         "推门进去，那里有完整的原理、代码与练习。"),
        "keeper_link": "回到大书 →",
        "analogy_label": "打个比方：",
        "page_head": PAGE_HEAD_ZH,
        "page_tail": PAGE_TAIL_ZH,
    },
    "en": {
        "dist": "yuyu-agent-harness-en.html",
        "book": "yuyu-agent-harness-en.html",
        "out": "beginner-reader.en.html",
        "order": ORDER_EN, "parts": PARTS_EN,
        "total": sum(len(us) for _, _, _, us in PARTS_EN) + len(APPENDIX_STATIONS),
        "widths": {u: 148 for u in ORDER_EN},
        "lang": "en",
        "captions": CAPTIONS_EN, "transitions": TRANSITIONS_EN,
        "videos": VIDEOS_EN,
        "takeaways": TAKEAWAYS_EN,
        "part_link": "Depth? Open {part} in the full book →",
        "quiz_label": "Test yourself · the answer is in the chapter",
        "appendix_part": "Appendix",
        "gain_label": "After this chapter you can: ",
        "bound_label": "Not covered here: ",
        "note_label": "The courier's note · author's chapter summary",
        "replay_label": "Replay the ink drawing of “{name}”",
        "verified_note": "link existence verified 2026-10-31 (non-normative)",
        "station_word": "Station {num} / {total}",
        "go_deeper": "Go deeper — open this chapter in the full book →",
        "hero_tag": "Opening · for everyone",
        "hero_h2": "What is this book about?",
        "hero_plain": ("LLMs are brilliant, but to make one truly work for you takes a "
                       "whole set of driving gear — this book takes that gear apart, "
                       "piece by piece. No programming required; just follow the pictures."),
        "hero_link": "Want depth? Open the preface →",
        "appendix_tag": "Appendix", "appendix_tier": "At hand",
        "appendix_h2": "New words on the road?",
        "appendix_plain": ("Glossary, source map, tool inventory, feature flags — all in "
                           "the appendices, ready to be looked up."),
        "appendix_link": "Depth? Open Appendix D →",
        "keeper_tag": "Arrived · a word from the old courier",
        "keeper_h2": "The road ends — what next?",
        "keeper_plain": ("This reader is just the map; the real scenery is in the full "
                         "book — every station has a door marked “go deeper”."),
        "keeper_link": "Back to the full book →",
        "analogy_label": "Think of it as: ",
        "page_head": PAGE_HEAD_EN,
        "page_tail": PAGE_TAIL_EN,
    },
}


def main():
    for lang in ("zh", "en"):
        out, n = build(lang)
        print(f"{out} ({n} stations)")


if __name__ == "__main__":
    main()
