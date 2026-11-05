"""Draw six Omp teaching illustrations with Pillow and installed CJK fonts.

Preview: python scripts/draw_omp_illustrations.py
Publish: python scripts/draw_omp_illustrations.py --out-dir omp/images
"""
from __future__ import annotations

import argparse
import io
from functools import lru_cache
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
# the builder inlines every bitmap into the single-file HTML under this cap
# (PHOTO_BYTES in yuyu-book/yuyu_book/art.py), so an oversized JPG fails the build
MAX_JPEG_BYTES = 300_000
PAPER = "#FBF7EF"
WHITE = "#FFFEFA"
INK = "#29332E"
MUTED = "#657269"
ORANGE = "#D9562B"
PEACH = "#F8E4D8"
GREEN = "#557767"
SAGE = "#E3ECE2"
BLUE = "#52728D"
SKY = "#E6EDF2"
LINE = "#D6DACE"
FONT_CANDIDATES = (
    "C:/Windows/Fonts/msyh.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/System/Library/Fonts/PingFang.ttc",
)
BOLD_CANDIDATES = (
    "C:/Windows/Fonts/msyhbd.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
)


def resolve_font(override: Path | None, candidates: tuple[str, ...]) -> Path:
    if override is not None:
        if not override.is_file():
            raise ValueError(f"Font does not exist: {override}")
        return override
    for candidate in candidates:
        path = Path(candidate)
        if path.is_file():
            return path
    raise ValueError("No CJK font found. Pass --font and optionally --bold-font.")


class Drawing:
    def __init__(self, regular: Path, bold: Path, scale: int = 2):
        self.scale = scale
        self.image = Image.new("RGB", (1200 * scale, 800 * scale), PAPER)
        self.draw = ImageDraw.Draw(self.image)
        self.regular, self.bold = regular, bold

    def coords(self, points):
        return tuple(round(value * self.scale) for value in points)

    @lru_cache(maxsize=24)
    def font(self, size: int, bold: bool = False):
        return ImageFont.truetype(str(self.bold if bold else self.regular), size * self.scale)

    def text(self, position, value, size=22, color=INK, bold=False, anchor="lt", width=None):
        font = self.font(size, bold)
        if width is not None and self.draw.textlength(value, font=font) > width * self.scale:
            raise ValueError(f"Label exceeds its {width}px space: {value}")
        self.draw.text(self.coords(position), value, font=font, fill=color, anchor=anchor)

    def box(self, bounds, fill=WHITE, outline=LINE, radius=18, stroke=2):
        self.draw.rounded_rectangle(self.coords(bounds), radius=radius * self.scale,
                                    fill=fill, outline=outline, width=stroke * self.scale)

    def line(self, points, color=INK, stroke=3):
        self.draw.line([self.coords(point) for point in points], fill=color,
                       width=stroke * self.scale, joint="curve")

    def circle(self, center, radius, fill=WHITE, outline=INK, stroke=2):
        center_x, center_y = center
        self.draw.ellipse(self.coords((center_x - radius, center_y - radius,
                                       center_x + radius, center_y + radius)),
                          fill=fill, outline=outline, width=stroke * self.scale)

    def arrow(self, points, color=ORANGE, stroke=4):
        self.line(points, color, stroke)
        start, end = points[-2:]
        angle = math.atan2(end[1] - start[1], end[0] - start[0])
        wings = [(end[0] - 13 * math.cos(angle + offset),
                  end[1] - 13 * math.sin(angle + offset)) for offset in (-0.5, 0.5)]
        self.line([wings[0], end, wings[1]], color, stroke)

    def badge(self, center, value, color=ORANGE):
        self.circle(center, 20, color, color)
        self.text(center, str(value), 21, WHITE, True, "mm")

    def header(self, chapter, title, subtitle):
        self.line([(54, 47), (91, 47)], ORANGE, 4)
        self.text((105, 33), chapter, 19, MUTED)
        self.text((54, 84), title, 39, bold=True, width=1092)
        self.text((56, 145), subtitle, 22, MUTED, width=1088)

    def footer(self, lesson):
        self.line([(54, 727), (1146, 727)], LINE, 1)
        self.text((56, 748), lesson, 21, bold=True, width=1088)

    def note(self, bounds, title, detail, color=GREEN, fill=SAGE):
        self.box(bounds, fill, fill, radius=12)
        left, top, right, bottom = bounds
        self.text((left + 20, top + 15), title, 23, color, True, width=right - left - 40)
        if detail:
            self.text((left + 20, top + 50), detail, 20, MUTED, width=right - left - 40)

    def paper(self, bounds, title="", accent=BLUE, fill=WHITE, ruled=True):
        left, top, right, bottom = bounds
        self.box(bounds, fill, accent, radius=6)
        self.line([(left + 14, top + 14), (right - 30, top + 14)], accent, 4)
        if title:
            self.text((left + 14, top + 31), title, 20, bold=True, width=right - left - 28)
        if ruled:
            for line_y in range(int(top + 73), int(bottom - 12), 15):
                self.line([(left + 14, line_y), (right - 18, line_y)], LINE, 2)

    def face(self, center, radius=40, color=INK, fill=WHITE, expression="smile"):
        center_x, center_y = center
        self.circle(center, radius, fill, color, 3)
        for offset in (-0.3, 0.3):
            self.circle((center_x + radius * offset, center_y - radius * 0.1),
                        2.5, color, color, 1)
        mouth_y = center_y + radius * 0.3
        if expression == "surprised":
            self.circle((center_x, mouth_y), 5, fill, color)
        else:
            self.line([(center_x - 10, mouth_y - 2), (center_x, mouth_y + 3),
                       (center_x + 10, mouth_y - 2)], color, 2)

    def robot(self, center, color=GREEN):
        center_x, center_y = center
        self.box((center_x - 47, center_y - 32, center_x + 47, center_y + 37),
                 WHITE, color, radius=16, stroke=3)
        self.line([(center_x, center_y - 32), (center_x, center_y - 49)], color)
        self.circle((center_x, center_y - 52), 5, ORANGE, ORANGE)
        self.circle((center_x - 18, center_y - 3), 5, color, color)
        self.circle((center_x + 18, center_y - 3), 5, color, color)
        self.line([(center_x - 13, center_y + 17), (center_x, center_y + 22),
                   (center_x + 13, center_y + 17)], color, 3)

    def terminal(self, bounds, result="测试通过", success=True, command="> run tests"):
        left, top, right, bottom = bounds
        self.box(bounds, INK, INK, radius=10)
        for offset, color in ((18, PEACH), (35, SAGE), (52, SKY)):
            self.circle((left + offset, top + 17), 4, color, color)
        self.text((left + 18, top + 44), command, 20, WHITE, width=right - left - 36)
        self.text((left + 18, bottom - 41), result, 22,
                  "#BCD5BD" if success else "#FFBB9A", True, width=right - left - 36)


