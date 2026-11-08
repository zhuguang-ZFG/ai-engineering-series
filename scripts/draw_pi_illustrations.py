#!/usr/bin/env python3
"""Draw Pi's hand-drawn SVG tray: 25 emblems, 6 part plates, 6 body plates.

The drawings follow the same contract as the two existing trays: one <svg>
with a viewBox, no ids, no hrefs, no styles or scripts, everything stroked in
`currentColor`, and a byte budget per size. The hand is a deterministic
jitter: every coordinate is nudged by a seeded random offset, so a line is
never mechanically straight but the file is reproducible.

    python scripts/draw_pi_illustrations.py            # write the tray
    python scripts/draw_pi_illustrations.py --check    # validate only
"""
from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRAY = ROOT / "yuyu-book" / "illustrations-pi"
EMBLEM_BUDGET = 6000
PLATE_BUDGET = 6000
BODY_BUDGET = 20000


class Pen:
    def __init__(self, w: int, h: int, seed: int, width: float = 2.2):
        self.w, self.h, self.seed, self.width = w, h, seed, width
        self.parts: list[str] = []
        self.rng = random.Random(seed)

    def _r(self, amp: float) -> float:
        return self.rng.uniform(-amp, amp)

    def path(self, pts, amp: float = 0.6, close: bool = False,
             width: float | None = None, opacity: float | None = None) -> None:
        if len(pts) < 2:
            return
        d = [f"M{pts[0][0] + self._r(amp):.1f} {pts[0][1] + self._r(amp):.1f}"]
        for x, y in pts[1:]:
            d.append(f"L{x + self._r(amp):.1f} {y + self._r(amp):.1f}")
        if close:
            d.append("Z")
        attrs = ""
        if width is not None:
            attrs += f' stroke-width="{width}"'
        if opacity is not None:
            attrs += f' opacity="{opacity}"'
        self.parts.append(f'<path d="{" ".join(d)}"{attrs}/>')

    def box(self, x, y, w, h, amp=0.5, width=None, opacity=None) -> None:
        self.path([(x, y), (x + w, y), (x + w, y + h), (x, y + h)],
                  amp=amp, close=True, width=width, opacity=opacity)

    def circle(self, cx, cy, r, amp=0.4, width=None, opacity=None) -> None:
        attrs = ""
        if width is not None:
            attrs += f' stroke-width="{width}"'
        if opacity is not None:
            attrs += f' opacity="{opacity}"'
        self.parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" '
                          f'r="{r:.1f}"{attrs}/>')

    def dot(self, x, y, r=1.2, opacity=0.7) -> None:
        self.parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" '
                          f'fill="currentColor" stroke="none" opacity="{opacity}"/>')

    def hatch(self, x, y, w, h, n=5, step=4.0, opacity=0.35) -> None:
        for i in range(n):
            x0 = x + i * step
            self.path([(x0, y + h), (x0 + h * 0.6, y)], amp=0.5,
                      width=0.8, opacity=opacity)

    def arrow(self, x1, y1, x2, y2, amp=0.5, width=None) -> None:
        self.path([(x1, y1), (x2, y2)], amp=amp, width=width)
        a = math.atan2(y2 - y1, x2 - x1)
        for side in (-0.5, 0.5):
            self.path([(x2, y2),
                       (x2 - 5 * math.cos(a + side), y2 - 5 * math.sin(a + side))],
                      amp=0.3, width=width)

    def render(self, width: float) -> str:
        return (f'<svg viewBox="0 0 {self.w} {self.h}" fill="none" '
                f'stroke="currentColor" stroke-width="{width}" '
                f'stroke-linecap="round" stroke-linejoin="round">'
                + "".join(self.parts) + "</svg>")


# ---------------------------------------------------------------- motifs --
def m_loop(p: Pen):
    p.circle(32, 32, 15)
    p.arrow(46, 24, 41, 35)
    p.arrow(18, 40, 23, 29)
    p.path([(28, 26), (33, 31), (28, 36)])
    p.dot(32, 32)


def m_terminal(p: Pen):
    p.box(12, 16, 40, 32)
    p.path([(20, 26), (26, 32), (20, 38)])
    p.path([(30, 38), (40, 38)])
    p.path([(12, 24), (52, 24)], opacity=.5)


