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