def agent_loop(picture: Drawing):
    picture.header("第 1 章 · 模型、工具与循环", "需求说一次，工作来回跑。",
                   "模型决定下一步，程序执行工具，再把结果交回模型。")
    picture.box((64, 237, 280, 495), WHITE, LINE)
    picture.badge((94, 261), 1)
    picture.face((171, 334), 39)
    picture.text((172, 407), "你：修好这个错误", 23, bold=True, anchor="mm")
    picture.text((172, 449), "目标 + 验收标准", 20, MUTED, anchor="mm")
    picture.arrow([(287, 356), (351, 356)])
    picture.box((367, 238, 714, 446), SAGE, GREEN)
    picture.badge((397, 263), 2, GREEN)
    picture.robot((541, 305))
    picture.text((541, 375), "模型想：接下来做什么？", 25, bold=True, anchor="mm")
    picture.text((541, 415), "读取 / 修改 / 再试一次", 20, MUTED, anchor="mm")
    picture.arrow([(721, 342), (791, 342)])
    picture.box((807, 238, 1136, 446), SKY, BLUE)
    picture.badge((837, 263), 3, BLUE)
    picture.terminal((858, 281, 1089, 387), "请求被执行", True, "> read / edit")
    picture.text((972, 418), "程序真正读文件、跑命令", 22, bold=True, anchor="mm")
    picture.arrow([(971, 454), (971, 490), (910, 490)])
    picture.box((681, 469, 894, 583), PEACH, ORANGE)
    picture.badge((709, 494), 4)
    picture.text((788, 521), "工具结果", 25, bold=True, anchor="mm")
    picture.text((788, 557), "内容 / diff / 报错", 18, MUTED, anchor="mm")
    picture.arrow([(674, 527), (541, 527), (541, 455)])
    picture.text((411, 553), "没完成：继续这一圈", 20, ORANGE, bold=True)
    picture.arrow([(694, 237), (694, 207), (1160, 207), (1160, 637), (1143, 637)], GREEN, 3)
    picture.text((958, 188), "由模型决定何时结束或问你", 18, GREEN, anchor="mm")
    picture.box((791, 601, 1136, 673), SAGE, SAGE, radius=12)
    picture.text((963, 637), "完成了 / 需要你确认 → 答复你", 21, GREEN, True, "mm")
    picture.footer("Agent = 模型 + 工具 + 循环。每一圈都要读回真实结果。")


def chat_vs_agent(picture: Drawing):
    picture.header("第 1 章 · 谁在真正动手", "同样一句需求，谁来读、改、跑？",
                   "聊天给出建议；Agent 把建议接到能执行、能反馈的工具上。")
    picture.box((60, 217, 578, 682), WHITE, LINE)
    picture.box((622, 217, 1140, 682), SAGE, SAGE)
    picture.text((319, 252), "聊天机器人", 28, bold=True, anchor="mm")
    picture.text((881, 252), "Agent", 28, GREEN, True, "mm")
    picture.robot((319, 337), BLUE)
    picture.robot((881, 337), GREEN)
    picture.box((125, 399, 515, 457), SKY, SKY, radius=12)
    picture.text((320, 428), "“你可以把这段代码改成……”", 23, BLUE, anchor="mm")
    picture.arrow([(319, 465), (319, 496)], BLUE)
    picture.face((176, 545), 29, expression="surprised")
    picture.text((238, 514), "你复制代码 → 你运行", 23, bold=True, width=300)
    picture.text((238, 554), "你贴报错 → 再问一轮", 23, bold=True, width=300)
    picture.line([(881, 382), (881, 431)], GREEN, 3)
    picture.line([(731, 431), (1031, 431)], GREEN, 3)
    for center, label in ((731, "读文件"), (881, "改代码"), (1031, "跑测试")):
        picture.box((center - 58, 466, center + 58, 526), WHITE, GREEN, radius=12)
        picture.text((center, 496), label, 22, GREEN, True, "mm")
        picture.arrow([(center, 431), (center, 459)], GREEN, 3)
    picture.arrow([(1031, 533), (1031, 567), (1104, 567), (1104, 337), (937, 337)], ORANGE, 3)
    picture.text((881, 602), "结果返回模型，继续判断", 23, GREEN, True, "mm")
    picture.text((319, 639), "执行与反馈，主要靠你", 23, MUTED, anchor="mm")
    picture.text((881, 649), "你仍负责目标、授权和验收", 21, MUTED, anchor="mm")
    picture.footer("看区别：谁执行工具，谁把结果带回下一轮？")


def context_desk(picture: Drawing):
    picture.header("第 2 章 · 上下文窗口", "模型眼前，只有这一张桌子。",
                   "能同时看到的材料有上限，聊天记录还在，不代表本轮都看得见。")
    picture.box((75, 259, 838, 539), SAGE, GREEN, radius=22, stroke=3)
    picture.text((105, 282), "当前上下文：模型这一轮的输入", 22, GREEN, True)
    for bounds, title, color in (
        ((110, 335, 270, 500), "系统规则", BLUE),
        ((289, 335, 449, 500), "你的问题", ORANGE),
        ((468, 335, 628, 500), "文件片段", BLUE),
        ((647, 335, 807, 500), "工具结果", GREEN),
    ):
        picture.paper(bounds, title, color)
    picture.line([(103, 545), (810, 545)], INK, 7)
    picture.line([(135, 548), (126, 625)], INK, 6)
    picture.line([(779, 548), (787, 625)], INK, 6)
    picture.robot((999, 310))
    picture.text((998, 375), "“本轮我能看到这些。”", 20, GREEN, anchor="mm")
    picture.arrow([(853, 414), (1099, 414), (1099, 310), (1056, 310)], GREEN, 3)
    picture.paper((936, 449, 1104, 575), "更早的对话", MUTED)
    picture.line([(916, 589), (1125, 589)], LINE, 3)
    picture.text((1020, 621), "可能已不在当前输入里", 19, MUTED, anchor="mm")
    picture.note((92, 644, 1108, 710), "桌面快满：定位后再读，把旧过程收成摘要。",
                 "", GREEN, SAGE)
    picture.footer("重要约定写进规则或记录；不要只凭“我们刚才聊过”。")


