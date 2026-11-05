"""Hand-inked SVG ornaments: the wheel, marks, traces and hairline knots."""
from __future__ import annotations

import math
import random
import re

WHEEL_SVG = """<svg class="wheel" viewBox="0 0 200 200" role="img" aria-hidden="true">
<defs><path id="spoke" d="M100 100q2.6-18.5.4-38.5t1.2-43.5"
 stroke="currentColor" stroke-width="2.4" stroke-linecap="round" fill="none"/></defs>
<path d="M104.5 12.6a88 89 0 0 1-2.4 175.4A89 87.2 0 0 1 104.5 12.6"
 fill="none" stroke="currentColor" stroke-width="5" stroke-linecap="round"/>
<path d="M101 28.4a72 73 0 0 1-1.6 143.2A72.8 71 0 0 1 101 28.4"
 fill="none" stroke="currentColor" stroke-width="2" opacity=".55" stroke-linecap="round"/>
<path d="M97 84.2a16 16.6 0 0 1 11.4 3.2 15.4 15 0 0 1-4.6 25.6 16.2 15.6 0 0 1-21-7.2 15.8 16.4 0 0 1 8.4-20.8"
 fill="none" stroke="currentColor" stroke-width="7" stroke-linecap="round"/>
<circle cx="100" cy="100" r="4" fill="currentColor"/>
<g opacity=".9">
<use href="#spoke"/><use href="#spoke" transform="rotate(15 100 100)"/>
<use href="#spoke" transform="rotate(30 100 100)"/><use href="#spoke" transform="rotate(45 100 100)"/>
<use href="#spoke" transform="rotate(60 100 100)"/><use href="#spoke" transform="rotate(75 100 100)"/>
<use href="#spoke" transform="rotate(90 100 100)"/><use href="#spoke" transform="rotate(105 100 100)"/>
<use href="#spoke" transform="rotate(120 100 100)"/><use href="#spoke" transform="rotate(135 100 100)"/>
<use href="#spoke" transform="rotate(150 100 100)"/><use href="#spoke" transform="rotate(165 100 100)"/>
<use href="#spoke" transform="rotate(180 100 100)"/><use href="#spoke" transform="rotate(195 100 100)"/>
<use href="#spoke" transform="rotate(210 100 100)"/><use href="#spoke" transform="rotate(225 100 100)"/>
<use href="#spoke" transform="rotate(240 100 100)"/><use href="#spoke" transform="rotate(255 100 100)"/>
<use href="#spoke" transform="rotate(270 100 100)"/><use href="#spoke" transform="rotate(285 100 100)"/>
<use href="#spoke" transform="rotate(300 100 100)"/><use href="#spoke" transform="rotate(315 100 100)"/>
<use href="#spoke" transform="rotate(330 100 100)"/><use href="#spoke" transform="rotate(345 100 100)"/>
</g></svg>"""


_WHEEL_N = 0


def wheel(size: int = 44) -> str:
    """Each instance needs its own spoke id — the SVG is inlined repeatedly."""
    global _WHEEL_N
    _WHEEL_N += 1
    sid = f"spoke{_WHEEL_N}"
    return (WHEEL_SVG
            .replace('viewBox', f'width="{size}" height="{size}" viewBox', 1)
            .replace('id="spoke"', f'id="{sid}"')
            .replace('href="#spoke"', f'href="#{sid}"'))


_INK_TAG = re.compile(r"<(path|circle)\b([^>]*?)(/?)>")
_INK_FILL = re.compile(r'fill\s*=\s*"currentColor"')


def _self_inking(svg: str) -> str:
    """Normalize every stroked shape to pathLength="100", so the stylesheet's
    scroll-driven ink-draw runs on generated marks exactly as it runs on the
    shipped illustrations. Dashed strokes keep their real-unit rhythm and fade
    instead; filled ink dots pop. Same rules as the emblem layer, one choke
    point for every generator that draws a road."""
    def _add(m: re.Match) -> str:
        tag, attrs, close = m.group(1), m.group(2), m.group(3)
        if ("pathLength" in attrs or "stroke-dasharray" in attrs
                or _INK_FILL.search(attrs)):
            return m.group(0)
        return f'<{tag}{attrs} pathLength="100"{close}>'
    return _INK_TAG.sub(_add, svg)