def m_key(p: Pen):
    p.circle(24, 32, 8)
    p.path([(32, 32), (50, 32)])
    p.path([(45, 32), (45, 38)])
    p.path([(50, 32), (50, 37)])
    p.dot(45, 39, 1.3, .85)
    p.dot(50, 38, 1.3, .85)
    p.dot(24, 32, 2)


def m_keys(p: Pen):
    for y in (22, 32, 42):
        for i in range(4):
            p.box(12 + i * 10, y, 7, 6, amp=.3, width=1.4)
    p.path([(8, 52), (56, 52)], opacity=.4)


def m_tree(p: Pen):
    p.path([(32, 52), (32, 36)])
    p.path([(32, 36), (18, 24)])
    p.path([(32, 36), (46, 24)])
    p.circle(18, 20, 4)
    p.circle(46, 20, 4)
    p.circle(32, 20, 3, opacity=.6)
    p.path([(46, 24), (52, 14)], opacity=.55)


def m_doc(p: Pen):
    p.box(18, 14, 28, 36)
    for y in (24, 30, 36):
        p.path([(24, y), (40, y)], opacity=.8)
    p.arrow(32, 12, 32, 4)
    p.path([(10, 26), (16, 26)])
    p.path([(48, 26), (54, 26)])


def m_compact(p: Pen):
    p.box(10, 24, 12, 16, amp=.4)
    p.box(42, 24, 12, 16, amp=.4)
    p.arrow(24, 32, 33, 32)
    p.arrow(40, 32, 31, 32)
    p.path([(27, 27), (32, 32), (27, 37)], opacity=.7)
    p.hatch(14, 26, 6, 12, 3, 3)


def m_stream(p: Pen):
    for i, y in enumerate((20, 28, 36, 44)):
        p.path([(10 + (i % 2) * 4, y), (54 - (i % 2) * 4, y)], width=2.2, opacity=.8)
    p.arrow(50, 12, 54, 20)
    p.dot(12, 12)
    p.path([(12, 12), (12, 16)], opacity=.5)


def m_turn(p: Pen):
    p.path([(12, 40), (12, 24), (28, 24), (28, 40), (44, 40), (44, 24), (52, 24)],
           amp=.5)
    p.arrow(48, 18, 52, 24)
    p.circle(12, 44, 3)
    p.circle(28, 44, 3)
    p.dot(44, 44)


def m_chip(p: Pen):
    p.box(20, 20, 24, 24, amp=.4)
    for i in range(3):
        p.path([(16, 24 + i * 8), (20, 24 + i * 8)], width=1.4)
        p.path([(44, 24 + i * 8), (48, 24 + i * 8)], width=1.4)
    for i in range(2):
        p.path([(24 + i * 8, 16), (24 + i * 8, 20)], width=1.4)
        p.path([(24 + i * 8, 44), (24 + i * 8, 48)], width=1.4)
    p.path([(52, 12), (56, 20), (52, 28)], opacity=.5)


def m_tools(p: Pen):
    p.path([(18, 46), (34, 30)])
    p.circle(38, 26, 8)
    p.path([(32, 20), (28, 16)])
    p.path([(16, 50), (12, 54)], opacity=.6)
    p.box(40, 38, 10, 10, amp=.3, opacity=.7)


def m_rows(p: Pen):
    for y in (16, 26, 36, 46):
        p.path([(14, y), (50, y)], opacity=.8)
        p.dot(11, y, 1)
    p.path([(32, 12), (32, 50)], width=.8, opacity=.3)


def m_screen(p: Pen):
    p.box(10, 14, 44, 32, amp=.4)
    p.path([(10, 22), (54, 22)], opacity=.6)
    for i in range(3):
        p.path([(16 + i * 8, 34), (20 + i * 8, 34)], width=1.2, opacity=.7)
    p.path([(34, 50), (34, 54)])
    p.path([(28, 54), (40, 54)])


def m_plug(p: Pen):
    p.box(14, 24, 16, 16, amp=.4)
    p.path([(30, 28), (40, 28)])
    p.path([(30, 36), (40, 36)])
    p.circle(46, 32, 6)
    p.path([(46, 26), (46, 18)], opacity=.6)
    p.dot(22, 32, 1.5)