def fork_resume(picture: Drawing):
    picture.header("第 7 章 · 会话管理", "fork 开新本，resume 翻旧本。",
                   "先分清：你要另试一条路，还是接着已有记录继续。")
    picture.box((60, 219, 577, 679), WHITE, LINE)
    picture.box((623, 219, 1140, 679), SKY, SKY)
    picture.text((319, 255), "/fork", 30, ORANGE, True, "mm")
    picture.text((881, 255), "/resume", 30, BLUE, True, "mm")
    picture.paper((110, 319, 260, 477), "当前会话", BLUE)
    picture.arrow([(277, 392), (345, 392)])
    picture.paper((365, 334, 515, 492), "新会话", ORANGE, PEACH)
    picture.text((185, 521), "原本还在", 23, BLUE, True, "mm")
    picture.text((440, 536), "复制并切换过去", 22, ORANGE, True, "mm")
    for offset in (0, 12, 24):
        picture.box((672 + offset, 326 + offset, 804 + offset, 472 + offset),
                     WHITE, BLUE, radius=6)
    picture.text((753, 388), "已有记录", 21, BLUE, True, "mm")
    picture.arrow([(842, 411), (907, 411)], BLUE)
    picture.paper((925, 332, 1075, 491), "选中的会话", BLUE)
    picture.circle((1001, 531), 19, GREEN, GREEN)
    picture.line([(992, 531), (998, 537), (1011, 523)], WHITE, 3)
    picture.text((881, 581), "打开已有记录，接着聊", 23, BLUE, True, "mm")
    picture.text((319, 620), "纯内存会话不能直接 /fork", 21, MUTED, anchor="mm")
    picture.text((881, 624), "外来记录会先转换成 omp 会话", 19, MUTED, anchor="mm")
    picture.footer("补充：/tree、/branch 是同一会话文件内的历史导航。")


def compaction(picture: Drawing):
    picture.header("第 15 章 · 压缩与长任务", "旧过程收成摘要，最近原文留下。",
                   "compaction 改变的是接下来发给模型的上下文，不是逐字保留全部旧对话。")
    picture.text((244, 240), "压缩前：旧过程越堆越高", 25, bold=True, anchor="mm")
    for index, label in enumerate(("最早的讨论", "查找与试错", "旧工具输出", "中间结论")):
        top = 293 + index * 50
        picture.box((93 + index * 12, top, 390 + index * 12, top + 67),
                     WHITE, BLUE, radius=7)
        picture.text((116 + index * 12, top + 18), label, 22)
    picture.arrow([(442, 391), (538, 391)])
    picture.text((489, 341), "提炼", 22, ORANGE, True, "mm")
    picture.paper((563, 290, 799, 520), "摘要", ORANGE, PEACH, ruled=False)
    for offset, label in enumerate(("目标与约束", "已经确认的事实", "未解决的问题")):
        picture.box((582, 364 + offset * 43, 781, 399 + offset * 43), PEACH, PEACH, radius=1)
        picture.text((585, 367 + offset * 43), label, 21, bold=True)
    picture.text((830, 396), "+", 39, GREEN, True, "mm")
    picture.paper((875, 290, 1111, 520), "最近原文", GREEN, SAGE, ruled=False)
    picture.text((898, 374), "保留的条目", 23, GREEN, True)
    picture.text((898, 422), "后续的新消息", 23, GREEN, True)
    picture.text((837, 558), "模型下一轮接着看的材料", 23, GREEN, True, "mm")
    picture.note((91, 599, 1110, 695), "摘要会丢细节，关键约定要能回查。",
                 "需要旧信息时，回到文件或记录核对；不要把摘要当全文。", ORANGE, PEACH)
    picture.footer("直觉：把旧草稿收成便签，给手头正在做的事腾地方。")


def memory_loop(picture: Drawing):
    picture.header("第 16 章 · 记忆系统", "记忆像笔记本：记下、翻查、反省。",
                   "以 mnemopi 为例；工具是否可用，取决于你选择并启用的后端。")
    steps = ((228, "retain", "记下耐久线索", BLUE, SKY),
             (600, "recall", "按问题找回线索", GREEN, SAGE),
             (972, "reflect", "回顾与归纳", ORANGE, PEACH))
    for center, command, title, color, fill in steps:
        picture.box((center - 152, 234, center + 152, 565), fill, fill)
        picture.text((center, 271), command, 28, color, True, "mm")
        picture.text((center, 315), title, 23, bold=True, anchor="mm")
    picture.paper((151, 365, 303, 497), "有效经验", BLUE)
    picture.line([(273, 377), (305, 345)], ORANGE, 7)
    picture.circle((595, 417), 39, WHITE, GREEN, 4)
    picture.line([(623, 446), (655, 477)], GREEN, 8)
    picture.text((595, 417), "?", 34, GREEN, True, "mm")
    for offset, label in enumerate(("线索 A", "线索 B")):
        picture.box((869 + offset * 94, 362, 954 + offset * 94, 423), WHITE, ORANGE, radius=7)
        picture.text((911 + offset * 94, 392), label, 18, anchor="mm")
    picture.arrow([(913, 434), (913, 457), (963, 457)], ORANGE, 3)
    picture.text((983, 475), "归纳", 23, ORANGE, True, "mm")
    picture.line([(389, 405), (437, 405)], LINE, 2)
    picture.line([(760, 405), (808, 405)], LINE, 2)
    picture.text((600, 602), "示意：三种用途，不要求每次固定顺序执行。", 22, MUTED, anchor="mm")
    picture.note((90, 630, 1110, 708), "记忆给线索，当前仓库给证据。",
                 "记忆说用 yarn，仓库已有 package-lock.json？先核对现状。", GREEN, SAGE)
    picture.footer("别混淆：当前窗口里的摘要，不等于跨会话的长期记忆。")