# ------------------------------------------------------- hand-inked marks ----
# Callouts used to open with a font glyph (✦ ⚠ ↗ ◎ ※), which is the one place in
# the book where the typeface had to speak for the drawing. These are the same
# five marks inked by hand in the emblems' idiom: a ring left open where the
# brush lifted, a triangle whose corners do not meet at a perfect angle, pads
# and stubs that route like a trace. Inline, currentColor, no ids -- a callout
# mark is repeated some seventy times per edition.
INK_MARKS = {
    "tip": ('<path d="M13.3 5.2C12.3 2.9 10.1 1.6 7.5 2 4.3 2.4 2 5.2 2.1 8.4'
            'c.1 3.2 2.7 5.7 5.9 5.6 3.1-.1 5.6-2.6 5.7-5.6.1-1.2-.1-2.3-.4-3.2"/>'
            '<path d="M5.2 8.3l2.1 2.3 3.9-5"/>'),
    "warning": ('<path d="M7.3 2.5 13.7 12.8c.3.6-.1 1.2-.7 1.2H3.1c-.7 0-1.1-.6'
                '-.8-1.2L6.6 2.5c.2-.5.5-.5.7 0z"/>'
                '<path d="M8 6.3v3.2"/>'
                '<circle cx="8" cy="11.5" r=".8" fill="currentColor" stroke="none"/>'),
    "info": ('<path d="M3.2 12.7C5.6 10.8 7.9 8.1 10.4 5"/>'
             '<path d="M6.8 4.7 10.6 4.5l.3 3.9"/>'),
    "concept": ('<path d="M8 1.9c3.4 0 6.2 2.7 6.1 6.2C14 11.5 11.4 14.1 8 14.1'
                '4.6 14.1 2 11.4 2 7.9 2 4.5 4.5 1.9 8 1.9z"/>'
                '<circle cx="8.1" cy="7.9" r="2.7" opacity=".7"/>'
                '<circle cx="8" cy="8" r=".9" fill="currentColor" stroke="none"/>'),
    "note": ('<path d="M8 2.5C7.8 6.1 7.8 9.7 8 13.5"/>'
             '<path d="M3.6 4.6C6 7.2 8.5 9.8 12.4 12.4"/>'
             '<path d="M12.4 4.6C10 7.2 7.5 9.8 3.6 12.4"/>'
             '<path opacity=".5" d="M2.7 8c3.5-.2 7.1-.2 10.6 0"/>'),
}


def ink_mark(kind: str) -> str:
    """A callout's drawn mark, or '' for a kind the book has not inked yet."""
    body = INK_MARKS.get(kind)
    if not body:
        return ""
    return (f'<svg class="ink-mark" viewBox="0 0 16 16" aria-hidden="true"'
            f' fill="none" stroke="currentColor" stroke-width="1.4"'
            f' stroke-linecap="round" stroke-linejoin="round">{body}</svg>')


def trace(seed: str) -> str:
    """The wire a chapter head closes on: one hand-run line with pads, a couple
    of stubs and two bends that lift it off the baseline, like a trace routing
    around a via. Seeded by the unit id, so no two chapters draw the same line
    and every rebuild draws the same one."""
    rng = random.Random(seed)
    width, base = 240.0, 11.0
    nodes, x = [], 5.0
    while x < width - 5.0:
        nodes.append((x, base + rng.uniform(-1.4, 1.4)))
        x += rng.uniform(23.0, 41.0)
    nodes.append((width - 5.0, base + rng.uniform(-1.4, 1.4)))
    if len(nodes) > 4:
        for i in rng.sample(range(1, len(nodes) - 1), 2):
            px, _ = nodes[i]
            nodes[i] = (px, base - rng.uniform(3.4, 4.8))
    d = "M{:.1f} {:.1f}".format(*nodes[0])
    for (ax, ay), (bx, by) in zip(nodes, nodes[1:]):
        d += (f"Q{(ax + bx) / 2:.1f} {(ay + by) / 2 + rng.uniform(-.9, .9):.1f}"
              f" {bx:.1f} {by:.1f}")
    out = [f'<path stroke-width="1.3" d="{d}"/>']
    # the wire always lands on a pad at its far end; the rest are wherever the
    # seed put them
    pads = [len(nodes) - 1] + rng.sample(range(len(nodes) - 1),
                                         min(3, len(nodes) - 1))
    for i in pads:
        px, py = nodes[i]
        out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="1.9" '
                   f'stroke-width="1.1"/>')
        if rng.random() < .6:
            down = 1 if py <= base else -1
            out.append(f'<path stroke-width="1" opacity=".65" '
                       f'd="M{px + 2.8:.1f} {py + 2.4 * down:.1f}'
                       f'l{rng.choice((5, 6, 7))} {3.4 * down}"/>')
    ex, ey = nodes[-1]
    out.append(f'<path stroke-width="1.2" d="M{ex + 1.8:.1f} {ey - 3.3:.1f}v6.6"/>')
    return _self_inking(
        f'<svg class="ch-trace" viewBox="0 0 250 22" aria-hidden="true"'
        f' fill="none" stroke="currentColor" stroke-linecap="round"'
        f' stroke-linejoin="round">{"".join(out)}</svg>')


