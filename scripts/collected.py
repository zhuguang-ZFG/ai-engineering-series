"""Merge the ten shipped books into one volume-numbered collected edition.

The collection is assembled from each book's own finished artifact, so every
volume keeps its native layout, numbering and cross-book prefixes. Only the
front matter (cover, master contents, one divider per volume) is generated.

Run from the series root:

    python series.py collected
    python series.py collected --date 2026-11-12

Nothing in the two source projects is rewritten; sources are read and the
collected artifacts are written under ``dist/``.
"""
from __future__ import annotations

import argparse
from datetime import date as _date
import hashlib
import json
from pathlib import Path
import posixpath
import re
import sys
import zipfile
from xml.etree import ElementTree
from xml.sax.saxutils import escape as xml_escape

import fitz

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import series  # noqa: E402  (the root router owns the catalog contract)

# The course comes first because the workbook and the harness books assume its
# vocabulary; the eight agent books then keep the order the series ships them.
ORDER = ("llm", "prompt", "book", "omp", "pi", "opencode", "deepseek", "hermes",
         "codex", "kimi")
CN_NUMBERS = ("一", "二", "三", "四", "五", "六", "七", "八", "九", "十")
A4 = (595.0, 842.0)
MARGIN = 64.0
TOC_TOP = 132.0
TOC_ROWS_PER_PAGE = 40
TOC_ROW_HEIGHT = 16.0
INK = (0.12, 0.12, 0.12)
MUTED = (0.42, 0.42, 0.42)


OPF_NS = {"opf": "http://www.idpf.org/2007/opf",
          "dc": "http://purl.org/dc/elements/1.1/",
          "cn": "urn:oasis:names:tc:opendocument:xmlns:container"}
ZIP_DATE = (1980, 1, 1, 0, 0, 0)


def volume_label(index: int) -> str:
    return f"卷{CN_NUMBERS[index]}"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def collection_plan(root: Path, catalog: dict, lang: str = "zh") -> list[dict]:
    """Ordered volumes, each pointing at the artifact it is merged from."""
    by_id = {book["id"]: book for book in catalog["books"]}
    if set(by_id) != set(ORDER):
        raise ValueError("collected: series.json no longer matches the volume order")
    plan = []
    for index, book_id in enumerate(ORDER):
        book = by_id[book_id]
        if lang not in book["languages"]:
            raise ValueError(f"collected: {book_id} has no {lang} edition")
        project = series.inside(root, book["project"])
        if book["project"] == "agent-books":
            relative = f'yuyu-book/dist/{book["artifact_prefix"]}-{lang}.pdf'
        else:
            relative = "deliverables/llm-course.pdf"
        path = series.inside(project, relative)
        if not path.is_file():
            raise FileNotFoundError(
                f"collected: missing {path}; build that project first")
        plan.append({"id": book_id, "no": volume_label(index),
                     "title": book["title"], "path": path})
    return plan


def _fit(font, text: str, size: float, width: float) -> str:
    if font.text_length(text, fontsize=size) <= width:
        return text
    while text and font.text_length(text + "…", fontsize=size) > width:
        text = text[:-1]
    return text.rstrip() + "…"


def _line(page, font, x, y, text, size=10.5, color=INK, width=None):
    if width is not None:
        text = _fit(font, text, size, width)
    writer = fitz.TextWriter(page.rect)
    writer.append((x, y), text, font=font, fontsize=size)
    writer.write_text(page, color=color)


def _right(page, font, right, y, text, size=10.5, color=INK):
    _line(page, font, right - font.text_length(text, fontsize=size), y, text,
          size=size, color=color)


def _divider(page, font, volume, source, page_span) -> None:
    _line(page, font, MARGIN, 300, volume["no"], size=16, color=MUTED)
    _line(page, font, MARGIN, 348, volume["title"], size=26,
          width=A4[0] - MARGIN * 2)
    _line(page, font, MARGIN, 392,
          f'{source["pages"]} 页 · 原书版式 · 合订本第 {page_span} 页', size=11.5)
    _line(page, font, MARGIN, A4[1] - 96,
          "本卷由该册已发布成品原样合入。", size=9.5, color=MUTED)


