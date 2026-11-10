"""Export the authored C01–C30 reading edition and separated answer editions.

Uses the same generated chapter HTML as the website. The 30-chapter book has its
own A5 sheet (book-course.css), cover, five stage openings, a printed contents
with pages resolved from the actual PDF, and a separate deep-reading appendix.
"""

import hashlib
import json
import os
import re
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
ASSETS = ROOT / "book/assets/handdraw/llm"
SHEET = ROOT / "scripts/llm/book-course.css"

HEADER_TEMPLATE = (
    '<div style="width:100%;padding:0 15mm;font-family:\'Noto Serif SC\',serif;'
    'font-size:7.5px;color:#6b6457;letter-spacing:.08em;display:flex;justify-content:space-between;">'
    "<span>大模型：从入门到精通</span><span>五阶段 · 三十章</span></div>"
)
FOOTER_TEMPLATE = (
    '<div style="width:100%;padding:0 15mm;font-family:\'Noto Serif SC\',serif;'
    'font-size:8px;color:#6b6457;text-align:center;letter-spacing:.06em;">'
    '<span class="pageNumber"></span></div>'
)


def json_file(path):
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_image(page, original, image_names, folder):
    """Render one SVG to PNG at 2x, or copy an existing raster asset."""
    png_name = original.stem + ".png"
    target = folder / png_name
    if not target.exists():
        if original.suffix.lower() == ".svg":
            svg = original.read_text(encoding="utf-8")
            page.set_content(
                '<!doctype html><html><head><meta charset="utf-8">'
                '<style>html,body{margin:0;background:#fbfaf1}svg{display:block}</style>'
                "</head><body>" + svg + "</body></html>"
            )
            page.evaluate("document.fonts.ready")
            page.locator("svg").screenshot(path=str(target))
        else:
            shutil.copyfile(original, target)
    image_names.add(png_name)
    return png_name


def clean_links(article, chapter, suffix):
    """Keep in-book links, turn repository paths into visible text."""
    expected = {entry["id"].lower() + suffix + ".html" for entry in content_document.chapters}
    main_chapters = {entry["id"].lower() + ".html": entry["id"] for entry in content_document.chapters}
    for anchor in article.xpath(".//a[@href]"):
        target = anchor.get("href")
        parsed = urlsplit(target)
        if parsed.scheme or target.startswith("#"):
            continue
        name = Path(parsed.path).name
        if name in expected:
            anchor.set("href", name[:-5] + ".xhtml" + ("#" + parsed.fragment if parsed.fragment else ""))
        elif name in main_chapters and not suffix:
            anchor.set("href", name[:-5] + ".xhtml#" + main_chapters[name])
        elif name in main_chapters:
            anchor.drop_tag()
        elif re.fullmatch(r"stage-s[1-5]\.html", name):
            anchor.set("href", name[:-5] + ".xhtml#S" + name[7])
        elif name == "course.html":
            anchor.set("href", "nav.xhtml#toc")
        elif name == "deep-reading.html":
            anchor.set("href", "deep-reading.xhtml#deep-reading")
        elif name == "index.html":
            anchor.set("href", "nav.xhtml#toc")
        else:
            label = "".join(anchor.itertext())
            if Path(parsed.path).suffix.lower() in {".md", ".json", ".py", ".mjs", ".txt"}:
                anchor.text = label + "（仓库：" + target + "）"
                for child in list(anchor):
                    anchor.remove(child)
            anchor.drop_tag()


def number_figures(article, chapter, answers):
    prefix = chapter["id"] + ("-A" if answers else "")
    figures = article.xpath('.//figure[contains(concat(" ",normalize-space(@class)," ")," curriculum-figure ")]')
    for index, figure in enumerate(figures, 1):
        caption = figure.find("figcaption")
        if caption is None:
            continue
        first = caption.text or ""
        first = re.sub(r"^\s*图[：:]\s*", "", first)
        caption.text = None
        label = etree.Element("b")
        label.text = "图 %s-%d" % (prefix, index)
        label.tail = "　" + first
        caption.insert(0, label)