def m_puzzle(p: Pen):
    p.path([(14, 30), (14, 18), (26, 18), (26, 24), (32, 24), (32, 18),
            (44, 18), (44, 30), (38, 30), (38, 36), (44, 42), (44, 50),
            (14, 50), (14, 42), (20, 42), (20, 36), (14, 36)], close=True, amp=.4)
    p.dot(29, 33, 1.4, .5)


def m_book(p: Pen):
    p.path([(32, 18), (16, 22), (16, 50), (32, 46), (48, 50), (48, 22)], close=True)
    p.path([(32, 18), (32, 46)], width=1.6, opacity=.6)
    p.path([(32, 12), (32, 18)], opacity=.5)
    p.dot(32, 10, 1.6)


def m_palette(p: Pen):
    p.circle(30, 32, 14)
    p.circle(30, 32, 4, opacity=.7)
    for a in (0, 90, 180, 270):
        x = 30 + 10 * math.cos(math.radians(a))
        y = 32 + 10 * math.sin(math.radians(a))
        p.dot(x, y, 1.6, .8)
    p.path([(44, 32), (54, 32)], opacity=.6)


def m_package(p: Pen):
    p.box(16, 22, 28, 24, amp=.4)
    p.path([(16, 30), (44, 30)], opacity=.6)
    p.path([(30, 22), (30, 30)], opacity=.6)
    p.path([(44, 26), (52, 26)], opacity=.5)
    p.path([(8, 52), (56, 52)], opacity=.3)


def m_api(p: Pen):
    p.path([(16, 20), (10, 32), (16, 44)])
    p.path([(44, 20), (50, 32), (44, 44)])
    p.circle(30, 26, 4)
    p.circle(30, 38, 4)
    p.path([(30, 30), (30, 34)], opacity=.6)


def m_delivery(p: Pen):
    p.box(12, 18, 22, 26, amp=.4)
    p.box(38, 26, 14, 18, amp=.4)
    p.path([(20, 28), (28, 28)], opacity=.7)
    p.path([(20, 34), (26, 34)], opacity=.7)
    p.arrow(44, 22, 50, 16)
    p.dot(50, 14, 2)


def m_pipeline(p: Pen):
    for i, x in enumerate((13, 27, 41)):
        p.box(x, 26, 10, 10, amp=.3)
        if i < 2:
            p.path([(x + 10, 31), (x + 14, 31)], width=1.2)
    p.path([(12, 20), (50, 20)], opacity=.4)
    p.path([(16, 44), (46, 44)], opacity=.4)


def m_lock(p: Pen):
    p.box(20, 28, 24, 18, amp=.4)
    p.path([(24, 28), (24, 22), (30, 18), (36, 18), (40, 22), (40, 28)], amp=.4)
    p.dot(32, 36, 1.6)
    p.path([(32, 38), (32, 42)], opacity=.6)


def m_scope(p: Pen):
    p.circle(28, 28, 12)
    p.path([(37, 37), (46, 46)])
    p.path([(28, 20), (28, 36)], opacity=.5)
    p.path([(20, 28), (36, 28)], opacity=.5)


def m_map(p: Pen):
    for x, y in ((12, 14), (36, 12), (16, 36), (40, 36), (26, 50)):
        p.box(x, y, 10, 8, amp=.3, width=1.3)
    p.path([(22, 18), (36, 16)])
    p.path([(21, 22), (22, 36)])
    p.path([(44, 20), (43, 36)])
    p.path([(26, 44), (31, 50)], opacity=.5)
    for x, y in ((22, 18), (36, 16), (22, 36), (43, 36)):
        p.dot(x, y, 1.2, .5)


def m_scales(p: Pen):
    p.path([(32, 14), (32, 50)])
    p.path([(18, 20), (46, 20)])
    p.path([(18, 20), (14, 32)])
    p.path([(18, 20), (22, 32)])
    p.path([(46, 20), (42, 32)])
    p.path([(46, 20), (50, 32)])
    p.path([(14, 32), (22, 32)], opacity=.6)
    p.path([(42, 32), (50, 32)], opacity=.6)
    p.path([(26, 52), (38, 52)])
    p.path([(32, 50), (28, 54)])
    p.path([(32, 50), (36, 54)])



