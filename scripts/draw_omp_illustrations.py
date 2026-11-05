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


def session_git(picture: Drawing):
    picture.header("第 7 章 · 会话树", "会话像提交图，leaf 是你站的位置。",
                   "条目有父子关系；leaf 决定下一步接在哪。")
    picture.line([(150, 400), (1050, 400)], MUTED, 3)
    for index in range(4):
        x = 190 + index * 220
        picture.circle((x, 400), 22, WHITE, INK, 3)
        picture.text((x, 400), str(index + 1), 19, INK, True, "mm")
    picture.line([(410, 400), (410, 300), (700, 300)], MUTED, 3)
    for x in (630, 770):
        picture.circle((x, 300), 22, WHITE, BLUE, 3)
        picture.text((x, 300), "b", 19, BLUE, True, "mm")
    picture.circle((850, 300), 26, ORANGE, ORANGE)
    picture.text((850, 300), "L", 21, WHITE, True, "mm")
    picture.text((850, 250), "leaf：下一步接这里", 20, ORANGE, True, "mm")
    picture.text((410, 216), "分叉出的另一条路", 19, BLUE, anchor="mm")
    picture.text((600, 470), "节点 = 历史条目，父子关系写在 JSONL 里", 20, MUTED, anchor="mm")
    picture.note((92, 540, 1108, 626), "/tree、/branch 只移动 leaf。",
                 "它们在同一个会话文件里导航，不会生成新文件；/fork 才另开一份。", BLUE, SKY)
    picture.footer("leaf 是「现在从哪继续」，不是「最新的一行」。")


def fresh_clear_new(picture: Drawing):
    picture.header("第 7 章 · 三种重新开始", "都像清空，保住的东西不同。",
                   "先问你要保住什么：供应商流状态、会话文件，还是一张白纸。")
    columns = (("/fresh", "换掉供应商流状态", "保住：对话与文件", "丢掉：卡住的缓存句柄", ORANGE, PEACH),
               ("/clear", "同一文件内划 boundary", "保住：会话 id 与文件", "丢掉：活上下文", BLUE, SKY),
               ("/new", "开一份新会话", "保住：旧文件原样", "丢掉：当前这一切", GREEN, SAGE))
    for index, (command, action, keep, drop, color, fill) in enumerate(columns):
        left = 62 + index * 272
        picture.box((left, 224, left + 252, 606), fill, color)
        picture.text((left + 126, 262), command, 28, color, True, "mm")
        picture.text((left + 126, 316), action, 18, anchor="mm", width=206)
        picture.text((left + 22, 388), keep, 20, GREEN, True, width=210)
        picture.text((left + 22, 448), drop, 20, ORANGE, True, width=210)
        picture.box((left + 22, 512, left + 230, 560), WHITE, color, radius=8)
        picture.text((left + 126, 536), ("下一步请求重建" if index == 0 else
                                         "旧内容仍可回看" if index == 1 else
                                         "从空白开始"), 18, MUTED, anchor="mm")
    picture.text((600, 632), "streaming 或前台命令还在跑时，前两种会拒绝", 20, MUTED, anchor="mm")
    picture.footer("选错这三个词，代价不一样：先想保住什么，再敲命令。")


def export_share(picture: Drawing):
    picture.header("第 7 章 · 带走或分享", "导出是行李，分享是明信片。",
                   "一个整包搬走，一个发出去给人看。")
    picture.box((90, 250, 560, 620), WHITE, LINE)
    picture.text((325, 278), "/export", 28, ORANGE, True, "mm")
    picture.draw.rounded_rectangle(picture.coords((250, 196, 400, 254)), radius=10 * picture.scale,
                                   outline=ORANGE, width=3 * picture.scale)
    picture.box((130, 330, 520, 470), PEACH, ORANGE, radius=8)
    for index, label in enumerate(("session header", "entries / leaf", "systemPrompt",
                                    "工具描述")):
        picture.text((150, 346 + index * 28), label, 18)
    picture.text((325, 502), "备份 · 迁机 · 当教材附件", 20, ORANGE, anchor="mm")
    picture.text((325, 548), "previousSessionFiles 不进 header", 18, MUTED, anchor="mm")
    picture.box((640, 250, 1110, 620), SAGE, GREEN)
    picture.text((875, 278), "/share", 28, GREEN, True, "mm")
    picture.box((690, 330, 1060, 500), WHITE, GREEN, radius=8)
    picture.line([(960, 330), (1060, 430)], GREEN, 2)
    picture.text((712, 352), "构建快照", 20, GREEN, True)
    picture.text((712, 396), "会话里有什么，就带走什么", 19, MUTED)
    picture.text((712, 440), "改过的文件不在其中", 19, MUTED)
    picture.arrow([(875, 512), (875, 552)], ORANGE)
    picture.text((875, 574), "上传或生成可分发形态", 19, ORANGE, anchor="mm")
    picture.note((92, 640, 1108, 700), "分享前自己过一遍：",
                 "密钥、内网 URL、客户代码——默认假设 transcript 里什么都有。", ORANGE, PEACH)
    picture.footer("行李可以重，明信片会被陌生人看到。")


def read_paths(picture: Drawing):
    picture.header("第 8 章 · read 的一个 path", "同一个字符串，五种落点。",
                   "解析器只在该切的时候切后缀，再按形态选 reader。")
    picture.box((392, 210, 808, 288), WHITE, ORANGE, radius=10)
    picture.text((600, 232), "path = src/app.ts:50-80", 24, ORANGE, True, "mm")
    picture.text((600, 264), "后缀只在合法形态下被切开", 18, MUTED, anchor="mm")
    targets = (("文件切片", "行范围 / :raw", BLUE, SKY),
               ("目录树", "逐项列表", GREEN, SAGE),
               ("归档内成员", "zip / tar 成员", BLUE, SKY),
               ("网页 URL", "fetch 管线 + 缓存", ORANGE, PEACH),
               ("内部资源", "ssh:// / xd://", GREEN, SAGE))
    for index, (title, detail, color, fill) in enumerate(targets):
        left = 58 + index * 220
        picture.arrow([(600, 296), (600, 330), (left + 100, 330), (left + 100, 358)],
                      color, 3)
        picture.box((left, 366, left + 200, 470), fill, color)
        picture.text((left + 100, 396), title, 22, color, True, "mm", width=180)
        picture.text((left + 100, 434), detail, 18, MUTED, anchor="mm", width=180)
    picture.note((92, 500, 1108, 610), "选择器是白名单，不是字符串猜测。",
                 "名字里带冒号的文件优先按字面路径处理；解析失败才报错，不会瞎切。", BLUE, SKY)
    picture.text((600, 650), "读图、读 PDF 也可能让审批档升到 exec", 19, MUTED, anchor="mm")
    picture.footer("先确认 path 落在哪种形态，再谈读多少。")


def grep_glob(picture: Drawing):
    picture.header("第 8 章 · 两种找法", "grep 问内容，glob 问名字。",
                   "一个在文件里搜模式，一个按文件名列候选。")
    picture.box((70, 216, 545, 596), SAGE, GREEN)
    picture.text((307, 248), "grep", 30, GREEN, True, "mm")
    picture.text((307, 292), "内容里有没有这个模式？", 21, GREEN, anchor="mm", width=440)
    picture.box((108, 336, 508, 430), INK, INK, radius=10)
    picture.text((126, 356), "abort\\(controller\\)", 19, WHITE)
    picture.text((126, 390), "命中的行带行号返回", 17, "#BCD5BD")
    picture.text((307, 468), "正则 / 范围 / 大小写开关", 19, MUTED, anchor="mm")
    picture.text((307, 520), "输出：内容命中或文件列表", 19, MUTED, anchor="mm")
    picture.box((655, 216, 1130, 596), SKY - "#000000" if False else SKY, BLUE)
    picture.text((892, 248), "glob", 30, BLUE, True, "mm")
    picture.text((892, 292), "名字像不像这个模式？", 21, BLUE, anchor="mm", width=440)
    picture.box((700, 336, 1084, 430), WHITE, BLUE, radius=10)
    picture.text((718, 350), "src/**/*.test.ts", 19, BLUE)
    picture.text((718, 384), "只回文件名单", 17, MUTED)
    picture.text((892, 468), "候选集合先收窄", 19, MUTED, anchor="mm")
    picture.text((892, 520), "再交给 grep / read", 19, MUTED, anchor="mm")
    picture.arrow([(307, 640), (892, 640)], GREEN, 3)
    picture.text((600, 664), "合起来：glob 收窄 → grep 抠符号 → read 精确切片", 19, INK, anchor="mm")
    picture.footer("找内容用 grep，找文件用 glob；别拿一个当另一个使。")


def ast_grep(picture: Drawing):
    picture.header("第 8 章 · ast_grep 按结构找", "字符串会误伤，语法不会。",
                   "注释和字符串里的同名调用，纯文本分不清。")
    picture.box((70, 210, 600, 500), INK, INK, radius=10)
    picture.text((92, 230), "src/handler.ts", 18, "#BCD5BD")
    lines = (("// 旧写法：foo( 已经废弃", "comment"),
             ("const a = foo(1);", "hit"),
             ("const b = \"foo( 在字符串里\";", "comment"),
             ("const c = foo(2);", "hit"))
    for index, (line, kind) in enumerate(lines):
        picture.text((92, 272 + index * 48), line, 18,
                     "#BCD5BD" if kind == "hit" else "#8E9A90")
    picture.box((560, 232, 1110, 330), PEACH, ORANGE)
    picture.text((582, 250), "grep \"foo(\" → 4 行全中", 20, ORANGE, True)
    picture.text((582, 286), "其中 2 行是注释或字符串", 18, MUTED)
    picture.box((560, 356, 1110, 454), SAGE, GREEN)
    picture.text((582, 374), "ast_grep 'foo($A)' → 2 个节点", 20, GREEN, True)
    picture.text((582, 410), "只回真正的调用表达式", 18, MUTED)
    picture.note((92, 528, 1108, 620), "结构命令要选对语言与规则。",
                 "规则语言以 ast-grep 文档为准；不确定就先小范围试跑。", BLUE, SKY)
    picture.text((600, 652), "找到节点后，下一步才是 ast_edit 出补丁", 19, MUTED, anchor="mm")
    picture.footer("先分清「长得像」和「语法上是」。")


def ast_edit_preview(picture: Drawing):
    picture.header("第 9 章 · ast_edit", "先提案，再 Accept。",
                   "结构级改动一次很多处，预览是必经之路。")
    picture.box((80, 216, 470, 330), WHITE, BLUE)
    picture.text((100, 238), "匹配的结构", 21, BLUE, True)
    picture.text((100, 276), "foo($A, $B)", 22)
    picture.text((100, 306), "工作区里 12 处", 18, MUTED)
    picture.arrow([(480, 273), (566, 273)], ORANGE)
    picture.box((578, 216, 900, 330), PEACH, ORANGE)
    picture.text((598, 238), "提案：换成 bar($A)", 21, ORANGE, True)
    picture.text((598, 276), "只列 diff，不落盘", 19, MUTED)
    picture.arrow([(910, 273), (996, 273)], ORANGE)
    picture.box((1008, 216, 1140, 330), SAGE, GREEN)
    picture.text((1074, 252), "Accept", 22, GREEN, True, "mm")
    picture.text((1074, 292), "才写磁盘", 18, MUTED, anchor="mm")
    picture.paper((200, 380, 1000, 590), "预览 3 / 12", ORANGE, PEACH, ruled=False)
    picture.text((226, 406), "- const x = foo(a, b);", 21, ORANGE)
    picture.text((226, 444), "+ const x = bar(a);", 21, GREEN)
    picture.text((226, 492), "上下文 2 行 · 语法平衡由规则保证", 18, MUTED)
    picture.arrow([(1074, 340), (1074, 640), (600, 640), (600, 596)], MUTED, 3)
    picture.text((820, 660), "拒绝：改规则，重新提案", 19, MUTED, anchor="mm")
    picture.footer("批量的前提是能看清：看不清的 diff，先别 Accept。")