def content_document(chapter, answers=False, page=None, image_names=None):
    suffix = "-answer" if answers else ""
    source = ROOT / "exports/llm" / (chapter["id"].lower() + suffix + ".html")
    parsed = html.fromstring(source.read_bytes())
    article = parsed.xpath("//article")[0]
    article = deepcopy(article)
    article.set("id", chapter["id"] + suffix)
    article.set("class", "chapter answer-edition" if answers else "chapter")
    for node in article.xpath(".//nav | .//script"):
        node.drop_tree()
    for node in article.xpath(".//details"):
        node.tag = "section"
        for summary in node.xpath("./summary"):
            summary.tag = "h3"
    for node in article.iter():
        for key in list(node.attrib):
            if key == "tabindex" or key.startswith(("data-", "aria-")):
                del node.attrib[key]
    for image in article.xpath('.//img[@src]'):
        original = (ROOT / "exports/llm" / image.get("src")).resolve()
        if not original.is_relative_to(ROOT) or not original.is_file():
            raise ValueError("Chapter image not in repository")
        png_name = ensure_image(page, original, image_names, WORK / "images")
        image.set("src", "images/" + png_name)
    clean_links(article, chapter, suffix)
    keep_equations_with_explanation(article)
    number_figures(article, chapter, answers)
    return article


def stage_plate_document(stage, note, image_names):
    body = element("body", **{"class": "stage-plate"})
    figure = append(body, "figure", **{"class": "stage-plate-figure"})
    append(figure, "img", src="images/stage-%s.png" % stage["id"][1:], alt="%s %s 阶段插画" % (stage["id"], stage["title"]))
    append(figure, "figcaption", "%s / %s · %s" % (stage["id"], stage["gate"], note["thesis"]))
    return body


def map_document(note):
    body = element("body", **{"class": "book-map", "id": "map"})
    append(body, "h1", note["title"])
    append(body, "p", "五阶段 · 三十章 · 五道能力门；横线是阶段，圆点是章号，右侧菱形是能力门。", **{"class": "map-sub"})
    figure = append(body, "figure", **{"class": "book-map-figure"})
    append(figure, "img", src="images/book-map.png", alt="全书地图：五条阶段线、30 个章号与 5 道能力门")
    append(figure, "figcaption", "五条阶段线、30 个章号与 5 道能力门。")
    return body


def stage_intro_document(stage, note, chapters):
    body = element("body", **{"class": "stage-intro", "id": stage["id"]})
    append(body, "p", "阶段 %s / %s" % (stage["id"][1:], stage["gate"]), **{"class": "stage-label"})
    append(body, "h1", "%s %s" % (stage["id"], stage["title"]))
    append(body, "p", note["thesis"], **{"class": "stage-thesis"})
    append(body, "p", "阶段门 %s · 本阶段 %d 章" % (stage["gate"], len(chapters)), **{"class": "stage-gate"})
    for paragraph in note["intro"]:
        append(body, "p", paragraph)
    block = append(body, "section", **{"class": "stage-chapters"})
    append(block, "h2", "本阶段章节")
    listing = append(block, "ol")
    for chapter in chapters:
        item = append(listing, "li")
        label = append(item, "p")
        append(label, "span", chapter["id"], **{"class": "chapter-id"})
        append(label, "span", chapter["title"])
        append(item, "p", chapter["abstract"], **{"class": "caption"})
    return body


def title_page_document(curriculum, answers):
    body = element("body", **{"class": "title-page"})
    if answers:
        append(body, "p", "分离答案 · 先作答，再核对", **{"class": "title-kicker"})
        append(body, "h1", curriculum["title"] + " · 核对依据")
        append(body, "p", "每章作业的核对过程、可接受范围与常见错误。", **{"class": "title-sub"})
        append(body, "p", "实施试读版 %s · 2026.11" % curriculum["version"], **{"class": "title-edition"})
    else:
        append(body, "p", "五阶段 · 三十章", **{"class": "title-kicker"})
        append(body, "h1", curriculum["title"])
        append(body, "p", "从一份通知，到一次能复现的交付。", **{"class": "title-sub"})
        append(body, "div", "", **{"class": "title-rule"})
        append(body, "p", "实施试读版 %s · 2026.11" % curriculum["version"], **{"class": "title-edition"})
    return body