def m_front(p: Pen):
    p.circle(32, 34, 12)
    p.circle(32, 34, 2, opacity=.8)
    for a in range(0, 360, 60):
        x = 32 + 17 * math.cos(math.radians(a))
        y = 34 + 17 * math.sin(math.radians(a))
        p.path([(x, y), (32 + 21 * math.cos(math.radians(a)),
                         34 + 21 * math.sin(math.radians(a)))], width=1.3)
    p.path([(32, 12), (32, 18)], opacity=.5)


def m_apxa(p: Pen):
    p.path([(18, 46), (18, 16)], opacity=.8)
    p.path([(18, 18), (38, 26), (18, 34)], close=True)
    p.path([(38, 44), (50, 44)], opacity=.6)
    p.path([(44, 40), (50, 44), (44, 48)], opacity=.6)


def m_apxb(p: Pen):
    p.path([(42, 14), (22, 50)], amp=.4)
    p.circle(22, 22, 4, opacity=.7)
    p.circle(42, 42, 4, opacity=.7)


def m_apxc(p: Pen):
    for i, y in enumerate((20, 32, 44)):
        p.path([(14, y), (50, y)], opacity=.7)
        p.circle(24 + i * 8, y, 4)
    p.dot(20, 20, 1.3, .5)


def m_apxd(p: Pen):
    p.path([(32, 16), (18, 20), (18, 48), (32, 44), (46, 48), (46, 20)], close=True)
    for y in (26, 32, 38):
        p.path([(22, y), (30, y)], width=1.1, opacity=.6)
        p.path([(34, y), (42, y)], width=1.1, opacity=.6)


def m_apxe(p: Pen):
    p.path([(20, 18), (46, 18), (46, 34), (32, 48), (18, 34), (18, 18)], close=True, amp=.4)
    p.circle(32, 26, 3)
    p.path([(32, 29), (32, 34)], opacity=.5)


EMBLEMS = {
    "ch01": m_loop, "ch02": m_terminal, "ch03": m_key, "ch04": m_keys,
    "ch05": m_tree, "ch06": m_doc, "ch07": m_compact, "ch08": m_stream,
    "ch09": m_turn, "ch10": m_chip, "ch11": m_tools, "ch12": m_rows,
    "ch13": m_screen, "ch14": m_plug, "ch15": m_puzzle, "ch16": m_book,
    "ch17": m_palette, "ch18": m_package, "ch19": m_api, "ch20": m_delivery,
    "ch21": m_pipeline, "ch22": m_lock, "ch23": m_scope, "ch24": m_map,
    "ch25": m_scales,
    "front": m_front, "apxa": m_apxa, "apxb": m_apxb,
    "apxc": m_apxc, "apxd": m_apxd, "apxe": m_apxe,
}


def emblem(name: str, seed: int) -> str:
    p = Pen(64, 64, seed, 2.2)
    EMBLEMS[name](p)
    p.hatch(10, 52, 6, 6, 3, 2.5, .25)
    p.dot(54, 12, 1.1, .35)
    p.dot(12, 50, .9, .3)
    return p.render(2.2)


PART_MOTIFS = {
    "p1": ("compass", 1), "p2": ("terminal", 2), "p3": ("gears", 3),
    "p4": ("modules", 4), "p5": ("road", 5), "p6": ("map", 6),
}