def _mini_wheel(cx: float, cy: float, r: float, n: int = 8,
                phase: float = 0.0) -> str:
    """A spoked wheel worked out with arithmetic instead of <defs>/<use>, so it
    can be inlined a hundred times without ever owing the page an id."""
    out = [f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}"/>',
           f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r * .58:.2f}" opacity=".5"/>']
    for i in range(n):
        a = phase + i * 2 * math.pi / n
        out.append(
            f'<path d="M{cx + r * .26 * math.cos(a):.2f} {cy + r * .26 * math.sin(a):.2f}'
            f'L{cx + r * .9 * math.cos(a):.2f} {cy + r * .9 * math.sin(a):.2f}"/>')
    out.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="1" fill="currentColor"'
               ' stroke="none"/>')
    return "".join(out)


def route_map(seed: str, count: int) -> str:
    """The itinerary a part opens on: one road inked in a single run, a station
    ring for every chapter the part holds, a milepost between each pair, and the
    wheel the ride starts from. Seeded by the part id, so no two parts roll the
    same road and a rebuild rolls the same one."""
    count = max(int(count), 1)
    rng = random.Random(f"route:{seed}")
    base, first, last = 20.0, 46.0, 286.0
    if count == 1:
        stops = [(0.5 * (first + last), base)]
    else:
        step = (last - first) / (count - 1)
        stops = [(first + step * i, base + rng.uniform(-1.7, 1.7))
                 for i in range(count)]
    nodes = [(24.0, base)] + stops + [(314.0, base + rng.uniform(-1.2, 1.2))]
    d = "M{:.1f} {:.1f}".format(*nodes[0])
    for (ax, ay), (bx, by) in zip(nodes, nodes[1:]):
        d += (f"Q{(ax + bx) / 2:.1f} {(ay + by) / 2 + rng.uniform(-1.1, 1.1):.1f}"
              f" {bx:.1f} {by:.1f}")
    out = [f'<path stroke-width="1.3" d="{d}"/>',
           f'<g stroke-width="1.1">{_mini_wheel(13, base, 8.4)}</g>']
    for (ax, ay), (bx, by) in zip(stops, stops[1:]):
        # a stone set between the stations, at the height of the road itself
        mx, my = (ax + bx) / 2, (ay + by) / 2 + 4.4
        out.append(f'<path stroke-width="1" opacity=".45" '
                   f'd="M{mx:.1f} {my:.1f}v{rng.uniform(2.6, 3.8):.1f}"/>')
    for i, (sx, sy) in enumerate(stops):
        # the last stop of the part gets a second ring: the far end of the leg
        halo = f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="6" opacity=".35"/>' \
            if i == len(stops) - 1 and count > 1 else ""
        out.append(f'{halo}<circle cx="{sx:.1f}" cy="{sy:.1f}" r="3.3"'
                   f' stroke-width="1.2"/>'
                   f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="1.1" fill="currentColor"'
                   f' stroke="none"/>')
    return _self_inking(
        f'<svg class="pd-route" viewBox="0 0 320 40" aria-hidden="true"'
        f' fill="none" stroke="currentColor" stroke-linecap="round"'
        f' stroke-linejoin="round">{"".join(out)}</svg>')