def harness_horse(picture: Drawing):
    picture.header("第 1 章 · harness 决定成绩", "同一匹马，换副缰绳。",
                   "模型不变，只改「怎么告诉程序改哪一行」。")
    picture.box((58, 205, 452, 662), WHITE, LINE)
    picture.text((88, 228), "抄原文替换", 25, bold=True)
    picture.paper((90, 272, 420, 424), "模型要把原行一字不差抄回", BLUE, WHITE)
    picture.text((106, 322), "const total = 0;", 20)
    picture.text((106, 362), "const  count = 1;", 20, ORANGE)
    picture.text((106, 390), "↑ 多一个空格就找不到", 18, ORANGE)
    picture.arrow([(255, 432), (255, 468)], ORANGE)
    picture.text((255, 486), "失败 → 整轮重试", 23, ORANGE, True, "mm")
    picture.text((255, 556), "6.7%", 56, ORANGE, True, "mm")
    picture.text((255, 606), "改代码成功率", 19, MUTED, anchor="mm")
    # horse: body, neck, head, legs, tail
    picture.draw.ellipse(picture.coords((512, 372, 688, 486)), fill=WHITE,
                         outline=INK, width=4 * picture.scale)
    picture.box((648, 300, 700, 356), WHITE, INK, radius=10, stroke=3)
    picture.line([(652, 300), (656, 282)], INK, 3)
    picture.line([(678, 300), (674, 282)], INK, 3)
    for leg_x in (536, 578, 630, 666):
        picture.line([(leg_x, 480), (leg_x - 4, 548)], INK, 4)
    picture.line([(512, 396), (486, 372), (486, 344)], INK, 3)
    picture.text((600, 246), "模型", 22, MUTED, anchor="mm")
    # full harness vs light rein
    picture.line([(512, 430), (700, 430)], ORANGE, 5)
    picture.line([(500, 430), (466, 430)], ORANGE, 4)
    picture.line([(690, 430), (724, 430)], ORANGE, 4)
    picture.text((600, 596), "缰绳 = 编辑格式", 21, ORANGE, True, "mm")
    picture.box((724, 205, 1140, 662), SAGE, GREEN)
    picture.text((754, 228), "按行哈希说改哪一行", 25, GREEN, True)
    for index, (tag, code) in enumerate((("#a1b2", "const total = 0;"),
                                         ("#c3d4", "const count = 1;"))):
        top = 280 + index * 84
        picture.box((754, top, 1110, top + 64), WHITE, GREEN, radius=8)
        picture.box((764, top + 12, 850, top + 52), SAGE, SAGE, radius=6)
        picture.text((807, top + 32), tag, 18, GREEN, True, "mm")
        picture.text((864, top + 20), code, 20)
    picture.arrow([(932, 452), (932, 488)], GREEN)
    picture.text((932, 506), "只说：把 #a1b2 换成…", 22, GREEN, True, "mm")
    picture.text((932, 576), "68.3%", 56, GREEN, True, "mm")
    picture.text((932, 626), "改代码成功率", 19, MUTED, anchor="mm")
    picture.footer("壳和模型一样重要：同样的马，缰绳换了，成绩能差十倍。")


def tool_envelope(picture: Drawing):
    picture.header("第 2 章 · tool calling", "模型只写信封，程序负责跑腿。",
                   "请求与结果都走同一个循环；真正读文件、跑命令的是 omp。")
    picture.box((58, 214, 330, 620), WHITE, LINE)
    picture.robot((194, 322))
    picture.text((194, 404), "模型", 25, bold=True, anchor="mm")
    picture.text((194, 444), "输出的是请求，不是执行", 20, MUTED, anchor="mm", width=250)
    picture.paper((358, 260, 606, 444), "请求信封", ORANGE, PEACH, ruled=False)
    picture.text((378, 288), "工具：read", 21, bold=True)
    picture.text((378, 324), "path: src/app.ts", 20)
    picture.text((378, 360), "range: 1-40", 20)
    picture.text((378, 400), "格式写错 → 工具失败 → 重试", 17, ORANGE)
    picture.arrow([(615, 352), (682, 352)])
    picture.box((692, 214, 1140, 620), SAGE, GREEN)
    picture.text((722, 238), "omp 循环：拆信、执行、回信", 24, GREEN, True)
    for center_x, label, color in ((796, "read", BLUE), (920, "bash", GREEN),
                                    (1044, "grep", BLUE)):
        picture.box((center_x - 54, 288, center_x + 54, 348), WHITE, color, radius=10)
        picture.text((center_x, 318), label, 22, color, True, "mm")
    picture.text((916, 380), "工具白名单与参数校验都在这一层", 19, MUTED, anchor="mm")
    picture.paper((760, 424, 1000, 574), "结果信封", GREEN, WHITE, ruled=False)
    picture.text((780, 448), "内容 / diff / 退出码", 20, GREEN, True)
    picture.text((780, 486), "成功就带回，失败就带报错", 18, MUTED)
    picture.arrow([(1009, 500), (1050, 500), (1050, 404), (344, 404), (344, 352)],
                  ORANGE, 3)
    picture.text((1040, 380), "塞回模型", 18, ORANGE)
    picture.text((194, 560), "模型读回信，决定下一封", 20, MUTED, anchor="mm", width=250)
    picture.footer("模型负责「写什么」；omp 负责「怎么送、送到哪、带回什么」。")