def bash_inprocess(picture: Drawing):
    picture.header("第 10 章 · 进程内命令", "能不出门，就不出门。",
                   "常用 coreutils 在 omp 里直接做；只有真外部程序才 fork。")
    picture.box((70, 214, 800, 596), SAGE, GREEN, radius=14)
    picture.text((100, 240), "omp 进程内", 24, GREEN, True)
    for index, tool in enumerate(("ls", "sed", "jq", "sort", "head", "wc")):
        left = 112 + (index % 3) * 220
        top = 300 + (index // 3) * 96
        picture.box((left, top, left + 180, top + 64), WHITE, GREEN, radius=8)
        picture.text((left + 90, top + 32), tool, 22, GREEN, True, "mm")
    picture.text((435, 530), "不启动新进程：快，也少环境差异", 20, MUTED, anchor="mm")
    picture.box((840, 214, 1130, 596), WHITE, ORANGE, radius=14)
    picture.text((985, 244), "真外部程序", 23, ORANGE, True, "mm")
    picture.box((880, 300, 1090, 388), PEACH, ORANGE, radius=8)
    picture.text((985, 330), "bash 命令", 21, ORANGE, True, "mm")
    picture.text((985, 362), "PTY / 后台 / 服务", 17, MUTED, anchor="mm")
    picture.arrow([(800, 340), (872, 340)], ORANGE, 3)
    picture.text((985, 430), "fork-exec 一次", 19, MUTED, anchor="mm")
    picture.text((985, 480), "等待、退出码、截断", 19, MUTED, anchor="mm")
    picture.text((985, 540), "审批与侧效应更重", 19, ORANGE, anchor="mm")
    picture.footer("写命令前先想：这件事进程内能不能做完？")


def pty_background(picture: Drawing):
    picture.header("第 10 章 · 四种跑法", "字段决定落到哪条分支。",
                   "不填是前台；pty、async、name 各走一条。")
    modes = (("普通前台", "不填字段", "同步等结果", ORANGE, PEACH),
             ("PTY", "pty: true", "真终端语义", BLUE, SKY),
             ("后台 job", "async: true", "立刻回 job id", GREEN, SAGE),
             ("受监督服务", "name: …", "ready 日志/端口", GREEN, SAGE))
    for index, (title, field, detail, color, fill) in enumerate(modes):
        left = 58 + index * 272
        picture.box((left, 224, left + 252, 520), fill, color)
        picture.text((left + 126, 258), title, 25, color, True, "mm", width=220)
        picture.box((left + 24, 312, left + 228, 368), WHITE, color, radius=8)
        picture.text((left + 126, 340), field, 19, color, True, "mm")
        picture.text((left + 126, 412), detail, 20, MUTED, anchor="mm", width=210)
        picture.text((left + 126, 470), "期限默认 300s", 18, MUTED, anchor="mm")
    picture.note((92, 548, 1108, 636), "name 与 async / timeout 互斥。",
                 "给了 name 就是服务：ready 由日志正则与 TCP 端口共同判定。", ORANGE, PEACH)
    picture.text((600, 668), "长跑不堵下一轮：交给 job 或 broker", 19, MUTED, anchor="mm")
    picture.footer("先挑跑法，再写命令；前台硬等是最常见的时间浪费。")


def eval_kernel(picture: Drawing):
    picture.header("第 10 章 · 持久内核", "一次调用一格，状态留下。",
                   "同一运行时里，后面的单元格还能看见前面的绑定。")
    cells = ("x = 41", "x += 1", "print(x)  # 42")
    for index, code in enumerate(cells):
        top = 230 + index * 118
        picture.box((120, top, 760, top + 92), INK, INK, radius=10)
        picture.text((146, top + 18), f"[{index + 1}]", 18, "#BCD5BD")
        picture.text((186, top + 30), code, 22, WHITE)
    picture.box((830, 268, 1120, 520), SAGE, GREEN, radius=14)
    picture.text((975, 296), "变量背包", 22, GREEN, True, "mm")
    picture.text((975, 336), "x = 42", 20, GREEN, "mm")
    picture.text((975, 386), "跨单元格可见", 19, MUTED, anchor="mm")
    picture.arrow([(770, 414), (820, 414)], GREEN, 3)
    picture.text((600, 624), "内核不随单次调用退出；语言运行时缺失会报错", 19, MUTED, anchor="mm")
    picture.footer("适合反复试：算数据、驱动 browser/computer；系统管道仍走 bash。")


def lsp_workbench(picture: Drawing):
    picture.header("第 11 章 · lsp 工作台", "IDE 菜单，变成工具调用。",
                   "问语言服务器，而不是靠上次读到的文本猜。")
    actions = ("diagnostics", "definition / references", "symbols", "rename", "code_actions")
    for index, action in enumerate(actions):
        top = 216 + index * 78
        picture.box((90, top, 520, top + 60), WHITE, BLUE, radius=8)
        picture.text((112, top + 18), action, 20, BLUE, True)
        picture.arrow([(530, top + 30), (618, top + 30)], BLUE, 3)
        picture.circle((650, top + 30), 16, SAGE, GREEN, 2)
        picture.line([(642, top + 30), (648, top + 37), (660, top + 21)], GREEN, 3)
    picture.box((700, 216, 1130, 600), SAGE, GREEN, radius=12)
    picture.text((726, 242), "服务器回答", 21, GREEN, True)
    picture.text((726, 288), "红线：3 处", 20)
    picture.text((726, 326), "定义：src/core.py:41", 20)
    picture.text((726, 364), "引用：12 处", 20)
    picture.text((726, 426), "rename 默认就应用", 19, ORANGE)
    picture.text((726, 462), "code_actions 默认只列", 19, ORANGE)
    picture.text((726, 518), "只读动作走 read 审批", 18, MUTED)
    picture.text((726, 550), "写入动作一律 write 审批", 18, MUTED)
    picture.text((600, 640), "服务器没见过你的手改？先让它同步磁盘", 19, MUTED, anchor="mm")
    picture.footer("让服务器当眼睛：类型与引用由它回答，不靠猜。")


def debug_dap(picture: Drawing):
    picture.header("第 11 章 · debug 会话", "断点 → 停下 → 看现场。",
                   "一次 DAP 会话有固定顺序，跳步就拿不到变量。")
    steps = (("launch / attach", "起进程或挂上去", ORANGE),
             ("set_breakpoint", "下断点，再 continue", BLUE),
             ("stack_trace / scopes", "停下后取栈与作用域", GREEN),
             ("variables / evaluate", "看值或在目标里算一句", GREEN),
             ("step_over / in / out", "单步继续", BLUE),
             ("terminate", "收尾，别留适配器进程", ORANGE))
    for index, (title, detail, color) in enumerate(steps):
        left = 60 + (index % 3) * 360
        top = 220 + (index // 3) * 190
        picture.box((left, top, left + 330, top + 150), WHITE, color, radius=10)
        picture.badge((left + 30, top + 30), index + 1, color)
        picture.text((left + 24, top + 58), title, 20, color, True, width=290)
        picture.text((left + 24, top + 96), detail, 18, MUTED, width=290)
    picture.arrow([(1110, 386), (1130, 386), (1130, 596), (410, 596), (410, 578)], LINE, 3)
    picture.note((92, 624, 1108, 692), "断点没命中，先看会话对不对。",
                 "`sessions` 能查还有几个会话；打到旧会话是常见根源。", ORANGE, PEACH)
    picture.footer("先起会话、再下断点；跳步会让 variables 无现场可取。")


def write_then_diagnose(picture: Drawing):
    picture.header("第 11 章 · 改完就体检", "edit → 红线 → 再修。",
                   "诊断是下一轮的输入，不是事后补课。")
    picture.box((90, 230, 500, 380), WHITE, INK)
    picture.text((112, 252), "edit", 23, INK, True)
    picture.text((112, 292), "#a1b2 → 3 行替换", 19)
    picture.text((112, 326), "写入磁盘", 18, MUTED)
    picture.arrow([(510, 305), (596, 305)], ORANGE)
    picture.box((608, 230, 1018, 380), WHITE, ORANGE)
    picture.text((630, 252), "lsp diagnostics", 23, ORANGE, True)
    picture.text((630, 292), "src/core.ts:41  类型不匹配", 19)
    picture.line([(630, 330), (700, 336), (770, 330), (850, 336), (940, 330)], ORANGE, 3)
    picture.arrow([(1018, 305), (1100, 305), (1100, 430), (295, 430), (295, 396)], GREEN, 3)
    picture.text((960, 408), "带着红线再改一次", 18, GREEN)
    picture.box((90, 452, 1118, 560), SAGE, GREEN, radius=12)
    picture.text((112, 476), "把红线当输入", 22, GREEN, True)
    picture.text((112, 512), "诊断带文件与位置 → 下一手 edit 有的放矢", 19, MUTED)
    picture.note((92, 590, 1108, 676), "diagnosticsOnEdit 默认关、lazy 默认开。",
                 "改完不显式拉诊断，就不会有红线；第一次调用还要等服务器冷启。", BLUE, SKY)
    picture.footer("诊断不是评分，是下一轮要用的证据。")


def browser_eval(picture: Drawing):
    picture.header("第 12 章 · 浏览器当工具面", "窗口变成可调用的 API。",
                   "Eval 里的 helpers 驱动页面，结果以结构化数据回来。")
    picture.box((110, 216, 760, 560), WHITE, INK, radius=12, stroke=3)
    picture.line([(110, 254), (760, 254)], LINE, 2)
    for offset in (130, 148, 166):
        picture.circle((offset, 235), 6, MUTED, MUTED)
    picture.text((200, 226), "https://example.test/pricing", 17, MUTED)
    picture.paper((160, 290, 700, 500), "页面内容", BLUE, WHITE)
    picture.text((184, 320), "table.price", 19, BLUE)
    picture.text((184, 356), "button.buy", 19, BLUE)
    picture.box((820, 216, 1130, 400), SAGE, GREEN, radius=12)
    picture.text((975, 244), "Eval 驱动", 21, GREEN, True, "mm")
    picture.text((975, 294), "open / click / type", 20, anchor="mm")
    picture.text((975, 336), "waitFor 选择器", 20, anchor="mm")
    picture.text((975, 372), "读取结构化结果", 19, MUTED, anchor="mm")
    picture.arrow([(800, 340), (812, 340)], GREEN, 3)
    picture.box((820, 424, 1130, 548), SKY, BLUE, radius=12)
    picture.text((975, 452), "截图 / DOM 片段", 20, BLUE, True, "mm")
    picture.text((975, 492), "回给模型继续判断", 18, MUTED, anchor="mm")
    picture.text((600, 606), "登录态、验证码、支付页属于高风险区", 19, MUTED, anchor="mm")
    picture.footer("先稳定选择器再连点；刷新会让裸 xpath 变脆。")


def computer_desktop(picture: Drawing):
    picture.header("第 12 章 · computer 是桌面", "不是网页，不暴露 DOM。",
                   "左边浏览器树；右边窗口、键鼠、剪贴板。")
    picture.box((70, 216, 560, 560), WHITE, BLUE)
    picture.text((94, 240), "浏览器里", 22, BLUE, True)
    picture.text((94, 280), "dom.html", 19, BLUE)
    for index, label in enumerate(("html", "  body", "    div#app", "      button")):
        picture.text((114 + index * 6, 320 + index * 40), label, 19,
                     INK if index else MUTED)
    picture.text((94, 506), "元素句柄可直接点", 18, MUTED)
    picture.box((650, 216, 1130, 560), SAGE, GREEN)
    picture.text((674, 240), "桌面上", 22, GREEN, True)
    for index, (label, detail) in enumerate((("windows", "枚举窗口 / 显示器"),
                                              ("screenshot", "截屏，按 display 选屏"),
                                              ("click / press", "原生键鼠"),
                                              ("clipboard", "读写剪贴板"))):
        top = 292 + index * 62
        picture.box((674, top, 1106, top + 48), WHITE, GREEN, radius=8)
        picture.text((690, top + 8), label, 19, GREEN, True)
        picture.text((690, top + 26), detail, 16, MUTED)
    picture.note((92, 588, 1108, 676), "一次只允许一个 run。",
                 "并发会回 Computer worker is busy；computer.run 漏传 read_only 就当 exec 审批。", ORANGE, PEACH)
    picture.footer("能控桌面 = 权限面更大；先读安全章再开。")


def todo_board(picture: Drawing):
    picture.header("第 13 章 · todo", "把步骤摊在板子上。",
                   "板子上永远只有一个任务在跑；完成后立刻勾掉。")
    columns = (("待办", "pending", MUTED, WHITE),
               ("进行中", "in_progress", ORANGE, PEACH),
               ("完成", "completed", GREEN, SAGE))
    for index, (title, state, color, fill) in enumerate(columns):
        left = 66 + index * 360
        picture.box((left, 220, left + 320, 600), fill, color, radius=12)
        picture.text((left + 24, 244), title, 23, color, True)
        picture.text((left + 24, 276), state, 16, MUTED)
    cards = (("列 3–7 条", 0), ("写迁移脚本", 0), ("改 API 返回", 1),
             ("补测试", 0), ("跑全量测试", 2), ("更新文档", 2))
    slots = [0, 0, 0]
    for label, column in cards:
        left = 90 + column * 360
        top = 330 + slots[column] * 82
        slots[column] += 1
        picture.box((left, top, left + 272, top + 62), WHITE,
                     ORANGE if column == 1 else LINE, radius=8)
        picture.text((left + 16, top + 20), label, 19,
                     INK if column != 2 else GREEN)
        if column == 2:
            picture.line([(left + 226, top + 31), (left + 238, top + 43),
                          (left + 256, top + 17)], GREEN, 3)
    picture.note((92, 622, 1108, 692), "start 会把其他在跑的降回 pending。",
                 "task / phase 都是精确匹配；写错一个字就是找不到。", BLUE, SKY)
    picture.footer("板子是活的：完成就勾，发现新坑就加。")


def ask_options(picture: Drawing):
    picture.header("第 13 章 · ask", "分叉权交回给你。",
                   "选项、后果、推荐都摆出来，再决定。")
    picture.box((120, 214, 1080, 590), WHITE, INK, radius=14, stroke=3)
    picture.text((150, 240), "迁移 API 返回结构，选哪条？", 25, bold=True)
    rows = (("A", "保留旧字段，只加新字段", "调用方不用改；多一层兼容", GREEN, False),
            ("B", "直接换成新结构", "调用方同步改；干净但破坏兼容", ORANGE, True),
            ("C", "先给迁移脚本", "多一步，可回退", BLUE, False))
    for index, (key, title, effect, color, recommended) in enumerate(rows):
        top = 300 + index * 92
        picture.box((150, top, 1050, top + 74), SAGE if recommended else WHITE,
                     color, radius=10)
        picture.badge((182, top + 37), key, color)
        picture.text((214, top + 12), title, 20, bold=True)
        picture.text((214, top + 42), effect, 18, MUTED)
        if recommended:
            picture.text((1032, top + 12), "推荐", 17, GREEN, True, "rt")
    picture.text((150, 556), "“Other” 可以直接写自己的方案", 18, MUTED)
    picture.arrow([(1090, 380), (1136, 380)], GREEN, 3)
    picture.text((1080, 610), "选完才继续", 18, ORANGE, anchor="mm")
    picture.footer("ask 管产品决策，审批管危险操作；两者不互相替代。")


def task_subagent(picture: Drawing):
    picture.header("第 13 章 · task", "分叉出去干，再汇合。",
                   "context 只写一遍，渲染进每个子代理的 system prompt。")
    picture.box((430, 208, 770, 300), SAGE, GREEN)
    picture.text((600, 232), "父代理", 24, GREEN, True, "mm")
    picture.text((600, 270), "定隔离边界与合并策略", 17, MUTED, anchor="mm")
    picture.box((120, 350, 520, 430), SKY, BLUE)
    picture.text((320, 372), "context：共享背景", 20, BLUE, True, "mm")
    picture.text((320, 404), "每个子代理都会收到", 17, MUTED, anchor="mm")
    picture.arrow([(600, 310), (600, 338), (320, 338), (320, 342)], BLUE, 3)
    for index, (label, color, fill) in enumerate((("子代理 1：调研", ORANGE, PEACH),
                                                  ("子代理 2：改模块", GREEN, SAGE))):
        left = 120 + index * 420
        picture.arrow([(600, 336), (600, 470), (left + 190, 470), (left + 190, 500)],
                      color, 3)
        picture.box((left, 508, left + 380, 578), fill, color)
        picture.text((left + 190, 538), label, 20, color, True, "mm")
    picture.box((586, 600, 800, 660), WHITE, INK, radius=10)
    picture.text((693, 622), "wait", 21, ink if False else INK, True, "mm")
    picture.text((693, 648), "收第一件落地的事", 16, MUTED, anchor="mm")
    picture.arrow([(320, 586), (320, 630), (578, 630)], MUTED, 2)
    picture.arrow([(960, 586), (960, 630), (808, 630)], MUTED, 2)
    picture.text((600, 682), "子代理吃 token、占上下文、可能写文件", 18, MUTED, anchor="mm")
    picture.footer("派发前先想清楚：谁能写哪、结果怎么合。")


def agents_md(picture: Drawing):
    picture.header("第 14 章 · 上下文文件", "规则会先被读到，再轮到你的话。",
                   "原生发现只认最近的非空 .omp/；空目录不贡献。")
    picture.box((90, 214, 560, 600), WHITE, INK, radius=10)
    picture.text((112, 236), "repo/", 20, bold=True)
    for index, line in enumerate(("  .omp/            ← 最近非空：独占", "    AGENTS.md",
                                  "  src/", "    app.ts", "  packages/",
                                  "    .omp/AGENTS.md  ← 不会继续补", "  AGENTS.md")):
        picture.text((124, 276 + index * 38), line, 18,
                     GREEN if "AGENTS" in line or ".omp/" in line else MUTED)
    picture.arrow([(574, 400), (660, 400)], GREEN)
    picture.box((676, 240, 1120, 560), SAGE, GREEN, radius=12)
    picture.text((700, 264), "注入到本轮", 22, GREEN, True)
    picture.paper((710, 310, 1086, 470), "repo-rules", GREEN, WHITE, ruled=False)
    picture.text((730, 336), "测试命令：bun test", 19)
    picture.text((730, 372), "目录约定：src 放实现", 19)
    picture.text((730, 408), "提交格式：feat(scope):", 19)
    picture.text((700, 496), "只读最近的非空 .omp/", 19, GREEN)
    picture.note((92, 618, 1108, 690), "两个零贡献：空目录、空文件。",
                 "缺文件也不会向上再找另一个 .omp/ 补。", ORANGE, PEACH)
    picture.footer("要规则生效，放在最近的 .omp/ 里并写实内容。")


def foreign_configs(picture: Drawing):
    picture.header("第 14 章 · 外来配置", "别家目录，也能读成同一套规则。",
                   "发现适配器知道各工具把文件放哪。")
    sources = (("~/.claude/CLAUDE.md", "claude"),
               (".cursor/rules/*.mdc", "cursor"),
               ("GEMINI.md", "gemini"))
    for index, (path, provider) in enumerate(sources):
        top = 236 + index * 122
        picture.box((80, top, 520, top + 92), SKY, BLUE, radius=10)
        picture.text((104, top + 18), path, 19, BLUE, True)
        picture.text((104, top + 54), f"provider: {provider}", 17, MUTED)
        picture.arrow([(530, top + 46), (620, top + 46)], BLUE, 3)
    picture.box((636, 236, 1130, 560), SAGE, GREEN, radius=12)
    picture.text((660, 260), "同一套上下文注入", 22, GREEN, True)
    picture.text((660, 302), "发现 → 读取 → 归一 → 进提示", 19, MUTED)
    picture.paper((676, 344, 1092, 500), "合并后的规则", GREEN, WHITE)
    picture.text((696, 368), "同作用域下 native 优先级最高", 18, ORANGE)
    picture.text((696, 404), "外来基不按 profile 隔离", 18, MUTED)
    picture.note((92, 590, 1108, 676), "读得进来，不等于你该全都留着。",
                 "同一件事写三份，冲突时按优先级裁决；清理比叠加省事。", ORANGE, PEACH)
    picture.footer("迁移期可以靠它过渡；稳定后收敛到一份 native 规则。")


def branch_summary(picture: Drawing):
    picture.header("第 15 章 · 分支摘要", "分叉口的去向，留一张便签。",
                   "branchSummary.enabled 默认 false；开了才会生成。")
    picture.line([(120, 420), (1060, 420)], MUTED, 3)
    for x in (200, 420, 640):
        picture.circle((x, 420), 20, WHITE, INK, 3)
    picture.line([(420, 420), (420, 300), (760, 300)], MUTED, 3)
    picture.circle((760, 300), 24, WHITE, ORANGE, 3)
    picture.text((760, 300), "b", 19, ORANGE, True, "mm")
    picture.arrow([(790, 300), (860, 300)], ORANGE, 3)
    picture.box((876, 240, 1110, 372), PEACH, ORANGE, radius=10)
    picture.text((894, 262), "分支摘要", 20, ORANGE, True)
    picture.text((894, 300), "从哪分出来、", 18)
    picture.text((894, 328), "为什么分、想试什么", 18)
    picture.box((876, 400, 1110, 500), SAGE, SAGE, radius=10)
    picture.text((894, 420), "默认关闭", 19, GREEN, True)
    picture.text((894, 452), "开了才写这一条", 17, MUTED)
    picture.text((380, 486), "摘要挂在分叉点，不代替原条目", 19, MUTED, anchor="mm")
    picture.note((92, 560, 1108, 650), "摘要也有成本。",
                 "短分叉不值得开；长实验、多人接力再打开。", BLUE, SKY)
    picture.footer("摘要记的是「为什么走这条」，细节仍回原文查。")


def sqlite_store(picture: Drawing):
    picture.header("第 16 章 · 本地后端", "记在本机，不出门。",
                   "local 后端的记忆产物有文件根；mnemopi 走检索接口。")
    picture.box((100, 220, 640, 560), WHITE, INK, radius=12)
    picture.text((124, 244), "这台机器", 23, bold=True)
    picture.box((150, 300, 590, 400), SAGE, GREEN, radius=10)
    picture.text((370, 326), "~/.omp/agent/", 20, GREEN, True, "mm")
    picture.text((370, 362), "MEMORY.md · learned.md", 18, GREEN, anchor="mm")
    picture.text((370, 440), "memory:// 前缀读得到", 18, MUTED, anchor="mm")
    picture.text((370, 478), "进不进远端，取决后端", 18, MUTED, anchor="mm")
    picture.box((720, 240, 1120, 520), SKY, BLUE, radius=12)
    picture.text((744, 264), "两种后端，别混", 21, BLUE, True)
    picture.text((744, 306), "local：文件根 + 摘要", 19)
    picture.text((744, 344), "mnemopi：retain/recall/reflect", 19)
    picture.text((744, 404), "local 没有结构化三件套", 18, ORANGE)
    picture.text((744, 442), "mnemopi 下 memory://root 会失败", 18, ORANGE)
    picture.arrow([(710, 380), (652, 380)], MUTED, 3)
    picture.note((92, 592, 1108, 680), "先问「写在哪」。",
                 "数据驻留位置、权限、撤销方式，接手任何机器都先确认。", GREEN, SAGE)
    picture.footer("本地不等于自动安全：盘上的东西也会被备份和分享带走。")


def advisor(picture: Drawing):
    picture.header("第 17 章 · advisor", "第二双眼睛，只管挑刺。",
                   "主模型做事；advisor 按 WATCHDOG 规则做隔离审查。")
    picture.box((70, 220, 700, 520), WHITE, INK, radius=12)
    picture.text((94, 244), "主模型", 22, bold=True)
    picture.robot((385, 360), BLUE)
    picture.text((385, 452), "改代码、跑测试、写提交", 19, MUTED, anchor="mm")
    picture.arrow([(390, 500), (390, 546), (300, 546)], ORANGE, 3)
    picture.box((120, 560, 480, 640), PEACH, ORANGE, radius=10)
    picture.text((300, 582), "高风险变更", 20, ORANGE, True, "mm")
    picture.text((300, 612), "架构 / 安全 / 大面积改动", 16, MUTED, anchor="mm")
    picture.arrow([(490, 600), (640, 600), (640, 430)], ORANGE, 3)
    picture.box((652, 236, 1120, 520), SAGE, GREEN, radius=12)
    picture.text((676, 260), "advisor", 23, GREEN, True)
    picture.text((676, 302), "读 WATCHDOG.md / WATCHDOG.yml", 19)
    picture.text((676, 340), "只看该看的：提案与 diff", 19)
    picture.text((676, 378), "工具隔离，不抢主会话的活", 19)
    picture.box((700, 420, 1076, 484), WHITE, GREEN, radius=8)
    picture.text((718, 438), "输出：挑刺清单 + 建议", 18, GREEN)
    picture.text((718, 462), "无异议才合并", 16, MUTED)
    picture.text((600, 672), "打开 advisor = 多付一路 token；高风险才开", 19, MUTED, anchor="mm")
    picture.footer("advisor 不是聊天玩伴，是隔离的审查视角。")


def magic_keywords(picture: Drawing):
    picture.header("第 18 章 · magic keywords", "词出现在散文里，才注入说明。",
                   "全小写、独立成词；代码块与行内代码不算。")
    picture.box((80, 226, 560, 420), SAGE, GREEN)
    picture.text((104, 250), "会触发", 21, GREEN, True)
    picture.text((104, 300), "ultrathink about the failure modes", 18)
    picture.text((104, 336), "orchestrate the migration", 18)
    picture.text((104, 380), "句读、引号相邻可以", 17, MUTED)
    picture.box((620, 226, 1110, 420), PEACH, ORANGE)
    picture.text((644, 250), "不触发", 21, ORANGE, True)
    picture.text((644, 300), "Ultrathink（大写开头）", 18)
    picture.text((644, 336), "ultrathink.ts / ultrathink()", 18)
    picture.text((644, 380), "围栏代码块、行内代码、注释", 17, MUTED)
    picture.arrow([(600, 323), (612, 323)], INK, 3)
    picture.box((80, 452, 1110, 556), INK, INK, radius=10)
    picture.text((104, 474), "→ 隐藏 notice 注入本轮", 19, "#BCD5BD")
    picture.text((104, 510), "可见词留在你的消息里；只影响含词的那一回合", 18, WHITE)
    picture.note((92, 584, 1108, 676), "开关在 /settings → Interaction → Magic Keywords。",
                 "也可 omp config set magicKeywords.ultrathink false 单独关。", BLUE, SKY)
    picture.footer("把词写进散文，不是写进代码示例。")


def approval_gate(picture: Drawing):
    picture.header("第 18 章 · 审批门禁", "危险工具先敲门。",
                   "审批是执行层门禁，和 ask 的产品决策是两回事。")
    picture.box((90, 230, 420, 330), SKY, BLUE)
    picture.text((255, 254), "高风险调用", 21, BLUE, True, "mm")
    picture.text((255, 294), "bash / write / computer", 17, MUTED, anchor="mm")
    picture.arrow([(430, 280), (530, 280)], ORANGE, 3)
    picture.box((542, 214, 900, 400), WHITE, ORANGE, radius=12, stroke=3)
    picture.text((721, 244), "审批", 26, ORANGE, True, "mm")
    branches = (("ask：当场问", 320), ("always-ask-cached：问过记住", 352),
                ("受限目录：出界加问", 384))
    for label, top in branches:
        picture.text((721, top), label, 18, anchor="mm")
    picture.arrow([(910, 300), (1000, 300)], GREEN, 3)
    picture.box((1014, 240, 1140, 360), SAGE, GREEN, radius=10)
    picture.text((1077, 268), "放行", 22, GREEN, True, "mm")
    picture.text((1077, 310), "或拒绝", 18, MUTED, anchor="mm")
    picture.box((542, 430, 1140, 520), PEACH, ORANGE, radius=10)
    picture.text((564, 452), "tools.approval 的逐工具 allow 在每个模式下都生效", 17, ORANGE)
    picture.text((564, 486), "光调 mode、不查 allow，可能什么门禁都没加", 17, MUTED)
    picture.note((92, 560, 1108, 650), "审批和 ask 互补。",
                 "ask 问「做不做这个产品决定」；审批挡「这一步能不能执行」。", BLUE, SKY)
    picture.footer("先读当前 allow 表，再谈模式；顺序反了会得出错误结论。")


def skill_layout(picture: Drawing):
    picture.header("第 19 章 · Skill 目录", "只扫一层，这是设计不是 bug。",
                   "常规根只认 <skills>/<name>/SKILL.md；再深一层不会被发现。")
    picture.box((80, 214, 620, 600), WHITE, INK, radius=10)
    picture.text((104, 236), "skills/", 21, bold=True)
    rows = (("  postgres/SKILL.md", "✅ 一层，能扫到", GREEN),
            ("  pdf/SKILL.md", "✅ 一层，能扫到", GREEN),
            ("  team/internal/SKILL.md", "❌ 再嵌套，扫不到", ORANGE))
    for index, (path, verdict, color) in enumerate(rows):
        top = 292 + index * 96
        picture.box((104, top, 596, top + 74), SAGE if color is GREEN else PEACH, color,
                     radius=8)
        picture.text((124, top + 12), path, 19, INK, True)
        picture.text((124, top + 44), verdict, 17, color)
    picture.box((646, 240, 1120, 360), SKY, BLUE, radius=10)
    picture.text((670, 262), "发现规则", 21, BLUE, True)
    picture.text((670, 304), "skills.customDirectories 同样非递归", 18)
    picture.text((670, 336), "想收深层：把扫描根指到那一层", 18, MUTED)
    picture.box((646, 396, 1120, 540), SAGE, GREEN, radius=10)
    picture.text((670, 420), "frontmatter 两个硬门槛", 20, GREEN, True)
    picture.text((670, 462), "name + path 必须给", 18)
    picture.text((670, 498), "description 空 → 模型不会想起读", 18, ORANGE)
    picture.note((92, 622, 1108, 692), "把目录抬上来，或改扫描根。",
                 "别把「埋深一点更整齐」带进 skills/。", ORANGE, PEACH)
    picture.footer("路径深度先过关，再谈 description 写得好不好。")


def skill_vs_ext(picture: Drawing):
    picture.header("第 19 章 · skill 与 extension", "一个写说明书，一个注册工具。",
                   "前者教模型怎么做，后者把能力接进注册表。")
    picture.box((64, 216, 552, 640), SAGE, GREEN)
    picture.text((308, 248), "Skill", 28, GREEN, True, "mm")
    picture.paper((100, 300, 516, 470), "SKILL.md", GREEN, WHITE, ruled=False)
    picture.text((122, 326), "发版检查单：", 19, GREEN, True)
    picture.text((122, 364), "1. 改 CHANGELOG", 18)
    picture.text((122, 396), "2. 打 tag", 18)
    picture.text((122, 428), "3. 推镜像", 18)
    picture.text((308, 512), "模型按需 read skill://", 19, MUTED, anchor="mm")
    picture.text((308, 550), "不新增可调用工具", 19, MUTED, anchor="mm")
    picture.text((308, 596), "改文档就能改行为", 18, GREEN, anchor="mm")
    picture.box((632, 216, 1120, 640), SKY, BLUE)
    picture.text((876, 248), "Extension", 28, BLUE, True, "mm")
    picture.box((668, 300, 1084, 470), INK, INK, radius=10)
    picture.text((688, 318), "export default (pi) => ({", 17, WHITE)
    picture.text((704, 350), "registerTool({...})", 17, "#BCD5BD")
    picture.text((704, 382), "registerCommand(/x)", 17, "#BCD5BD")
    picture.text((704, 414), "return factory", 17, WHITE)
    picture.text((876, 512), "模型能直接调用工具", 19, MUTED, anchor="mm")
    picture.text((876, 550), "要写代码、要加载", 19, MUTED, anchor="mm")
    picture.text((876, 596), "能力面更大，也更要审", 18, BLUE, anchor="mm")
    picture.note((92, 660, 1108, 700), "先问：是流程说明，还是要执行？",
                 "流程 → skill；执行 → extension。", ORANGE, PEACH)
    picture.footer("skill 不改调用面；需要新工具就别硬塞 SKILL.md。")


def mcp_trust(picture: Drawing):
    picture.header("第 20 章 · MCP 信任边界", "配置连出去，工具走进来。",
                   "每个 server 都是一条外部能力，边界要显式。")
    picture.box((80, 240, 420, 420), WHITE, INK)
    picture.text((104, 262), ".omp/mcp.json", 21, True)
    picture.text((104, 306), "项目级：随仓库走", 18, MUTED)
    picture.text((104, 344), "clone 即可能成为攻击面", 18, ORANGE)
    picture.arrow([(430, 330), (520, 330)], ORANGE, 3)
    picture.box((532, 232, 700, 560), PEACH, ORANGE, radius=40)
    picture.text((616, 262), "信任边界", 20, ORANGE, True, "mm")
    for top in (320, 390, 460):
        picture.line([(552, top), (680, top)], ORANGE, 2)
    picture.arrow([(710, 330), (800, 330)], ORANGE, 3)
    picture.box((812, 232, 1130, 560), SAGE, GREEN, radius=12)
    picture.text((836, 256), "服务器与工具", 21, GREEN, True)
    for index, (name, detail) in enumerate((("filesystem", "两个白名单目录"),
                                             ("github", "仓库读写权限"),
                                             ("internal-http", "内网端点"))):
        top = 306 + index * 78
        picture.box((836, top, 1108, top + 60), WHITE, GREEN, radius=8)
        picture.text((852, top + 10), name, 19, GREEN, True)
        picture.text((852, top + 34), detail, 16, MUTED)
    picture.note((92, 586, 1108, 674), "控制面：先审再开。",
                 "--no-extensions、mcp.enableProjectConfig、disabledServers、--profile 隔离。", BLUE, SKY)
    picture.footer("不知名仓库，先读配置，再让 agent 动手。")


def mcp_review(picture: Drawing):
    picture.header("第 20 章 · 打开仓库先看 MCP", "四步审查，再开会话。",
                   "恶意工具名与描述能诱导模型乱调用。")
    steps = (("读", "读 mcp.json 的来源", BLUE, SKY),
             ("比", "和上游对照，找多出的条目", GREEN, SAGE),
             ("关", "不用的条目点名关掉", ORANGE, PEACH),
             ("开", "带审批，先只读跑一轮", GREEN, SAGE))
    for index, (verb, detail, color, fill) in enumerate(steps):
        left = 56 + index * 276
        picture.box((left, 250, left + 244, 540), fill, color)
        picture.circle((left + 122, 306), 34, WHITE, color, 3)
        picture.text((left + 122, 306), verb, 26, color, True, "mm")
        picture.text((left + 20, 366), detail, 17, anchor="mm", width=206)
        if index < 3:
            picture.arrow([(left + 252, 396), (left + 270, 396)], color, 3)
    picture.box((92, 570, 1108, 648), WHITE, ORANGE, radius=10)
    picture.text((114, 592), "没有 --no-mcp 这个旗标", 21, ORANGE, True)
    picture.text((114, 622), "可用的是 --no-extensions、enableProjectConfig、disabledServers、--profile", 18, MUTED)
    picture.text((600, 680), "审配置比事后翻调用记录便宜", 19, MUTED, anchor="mm")
    picture.footer("陌生仓库的第一条命令不是「跑一下」，是「读配置」。")


def hooks(picture: Drawing):
    picture.header("第 21 章 · 钩子点", "调用前后，各挂一道门帘。",
                   "pre 能改写或拦截；post 记录结果。")
    picture.box((80, 330, 300, 470), WHITE, INK)
    picture.text((190, 386), "模型请求", 21, INK, True, "mm")
    picture.text((190, 424), "tool_call", 18, MUTED, anchor="mm")
    picture.arrow([(310, 400), (400, 400)], INK, 3)
    picture.box((412, 280, 700, 520), PEACH, ORANGE, radius=12)
    picture.text((556, 308), "pre 钩子", 24, ORANGE, True, "mm")
    picture.text((556, 356), "审计参数", 19, anchor="mm")
    picture.text((556, 394), "{ input } 改写", 19, anchor="mm")
    picture.text((556, 432), "{ block, reason } 拦下", 19, anchor="mm")
    picture.arrow([(710, 400), (800, 400)], ORANGE, 3)
    picture.box((812, 330, 1000, 470), SAGE, GREEN)
    picture.text((906, 384), "工具执行", 21, GREEN, True, "mm")
    picture.text((906, 422), "真实副作用", 17, MUTED, anchor="mm")
    picture.arrow([(1010, 400), (1080, 400)], GREEN, 3)
    picture.text((1080, 370), "结果", 18, MUTED, anchor="mm")
    picture.arrow([(906, 480), (906, 570), (556, 570), (556, 532)], BLUE, 3)
    picture.box((412, 578, 900, 660), SKY, BLUE, radius=10)
    picture.text((434, 600), "post 钩子：记录、摘要、报警", 19, BLUE, True)
    picture.text((434, 632), "拒绝要在 pre 返回 reason，静默失败最糟", 17, MUTED)
    picture.text((600, 700), "根目录的工厂不会被发现：放进 pre/ 或 post/", 18, MUTED, anchor="mm")
    picture.footer("两道门帘都只为同一件事：让副作用可见、可拦。")


def hook_approve(picture: Drawing):
    picture.header("第 21 章 · 钩子与审批", "两道门，各自有分工。",
                   "hook 是策略，审批是人；同一规则别写两遍。")
    picture.box((80, 240, 330, 420), WHITE, INK)
    picture.text((205, 300), "工具调用", 21, INK, True, "mm")
    picture.text((205, 344), "bash rm -rf …", 18, MUTED, anchor="mm")
    picture.arrow([(340, 330), (430, 330)], INK, 3)
    picture.box((442, 224, 760, 456), PEACH, ORANGE, radius=12)
    picture.text((601, 250), "第一道：hook", 22, ORANGE, True, "mm")
    picture.text((601, 294), "机器可判的规则", 18, MUTED, "mm")
    picture.text((601, 336), "返回 block + reason", 19, ORANGE, "mm")
    picture.text((601, 378), "命中就直接失败", 18, MUTED, "mm")
    picture.text((601, 418), "模型读得到原因", 17, MUTED, "mm")
    picture.arrow([(770, 330), (860, 330)], ORANGE, 3)
    picture.box((872, 224, 1120, 456), SKY, BLUE, radius=12)
    picture.text((996, 250), "第二道：审批", 22, BLUE, True, "mm")
    picture.text((996, 294), "需要人判断", 18, MUTED, "mm")
    picture.text((996, 336), "ask / 记住 / 受限目录", 18, BLUE, "mm")
    picture.text((996, 378), "你点同意或拒绝", 18, MUTED, "mm")
    picture.text((996, 418), "拒绝理由回给模型", 17, MUTED, "mm")
    picture.arrow([(996, 466), (996, 520)], GREEN, 3)
    picture.box((880, 532, 1112, 604), SAGE, GREEN, radius=10)
    picture.text((996, 554), "执行或终止", 19, GREEN, True, "mm")
    picture.text((996, 582), "两页日志都要有", 16, MUTED, anchor="mm")
    picture.note((92, 630, 1108, 700), "想清楚哪道是策略、哪道是人。",
                 "同一规则写两遍，排障时会互相掩盖。", ORANGE, PEACH)
    picture.footer("hook 挡确定的事，审批挡需要判断的事。")


def extension_factory(picture: Drawing):
    picture.header("第 22 章 · 扩展工厂", "先注册，再初始化，最后才有动作。",
                   "注册阶段可以挂东西；sendMessage 要等 initialize。")
    picture.box((80, 230, 560, 330), INK, INK, radius=10)
    picture.text((102, 250), "export default (pi) => ({", 19, WHITE)
    picture.text((102, 282), "  registerTool / registerCommand / on", 19, "#BCD5BD")
    picture.text((102, 310), "})", 19, WHITE)
    picture.arrow([(570, 280), (650, 280)], ORANGE, 3)
    picture.box((662, 222, 1120, 340), SAGE, GREEN, radius=12)
    picture.text((686, 246), "注册表", 21, GREEN, True)
    picture.text((686, 286), "工具 · 斜杠命令 · 快捷键 · 事件", 18)
    picture.text((686, 316), "模块先 import，工厂按路径顺序跑", 17, MUTED)
    picture.arrow([(891, 350), (891, 400)], GREEN, 3)
    picture.box((662, 412, 1120, 520), SKY, BLUE, radius=12)
    picture.text((686, 436), "initialize", 21, BLUE, True)
    picture.text((686, 476), "接 mode / session / 工具包装", 18)
    picture.text((686, 504), "这之后 sendMessage 才合法", 17, ORANGE)
    picture.arrow([(891, 530), (891, 580)], BLUE, 3)
    picture.box((662, 592, 1120, 664), PEACH, ORANGE, radius=10)
    picture.text((686, 612), "过早调用", 19, ORANGE, True)
    picture.text((686, 640), "ExtensionRuntimeNotInitializedError", 17, MUTED)
    picture.box((80, 400, 560, 600), WHITE, INK, radius=10)
    picture.text((104, 424), "子会话", 20, bold=True)
    picture.text((104, 464), "复用已 import 的工厂", 18, MUTED)
    picture.text((104, 500), "但绑定新的 API 与注册", 18, MUTED)
    picture.text((104, 552), "顶层变量别当全局单例", 18, ORANGE)
    picture.footer("生命周期是硬约束：注册 → initialize → 动作。")


def reload_plugins(picture: Drawing):
    picture.header("第 22 章 · 热重载", "换扩展，不重启会话。",
                   "/reload-plugins 只重跑扩展加载，会话记录还在。")
    picture.box((80, 240, 500, 560), WHITE, INK)
    picture.text((104, 264), "会话", 21, bold=True)
    picture.text((104, 306), "对话、文件、todo 都保留", 18, MUTED)
    picture.box((110, 356, 470, 430), SAGE, SAGE, radius=8)
    picture.text((130, 380), "扩展 v1", 19, GREEN, True)
    picture.text((130, 408), "旧行为", 16, MUTED)
    picture.arrow([(510, 390), (610, 390)], ORANGE, 3)
    picture.text((560, 360), "/reload-plugins", 18, ORANGE, True, "mm")
    picture.box((622, 240, 1120, 560), SAGE, GREEN)
    picture.text((646, 264), "扩展加载重跑", 21, GREEN, True)
    picture.text((646, 306), "重新 import、重新注册", 18)
    picture.text((646, 344), "命令与工具列表按新代码刷新", 18)
    picture.box((654, 392, 1088, 470), WHITE, GREEN, radius=8)
    picture.text((674, 414), "扩展 v2", 19, GREEN, True)
    picture.text((674, 444), "新行为，会话没断", 16, MUTED)
    picture.box((80, 590, 1120, 664), PEACH, PEACH, radius=10)
    picture.text((104, 610), "重载不保证清理旧状态", 19, ORANGE, True)
    picture.text((104, 638), "模块顶层缓存、定时器、子进程要自己收", 18, MUTED)
    picture.footer("热重载是开发循环工具，不是部署方案。")


def theme(picture: Drawing):
    picture.header("第 23 章 · 主题", "换皮肤，不换引擎。",
                   "主题只改界面观感；模型、工具、审批都不动。")
    picture.box((90, 220, 540, 600), WHITE, LINE, radius=12)
    picture.text((112, 244), "默认", 20, MUTED, True)
    picture.box((120, 300, 500, 380), "#F5F2EA", LINE, radius=8)
    picture.text((140, 326), "对话与卡片", 18, MUTED)
    picture.box((120, 400, 500, 470), INK, INK, radius=8)
    picture.text((140, 424), "深色状态栏", 17, WHITE)
    picture.arrow([(550, 400), (630, 400)], ORANGE, 3)
    picture.box((650, 220, 1110, 600), SAGE, GREEN, radius=12)
    picture.text((672, 244), "主题 JSON", 20, GREEN, True)
    for index, (name, color) in enumerate((("accent", ORANGE), ("muted", MUTED),
                                            ("surface", SAGE))):
        top = 300 + index * 74
        picture.box((684, top, 720, top + 44), color, color, radius=6)
        picture.text((736, top + 8), name, 19, INK, True)
    picture.box((684, 526, 1070, 586), "#F5F2EA", LINE, radius=6)
    picture.text((704, 546), "配色映射到界面角色", 17, MUTED)
    picture.note((92, 632, 1108, 700), "团队共享示例文件，个人覆盖放用户层。",
                 "把「确认提交」绑到难误触的键，是安全问题，不是审美问题。", BLUE, SKY)
    picture.footer("主题影响你盯日志的舒适度，不影响结论。")


def keys_isolation(picture: Drawing):
    picture.header("第 23 章 · 密钥与隔离", "profile 管配置，密钥另走一路。",
                   "profile 隔离 settings / auth / sessions / caches 的目录。")
    picture.box((76, 226, 544, 590), WHITE, INK, radius=12)
    picture.text((100, 250), "profile: work", 21, bold=True)
    picture.text((100, 292), "~/.omp/profiles/work/agent", 17, MUTED)
    for index, item in enumerate(("settings.yml", "sessions/", "caches/", "mcp.json")):
        top = 330 + index * 52
        picture.box((112, top, 508, top + 40), SAGE, SAGE, radius=6)
        picture.text((130, top + 10), item, 17, GREEN)
    picture.text((310, 548), "互不污染", 18, MUTED, anchor="mm")
    picture.box((640, 226, 1120, 590), SAGE, GREEN)
    picture.text((664, 250), "密钥仍在环境 / secrets", 21, GREEN, True)
    picture.text((664, 300), "不进可提交的 config", 18)
    picture.box((676, 344, 1084, 420), INK, INK, radius=8)
    picture.text((696, 366), "OPENAI_API_KEY=…", 17, WHITE)
    picture.text((696, 394), "OMP_PROFILE=sandbox", 17, "#BCD5BD")
    picture.text((664, 460), "secrets 子系统负责注入与遮罩", 18, MUTED)
    picture.text((664, 502), "分享前仍要自己扫一遍 transcript", 18, ORANGE)
    picture.note((92, 620, 1108, 694), "沙箱 profile：关扩展、关 MCP、便宜模型。",
                 "切过去用 --profile，别靠「记得改回 yaml」。", ORANGE, PEACH)
    picture.footer("隔离的是习惯与目录，不是密钥本身。")


def profile_hats(picture: Drawing):
    picture.header("第 23 章 · 多顶帽子", "一个开关，换一套环境。",
                   "default / work / sandbox 各自独立；--profile 压过环境变量。")
    hats = (("default", "日常", "全开", GREEN, SAGE),
            ("work", "团队", "团队技能与 MCP", BLUE, SKY),
            ("sandbox", "试验", "关扩展、关 MCP、便宜模型", ORANGE, PEACH))
    for index, (name, use, detail, color, fill) in enumerate(hats):
        left = 64 + index * 360
        picture.box((left, 224, left + 320, 560), fill, color)
        picture.text((left + 160, 262), name, 28, color, True, "mm")
        picture.text((left + 160, 318), use, 21, MUTED, anchor="mm")
        picture.text((left + 28, 372), detail, 18, anchor="mm", width=264)
        picture.text((left + 160, 500), f"--profile {name}", 18, color, True, "mm")
    picture.arrow([(600, 580), (600, 618)], INK, 3)
    picture.text((600, 640), "OMP_PROFILE 次之；PI_PROFILE 仅兜底", 18, MUTED, anchor="mm")
    picture.text((600, 678), "命名 profile 目录：~/.omp/profiles/<name>/agent", 17, MUTED, anchor="mm")
    picture.footer("用帽子隔离场景，别用「记得改回去」。")


def unknown_repo(picture: Drawing):
    picture.header("第 24 章 · 陌生仓库", "先画圈，再钻细节。",
                   "入口、边界、主数据流先落纸；细节等地图有了再说。")
    picture.box((70, 214, 640, 620), WHITE, INK, radius=10)
    picture.box((100, 250, 380, 330), SAGE, GREEN, radius=8)
    picture.text((120, 268), "入口", 20, GREEN, True)
    picture.text((120, 302), "main / cmd / route", 17)
    picture.box((410, 250, 610, 330), SKY, BLUE, radius=8)
    picture.text((430, 268), "边界", 20, BLUE, True)
    picture.text((430, 302), "外部进程 / 网络", 17)
    picture.box((100, 370, 610, 470), PEACH, ORANGE, radius=8)
    picture.text((120, 390), "主数据流：请求从哪进、存哪、谁在后台跑", 18, ORANGE, True)
    picture.box((100, 510, 250, 590), WHITE, MUTED, radius=8)
    picture.text((175, 540), "vendor/", 18, MUTED, "mm")
    picture.text((175, 566), "先别读", 15, MUTED, anchor="mm")
    picture.box((280, 510, 430, 590), WHITE, MUTED, radius=8)
    picture.text((355, 540), "生成物/", 18, MUTED, "mm")
    picture.text((355, 566), "先别读", 15, MUTED, anchor="mm")
    picture.box((460, 510, 610, 590), WHITE, MUTED, radius=8)
    picture.text((535, 540), "大 fixture", 18, MUTED, "mm")
    picture.text((535, 566), "先别读", 15, MUTED, anchor="mm")
    picture.circle((700, 300), 42, WHITE, INK, 5)
    picture.line([(730, 334), (770, 376)], INK, 8)
    picture.text((700, 250), "放大镜只对准枢纽", 18, MUTED, anchor="mm")
    picture.box((790, 400, 1120, 610), SAGE, GREEN, radius=10)
    picture.text((812, 424), "两小时交付物", 20, GREEN, True)
    picture.text((812, 466), "1. 四格 todo：地图 / 命令 / 风险 / 文档", 17)
    picture.text((812, 500), "2. 一张十分钟能讲完的草图", 17)
    picture.text((812, 534), "3. 跑通过一次的官方命令", 17)
    picture.text((812, 568), "4. docs/architecture-notes.md", 17)
    picture.footer("只读开场：先知道东西在哪，再决定碰哪。")


def project_flow(picture: Drawing):
    picture.header("第 24 章 · 接手流程", "四步走完，再谈改。",
                   "顺序固定；跳步的代价是半夜回滚。")
    steps = (("摸底", "只读：树与入口", BLUE, SKY),
             ("画图", "盒子与箭头先糙后细", GREEN, SAGE),
             ("跑通", "官方命令原样执行", ORANGE, PEACH),
             ("落盘", "写 notes，列问题", GREEN, SAGE))
    for index, (title, detail, color, fill) in enumerate(steps):
        left = 58 + index * 276
        picture.box((left, 240, left + 250, 500), fill, color)
        picture.badge((left + 34, 272), index + 1, color)
        picture.text((left + 125, 330), title, 26, color, True, "mm")
        picture.text((left + 24, 386), detail, 18, anchor="mm", width=202)
        if index < 3:
            picture.arrow([(left + 258, 370), (left + 274, 370)], color, 3)
    picture.note((92, 530, 1108, 628), "跑不通也是结果。",
                 "把完整报错贴回对话，别换一条「看起来能过」的命令。", ORANGE, PEACH)
    picture.text((600, 664), "四步里只有第三步会产生真实副作用", 19, MUTED, anchor="mm")
    picture.footer("流程的意义：让「我懂了」有可核对的证据。")


def arch_sketch(picture: Drawing):
    picture.header("第 24 章 · 架构草图", "盒子是进程或包，箭头是调用。",
                   "画给自己看：允许丑，必须有边界。")
    for bounds, label, color in (((110, 260, 360, 350), "web", BLUE),
                                  ((460, 240, 740, 340), "api", ORANGE),
                                  ((840, 260, 1090, 350), "worker", GREEN)):
        picture.box(bounds, WHITE, color, radius=8)
        picture.text((bounds[0] + 20, bounds[1] + 20), label, 22, color, True)
    picture.text((130, 300), "进程：接收请求", 16, MUTED)
    picture.text((480, 280), "进程：校验 + 写库", 16, MUTED)
    picture.text((860, 300), "进程：异步任务", 16, MUTED)
    picture.arrow([(370, 300), (450, 300)], INK, 3)
    picture.text((410, 272), "HTTP", 16, MUTED, anchor="mm")
    picture.arrow([(750, 300), (830, 300)], INK, 3)
    picture.text((790, 272), "队列", 16, MUTED, anchor="mm")
    picture.box((410, 420, 750, 500), SAGE, GREEN, radius=8)
    picture.text((430, 440), "db（单独进程）", 19, GREEN, True)
    picture.text((430, 470), "只有 api 直连", 16, MUTED)
    picture.arrow([(580, 350), (580, 410)], INK, 3)
    picture.box((110, 420, 360, 500), SKY, SKY, radius=8)
    picture.text((130, 440), "第三方", 19, BLUE, True)
    picture.text((130, 470), "只知道它存在", 16, MUTED)
    picture.arrow([(480, 330), (360, 430)], MUTED, 2)
    picture.note((92, 530, 1108, 628), "三问自检：",
                 "数据存哪？谁能写？失败谁重试？答不上就还没画完。", ORANGE, PEACH)
    picture.text((600, 664), "箭头方向 = 依赖方向，别画反", 19, MUTED, anchor="mm")
    picture.footer("草图进 docs/architecture-notes.md，供下一个人接。")


def agents_seed(picture: Drawing):
    picture.header("第 24 章 · 种下规则", "一份 AGENTS.md，省十轮解释。",
                   "写命令、目录、禁区；别写口号。")
    picture.box((80, 230, 560, 600), INK, INK, radius=10)
    picture.text((102, 252), "# AGENTS.md", 21, "#BCD5BD")
    for index, line in enumerate(("## 命令", "测试：bun test", "类型：bun run typecheck",
                                   "## 目录", "src/ 实现；tests/ 镜像结构",
                                   "## 禁区", "别改 migrations/")):
        picture.text((102, 292 + index * 42), line, 18, WHITE if line.startswith("#") else "#D8E0D8")
    picture.arrow([(570, 410), (660, 410)], GREEN, 3)
    picture.box((672, 250, 1120, 380), SAGE, GREEN, radius=10)
    picture.text((696, 274), "下次会话开始时自动注入", 20, GREEN, True)
    picture.text((696, 314), "模型先按规则行事，再读你的话", 18, MUTED)
    picture.box((672, 410, 1120, 580), WHITE, LINE, radius=10)
    picture.text((696, 434), "好规则的三个特征", 20, bold=True)
    picture.text((696, 476), "命令可原样粘贴", 18)
    picture.text((696, 510), "目录指向真实路径", 18)
    picture.text((696, 544), "禁区写出例外", 18)
    picture.footer("规则是给下一个会话的自己写的说明书。")


def handoff_checklist(picture: Drawing):
    picture.header("第 24 章 · 交付清单", "交接是勾选，不是抒情。",
                   "每一项都有证据路径与负责人。")
    items = (("安装命令跑通", "终端输出已存档"),
             ("测试命令与基线", "全绿或列出既有失败"),
             ("架构草图", "docs/architecture-notes.md"),
             ("风险与开放问题", "每条有下一步谁查"),
             ("回滚方式", "怎么退回上一版"))
    for index, (title, evidence) in enumerate(items):
        top = 232 + index * 82
        picture.box((100, top, 1080, top + 64), WHITE, LINE, radius=8)
        picture.circle((138, top + 32), 17, SAGE, GREEN, 2)
        picture.line([(130, top + 32), (137, top + 40), (150, top + 22)], GREEN, 3)
        picture.text((172, top + 12), title, 20, bold=True)
        picture.text((172, top + 38), evidence, 16, MUTED)
    picture.text((600, 668), "空着的那项，就是下一场事故的入口", 19, MUTED, anchor="mm")
    picture.footer("清单交给接手人，不是交给文档生成器。")


def explore_loop(picture: Drawing):
    picture.header("第 24 章 · 探索回路", "看一眼，确认一次，再往前。",
                   "每圈都有产出，不是反复转圈。")
    nodes = ((600, 268, "探索", BLUE, SKY),
             (900, 430, "确认", ORANGE, PEACH),
             (600, 590, "交付", GREEN, SAGE),
             (300, 430, "记录", BLUE, SKY))
    for center_x, center_y, label, color, fill in nodes:
        picture.circle((center_x, center_y), 74, fill, color, 4)
        picture.text((center_x, center_y), label, 24, color, True, "mm")
    picture.arrow([(662, 314), (820, 382)], INK, 3)
    picture.arrow([(846, 494), (672, 566)], INK, 3)
    picture.arrow([(536, 550), (368, 492)], INK, 3)
    picture.arrow([(364, 374), (534, 312)], INK, 3)
    picture.text((760, 330), "问一句", 16, MUTED)
    picture.text((760, 540), "落一条", 16, MUTED, anchor="mm")
    picture.text((420, 540), "补进 todo", 16, MUTED)
    picture.text((420, 330), "只读看", 16, MUTED, anchor="mm")
    picture.text((600, 690), "每圈结束都要有可指的东西：todo、notes 或命令输出", 18, MUTED, anchor="mm")
    picture.footer("转圈不可怕，空转才可怕。")


def bug_hunt(picture: Drawing):
    picture.header("第 25 章 · 抓 bug", "症状到根因，是一层层收窄。",
                   "先列候选，再用证据砍掉，别一上来就改。")
    picture.box((80, 224, 1120, 292), PEACH, ORANGE, radius=8)
    picture.text((102, 244), "症状：下单页偶发 500，日志只有一句 TypeError", 19, ORANGE, True)
    picture.arrow([(600, 300), (600, 340)], ORANGE, 3)
    picture.box((90, 350, 1110, 480), WHITE, LINE, radius=8)
    picture.text((112, 368), "候选（先全部写下）", 18, MUTED, True)
    for index, (label, keep) in enumerate((("空回复没判空", True),
                                             ("时区解析", False),
                                             ("缓存击穿", True),
                                             ("第三方超时", False))):
        left = 116 + index * 240
        picture.box((left, 402, left + 210, 456), SAGE if keep else WHITE,
                     GREEN if keep else LINE, radius=6)
        picture.text((left + 14, 418), label, 17, GREEN if keep else MUTED)
        picture.text((left + 196, 412), "留" if keep else "砍", 15,
                     GREEN if keep else MUTED, True, "rt")
    picture.arrow([(500, 490), (500, 540)], GREEN, 3)
    picture.box((180, 550, 1020, 640), SAGE, GREEN, radius=8)
    picture.text((202, 570), "根因：空回复在解析前就被解引用", 20, GREEN, True)
    picture.text((202, 606), "证据：栈帧 41 行 + 复现命令 + 最小输入", 17, MUTED)
    picture.text((600, 672), "砍掉的候选也要记，免得下一轮重新怀疑", 18, MUTED, anchor="mm")
    picture.footer("先收窄，再动手；一次只改一个原因。")


def repro_first(picture: Drawing):
    picture.header("第 25 章 · 复现优先", "先把失败钉死，再谈优雅。",
                   "一条能重复跑的命令，胜过十句描述。")
    picture.box((90, 224, 1110, 420), INK, INK, radius=10)
    picture.text((116, 246), "$ python -m unittest tests.test_order", 19, WHITE)
    picture.text((116, 286), "FAIL: test_totals (tests.test_order)", 18, "#FFBB9A")
    picture.text((116, 320), "AssertionError: 99.5 != 99.0", 18, "#FFBB9A")
    picture.text((116, 360), "退出码 1 · 3.2s · 必现", 16, "#BCD5BD")
    picture.box((90, 450, 650, 590), WHITE, GREEN, radius=10)
    picture.text((114, 472), "要记全的四项", 20, GREEN, True)
    picture.text((114, 512), "命令原文 / 期望 / 实际输出 / 环境", 18)
    picture.box((680, 450, 1110, 590), PEACH, ORANGE, radius=10)
    picture.text((704, 472), "偶发就先问", 20, ORANGE, True)
    picture.text((704, 512), "种子、并发、时间依赖、数据形状", 18)
    picture.note((92, 612, 1108, 690), "「尚未稳定复现」也是结论。",
                 "假装修好，比承认没复现更耽误人。", BLUE, SKY)
    picture.footer("复现命令是后面每一步的地基，别先改代码。")


def debug_session(picture: Drawing):
    picture.header("第 25 章 · 断点调查", "断点打必经之路，不打地毯。",
                   "先搜索静态嫌疑；运行态只用来验证假设。")
    picture.box((80, 230, 760, 420), WHITE, INK, radius=10)
    picture.text((104, 252), "处理函数", 20, bold=True)
    for index, line in enumerate(("  42  parse(body)", "  43  total = sum(items)",
                                   "  44  return total", "  45  except ValueError:")):
        top = 290 + index * 28
        if index == 1:
            picture.circle((124, top + 8), 8, ORANGE, ORANGE)
            picture.text((104, top), "▶", 16, ORANGE)
        picture.text((146, top), line, 17, INK if index == 1 else MUTED)
    picture.text((104, 410), "44 行前停住：total 到底是多少", 17, ORANGE)
    picture.box((800, 240, 1130, 420), SAGE, GREEN, radius=10)
    picture.text((824, 264), "停下后能做", 20, GREEN, True)
    picture.text((824, 306), "stack_trace / scopes", 17)
    picture.text((824, 340), "variables 读值", 17)
    picture.text((824, 374), "evaluate 算一句", 17)
    picture.text((600, 470), "只有搜索不够、假设又很具体时，才值得开 debug", 18, MUTED, anchor="mm")
    picture.note((92, 520, 1108, 620), "断点没命中，先查会话。",
                 "sessions 看还有几个；打到旧会话是常见根源。", ORANGE, PEACH)
    picture.text((600, 660), "调查完 terminate，别留适配器进程", 18, MUTED, anchor="mm")
    picture.footer("运行态是证据，不是探索工具。")


def debug_tools(picture: Drawing):
    picture.header("第 25 章 · 工具分工", "按问题形状选工具。",
                   "越往右越贵：能左就左。")
    columns = (("grep", "错误串、断言消息", GREEN, SAGE),
               ("read", "命中点前后 40 行", BLUE, SKY),
               ("ast_grep", "成片的结构形态", ORANGE, PEACH),
               ("debug", "运行态、变量、栈", MUTED, WHITE))
    for index, (tool, use, color, fill) in enumerate(columns):
        left = 56 + index * 276
        picture.box((left, 250, left + 250, 470), fill, color)
        picture.text((left + 125, 288), tool, 26, color, True, "mm")
        picture.text((left + 24, 346), use, 18, anchor="mm", width=202)
        picture.text((left + 125, 424), f"第 {index + 1} 选", 17, MUTED, anchor="mm")
        if index < 3:
            picture.arrow([(left + 258, 360), (left + 274, 360)], MUTED, 3)
    picture.box((92, 500, 1108, 590), SAGE, SAGE, radius=8)
    picture.text((114, 520), "组合拳：grep 锁定 → read 看上下文 → ast_grep 看结构 → debug 验假设", 19, GREEN, True)
    picture.text((114, 556), "反着来（先 debug）只在假设已经很具体时成立", 17, MUTED)
    picture.text((600, 636), "工具越贵，越要带着问题去用", 18, MUTED, anchor="mm")
    picture.footer("先便宜后昂贵，是排障的默认顺序。")


def red_green(picture: Drawing):
    picture.header("第 25 章 · 红绿循环", "先红，再绿，最后才重构。",
                   "重构是奖励，不是入场券。")
    stages = (("红", "写一条会失败的测试", ORANGE, PEACH),
              ("绿", "最小改动让它过", GREEN, SAGE),
              ("重构", "在绿的前提下整理", BLUE, SKY))
    for index, (title, detail, color, fill) in enumerate(stages):
        left = 110 + index * 340
        picture.circle((left + 100, 320), 76, fill, color, 4)
        picture.text((left + 100, 320), title, 32, color, True, "mm")
        picture.text((left + 100, 430), detail, 18, anchor="mm", width=220)
        if index < 2:
            picture.arrow([(left + 186, 320), (left + 236, 320)], color, 3)
    picture.arrow([(900, 410), (900, 470), (410, 470), (410, 410)], MUTED, 2)
    picture.text((655, 494), "重构后又红？回到最小修复", 17, MUTED, anchor="mm")
    picture.note((92, 536, 1108, 640), "同一条失败命令必须重跑。",
                 "测试通过不代表修对了；用原始复现命令验收，而不是「看起来合理」。", ORANGE, PEACH)
    picture.text((600, 672), "红绿之间不要顺手加功能", 18, MUTED, anchor="mm")
    picture.footer("每一步只有一个变量：测试、修复、整理。")


def ast_refactor(picture: Drawing):
    picture.header("第 26 章 · AST 重构", "按语法树改，不按文本糊。",
                   "规则先小范围试跑，再看全量 diff。")
    picture.box((80, 230, 500, 470), INK, INK, radius=10)
    picture.text((102, 252), "规则", 19, "#BCD5BD")
    picture.text((102, 292), "foo($A, $B)", 20, WHITE)
    picture.text((102, 330), "↓", 20, ORANGE)
    picture.text((102, 366), "bar($A)", 20, WHITE)
    picture.text((102, 410), "匹配 12 处调用", 17, "#BCD5BD")
    picture.arrow([(510, 350), (596, 350)], ORANGE, 3)
    picture.box((608, 230, 1120, 470), SAGE, GREEN, radius=10)
    picture.text((632, 254), "先小范围试跑", 20, GREEN, True)
    for index, (line, color) in enumerate((("- foo(a, b);", ORANGE), ("+ bar(a);", GREEN))):
        picture.text((636, 300 + index * 38), line, 18, color)
    picture.text((636, 386), "语法平衡由规则保证", 17, MUTED)
    picture.text((636, 422), "树没被压成线性文本", 17, MUTED)
    picture.note((92, 500, 1108, 600), "什么不适合 ast_edit：",
                 "单行小补丁用 hashline；语言不支持就别硬上。", ORANGE, PEACH)
    picture.text((600, 636), "批量 = 提案 + 预览 + Accept", 18, MUTED, anchor="mm")
    picture.footer("规则能描述形状，才配改一批。")


def task_shards(picture: Drawing):
    picture.header("第 26 章 · 子代理分片", "只有独立子树才值得并行。",
                   "共享文件的分片，合并时会互相踩。")
    picture.box((420, 210, 780, 290), SAGE, GREEN)
    picture.text((600, 232), "一次重构", 21, GREEN, True, "mm")
    picture.text((600, 266), "先切分，再派发", 16, MUTED, anchor="mm")
    lanes = (("src/auth/**", "独立：可并行", GREEN, SAGE),
             ("src/billing/**", "独立：可并行", GREEN, SAGE),
             ("src/shared/**", "共享：串行或最后合", ORANGE, PEACH))
    for index, (path, verdict, color, fill) in enumerate(lanes):
        left = 66 + index * 372
        picture.arrow([(600, 300), (600, 340), (left + 160, 340), (left + 160, 370)],
                      color, 3)
        picture.box((left, 378, left + 320, 500), fill, color)
        picture.text((left + 160, 404), path, 19, color, True, "mm")
        picture.text((left + 160, 444), verdict, 17, MUTED, anchor="mm")
    picture.box((560, 530, 900, 610), WHITE, INK, radius=8)
    picture.text((580, 550), "合并前跑全量测试", 18, INK, True)
    picture.text((580, 582), "冲突由一个人收口", 16, MUTED)
    picture.text((600, 650), "分片不是越多越好：子代理也吃 token", 18, MUTED, anchor="mm")
    picture.footer("先看目录是否重叠，再决定派几个。")


def batch_rollback(picture: Drawing):
    picture.header("第 26 章 · 批量与回滚", "改得动，也要退得回。",
                   "批量前存锚点，批量后先验证再提交。")
    picture.box((80, 230, 1110, 300), SKY, SKY, radius=8)
    picture.text((102, 250), "0. 存基线：git switch -c refactor-x；跑一次全量测试并记录", 18, INK)
    picture.box((80, 320, 1110, 440), PEACH, ORANGE, radius=8)
    picture.text((102, 340), "1. 批量改：规则 → 预览 → Accept（分片执行）", 18, ORANGE, True)
    picture.text((102, 376), "2. 立即跑全量测试；红了就看 diff 决定修或退", 18)
    picture.text((102, 408), "3. 绿了才提交；一次只提交一个意图", 18)
    picture.arrow([(600, 450), (600, 500)], INK, 3)
    picture.box((200, 510, 520, 600), WHITE, GREEN, radius=8)
    picture.text((222, 532), "保留", 20, GREEN, True)
    picture.text((222, 568), "git commit -m …", 17)
    picture.box((680, 510, 1000, 600), WHITE, ORANGE, radius=8)
    picture.text((702, 532), "回滚", 20, ORANGE, True)
    picture.text((702, 568), "git restore . / git switch -", 17)
    picture.text((600, 636), "两个方向都要事先想好，别等红了才找退路", 18, MUTED, anchor="mm")
    picture.footer("批量操作的信心，来自退路而不是预览。")


def atomic_commit(picture: Drawing):
    picture.header("第 27 章 · 原子提交", "一次一件事。",
                   "修 bug、格式化、改 CI 分开放。")
    picture.box((80, 230, 560, 430), PEACH, ORANGE, radius=10)
    picture.text((104, 252), "❌ 一坨", 21, ORANGE, True)
    for index, line in enumerate(("fix: 修空回复", "顺手 format 全仓",
                                   "顺手改 CI", "顺手升依赖")):
        picture.text((104, 296 + index * 34), "• " + line, 18)
    picture.arrow([(570, 330), (660, 330)], INK, 3)
    picture.box((672, 230, 1120, 430), SAGE, GREEN, radius=10)
    picture.text((696, 252), "✅ 三个提交", 21, GREEN, True)
    for index, line in enumerate(("fix(order): 空回复判空", "style: 全仓格式化",
                                   "ci: 缓存依赖")):
        top = 296 + index * 40
        picture.box((690, top, 1096, top + 32), WHITE, GREEN, radius=6)
        picture.text((706, top + 7), line, 16, GREEN)
    picture.box((80, 460, 1120, 560), SKY, SKY, radius=8)
    picture.text((104, 480), "每个提交都能单独 revert / cherry-pick", 18, BLUE, True)
    picture.text((104, 514), "提交信息写原因与验证命令，不写流水账", 17, MUTED)
    picture.note((92, 584, 1108, 664), "拆之前先问：",
                 "这个提交能独立通过测试吗？不能就还没拆干净。", ORANGE, PEACH)
    picture.footer("方便回滚，才是原子提交的真实目的。")


def pr_body(picture: Drawing):
    picture.header("第 27 章 · PR 正文", "评审看意图与证据。",
                   "四节固定；缺一节就先别开。")
    sections = (("Why", "为什么现在做，关联哪张票"),
                ("What", "改了什么，边界在哪"),
                ("Test", "跑过的命令与结果"),
                ("Risk", "回滚方式、影响面"))
    for index, (title, detail) in enumerate(sections):
        top = 224 + index * 104
        picture.box((100, top, 1080, top + 84), WHITE, LINE, radius=8)
        picture.text((124, top + 14), f"## {title}", 20, INK, True)
        picture.text((124, top + 48), detail, 17, MUTED)
    picture.text((600, 668), "标题写范围与意图；截图贴渲染差异", 18, MUTED, anchor="mm")
    picture.footer("正文是给半年后的自己看的，不只是给评审。")


def sdk_events(picture: Drawing):
    picture.header("第 28 章 · SDK 事件流", "先订阅，再提问，最后释放。",
                   "顺序反了，输出会丢；忘了 dispose，进程不退出。")
    steps = (("createAgentSession", "拿 session 与回退提示", BLUE, SKY),
             ("session.subscribe", "接 message_update / text_delta", GREEN, SAGE),
             ("session.prompt", "发问题，边收边写 stdout", ORANGE, PEACH),
             ("unsubscribe + dispose", "解订阅、释放，再 postmortem.cleanup", BLUE, SKY))
    for index, (call, detail, color, fill) in enumerate(steps):
        top = 230 + index * 104
        picture.box((100, top, 1080, top + 84), fill, color, radius=8)
        picture.text((124, top + 14), call, 20, color, True)
        picture.text((124, top + 48), detail, 17, MUTED)
        if index < 3:
            picture.arrow([(600, top + 90), (600, top + 100)], color, 3)
    picture.note((92, 620, 1108, 692), "进程生命周期归宿主。",
                 "导入 SDK 不装信号处理器；收到 SIGINT 要自己释放。", ORANGE, PEACH)
    picture.footer("事件流是流式输出，不是一次性返回值。")


def rpc_frames(picture: Drawing):
    picture.header("第 28 章 · RPC 帧", "一行一个 JSON，id 对 id。",
                   "stdin 请求，stdout 响应与事件；先握手。")
    picture.box((80, 220, 540, 300), SKY, BLUE, radius=8)
    picture.text((102, 240), '{"type":"ready",…}', 17, BLUE, True)
    picture.box((80, 340, 540, 430), WHITE, INK, radius=8)
    picture.text((102, 358), '{"id":"probe-1","type":"get_state"}', 17)
    picture.arrow([(550, 385), (650, 385)], INK, 3)
    picture.text((600, 360), "stdin", 16, MUTED, anchor="mm")
    picture.box((660, 340, 1120, 430), WHITE, GREEN, radius=8)
    picture.text((682, 358), '{"id":"probe-1","success":true,…}', 17, GREEN)
    picture.box((660, 460, 1120, 540), SAGE, SAGE, radius=8)
    picture.text((682, 478), '{"type":"event",…}', 17, GREEN)
    picture.text((682, 508), "事件无 id，单向推送", 16, MUTED)
    picture.arrow([(1120, 490), (1140, 490), (1140, 300), (540, 300)], MUTED, 2)
    picture.note((92, 566, 1108, 664), "错误分可恢复与不可恢复。",
                 "先跑最小握手，再看错误模型；别从语音子协议开始。", ORANGE, PEACH)
    picture.text((600, 692), "maxFrameBytes 在 ready 里，但不过滤会话内容", 17, MUTED, anchor="mm")
    picture.footer("帧是壳子，语义仍在命令与事件里。")


def team_pack(picture: Drawing):
    picture.header("第 29 章 · 团队扩展包", "把重复劳动捆成可版本化的一包。",
                   "先写清解决谁的什么问题，再堆文件。")
    picture.box((90, 230, 1080, 470), WHITE, INK, radius=12)
    for index, (label, note) in enumerate((("约定", "适用仓库与命令"),
                                            ("技能", "固定流程"),
                                            ("工具", "带审批的副作用"),
                                            ("文档", "安装、试跑、回滚"))):
        left = 120 + index * 238
        picture.box((left, 270, left + 200, 400), SAGE, GREEN, radius=10)
        picture.text((left + 100, 300), label, 23, GREEN, True, "mm")
        picture.text((left + 16, 346), note, 17, anchor="mm", width=168)
    picture.box((90, 500, 1080, 560), SKY, SKY, radius=8)
    picture.text((114, 520), "版本钉扎 + 支持的 omp 范围 + 回滚方式，缺一不可", 18, INK)
    picture.note((92, 590, 1080, 676), "没有版本的一包，就是一次性赠与。",
                 "收包的人无法判断兼容性，也无法安全升级。", ORANGE, PEACH)
    picture.text((585, 700), "先解决重复劳动，再谈打包格式", 17, MUTED, anchor="mm")
    picture.footer("包是给人交接的，不是给磁盘归档的。")


def ext_tool(picture: Drawing):
    picture.header("第 29 章 · 团队工具", "可审批、可审计，不做黑盒。",
                   "输入、副作用、失败模式都写在描述里。")
    picture.box((80, 230, 560, 560), WHITE, INK, radius=10)
    picture.text((104, 254), "输入结构", 20, bold=True)
    picture.box((110, 300, 530, 400), INK, INK, radius=8)
    picture.text((130, 318), "env: staging | prod", 17, WHITE)
    picture.text((130, 350), "dryRun: boolean", 17, WHITE)
    picture.text((130, 382), "仅这些字段，不接受自由文本", 16, "#BCD5BD")
    picture.text((104, 440), "副作用写在描述第一行", 18, ORANGE)
    picture.text((104, 486), "prod 默认只读；发消息必须预览", 18, ORANGE)
    picture.box((590, 250, 1120, 400), SAGE, GREEN, radius=10)
    picture.text((614, 274), "审批与审计", 20, GREEN, True)
    picture.text((614, 316), "写操作走审批；参数进日志", 18)
    picture.text((614, 352), "拒绝时给可执行的修复建议", 18)
    picture.box((590, 430, 1120, 540), PEACH, ORANGE, radius=10)
    picture.text((614, 452), "失败模式", 20, ORANGE, True)
    picture.text((614, 492), "超时、部分成功、幂等性——都写清", 18)
    picture.footer("团队工具的第一用户是半年后的同事。")


def distribute_trust(picture: Drawing):
    picture.header("第 29 章 · 分发与信任", "三问答得出，再装。",
                   "来源、版本、权限；有一项含糊就先别动。")
    questions = (("来源", "谁维护？仓库还是私有源？", BLUE, SKY),
                 ("版本", "钉在哪一版？兼容哪个 omp？", GREEN, SAGE),
                 ("权限", "要工具、网络、密钥里的哪些？", ORANGE, PEACH))
    for index, (title, detail, color, fill) in enumerate(questions):
        top = 230 + index * 118
        picture.box((80, top, 760, top + 92), fill, color, radius=10)
        picture.circle((126, top + 46), 24, WHITE, color, 3)
        picture.text((126, top + 46), "?", 24, color, True, "mm")
        picture.text((170, top + 16), title, 22, color, True)
        picture.text((170, top + 54), detail, 18)
    picture.box((820, 230, 1120, 490), SAGE, GREEN, radius=12)
    picture.text((844, 254), "答完才允许", 20, GREEN, True)
    picture.text((844, 298), "装", 24, GREEN, True)
    picture.text((844, 348), "试跑最小用例", 18)
    picture.text((844, 386), "看审批提示", 18)
    picture.text((844, 424), "记录来源与版本", 18)
    picture.note((92, 520, 1108, 610), "--no-extensions 是应急刹车。",
                 "怀疑捣乱时先关掉扩展复现，再回头查包。", ORANGE, PEACH)
    picture.text((600, 650), "答不出的那一项，就是装完之后要炸的点", 18, MUTED, anchor="mm")
    picture.footer("信任是问出来的，不是装出来的。")


def symptom_index(picture: Drawing):
    picture.header("第 30 章 · 症状索引", "按症状找路，别按猜测找。",
                   "一句话描述可观察症状，再进对应一节。")
    doors = (("安装 / 启动", "命令找不到、一开就报错", ORANGE, PEACH),
             ("鉴权 / 提供方", "未登录、模型列表空", BLUE, SKY),
             ("限流 / 配额", "频繁 429、突然变慢", GREEN, SAGE),
             ("语言服务", "诊断不出现、索引卡住", BLUE, SKY),
             ("会话卡住", "Working 不动、重开又卡", ORANGE, PEACH))
    for index, (title, detail, color, fill) in enumerate(doors):
        top = 216 + index * 92
        picture.box((80, top, 700, top + 74), fill, color, radius=10)
        picture.text((104, top + 12), title, 21, color, True)
        picture.text((104, top + 44), detail, 17, MUTED)
        picture.arrow([(710, top + 37), (790, top + 37)], color, 3)
        picture.text((812, top + 22), f"§30.{index + 2}", 20, MUTED, True)
    picture.note((700, 216, 1120, 470), "顺序：",
                 "先收集，再最小动作，带证据去问。", BLUE, SKY)
    picture.text((600, 692), "别连砸同一条命令；别一上来猜根因", 18, MUTED, anchor="mm")
    picture.footer("索引是分诊台，不是原理课。")


def auth_provider(picture: Drawing):
    picture.header("第 30 章 · 鉴权与提供方", "先分清是没登录，还是模型名不对。",
                   "两条路的修法完全不同。")
    picture.box((300, 214, 900, 290), WHITE, INK, radius=8)
    picture.text((600, 234), "报错：鉴权失败 / 模型不可用", 21, INK, True, "mm")
    picture.arrow([(480, 300), (360, 360)], BLUE, 3)
    picture.arrow([(720, 300), (840, 360)], ORANGE, 3)
    picture.box((80, 370, 620, 610), SKY, BLUE)
    picture.text((104, 394), "A. 没登录 / 密钥无效", 21, BLUE, True)
    picture.text((104, 438), "查：是否做过 /login", 18)
    picture.text((104, 474), "查：环境变量名对不对", 18)
    picture.text((104, 510), "查：--profile 是否指错档", 18)
    picture.text((104, 560), "修：回第 5 章登录路径", 18, BLUE, True)
    picture.box((660, 370, 1120, 610), PEACH, ORANGE)
    picture.text((684, 394), "B. 提供方或模型 id 不对", 21, ORANGE, True)
    picture.text((684, 438), "查：--model 写法是否 provider/model", 18)
    picture.text((684, 474), "查：角色表里那个名字存在吗", 18)
    picture.text((684, 510), "修：omp models find 先确认", 18, ORANGE, True)
    picture.text((600, 650), "两条都查过，再谈网络与配额", 18, MUTED, anchor="mm")
    picture.footer("鉴权是「你是谁」，模型名是「找谁」——别混。")


def session_stuck(picture: Drawing):
    picture.header("第 30 章 · 会话卡住", "先看是不是还在生成。",
                   "streaming 中的命令拒绝，常被误读成「没反应」。")
    picture.box((100, 230, 1120, 340), INK, INK, radius=10)
    picture.text((124, 252), "屏幕上只有：Working...", 20, WHITE)
    picture.text((124, 292), "先敲 Esc 或等本轮结束，不要连敲命令", 18, "#BCD5BD")
    picture.box((100, 380, 520, 560), PEACH, ORANGE, radius=10)
    picture.text((124, 402), "还在 streaming", 20, ORANGE, True)
    picture.text((124, 444), "/fresh 拒绝", 18)
    picture.text((124, 478), "/clear 拒绝（先中止压缩）", 18)
    picture.text((124, 512), "裸 /fork 警告并挡住", 18)
    picture.text((124, 546), "→ 中止本轮再试", 18, ORANGE, True)
    picture.box((560, 380, 1120, 560), SAGE, GREEN, radius=10)
    picture.text((584, 402), "真的卡死", 20, GREEN, True)
    picture.text((584, 444), "重开会话 / 换 profile 复现", 18)
    picture.text((584, 478), "带 stderr 与时间点去查", 18)
    picture.text((584, 512), "看是否与某个扩展同时出现", 18)
    picture.note((92, 590, 1108, 676), "别把「等」当成故障。",
                 "先分清生成中、压缩中、前台命令跑着——三种都会拒命令。", BLUE, SKY)
    picture.footer("卡住先看状态，再决定等还是中止。")


def trust_load(picture: Drawing):
    picture.header("第 31 章 · 信任加载", "来路不清，先冻结。",
                   "能写盘、能跑命令的，全在信任边界内。")
    picture.box((90, 230, 430, 480), PEACH, ORANGE)
    picture.text((114, 254), "来路不清的扩展", 21, ORANGE, True)
    picture.text((114, 298), "拷来的 zip", 18)
    picture.text((114, 334), "聊天里贴的工厂", 18)
    picture.text((114, 370), "陌生仓库的 .omp/", 18)
    picture.text((114, 424), "先别开会话", 19, ORANGE, True)
    picture.arrow([(440, 355), (540, 355)], ORANGE, 3)
    picture.box((552, 240, 900, 470), WHITE, INK, radius=10)
    picture.text((576, 264), "冻结动作", 21, bold=True)
    picture.text((576, 308), "读源码与文档", 18)
    picture.text((576, 344), "列工具、网络、密钥需求", 18)
    picture.text((576, 380), "来源、版本、权限三问", 18)
    picture.box((920, 260, 1120, 450), SAGE, GREEN, radius=10)
    picture.text((1020, 288), "确认", 22, GREEN, True, "mm")
    picture.text((1020, 330), "再开", 18, MUTED, anchor="mm")
    picture.text((1020, 380), "默认不信", 18, GREEN, anchor="mm")
    picture.note((92, 510, 1108, 606), "技能、MCP、钩子、扩展工厂——一样。",
                 "只要它能改磁盘或跑命令，就在边界内。", ORANGE, PEACH)
    picture.text((600, 646), "来源不明就冻结，是默认姿势", 18, MUTED, anchor="mm")
    picture.footer("装上之后再后悔，成本比先读十分钟高。")


def no_extensions(picture: Drawing):
    picture.header("第 31 章 · 无扩展复现", "先做减法，定位层。",
                   "症状消失 → 问题在扩展；仍在 → 往下查。")
    picture.box((110, 230, 1110, 300), WHITE, INK, radius=8)
    picture.text((134, 250), "症状：一开就慢 / 一开就挂 / 行为与文档不符", 19)
    picture.choice = None
    picture.box((300, 340, 900, 410), INK, INK, radius=8)
    picture.text((324, 358), "omp --no-extensions", 20, WHITE)
    picture.arrow([(470, 420), (360, 470)], ORANGE, 3)
    picture.arrow([(730, 420), (840, 470)], GREEN, 3)
    picture.box((90, 480, 620, 620), PEACH, ORANGE, radius=10)
    picture.text((114, 502), "症状消失", 20, ORANGE, True)
    picture.text((114, 544), "问题在扩展层", 18)
    picture.text((114, 580), "回第 29 章三问，逐个关", 18)
    picture.box((660, 480, 1120, 620), SAGE, GREEN, radius=10)
    picture.text((684, 502), "症状仍在", 20, GREEN, True)
    picture.text((684, 544), "查模型、鉴权、仓库本身", 18)
    picture.text((684, 580), "转第 30 章症状索引", 18)
    picture.text((600, 660), "显式 -e 路径不受 --no-extensions 影响", 18, MUTED, anchor="mm")
    picture.footer("无扩展复现是分诊，不是长期方案。")


def secrets(picture: Drawing):
    picture.header("第 31 章 · 秘密遮罩", "出模型前遮，进工具前还原。",
                   "默认关闭；secrets.enabled: true 后才生效。")
    picture.box((80, 230, 420, 330), SKY, SKY, radius=10)
    picture.text((104, 260), "原始文本", 20, BLUE, True)
    picture.text((104, 296), "OPENAI_API_KEY=sk-…", 18)
    picture.arrow([(430, 280), (520, 280)], BLUE, 3)
    picture.box((532, 230, 900, 330), SAGE, GREEN, radius=10)
    picture.text((556, 260), "遮罩后送进模型", 20, GREEN, True)
    picture.text((556, 296), "OPENAI_API_KEY=[secret:1]", 18)
    picture.arrow([(910, 280), (990, 280)], GREEN, 3)
    picture.box((1002, 230, 1120, 330), WHITE, INK, radius=10)
    picture.text((1061, 262), "模型", 19, INK, True, "mm")
    picture.arrow([(1061, 340), (1061, 410), (700, 410), (700, 470)], ORANGE, 3)
    picture.box((520, 480, 1080, 590), PEACH, ORANGE, radius=10)
    picture.text((544, 502), "工具执行前还原", 20, ORANGE, True)
    picture.text((544, 544), "可逆模式：模型给占位符，程序换回真值", 18)
    picture.note((92, 610, 1108, 690), "遮罩不是保险箱。",
                 "transcript 里仍可能有明文；分享前自己扫一遍。", BLUE, SKY)
    picture.text((360, 590), "日志与卡片仍要人工过目", 17, MUTED, anchor="mm")
    picture.footer("遮罩降低泄漏面，不替代密钥管理。")


def token_flow(picture: Drawing):
    picture.header("第 32 章 · 用量流向", "三条管子都在计费。",
                   "输入、工具结果、输出；子代理是乘数。")
    sources = (("你的提示 + 历史", ORANGE, PEACH),
               ("工具结果", BLUE, SKY),
               ("模型输出", GREEN, SAGE))
    for index, (label, color, fill) in enumerate(sources):
        left = 90 + index * 340
        picture.box((left, 230, left + 300, 340), fill, color, radius=10)
        picture.text((left + 150, 268), label, 19, color, True, "mm")
        picture.arrow([(left + 150, 350), (left + 150, 400)], color, 3)
    picture.box((90, 410, 1000, 500), INK, INK, radius=10)
    picture.text((114, 432), "上下文窗口：每一轮都要重发", 19, WHITE)
    picture.text((114, 466), "越长越贵，压缩前先救证据", 17, "#BCD5BD")
    picture.box((290, 540, 900, 620), PEACH, ORANGE, radius=8)
    picture.text((314, 558), "子代理：各自带一份上下文", 19, ORANGE, True)
    picture.text((314, 592), "开 N 个 ≈ 乘 N 份开销", 17, MUTED)
    picture.text((600, 660), "能 grep 就别整树灌；能摘要就别全文复述", 17, MUTED, anchor="mm")
    picture.footer("成本不是账单问题，是上下文卫生问题。")


def role_cost(picture: Drawing):
    picture.header("第 32 章 · 角色与成本", "杀鸡别用牛刀。",
                   "按任务挑档位，不按心情。")
    rows = (("smol", "改文案、分类、格式转换", "¥", GREEN, SAGE),
            ("default", "日常实现与调试", "¥¥", BLUE, SKY),
            ("slow", "架构争议、疑难根因", "¥¥¥", ORANGE, PEACH),
            ("plan", "跨模块方案", "¥¥¥", ORANGE, PEACH))
    for index, (role, use, cost, color, fill) in enumerate(rows):
        top = 230 + index * 96
        picture.box((100, top, 1080, top + 76), fill, color, radius=8)
        picture.text((124, top + 12), role, 21, color, True)
        picture.text((280, top + 24), use, 18)
        picture.text((1040, top + 20), cost, 20, color, True, "rt")
    picture.note((92, 630, 1108, 700), "在 todo 里标本任务角色。",
                 "结束复盘：是不是「用牛刀杀鸡」？", ORANGE, PEACH)
    picture.footer("省钱的顺序：先换档，再减上下文，最后才并行。")


def cache_compact(picture: Drawing):
    picture.header("第 32 章 · 缓存与压缩", "能缓存别重算，压缩前先救证据。",
                   "缓存键用错会失效；压缩会折叠历史。")
    picture.box((80, 230, 540, 420), SAGE, GREEN, radius=10)
    picture.text((104, 254), "提示缓存", 21, GREEN, True)
    picture.text((104, 298), "稳定前缀命中就便宜", 18)
    picture.text((104, 334), "乱插时间戳 / 随机串 → 全失效", 18, ORANGE)
    picture.text((104, 380), "缓存键旗标先读帮助再改", 18, MUTED)
    picture.box((570, 230, 1120, 420), PEACH, ORANGE, radius=10)
    picture.text((594, 254), "会话压缩", 21, ORANGE, True)
    picture.text((594, 298), "折叠旧历史为摘要", 18)
    picture.text((594, 334), "失败命令、文件:行、测试输出", 18)
    picture.text((594, 370), "先写进 todo 或仓库笔记", 18, ORANGE, True)
    picture.arrow([(600, 430), (600, 490)], INK, 3)
    picture.box((200, 500, 1000, 590), WHITE, INK, radius=8)
    picture.text((224, 520), "压缩前后的对照物：早先约定的命令、关键 diff", 18)
    picture.text((224, 556), "只活在早聊里的东西，压完就可能问不出来", 17, MUTED)
    picture.text((600, 630), "证据进文件，摘要才安全", 18, MUTED, anchor="mm")
    picture.footer("压缩是空间管理，不是记忆备份。")


def callchain(picture: Drawing):
    picture.header("第 33 章 · 调用链", "从敲命令到工具注册，一格不能断。",
                   "自检用：每格能说出入口与验证方式。")
    links = (("启动", "omp / -p"),
             ("上下文", "cwd、AGENTS"),
             ("循环", "请求 → 结果"),
             ("工具", "注册表 + 审批"),
             ("扩展", "工厂、钩子"))
    for index, (title, detail) in enumerate(links):
        left = 56 + index * 220
        picture.box((left, 260, left + 190, 420), WHITE, INK if index % 2 == 0 else ORANGE)
        picture.text((left + 95, 296), title, 20, INK, True, "mm")
        picture.text((left + 16, 350), detail, 15, anchor="mm", width=170)
        if index < 4:
            picture.arrow([(left + 196, 340), (left + 212, 340)], MUTED, 3)
    picture.note((92, 450, 1108, 540), "断格自检：", 
                 "说不出入口 → 回第 3 章；说不清上下文 → 第 14 章；说不清工具 → 第 21 章。", BLUE, SKY)
    picture.text((600, 580), "每格都配一条可复验命令，才算复习完", 18, MUTED, anchor="mm")
    picture.text((600, 620), "不写新功能，只接线路", 18, MUTED, anchor="mm")
    picture.footer("整条链能画出来，才敢说自己会了。")


def from_launch(picture: Drawing):
    picture.header("第 33 章 · 从启动出发", "同一引擎，外壳不同。",
                   "入口决定协议与生命周期，不改变能力。")
    for index, (entry, color, fill) in enumerate((("omp", ORANGE, PEACH),
                                                   ("omp -p", BLUE, SKY),
                                                   ("SDK", GREEN, SAGE),
                                                   ("omp --mode rpc", MUTED, WHITE))):
        left = 70 + index * 270
        picture.box((left, 230, left + 240, 320), fill, color, radius=10)
        picture.text((left + 120, 275), entry, 21, color, True, "mm")
        picture.arrow([(left + 120, 330), (left + 120, 390)], color, 3)
    picture.box((250, 400, 950, 520), SAGE, GREEN, radius=12)
    picture.text((600, 430), "同一套运行时", 23, GREEN, True, "mm")
    picture.text((600, 470), "上下文、工具、模型路由、审批", 18, anchor="mm")
    picture.text((600, 500), "差别只在谁持有进程与输出", 17, MUTED, anchor="mm")
    picture.note((92, 550, 1108, 640), "选入口看谁持有生命周期。",
                 "人用 TUI；脚本用 -p；宿主程序自己管进程，才用 SDK/RPC。", ORANGE, PEACH)
    picture.text((600, 676), "外壳换了，行为契约不换", 18, MUTED, anchor="mm")
    picture.footer("先定外壳，再谈参数；顺序反了会多写一堆胶水。")


def pin_version(picture: Drawing):
    picture.header("附录 E · 钉住版本", "写作版本与本机版本，都写下来。",
                   "两者不一致时，以本机二进制为准并记页边。")
    picture.box((100, 250, 520, 430), WHITE, INK, radius=10)
    picture.text((124, 274), "写作钉", 21, bold=True)
    picture.text((124, 320), "omp/18.15.0", 24, ORANGE, True)
    picture.text((124, 366), "正文技术叙述的依据", 17, MUTED)
    picture.box((600, 250, 1020, 430), WHITE, INK, radius=10)
    picture.text((624, 274), "本机验证", 21, bold=True)
    picture.text((624, 320), "omp --version → omp/18.16.0", 19, GREEN, True)
    picture.text((624, 366), "实际跑过才算，写日期与形态", 17, MUTED)
    picture.text((560, 340), "≠", 34, ORANGE, True, "mm")
    picture.note((92, 470, 1108, 560), "冲突时以现场为准。",
                 "帮助与行为优先；差异回流页边，不是改掉记录。", BLUE, SKY)
    picture.text((600, 600), "三者：本书钉、本机字符串、扩展兼容范围", 18, MUTED, anchor="mm")
    picture.text((600, 640), "都要有出处", 18, MUTED, anchor="mm")
    picture.footer("版本是时间戳，不是装饰。")


def docs_vs_bin(picture: Drawing):
    picture.header("附录 E · 文档与二进制", "冲突时，现场优先。",
                   "再看文档理解为什么漂移，最后记页边。")
    picture.box((80, 240, 500, 420), SKY, BLUE)
    picture.text((104, 264), "文档", 21, BLUE, True)
    picture.text((104, 306), "写作钉的出处", 18)
    picture.text((104, 342), "可能过期", 18, MUTED)
    picture.box((640, 240, 1120, 420), SAGE, GREEN)
    picture.text((664, 264), "本机二进制", 21, GREEN, True)
    picture.text((664, 306), "omp --help / 实际行为", 18)
    picture.text((664, 342), "冲突时的裁判", 18, GREEN, True)
    picture.arrow([(510, 300), (630, 300)], ORANGE, 3)
    picture.arrow([(630, 360), (510, 360)], MUTED, 2)
    picture.text((570, 330), "对照", 16, MUTED, anchor="mm")
    picture.box((200, 470, 1000, 560), WHITE, INK, radius=8)
    picture.text((224, 490), "差异写法：本机有/无某某；日期；版本字符串", 18)
    picture.text((224, 526), "挑附录 A 任一旗标即可练", 17, MUTED)
    picture.text((600, 620), "不把猜测写成已验证", 18, MUTED, anchor="mm")
    picture.footer("文档给方向，二进制给事实。")


def margin_notes(picture: Drawing):
    picture.header("附录 E · 页边核对", "记差异与命令，不记课外作业。",
                   "字段固定，证据落到路径。")
    fields = ("日期与时区", "写作版本 / 本机版本", "安装形态",
              "差异摘要", "复验命令 + 退出码", "证据位置 / 是否反馈上游")
    for index, label in enumerate(fields):
        top = 230 + index * 66
        picture.box((100, top, 760, top + 50), WHITE, LINE, radius=6)
        picture.text((124, top + 12), f"{index + 1}. {label}", 18)
    picture.box((800, 230, 1120, 560), SAGE, GREEN, radius=10)
    picture.text((824, 254), "示例", 20, GREEN, True)
    picture.text((824, 296), "2026-11-05 UTC", 17)
    picture.text((824, 330), "v18.15.0 / v18.16.0", 17)
    picture.text((824, 364), "Windows · Bun 全局", 17)
    picture.text((824, 398), "flag 存在差异", 17)
    picture.text((824, 432), "omp --help → exit 0", 17)
    picture.text((824, 466), "facts/live-…", 17)
    picture.text((600, 600), "观察写实，推测标推测", 18, MUTED, anchor="mm")
    picture.footer("页边是给下一次升级的自己留的线索。")



def flag_layers(picture: Drawing):
    picture.header("附录 A · 旗标分层", "位置参数先问「是不是子命令」，再问「去哪」。",
                   "launch 旗标、子命令旗标与裸词提示词，各走各的门。")
    picture.box((58, 208, 400, 320), PEACH, ORANGE)
    picture.text((229, 232), "第一位置参数", 24, ORANGE, True, "mm")
    picture.text((229, 272), 'omp "修一下构建"', 20, MUTED, anchor="mm")
    picture.text((229, 300), "不是已注册子命令", 18, MUTED, anchor="mm")
    picture.box((58, 340, 400, 452), SKY, BLUE)
    picture.text((229, 364), "是子命令名", 24, BLUE, True, "mm")
    picture.text((229, 404), "omp models / omp commit", 19, MUTED, anchor="mm")
    picture.text((229, 432), "走该命令自己的旗标集", 18, MUTED, anchor="mm")
    picture.arrow([(410, 264), (500, 264)], ORANGE)
    picture.arrow([(410, 396), (500, 396)], BLUE)
    picture.box((510, 208, 1140, 452), WHITE, LINE)
    picture.text((540, 232), "两级路由", 24, INK, True)
    for index, (title, detail, color) in enumerate((
            ("默认 launch", "进交互或 print；launch 旗标在此有效", ORANGE),
            ("子命令", "omp <command> --help 是该命令的公开面", BLUE),
            ("裸词", "omp launch <word> 才把词当提示词", GREEN))):
        top = 274 + index * 56
        picture.circle((556, top + 12), 8, color, color)
        picture.text((578, top), title, 21, color, True)
        picture.text((578, top + 26), detail, 18, MUTED)
    picture.note((92, 488, 1108, 588), "只有 launch 的旗标跑到别的子命令前，",
                 "可能被剥掉而不生效——文档例子：omp --cwd dir update。", BLUE, SKY)
    picture.footer("先分类，再记旗标；分类错了，背再多旗标也没用。")


def binary_probe(picture: Drawing):
    picture.header("附录 A · 帮助漏列", "帮助是摘要，二进制才是判官。",
                   "旗标没印在 --help 里，未必不被解析。")
    picture.paper((58, 206, 566, 452), "omp --help 的正文", BLUE, WHITE, ruled=False)
    picture.text((80, 252), "常见 launch 旗标与子命令表", 20, MUTED)
    picture.text((80, 292), "— 没列 --fork", 21, ORANGE, True)
    picture.text((80, 328), "— 没列 --session", 21, ORANGE, True)
    picture.text((80, 364), "— 没列 --trusted-extension", 21, ORANGE, True)
    picture.text((80, 408), "不等于「不认识」", 19, MUTED)
    picture.arrow([(578, 330), (660, 330)], ORANGE)
    picture.paper((672, 206, 1140, 452), "缺值探针", GREEN, WHITE, ruled=False)
    picture.text((694, 252), "给一个不该给的值，读报错", 20, GREEN, True)
    picture.text((694, 300), "omp --trusted-extension 2>&1", 19, MUTED)
    picture.text((694, 338), "未知旗标 → unrecognized", 18, MUTED)
    picture.text((694, 374), "已知旗标 → 要值 / 走下一步", 18, MUTED)
    picture.note((92, 486, 1108, 620), "三处对齐再下结论：",
                 "帮助摘要、docs/cli-reference.md、二进制实际解析。"
                 "三者冲突时，以你本机跑出来的行为为准。", GREEN, SAGE)
    picture.footer("帮助列不全不是 bug 的证据，也不是「不存在」的证据。")


def slash_vs_flag(picture: Drawing):
    picture.header("附录 B · 分工", "同一件事，两条入口。",
                   "脚本里写旗标，人手里敲斜杠；不要求同名。")
    picture.box((58, 214, 578, 620), SKY, BLUE)
    picture.text((318, 244), "会话内：斜杠命令", 26, BLUE, True, "mm")
    picture.terminal((86, 296, 550, 430), "续聊上一会话", True, "> /resume")
    picture.text((318, 460), "住在 TUI 输入框里", 21, MUTED, anchor="mm")
    picture.text((318, 500), "随版本、主题、扩展变化", 20, MUTED, anchor="mm")
    picture.text((318, 556), "补全 / 帮助优先", 20, BLUE, True, "mm")
    picture.box((622, 214, 1142, 620), SAGE, GREEN)
    picture.text((882, 244), "shell 里：旗标", 26, GREEN, True, "mm")
    picture.terminal((650, 296, 1114, 430), "同样的续聊，退出码可判", True,
                     "> omp --continue")
    picture.text((882, 460), "写在命令行上，可进脚本", 21, MUTED, anchor="mm")
    picture.text((882, 500), "--continue / --resume / --restore", 19, MUTED,
                 anchor="mm")
    picture.text((882, 556), "CI 与自动化更稳", 20, GREEN, True, "mm")
    picture.note((92, 640, 1108, 706), "不对称是常态：",
                 "别假设每条斜杠都有同名旗标，也别在脚本里赌 TUI 补全。", BLUE, SKY)
    picture.footer("一次意图，两条入口——按「谁在按」来选，不按记性来选。")


def slash_not_shell(picture: Drawing):
    picture.header("附录 B · 不报错的错", "敲错位置不报错，只把整句喂给模型。",
                   "shell 里没有 /memory、/mcp 这类会话内命令。")
    picture.terminal((58, 210, 1140, 470), "Working...", False,
                     "> omp /memory view")
    picture.arrow([(600, 480), (600, 526)], ORANGE)
    picture.box((58, 536, 560, 660), PEACH, ORANGE)
    picture.text((309, 560), "以为：命令没找到", 22, ORANGE, True, "mm")
    picture.text((309, 606), "实际：进了默认 launch", 20, MUTED, anchor="mm")
    picture.text((309, 634), "整句当提示词", 20, MUTED, anchor="mm")
    picture.box((640, 536, 1140, 660), SAGE, GREEN)
    picture.text((890, 560), "正确探法", 22, GREEN, True, "mm")
    picture.text((890, 606), "omp --help 数 COMMANDS", 20, MUTED, anchor="mm")
    picture.text((890, 634), "斜杠只在会话内", 20, MUTED, anchor="mm")
    picture.footer("「没报错」不等于「跑对了」：先确认自己在哪一层。")


def config_stack(picture: Drawing):
    picture.header("附录 C · 哪一层生效", "从上往下找，找到第一顶戴着的帽子。",
                   "改完只用最小会话验证一个键，别一次改十二个。")
    layers = (("--profile / OMP_PROFILE", "命名配置档：隔离鉴权、会话、设置、缓存", ORANGE, PEACH),
              ("--cwd / 项目目录", "决定相对路径与项目级 .omp/ 的落点", BLUE, SKY),
              ("--config <file>", "额外覆盖层，可重复，用于临时试法", GREEN, SAGE),
              ("最小会话验证", "只验一个键，确认生效再继续改", MUTED, WHITE))
    for index, (title, detail, color, fill) in enumerate(layers):
        top = 210 + index * 106
        picture.box((200, top, 1000, top + 86), fill, color)
        picture.text((228, top + 14), title, 24, color, True)
        picture.text((228, top + 48), detail, 19, MUTED)
        if index:
            picture.arrow([(600, top - 14), (600, top - 2)], LINE, 3)
    picture.text((70, 384), "先问顺序，", 21, MUTED, True)
    picture.text((70, 412), "再问键名", 21, MUTED)
    picture.note((92, 646, 1108, 706), "配置分散在：",
                 "config.yml、项目 .omp/、环境变量、secrets.yml、LSP 配置——完整键名以帮助与文档为准。",
                 BLUE, SKY)
    picture.footer("先定位生效层，再谈值对不对；层搞错，改的是没人读的那份。")


def secrets_paths(picture: Drawing):
    picture.header("附录 C · secrets 放哪", "全局一份，项目一份，后者压前者。",
                   "命名 profile 与 SDK 的 agentDir 都会改写「全局」的位置。")
    picture.paper((58, 208, 566, 470), "全局", BLUE, WHITE, ruled=False)
    picture.text((80, 252), "~/.omp/agent/secrets.yml", 20, BLUE, True)
    picture.text((80, 296), "跨项目共用", 20, MUTED)
    picture.text((80, 336), "跟随活动 agent 目录", 19, MUTED)
    picture.text((80, 372), "profile / agentDir 一改，", 19, ORANGE)
    picture.text((80, 398), "它就换地方", 19, ORANGE)
    picture.plus = None
    picture.text((600, 330), "→", 46, MUTED, True, "mm")
    picture.paper((632, 208, 1140, 470), "项目", GREEN, WHITE, ruled=False)
    picture.text((654, 252), "<cwd>/.omp/secrets.yml", 20, GREEN, True)
    picture.text((654, 296), "只服务本仓库", 20, MUTED)
    picture.text((654, 336), "按 content 覆盖全局", 19, MUTED)
    picture.text((654, 372), "所以别把明文密钥", 19, ORANGE)
    picture.text((654, 398), "提交进仓库", 19, ORANGE)
    picture.note((92, 496, 1108, 600), "开关在 config.yml：",
                 "secrets.enabled 为 true 才谈遮罩；两种模式见第 31 章（obfuscate 可逆 / replace 不可逆）。",
                 GREEN, SAGE)
    picture.footer("路径先看清，再谈遮罩；写错文件，等于没开。")


def glossary_rings(picture: Drawing):
    picture.header("附录 D · 术语分环", "先记环，再记词。",
                   "一个词属于哪一环，决定它跟谁容易混。")
    center = (600, 420)
    rings = ((250, "产品与界面", ORANGE, PEACH),
             (180, "会话与配置", BLUE, SKY),
             (110, "代理循环与工具", GREEN, SAGE))
    for radius, label, color, fill in rings:
        picture.circle(center, radius, fill, color, 4)
    picture.circle(center, 44, WHITE, INK, 3)
    picture.text((600, 420), "omp", 24, INK, True, "mm")
    picture.text((600, 106), "产品与界面", 21, ORANGE, True, "mm")
    picture.text((600, 176), "会话与配置", 20, BLUE, True, "mm")
    picture.text((600, 246), "循环与工具", 20, GREEN, True, "mm")
    picture.text((600, 710), "扩展与安全、嵌入、魔法词各自成环：先记环名，再记环里的词。",
                 19, MUTED, anchor="mm")
    picture.footer("术语表的用法是默写后对答案，不是从头读到尾。")


def confusable_pairs(picture: Drawing):
    picture.header("附录 D · 易混对", "成对记，比单词记牢。",
                   "默写时专门练这几对。")
    pairs = (("斜杠命令", "魔法词", "你下的命令 / 提示词里的倾向"),
             ("profile", "cwd", "一顶帽子 / 一个站位"),
             ("obfuscate", "replace", "可逆 / 不可逆"),
             ("SDK", "RPC", "同进程 / 跨进程"),
             ("RPC", "ACP", "自定义 JSONL / JSON-RPC over stdio"),
             ("task", "orchestrate", "委派 / 鼓励并行的魔法倾向"))
    for index, (left, right, why) in enumerate(pairs):
        column, row = divmod(index, 3)
        top = 206 + row * 158
        left_x = 58 + column * 552
        picture.box((left_x, top, left_x + 520, top + 132), WHITE, LINE)
        picture.text((left_x + 24, top + 18), left, 24, ORANGE, True)
        picture.text((left_x + 250, top + 18), right, 24, BLUE, True)
        picture.line([(left_x + 222, top + 22), (left_x + 222, top + 50)], LINE, 2)
        picture.line([(left_x + 24, top + 66), (left_x + 496, top + 66)], LINE, 1)
        picture.text((left_x + 24, top + 84), why, 19, MUTED, width=472)
    picture.footer("练易混对比背孤立定义省力：错一次，记住的是一对。")


def discovery_ladder(picture: Drawing):
    picture.header("第 14 章 · 发现优先级", "同层只活一个，跨层各活一份。",
                   "数字是文档给的发现优先级：native 最高，原生文件赢在起点。")
    rows = (("native", 100, ORANGE), ("omp-plugins", 90, ORANGE),
            ("claude", 80, BLUE), ("agent-plugins", 75, BLUE),
            ("agents / codex", 70, BLUE), ("gemini", 60, GREEN),
            ("opencode", 55, GREEN), ("cursor / windsurf", 50, GREEN),
            ("cline", 40, GREEN), ("github", 30, MUTED),
            ("vscode", 20, MUTED), ("agents-md / claude-md", 10, MUTED))
    for index, (name, score, color) in enumerate(rows):
        column, row = divmod(index, 6)
        left = 58 + column * 552
        top = 212 + row * 66
        width = int(score * 3.4)
        picture.box((left, top, left + max(width, 30), top + 48), WHITE, color, radius=8)
        picture.text((left + 12, top + 12), name, 19, INK)
        picture.text((left + 470, top + 12), str(score), 19, color, True, "rm")
    picture.note((92, 620, 1108, 700), "记两条就够：",
                 "用户级只留一份（native 遮住其他用户级）；项目级按目录深度，每层一份，越靠近 cwd 越显眼。",
                 BLUE, SKY)
    picture.footer("调试「怎么还念旧规矩」：先看 cwd 与最近非空 .omp/，再看 enabledProviders。")


def role_layers(picture: Drawing):
    picture.header("第 17 章 · 谁压住谁", "从下往上找，最后说话的那层赢。",
                   "改的那层不是生效的那层，是角色路由最常见的坑。")
    layers = (("setting env var", "PI_SMOL_MODEL / PI_SLOW_MODEL / PI_PLAN_MODEL", ORANGE),
              ("runtime overrides", "--smol / --slow / --plan（不落盘）", ORANGE),
              ("CLI overlays", "--config <file>", BLUE),
              ("project config", "<cwd>/.omp/config.yml", GREEN),
              ("global config", "~/.omp/agent/config.yml", GREEN),
              ("built-in defaults", "出厂值", MUTED))
    for index, (title, detail, color) in enumerate(layers):
        top = 640 - index * 82
        picture.box((200, top, 1000, top + 64), WHITE, color, radius=8)
        picture.text((226, top + 8), title, 22, color, True)
        picture.text((226, top + 36), detail, 18, MUTED)
    picture.arrow([(150, 690), (150, 200)], MUTED, 4)
    picture.text((112, 440), "优先级升高", 19, MUTED, anchor="mm")
    picture.note((92, 470, 1108, 470), "", "")
    picture.footer("modelRoleStorage 决定 /model 里的指派写到哪一层；本机默认为 global。")


def rebuild_order(picture: Drawing):
    picture.header("第 15 章 · 上下文怎么重新拼出来", "buildSessionContext 按固定顺序拼五段。",
                   "模型看到的不是你屏幕上的全文，而是这五段按序拼起来的结果。")
    steps = (("最新那条 compaction", "活动路径上只取最新的一条，转成一条摘要消息", ORANGE),
             ("firstKeptEntryId 之后的保留条目", "从边界到压缩点的原文重新放回", ORANGE),
             ("压缩点之后的条目", "路径上更晚的条目按原样追加", BLUE),
             ("branch_summary", "转成分支摘要消息；本机默认 false，不生成", GREEN),
             ("custom_message", "转成自定义消息", GREEN))
    for index, (title, detail, color) in enumerate(steps):
        top = 198 + index * 84
        picture.box((110, top, 1108, top + 68), WHITE, color, radius=10)
        picture.badge((142, top + 34), index + 1, color)
        picture.text((182, top + 12), title, 23, color, True, width=900)
        picture.text((182, top + 42), detail, 19, MUTED, width=900)
    picture.note((92, 622, 1108, 702), "最后一步容易看漏：",
                 "convertToLlm() 把两类摘要都变成 user 消息、套静态模板——读起来像你口述的背景。",
                 BLUE, SKY)
    picture.footer("关键约定别只活在会被压掉的闲聊里：写进 RULES.md、记忆或仓库文件。")


def memory_urls(picture: Drawing):
    picture.header("第 16 章 · memory:// 读得到什么", "URL 形态固定，能不能解析看 backend。",
                   "根 URL 主要在 local backend 下成立；别在别的 backend 下假想它可读。")
    rows = (("memory://root", "启动注入的紧凑摘要"),
            ("memory://root/MEMORY.md", "长期记忆全文"),
            ("memory://root/learned.md", "learn 捕获的 lessons"),
            ("memory://root/skills/<name>/SKILL.md", "生成的 skill 剧本"),
            ("memory://<memory-id>", "Mnemopi 整行（仅 mnemopi）"))
    picture.text((60, 196), "read 能吃的 URL", 23, INK, True, width=380)
    for index, (url, meaning) in enumerate(rows):
        top = 230 + index * 76
        picture.box((60, top, 690, top + 62), WHITE, BLUE, radius=8)
        picture.text((78, top + 10), url, 19, INK, width=594)
        picture.text((78, top + 36), meaning, 18, MUTED, width=594)
    picture.text((726, 196), "根 URL 解析得了吗", 23, INK, True, width=400)
    cards = (("local", "根 URL 成立", "合并管线把文件写到 memory://root/...", GREEN),
             ("hindsight / mnemopi", "根 URL 可能不解析", "改用 recall / reflect；mnemopi 还能按 id 读", ORANGE),
             ("off", "没有记忆工具面", "连注入都不发生", MUTED))
    for index, (name, verdict, detail, color) in enumerate(cards):
        top = 230 + index * 128
        picture.box((726, top, 1140, top + 110), WHITE, color, radius=10)
        picture.text((748, top + 12), name, 21, color, True, width=370)
        picture.text((748, top + 42), verdict, 19, INK, width=370)
        picture.text((748, top + 72), detail, 17, MUTED, width=370)
    picture.footer("本机 mnemopi 下 omp read memory://root 退出码 1，并直说当前 backend——比让模型猜快。")


def keyword_switches(picture: Drawing):
    picture.header("第 18 章 · 四个词各自要什么", "词认出来了，不等于它能干活。",
                   "三个词依赖工具开关；关着的时候注入照发，契约却落不了地。")
    cards = (("ultrathink", "多步谨慎推理说明", "不需要额外工具",
              "自动 thinking 开着时，该回合拉到模型最高推理强度", ORANGE),
             ("orchestrate", "多代理编排契约", "需要 task 启用",
              "划界、并行委派、分阶段验证，直到完成", BLUE),
             ("workflowz", "确定性多子代理工作流", "需要 eval 与 task",
              "围绕持久 eval 内核的 agent() / completion() / wait()", GREEN),
             ("jevify", "批量判定契约", "需要 eval 启用",
              "先冻结问题与量规，再 judge() 一批，只精读打标项", GREEN))
    for index, (word, effect, need, detail, color) in enumerate(cards):
        column, row = divmod(index, 2)
        left = 64 + column * 548
        top = 200 + row * 212
        picture.box((left, top, left + 524, top + 184), WHITE, color, radius=12)
        picture.text((left + 24, top + 16), word, 27, color, True, width=476)
        picture.text((left + 24, top + 56), effect, 20, INK, width=476)
        picture.box((left + 24, top + 88, left + 290, top + 124), WHITE, color, radius=8)
        picture.text((left + 38, top + 97), need, 18, color, True, width=238)
        picture.text((left + 24, top + 136), detail, 17, MUTED, width=476)
    picture.note((92, 630, 1108, 700), "匹配只认全小写独立散文词：",
                 "orchestrated、orchestrate.ts、orchestrate() 都不触发；"
                 "围栏与行内代码里的同名字符串也不算。", BLUE, SKY)
    picture.footer("只影响含该词的那一回合；合成的、agent 发起的提示不触发。")


def skill_triage(picture: Drawing):
    picture.header("第 19 章 · 技能不露面，五步排查",
                   "从路径到生效时机，按序查，别跳。",
                   "路径不对，后面全白查。")
    steps = (("① 路径深度", "常规根只认 skills/<name>/SKILL.md 一层，嵌套不递归", ORANGE),
             ("② frontmatter", "name 齐；description 为空等于没写", BLUE),
             ("③ 开关", "skills.enabled、--no-skills、ignoredSkills、includeSkills", GREEN),
             ("④ 遮蔽", "用户级与项目级重名：capability 去重按 provider 优先级", ORANGE),
             ("⑤ 生效时机", "改完要重开会话；会话内不会热加载", BLUE))
    for index, (title, detail, color) in enumerate(steps):
        top = 196 + index * 84
        picture.box((110, top, 1108, top + 68), WHITE, color, radius=10)
        picture.badge((142, top + 34), index + 1, color)
        picture.text((182, top + 12), title, 23, color, True, width=880)
        picture.text((182, top + 42), detail, 18, MUTED, width=880)
    picture.footer("每一步都能自己复现；别用 omp read skill:// 判断项目技能。")


def mcp_precedence(picture: Drawing):
    picture.header("第 20 章 · 谁覆盖谁",
                   "MCP 配置的失败多是「键被更强的键吃掉」。",
                   "按这张梯子从上往下查，第一个命中的就是答案。")
    layers = (("disabledServers", "黑名单；连 enabledServers 强开也赢不了它", ORANGE),
              ("enabledServers", "白名单，强行打开同名条目", BLUE),
              ("条目 enabled: false", "整个 server 被跳过，工具一并消失", GREEN))
    for index, (name, detail, color) in enumerate(layers):
        top = 216 + index * 128
        picture.box((150, top, 1108, top + 100), WHITE, color, radius=10)
        picture.text((178, top + 14), name, 22, color, True, width=900)
        picture.text((178, top + 52), detail, 18, MUTED, width=900)
        if index < 2:
            picture.arrow([(104, top + 100), (104, top + 128)])
    picture.text((96, 206), "覆盖 ↓", 20, MUTED, True)
    picture.note((92, 626, 1108, 704), "另一条独立的轴（文档所述，本机未验证）：",
                 "OMP_MCP_TIMEOUT_MS 只压 per-server timeout 优先权，与可见性无关。",
                 BLUE, SKY)
    picture.footer("排障顺序：先黑名单，再白名单，最后才轮到条目自己。")


def hook_returns(picture: Drawing):
    picture.header("第 21 章 · tool_call 处理器的两种返回",
                   "拦下来，还是改了再放行。",
                   "同一个处理器按条件二选一，返回值就是契约。")
    picture.text((92, 190), "pi.on(\"tool_call\", ...) 之前/之后各挂一道", 22, INK, True, width=976)
    picture.box((92, 240, 584, 480), WHITE, ORANGE, radius=12)
    picture.text((116, 264), "{ block: true,", 24, ORANGE, True, width=444)
    picture.text((116, 296), "  reason: \"...\" }", 24, ORANGE, True, width=444)
    picture.text((116, 340), "调用被拦", 22, INK, True, width=444)
    picture.text((116, 376), "模型只会看到 reason，", 18, MUTED, width=444)
    picture.text((116, 404), "拿不到工具结果。", 18, MUTED, width=444)
    picture.box((616, 240, 1108, 480), WHITE, BLUE, radius=12)
    picture.text((640, 264), "{ input: {...} }", 24, BLUE, True, width=444)
    picture.text((640, 340), "参数被改写", 22, INK, True, width=444)
    picture.text((640, 376), "真正执行的是新参数，", 18, MUTED, width=444)
    picture.text((640, 404), "原调用悄悄被替换。", 18, MUTED, width=444)
    picture.note((92, 508, 1108, 588), "用在刀刃上：",
                 "审计、改写参数、阻止危险调用；审批门禁是另一道，两者叠加时都要过。",
                 GREEN, SAGE)
    picture.footer("钩子失败要吵出来：静默的 block 比报错难查十倍。")


def registerables(picture: Drawing):
    picture.header("第 22 章 · 扩展能注册什么",
                   "六类能力，名称以当前 ExtensionAPI 为准。",
                   "升级后先对照类型定义，别背旧清单。")
    cards = (("pi.on(...)", "事件：session / agent / tool 生命周期", ORANGE),
             ("pi.registerTool", "工具：模型可调用", BLUE),
             ("pi.registerCommand", "斜杠命令", GREEN),
             ("快捷键与旗标", "交互入口也归扩展管", BLUE),
             ("自定义渲染", "界面表现层", GREEN),
             ("sendMessage 注入", "initialize 后向会话投递消息", ORANGE))
    for index, (name, detail, color) in enumerate(cards):
        column, row = divmod(index, 2)
        left = 92 + column * 516
        top = 196 + row * 148
        picture.box((left, top, left + 492, top + 124), WHITE, color, radius=12)
        picture.text((left + 22, top + 14), name, 22, color, True, width=448)
        picture.text((left + 22, top + 56), detail, 18, MUTED, width=448)
    picture.note((92, 626, 1108, 704), "时机差异：",
                 "pi.exec() 在 load 阶段就可用；provider 注册可能排队到 session setup。",
                 BLUE, SKY)
    picture.footer("模型调不到 = registerTool 没生效；斜杠没有 = registerCommand 没生效。")


def count_ledger(picture: Drawing):
    picture.header("第 26 章 · 旧名对账",
                   "before 与 after 的计数相减，要等于迁移条数。",
                   "对不上不合并——数字比肉眼扫 diff 靠谱。")
    picture.box((92, 200, 584, 356), WHITE, ORANGE, radius=10)
    picture.text((116, 216), "before.txt", 21, ORANGE, True, width=444)
    picture.text((116, 256), "$ omp grep -c calcFee omp/", 18, INK, width=444)
    picture.text((116, 288), "Total matches: 200", 18, INK, width=444)
    picture.text((116, 320), "Files searched: 1", 18, MUTED, width=444)
    picture.box((616, 200, 1108, 356), WHITE, BLUE, radius=10)
    picture.text((640, 216), "after.txt", 21, BLUE, True, width=444)
    picture.text((640, 256), "$ omp grep -c calcFee omp/", 18, INK, width=444)
    picture.text((640, 288), "Total matches: 0", 18, INK, width=444)
    picture.text((640, 320), "Files searched: 1", 18, MUTED, width=444)
    picture.box((92, 396, 1108, 500), WHITE, GREEN, radius=10)
    picture.text((116, 412), "对账规则", 21, GREEN, True, width=968)
    picture.text((116, 448), "200 − 0 = 200 = 计划迁移条数；对不上先查 Files searched 与 Gitignore。",
                 19, INK, width=968)
    picture.note((92, 528, 1108, 608), "数数只用 -c：",
                 "-f 报的是被上限截断的行数，还带 Limit reached: true——不是匹配次数。",
                 ORANGE, PEACH)
    picture.footer("Files searched 是 0 或 1？路径或 glob 写错，不是「仓库里没有旧名」。")


def review_replies(picture: Drawing):
    picture.header("第 27 章 · 被退回后的三种回法",
                   "不要先解释——先归类，再动手。",
                   "共同点：每条回复都带一个可执行命令或文件路径。")
    replies = (("范围太大", "拆提交，或把无关文件移出暂存；回复只写一句：已拆成 N 个提交", ORANGE),
               ("证据不足", "补三样：测试命令原文与末 20 行、复现步骤、改动前后对比", BLUE),
               ("方案被质疑", "回 ask，把两个方案的成本写成两行（改动面、回滚代价），让人选", GREEN))
    for index, (title, detail, color) in enumerate(replies):
        top = 200 + index * 128
        picture.box((110, top, 1108, top + 104), WHITE, color, radius=12)
        picture.badge((144, top + 52), index + 1, color)
        picture.text((186, top + 16), title, 24, color, True, width=880)
        picture.text((186, top + 58), detail, 19, MUTED, width=880)
    picture.note((92, 600, 1108, 680), "反面清单：",
                 "「我本地试过了」不算证据；评论区打三轮字，比约十分钟会议更贵。",
                 ORANGE, PEACH)
    picture.footer("没有命令或路径的回复，等于没回。")


def sdk_lifecycle(picture: Drawing):
    picture.header("第 28 章 · 进程生命周期归宿主",
                   "导入 SDK 不会替你装信号与致命错误处理器。",
                   "把下面四件事写进宿主，再谈提问。")
    duties = (("信号处理器", "SIGINT / SIGTERM 由宿主接，SDK 不代劳", ORANGE),
              ("致命错误处理器", "未捕获异常不让进程半死", BLUE),
              ("释放会话", "关机前先关会话，别留悬挂句柄", GREEN),
              ("postmortem.cleanup()", "释放会话后再调，清理才完整", ORANGE))
    for index, (title, detail, color) in enumerate(duties):
        column, row = divmod(index, 2)
        left = 92 + column * 516
        top = 210 + row * 176
        picture.box((left, top, left + 492, top + 152), WHITE, color, radius=12)
        picture.text((left + 22, top + 16), title, 23, color, True, width=448)
        picture.text((left + 22, top + 60), detail, 19, MUTED, width=448)
    picture.note((92, 574, 1108, 668), "为什么要单列：",
                 "这两样缺失时，进程会在「看起来正常」的状态下挂住或半死——比报错更难查。",
                 BLUE, SKY)
    picture.footer("SDK 最小闭环之后立刻补生命周期，再往业务里接。")


def pack_three_layers(picture: Drawing):
    picture.header("第 29 章 · 装完不生效，三层分开看",
                   "从下往上查：装没装上 → 坏没坏 → 配置读没读。",
                   "第三层最容易冤枉插件。")
    layers = (("① 装没装上", "omp plugin list：npm / Marketplace 两段，名字不在就是没装", ORANGE),
              ("② 装上了但坏了", "omp plugin doctor：逐项打勾，指出哪一项坏，不替你修", BLUE),
              ("③ 配置没生效", "mcp.enableProjectConfig 默认 false——.omp/mcp.json 不被读", GREEN))
    for index, (title, detail, color) in enumerate(layers):
        top = 200 + index * 132
        picture.box((110, top, 1108, top + 108), WHITE, color, radius=12)
        picture.text((136, top + 14), title, 24, color, True, width=920)
        picture.text((136, top + 58), detail, 19, MUTED, width=920)
        if index < 2:
            picture.arrow([(104, top + 108), (104, top + 132)], MUTED, 3)
    picture.note((92, 610, 1108, 690), "证据都是只读的：",
                 "plugin-list / plugin-doctor / config-get 三份输出贴进变更单，比口述可靠。",
                 GREEN, SAGE)
    picture.footer("团队包 README 必须写清第三层默认值，否则每个同事各踩一遍。")


def evidence_pack(picture: Drawing):
    picture.header("第 30 章 · 四行证据包",
                   "排障的第一产物不是结论，是可转发的四行。",
                   "四条都只读、不耗 API；跑完存页边。")
    commands = (("omp --version", "版本字符串", ORANGE),
                ("omp ps --json", "当前项目与 daemon 目录", BLUE),
                ("omp config get secrets.enabled", "遮罩开关（本机回 false）", GREEN),
                ("omp plugin doctor", "末尾 Summary：ok / warnings / errors", ORANGE))
    for index, (command, detail, color) in enumerate(commands):
        top = 196 + index * 96
        picture.box((92, top, 1108, top + 76), WHITE, color, radius=10)
        picture.text((116, top + 10), command, 21, color, True, width=560)
        picture.text((700, top + 12), detail, 18, MUTED, width=392)
    picture.note((92, 590, 1108, 684), "再补一条（第 28 章）：",
                 "RPC get_state 只读返回 isSettled——「卡在 Working」时用它判断还有没有未完成轮次。",
                 BLUE, SKY)
    picture.footer("读得出具体数字，才算把「好像没事」变成证据。")


def secret_modes(picture: Drawing):
    picture.header("第 31 章 · 秘密遮罩的两种模式",
                   "默认关闭；开启后有两种换法。",
                   "先把 secrets.enabled 打开，再选模式。")
    picture.box((92, 196, 584, 420), WHITE, GREEN, radius=12)
    picture.text((116, 212), "obfuscate（默认）", 23, GREEN, True, width=444)
    picture.text((116, 256), "换成确定性 $$HASH(:hint)$$ 或友好占位", 18, MUTED, width=444)
    picture.text((116, 292), "可逆：工具参数执行前还原", 18, MUTED, width=444)
    picture.text((116, 328), "短于 8 字符的普通值与正则匹配忽略", 18, MUTED, width=444)
    picture.box((616, 196, 1108, 420), WHITE, ORANGE, radius=12)
    picture.text((640, 212), "replace", 23, ORANGE, True, width=444)
    picture.text((640, 256), "换成配置的 replacement", 18, MUTED, width=444)
    picture.text((640, 292), "不可逆：适合红线值", 18, MUTED, width=444)
    picture.text((640, 328), "可处理短值", 18, MUTED, width=444)
    picture.note((92, 460, 1108, 556), "覆盖范围要点：",
                 "送模型的对话文本等字段会被替换；静态系统提示、静态工具定义、二进制载荷不在范围内。",
                 BLUE, SKY)
    picture.footer("本机默认 secrets.enabled=false——不开就没有遮罩，别把默认当保护。")


def cost_leaks(picture: Drawing):
    picture.header("第 32 章 · 钱从哪流走",
                   "五个常见黑洞，先堵最容易的。",
                   "省钱先省上下文，再谈换模型。")
    leaks = (("超长重试", ORANGE), ("整树列表灌进上下文", BLUE),
             ("并行子代理各带大历史", GREEN), ("慢角色做简单活", ORANGE),
             ("反复全仓测试不缓存", BLUE))
    for index, (label, color) in enumerate(leaks):
        top = 196 + index * 76
        picture.box((92, top, 620, top + 60), WHITE, color, radius=10)
        picture.badge((124, top + 30), index + 1, color)
        picture.text((166, top + 14), label, 21, color, True, width=430)
    picture.box((652, 196, 1108, 528), WHITE, BLUE, radius=12)
    picture.text((676, 212), "工具结果节流", 22, BLUE, True, width=408)
    picture.text((676, 256), "能 grep / glob 就别 bash find", 18, MUTED, width=408)
    picture.text((676, 292), "read 大文件用行范围", 18, MUTED, width=408)
    picture.text((676, 328), "扫过的卡片别让模型全文复述", 18, MUTED, width=408)
    picture.text((676, 364), "失败输出存仓库笔记，压缩前救证据", 18, MUTED, width=408)
    picture.footer("省钱的顺序：先砍上下文，再砍并行度，最后才换更便宜的模型。")


def six_step_chain(picture: Drawing):
    picture.header("第 33 章 · 六十分钟串链",
                   "每步留产物，六步齐了才算总复习及格。",
                   "第 1、2 步命令形状本机已验；3–6 步产物以你仓库为准。")
    steps = (("① 确认二进制", "5 分钟 · omp --version 读出版本", ORANGE),
             ("② 新配置档", "15 分钟 · --profile review 回「在线」", BLUE),
             ("③ 小仓走一圈", "20 分钟 · git diff 即产物", GREEN),
             ("④ 制造失败", "10 分钟 · 看它先复现再改", ORANGE),
             ("⑤ 遮罩实验", "5 分钟 · 假密钥走一遍再删", BLUE),
             ("⑥ 架构笔记", "5 分钟 · 导出会话得 HTML", GREEN))
    for index, (title, detail, color) in enumerate(steps):
        column, row = divmod(index, 2)
        left = 92 + column * 516
        top = 200 + row * 150
        picture.box((left, top, left + 492, top + 126), WHITE, color, radius=12)
        picture.text((left + 22, top + 14), title, 22, color, True, width=448)
        picture.text((left + 22, top + 56), detail, 18, MUTED, width=448)
    picture.note((92, 656, 1108, 720), "及格线：", "六步都有产物。", GREEN, SAGE)
    picture.footer("这一步走完，前面 32 章的碎片才串成一条链。")


def subcommand_grid(picture: Drawing):
    picture.header("附录 A · 子命令地图",
                   "按你日常问的问题分格，不冒充完整表。",
                   "以 omp --help 的 COMMANDS 表为准；未知旗标才会报错 exit 2。")
    cells = (("接模型", "login / models / models find", ORANGE),
             ("会话迁移", "session pack / unpack / moved", BLUE),
             ("后台进程", "ps --json / --plain", GREEN),
             ("改配置", "config list / get / set / reset", ORANGE),
             ("技能与包", "skill（单数）/ plugin / install", BLUE),
             ("当服务跑", "--mode rpc / acp", GREEN),
             ("升级本体", "update --check / --plugins", ORANGE),
             ("离线计数", "toks <文件或文本>", BLUE))
    for index, (name, commands, color) in enumerate(cells):
        column, row = divmod(index, 2)
        left = 92 + column * 516
        top = 196 + row * 118
        picture.box((left, top, left + 492, top + 96), WHITE, color, radius=10)
        picture.text((left + 20, top + 12), name, 21, color, True, width=452)
        picture.text((left + 20, top + 50), commands, 17, MUTED, width=452)
    picture.footer("拿不准就跑 omp <猜的名字>？不行——整句会被当提示词送进模型。")


def lookup_order(picture: Drawing):
    picture.header("附录 B · 怎么查，而不是怎么背",
                   "斜杠命令随版本、主题与扩展变化。",
                   "按这张顺序查，比背表可靠。")
    steps = (("① TUI 内帮助与补全", "先进 omp 会话，敲 / 看补全；/help 看全量", ORANGE),
             ("② 官方文档", "docs 里的 slash-commands 与版本说明", BLUE),
             ("③ 本机实验", "怀疑扩展覆盖：--no-extensions 开新会话对比", GREEN))
    for index, (title, detail, color) in enumerate(steps):
        top = 200 + index * 120
        picture.box((110, top, 1108, top + 96), WHITE, color, radius=12)
        picture.badge((144, top + 48), index + 1, color)
        picture.text((186, top + 14), title, 23, color, True, width=880)
        picture.text((186, top + 56), detail, 19, MUTED, width=880)
    picture.note((92, 574, 1108, 668), "最容易踩的坑：",
                 "在 shell 敲 omp /memory view 不报错——整句被当提示词吞掉。斜杠命令只在会话内。",
                 ORANGE, PEACH)
    picture.footer("查不到时带上版本字符串再查文档；别用猜的命令形状。")


def verify_script(picture: Drawing):
    picture.header("附录 C · 配置变更的最小验证剧本",
                   "每改一个键，走一遍五步。",
                   "拒绝「改完再说」的堆叠式配置。")
    steps = (("① 只改一个键", "一次一个，别批量", ORANGE),
             ("② 开临时会话", "或 --no-session 若适用", BLUE),
             ("③ 最小提示触发", "只问与该键相关的一件事", GREEN),
             ("④ 看卡片或日志", "确认行为符合预期", ORANGE),
             ("⑤ 失败先回滚", "回滚该键，不在废墟上叠加", BLUE))
    for index, (title, detail, color) in enumerate(steps):
        top = 196 + index * 92
        picture.box((110, top, 1108, top + 72), WHITE, color, radius=10)
        picture.badge((144, top + 36), index + 1, color)
        picture.text((186, top + 10), title, 22, color, True, width=560)
        picture.text((700, top + 16), detail, 18, MUTED, width=392)
    picture.note((92, 664, 1108, 718), "Profile 弄乱时：",
                 "新建命名配置档对比，比在废墟上修补快。", GREEN, SAGE)
    picture.footer("验证命令写进页边——下次改同一个键，直接抄。")


def recall_drill(picture: Drawing):
    picture.header("附录 D · 默写流程",
                   "从最近一章抄十个词，闭卷默写，再对本文。",
                   "错词记页边；升级二进制后重默写四个词。")
    steps = (("① 抄十个词", "从最近一章挑高频术语", ORANGE),
             ("② 闭卷默写", "合上书，写解释不写名词", BLUE),
             ("③ 对本文", "逐条核对定义与边界", GREEN),
             ("④ 错词记页边", "标记回哪一章补", ORANGE),
             ("⑤ 每月重默写", "profile / launch / secrets / task", BLUE))
    for index, (title, detail, color) in enumerate(steps):
        top = 196 + index * 88
        picture.box((110, top, 1108, top + 68), WHITE, color, radius=10)
        picture.badge((144, top + 34), index + 1, color)
        picture.text((186, top + 10), title, 22, color, True, width=560)
        picture.text((700, top + 16), detail, 18, MUTED, width=392)
    picture.note((92, 650, 1108, 704), "易混对专练：",
                 "默写时把易混对拆开写，各写一句「它不是什么」。", GREEN, SAGE)
    picture.footer("能指回章节、能说清边界，才算记住。")


def three_outcomes(picture: Drawing):
    picture.header("第 1 章 · 三种命令，三种结局",
                   "旗标拼错会报错；子命令猜错不会。",
                   "带横杠的是旗标，不带的是你要说的话。")
    rows = (("omp notasubcommand", "停在 Working...——整句被当提示词送进模型", ORANGE),
            ("omp --model（缺值）", "同样 Working...；缺的值被吞进提示词", ORANGE),
            ("omp --nopt（旗标拼错）", "Error: unknown flag: --nopt，exit 2", GREEN))
    for index, (command, outcome, color) in enumerate(rows):
        top = 200 + index * 122
        picture.box((110, top, 1108, top + 98), WHITE, color, radius=12)
        picture.text((136, top + 12), command, 22, color, True, width=940)
        picture.text((136, top + 54), outcome, 19, MUTED, width=940)
    picture.note((92, 574, 1108, 656), "卡片比总结硬：",
                 "「我已经改好了」不算数——往上翻工具卡片，确认 edit / write 真跑过。",
                 BLUE, SKY)
    picture.footer("先 omp --help 数 COMMANDS，再决定有没有那个子命令。")


def desk_pile(picture: Drawing):
    picture.header("第 2 章 · 书桌上堆了什么",
                   "agent 的书桌比聊天热闹得多。",
                   "同一个 128k，agent 三五个工具回合就紧张。")
    piles = (("系统侧", "人格与安全约束、工具清单、项目规则", ORANGE),
             ("你刚说的话", "可能还带 ultrathink 触发的隐藏说明", BLUE),
             ("read 的结果", "摘要与挑片段，不是整文件倾倒", GREEN),
             ("搜索命中", "grep / glob / ast_grep 的列表", ORANGE),
             ("编辑预览与测试输出", "edit 的 diff、bash 的 stdout/stderr", BLUE),
             ("子代理回传", "task 的结构化结果，不是一大段散文", GREEN))
    for index, (name, detail, color) in enumerate(piles):
        column, row = divmod(index, 2)
        left = 92 + column * 516
        top = 196 + row * 152
        picture.box((left, top, left + 492, top + 128), WHITE, color, radius=12)
        picture.text((left + 22, top + 14), name, 21, color, True, width=448)
        picture.text((left + 22, top + 54), detail, 17, MUTED, width=448)
    picture.footer("定位再精读，比「把整个仓库读一遍」省一张书桌。")


def tool_baskets(picture: Drawing):
    picture.header("第 3 章 · 能力分筐，入口统一",
                   "内置工具大致六筐，同一命名空间。",
                   "有的默认关闭，要在设置里打开。")
    baskets = (("文件与搜索", "read / write / edit / ast_edit / ast_grep / grep / glob", ORANGE),
               ("运行时", "bash / eval（持久 Python / JS）", BLUE),
               ("代码智能", "lsp / debug / 门控的 security_scan", GREEN),
               ("协作", "task / wait / todo / ask", ORANGE),
               ("桌面与网络", "browser / computer / web_search / 门控 github", BLUE),
               ("记忆与技能", "retain / recall / reflect / learn / manage_skill", GREEN))
    for index, (name, detail, color) in enumerate(baskets):
        column, row = divmod(index, 2)
        left = 92 + column * 516
        top = 196 + row * 148
        picture.box((left, top, left + 492, top + 124), WHITE, color, radius=12)
        picture.text((left + 22, top + 14), name, 21, color, True, width=448)
        picture.text((left + 22, top + 54), detail, 17, MUTED, width=448)
    picture.note((92, 640, 1108, 704), "可以躲进设备：",
                 "read xd:// 列出；tools.xdev 打开后用 write xd://<tool> 运行。", BLUE, SKY)
    picture.footer("模型只学一套命名空间——不用记八套插件 API。")


def pick_four(picture: Drawing):
    picture.header("第 12 章 · 四只手怎么选",
                   "目标决定工具，别凭手感点。",
                   "点错工具比不会用更费时间。")
    choices = (("网页 DOM / 页面流程", "browser", ORANGE),
               ("本机 App、AX、剪贴板", "computer", BLUE),
               ("查公开资料", "web_search，再 read URL", GREEN),
               ("仓库 / PR / Actions", "github", ORANGE))
    for index, (goal, tool, color) in enumerate(choices):
        column, row = divmod(index, 2)
        left = 92 + column * 516
        top = 200 + row * 164
        picture.box((left, top, left + 492, top + 140), WHITE, color, radius=12)
        picture.text((left + 22, top + 16), goal, 21, color, True, width=448)
        picture.text((left + 22, top + 62), tool, 20, INK, True, width=448)
    picture.note((92, 544, 1108, 656), "两条纪律：",
                 "搜索摘要不是一级事实源——read 原始 URL；PR 状态是快照，关键操作前再查。",
                 BLUE, SKY)
    picture.footer("浏览器进程、驱动、临时 profile 会残留——长会话记得回收。")


def collab_trio(picture: Drawing):
    picture.header("第 13 章 · 三兄弟别混着排障",
                   "/fork、task、wait 不在同一层。",
                   "会话章管历史；本章管单次任务内的协作。")
    trio = (("/fork", "复制的是会话笔记本", ORANGE),
            ("task", "一次工具调用拉起的子 agent 运行", BLUE),
            ("wait", "同步原语：等第一件落地的事", GREEN))
    for index, (name, detail, color) in enumerate(trio):
        top = 196 + index * 116
        picture.box((110, top, 1108, top + 92), WHITE, color, radius=12)
        picture.text((136, top + 12), name, 24, color, True, width=920)
        picture.text((136, top + 54), detail, 19, MUTED, width=920)
    picture.note((92, 560, 1108, 668), "wait 的硬规则：",
                 "不收参数、每条 30 分钟硬顶；结果被消费掉不会再来，?progress 不算答复。",
                 BLUE, SKY)
    picture.footer("要掐掉别等：write proc://<id>/kill。")


def read_hunt(picture: Drawing):
    picture.header("第 8 章 · 摸清模块的四步",
                   "找到入口，再精读——别整库倾倒。",
                   "中间任何一步空结果，先怀疑模式/路径，再怀疑「真的没有」。")
    steps = (("① glob 找入口", "**/index.ts、**/mod.rs、**/__init__.py，按语言选", ORANGE),
             ("② grep 关键词", "export / pub use / __all__，限制在上一步命中的目录", BLUE),
             ("③ read 核心文件", "2–3 个文件读 :1-80，需要时再补范围", GREEN),
             ("④ ast_grep 批量", "找「所有 createX( 调用」用结构匹配，别用脆弱正则", ORANGE))
    for index, (title, detail, color) in enumerate(steps):
        top = 200 + index * 116
        picture.box((110, top, 1108, top + 92), WHITE, color, radius=12)
        picture.badge((144, top + 46), index + 1, color)
        picture.text((186, top + 14), title, 23, color, True, width=880)
        picture.text((186, top + 54), detail, 18, MUTED, width=880)
    picture.note((92, 572, 1108, 664), "空结果先别下结论：",
                 "换模式、放宽路径、加 --no-gitignore 再试；被 ignore 的目录根本没进搜索。",
                 BLUE, SKY)
    picture.footer("四步走完，你手里是入口清单与关键片段，不是一堆噪音。")


def patch_forms(picture: Drawing):
    picture.header("第 9 章 · 补丁长什么样",
                   "一段输入字符串，多个 section。",
                   "带 body 的 PUT 每行都是 +TEXT——正文是最终内容，不是前后对。")
    picture.box((92, 196, 1108, 300), WHITE, ORANGE, radius=10)
    picture.text((116, 210), "[src/example.ts#1A2B]", 20, ORANGE, True, width=960)
    picture.text((116, 244), "PUT 4.=4:", 20, INK, width=960)
    picture.text((116, 274), "  +const value = 2;", 20, INK, width=960)
    forms = (("PUT N.=M", "替换闭区间；PUT <N / >N 插入", BLUE),
             ("PUT N*", "从 N 行的语法块整块替换", GREEN),
             ("CUT N.=M", "删除并捕获，可 @name 进寄存器", ORANGE),
             ("MV DEST / REM", "改完写到目标并删源 / 删整个文件", BLUE))
    for index, (form, detail, color) in enumerate(forms):
        column, row = divmod(index, 2)
        left = 92 + column * 516
        top = 320 + row * 132
        picture.box((left, top, left + 492, top + 112), WHITE, color, radius=10)
        picture.text((left + 20, top + 12), form, 22, color, True, width=452)
        picture.text((left + 20, top + 54), detail, 18, MUTED, width=452)
    picture.note((92, 596, 1108, 668), "行号基准：",
                 "全部相对原始快照——多段补丁都按改前行号，别按执行后重数。", BLUE, SKY)
    picture.footer("TAG 必须抄自最近锚定的 read / grep / 成功 edit；新建用 write。")


def two_gates(picture: Drawing):
    picture.header("第 10 章 · bash 前面的两道闸",
                   "改道让模型换工具；权限按序第一条命中就赢。",
                   "位置不同，结果也不同。")
    picture.box((92, 196, 584, 468), WHITE, ORANGE, radius=12)
    picture.text((116, 212), "第一道：改道", 23, ORANGE, True, width=444)
    picture.text((116, 254), "cat / head → read", 18, MUTED, width=444)
    picture.text((116, 288), "grep / rg → grep", 18, MUTED, width=444)
    picture.text((116, 322), "find -name → glob", 18, MUTED, width=444)
    picture.text((116, 356), "sed -i → edit", 18, MUTED, width=444)
    picture.text((116, 390), "npm run dev / 裸 & → 命名服务", 18, MUTED, width=444)
    picture.box((616, 196, 1108, 468), WHITE, BLUE, radius=12)
    picture.text((640, 212), "第二道：权限", 23, BLUE, True, width=444)
    picture.text((640, 254), "allow / prompt / deny 三选一", 18, MUTED, width=444)
    picture.text((640, 288), "按序比，第一条命中就赢", 18, MUTED, width=444)
    picture.text((640, 322), "deny 在 execute 之前拦，yolo 也拦", 18, MUTED, width=444)
    picture.text((640, 356), "allow 默认只降简单命令", 18, MUTED, width=444)
    picture.text((640, 390), "复合命令要开 allowCompoundCommands", 18, MUTED, width=444)
    picture.note((92, 496, 1108, 592), "反例可以保留：",
                 "构建脚本、docker、项目自定义 CLI 本来就该进 shell——别硬改成专用工具。",
                 GREEN, SAGE)
    picture.footer("被改道不是报错，让你用上下文更好的那条路。")


def compaction_keys(picture: Drawing):
    picture.header("第 15 章 · 十个键各管一段",
                   "本机 [context] 与 [internal] 段的压缩键。",
                   "改阈值前先读原值，别把默认当「没配」。")
    groups = (("总开关", "compaction.enabled = true", ORANGE),
              ("阈值", "thresholdPercent / thresholdTokens 均为 -1，由窗口与 modelThresholds 推", BLUE),
              ("方法与保留", "methodOrder [remote, soft]；keepRecentTokens 20000", GREEN),
              ("维护时机", "midTurn / idle 开关；idle 阈值 200000、闲 300 秒", ORANGE))
    for index, (title, detail, color) in enumerate(groups):
        top = 196 + index * 112
        picture.box((110, top, 1108, top + 92), WHITE, color, radius=12)
        picture.text((136, top + 12), title, 22, color, True, width=930)
        picture.text((136, top + 52), detail, 18, MUTED, width=930)
    picture.note((92, 592, 1108, 664), "另一件事：",
                 "branchSummary.enabled = false——分支摘要默认不生成，别和压缩总开关混为一谈。",
                 BLUE, SKY)
    picture.footer("reason 有四种：overflow / incomplete / threshold / idle，别混成一件事。")


def learn_timing(picture: Drawing):
    picture.header("第 16 章 · learn 什么时候生效",
                   "写进 learned.md，但不改本轮前缀。",
                   "从下一会话起才注入。")
    picture.box((92, 200, 584, 430), WHITE, GREEN, radius=12)
    picture.text((116, 216), "learn（autolearn 开着才有）", 21, GREEN, True, width=444)
    picture.text((116, 258), "把耐久 lessons 写进 learned.md", 18, MUTED, width=444)
    picture.text((116, 292), "去重、脱敏、有上限", 18, MUTED, width=444)
    picture.text((116, 326), "不改当前会话 prompt-cache 前缀", 18, MUTED, width=444)
    picture.text((116, 360), "从下一会话起注入", 18, INK, True, width=444)
    picture.box((616, 200, 1108, 430), WHITE, BLUE, radius=12)
    picture.text((640, 216), "本地管线（启动时跑）", 21, BLUE, True, width=444)
    picture.text((640, 258), "Phase 1：从变更过的历史会话抽耐久信号", 18, MUTED, width=444)
    picture.text((640, 292), "Phase 2：合并为 MEMORY.md 等产物", 18, MUTED, width=444)
    picture.text((640, 326), "/memory enqueue 标记工作，下次启动捡起", 18, MUTED, width=444)
    picture.note((92, 452, 1108, 552), "会被跳过：",
                 "子代理、未持久化会话，以及太新 / 太旧 / 活跃中的会话都不进管线。",
                 ORANGE, PEACH)
    picture.footer("要它立刻记住：写进仓库文件或规则，别指望聊天窗口当硬盘。")


def role_routing(picture: Drawing):
    picture.header("第 17 章 · 角色怎么配不烧钱",
                   "按任务选角色，不按心情选。",
                   "成本细节见第 32 章。")
    rules = (("子代理默认绑 task 角色", "别让每个探路子任务都上旗舰模型", ORANGE),
             ("提交信息 / 分类 / 格式转换", "优先 smol / tiny", BLUE),
             ("架构裁决 / 安全敏感改动", "再上 slow / default", GREEN),
             ("advisor 打开 = 多付一路", "只在高风险变更开", ORANGE))
    for index, (title, detail, color) in enumerate(rules):
        top = 200 + index * 112
        picture.box((110, top, 1108, top + 92), WHITE, color, radius=12)
        picture.badge((144, top + 46), index + 1, color)
        picture.text((186, top + 14), title, 22, color, True, width=880)
        picture.text((186, top + 54), detail, 18, MUTED, width=880)
    picture.footer("角色值的六层优先级见 §17.2a——你改的那层未必是生效的那层。")


def plan_keys(picture: Drawing):
    picture.header("第 18 章 · 计划模式与开启方式",
                   "可用但默认不自动进。",
                   "本机 18.16.0 实跑键值，证据在 facts/live-18.16.0。")
    keys = (("plan.enabled", "true——计划模式在这台机器上可用", GREEN),
            ("plan.defaultOnStartup", "false——启动不自动进入", BLUE),
            ("--plan-yolo", "只读 plan 开场；第一次 resolve 自动批准，再切 --plan-yolo-into 实现", ORANGE),
            ("--goal=<value>", "直接从 goal 模式开场", ORANGE))
    for index, (name, detail, color) in enumerate(keys):
        top = 196 + index * 112
        picture.box((110, top, 1108, top + 92), WHITE, color, radius=12)
        picture.text((136, top + 12), name, 22, color, True, width=930)
        picture.text((136, top + 52), detail, 18, MUTED, width=930)
    picture.note((92, 592, 1108, 664), "和审批模式互补：",
                 "审批是执行门禁，ask 是产品决策问答——两者都不替你做计划。",
                 BLUE, SKY)
    picture.footer("想用计划模式就显式开；别指望它自己跳出来。")


def mode_matrix(picture: Drawing):
    picture.header("附录 A · 打印模式与输出模式",
                   "-p 走非交互；--mode 控制输出形态。",
                   "第一次学手感请留在 TUI（第 6 章）。")
    modes = (("text", "默认；给人读", ORANGE),
             ("json", "机器解析用", BLUE),
             ("rpc / rpc-ui", "stdio 上的 JSONL 帧", GREEN),
             ("acp", "cli-reference 另列；--mode acp 与 omp acp 都可", ORANGE))
    for index, (name, detail, color) in enumerate(modes):
        column, row = divmod(index, 2)
        left = 92 + column * 516
        top = 200 + row * 140
        picture.box((left, top, left + 492, top + 116), WHITE, color, radius=12)
        picture.text((left + 22, top + 14), name, 23, color, True, width=448)
        picture.text((left + 22, top + 56), detail, 18, MUTED, width=448)
    picture.note((92, 492, 1108, 592), "两条提醒：",
                 "脚本与 CI 用打印模式，别在 TUI 里写脚本；计划类默认启动行为在打印模式可能被忽略。",
                 BLUE, SKY)
    picture.footer("选模式前先问：这一跑是给人看，还是给程序读？")


def slash_vs_keyword(picture: Drawing):
    picture.header("附录 B · 斜杠与魔法词",
                   "一个是命令，一个是行为倾向。",
                   "弄混就会「怎么按了没反应」。")
    picture.box((92, 210, 584, 470), WHITE, ORANGE, radius=12)
    picture.text((116, 226), "斜杠命令", 24, ORANGE, True, width=444)
    picture.text((116, 270), "你下的命令", 20, INK, True, width=444)
    picture.text((116, 310), "在会话输入框里敲，回车执行", 18, MUTED, width=444)
    picture.text((116, 344), "示例：/memory view、/mcp list", 18, MUTED, width=444)
    picture.text((116, 378), "shell 里敲不会执行", 18, MUTED, width=444)
    picture.box((616, 210, 1108, 470), WHITE, BLUE, radius=12)
    picture.text((640, 226), "魔法词", 24, BLUE, True, width=444)
    picture.text((640, 270), "提示词里触发的行为倾向", 20, INK, True, width=444)
    picture.text((640, 310), "随你的话一起送进模型（第 18 章）", 18, MUTED, width=444)
    picture.text((640, 344), "示例：ultrathink、orchestrate", 18, MUTED, width=444)
    picture.text((640, 378), "只影响含该词的那一回合", 18, MUTED, width=444)
    picture.footer("按了没反应，先分清你按的是命令，还是在话里埋了暗示。")


def embed_diff(picture: Drawing):
    picture.header("附录 C · 与 SDK 嵌入的关系",
                   "配置发现也可以嵌进你的程序。",
                   "用发现还是用覆盖，要明确写死一种。")
    picture.box((92, 200, 584, 440), WHITE, ORANGE, radius=12)
    picture.text((116, 216), "走 CLI", 23, ORANGE, True, width=444)
    picture.text((116, 258), "agentDir、settings 默认被发现", 18, MUTED, width=444)
    picture.text((116, 292), "cwd / 鉴权 / 模型都按环境解析", 18, MUTED, width=444)
    picture.text((116, 326), "行为随机器与 profile 变化", 18, MUTED, width=444)
    picture.box((616, 200, 1108, 440), WHITE, BLUE, radius=12)
    picture.text((640, 216), "走嵌入", 23, BLUE, True, width=444)
    picture.text((640, 258), "createAgentSession 可传可发现", 18, MUTED, width=444)
    picture.text((640, 292), "宿主决定用哪一层、覆盖什么", 18, MUTED, width=444)
    picture.text((640, 326), "不写死就会出现幽灵差异", 18, MUTED, width=444)
    picture.note((92, 464, 1108, 560), "幽灵差异长这样：",
                 "同一份仓库，CLI 一套行为、嵌入另一套——查半天才发现是发现顺序不同。",
                 BLUE, SKY)
    picture.footer("嵌入前先决定：发现还是覆盖，写进你的初始化代码。")


def uncovered_gaps(picture: Drawing):
    picture.header("附录 E · 三处刻意留白",
                   "上游 README 21 项能力，本书展开 18 项。",
                   "宁可不写，也不把宣传语当规范。")
    gaps = (("04 · 流式规则注入", "需要本机二进制或对应 docs 验证", ORANGE),
            ("18 · 冲突解决 /resolve", "同上——未验证就不写成规范", BLUE),
            ("20 · Slack（浏览器已展开）", "同上；第 12 章只覆盖浏览器", GREEN))
    for index, (title, detail, color) in enumerate(gaps):
        top = 200 + index * 116
        picture.box((110, top, 1108, top + 96), WHITE, color, radius=12)
        picture.badge((144, top + 48), index + 1, color)
        picture.text((186, top + 14), title, 22, color, True, width=880)
        picture.text((186, top + 56), detail, 18, MUTED, width=880)
    picture.note((92, 564, 1108, 664), "怎么补：",
                 "按页边核对法——对照本机帮助或上游文档核一条，写进页边再决定是否展开。",
                 BLUE, SKY)
    picture.footer("章节顺序不必按表走；把 21 项当索引，读完一章回来划掉一行。")


def lsp_switches(picture: Drawing):
    picture.header("第 11 章 · 七个开关各管一段",
                   "本机 [files] 段里管 lsp 的行。",
                   "两行解释大半「为什么没红线」。")
    groups = (("注册", "lsp.enabled = true；关掉后 lsp 工具根本不注册", ORANGE),
              ("启动", "lazy 按需冷启；shared 先问 broker，失败才起私有进程", BLUE),
              ("诊断", "onWrite = true；onEdit = false——改完不拉就没有", GREEN),
              ("格式化与超时", "formatOnWrite = false；requestTimeout 10 秒（上限 max(20, 它)）", ORANGE))
    for index, (title, detail, color) in enumerate(groups):
        top = 196 + index * 112
        picture.box((110, top, 1108, top + 92), WHITE, color, radius=12)
        picture.text((136, top + 12), title, 22, color, True, width=930)
        picture.text((136, top + 52), detail, 18, MUTED, width=930)
    picture.note((92, 592, 1108, 664), "记住这两条默认值：",
                 "diagnosticsOnEdit 关、lazy 开——第一个解释「没红线」，第二个解释「第一次慢」。",
                 BLUE, SKY)
    picture.footer("想改完立刻看诊断，就显式调一次 lsp；别等自动。")


def config_actions(picture: Drawing):
    picture.header("第 23 章 · omp config 五个动作",
                   "list / get / set / reset / path。",
                   "本机 --help 原文见 facts/live-18.16.0/help-config.txt。")
    rows = (("list", "打印所有设置及生效值；--scope 只看某一层写了什么", ORANGE),
            ("get <key>", "取一个键的生效值；未知键 exit 非零", BLUE),
            ("set <key> <value>", "schema 解析后写进全局 config.yml；别的层仍生效时会说是谁", GREEN),
            ("reset <key>", "从全局删掉这个键，让默认值生效", ORANGE),
            ("path", "打印活动 agent 目录（认 PI_CODING_AGENT_DIR）", BLUE))
    for index, (action, detail, color) in enumerate(rows):
        top = 196 + index * 90
        picture.box((110, top, 1108, top + 72), WHITE, color, radius=10)
        picture.text((136, top + 10), action, 21, color, True, width=380)
        picture.text((540, top + 12), detail, 18, MUTED, width=548)
    picture.note((92, 646, 1108, 712), "旗标边界：", "--json 被 list/get/set/reset 接受；--scope 只有 list 用。",
                 BLUE, SKY)
    picture.footer("set 之后照它说的查「谁还在提供值」——改的那层未必是生效的那层。")


def pipeline_vs_approval(picture: Drawing):
    picture.header("附录 D · 过关、点头、问你",
                   "三个词三件事，别混用。",
                   "权限管线与审批是一问一答的两端。")
    cards = (("权限管线", "一条命令从发起到执行要过的几道关；卡在哪就看它停在第几关", ORANGE),
             ("审批 approval", "工具动手前由谁点头的判据——执行门禁那端", BLUE),
             ("ask 工具", "产品决策问答，不是执行门禁", GREEN))
    for index, (title, detail, color) in enumerate(cards):
        top = 200 + index * 120
        picture.box((110, top, 1108, top + 96), WHITE, color, radius=12)
        picture.text((136, top + 12), title, 23, color, True, width=920)
        picture.text((136, top + 56), detail, 18, MUTED, width=920)
    picture.note((92, 576, 1108, 656), "yolo 是另一个档：",
                 "不再逐条问、命令直接跑；演示图省事可以开，跑别人代码前记得关回去。",
                 ORANGE, PEACH)
    picture.footer("第 10 章的「两道闸」讲同一件事：改道在前，权限在后。")


def reading_map(picture: Drawing):
    picture.header("前言 · 这本书怎么走",
                   "先原理、再实战；七篇加五个附录。",
                   "插画双轨：Mermaid 管架构关系，handraw 管概念漫画。")
    parts = (("一 · 原理", "agent = 模型 + 工具 + 循环", ORANGE),
             ("二 · 上手", "装好、接上模型、第一次改代码", BLUE),
             ("三 · 工具箱", "读、搜、改、跑、看、协作", GREEN),
             ("四 · 上下文", "压缩、记忆、角色", ORANGE),
             ("五 · 扩展", "Skills、MCP、自定义工具、扩展包", BLUE),
             ("六 · 实战", "六个真实任务", GREEN),
             ("七 · 排障", "排错、安全、成本、读源码", ORANGE))
    for index, (name, detail, color) in enumerate(parts[:6]):
        column, row = divmod(index, 2)
        left = 92 + column * 516
        top = 196 + row * 118
        picture.box((left, top, left + 492, top + 96), WHITE, color, radius=10)
        picture.text((left + 20, top + 12), name, 21, color, True, width=452)
        picture.text((left + 20, top + 50), detail, 17, MUTED, width=452)
    picture.box((92, 550, 1108, 618), WHITE, ORANGE, radius=10)
    picture.text((116, 566), "七 · 排障", 21, ORANGE, True, width=420)
    picture.text((560, 568), "排错、安全、成本、读源码", 17, MUTED, width=520)
    picture.note((92, 634, 1108, 704), "附录 A–E：", "命令行、斜杠、配置、术语、版本钉——查得到就好，不必通读。",
                 BLUE, SKY)
    picture.footer("准备好了，从第 1 章开始。")


def skill_lifecycle(picture: Drawing):
    picture.header("第 19 章 · Skill 的团队生命周期",
                   "起草到上线，五步；删除比堆积重要。",
                   "description 当广告写，正文当手册写。")
    steps = (("① 起草", "description 写触发场景，正文写步骤", ORANGE),
             ("② 同事手跑", "别人照着做一遍，看会不会卡", BLUE),
             ("③ 收进规范位置", "skills/<name>/SKILL.md，版本记文首", GREEN),
             ("④ 试用一周", "记录误触发与漏触发", ORANGE),
             ("⑤ 再决定 extension", "要注册工具才升级成扩展", BLUE))
    for index, (title, detail, color) in enumerate(steps):
        top = 196 + index * 88
        picture.box((110, top, 1108, top + 68), WHITE, color, radius=10)
        picture.badge((144, top + 34), index + 1, color)
        picture.text((186, top + 10), title, 21, color, True, width=560)
        picture.text((700, top + 16), detail, 18, MUTED, width=392)
    picture.note((92, 650, 1108, 712), "升级后抽测：",
                 "omp 升级完抽测触发是否仍准；过期 skill 会污染元数据列表，该删就删。",
                 ORANGE, PEACH)
    picture.footer("删除比堆积更重要——元数据列表越长，模型越难挑对。")


def hook_audit(picture: Drawing):
    picture.header("第 21 章 · 钩子失败要吵出来",
                   "静默失败比没有钩子更糟。",
                   "模型会以为工具成功了。")
    rules = (("拒绝时", "返回清楚原因，别只给一个 false", ORANGE),
             ("改写参数时", "打审计日志——谁改了、改成了什么", BLUE),
             ("日志一行一条", "时间、工具名、决策、原因码", GREEN),
             ("上线前自测", "用 -p 做一次「故意缺参」，确认 schema 报错可读", ORANGE))
    for index, (title, detail, color) in enumerate(rules):
        top = 200 + index * 112
        picture.box((110, top, 1108, top + 92), WHITE, color, radius=12)
        picture.text((136, top + 12), title, 22, color, True, width=930)
        picture.text((136, top + 52), detail, 18, MUTED, width=930)
    picture.note((92, 652, 1108, 716), "给模型的 UI：",
                 "自定义工具的 schema 与描述是给模型看的界面，吝啬文字等于自找误调用。",
                 BLUE, SKY)
    picture.footer("模型可见的错误字符串要人话；结构化留给日志。")


def ext_acceptance(picture: Drawing):
    picture.header("第 22 章 · 扩展验收六步",
                   "全部绿灯才允许进团队默认配置。",
                   "PR 审扩展像审生产服务。")
    steps = (("① 干净 profile 加载", "没有历史配置帮忙", ORANGE),
             ("② 命令列表含新命令", "斜杠看得见", BLUE),
             ("③ 工具可调用", "模型调得到、结果对", GREEN),
             ("④ 故意重复名", "看冲突日志是否可读", ORANGE),
             ("⑤ /reload-plugins", "热重载后行为可解释", BLUE),
             ("⑥ 卸载后消失", "列表里干净退出", GREEN))
    for index, (title, detail, color) in enumerate(steps):
        column, row = divmod(index, 2)
        left = 92 + column * 516
        top = 200 + row * 132
        picture.box((left, top, left + 492, top + 108), WHITE, color, radius=12)
        picture.text((left + 22, top + 14), title, 21, color, True, width=448)
        picture.text((left + 22, top + 54), detail, 18, MUTED, width=448)
    picture.note((92, 600, 1108, 690), "顺带三句：",
                 "依赖、权限、失败与卸载都要写清；模块顶层状态跨子会话会脏；名字加团队前缀。",
                 BLUE, SKY)
    picture.footer("验收脚本落进仓库，别人合并前也跑一遍。")


def mcp_ticket(picture: Drawing):
    picture.header("第 20 章 · 引入 MCP 的变更单",
                   "每个 server 条目都是供应链。",
                   "锁定版本、记维护人、写失败手册。")
    fields = (("server 名称与版本", "钉住具体版本，别用 latest", ORANGE),
              ("启动命令", "stdio 的 command / args / env / cwd", BLUE),
              ("所需环境变量", "只写变量名，不写值", GREEN),
              ("是否出网", "传输选 stdio 还是远程决定攻击面", ORANGE),
              ("失败时人类步骤", "指向 stderr 与 exit 码", BLUE),
              ("回滚方式", "删 disabledServers 或 PR 回滚条目", GREEN))
    for index, (name, detail, color) in enumerate(fields):
        column, row = divmod(index, 2)
        left = 92 + column * 516
        top = 196 + row * 132
        picture.box((left, top, left + 492, top + 108), WHITE, color, radius=12)
        picture.text((left + 22, top + 14), name, 21, color, True, width=448)
        picture.text((left + 22, top + 54), detail, 18, MUTED, width=448)
    picture.note((92, 600, 1108, 686), "两条回滚路径别混写：",
                 "disabledServers 删掉即恢复；enabled:false 只有 PR 回滚能改。",
                 ORANGE, PEACH)
    picture.footer("合并前在干净 profile 验证：工具列表出现，且最小调用成功。")


def secret_shapes(picture: Drawing):
    picture.header("第 31 章 · 启动时还收集什么",
                   "除了配置里的秘密，还有三类形状。",
                   "以文档列表为准；别拿生产密钥做第一次实验。")
    shapes = (("环境变量", "名称像密钥的变量，值至少 8 字符", ORANGE),
              ("连接串密码", "URL 里带的凭据", BLUE),
              ("内置可逆正则", "GitHub / AWS / JWT / Bearer / PEM 等族", GREEN))
    for index, (title, detail, color) in enumerate(shapes):
        top = 196 + index * 108
        picture.box((110, top, 1108, top + 88), WHITE, color, radius=12)
        picture.text((136, top + 12), title, 22, color, True, width=930)
        picture.text((136, top + 52), detail, 18, MUTED, width=930)
    picture.note((92, 542, 1108, 636), "占位怎么算：",
                 "哈希基于安装私有密钥，避免按字典反推；友好名净化成大写字母数字且有长度上限。",
                 BLUE, SKY)
    picture.footer("密钥文件本身不要提交进仓库——它救不了被抄走的哈希。")


def cost_review(picture: Drawing):
    picture.header("第 32 章 · 一次成本复盘",
                   "挑昨天一场会话，只回答四个问题。",
                   "只改一条习惯，才能坚持。")
    questions = (("用了哪个模型", "是不是「杀鸡用牛刀」", ORANGE),
                 ("起了几个子代理", "每个都乘一份上下文", BLUE),
                 ("最大工具输出多长", "整树列表还是片段", GREEN),
                 ("有没有无意义重试", "同一命令反复跑", ORANGE))
    for index, (title, detail, color) in enumerate(questions):
        top = 196 + index * 104
        picture.box((110, top, 1108, top + 84), WHITE, color, radius=10)
        picture.badge((144, top + 42), index + 1, color)
        picture.text((186, top + 12), title, 22, color, True, width=560)
        picture.text((700, top + 18), detail, 18, MUTED, width=392)
    picture.note((92, 594, 1108, 664), "产出：",
                 "一条写进 AGENTS 或个人片段的习惯——下个月复盘时对照它。",
                 GREEN, SAGE)
    picture.footer("成本不是省出来的，是把大头一个个认出来。")


def incident_pack(picture: Drawing):
    picture.header("第 30 章 · 证据包模板",
                   "找人帮忙前，把这六样打包。",
                   "只写环境变量名，不贴密钥正文。")
    items = (("症状一句话", "别写「它坏了」", ORANGE),
             ("命令原文", "能直接粘贴重跑", BLUE),
             ("完整错误", "含 exit 码与 stderr 摘要", GREEN),
             ("版本首行", "omp --version 那行", ORANGE),
             ("相关配置路径", "密钥打码", BLUE),
             ("已尝试的最小动作", "做过什么、结果如何", GREEN))
    for index, (title, detail, color) in enumerate(items):
        column, row = divmod(index, 2)
        left = 92 + column * 516
        top = 196 + row * 124
        picture.box((left, top, left + 492, top + 100), WHITE, color, radius=10)
        picture.text((left + 22, top + 12), title, 21, color, True, width=448)
        picture.text((left + 22, top + 50), detail, 17, MUTED, width=448)
    picture.note((92, 576, 1108, 656), "为什么打包：",
                 "「我觉得卡住了」无法转发；六样齐了，别人才能复现或直接定位。",
                 BLUE, SKY)
    picture.footer("排障的第一产物是证据包，不是结论。")


def config_diary(picture: Drawing):
    picture.header("第 23 章 · 配置变更日记",
                   "日记一行一条，七个字段。",
                   "改一层、开新会话、记下 profile 与路径。")
    fields = (("时间", "什么时候改的", ORANGE),
              ("profile", "活动配置档名", BLUE),
              ("文件路径", "动的是哪个文件", GREEN),
              ("键 / 旧值 / 新值", "三个一起记，别只记新值", ORANGE),
              ("验证方法", "下次照着验一遍", BLUE))
    for index, (title, detail, color) in enumerate(fields):
        top = 196 + index * 96
        picture.box((110, top, 1108, top + 76), WHITE, color, radius=10)
        picture.badge((144, top + 38), index + 1, color)
        picture.text((186, top + 12), title, 21, color, True, width=560)
        picture.text((700, top + 18), detail, 18, MUTED, width=392)
    picture.note((92, 664, 1108, 722), "两条硬规矩：",
                 "CI 只读叠加层单独成文件；密钥示例只写环境变量名。", GREEN, SAGE)
    picture.footer("文档里禁止「请开发者改 ~/.omp」——那是要事故的写法。")


def antipatterns(picture: Drawing):
    picture.header("第 24 章 · 反模式墙",
                   "接手陌生仓库时，贴在显示器边上。",
                   "五句话，每句都能让你白干一天。")
    walls = (("一上来重构整个目录", "地图都没有就先动土", ORANGE),
             ("用 shell 枚举代替 glob/grep", "窗口塞满噪音", BLUE),
             ("不跑测试就宣布读懂", "读懂的证据是绿测试", GREEN),
             ("把临时猜测写进 AGENTS.md", "猜想变规则，后来人照做", ORANGE),
             ("没地图就并行 task", "子代理各带一份大历史乱撞", BLUE))
    for index, (title, detail, color) in enumerate(walls):
        top = 196 + index * 92
        picture.box((110, top, 1108, top + 72), WHITE, color, radius=10)
        picture.badge((144, top + 36), index + 1, color)
        picture.text((186, top + 10), title, 21, color, True, width=560)
        picture.text((700, top + 16), detail, 18, MUTED, width=392)
    picture.footer("反模式不用记全，记住「先画地图再动土」这一条就够挡一半。")


def embed_checklist(picture: Drawing):
    picture.header("第 28 章 · 嵌入前的核对表",
                   "左边记发现项，右边按序排错。",
                   "都是外壳，同一套 agent 循环。")
    picture.box((92, 196, 584, 520), WHITE, ORANGE, radius=12)
    picture.text((116, 212), "嵌入前记录", 22, ORANGE, True, width=444)
    picture.text((116, 254), "cwd", 18, MUTED, width=444)
    picture.text((116, 288), "agentDir", 18, MUTED, width=444)
    picture.text((116, 322), "是否持久（文件式 / 内存式）", 18, MUTED, width=444)
    picture.text((116, 356), "模型与 fallback", 18, MUTED, width=444)
    picture.text((116, 390), "扩展是否加载", 18, MUTED, width=444)
    picture.box((616, 196, 1108, 520), WHITE, BLUE, radius=12)
    picture.text((640, 212), "RPC 排错顺序", 22, BLUE, True, width=444)
    picture.text((640, 254), "① 帧解析", 18, MUTED, width=444)
    picture.text((640, 288), "② 相关标识怎么对", 18, MUTED, width=444)
    picture.text((640, 322), "③ 错误是否可恢复", 18, MUTED, width=444)
    picture.text((640, 356), "④ 事件背压", 18, MUTED, width=444)
    picture.note((92, 540, 1108, 620), "共同点：",
                 "命令行、打印模式、SDK、RPC 都是外壳；信卡片在这里变成信事件与响应帧。",
                 GREEN, SAGE)
    picture.footer("排错别跳步：帧都解析不对，就别查相关标识。")


def three_deceptions(picture: Drawing):
    picture.header("第 33 章 · 总复习的三处自欺",
                   "最容易骗自己的三条，逐条对号。",
                   "六步缺一不可，产物写进笔记才算数。")
    traps = (("「我懂了」但说不出链", "被问「模型怎么找到 bash」时卡住", ORANGE),
             ("用日常配置档做实验", "扩展、技能、记忆全在，实验不干净", BLUE),
             ("只跑第 1、2 步就说串完了", "发现层、工具层、扩展层都没碰", GREEN))
    for index, (title, detail, color) in enumerate(traps):
        top = 200 + index * 122
        picture.box((110, top, 1108, top + 98), WHITE, color, radius=12)
        picture.badge((144, top + 49), index + 1, color)
        picture.text((186, top + 12), title, 22, color, True, width=880)
        picture.text((186, top + 54), detail, 18, MUTED, width=880)
    picture.note((92, 576, 1108, 656), "纠正办法：",
                 "用 33.7 的六步把每格走一遍；卡住的格子回对应章补，再开干净档重跑。",
                 BLUE, SKY)
    picture.footer("能把整条链复述出来，比「读完了」值钱。")


def four_names(picture: Drawing):
    picture.header("第 14 章 · 四个容易混的名字",
                   "混着叫，排障就会找错层。",
                   "前三个是上下文文件，第四个是推理后端。")
    names = (("Context files", "普通 Markdown 说明，开会话时注入", ORANGE),
             ("Sticky rules", "顶层 RULES.md 转成 always-apply 规则", BLUE),
             ("Discovery providers", "各工具的文件位置适配器", GREEN),
             ("Model providers", "推理后端（anthropic / openai……）", ORANGE))
    for index, (name, detail, color) in enumerate(names):
        column, row = divmod(index, 2)
        left = 92 + column * 516
        top = 200 + row * 150
        picture.box((left, top, left + 492, top + 126), WHITE, color, radius=12)
        picture.text((left + 22, top + 14), name, 21, color, True, width=448)
        picture.text((left + 22, top + 56), detail, 17, MUTED, width=448)
    picture.note((92, 528, 1108, 620), "共享名单的坑：",
                 "model providers 跟上下文文件无关，却与它们共享 disabledProviders 名单——关错了会连模型一起关。",
                 ORANGE, PEACH)
    picture.footer("适配器如 native / claude / cursor；skills 与普通 rule 见第 19 章。")


def session_questions(picture: Drawing):
    picture.header("第 7 章 · 卡住时先问三个问题",
                   "你要动的是哪一层？",
                   "答案决定用哪条命令。")
    pairs = (("屏幕上的字", "/clear", ORANGE),
             ("磁盘上的本", "/new · /fork", BLUE),
             ("供应商那边的缓存句柄", "/fresh", GREEN))
    for index, (question, answer, color) in enumerate(pairs):
        top = 200 + index * 116
        picture.box((110, top, 1108, top + 92), WHITE, color, radius=12)
        picture.text((136, top + 12), question, 22, color, True, width=620)
        picture.text((820, top + 16), answer, 22, INK, True, width=260)
    picture.note((92, 566, 1108, 664), "streaming 中的拒绝：",
                 "/fresh 拒绝；/clear 拒绝（若在压缩会先中止压缩）；裸 /fork 警告并挡住。",
                 ORANGE, PEACH)
    picture.footer("「命令没反应」先看是不是还在生成——中止当前轮再试。")


def edit_modes(picture: Drawing):
    picture.header("第 9 章 · edit 选哪条线协议",
                   "resolveEditMode() 的顺序，越靠前越优先。",
                   "日常记住：默认按 hashline 读文档就对了。")
    steps = (("① 模型相关配置变体", "按模型族推", ORANGE),
             ("② PI_EDIT_VARIANT", "环境变量压过设置", BLUE),
             ("③ edit.mode", "设置项", GREEN),
             ("④ 默认 hashline", "以上都没写就落到这里", ORANGE))
    for index, (title, detail, color) in enumerate(steps):
        top = 196 + index * 92
        picture.box((110, top, 1108, top + 72), WHITE, color, radius=10)
        picture.badge((144, top + 36), index + 1, color)
        picture.text((186, top + 10), title, 21, color, True, width=560)
        picture.text((700, top + 16), detail, 18, MUTED, width=392)
    picture.note((92, 566, 1108, 664), "两种模式风险：",
                 "PI_STRICT_EDIT_MODE 可关掉个别模型族的回退；edit 是 strict 且排他并发，别指望两个 edit 抢着写。",
                 BLUE, SKY)
    picture.footer("模式列表：hashline / apply_patch / patch / replace / sloppy。")


def secret_scan(picture: Drawing):
    picture.header("第 27 章 · 密钥扫描怎么不吓人",
                   "把判据写死，只报告不改。",
                   "每条给文件:行号与前 6 个字符。")
    shapes = (("sk- 开头的长串", "OpenAI 风格 API key", ORANGE),
              ("AKIA 开头的 20 位大写字母数字", "AWS access key id", BLUE),
              ("-----BEGIN 开头的私钥块", "PEM 私钥", GREEN),
              ("://user:口令@ 形式的 URL", "连接串里的凭据", ORANGE))
    for index, (shape, meaning, color) in enumerate(shapes):
        top = 196 + index * 96
        picture.box((110, top, 1108, top + 76), WHITE, color, radius=10)
        picture.text((136, top + 10), shape, 20, color, True, width=620)
        picture.text((800, top + 12), meaning, 17, MUTED, width=292)
    picture.box((92, 576, 1108, 640), WHITE, BLUE, radius=10)
    picture.text((116, 592), 'omp grep "sk-[A-Za-z0-9_-]{20,}" . --no-gitignore -l 100',
                 18, INK, width=960)
    picture.text((116, 614), "--no-gitignore 让被忽略的本地配置也进搜索；-l 100 封顶。",
                 16, MUTED, width=960)
    picture.footer("命中不等于泄露：fixture 与 .env.example 常误报——按文件判断，别一键替换。")


def acp_notifications(picture: Drawing):
    picture.header("第 15 章 · ACP 里的压缩通知",
                   "协议模式下，压缩事件要通知对端。",
                   "两条 JSON-RPC 扩展通知，就这两条。")
    picture.box((92, 200, 584, 420), WHITE, ORANGE, radius=12)
    picture.text((116, 216), "_omp/compaction/start", 20, ORANGE, True, width=444)
    picture.text((116, 260), "sessionId", 18, MUTED, width=444)
    picture.text((116, 292), "reason", 18, MUTED, width=444)
    picture.text((116, 324), "action", 18, MUTED, width=444)
    picture.box((616, 200, 1108, 420), WHITE, BLUE, radius=12)
    picture.text((640, 216), "_omp/compaction/end", 20, BLUE, True, width=444)
    picture.text((640, 260), "sessionId / action / aborted / willRetry", 16, MUTED, width=444)
    picture.text((640, 292), "可选：skipped / errorMessage", 16, MUTED, width=444)
    picture.text((640, 324), "可选：tokensBefore", 16, MUTED, width=444)
    picture.note((92, 444, 1108, 540), "谁该关心：",
                 "只跑 TUI 与你无关；嵌 ACP 时这是「UI 上为何写刚压缩过」的唯一来源，进度条挂这两条。",
                 GREEN, SAGE)
    picture.footer("不实现这两个通知的客户端可以直接忽略，不会报协议错。")


def backend_choice(picture: Drawing):
    picture.header("第 16 章 · 远程后端上线前",
                   "先答三个问题，再谈选哪个。",
                   "默认先在 local 或 mnemopi 建立直觉。")
    questions = (("数据出不出本机", "驻留与合规先定", ORANGE),
                 ("bank 范围有多大", "谁有权限、谁在写", BLUE),
                 ("后台合并语义", "什么时候合并、会不会改历史", GREEN))
    for index, (title, detail, color) in enumerate(questions):
        top = 200 + index * 108
        picture.box((110, top, 1108, top + 88), WHITE, color, radius=12)
        picture.text((136, top + 12), title, 22, color, True, width=620)
        picture.text((760, top + 16), detail, 18, MUTED, width=320)
    picture.note((92, 542, 1108, 636), "覆盖与边界：",
                 "HINDSIGHT_* 环境变量压过所有 hindsight.* 设置；Sharpshooter 适合决策文件，不适合当聊天备份盘。",
                 BLUE, SKY)
    picture.footer("人走了怎么撤销权限，也要提前写清。")


def model_vs_role(picture: Drawing):
    picture.header("第 17 章 · /model 与角色不是一回事",
                   "手动切换 ≠ 自动分流。",
                   "两者一起看，才不会被「上一层赢了」骗到。")
    picture.box((92, 200, 584, 400), WHITE, ORANGE, radius=12)
    picture.text((116, 216), "/model", 24, ORANGE, True, width=444)
    picture.text((116, 262), "改你正在聊的那一路", 19, INK, width=444)
    picture.text((116, 302), "只影响当前会话的选路", 18, MUTED, width=444)
    picture.box((616, 200, 1108, 400), WHITE, BLUE, radius=12)
    picture.text((640, 216), "角色映射", 24, BLUE, True, width=444)
    picture.text((640, 262), "决定自动分流时谁接盘", 19, INK, width=444)
    picture.text((640, 302), "子代理、advisor、计划各按角色走", 18, MUTED, width=444)
    picture.note((92, 424, 1108, 520), "别想当然：",
                 "手动切到旗舰，不等于子代理也升舱——角色值按第 17.2a 的六层生效。",
                 ORANGE, PEACH)
    picture.footer("models.yml 的 provider 级字段写死前，先查 docs/models.md 对照。")


def preview_failures(picture: Drawing):
    picture.header("第 26 章 · 预演失败的三种长相",
                   "匹配数、文件数、测试退出码——三个数对上才算过。",
                   "第三种最危险，因为「绿」让人放松。")
    shapes = (("① 匹配数 0", "路径/glob 写错，或目标被 .gitignore 排除", ORANGE),
              ("② 数对、测试红", "规则把字符串/快照/注释一起改了", BLUE),
              ("③ 绿、diff 超范围", "格式化钩子或 IDE 顺手改了", GREEN))
    for index, (title, detail, color) in enumerate(shapes):
        top = 200 + index * 116
        picture.box((110, top, 1108, top + 92), WHITE, color, radius=12)
        picture.text((136, top + 12), title, 22, color, True, width=620)
        picture.text((136, top + 54), detail, 18, MUTED, width=920)
    picture.note((92, 560, 1108, 664), "退出预演的动作：",
                 "git checkout -- <超范围文件> 逐个退回；别在超范围 diff 上再叠第二片。",
                 ORANGE, PEACH)
    picture.footer("确认命令：omp grep -c <旧名> <路径> --no-gitignore；数数只用 -c。")


def read_selectors(picture: Drawing):
    picture.header("第 8 章 · read 的选择器",
                   "只有尾巴长得合法才切开。",
                   "行号从 1 起；字面路径优先。")
    suffixes = ((":raw", "原样输出，关摘要与行前缀", ORANGE),
                (":img", "把 .svg/.svgz 栅格化喂视觉输入", BLUE),
                (":conflicts", "扫 Git 冲突区，给紧凑索引", GREEN),
                (":N / :A-B / :A+C / :-N", "行范围四形态", ORANGE),
                (":R1,R2,...", "多段范围，先排序合并", BLUE))
    for index, (suffix, meaning, color) in enumerate(suffixes):
        top = 196 + index * 92
        picture.box((110, top, 1108, top + 72), WHITE, color, radius=10)
        picture.text((136, top + 10), suffix, 20, color, True, width=520)
        picture.text((700, top + 16), meaning, 17, MUTED, width=392)
    picture.note((92, 566, 1108, 660), "两个易错点：",
                 ":0 会报错；主机带端口时先写尾斜杠，如 https://example.com/:80。",
                 ORANGE, PEACH)
    picture.footer("归档与 SQLite 吃自己的冒号语法，别拿普通行选择器硬套。")


def truncation_fields(picture: Drawing):
    picture.header("第 10 章 · 截断是可读的字段",
                   "不是感觉，是 details 里的证据。",
                   "看到就让 agent 改命令，别假定它看见了全量。")
    fields = (("details.meta.truncation", "在内存里被截断", ORANGE),
              ("artifactId", "溢出到 artifact 时附带", BLUE),
              ("details.timedOut", "超时标记为 true", GREEN),
              ("Command exited with code <n>", "非零退出，结果标 isError", ORANGE))
    for index, (field, meaning, color) in enumerate(fields):
        top = 196 + index * 96
        picture.box((110, top, 1108, top + 76), WHITE, color, radius=10)
        picture.text((136, top + 10), field, 19, color, True, width=580)
        picture.text((740, top + 14), meaning, 17, MUTED, width=352)
    picture.note((92, 580, 1108, 664), "副作用清单（允许高风险命令前过一遍）：",
                 "改文件 / 装包 / 移数据库；监听端口 / 拉容器 / 写 systemd；对远程主机的 ssh。",
                 ORANGE, PEACH)
    picture.footer("正确处理：加过滤、降日志级别、写到文件再 read——别催模型复述。")


def task_ticket(picture: Drawing):
    picture.header("第 13 章 · 任务说明像委派工单",
                   "写得像另一个人明天才读到的工单。",
                   "四条齐全，子代理才少跑偏。")
    parts = (("目标一句话", "要什么结果，不要过程", ORANGE),
             ("允许 / 禁止", "工具与路径的边界", BLUE),
             ("交付格式", "例如只返回文件列表与结论", GREEN),
             ("完成标准", "怎样算做完，可验收", ORANGE))
    for index, (title, detail, color) in enumerate(parts):
        top = 200 + index * 104
        picture.box((110, top, 1108, top + 84), WHITE, color, radius=10)
        picture.badge((144, top + 42), index + 1, color)
        picture.text((186, top + 12), title, 21, color, True, width=560)
        picture.text((700, top + 18), detail, 18, MUTED, width=392)
    picture.note((92, 630, 1108, 712), "两个实现细节：",
                 "批量调用有必填 context；要机器可读就传 outputSchema——strict 失败，permissive 带警告收下。",
                 BLUE, SKY)
    picture.footer("拿子代理结论驱动下一步时，用 strict。")


def permission_matrix(picture: Drawing):
    picture.header("第 29 章 · 团队权限矩阵",
                   "四类能力，默认与升级条件分开写。",
                   "写进团队表格，别口头约定。")
    rows = (("只读巡检技能", "全员", "无", ORANGE),
            ("写生产工具", "关闭", "双人审批与审计", BLUE),
            ("发外消息钩子", "预览必过", "频道白名单", GREEN),
            ("自动更新扩展", "关闭", "变更窗口与钉版本", ORANGE))
    picture.text((136, 196), "能力", 19, MUTED, True, width=400)
    picture.text((560, 196), "默认", 19, MUTED, True, width=200)
    picture.text((760, 196), "升级条件", 19, MUTED, True, width=330)
    for index, (ability, default, upgrade, color) in enumerate(rows):
        top = 228 + index * 92
        picture.box((110, top, 1108, top + 72), WHITE, color, radius=10)
        picture.text((136, top + 20), ability, 20, color, True, width=400)
        picture.text((560, top + 22), default, 18, INK, width=200)
        picture.text((760, top + 22), upgrade, 18, MUTED, width=330)
    picture.footer("矩阵是团队公约：默认值可读，升级路径可审。")



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
    "fig7-1-session-git": session_git,
    "fig7-2-fork-resume": fork_resume,
    "fig7-3-fresh-clear-new": fresh_clear_new,
    "fig7-4-export-share": export_share,
    "fig8-1-read-paths": read_paths,
    "fig8-2-grep-glob": grep_glob,
    "fig8-3-ast-grep": ast_grep,
    "fig9-3-ast-edit-preview": ast_edit_preview,
    "fig10-1-bash-inprocess": bash_inprocess,
    "fig10-2-pty-background": pty_background,
    "fig10-3-eval-kernel": eval_kernel,
    "fig11-1-lsp-workbench": lsp_workbench,
    "fig11-2-debug-dap": debug_dap,
    "fig11-3-write-then-diagnose": write_then_diagnose,
    "fig12-1-browser-eval": browser_eval,
    "fig12-2-computer-desktop": computer_desktop,
    "fig13-1-todo-board": todo_board,
    "fig13-2-ask-options": ask_options,
    "fig13-3-task-subagent": task_subagent,
    "fig14-1-agents-md": agents_md,
    "fig14-2-foreign-configs": foreign_configs,
    "fig15-2-branch-summary": branch_summary,
    "fig16-2-sqlite-store": sqlite_store,
    "fig17-2-advisor": advisor,
    "fig18-1-magic-keywords": magic_keywords,
    "fig18-2-approval": approval_gate,
    "fig19-1-skill-layout": skill_layout,
    "fig19-3-skill-vs-ext": skill_vs_ext,
    "fig20-1-mcp-trust": mcp_trust,
    "fig20-3-mcp-review": mcp_review,
    "fig21-2-hooks": hooks,
    "fig21-3-hook-approve": hook_approve,
    "fig22-1-extension-factory": extension_factory,
    "fig22-3-reload": reload_plugins,
    "fig23-2-theme": theme,
    "fig23-3-keys": keys_isolation,
    "fig23-4-profile": profile_hats,
    "fig24-1-unknown-repo": unknown_repo,
    "fig24-4-project-flow": project_flow,
    "fig24-2-arch-sketch": arch_sketch,
    "fig24-5-agents-seed": agents_seed,
    "fig24-3-handoff-checklist": handoff_checklist,
    "fig24-6-loop": explore_loop,
    "fig25-4-bug-hunt": bug_hunt,
    "fig25-1-repro-first": repro_first,
    "fig25-2-debug-session": debug_session,
    "fig25-5-debug-tools": debug_tools,
    "fig25-3-red-green": red_green,
    "fig26-1-ast-refactor": ast_refactor,
    "fig26-2-task-shards": task_shards,
    "fig26-3-batch-rollback": batch_rollback,
    "fig27-2-atomic-commit": atomic_commit,
    "fig27-3-pr-body": pr_body,
    "fig28-2-sdk-events": sdk_events,
    "fig28-3-rpc-frames": rpc_frames,
    "fig29-1-team-pack": team_pack,
    "fig29-2-ext-tool": ext_tool,
    "fig29-3-distribute-trust": distribute_trust,
    "fig30-1-symptom-index": symptom_index,
    "fig30-2-auth-provider": auth_provider,
    "fig30-3-session-stuck": session_stuck,
    "fig31-1-trust-load": trust_load,
    "fig31-2-no-extensions": no_extensions,
    "fig31-3-secrets": secrets,
    "fig32-1-token-flow": token_flow,
    "fig32-2-role-cost": role_cost,
    "fig32-3-cache-compact": cache_compact,
    "fig33-1-callchain": callchain,
    "fig33-2-from-launch": from_launch,
    "figE-1-pin-version": pin_version,
    "figE-2-docs-vs-bin": docs_vs_bin,
    "figE-3-margin-notes": margin_notes,
    "fig15-1-compaction": compaction,
    "fig16-1-memory-loop": memory_loop,
    "figA-1-flag-layers": flag_layers,
    "figA-2-binary-probe": binary_probe,
    "figB-1-slash-vs-flag": slash_vs_flag,
    "figB-2-slash-not-shell": slash_not_shell,
    "figC-1-config-stack": config_stack,
    "figC-2-secrets-paths": secrets_paths,
    "figD-1-glossary-rings": glossary_rings,
    "figD-2-confusable-pairs": confusable_pairs,
    "fig14-3-discovery-ladder": discovery_ladder,
    "fig17-3-role-layers": role_layers,
    "fig15-3-rebuild-order": rebuild_order,
    "fig16-3-memory-urls": memory_urls,
    "fig18-3-keyword-switches": keyword_switches,
    "fig19-4-skill-triage": skill_triage,
    "fig20-4-mcp-precedence": mcp_precedence,
    "fig21-4-hook-returns": hook_returns,
    "fig22-4-registerables": registerables,
    "fig26-4-count-ledger": count_ledger,
    "fig27-4-review-replies": review_replies,
    "fig28-4-sdk-lifecycle": sdk_lifecycle,
    "fig29-4-pack-layers": pack_three_layers,
    "fig30-4-evidence-pack": evidence_pack,
    "fig31-4-secret-modes": secret_modes,
    "fig32-4-cost-leaks": cost_leaks,
    "fig33-4-six-step-chain": six_step_chain,
    "figA-3-subcommand-grid": subcommand_grid,
    "figB-3-lookup-order": lookup_order,
    "figC-3-verify-script": verify_script,
    "figD-3-recall-drill": recall_drill,
    "fig1-4-three-outcomes": three_outcomes,
    "fig2-4-desk-pile": desk_pile,
    "fig3-4-tool-baskets": tool_baskets,
    "fig12-4-pick-four": pick_four,
    "fig13-4-collab-trio": collab_trio,
    "fig8-4-read-hunt": read_hunt,
    "fig9-4-patch-forms": patch_forms,
    "fig10-4-two-gates": two_gates,
    "fig15-4-compaction-keys": compaction_keys,
    "fig16-4-learn-timing": learn_timing,
    "fig17-4-role-routing": role_routing,
    "fig18-4-plan-keys": plan_keys,
    "figA-4-mode-matrix": mode_matrix,
    "figB-4-slash-vs-keyword": slash_vs_keyword,
    "figC-4-embed-diff": embed_diff,
    "figE-4-uncovered": uncovered_gaps,
    "fig11-5-lsp-switches": lsp_switches,
    "fig23-5-config-actions": config_actions,
    "figD-4-pipeline-vs-approval": pipeline_vs_approval,
    "fig0-1-reading-map": reading_map,
    "fig19-5-skill-lifecycle": skill_lifecycle,
    "fig21-5-hook-audit": hook_audit,
    "fig22-5-ext-acceptance": ext_acceptance,
    "fig20-5-mcp-ticket": mcp_ticket,
    "fig31-5-secret-shapes": secret_shapes,
    "fig32-5-cost-review": cost_review,
    "fig30-5-incident-pack": incident_pack,
    "fig23-6-config-diary": config_diary,
    "fig24-7-antipatterns": antipatterns,
    "fig28-5-embed-checklist": embed_checklist,
    "fig33-5-three-deceptions": three_deceptions,
    "fig14-4-four-names": four_names,
    "fig7-5-three-questions": session_questions,
    "fig9-5-edit-modes": edit_modes,
    "fig27-5-secret-scan": secret_scan,
    "fig15-5-acp-notifications": acp_notifications,
    "fig16-5-backend-choice": backend_choice,
    "fig17-5-model-vs-role": model_vs_role,
    "fig26-5-preview-failures": preview_failures,
    "fig8-5-read-selectors": read_selectors,
    "fig10-5-truncation-fields": truncation_fields,
    "fig13-5-task-ticket": task_ticket,
    "fig29-5-permission-matrix": permission_matrix,
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


def encode_jpeg(image, subsampling: int) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=80, subsampling=subsampling,
               optimize=True, dpi=(300, 300))
    return buffer.getvalue()


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
            raw = encode_jpeg(image, subsampling=0)
            if len(raw) > MAX_JPEG_BYTES:
                # Flat-colour plates tolerate 4:2:0; step down before failing.
                raw = encode_jpeg(image, subsampling=2)
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