def howto_document(answers):
    body = element("body", **{"class": "reading-guide"})
    if answers:
        append(body, "h1", "怎么用这份核对依据")
        append(body, "p", "先合上这份文件，按题目独立作答；写完后再逐项核对。答案给的是可接受的判断过程和范围，不是唯一措辞。")
        for text in [
            "每章答案先列核对表，再解释容易混淆的地方。",
            "凡标“材料未提供”“冲突待确认”的格，不要用常识补全；补全了就失去可核对性。",
            "数值题保留中间步骤与容差；只对最终数字不算完成。",
            "答案不替你完成项目文件、真实模型调用或独立复做；这些仍要在自己的环境里留下证据。",
        ]:
            append(body, "p", text)
        append(body, "h2", "版本与边界")
        append(body, "p", "这是实施试读版。答案由课程作者编写，未经过真实初学者全程试做；它不能替代你的运行记录、评测数据或独立复做。")
        return body
    append(body, "h1", "怎么读这本书")
    append(body, "p", "这本书按五个阶段组织：会使用、懂原理、能实现、会改进、独立交付。每个阶段先有一张阶段插画和一页导言，再进入该阶段的章节。阶段导言说明这一阶段要练什么、哪里容易误判；章节正文只解决一个具体问题。")
    append(body, "h2", "一条线，五种读法")
    for text in [
        "第一次读：按 C01 到 C30 的顺序走。每章先读开场情境，再跟算例或程序走一遍，最后做章末独立作业。",
        "想先看全貌：先读五个阶段导言和书末《深读：五个不能再简化的问题》，再回到具体章节。",
        "工作中遇到问题：从目录定位章节；每章末尾的“来源与边界”说明这一章能支持什么、不能支持什么。",
        "做项目：把每章“项目增量”留下的文件接起来；不要跳过失败记录，它们和成功结果一样是交付物。",
        "复习：只看每章开头的摘要、图中的数字和章末的失败对照；能复述这三点，再回到正文补细节。",
    ]:
        append(body, "p", text)
    append(body, "h2", "图、公式与编号")
    append(body, "p", "正文插图按章编号，例如“图 C01-1”。图只承担它自己说明的关系；图注会写出边界，读到数字时先看它是不是人工示例。公式用等宽字体排印，前后文保留同一组符号；不要把图中的示意值当成模型内部读数。")
    append(body, "h2", "纸书、电子书与代码")
    append(body, "p", "PDF 有封面、阶段页、章首页和实际页码目录；EPUB 使用流式排版，可以调整字号，目录能展开到章。两种版本都不执行模型、程序或网页按钮；需要运行的命令请在本地环境按正文步骤执行。")
    append(body, "h2", "版本与边界")
    append(body, "p", "这是实施试读版。课文、图解和检查脚本已经同源生成，但真实初学者全程试读、独立复做与读屏验收尚未完成；读完三十章不等于通过五道能力门。每章末尾的来源与边界，以及书末的深读文章，都保留失败与未完成项。")
    return body


def toc_document(curriculum, entries, answers):
    body = element("body", **{"class": "toc"})
    append(body, "h1", "核对依据目录" if answers else "目录")
    nav = append(body, "nav", id="toc")
    nav.set("{%s}type" % EPUB, "toc")
    listing = append(nav, "ol")
    for entry in entries:
        if entry["kind"] == "stage":
            item = append(listing, "li", **{"class": "toc-stage"})
            link = append(item, "a", href=entry["href"])
            append(link, "span", entry["label"])
            append(item, "span", "", **{"class": "toc-dots"})
            entry["page"] = append(item, "span", "000", **{"class": "toc-page", "data-toc-id": entry["id"]})
        else:
            item = append(listing, "li", **{"class": "toc-line" + (" toc-appendix" if entry["kind"] in {"deep", "glossary"} else "") + (" toc-map" if entry["kind"] == "map" else "")})
            link = append(item, "a", **{"class": "toc-label", "href": entry["href"]})
            if entry["kind"] == "chapter" and not answers:
                append(link, "span", entry["id"], **{"class": "toc-id"})
            append(link, "span", entry["label"])
            append(item, "span", "", **{"class": "toc-dots"})
            entry["page"] = append(item, "span", "000", **{"class": "toc-page", "data-toc-id": entry["id"]})
    return body