def thinking_dial(picture: Drawing):
    picture.header("第 2 章 · 推理强度", "像音量旋钮，能拧，但不是人人有。",
                   "thinking 强度按档位调；档位由模型与提供商决定。")
    center = (610, 410)
    picture.circle(center, 196, WHITE, INK, 4)
    for index, (angle, label) in enumerate(((-135, "关"), (-45, "低"),
                                            (45, "中"), (135, "高"))):
        radians = math.radians(angle)
        inner = (center[0] + 158 * math.cos(radians), center[1] + 158 * math.sin(radians))
        outer = (center[0] + 182 * math.cos(radians), center[1] + 182 * math.sin(radians))
        picture.line([inner, outer], MUTED, 5)
        picture.text((center[0] + 122 * math.cos(radians),
                      center[1] + 122 * math.sin(radians)), label, 26, INK, True, "mm")
    knob = math.radians(-125)
    picture.line([center, (center[0] + 132 * math.cos(knob),
                           center[1] + 132 * math.sin(knob))], ORANGE, 9)
    picture.circle(center, 26, ORANGE, ORANGE)
    picture.text((center[0], 470), "推理档位", 23, MUTED, anchor="mm")
    picture.note((92, 588, 1108, 682), "不是所有模型都有这颗旋钮。",
                 "有的只暴露部分档位；拧到「高」也受提供商与账号能力限制。", BLUE, SKY)
    picture.footer("强度是请求，不是保证：看模型卡与 /model 的实际选项。")


def four_shells(picture: Drawing):
    picture.header("第 3 章 · 四种入口", "外壳能换，引擎不换。",
                   "工具、会话、模型路由都在同一套运行时里。")
    shells = (("交互 TUI", "直接运行 omp", ORANGE, PEACH),
              ("单次问答", "omp -p / --print", BLUE, SKY),
              ("Node SDK", "import 进你的程序", GREEN, SAGE),
              ("RPC / ACP", "omp --mode rpc / acp", MUTED, WHITE))
    for index, (title, command, color, fill) in enumerate(shells):
        left = 62 + index * 270
        picture.box((left, 218, left + 250, 376), fill, color)
        picture.text((left + 125, 250), title, 25, color, True, "mm")
        picture.text((left + 125, 302), command, 18, MUTED, anchor="mm", width=230)
        picture.arrow([(left + 125, 386), (left + 125, 440)], color, 3)
    picture.box((300, 452, 900, 600), SAGE, GREEN, radius=18, stroke=3)
    picture.text((600, 492), "同一个引擎", 30, GREEN, True, "mm")
    picture.text((600, 540), "工具 · 会话 · 上下文 · 模型路由", 22, GREEN, anchor="mm")
    picture.text((600, 576), "四条入口只在启动方式和协议上不同", 19, MUTED, anchor="mm")
    picture.note((92, 622, 1108, 690), "选入口看场景：",
                 "人对人用 TUI；脚本用 -p；嵌进程序用 SDK；让编辑器遥控走 RPC/ACP。", BLUE, SKY)
    picture.footer("别为入口记四套心智模型——差异在外壳，能力在引擎。")


def package_map(picture: Drawing):
    picture.header("第 3 章 · 包结构", "依赖自上而下，一层压一层。",
                   "示意分层；具体模块名以你装的版本为准。")
    layers = (("CLI / SDK 入口", "omp 命令、import 包", ORANGE, PEACH),
              ("终端 UI", "TUI、卡片、预览", BLUE, SKY),
              ("agent 运行时", "循环、工具、会话、上下文", GREEN, SAGE),
              ("模型客户端 / 目录", "provider、模型选择", BLUE, SKY),
              ("Rust 原生", "natives：搜索、shell、AST", MUTED, WHITE))
    for index, (title, detail, color, fill) in enumerate(layers):
        top = 202 + index * 92
        picture.box((300, top, 900, top + 74), fill, color, radius=12)
        picture.text((330, top + 14), title, 24, color, True)
        picture.text((330, top + 44), detail, 18, MUTED)
        if index:
            picture.line([(316, top - 18), (600, top - 18)], LINE, 2)
            picture.arrow([(552, top - 18), (552, top - 6)], LINE, 3)
    picture.text((944, 336), "调用方向：", 21, MUTED, True)
    picture.text((944, 366), "上层调下层", 21, MUTED)
    picture.text((944, 420), "底层不反向依赖界面", 21, MUTED)
    picture.footer("读报错栈时先认层：越靠下的问题，越少是「提示词」造成的。")


def natives_inplace(picture: Drawing):
    picture.header("第 3 章 · natives 在进程内", "少一次出门，快一截。",
                   "同样的搜索与 shell 能力，一种每次 fork，一种住在进程里。")
    picture.box((62, 210, 556, 668), WHITE, LINE)
    picture.text((309, 236), "每次 fork 外部程序", 24, bold=True, anchor="mm")
    picture.box((110, 292, 508, 396), WHITE, ORANGE)
    picture.text((309, 320), "omp 进程", 21, ORANGE, True, "mm")
    for index, tool in enumerate(("rg", "bash", "find")):
        left = 140 + index * 130
        picture.box((left, 470, left + 104, 540), WHITE, ORANGE, radius=10)
        picture.text((left + 52, 505), tool, 21, ORANGE, True, "mm")
        picture.arrow([(309, 404), (309, 440), (left + 52, 440), (left + 52, 462)],
                      ORANGE, 3)
        picture.arrow([(left + 52, 548), (left + 52, 596), (309, 596)], MUTED, 2)
    picture.text((309, 624), "启动、退出、拷贝结果", 20, MUTED, anchor="mm")
    picture.text((309, 656), "进程边界 = 额外开销", 19, ORANGE, anchor="mm")
    picture.box((584, 210, 1138, 668), SAGE, GREEN)
    picture.text((861, 236), "工具住在进程内", 24, GREEN, True, "mm")
    picture.box((648, 292, 1074, 600), WHITE, GREEN, radius=14)
    picture.text((861, 322), "omp 进程", 21, GREEN, True, "mm")
    for index, tool in enumerate(("natives 搜索", "内嵌 shell", "AST 管线")):
        top = 368 + index * 74
        picture.box((700, top, 1022, top + 56), SAGE, SAGE, radius=8)
        picture.text((861, top + 28), tool, 21, GREEN, True, "mm")
    picture.text((861, 630), "调用即函数调用", 20, MUTED, anchor="mm")
    picture.text((861, 660), "没有进程启动成本", 19, GREEN, anchor="mm")
    picture.footer("能用进程内能力就别 fork：快，也少一层环境差异。")