def part_plate(pid: str, seed: int) -> str:
    p = Pen(200, 140, seed, 1.6)
    if pid == "p1":
        p.circle(100, 66, 30)
        p.circle(100, 66, 3, opacity=.8)
        for a in range(0, 360, 45):
            x = 100 + 24 * math.cos(math.radians(a))
            y = 66 + 24 * math.sin(math.radians(a))
            p.dot(x, y, 1.6, .7)
        p.path([(100, 24), (100, 18)], opacity=.6)
        p.path([(100, 108), (100, 114)], opacity=.6)
    elif pid == "p2":
        p.box(48, 30, 104, 70, amp=.5)
        p.path([(48, 44), (152, 44)], opacity=.5)
        p.path([(64, 58), (78, 68), (64, 78)])
        for i in range(4):
            p.path([(92, 58 + i * 8), (136, 58 + i * 8)], width=1.2, opacity=.65)
    elif pid == "p3":
        p.circle(78, 66, 18)
        p.circle(78, 66, 7)
        for a in range(0, 360, 60):
            p.path([(78 + 18 * math.cos(math.radians(a)), 66 + 18 * math.sin(math.radians(a))),
                    (78 + 26 * math.cos(math.radians(a)), 66 + 26 * math.sin(math.radians(a)))])
        p.circle(132, 78, 12)
        p.circle(132, 78, 4)
        p.arrow(96, 66, 120, 74)
        p.path([(150, 40), (160, 40)], opacity=.4)
    elif pid == "p4":
        for x, y in ((36, 30), (76, 30), (116, 30), (56, 70), (96, 70), (136, 70)):
            p.box(x, y, 26, 22, amp=.4)
            p.dot(x + 13, y + 11, 1.4, .6)
        p.path([(62, 41), (76, 41)], opacity=.5)
        p.path([(102, 41), (116, 41)], opacity=.5)
        p.path([(69, 70), (76, 52)], opacity=.5)
        p.path([(109, 70), (116, 52)], opacity=.5)
    elif pid == "p5":
        p.path([(24, 104), (74, 96), (112, 72), (164, 46)], amp=1.2)
        for x, y in ((40, 102), (76, 94), (112, 72), (148, 54)):
            p.circle(x, y, 4)
            p.dot(x, y, 1.2, .8)
        p.path([(150, 38), (164, 46), (150, 54)], opacity=.7)
        p.hatch(30, 112, 10, 8, 4, 3, .25)
    else:
        for x, y in ((36, 26), (82, 20), (128, 28), (54, 66), (100, 58), (146, 66)):
            p.circle(x, y, 5)
            p.circle(x, y, 1.2, opacity=.8)
        p.path([(41, 26), (77, 21)])
        p.path([(87, 20), (123, 27)])
        p.path([(40, 30), (52, 62)])
        p.path([(84, 25), (58, 63)])
        p.path([(128, 32), (102, 57)])
        p.path([(150, 66), (150, 98)])
        p.path([(54, 70), (54, 98)])
    p.path([(20, 124), (180, 124)], opacity=.25)
    p.dot(172, 24, 1.4, .35)
    p.dot(28, 26, 1.0, .3)
    p.hatch(24, 112, 8, 8, 3, 3, .2)
    return p.render(1.6)


BODY = {
    "p1": ("loop", 11), "p2": ("daily", 12), "p3": ("engine", 13),
    "p4": ("modules", 14), "p5": ("delivery", 15), "p6": ("map", 16),
}


