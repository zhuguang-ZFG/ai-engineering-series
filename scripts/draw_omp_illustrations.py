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


FIGURES = {
    "fig1-1-agent-loop": agent_loop,
    "fig1-2-chat-vs-agent": chat_vs_agent,
    "fig2-1-context-desk": context_desk,
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
