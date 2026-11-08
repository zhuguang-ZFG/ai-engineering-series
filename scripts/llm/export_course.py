"""Export the authored C01–C30 reading edition and separated answer editions.

Uses the same generated chapter HTML as the website. Legacy L books remain intact.
"""

import hashlib
import json
import os
import shutil
import zipfile
from copy import deepcopy
from pathlib import Path
from urllib.parse import urlsplit

import fitz
from lxml import etree, html
from playwright.sync_api import sync_playwright

from export_books import ROOT, OUT, source_hash, xhtml_document, element, append, keep_equations_with_explanation

WORK = ROOT / "tmp" / "llm-course-review"
XHTML = "http://www.w3.org/1999/xhtml"
EPUB = "http://www.idpf.org/2007/ops"
OPF = "http://www.idpf.org/2007/opf"
DC = "http://purl.org/dc/elements/1.1/"


def content_document(chapter, answers=False):
    suffix = "-answer" if answers else ""
    page = html.fromstring((ROOT / "exports/llm" / (chapter["id"].lower() + suffix + ".html")).read_bytes())
    article = page.xpath('//article')[0]
    article = deepcopy(article)
    article.set("id", chapter["id"] + suffix)
    for node in article.xpath('.//nav | .//script'):
        node.drop_tree()
    for node in article.xpath('.//details'):
        node.tag = "section"
        for summary in node.xpath('./summary'):
            summary.tag = "h3"
    for node in article.iter():
        for key in list(node.attrib):
            if key == "tabindex" or key.startswith(("data-", "aria-")):
                del node.attrib[key]
    for image in article.xpath('.//img[@src]'):
        original = (ROOT / "exports/llm" / image.get("src")).resolve()
        if not original.is_relative_to(ROOT) or not original.is_file():
            raise ValueError("Chapter image not in repository")
        image.set("src", "images/" + original.name)
    for anchor in article.xpath('.//a[@href]'):
        target = anchor.get("href")
        parsed = urlsplit(target)
        if parsed.scheme or target.startswith("#"):
            continue
        name = Path(parsed.path).name
        expected = {entry["id"].lower() + suffix + ".html" for entry in content_document.chapters}
        if name in expected:
            anchor.set("href", name[:-5] + ".xhtml" + ("#" + parsed.fragment if parsed.fragment else ""))
        elif name == "course.html":
            anchor.set("href", "nav.xhtml#toc")
        else:
            # Keep offline instructions as visible paths, not broken EPUB links.
            label = "".join(anchor.itertext())
            anchor.text = label + "（仓库：" + target + "）"
            for child in list(anchor):
                anchor.remove(child)
            anchor.drop_tag()
    keep_equations_with_explanation(article)
    return article


