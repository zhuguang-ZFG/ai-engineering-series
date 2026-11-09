"""Markdown -> HTML rendering pipeline for one unit of the book.

Pipeline: synthesize H1 -> python-markdown (toc/codehilite/extra) ->
callout classify -> external-link footnotes -> table wrap -> mermaid
figures -> id prefix -> cross-ref autolink (inserted after prefix so the
global anchors stay unprefixed) -> plain-layer marks -> heading collect ->
section tier chips.
"""
from __future__ import annotations

import html
import re
import unicodedata

from pathlib import Path

import markdown
from markdown.extensions.toc import TocExtension
from markdown.extensions.codehilite import CodeHiliteExtension

from .core import REPO_ROOT, BuildError, Unit
from .style import ink_mark, knot
from . import art, pages, plain
from .plates import (_PLATE_PH_RE, drawing_slots, floor_wide_svg, illu_figure,
                     mermaid_figure, plate_cap, plate_landscape)  # noqa: F401
from .refs import (RefLinker, _TAG_RE, _VOID_TAGS, footnotes_html, iter_doc,
                   process_links, resolve_local_links)

# ------------------------------------------------------------ callouts ----

CALLOUT_LABELS: dict[str, str] = {
    "最佳实践": "tip", "正确做法": "tip", "推荐做法": "tip",
    "反模式警告": "warning", "危险": "warning", "注意": "warning",
    "交叉引用": "info", "交叉引用提示": "info",
    "设计洞察": "concept", "原理": "concept",
    "best practice": "tip", "correct approach": "tip",
    "anti-pattern warning": "warning", "warning": "warning",
    "cross-reference": "info", "extended reflection": "info",
    "practical application scenarios": "info",
    "memories that should be saved": "tip",
    "memories that should not be saved": "warning",
    "design insight": "concept",
}
_LEAD_LABEL_RE = re.compile(
    r"<blockquote>\s*<p>\s*<strong>([^<]+?)\s*[：:]\s*</strong>")


def classify_callouts(doc: str, lang: str) -> str:
    def repl(m):
        raw = m.group(1).strip()
        key = re.sub(r"\s*[（(].*?[)）]\s*", "", raw).lower()
        ctype = CALLOUT_LABELS.get(key)
        if ctype is None:
            ctype = "note" if re.match(r"[A-Z]?[\w ]{2,40}$", raw) and \
                raw.lower() in {"learning objectives", "reference answer",
                                "reference answers", "reference answer hints"} \
                else None
            if ctype is None:
                return m.group(0)
        icon = ink_mark(ctype)
        colon = pages.COLON[lang]
        # balanced: the original paragraph's </p> closes callout-body
        return (f'<blockquote class="callout callout-{ctype}">'
                f'<p class="callout-tag">'
                f'<span class="callout-icon" aria-hidden="true">{icon}</span>'
                f'<strong>{html.escape(raw)}{colon}</strong></p>'
                f'<p class="callout-body">')
    return _LEAD_LABEL_RE.sub(repl, doc)


_HR_RE = re.compile(r"<hr\s*/>")


def ink_rules(doc: str) -> str:
    """A `---` in the manuscript is a scene change. Typeset as a drawn coupling
    between two hairlines instead of a diamond out of the font."""
    return _HR_RE.sub(f'<div class="hr-rule" aria-hidden="true">{knot()}</div>',
                      doc)


# --------------------------------------------------------------- links ----

_CURL_SKIP = {"code", "pre", "svg", "style", "kbd", "samp", "var", "textarea"}


# --------------------------------------------------------------- tables ---

_TABLE_RE = re.compile(r"<table>.*?</table>", re.S)


def wrap_tables(doc: str) -> str:
    def repl(m):
        t = m.group(0)
        cols = t.count("<th") or t.count("<td") or 1
        return f'<div class="table-scroll" data-cols="{cols}" tabindex="0">{t}</div>'
    return _TABLE_RE.sub(repl, doc)