def appendix_document(web_name, element_id, class_name, page, image_names):
    parsed = html.fromstring((ROOT / "exports/llm" / web_name).read_bytes())
    article = parsed.xpath("//article")[0]
    article = deepcopy(article)
    article.set("id", element_id)
    article.set("class", class_name)
    for node in article.xpath(".//nav | .//script"):
        node.drop_tree()
    for node in article.iter():
        for key in list(node.attrib):
            if key == "tabindex" or key.startswith(("data-", "aria-")):
                del node.attrib[key]
    for image in article.xpath('.//img[@src]'):
        original = (ROOT / "exports/llm" / image.get("src")).resolve()
        png_name = ensure_image(page, original, image_names, WORK / "images")
        image.set("src", "images/" + png_name)
    clean_links(article, {"id": element_id}, "")
    keep_equations_with_explanation(article)
    return article


def deep_reading_document(curriculum, page, image_names):
    return appendix_document("deep-reading.html", "deep-reading", "deep-reading", page, image_names)


def glossary_document(curriculum, page, image_names):
    return appendix_document("glossary.html", "glossary", "glossary", page, image_names)


def colophon_document(curriculum, answers):
    body = element("body", **{"class": "colophon"})
    append(body, "p", "大模型：从入门到精通", **{"class": "colophon-mark"})
    append(body, "p", ("核对依据 · " if answers else "") + "实施试读版 %s · 2026.11" % curriculum["version"])
    append(body, "p", "课文、阶段导言与图解由 Markdown 与可编辑 SVG 同源生成；第三方来源、许可与边界见正文“来源与边界”及 book/llm/sources.json。")
    append(body, "p", "PDF 的目录页码由实际排版回填；EPUB 使用流式排版，目录可展开到章。书中的程序、模型调用与网页按钮不会在纸书或 EPUB 中执行。")
    append(body, "p", "真实初学者全程试读、独立复做与读屏验收尚未完成；本书不构成能力认证，也不把作者烟测当作读者学习结果。")
    return body


def print_body_from_docs(docs):
    body = element("body")
    for _, document in docs.values():
        section = deepcopy(document)
        section.tag = "section"
        section.set("class", (section.get("class", "") + " print-section").strip())
        body.append(section)
    return body


def find_outline_page(outline, heading):
    wanted = "".join(str(heading).split())
    matches = [number for level, text, number in outline if level == 1 and "".join(str(text).split()) == wanted]
    if not matches:
        matches = [number for level, text, number in outline if "".join(str(text).split()) == wanted]
    assert len(matches) == 1, ("Ambiguous or missing PDF heading", heading, matches)
    return matches[0]


def has_repeated_first_line(document, destination, expected, actual):
    """Require the repeated prefix to be the rendered heading's first line."""
    if destination.get("kind") != fitz.LINK_GOTO or destination.get("to") is None:
        return False
    page_number = destination.get("page", -1)
    if not 0 <= page_number < len(document):
        return False
    matches = 0
    for block in document[page_number].get_text("dict")["blocks"]:
        lines = [
            "".join("".join(span["text"] for span in line["spans"]).split())
            for line in block.get("lines", [])
        ]
        if (
            len(lines) > 1
            and "".join(lines) == expected
            and actual == lines[0] + expected
            and fitz.Rect(block["bbox"]).contains(destination["to"])
        ):
            matches += 1
    return matches == 1


def repair_outline_titles(document, body):
    """Repair Chrome's repeated PDF heading text against the authored headings.

    Linux Chrome 157 can repeat a title or its first rendered line in an outline.
    Match the complete ordered heading tree before changing titles. For wrapped
    headings, also verify the actual lines at the PDF destination. Legitimate
    repeated wording and every original destination remain intact.
    """
    headings = [
        (int(node.tag.rsplit("}", 1)[-1][1]), "".join(node.itertext()).strip())
        for node in body.iter()
        if isinstance(node.tag, str) and node.tag.rsplit("}", 1)[-1] in {"h1", "h2", "h3", "h4", "h5", "h6"}
    ]
    outline = document.get_toc(simple=False)
    assert len(outline) == len(headings), ("PDF heading count differs from source", len(outline), len(headings))
    repairs = []
    for index, ((level, title, _, destination), (expected_level, expected_title)) in enumerate(zip(outline, headings)):
        assert level == expected_level, ("PDF heading level differs from source", index, level, expected_level)
        actual = "".join(title.split())
        expected = "".join(expected_title.split())
        assert expected, ("Empty source heading", index)
        if actual == expected:
            continue
        repeats, remainder = divmod(len(actual), len(expected))
        repeated_title = repeats >= 2 and not remainder and actual == expected * repeats
        assert repeated_title or has_repeated_first_line(document, destination, expected, actual), (
            "PDF heading differs from source", index, title, expected_title,
        )
        repairs.append((index, expected_title))
    for index, title in repairs:
        # Updating only /Title preserves coordinates, page numbers and nesting.
        document.set_toc_item(index, title=title)
    return len(repairs)