def package_epub(stem, title, docs, image_names, css):
    package = etree.Element("{%s}package" % OPF, nsmap={None: OPF, "dc": DC}, version="3.0", **{"unique-identifier": "book-id"})
    metadata = etree.SubElement(package, "{%s}metadata" % OPF)
    for name, value in [("identifier", "urn:llm-course:" + stem + ":1.0.0"), ("title", title), ("language", "zh-CN"), ("creator", "Vibe Coding 101 课程项目"), ("rights", "原课程图与新编教学内容；第三方来源和许可见正文，未转授权外部书图。")]:
        node = etree.SubElement(metadata, "{%s}%s" % (DC, name))
        node.text = value
        if name == "identifier":
            node.set("id", "book-id")
    etree.SubElement(metadata, "{%s}meta" % OPF, property="dcterms:modified").text = "2026-11-08T00:00:00Z"
    manifest = etree.SubElement(package, "{%s}manifest" % OPF)
    for index, (name, _) in enumerate(docs.items()):
        attrs = {"id": "doc-" + str(index), "href": name, "media-type": "application/xhtml+xml"}
        if name == "nav.xhtml":
            attrs["properties"] = "nav"
        etree.SubElement(manifest, "{%s}item" % OPF, **attrs)
    etree.SubElement(manifest, "{%s}item" % OPF, id="css", href="book.css", **{"media-type": "text/css"})
    for index, name in enumerate(image_names):
        etree.SubElement(manifest, "{%s}item" % OPF, id="image-" + str(index), href="images/" + name, **{"media-type": "image/png"})
    spine = etree.SubElement(package, "{%s}spine" % OPF)
    for index in range(len(docs)):
        etree.SubElement(spine, "{%s}itemref" % OPF, idref="doc-" + str(index))
    container = b'<?xml version="1.0" encoding="utf-8"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>'
    with zipfile.ZipFile(OUT / (stem + ".epub"), "w") as archive:
        def put(name, data, compressed=True):
            info = zipfile.ZipInfo(name, (2026, 11, 8, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED if compressed else zipfile.ZIP_STORED
            info.external_attr = 0o644 << 16
            archive.writestr(info, data)
        put("mimetype", b"application/epub+zip", False)
        put("META-INF/container.xml", container)
        put("OEBPS/content.opf", etree.tostring(package, xml_declaration=True, encoding="utf-8"))
        put("OEBPS/book.css", css)
        for name, (document_title, body) in docs.items():
            put("OEBPS/" + name, xhtml_document(document_title, body))
        for name in image_names:
            put("OEBPS/images/" + name, (WORK / "images" / name).read_bytes())


def run():
    curriculum = json.loads((ROOT / "book/llm/course.json").read_text(encoding="utf-8"))["curriculum"]
    chapters = curriculum["chapters"]
    content_document.chapters = chapters
    fingerprint = source_hash()
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / "images").mkdir(exist_ok=True)
    css = (ROOT / "scripts/llm/book.css").read_bytes() + b"\npre, tr { break-inside: auto; } code { overflow-wrap: anywhere; } img { display: block; max-width: 100%; width: auto; height: auto; margin: 1em auto; } @media print { img { max-height: 145mm; max-width: 100%; object-fit: contain; } .curriculum-figure { margin: 1em auto; break-inside: avoid; } .curriculum-figure img { max-height: 128mm; margin: 0 auto; } }\n"
    (WORK / "book.css").write_bytes(css)
    node = shutil.which("node")
    if node:
        os.environ.setdefault("PLAYWRIGHT_NODEJS_PATH", node)
    if os.name == "nt":
        os.environ["NODE_OPTIONS"] = os.environ.get("NODE_OPTIONS", "") + " --preserve-symlinks --preserve-symlinks-main"
    results = {}
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(viewport={"width": 1000, "height": 1400}, device_scale_factor=2)
        context.set_offline(True)
        page = context.new_page()
        for answers in (False, True):
            stem = "llm-course-answers" if answers else "llm-course"
            title = "五阶段三十章 · 核对依据" if answers else "把大模型拆开看 · 从入门到独立交付"
            intro = element("body", **{"class": "reading-part"})
            append(intro, "h1", title)
            append(intro, "p", "实施试读版 1.0.0；真人学习效果、独立复做与资源条件以验收记录为准，不因出版成品而通过。")
            append(intro, "p", "先独立作答，再打开单独的核对依据。正文中的程序在本地环境运行，纸书和 EPUB 不执行模型或代码。旧 L01–L12 实验与网页回查保留。")
            nav_body = element("body", **{"class": "reading-part"})
            append(nav_body, "h1", "核对依据目录" if answers else "五阶段目录")
            navigation = append(nav_body, "nav", id="toc")
            navigation.set("{%s}type" % EPUB, "toc")
            listing = append(navigation, "ol")
            documents = {"intro.xhtml": (title, intro), "nav.xhtml": ("目录", nav_body)}
            image_names = set()
            for chapter in chapters:
                suffix = "-answer" if answers else ""
                filename = chapter["id"].lower() + suffix + ".xhtml"
                article = content_document(chapter, answers)
                chapter_title = "".join(article.xpath('.//h1')[0].itertext())
                item = append(listing, "li")
                append(item, "a", chapter_title, href=filename + "#" + chapter["id"] + suffix)
                sections = article.xpath('.//h2[@id] | .//h3[@id]')
                nested = append(item, "ol") if sections else None
                for section in sections:
                    child = append(nested, "li")
                    append(child, "a", "".join(section.itertext()), href=filename + "#" + section.get("id"))
                for image in article.xpath('.//img[@src]'):
                    svg_name = Path(image.get("src")).name
                    png_name = Path(svg_name).stem + ".png" if svg_name.endswith(".svg") else svg_name
                    if png_name not in image_names:
                        original = ROOT / "book/assets/handdraw/llm" / svg_name
                        if svg_name.endswith(".svg"):
                            svg = original.read_text(encoding="utf-8")
                            page.set_content('<!doctype html><html><head><meta charset="utf-8"></head><body style="margin:0;display:inline-block">' + svg + "</body></html>")
                            page.evaluate("document.fonts.ready")
                            page.locator("svg").screenshot(path=str(WORK / "images" / png_name))
                        else:
                            shutil.copyfile(original, WORK / "images" / png_name)
                    image_names.add(png_name)
                    image.set("src", "images/" + png_name)
                documents[filename] = (chapter_title, article)
            print_body = element("body")
            for _, body in documents.values():
                section = deepcopy(body)
                section.tag = "section"
                section.set("class", "chapter")
                for anchor in section.xpath('.//a[@href]'):
                    target = anchor.get("href")
                    if ".xhtml#" in target:
                        anchor.set("href", "#" + target.split("#", 1)[1])
                    elif target.endswith(".xhtml"):
                        stem_target = target[:-6]
                        destination = stem_target[:3].upper() + stem_target[3:]
                        anchor.set("href", "#" + destination)
                print_body.append(section)
            reading = WORK / (stem + ".html")
            reading.write_bytes(xhtml_document(title, print_body))
            page.goto(reading.as_uri())
            page.evaluate("document.fonts.ready")
            if not page.evaluate("[...document.images].every(image => image.complete && image.naturalWidth > 0)"):
                raise RuntimeError("Book image failed to load")
            page.pdf(path=str(OUT / (stem + ".pdf")), prefer_css_page_size=True, print_background=True, tagged=True, outline=True)
            package_epub(stem, title, documents, sorted(image_names), css)
            with fitz.open(OUT / (stem + ".pdf")) as pdf:
                results[stem] = {"pdfPages": len(pdf), "outlineEntries": len(pdf.get_toc()), "chapters": len(chapters), "images": len(image_names)}
                pdf[0].get_pixmap(matrix=fitz.Matrix(1.2, 1.2)).save(WORK / (stem + "-first.png"))
        browser.close()
    if source_hash() != fingerprint:
        raise RuntimeError("Course source changed during book export")
    filenames = [stem + suffix for stem in results for suffix in (".pdf", ".epub")]
    metadata = {"version": curriculum["version"], "sourceHash": fingerprint, "editions": results, "files": {name: {"bytes": (OUT/name).stat().st_size, "sha256": hashlib.sha256((OUT/name).read_bytes()).hexdigest()} for name in filenames}, "limitations": ["真实初学者验收未完成", "运行证据与独立复做分开", "EPUB和PDF不执行代码"]}
    (OUT / "llm-course.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metadata, ensure_ascii=False))


if __name__ == "__main__":
    run()