def rut(seed: str) -> str:
    """The mark a chapter closes on: the two ruts the wheels left in the road,
    running out and fraying into dashes, with the grit the ride kicked up. It
    sits where a chapter end used to leave a bare band of paper, and like the
    head wire it is seeded by the unit id."""
    rng = random.Random(f"rut:{seed}")
    top, low = 8.4, 13.6

    def line(y0: float) -> str:
        nodes, x = [], 26.0
        while x < 190.0:
            nodes.append((x, y0 + rng.uniform(-.75, .75)))
            x += rng.uniform(24.0, 44.0)
        nodes.append((198.0, y0 + rng.uniform(-.4, .4)))
        d = "M{:.1f} {:.1f}".format(*nodes[0])
        for (ax, ay), (bx, by) in zip(nodes, nodes[1:]):
            d += (f"Q{(ax + bx) / 2:.1f} {(ay + by) / 2 + rng.uniform(-.6, .6):.1f}"
                  f" {bx:.1f} {by:.1f}")
        return d

    out = [f'<g stroke-width="1.25">{_mini_wheel(13, 11, 8.8)}</g>',
           f'<path stroke-width="1.35" d="{line(top)}"/>',
           f'<path stroke-width="1.25" opacity=".85" d="{line(low)}"/>']
    for i, (x, w) in enumerate(((204, 13.0), (221, 9.0), (233, 5.0))):
        y = (top, low)[i % 2] + rng.uniform(-.9, .9)
        out.append(f'<path stroke-width="1.15" opacity="{.62 - .12 * i:.2f}"'
                   f' d="M{x} {y:.1f}h{w}"/>')
    for _ in range(rng.randint(2, 3)):
        sx, sy = rng.uniform(40, 186), rng.uniform(top + 3.4, low + 3.2)
        out.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{rng.uniform(.6, 1.1):.1f}"'
                   f' opacity=".45" fill="currentColor" stroke="none"/>')
    return (f'<svg class="ch-rut" viewBox="0 0 250 22" aria-hidden="true"'
            f' fill="none" stroke="currentColor" stroke-linecap="round"'
            f' stroke-linejoin="round">{"".join(out)}</svg>')