def print_with_pages(page, title, body, path, target, entries):
    previous = None
    for attempt in range(1, 5):
        path.write_bytes(xhtml_document(title, body))
        page.goto(path.as_uri())
        page.evaluate("document.fonts.ready")
        if not page.evaluate("[...document.images].every(image => image.complete && image.naturalWidth > 0)"):
            raise RuntimeError("Book image failed to load")
        page.pdf(
            path=str(target),
            prefer_css_page_size=True,
            print_background=True,
            tagged=True,
            outline=True,
            display_header_footer=True,
            header_template=HEADER_TEMPLATE,
            footer_template=FOOTER_TEMPLATE,
        )
        with fitz.open(target) as document:
            if repair_outline_titles(document, body):
                document.saveIncr()
            outline = document.get_toc()
            current = {entry["id"]: find_outline_page(outline, entry["heading"]) for entry in entries}
            total = len(document)
        if current == previous:
            return current, attempt, total
        for entry in entries:
            nodes = body.xpath('.//*[@data-toc-id=$value]', value=entry["id"])
            assert len(nodes) == 1, ("Missing TOC page slot", entry["id"])
            nodes[0].text = str(current[entry["id"]])
        previous = current
    raise AssertionError("Printed contents page numbers did not stabilize in four passes")


def hide_running_marks(target):
    """Remove running heads and folios from cover, title and part plates."""
    with fitz.open(target) as document:
        for page in document:
            if len("".join(page.get_text().split())) >= 120:
                continue
            page.draw_rect(fitz.Rect(0, 0, page.rect.width, 44), color=None, fill=(1, 1, 1), overlay=True)
            page.draw_rect(fitz.Rect(0, page.rect.height - 52, page.rect.width, page.rect.height), color=None, fill=(1, 1, 1), overlay=True)
        document.saveIncr()