# ------------------------------------------------------------- name breaks --

_LONG_RUN = re.compile(r"\S{12,}")
_BREAK_AFTER = re.compile(r"[_/]+")
_CAMEL = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")
_NAME_BREAK_SKIP = {"svg", "style", "script", "textarea", "pre",
                    "h1", "h2", "h3", "h4", "h5", "h6"}


def _break_offsets(run: str) -> list[int]:
    """Character indices inside `run` where a line may break without damage."""
    cuts = {m.end() for m in _BREAK_AFTER.finditer(run)}
    cuts |= {m.start() for m in _CAMEL.finditer(run)}
    return sorted(c for c in cuts if 0 < c < len(run))


def soften_long_names(doc: str) -> str:
    """Give `FLAG_NAME_WITH_UNDERSCORES`, `skipDangerousMode…` and
    `~/.claude/settings.json` a place to break.

    Justified prose stretches badly when the next token cannot be cut: at
    desktop width 56 distinct inline tokens took more than 30% of a line on
    their own, and `getFeatureValue_CACHED_MAY_BE_STALE` filled 96% of a
    390px line. `overflow-wrap` does not create a *preferred* break and does
    not feed min-content width either, so it fixes neither the rivers on
    screen nor the table that ran past the A4 page box; an explicit `<wbr>`
    does, and is only used when the name genuinely cannot fit.

    Only runs of twelve characters or more are even examined, and a run is
    left alone if it holds no separator or case boundary, so ordinary English
    words are never cut. Entities are copied through untouched -- the offsets
    are computed against the source text, and `&amp;` is not an identifier.
    """
    def repl(m):
        run = m.group(0)
        if "&" in run:
            return run
        cuts = _break_offsets(run)
        if not cuts:
            return run
        out, prev = [], 0
        for c in cuts:
            out.append(run[prev:c])
            out.append("<wbr>")
            prev = c
        out.append(run[prev:])
        return "".join(out)

    out = []
    for kind, text, blocked in iter_doc(doc, _NAME_BREAK_SKIP):
        out.append(text if kind == "tag" or blocked else _LONG_RUN.sub(repl, text))
    return "".join(out)


# ------------------------------------------------------------- unit close --

_CLOSER_TAGS = {"p", "ul", "ol", "aside", "blockquote", "div"}
_CLOSER_HEAVY = ("<table", "<figure", "<svg")


def glue_closer(doc: str, ornament: str) -> str:
    """Wrap the block a unit ends on together with the ruts that close it.

    Chromium honours `break-inside: avoid` but not `break-before: avoid`, so a
    rut that no longer fitted on the last page landed alone at the top of a
    fresh sheet -- and since the next unit opens with a forced break, that sheet
    stayed empty: three of them in the Chinese PDF, two in the English. Glued to
    the block it closes, the pair moves together and the page ends short instead
    of vanishing.

    Only a light tail is wrapped: a plate or a wide table is its own
    keep-together unit already, and anything tall enough to be one of those
    cannot be moved at all, so gluing to it would only buy a hole.
    """
    stack: list[tuple[str, int]] = []
    last: tuple[str, int, int] | None = None
    for m in _TAG_RE.finditer(doc):
        name = m.group(2).lower()
        if name in _VOID_TAGS or m.group(3):
            continue
        if m.group(1):
            if not stack or name not in [n for n, _ in stack]:
                continue
            while stack[-1][0] != name:
                stack.pop()
            opened, start = stack.pop()
            if not stack:
                last = (opened, start, m.end())
        else:
            stack.append((name, m.start()))
    if last is None or doc[last[2]:].strip():
        return doc + ornament
    name, start, end = last
    block = doc[start:end]
    if name not in _CLOSER_TAGS or any(t in block for t in _CLOSER_HEAVY):
        return doc + ornament
    if len(re.sub(r"<[^>]+>", "", block)) > 900 or block.count("\n") > 30:
        return doc + ornament
    return doc[:start] + f'<div class="ch-close">{block}{ornament}</div>' + doc[end:]