def install_tree(picture: Drawing):
    picture.header("第 4 章 · 安装路线", "五条路，先挑平台。",
                   "curl 脚本、包管理器或预编译二进制；按你的系统选一条。")
    picture.box((470, 200, 730, 268), SAGE, GREEN)
    picture.text((600, 234), "安装入口", 24, GREEN, True, "mm")
    routes = (("curl | sh", "macOS / Linux", ORANGE, PEACH),
              ("Homebrew", "macOS", BLUE, SKY),
              ("Bun ≥ 1.4.4", "三平台", GREEN, SAGE),
              ("Nix", "NixOS / 声明式", BLUE, SKY),
              ("PowerShell", "Windows", ORANGE, PEACH))
    for index, (title, platform, color, fill) in enumerate(routes):
        left = 58 + index * 220
        picture.arrow([(600, 276), (600, 300), (left + 100, 300), (left + 100, 330)],
                      color, 3)
        picture.box((left, 338, left + 200, 430), fill, color)
        picture.text((left + 100, 368), title, 23, color, True, "mm")
        picture.text((left + 100, 402), platform, 18, MUTED, anchor="mm")
    picture.note((92, 470, 1108, 590), "装完都要验证：",
                 "omp --version 能回版本，才算真的装上；脚本路线可用 --ref 钉 tag。", BLUE, SKY)
    picture.note((92, 610, 1108, 692), "别混用包管理器：",
                 "同一台机器只用一条路线，否则 PATH 里会出现两个版本。", ORANGE, PEACH)
    picture.footer("先选路线再敲命令；回退路线写进笔记，下次不用重新查。")


def bun_or_binary(picture: Drawing):
    picture.header("第 4 章 · 安装脚本判断环境", "有 bun 走包，没有走二进制。",
                   "两条路都从同一个脚本入口分叉，产物不同。")
    picture.box((380, 198, 820, 276), SAGE, GREEN)
    picture.text((600, 222), "安装脚本读环境", 24, GREEN, True, "mm")
    picture.text((600, 254), "显式 --binary 也走右边", 18, MUTED, anchor="mm", width=400)
    picture.arrow([(500, 286), (330, 340)], GREEN, 3)
    picture.arrow([(700, 286), (870, 340)], ORANGE, 3)
    picture.box((70, 350, 540, 596), SAGE, GREEN)
    picture.text((305, 380), "已有可用 bun", 24, GREEN, True, "mm")
    picture.text((305, 420), "包安装：", 20)
    picture.box((110, 452, 500, 512), WHITE, GREEN, radius=8)
    picture.text((305, 482), "@oh-my-pi/pi-coding-agent", 19, GREEN, True, "mm")
    picture.text((305, 536), "升级走包管理器，不追 --ref", 18, MUTED, anchor="mm")
    picture.box((660, 350, 1130, 596), PEACH, ORANGE)
    picture.text((895, 380), "无 bun 或 --binary", 24, ORANGE, True, "mm")
    picture.text((895, 420), "预编译二进制：", 20)
    picture.box((700, 452, 1090, 512), WHITE, ORANGE, radius=8)
    picture.text((895, 482), "build.stencil.so · 钉 --ref", 19, ORANGE, True, "mm")
    picture.text((895, 536), "安装前校验 SHA-256", 18, MUTED, anchor="mm")
    picture.note((92, 620, 1108, 692), "两条路都得能回滚。",
                 "钉版本时记下 tag 与产物来源；不要用最新版覆盖正在用的版本。", BLUE, SKY)
    picture.footer("让脚本替你判断可以；判断结果要能复核——看它走的哪一支。")


def provider_board(picture: Drawing):
    picture.header("第 5 章 · 供应商与模型", "插座通电，才谈得上插头。",
                   "先有供应商凭证或本地服务，再用 /model 选具体模型。")
    picture.box((80, 210, 1120, 540), "#EFE7DA", INK, radius=18, stroke=3)
    picture.text((600, 232), "凭证 / 本地服务", 22, MUTED, True, "mm")
    names = ("anthropic", "openai", "google", "ollama", "自定义")
    for index, name in enumerate(names):
        left = 118 + index * 196
        picture.box((left, 290, left + 160, 400), WHITE, INK, radius=10)
        for offset in (0, 1):
            picture.circle((left + 58 + offset * 44, 330), 12, MUTED, MUTED)
            picture.circle((left + 58 + offset * 44, 368), 12, MUTED, MUTED)
        picture.text((left + 80, 424), name, 20, INK, True, "mm")
    picture.box((706, 290, 866, 400), "#E6E1D8", MUTED, radius=10)
    picture.line([(716, 300), (856, 390)], ORANGE, 5)
    picture.text((786, 424), "禁用：整排拔掉", 19, ORANGE, True, "mm")
    for index in range(4):
        left = 150 + index * 250
        picture.line([(left + 60, 452), (left + 60, 496)], MUTED, 7)
        picture.box((left, 500, left + 120, 566), SKY, BLUE, radius=10)
        picture.text((left + 60, 533), "模型", 21, BLUE, True, "mm")
    picture.text((600, 610), "插头 = provider/model-id", 22, MUTED, anchor="mm")
    picture.footer("先 /login 或起本地服务，再 /model；两步顺序别反。")