def _link_action(link: dict, names: dict) -> tuple[str, int] | None:
    """Decide how a source link behaves inside the collected document.

    ``insert_pdf`` keeps URI links, silently drops internal named links and
    turns launch links into references to files on the build machine.  The
    collected edition rebuilds the first two and removes the third.
    """
    kind = link.get("kind")
    if kind == fitz.LINK_NAMED:
        dest = names.get(link.get("nameddest") or link.get("name"))
        if dest and dest.get("page", -1) >= 0:
            return "goto", dest["page"]
        return "delete", 0
    if kind in (fitz.LINK_GOTOR, fitz.LINK_LAUNCH):
        return "delete", 0
    return None


def build_pdf(root: Path = ROOT, *, lang: str = "zh", date: str | None = None,
              out_dir: Path | None = None) -> dict:
    root = Path(root).resolve()
    date = date or _date.today().isoformat()
    catalog = json.loads((root / "series.json").read_text(encoding="utf-8"))
    plan = collection_plan(root, catalog, lang)

    sources = []
    for volume in plan:
        source = fitz.open(volume["path"])
        sources.append({"pages": source.page_count, "toc": source.get_toc()})
        source.close()

    # The contents row count alone fixes the contents length, so front matter
    # can be laid out once with final page numbers.
    counts = [1 + sum(1 for entry in source["toc"] if entry[0] == 1)
              for source in sources]
    toc_pages = max(1, -(-sum(counts) // TOC_ROWS_PER_PAGE))
    front_pages = 1 + toc_pages

    starts, cursor = [], front_pages
    for source in sources:
        starts.append(cursor)
        cursor += 1 + source["pages"]
    total = cursor

    rows = []
    for index, (volume, source) in enumerate(zip(plan, sources)):
        rows.append((0, f'{volume["no"]}\u3000{volume["title"]}',
                     starts[index] + 1))
        for level, title, page in source["toc"]:
            if level == 1:
                rows.append((1, title, starts[index] + page))

    doc = fitz.open()
    font = fitz.Font("cjk")

    for _ in range(front_pages):
        doc.new_page(width=A4[0], height=A4[1])

    # Content first: links in the contents can only point at existing pages.
    outline = []
    remapped = removed = 0
    for index, (volume, source) in enumerate(zip(plan, sources)):
        start = starts[index] + 1
        divider = doc.new_page(width=A4[0], height=A4[1])
        if divider.number + 1 != start:
            raise RuntimeError("collected: front matter length drifted")
        _divider(divider, font, volume, source,
                 f"{start}–{start + source['pages']}")
        outline.append([1, f'{volume["no"]}\u3000{volume["title"]}', start])
        source_doc = fitz.open(volume["path"])
        for level, title, page in source["toc"]:
            if page > 0:
                outline.append([min(level + 1, 6), title, start + page])
        names = source_doc.resolve_names()
        # insert_pdf drops named internal links and turns launch links into
        # build-machine file references, so repair the source copy first.
        for page in source_doc:
            for link in page.get_links():
                action = _link_action(link, names)
                if action is None:
                    continue
                if action[0] == "goto":
                    dest = names[link.get("nameddest") or link.get("name")]
                    link.update(kind=fitz.LINK_GOTO, page=action[1],
                                to=fitz.Point(dest.get("to") or (0, 0)))
                    page.update_link(link)
                    remapped += 1
                else:
                    page.delete_link(link)
                    removed += 1
        doc.insert_pdf(source_doc, annots=True, links=True)
        source_doc.close()

    cover = doc[0]
    _line(cover, font, MARGIN, 150, "大模型与智能体工程", size=13)
    _line(cover, font, MARGIN, 205, "十卷合订本", size=40)
    _line(cover, font, MARGIN, 250, "从大模型原理到 Agent Harness 工程", size=15)
    y = 300
    for volume in plan:
        _line(cover, font, MARGIN, y, f'{volume["no"]}\u3000{volume["title"]}', size=11)
        y += 20
    _line(cover, font, MARGIN, A4[1] - 96,
          f"各卷保留原有版本、页码与版式；卷首与总目为合订本新增。{date}",
          size=9.5, color=MUTED)

    for index in range(toc_pages):
        page = doc[index + 1]
        _line(page, font, MARGIN, 92, "总目", size=24)
        y = TOC_TOP
        for level, title, page_no in rows[index * TOC_ROWS_PER_PAGE:
                                         (index + 1) * TOC_ROWS_PER_PAGE]:
            indent = MARGIN + (0 if level == 0 else 22)
            size = 11.5 if level == 0 else 10
            _line(page, font, indent, y, title, size=size,
                  width=A4[0] - MARGIN - indent - 60)
            _right(page, font, A4[0] - MARGIN, y, str(page_no),
                   size=11 if level == 0 else 10)
            if level == 0:
                page.insert_link({"kind": fitz.LINK_GOTO,
                                  "from": fitz.Rect(MARGIN, y - 12,
                                                    A4[0] - MARGIN, y + 4),
                                  "page": page_no - 1, "to": fitz.Point(0, 0)})
            y += TOC_ROW_HEIGHT if level == 0 else TOC_ROW_HEIGHT - 2
        _right(page, font, A4[0] - MARGIN, A4[1] - 64, str(index + 2), size=9,
               color=MUTED)

    # Every divider and inserted book must land exactly where the contents say.
    if doc.page_count != total:
        raise RuntimeError(f"collected: page layout drifted ({doc.page_count} != {total})")

    doc.set_toc(outline)
    doc.set_metadata({"title": "大模型与智能体工程 · 十卷合订本",
                      "author": "LinTsinghua", "subject": "合订本（十卷）",
                      "keywords": "大模型, Agent, Harness, 合订本"})
    doc.set_pagemode("UseOutlines")

    out_dir = Path(out_dir) if out_dir else root / "dist"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_pdf = out_dir / f"yuyu-collected-{lang}.pdf"
    doc.save(out_pdf, garbage=4, deflate=True, no_new_id=True)
    doc.close()

    manifest = {
        "schema_version": 1,
        "internal_links_remapped": remapped,
        "file_links_removed": removed,
        "title": "大模型与智能体工程 · 十卷合订本",
        "lang": lang,
        "date": date,
        "output": out_pdf.name,
        "sha256": sha256(out_pdf),
        "total_pages": total,
        "front_pages": front_pages,
        "outline_entries": len(outline),
        "volumes": [
            {"no": volume["no"], "id": volume["id"], "title": volume["title"],
             "source": volume["path"].relative_to(root).as_posix(),
             "source_sha256": sha256(volume["path"]),
             "source_pages": source["pages"],
             "divider_page": starts[index] + 1,
             "content_start": starts[index] + 2}
            for index, (volume, source) in enumerate(zip(plan, sources))],
    }
    (out_dir / f"yuyu-collected-{lang}.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def verify_pdf(path: Path, manifest: dict) -> dict:
    """Read the merged PDF back and check the layout contract."""
    doc = fitz.open(path)
    try:
        if doc.page_count != manifest["total_pages"]:
            raise ValueError("collected: merged page count drifted")
        outline = doc.get_toc()
        if len(outline) != manifest["outline_entries"]:
            raise ValueError("collected: outline drifted")
        volumes = [entry for entry in outline if entry[0] == 1]
        if len(volumes) != len(manifest["volumes"]):
            raise ValueError("collected: expected one outline entry per volume")
        if "十卷合订本" not in doc[0].get_text():
            raise ValueError("collected: cover text missing")
        contents = "".join(doc[number].get_text()
                           for number in range(1, manifest["front_pages"]))
        links = sorted(link["page"] for number in range(1, manifest["front_pages"])
                       for link in doc[number].get_links()
                       if link.get("kind") == fitz.LINK_GOTO)
        expected = [volume["divider_page"] - 1 for volume in manifest["volumes"]]
        if links != expected:
            raise ValueError("collected: contents links drifted")
        for entry, volume in zip(volumes, manifest["volumes"]):
            if entry[2] != volume["divider_page"]:
                raise ValueError("collected: outline page drifted")
            if volume["title"] not in contents:
                raise ValueError("collected: contents missing a volume title")
            if not doc[volume["content_start"] - 1].get_text().strip():
                raise ValueError("collected: empty first page in a volume")
        file_links = goto_links = 0
        for page in doc:
            for link in page.get_links():
                if link["kind"] in (fitz.LINK_GOTOR, fitz.LINK_LAUNCH):
                    file_links += 1
                elif link["kind"] == fitz.LINK_GOTO:
                    goto_links += 1
        if file_links:
            raise ValueError("collected: file links survive in the merged PDF")
        if goto_links < manifest.get("internal_links_remapped", 0):
            raise ValueError("collected: internal link remap lost")
    finally:
        doc.close()
    return {"pages": manifest["total_pages"], "volumes": len(manifest["volumes"]),
            "outline_entries": manifest["outline_entries"],
            "contents_links": len(manifest["volumes"])}


def _parse_epub(path: Path) -> dict:
    with zipfile.ZipFile(path) as archive:
        container = ElementTree.fromstring(archive.read("META-INF/container.xml"))
        rootfile = container.find(".//cn:rootfile", OPF_NS)
        if rootfile is None or not rootfile.get("full-path"):
            raise ValueError(f"collected: {path.name} has no rootfile")
        opf_name = rootfile.get("full-path")
        opf = ElementTree.fromstring(archive.read(opf_name))
        names = set(archive.namelist())
    base = posixpath.dirname(opf_name)
    items = []
    for item in opf.findall("opf:manifest/opf:item", OPF_NS):
        href = item.get("href") or ""
        items.append({"id": item.get("id") or "", "href": href,
                      "type": item.get("media-type") or "application/octet-stream",
                      "properties": (item.get("properties") or "").split(),
                      "full": posixpath.normpath(posixpath.join(base, href))})
    spine = [ref.get("idref") for ref in opf.findall("opf:spine/opf:itemref", OPF_NS)]
    by_id = {item["id"]: item for item in items}
    missing = [idref for idref in spine if idref not in by_id
               or by_id[idref]["full"] not in names]
    if missing:
        raise ValueError(f"collected: {path.name} spine points at missing items {missing[:3]}")
    title = (opf.findtext("opf:metadata/dc:title", default="", namespaces=OPF_NS) or "").strip()
    return {"opf": opf_name, "base": base, "items": items, "spine": spine,
            "title": title, "names": names}


def _xhtml(title: str, body: str, *, lang: str = "zh") -> str:
    return ('<?xml version="1.0" encoding="utf-8"?>\n'
            '<!DOCTYPE html>\n'
            '<html xmlns="http://www.w3.org/1999/xhtml" '
            'xmlns:epub="http://www.idpf.org/2007/ops" '
            f'xml:lang="{lang}" lang="{lang}">\n<head><meta charset="utf-8"/>'
            f'<title>{title}</title>'
            '<style>body{font-family:serif;line-height:1.8;margin:2em}'
            'h1{font-size:1.6em;margin:2em 0 1em}.vol{letter-spacing:.2em;'
            'color:#666}.meta{color:#666;font-size:.9em}</style></head>\n'
            f'<body>{body}</body>\n</html>\n')


def _epub_entry(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=ZIP_DATE)
    info.compress_type = zipfile.ZIP_DEFLATED
    return info


def build_epub(root: Path = ROOT, *, lang: str = "zh", date: str | None = None,
               out_dir: Path | None = None) -> dict:
    root = Path(root).resolve()
    date = date or _date.today().isoformat()
    catalog = json.loads((root / "series.json").read_text(encoding="utf-8"))
    plan = collection_plan(root, catalog, lang)

    for volume in plan:
        epub = series.inside(volume["path"].parent, volume["path"].stem + ".epub")
        if not epub.is_file():
            raise FileNotFoundError(f"collected: missing {epub}; build that project first")
        volume["epub"] = epub
        volume["parsed"] = _parse_epub(epub)

    out_dir = Path(out_dir) if out_dir else root / "dist"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_epub = out_dir / f"yuyu-collected-{lang}.epub"

    title = "大模型与智能体工程 · 十卷合订本"
    manifest_items, ids = [], set()
    volume_spines = []
    for index, volume in enumerate(plan):
        parsed = volume["parsed"]
        prefix = f'v{index + 1:02d}'
        by_id = {}
        for item in parsed["items"]:
            merged_id = f'{prefix}-{item["id"]}'
            if merged_id in ids:
                raise ValueError(f"collected: duplicate manifest id {merged_id}")
            ids.add(merged_id)
            by_id[item["id"]] = merged_id
            properties = [value for value in item["properties"]
                          if value not in ("nav", "cover-image")]
            manifest_items.append({"id": merged_id,
                                   "href": f'{prefix}/{item["full"]}',
                                   "type": item["type"], "properties": properties})
        volume_spines.append([by_id[idref] for idref in parsed["spine"]])
        volume["prefix"] = prefix

    # Deterministic package identity: the same sources and date give the same id.
    identity = hashlib.sha256()
    for volume in plan:
        identity.update(sha256(volume["epub"]).encode())
    identity.update(date.encode())

    # Only spine items may appear in the collected nav: linking a volume's own
    # nav document here trips EPUBCheck RSC-011, because those files stay out
    # of the merged spine.
    nav_items = "".join(
        f'<li><a href="vol{i + 1:02d}.xhtml">'
        f'{xml_escape(volume["no"] + "　" + volume["title"])}</a></li>'
        for i, volume in enumerate(plan))
    cover_body = ('<h1>大模型与智能体工程</h1><p class="vol">十卷合订本</p>'
                  + "".join(f'<p>{xml_escape(volume["no"] + "　" + volume["title"])}</p>'
                            for volume in plan)
                  + f'<p class="meta">各卷保留原有版本与版式；卷首与本目录为合订本新增。{date}</p>')

    files = {
        "META-INF/container.xml": (
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
            '<rootfiles><rootfile full-path="EPUB/package.opf" '
            'media-type="application/oebps-package+xml"/></rootfiles></container>\n'),
        "EPUB/package.opf": None,
        "EPUB/cover.xhtml": _xhtml("封面", cover_body, lang=lang),
        "EPUB/nav.xhtml": _xhtml("总目", f'<h1>总目</h1><nav epub:type="toc"><ol>{nav_items}</ol></nav>', lang=lang),
    }
    for index, volume in enumerate(plan):
        files[f"EPUB/vol{index + 1:02d}.xhtml"] = _xhtml(
            f'{volume["no"]}', f'<p class="vol">{volume["no"]}</p>'
            f'<h1>{xml_escape(volume["title"])}</h1>'
            '<p class="meta">本卷由该册已发布 EPUB 原样合入。</p>',
            lang=lang)
        with zipfile.ZipFile(volume["epub"]) as archive:
            for name in archive.namelist():
                if name == "mimetype" or name.startswith("META-INF/"):
                    continue
                files[f'EPUB/{volume["prefix"]}/{name}'] = archive.read(name)

    manifest_xml = "".join(
        '<item id="%s" href="%s" media-type="%s"%s/>' % (
            item["id"], item["href"], item["type"],
            f' properties="{" ".join(item["properties"])}"' if item["properties"] else "")
        for item in manifest_items)
    front = [("cover", "cover.xhtml", "application/xhtml+xml"),
             ("nav", "nav.xhtml", "application/xhtml+xml", ' properties="nav"')]
    for index in range(len(plan)):
        front.append((f'divider{index + 1:02d}', f'vol{index + 1:02d}.xhtml',
                      "application/xhtml+xml"))
    front_xml = "".join(
        '<item id="%s" href="%s" media-type="%s"%s/>' % ((row + ("",))[:4])
        for row in front)
    spine_order = ["cover", "nav"]
    for index, book_spine in enumerate(volume_spines):
        spine_order.append(f"divider{index + 1:02d}")
        spine_order.extend(book_spine)
    spine_xml = "".join('<itemref idref="%s"/>' % idref for idref in spine_order)
    files["EPUB/package.opf"] = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" '
        'unique-identifier="pub-id" xml:lang="%s">\n'
        '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">'
        '<dc:identifier id="pub-id">urn:sha256:%s</dc:identifier>'
        '<dc:title>%s</dc:title><dc:language>%s</dc:language>'
        '<meta property="dcterms:modified">%sT00:00:00Z</meta></metadata>\n'
        '<manifest>%s%s</manifest>\n<spine>%s</spine>\n</package>\n'
        % (lang, identity.hexdigest(), xml_escape(title), lang, date, front_xml, manifest_xml,
           spine_xml))

    with zipfile.ZipFile(out_epub, "w") as archive:
        info = zipfile.ZipInfo("mimetype", date_time=ZIP_DATE)
        info.compress_type = zipfile.ZIP_STORED
        archive.writestr(info, "application/epub+zip")
        for name, data in files.items():
            if name == "EPUB/package.opf":
                data = data.encode("utf-8")
            elif isinstance(data, str):
                data = data.encode("utf-8")
            archive.writestr(_epub_entry(name), data)

    return {"output": out_epub.name, "sha256": sha256(out_epub),
            "volumes": len(plan), "items": len(manifest_items) + len(front),
            "spine_items": len(spine_order)}


def verify_epub(path: Path) -> dict:
    """Read the merged EPUB back and check the package contract."""
    with zipfile.ZipFile(path) as archive:
        if archive.namelist()[0] != "mimetype":
            raise ValueError("collected: mimetype must be the first entry")
        if archive.getinfo("mimetype").compress_type != zipfile.ZIP_STORED:
            raise ValueError("collected: mimetype must be stored")
        container = ElementTree.fromstring(archive.read("META-INF/container.xml"))
        opf_name = container.find(".//cn:rootfile", OPF_NS).get("full-path")
        opf = ElementTree.fromstring(archive.read(opf_name))
        names = set(archive.namelist())
        items = {item.get("id"): item.get("href")
                 for item in opf.findall("opf:manifest/opf:item", OPF_NS)}
        spine = [ref.get("idref") for ref in opf.findall("opf:spine/opf:itemref", OPF_NS)]
        missing = [idref for idref in spine if idref not in items]
        if missing:
            raise ValueError(f"collected: spine ids missing from manifest: {missing[:3]}")
        absent = [href for href in items.values()
                  if posixpath.join("EPUB", href) not in names]
        if absent:
            raise ValueError(f"collected: manifest files absent: {absent[:3]}")
        navs = [item for item in opf.findall("opf:manifest/opf:item", OPF_NS)
                if "nav" in (item.get("properties") or "")]
        if len(navs) != 1:
            raise ValueError("collected: expected exactly one nav document")
        nav = archive.read(posixpath.join("EPUB", navs[0].get("href"))).decode("utf-8")
        volumes = re.findall(r"vol\d\d\.xhtml", nav)
        by_href = {href: id_ for id_, href in items.items()}
        base = posixpath.dirname(navs[0].get("href"))
        stray = []
        for href in re.findall(r'<a href="([^"]+)"', nav):
            target = posixpath.normpath(posixpath.join(base, href))
            idref = by_href.get(target)
            if idref is None:
                stray.append(f"{href} (not in manifest)")
            elif idref not in spine:
                stray.append(f"{href} (not in spine)")
        if stray:
            raise ValueError(f"collected: nav links outside the spine: {stray[:3]}")
    return {"spine_items": len(spine), "items": len(items),
            "volumes": len(set(volumes))}


def main(argv=None, *, root=ROOT):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--lang", default="zh")
    parser.add_argument("--date", default=None)
    parser.add_argument("--out-dir", default=None)
    args = parser.parse_args(argv)
    out_dir = Path(args.out_dir) if args.out_dir else None
    manifest = build_pdf(root, lang=args.lang, date=args.date, out_dir=out_dir)
    verified = verify_pdf((out_dir or root / "dist") / manifest["output"], manifest)
    manifest["verified"] = verified
    epub = build_epub(root, lang=args.lang, date=args.date, out_dir=out_dir)
    checked = verify_epub((out_dir or root / "dist") / epub["output"])
    manifest["epub"] = dict(epub, verified_spine=checked["spine_items"],
                            verified_volumes=checked["volumes"])
    (Path(out_dir) if out_dir else root / "dist").joinpath(
        f"yuyu-collected-{args.lang}.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f'collected: {manifest["output"]} {manifest["total_pages"]} pages, '
          f'{len(manifest["volumes"])} volumes, '
          f'{manifest["outline_entries"]} outline entries; '
          f'{epub["output"]} {epub["spine_items"]} spine items')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