# ------------------------------------------------------------- code langs -

_CODE_DIV_RE = re.compile(r'<div class="codehilite">')
_CODE_PRE_RE = re.compile(r'(<div class="codehilite"[^>]*>)<pre>')


def stamp_code_langs(doc: str, langs: list[str], file: str) -> str:
    """Label each highlighted block with the language it was fenced as, so
    the stylesheet can print a corner chip. Position-matched, so a drift
    between source fences and rendered blocks must fail loudly.

    The pass also gives each block's scroller a tab stop: a long line runs
    past the column and the block, unlike a link, is otherwise unreachable
    without a mouse."""
    left = list(langs)
    found = len(_CODE_DIV_RE.findall(doc))
    if found != len(left):
        raise BuildError(f"{file}: {found} rendered code blocks but "
                         f"{len(left)} source fences")

    def repl(m):
        lang = left.pop(0)
        if not lang:
            return m.group(0)
        return f'<div class="codehilite" data-lang="{html.escape(lang)}">'
    doc = _CODE_DIV_RE.sub(repl, doc)
    return _CODE_PRE_RE.sub(r'\1<pre tabindex="0">', doc)


# -------------------------------------------------------------- mermaid ---

ART_REF = "illustrations/"
_IMG_TAG_RE = re.compile(r'<img\b([^>]*?)src="([^"]+)"([^>]*?)(/?)>')

def inline_images(doc: str, file: str) -> str:
    """Rewrite a photograph's src to a data URI, or say why it cannot.

    The audit counts any `<img>` whose src is not `data:` as a hole in the
    offline guarantee, so failing here is the friendly version of a red build
    on someone's plane. Unit-relative paths (omp hand-drawn `images/…`) resolve
    against the manuscript file and stay inside the repo root.
    """
    from .core import REPO_ROOT

    def repl(m):
        src = m.group(2)
        if src.startswith("data:"):
            return m.group(0)
        if src.startswith(ART_REF):
            return (f'<img{m.group(1)}src="{art.photo(src[len(ART_REF):])}"'
                    f'{m.group(3)}>')
        rel = (Path(file).parent / src).as_posix()
        path = (REPO_ROOT / rel).resolve()
        try:
            path.relative_to(REPO_ROOT.resolve())
        except ValueError as exc:
            raise BuildError(
                f"{file}: <img src=\"{src}\"> escapes the repository"
            ) from exc
        if not path.is_file():
            raise BuildError(f"{file}: <img src=\"{src}\"> missing at {rel}")
        return (f'<img{m.group(1)}src="{art.photo_path(path, label=rel)}"'
                f'{m.group(3)}>')
    return _IMG_TAG_RE.sub(repl, doc)


# a hand-drawn plate is written as a captioned pair:
#   ![图13-1 任务板](images/fig13-1-todo-board.jpg)
#   *图13-1：任务板在第二轮的样子。*
# Left as two paragraphs that pair reads as a screenshot dropped into prose and
# the figure furniture (frame, hairline caption, bronze number, scroll reveal)
# never applies. This is the one place that sees both lines, so the wrap lives
# here. Figures already carrying a caption of their own (`figure.illu-line`)
# are untouched: they never come through as a bare `<img>` paragraph.
_PHOTO_PARA_RE = re.compile(
    r'<p>(<img\b[^>]*alt="图(?:[A-Za-z]|\d+)-\d+[^"]*"[^>]*>)</p>'
    r"(?:\s*<p><em>(.*?)</em></p>)?", re.S)