def model_roles(picture: Drawing):
    picture.header("第 5 章 · 角色分配", "不同活，找不同工位。",
                   "角色把请求路由到合适的模型；/model 负责换人。")
    seats = (("default", "常规对话", "主力", ORANGE, PEACH),
             ("smol", "低成本批量", "省钱", GREEN, SAGE),
             ("slow", "深度推理", "深想", BLUE, SKY),
             ("vision", "看图", "眼睛", BLUE, SKY))
    for index, (role, task, tag, color, fill) in enumerate(seats):
        left = 62 + index * 272
        picture.box((left, 220, left + 252, 520), fill, color)
        picture.box((left + 16, 240, left + 236, 296), WHITE, WHITE, radius=6)
        picture.text((left + 126, 268), role, 22, color, True, "mm")
        picture.text((left + 126, 344), task, 22, bold=True, anchor="mm", width=220)
        picture.circle((left + 126, 424), 38, WHITE, color, 3)
        picture.text((left + 126, 424), tag, 20, color, True, "mm")
    picture.arrow([(600, 540), (600, 580)], ORANGE)
    picture.text((600, 604), "/model 换掉具体模型，角色还在", 22, ORANGE, True, "mm")
    picture.note((92, 636, 1108, 700), "角色不是权限，是路由。",
                 "省钱档也别拿来做验收判断——按任务挑，不按习惯挑。", GREEN, SAGE)
    picture.footer("先看任务像哪个工位，再决定花多少钱。")


def tui_zones(picture: Drawing):
    picture.header("第 6 章 · TUI 分区", "先认地盘，再动手。",
                   "布局随主题微调；四块地盘的职责不变。")
    picture.box((62, 206, 1138, 664), WHITE, INK, radius=14, stroke=3)
    picture.box((82, 226, 800, 546), "#FCFAF5", LINE, radius=8)
    picture.text((102, 244), "① 对话区", 22, MUTED, True)
    picture.text((102, 286), "你的话、模型的话、穿插的工具过程", 20)
    picture.paper((112, 330, 470, 470), "助手回复", BLUE, WHITE)
    picture.paper((500, 360, 780, 500), "工具过程", GREEN, SAGE)
    picture.box((822, 226, 1118, 546), SAGE, GREEN, radius=8)
    picture.text((842, 244), "② 工具卡片", 22, GREEN, True)
    for index, label in enumerate(("read 3 行", "bash exit 0", "edit 2 处")):
        top = 292 + index * 74
        picture.box((842, top, 1098, top + 56), WHITE, GREEN, radius=8)
        picture.text((856, top + 28), label, 19, GREEN, anchor="lm")
    picture.box((82, 566, 800, 622), WHITE, ORANGE, radius=8)
    picture.text((102, 585), "③ 输入框：自然语言，或 / 开头的斜杠命令", 19)
    picture.box((82, 636, 1118, 656), INK, INK, radius=6)
    picture.text((96, 646), "④ 状态栏：模型 · 会话 · 模式 · 你现在站在哪", 17, WHITE, anchor="lm")
    picture.footer("认地盘：对话区读，卡片扫，输入框打字，状态栏确认身位。")


def tool_cards(picture: Drawing):
    picture.header("第 6 章 · 工具结果是卡片", "一眼扫过去，知道它干了啥。",
                   "卡片把每次调用收成可扫读的一条；成功打勾，失败给摘要。")
    cards = (("read", "src/app.ts:1-40", "新锚已就绪", True, BLUE, SKY),
             ("bash", "python -m unittest", "exit 0 · 12 passed", True, GREEN, SAGE),
             ("edit", "#a1b2 → 3 行替换", "1 处冲突，需重读", False, ORANGE, PEACH))
    for index, (tool, detail, status, ok, color, fill) in enumerate(cards):
        top = 214 + index * 130
        picture.box((120, top, 1080, top + 108), fill, color, radius=12)
        picture.text((150, top + 20), tool, 24, color, True)
        picture.text((150, top + 56), detail, 20)
        picture.circle((1010, top + 54), 24, WHITE, color, 3)
        if ok:
            picture.line([(998, top + 54), (1007, top + 63), (1022, top + 44)], GREEN, 4)
        else:
            picture.line([(999, top + 43), (1021, top + 65)], ORANGE, 4)
            picture.line([(1021, top + 43), (999, top + 65)], ORANGE, 4)
        picture.text((960, top + 20), status, 18, MUTED, anchor="rt")
    picture.text((600, 636), "卡片可以展开细节；先扫状态，再决定看不看", 21, MUTED, anchor="mm")
    picture.footer("卡片是给你扫的，不是给机器看的：先看成功/失败，再进细节。")


def preview_accept(picture: Drawing):
    picture.header("第 6 章 · 预览再落盘", "proposed → Accept → 磁盘。",
                   "写盘前你有一票否决；中间那步不是装饰。")
    picture.paper((92, 222, 470, 560), "proposed 变更", ORANGE, PEACH, ruled=False)
    picture.text((118, 254), "- const total = 0;", 21, ORANGE)
    picture.text((118, 292), "+ const total = 1;", 21, GREEN)
    picture.text((118, 340), "3 行上下文", 19, MUTED)
    picture.text((118, 396), "改的是哪一行、", 20)
    picture.text((118, 428), "前后长什么样，", 20)
    picture.text((118, 460), "都在这里写清楚。", 20)
    picture.arrow([(480, 390), (566, 390)])
    picture.box((578, 318, 780, 462), SAGE, GREEN, radius=16)
    picture.text((679, 360), "Accept", 30, GREEN, True, "mm")
    picture.text((679, 412), "或先反对", 20, MUTED, anchor="mm")
    picture.arrow([(790, 390), (872, 390)], GREEN)
    picture.box((884, 300, 1114, 480), WHITE, INK, radius=12)
    picture.text((999, 330), "磁盘", 24, bold=True, anchor="mm")
    for index in range(3):
        top = 372 + index * 26
        picture.line([(908, top), (1090, top)], LINE, 5)
    picture.text((999, 500), "接受后才写入", 19, MUTED, anchor="mm")
    picture.arrow([(679, 470), (679, 540), (281, 540), (281, 572)], MUTED, 3)
    picture.text((480, 566), "反对：补一句要求，重新提案", 20, MUTED, anchor="mm")
    picture.footer("预览是安全带：先看清 diff，再让它落盘。")