def itinerary(seed: str, legs: list[tuple[str, list[tuple[str, str]]]],
              dashed_last: bool = True, start_label: str = "") -> str:
    """The whole book as one road, for the page that tells readers where to
    start: a leg per part, a ring per unit of that leg, and the appendices
    running dashed at the end because they are a siding, not a stop on the
    ride. Serpentine so the line never lifts off the sheet, seeded so the map
    is the same map every build. The drawing is decorative -- the list under it
    carries the same route as text, and links."""
    rng = random.Random(f"map:{seed}")
    width, x_lo, x_hi = 760.0, 58.0, 702.0
    y0, dy, pad = 54.0, 76.0, 96.0
    height = y0 + dy * (len(legs) - 1) + 38
    out: list[str] = []

    def run(nodes: list[tuple[float, float]]) -> str:
        d = "M{:.1f} {:.1f}".format(*nodes[0])
        for (ax, ay), (bx, by) in zip(nodes, nodes[1:]):
            d += (f"Q{(ax + bx) / 2:.1f} {(ay + by) / 2 + rng.uniform(-1.4, 1.4):.1f}"
                  f" {bx:.1f} {by:.1f}")
        return d

    for i, (label, stops) in enumerate(legs):
        y = y0 + i * dy
        right = i % 2 == 0
        d = 1 if right else -1
        sx, ex = (x_lo, x_hi) if right else (x_hi, x_lo)
        first = sx + d * pad
        n = max(len(stops), 1)
        xs = [first] if n == 1 else [first + (ex - d * 14 - first) * k / (n - 1)
                                     for k in range(n)]
        ys = [y + rng.uniform(-2.2, 2.2) for _ in range(n)]
        dashed = dashed_last and i == len(legs) - 1
        road = f'<path stroke-width="1.3" d="{run([(sx, y)] + list(zip(xs, ys)) + [(ex, y)])}"'
        if dashed:
            road += ' class="march m110" stroke-dasharray="6 5" opacity=".8"/>'
        else:
            road += "/>"
        out.append(road)
        if i + 1 < len(legs):
            ny = y + dy
            out.append(f'<path stroke-width="1.3" d="M{ex:.1f} {y:.1f}'
                       f'C{ex + d * 34:.1f} {y + dy * .18:.1f}'
                       f' {ex + d * 34:.1f} {ny - dy * .18:.1f} {ex:.1f} {ny:.1f}"/>')
        out.append(f'<text x="{sx + d * 4:.1f}" y="{y - 21:.1f}" '
                   f'text-anchor="{"start" if right else "end"}">{label}</text>')
        for (ax, ay), (bx, by) in zip(list(zip(xs, ys)), list(zip(xs, ys))[1:]):
            out.append(f'<path stroke-width="1" opacity=".4" '
                       f'd="M{(ax + bx) / 2:.1f} {(ay + by) / 2 + 4.2:.1f}v3.4"/>')
        for (anchor, ring), px, py in zip(stops, xs, ys):
            r = 2.7 if dashed else 3.6
            out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r}"'
                       f' stroke-width="1.2"/>'
                       f'<circle cx="{px:.1f}" cy="{py:.1f}" r="1.1" '
                       f'fill="currentColor" stroke="none"/>'
                       f'<text x="{px:.1f}" y="{py + 17:.1f}" '
                       f'text-anchor="middle">{ring}</text>')
        if i == 0:
            wx = sx - d * 22
            out.append(f'<g stroke-width="1.2">{_mini_wheel(wx, y, 9.2)}</g>')
            if start_label:
                out.append(f'<text x="{wx:.1f}" y="{y + 23:.1f}" '
                           f'text-anchor="middle">{start_label}</text>')
        if i == len(legs) - 1:
            out.append(f'<circle cx="{ex + d * 16:.1f}" cy="{y:.1f}" r="5.4" '
                       f'stroke-width="1.1" opacity=".75"/>'
                       f'<circle cx="{ex + d * 16:.1f}" cy="{y:.1f}" r="2.2"/>')
    return _self_inking(
        f'<svg class="itinerary" viewBox="0 0 {width:.0f} {height:.0f}"'
        f' aria-hidden="true" fill="none" stroke="currentColor"'
        f' stroke-linecap="round" stroke-linejoin="round">{"".join(out)}</svg>')


def key_mark(kind: str) -> str:
    """The legend for the route map: the wheel that starts the ride, one ring
    per stop, and the dashed siding the appendices run down. Worked out at the
    same radii as the map itself, so the key shows what the sheet actually
    draws rather than a plumper stand-in."""
    body = {
        "wheel": _mini_wheel(11, 11, 8.6),
        "ring": ('<circle cx="11" cy="11" r="3.6" stroke-width="1.2"/>'
                 '<circle cx="11" cy="11" r="1.1" fill="currentColor" stroke="none"/>'),
        "siding": ('<path stroke-width="1.3" stroke-dasharray="6 5" opacity=".8"'
                   ' d="M2 11h13.5"/>'
                   '<circle cx="18.6" cy="11" r="2.6" stroke-width="1.1"/>'),
    }[kind]
    return (f'<svg class="rmk rmk-{kind}" viewBox="0 0 22 22" aria-hidden="true"'
            f' fill="none" stroke="currentColor" stroke-width="1.2"'
            f' stroke-linecap="round" stroke-linejoin="round">{body}</svg>')


def knot() -> str:
    """The mark a section break carries: two pads joined by a coupling, drawn
    once and repeated ~110 times per edition, where a typed ❖ used to sit."""
    return ('<svg class="hr-knot" viewBox="0 0 56 14" aria-hidden="true"'
            ' fill="none" stroke="currentColor" stroke-width="1.2"'
            ' stroke-linecap="round">'
            '<path d="M2.4 7.2c3.6-.3 7.6-.3 11.6-.1"/>'
            '<circle cx="17.2" cy="7" r="2.7"/>'
            '<path d="M19.9 7c2.8-3.4 5.3-3.4 8.1 0s5.3 3.4 8.1 0"/>'
            '<circle cx="38.8" cy="7" r="2.7"/>'
            '<path d="M41.5 6.9c4-.2 8-.2 12.1.1"/></svg>')