def photo_figures(doc: str) -> str:
    """Promote a captioned plate `<img>` pair into a real `<figure>`."""
    def repl(m):
        img, caption = m.group(1), (m.group(2) or "").strip()
        alt = re.search(r'alt="([^"]*)"', img)
        alt = alt.group(1) if alt else ""
        number = re.match(r"(图(?:[A-Za-z]|\d+)-\d+)", alt)
        number = number.group(1) if number else ""
        label = caption or alt
        label = re.sub(r"^图(?:[A-Za-z]|\d+)-\d+\s*[：:]\s*", "", label)
        head = f'<span class="fig-no">{number}</span>' if number else ""
        tail = (f'<figcaption>{head}<span class="fig-cap">{label}</span>'
                f"</figcaption>") if label else ""
        return (f'<figure class="illu illu-photo">'
                f'<div class="illu-frame">{img}</div>{tail}</figure>')
    return _PHOTO_PARA_RE.sub(repl, doc)


# ---------------------------------------------------------------- ids -----

_STRAY_ANGLE = re.compile(r"<[A-Za-z][A-Za-z0-9_]*"
                          r"(?:[,\s]+[A-Za-z0-9_=?<>.'’]+)+>")


def escape_stray_angles(md_text: str) -> str:
    """Type-parameter notation like Tool<I,O,P> in prose is invalid HTML and
    would be swallowed by browsers; fence/code spans are left untouched."""
    lines, fence = [], None
    for line in md_text.split("\n"):
        m = re.match(r"^\s*(`{3,}|~{3,})(.*)$", line)
        if m:
            token, info = m.group(1), m.group(2).strip()
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence) and not info:
                fence = None
            lines.append(line)
            continue
        if fence is not None:
            lines.append(line)
            continue
        parts = re.split(r"(`+[^`]*`+)", line)
        for i, seg in enumerate(parts):
            if i % 2 == 0 and "<" in seg:
                parts[i] = _STRAY_ANGLE.sub(
                    lambda mm: mm.group(0).replace("<", "&lt;").replace(
                        ">", "&gt;"), seg)
        lines.append("".join(parts))
    return "\n".join(lines)

def prefix_ids(doc: str, pfx: str) -> str:
    doc = re.sub(rf'\bid="(?!mm-|fig-)((?!{pfx}-)[^"]+)"',
                 rf'id="{pfx}-\1"', doc)
    doc = re.sub(r'href="#(?!fn-)((?!{0}-)[^"]+)"'.format(pfx),
                 rf'href="#{pfx}-\1"', doc)
    doc = doc.replace('href="#fn-', f'href="#{pfx}-fn-')
    return doc


# ------------------------------------------------------------ slugify ----

def book_slug(value: str, separator: str = "-") -> str:
    s = unicodedata.normalize("NFKC", value).strip().lower()
    s = re.sub(r"[`*_~\[\]()（）「」：:，,。.；;/\\]", "", s)
    s = re.sub(r"[^\w一-鿿-]", " ", s)
    s = re.sub(r"\s+", separator, s.strip())
    return s or "section"


# ------------------------------------------------------------- render ----

def build_md():
    return markdown.Markdown(extensions=[
        "extra", "sane_lists",
        TocExtension(slugify=book_slug, permalink=False),
        CodeHiliteExtension(language="text", guess_lang=False, linenums=False),
    ])


def curlify(doc: str) -> str:
    """Straight double quotes → typographic pairs in prose, never in code."""
    state = [0]

    def flip(_m):
        state[0] += 1
        return "“" if state[0] % 2 else "”"

    out, skip = [], None
    for piece in re.split(r"(<[^>]+>)", doc):
        if piece.startswith("<") and piece.endswith(">"):
            m = re.match(r"</?([a-zA-Z][\w-]*)", piece)
            name = m.group(1).lower() if m else ""
            if piece.startswith("</"):
                if name == skip:
                    skip = None
            elif skip is None and name in _CURL_SKIP:
                skip = name
            out.append(piece)
            continue
        out.append(re.sub(r'"', flip, piece) if not skip else piece)
    return "".join(out)