def ask_picker(picture: Drawing):
    picture.header("第 6 章 · 歧义就 ask", "别让模型瞎猜，让人点一下。",
                   "ask 把分叉摊在桌面上：选项、后果、然后才动手。")
    picture.robot((180, 330))
    picture.text((180, 406), "模型拿不准", 22, bold=True, anchor="mm")
    picture.text((180, 446), "两种改法都说得通", 19, MUTED, anchor="mm")
    picture.arrow([(258, 380), (352, 380)], ORANGE)
    picture.box((366, 214, 1000, 596), WHITE, INK, radius=14, stroke=3)
    picture.text((394, 238), "ask：选一个", 24, bold=True)
    options = (("A", "保留旧字段，只加新字段", "兼容旧调用", GREEN),
               ("B", "删掉旧字段，直接用新结构", "调用方要同步改", ORANGE),
               ("C", "先给迁移脚本", "多一步，但可回退", BLUE))
    for index, (key, title, effect, color) in enumerate(options):
        top = 286 + index * 96
        picture.box((394, top, 972, top + 76), SAGE if color is GREEN else WHITE,
                     color, radius=10)
        picture.badge((424, top + 38), key, color)
        picture.text((456, top + 14), title, 20, bold=True)
        picture.text((456, top + 44), effect, 18, MUTED)
    picture.text((394, 566), "你点完，循环才继续", 19, ORANGE)
    picture.arrow([(1010, 380), (1096, 380), (1096, 300)], GREEN, 3)
    picture.box((1030, 246, 1150, 296), SAGE, SAGE, radius=8)
    picture.text((1090, 271), "继续", 20, GREEN, True, "mm")
    picture.footer("能问就问：猜错的返工，通常比一次点击贵。")


def first_project(picture: Drawing):
    picture.header("第 6 章 · 第一次改代码", "四步走完一轮。",
                   "从打开仓库到验收，路径是固定的。")
    steps = (("打开仓库", "在项目根目录启动 omp", ORANGE, PEACH),
             ("说需求", "目标 + 验收标准", BLUE, SKY),
             ("看工具卡片", "它读了什么、改了什么", GREEN, SAGE),
             ("验收改动", "自己跑一遍，再决定收下", ORANGE, PEACH))
    for index, (title, detail, color, fill) in enumerate(steps):
        left = 56 + index * 284
        picture.box((left, 240, left + 256, 470), fill, color)
        picture.badge((left + 34, 272), index + 1, color)
        picture.text((left + 128, 330), title, 25, color, True, "mm", width=220)
        picture.text((left + 128, 382), detail, 19, MUTED, anchor="mm", width=210)
        if index < 3:
            picture.arrow([(left + 264, 355), (left + 282, 355)], color, 3)
    picture.note((92, 512, 1108, 608), "第四步不能省。",
                 "模型说「改好了」不算验收；看 diff、跑测试、再提交。", ORANGE, PEACH)
    picture.note((92, 628, 1108, 700), "跑了偏？",
                 "先截图或贴报错进对话，再让它修；不要只凭印象复述。", BLUE, SKY)
    picture.footer("一轮的终点是「你验收过」，不是「模型说完了」。")


FIGURES = {
    "fig1-1-agent-loop": agent_loop,
    "fig1-2-chat-vs-agent": chat_vs_agent,
    "fig1-3-harness-horse": harness_horse,
    "fig2-1-context-desk": context_desk,
    "fig2-2-tool-envelope": tool_envelope,
    "fig2-3-thinking-dial": thinking_dial,
    "fig3-1-four-shells": four_shells,
    "fig3-2-package-map": package_map,
    "fig3-3-natives-inplace": natives_inplace,
    "fig4-1-install-tree": install_tree,
    "fig4-2-bun-vs-binary": bun_or_binary,
    "fig5-1-provider-board": provider_board,
    "fig5-2-model-roles": model_roles,
    "fig6-1-tui-zones": tui_zones,
    "fig6-2-tool-cards": tool_cards,
    "fig6-3-preview-accept": preview_accept,
    "fig6-4-ask-picker": ask_picker,
    "fig6-5-first-project": first_project,
    "fig7-2-fork-resume": fork_resume,
    "fig15-1-compaction": compaction,
    "fig16-1-memory-loop": memory_loop,
}


def contact_sheet(paths: list[Path], destination: Path, regular: Path):
    columns = 2
    rows = math.ceil(len(paths) / columns)
    sheet = Image.new("RGB", (columns * 720, rows * 510), "#EDEFE7")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(str(regular), 18)
    for index, path in enumerate(paths):
        with Image.open(path) as original:
            thumbnail = original.copy()
        thumbnail.thumbnail((708, 472), Image.Resampling.LANCZOS)
        left, top = index % columns * 720 + 6, index // columns * 510 + 4
        sheet.paste(thumbnail, (left, top))
        draw.text((left + 8, top + 477), path.name, font=font, fill=INK)
    destination.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(destination, quality=94, subsampling=0)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=ROOT / ".scratch/python-illustrations/preview")
    parser.add_argument("--figure", choices=FIGURES, action="append")
    parser.add_argument("--font", type=Path)
    parser.add_argument("--bold-font", type=Path)
    parser.add_argument("--scale", type=int, choices=(1, 2, 3), default=2)
    parser.add_argument("--contact-sheet", type=Path)
    args = parser.parse_args(argv)
    try:
        regular = resolve_font(args.font, FONT_CANDIDATES)
        bold = resolve_font(args.bold_font, BOLD_CANDIDATES + (str(regular),))
        pictures = []
        for name in args.figure or FIGURES:
            picture = Drawing(regular, bold, args.scale)
            FIGURES[name](picture)
            pictures.append((name, picture.image))
        args.out_dir.mkdir(parents=True, exist_ok=True)
        encoded = []
        for name, image in pictures:
            buffer = io.BytesIO()
            image.save(buffer, format="JPEG", quality=80, subsampling=0,
                       optimize=True, dpi=(300, 300))
            raw = buffer.getvalue()
            if len(raw) > MAX_JPEG_BYTES:
                raise ValueError(
                    f"{name}: {len(raw)} bytes, over the {MAX_JPEG_BYTES} "
                    "budget the book embeds per photograph")
            encoded.append((name, image, raw))
        paths = []
        for name, image, raw in encoded:
            path = args.out_dir / f"{name}.jpg"
            path.write_bytes(raw)
            paths.append(path)
            print(f"{path.name}: {image.width} x {image.height}, {len(raw)} bytes")
        if args.contact_sheet:
            contact_sheet(paths, args.contact_sheet, regular)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Illustration generation failed: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