def body_plate(pid: str, seed: int) -> str:
    p = Pen(640, 360, seed, 1.8)
    p.path([(40, 320), (600, 318)], opacity=.18)
    if pid == "p1":
        p.circle(320, 170, 92)
        p.circle(320, 170, 22)
        p.arrow(398, 108, 418, 140)
        p.arrow(242, 232, 222, 200)
        p.path([(310, 140), (330, 170), (310, 200)])
        for i in range(4):
            p.box(96 + i * 118, 48, 74, 34, amp=.4, opacity=.55)
            p.dot(133 + i * 118, 65, 2, .5)
        p.path([(133, 82), (133, 112), (300, 112)], opacity=.35)
        p.hatch(72, 268, 14, 22, 6, 4, .25)
        p.hatch(556, 268, 14, 22, 6, 4, .25)
    elif pid == "p2":
        p.box(120, 60, 400, 220, amp=.8)
        p.path([(120, 104), (520, 104)], opacity=.5)
        p.path([(150, 130), (180, 160), (150, 190)])
        for i in range(6):
            p.path([(220, 134 + i * 22), (470, 134 + i * 22)], width=1.2, opacity=.55)
        p.path([(120, 232), (520, 232)], opacity=.3)
        p.arrow(300, 292, 300, 312)
        p.circle(300, 40, 10, opacity=.5)
    elif pid == "p3":
        for i in range(4):
            p.box(96, 60 + i * 62, 448, 44, amp=.5)
            p.path([(120, 82 + i * 62), (200, 82 + i * 62)], width=1.2, opacity=.6)
            p.dot(500, 82 + i * 62, 2, .5)
        p.arrow(320, 104, 320, 122)
        p.arrow(320, 166, 320, 184)
        p.arrow(320, 228, 320, 246)
        p.circle(320, 330, 12, opacity=.5)
        p.path([(320, 300), (320, 318)], opacity=.4)
    elif pid == "p4":
        for i, (x, y) in enumerate(((90, 70), (250, 70), (410, 70),
                                    (170, 210), (330, 210), (490, 210))):
            p.box(x, y, 90, 60, amp=.5)
            p.circle(x + 45, y + 30, 8, opacity=.6)
            p.dot(x + 45, y + 30, 2, .5)
        p.path([(180, 100), (250, 100)], opacity=.5)
        p.path([(340, 100), (410, 100)], opacity=.5)
        p.path([(295, 130), (260, 210)], opacity=.5)
        p.path([(355, 130), (390, 210)], opacity=.5)
        p.hatch(70, 300, 16, 18, 6, 4, .2)
    elif pid == "p5":
        p.path([(80, 300), (220, 270), (360, 190), (520, 96)], amp=1.6)
        for x, y in ((110, 292), (220, 270), (330, 205), (440, 140), (520, 96)):
            p.circle(x, y, 10)
            p.circle(x, y, 3, opacity=.7)
        p.path([(500, 70), (520, 96), (494, 118)], opacity=.7)
        p.box(70, 60, 120, 70, amp=.5, opacity=.55)
        p.path([(90, 82), (160, 82)], opacity=.5)
        p.path([(90, 100), (140, 100)], opacity=.5)
        p.hatch(520, 280, 18, 24, 7, 4, .22)
    else:
        for i, (x, y) in enumerate(((80, 70), (240, 50), (400, 80), (520, 60),
                                    (140, 190), (300, 170), (460, 200),
                                    (100, 290), (260, 280), (420, 300), (540, 250))):
            p.circle(x, y, 9)
            p.dot(x, y, 2.4, .5)
            if i % 2:
                p.path([(x, y + 9), (x, y + 26)], opacity=.35)
        for a, b in (((80, 70), (240, 50)), ((240, 50), (400, 80)),
                     ((400, 80), (520, 60)), ((80, 70), (140, 190)),
                     ((240, 50), (300, 170)), ((400, 80), (460, 200)),
                     ((140, 190), (100, 290)), ((300, 170), (260, 280)),
                     ((460, 200), (420, 300)), ((520, 60), (540, 250))):
            p.path([a, b], width=1.0, opacity=.3)
    p.dot(600, 40, 2, .25)
    p.dot(36, 44, 1.5, .2)
    return p.render(1.8)


def build() -> dict[Path, str]:
    files: dict[Path, str] = {}
    for i, name in enumerate(EMBLEMS, 1):
        files[TRAY / f"pi-{name}.svg"] = emblem(name, 100 + i)
    for i, pid in enumerate(PART_MOTIFS, 1):
        files[TRAY / f"part-pi-{pid}.svg"] = part_plate(pid, 200 + i)
    for i, pid in enumerate(BODY, 1):
        files[TRAY / f"pi-plate-{pid}.svg"] = body_plate(pid, 300 + i)
    return files


def validate(text: str, budget: int, label: str) -> None:
    size = len(text.encode("utf-8"))
    if size > budget:
        raise SystemExit(f"{label}: {size} bytes over {budget}")
    for banned in ("<script", "<style", "<iframe", "id=", "href=", "url("):
        if banned in text:
            raise SystemExit(f"{label}: contains {banned}")
    if not text.startswith("<svg") or "viewBox" not in text.split(">", 1)[0]:
        raise SystemExit(f"{label}: bad root")
    if "currentColor" not in text:
        raise SystemExit(f"{label}: no currentColor")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--out-dir", default=str(TRAY))
    args = ap.parse_args()
    out = Path(args.out_dir)
    files = build()
    for path, text in files.items():
        budget = BODY_BUDGET if path.name.startswith("pi-plate-") else (
            PLATE_BUDGET if path.name.startswith("part-") else EMBLEM_BUDGET)
        validate(text, budget, path.name)
    if args.check:
        print(f"{len(files)} drawings valid")
        return 0
    out.mkdir(parents=True, exist_ok=True)
    for path, text in files.items():
        (out / path.name).write_text(text + "\n", encoding="utf-8")
    total = sum(len(t.encode()) for t in files.values())
    print(f"wrote {len(files)} drawings to {out} ({total} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
