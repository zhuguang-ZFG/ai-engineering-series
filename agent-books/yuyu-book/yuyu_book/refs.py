"""Link handling and HTML text-run walking."""
from __future__ import annotations

import html
import posixpath
import re
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

_EXT_LINK_RE = re.compile(
    r'<a href="(https?://[^"]+)"(\s[^>]*)?>(.*?)</a>', re.S)
_SKIP_TAGS = {"a", "code", "pre", "h1", "svg", "style", "sup", "figure"}
_VOID_TAGS = ("br", "img", "hr", "meta", "input", "wbr")
_TAG_RE = re.compile(r"<(/?)([a-zA-Z][a-zA-Z0-9]*)[^>]*?(/)?>")
_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)


def resolve_local_links(doc: str, source: str, targets: dict[str, str],
                        repository: Path, *, chapters: bool) -> str:
    """Resolve chapter links after ID prefixing, source links before footnotes.

    Included chapters stay inside the offline book. Other existing repository
    files open their published source; paths outside the repository stay
    untouched so malformed links are still caught by the assembly audit.
    """
    root = repository.resolve()

    def replace(match):
        url = urlsplit(html.unescape(match.group(1)))
        if url.scheme or url.netloc or not url.path or url.path.startswith("/"):
            return match.group(0)
        path = posixpath.normpath(posixpath.join(
            posixpath.dirname(source), unquote(url.path)))
        if path == ".." or path.startswith("../"):
            return match.group(0)
        target = targets.get(path)
        if target:
            if not chapters:
                return match.group(0)
            fragment = unquote(url.fragment)
            anchor = target
            if fragment:
                anchor = (fragment if fragment == target or
                          fragment.startswith(target + "-")
                          else target + "-" + fragment)
            href = "#" + anchor
        else:
            if chapters:
                return match.group(0)
            file = (root / path).resolve()
            if not file.is_relative_to(root) or not file.is_file():
                return match.group(0)
            href = ("https://github.com/zhuguang-ZFG/ai-engineering-series/blob/main/"
                    "agent-books/" + quote(path, safe="/"))
            if url.fragment:
                href += "#" + url.fragment
        return 'href="' + html.escape(href, quote=True) + '"'

    return re.sub(r'\bhref="([^"]+)"', replace, doc)


def process_links(doc: str, external: list[str]) -> str:
    """External links get a superscript footnote marker; every chapter ends
    with the full URL list so the printed book keeps all references."""
    counter: dict[str, int] = {}

    def repl(m):
        url, attrs, label = m.group(1), m.group(2) or "", m.group(3)
        if "class=" in attrs or 'rel="' in attrs or "<a " in label:
            return m.group(0)
        first = url not in counter
        if first:
            external.append(url)
            counter[url] = len(external)
        num = counter[url]
        ref_id = f' id="fnref-{num}"' if first else ""
        return (f'<a class="ext" href="{url}" rel="noopener"{attrs}>{label}</a>'
                f'<sup class="fnum"><a href="#fn-{num}"{ref_id}>[{num}]</a></sup>')
    return _EXT_LINK_RE.sub(repl, doc)


def footnotes_html(external: list[str], lang: str) -> str:
    if not external:
        return ""
    # the list closes whichever unit it sits under — the foreword and the
    # appendices cite too, and are not chapters
    title = "引用链接" if lang == "zh" else "Cited links"
    items = "".join(
        f'<li id="fn-{i}"><a class="fn-url" href="{html.escape(u, True)}" '
        f'rel="noopener">{html.escape(u)}</a> '
        f'<a class="backref" href="#fnref-{i}" aria-label="back">↩</a></li>'
        for i, u in enumerate(external, 1))
    return (f'<aside class="chapter-notes"><h4 class="notes-title">{title}</h4>'
            f'<ol class="notes-list">{items}</ol></aside>')


def iter_doc(doc: str, skip_tags: set[str]):
    """Walk rendered HTML and yield (kind, text, blocked) chunks, 'tag' being
    markup copied through verbatim. `blocked` says an element in skip_tags
    still owns this run, so prose annotators never reach into code, links,
    plates or headings. Closing tags whose partner never opened (the mermaid
    SVGs are full of them) pop back to the matching level instead of
    corrupting the stack."""
    stack: list[str] = []
    pos = 0
    while True:
        m = _TAG_RE.search(doc, pos)
        comment = _COMMENT_RE.search(doc, pos)
        if comment and (m is None or comment.start() < m.start()):
            if comment.start() > pos:
                yield "text", doc[pos:comment.start()], \
                    any(name in skip_tags for name in stack)
            # A comment is markup, not prose: gloss and autolink must never
            # rewrite its text (a block marker contains the word `block`).
            yield "tag", comment.group(0), \
                any(name in skip_tags for name in stack)
            pos = comment.end()
            continue
        seg_end = m.start() if m else len(doc)
        blocked = any(name in skip_tags for name in stack)
        if seg_end > pos:
            yield "text", doc[pos:seg_end], blocked
        if not m:
            return
        closing, name, selfclose = m.group(1), m.group(2).lower(), m.group(3)
        if name in _VOID_TAGS or selfclose:
            pass
        elif closing:
            if name in stack:
                while stack and stack[-1] != name:
                    stack.pop()
                stack.pop()
        else:
            stack.append(name)
        yield "tag", m.group(0), blocked
        pos = m.end()


class RefLinker:
    """Wrap bare 第N章/Chapter N/附录X/Appendix X mentions in <a class=xref>.
    Skips subtrees of block/inline anchors; one link per target per text run."""

    def __init__(self, mapping: dict[str, str], current: str, lang: str):
        if lang == "zh":
            self.rx = re.compile(r"第\s*(\d{1,2})\s*章|附录\s*([A-D])")
        else:
            self.rx = re.compile(
                r"\bChapter\s+(\d{1,2})\b|\bAppendix\s+([A-D])\b")
        self.map = mapping
        self.current = current

    def transform(self, doc: str) -> str:
        out = []
        for kind, text, blocked in iter_doc(doc, _SKIP_TAGS):
            out.append(text if kind == "tag" or blocked
                       else self._link_text(text))
        return "".join(out)

    def _link_text(self, text: str) -> str:
        used: set[str] = set()
        out, last = [], 0
        for m in self.rx.finditer(text):
            g1, g2 = m.group(1), m.group(2)
            aid = f"ch{int(g1):02d}" if g1 else f"apx{g2.lower()}"
            anchor = self.map.get(aid)
            if not anchor or anchor == self.current or aid in used:
                continue
            used.add(aid)
            out.append(text[last:m.start()])
            out.append(f'<a class="xref" href="#{anchor}">{m.group(0)}</a>')
            last = m.end()
        out.append(text[last:])
        return "".join(out)