def package_epub(stem, title, docs, image_names, css, cover_name):
    package = etree.Element("{%s}package" % OPF, nsmap={None: OPF, "dc": DC}, version="3.0", **{"unique-identifier": "book-id"})
    metadata = etree.SubElement(package, "{%s}metadata" % OPF)
    for name, value in [
        ("identifier", "urn:llm-course:" + stem + ":1.1.2"),
        ("title", title),
        ("language", "zh-CN"),
        ("creator", "Vibe Coding 101 课程项目"),
        ("rights", "课程原创课文与图解；第三方来源和许可见正文，未转授权外部书图。"),
    ]:
        node = etree.SubElement(metadata, "{%s}%s" % (DC, name))
        node.text = value
        if name == "identifier":
            node.set("id", "book-id")
    etree.SubElement(metadata, "{%s}meta" % OPF, property="dcterms:modified").text = "2026-11-10T00:00:00Z"
    etree.SubElement(metadata, "{%s}meta" % OPF, name="cover", content="cover-image")
    manifest = etree.SubElement(package, "{%s}manifest" % OPF)
    for index, (name, _) in enumerate(docs.items()):
        attrs = {"id": "doc-" + str(index), "href": name, "media-type": "application/xhtml+xml"}
        if name == "nav.xhtml":
            attrs["properties"] = "nav"
        etree.SubElement(manifest, "{%s}item" % OPF, **attrs)
    etree.SubElement(manifest, "{%s}item" % OPF, id="css", href="book.css", **{"media-type": "text/css"})
    for index, name in enumerate(sorted(image_names)):
        attrs = {"id": "image-" + str(index), "href": "images/" + name, "media-type": "image/png"}
        if name == cover_name:
            attrs["properties"] = "cover-image"
            attrs["id"] = "cover-image"
        etree.SubElement(manifest, "{%s}item" % OPF, **attrs)
    spine = etree.SubElement(package, "{%s}spine" % OPF)
    for index in range(len(docs)):
        etree.SubElement(spine, "{%s}itemref" % OPF, idref="doc-" + str(index))
    container = b'<?xml version="1.0" encoding="utf-8"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>'
    with zipfile.ZipFile(OUT / (stem + ".epub"), "w") as archive:
        def put(name, data, compressed=True):
            info = zipfile.ZipInfo(name, (2026, 11, 10, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED if compressed else zipfile.ZIP_STORED
            info.external_attr = 0o644 << 16
            archive.writestr(info, data)

        put("mimetype", b"application/epub+zip", False)
        put("META-INF/container.xml", container)
        put("OEBPS/content.opf", etree.tostring(package, xml_declaration=True, encoding="utf-8"))
        put("OEBPS/book.css", css)
        for name, (document_title, body) in docs.items():
            put("OEBPS/" + name, xhtml_document(document_title, body))
        for name in sorted(image_names):
            put("OEBPS/images/" + name, (WORK / "images" / name).read_bytes())


def run():
    curriculum = json_file(ROOT / "book/llm/course.json")["curriculum"]
    chapters = curriculum["chapters"]
    stages = curriculum["stages"]
    stage_notes = json_file(ROOT / "book/llm/stages.json")
    stage_map = {stage["id"]: stage for stage in stage_notes["stages"]}
    deep_meta = stage_notes["deepReading"]
    content_document.chapters = chapters
    fingerprint = source_hash()
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / "images").mkdir(exist_ok=True)
    shutil.copyfile(SHEET, WORK / "book.css")
    css = SHEET.read_bytes()
    css_epub = css + b"\n.toc-dots,.toc-page{display:none}\n.title-page{min-height:0}\n"
    node = shutil.which("node")
    if node:
        os.environ.setdefault("PLAYWRIGHT_NODEJS_PATH", node)
    if os.name == "nt":
        os.environ["NODE_OPTIONS"] = os.environ.get("NODE_OPTIONS", "") + " --preserve-symlinks --preserve-symlinks-main"
    results = {}
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(viewport={"width": 1300, "height": 1800}, device_scale_factor=2)
        context.set_offline(True)
        page = context.new_page()
        image_names = set()
        ensure_image(page, ASSETS / "cover-course.svg", image_names, WORK / "images")
        ensure_image(page, ASSETS / stage_notes["map"]["file"], image_names, WORK / "images")
        for stage in stages:
            ensure_image(page, ASSETS / stage_map[stage["id"]]["plate"], image_names, WORK / "images")

        for answers in (False, True):
            stem = "llm-course-answers" if answers else "llm-course"
            title = curriculum["title"] + (" · 核对依据" if answers else "")
            docs = {}
            entries = []
            if not answers:
                docs["cover.xhtml"] = ("封面", element("body", **{"class": "cover-page"}))
                docs["cover.xhtml"][1].append(
                    etree.Element("img", src="images/cover-course.png", alt=curriculum["title"] + " 封面")
                )
            docs["titlepage.xhtml"] = ("书名", title_page_document(curriculum, answers))
            docs["howto.xhtml"] = ("怎么读", howto_document(answers))
            if not answers:
                docs["map.xhtml"] = (stage_notes["map"]["title"], map_document(stage_notes["map"]))
                entries.append({
                    "kind": "map",
                    "id": "map",
                    "heading": stage_notes["map"]["title"],
                    "label": stage_notes["map"]["title"],
                    "href": "map.xhtml#map",
                })

            for stage in stages:
                stage_chapters = [chapter for chapter in chapters if chapter["stage"] == stage["id"]]
                if not answers:
                    docs["stage-%s-plate.xhtml" % stage["id"].lower()] = (
                        "%s 阶段插画" % stage["id"],
                        stage_plate_document(stage, stage_map[stage["id"]], image_names),
                    )
                    docs["stage-%s.xhtml" % stage["id"].lower()] = (
                        "%s 阶段导言" % stage["id"],
                        stage_intro_document(stage, stage_map[stage["id"]], stage_chapters),
                    )
                    entries.append({
                        "kind": "stage",
                        "id": stage["id"],
                        "heading": "%s %s" % (stage["id"], stage["title"]),
                        "label": "%s · %s / %s" % (stage["id"], stage["title"], stage["gate"]),
                        "href": "stage-%s.xhtml#%s" % (stage["id"].lower(), stage["id"]),
                    })
                for chapter in stage_chapters:
                    suffix = "-answer" if answers else ""
                    filename = chapter["id"].lower() + suffix + ".xhtml"
                    article = content_document(chapter, answers, page, image_names)
                    heading = "".join(article.xpath(".//h1")[0].itertext()).strip()
                    docs[filename] = (heading, article)
                    entries.append({
                        "kind": "chapter",
                        "id": chapter["id"],
                        "heading": heading,
                        "label": chapter["title"] if not answers else heading,
                        "href": filename + "#" + chapter["id"] + suffix,
                    })

            if not answers:
                deep = deep_reading_document(curriculum, page, image_names)
                docs["deep-reading.xhtml"] = (deep_meta["title"], deep)
                entries.append({
                    "kind": "deep",
                    "id": "deep-reading",
                    "heading": deep_meta["title"],
                    "label": deep_meta["title"],
                    "href": "deep-reading.xhtml#deep-reading",
                })
                glossary = glossary_document(curriculum, page, image_names)
                docs["glossary.xhtml"] = (stage_notes["glossary"]["title"], glossary)
                entries.append({
                    "kind": "glossary",
                    "id": "glossary",
                    "heading": stage_notes["glossary"]["title"],
                    "label": stage_notes["glossary"]["title"],
                    "href": "glossary.xhtml#glossary",
                })
            docs["colophon.xhtml"] = ("版本说明", colophon_document(curriculum, answers))

            toc = toc_document(curriculum, entries, answers)
            ordered = {}
            for name in ["cover.xhtml", "titlepage.xhtml", "howto.xhtml"]:
                if name in docs:
                    ordered[name] = docs[name]
            ordered["nav.xhtml"] = ("目录", toc)
            for name, value in docs.items():
                if name not in ordered:
                    ordered[name] = value
            docs = ordered

            reading = WORK / (stem + ".html")
            body = print_body_from_docs(docs)
            pages, passes, total = print_with_pages(page, title, body, reading, OUT / (stem + ".pdf"), entries)
            hide_running_marks(OUT / (stem + ".pdf"))
            with fitz.open(OUT / (stem + ".pdf")) as pdf:
                outline = pdf.get_toc()
                first_entry = min(pages.values())
                toc_page = next(number for level, text, number in outline if "".join(text.split()) == ("核对依据目录" if answers else "目录") and number < first_entry)
                toc_marker = "C30" if answers else "术语"
                toc_last = max(number for number in range(toc_page, first_entry) if toc_marker in pdf[number - 1].get_text())
                results[stem] = {
                    "pdfPages": len(pdf),
                    "outlineEntries": len(outline),
                    "chapters": len(chapters),
                    "stagePages": 0 if answers else len(stages) * 2,
                    "tocEntries": len(entries),
                    "tocPages": toc_last - toc_page + 1,
                    "contentsPasses": passes,
                    "images": len(image_names),
                    "pages": pages,
                }
            epub_docs = {}
            for name, (document_title, document_body) in docs.items():
                clean = deepcopy(document_body)
                if name == "nav.xhtml":
                    for node in clean.xpath('.//*[contains(concat(" ",normalize-space(@class)," ")," toc-dots ") or contains(concat(" ",normalize-space(@class)," ")," toc-page ")]'):
                        parent = node.getparent()
                        if parent is not None:
                            parent.remove(node)
                epub_docs[name] = (document_title, clean)
            package_epub(stem, title, epub_docs, image_names, css_epub, "cover-course.png")
        browser.close()
    if source_hash() != fingerprint:
        raise RuntimeError("Course source changed during book export")
    filenames = [stem + suffix for stem in results for suffix in (".pdf", ".epub")]
    metadata = {
        "version": curriculum["version"],
        "sourceHash": fingerprint,
        "design": {
            "page": "A5",
            "bodyFace": "Noto Serif SC / Songti",
            "cover": "cover-course.svg",
            "stagePlates": len(stages),
            "deepReading": deep_meta["title"],
            "glossary": stage_notes["glossary"]["title"],
        },
        "editions": results,
        "files": {name: {"bytes": (OUT / name).stat().st_size, "sha256": hashlib.sha256((OUT / name).read_bytes()).hexdigest()} for name in filenames},
        "limitations": ["真实初学者验收未完成", "运行证据与独立复做分开", "EPUB和PDF不执行代码"],
    }
    (OUT / "llm-course.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metadata, ensure_ascii=False))


if __name__ == "__main__":
    run()