def render_unit(unit: Unit, mapping: dict[str, str], *,
                diagrams: dict[str, tuple[str, str]],
                autolink: bool = True, gloss=None,
                tiers: list[str] | None = None,
                local_targets: dict[str, str] | None = None) -> dict:
    body = re.sub(r"\A[ \t]*>[ \t]*(English|中文)[^\n]*\n+", "", unit.md)
    if unit.kind == "front":
        h1 = f"# {unit.title}"
    elif unit.lang == "zh":
        h1 = f"# {unit.no}　{unit.title}"
    else:
        h1 = f"# {unit.no}: {unit.title}"

    md = build_md()
    doc = curlify(md.convert(escape_stray_angles(h1 + "\n\n" + body)))
    doc = stamp_code_langs(doc, unit.code_langs, unit.path)

    external: list[str] = []
    doc = classify_callouts(doc, unit.lang)
    doc = ink_rules(doc)
    if local_targets is not None:
        doc = resolve_local_links(doc, unit.path, local_targets, REPO_ROOT,
                                  chapters=False)
    doc = process_links(doc, external)
    doc += footnotes_html(external, unit.lang)
    doc = wrap_tables(doc)

    ch_num = re.sub(r"\D", "", unit.no) or ""
    apx_letter = unit.id[-1].upper()
    fig_seq = [0]

    def fig_no():
        fig_seq[0] += 1
        if unit.kind == "chapter":
            return f"{int(ch_num)}-{fig_seq[0]}"
        if unit.kind == "front":
            # front matter has no number to inherit; plain digits read better
            # than the "T" that unit.id[-1] would give 前言/front
            return f"{fig_seq[0]}"
        return f"{apx_letter}{fig_seq[0]}"

    slots = drawing_slots(unit)

    def plate_repl(m):
        kind, uid = (m.group(1) or m.group(2)).split(":", 1)
        if kind == "ILL":
            entry = slots.get(uid)
            if entry is None:
                raise BuildError(
                    f"{unit.path}: an @@ILL:{uid}@@ placeholder with no "
                    "ill fence behind it")
            name, caption = entry
            svg = art.drawing(name)
            # a plate declares itself sequential by carrying the `seq` class on
            # its root, so the prose never has to say how to animate it
            art_kind = "seq" if art.SEQ_ROOT.search(svg) else "line"
            return illu_figure(uid, svg, fig_no(), caption, unit.lang,
                               art_kind)
        entry = diagrams.get(uid)
        if entry is None:
            return f'<div class="mermaid-missing">缺失图 {uid}</div>'
        caption, svg = entry
        return mermaid_figure(uid, svg, fig_no(), caption, unit.lang)
    doc = _PLATE_PH_RE.sub(plate_repl, doc)
    doc = inline_images(doc, unit.path)
    doc = photo_figures(doc)

    doc = prefix_ids(doc, unit.id)
    if local_targets is not None:
        doc = resolve_local_links(doc, unit.path, local_targets, REPO_ROOT,
                                  chapters=True)
    if autolink:
        doc = RefLinker(mapping, unit.id, unit.lang).transform(doc)

    new_terms: list[dict] = []
    if gloss is not None and gloss.active:
        doc, new_terms = gloss.apply(doc, tiers, who=unit.path)

    headings = [{"level": int(lvl), "id": hid,
                 "text": re.sub(r"<[^>]+>", "", txt)}
                for lvl, hid, txt in re.findall(
                    r'<h([234]) id="([^"]+)">(.*?)</h\1>', doc)]
    # stamped after the outline is collected: the chip belongs to the reader,
    # not to the section's name
    doc = plain.stamp_tiers(doc, tiers or [], unit.lang, who=unit.id)
    # the break points go in once the whole book is assembled, so the front and
    # back matter get them too — see build.py
    return {"unit": unit, "html": doc, "headings": headings,
            "external": external, "n_diagrams": fig_seq[0],
            "new_terms": new_terms}
