"""Build the twelve-lesson local PDF and EPUB from generated lesson pages.

Run after build:llm. Uses Python Playwright, lxml and PyMuPDF; never calls a model.
"""

import hashlib
import json
import os
import shutil
import sys
import zipfile
from pathlib import Path

import fitz
from lxml import etree, html
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / "exports" / "llm"
OUT = ROOT / "deliverables"
REVIEW = ROOT / "tmp" / "llm-book-review"
STEM = "llm-explained-handdraw"
XHTML = "http://www.w3.org/1999/xhtml"
EPUB = "http://www.idpf.org/2007/ops"
OPF = "http://www.idpf.org/2007/opf"
DC = "http://purl.org/dc/elements/1.1/"
FIXED_DATE = "2026-11-07T00:00:00Z"


def json_file(path):
    return json.loads(path.read_text(encoding="utf-8"))


def element(tag, text=None, **attrs):
    node = etree.Element(tag, **attrs)
    node.text = text
    return node


def append(parent, tag, text=None, **attrs):
    child = element(tag, text, **attrs)
    parent.append(child)
    return child


def xhtml_document(title, body, stylesheet="book.css"):
    doc = etree.Element("{%s}html" % XHTML, nsmap={None: XHTML, "epub": EPUB})
    doc.set("lang", "zh-CN")
    doc.set("{http://www.w3.org/XML/1998/namespace}lang", "zh-CN")
    head = append(doc, "head")
    append(head, "meta", charset="utf-8")
    append(head, "title", title)
    append(head, "meta", name="viewport", content="width=device-width, initial-scale=1")
    append(head, "link", rel="stylesheet", type="text/css", href=stylesheet)
    if body.tag.rsplit("}", 1)[-1] != "body":
        wrapper = element("body")
        wrapper.append(body)
        body = wrapper
    doc.append(body)
    for node in doc.iter():
        if isinstance(node.tag, str) and not node.tag.startswith("{"):
            node.tag = "{%s}%s" % (XHTML, node.tag)
    return etree.tostring(doc, encoding="utf-8", xml_declaration=True, pretty_print=True, doctype="<!DOCTYPE html>")


def clean_chapter(lesson):
    page = html.fromstring((WEB / (lesson["slug"] + ".html")).read_bytes())
    article = page.xpath('//article[contains(concat(" ",normalize-space(@class)," ")," lesson ")]')[0]
    for node in article.xpath('.//section[@data-experiment] | .//form | .//section[@class="model-practice"] | .//nav'):
        node.drop_tree()
    # lxml parses noscript contents as elements; retain the shared static result.
    for node in article.xpath('.//noscript'):
        node.drop_tag()
    for node in article.xpath('.//details'):
        node.tag = "section"
        for summary in node.xpath('./summary'):
            summary.tag = "h2" if "sources" in node.get("class", "") else "h3"
    for node in article.iter():
        for key in list(node.attrib):
            if key == "hidden" or key.startswith("aria-") or key.startswith("data-"):
                del node.attrib[key]
    # The web quiz's static version has the question and correct answer.
    for quiz in article.xpath('.//section[@class="quiz"]'):
        for child in list(quiz):
            quiz.remove(child)
        append(quiz, "h2", "自己判断一次")
        append(quiz, "p", lesson["question"])
        options = append(quiz, "ol")
        for option in lesson["options"]:
            append(options, "li", option)
        answer = append(quiz, "div", **{"class": "answer"})
        append(answer, "p", "答案：" + lesson["options"][lesson["correct"]])
        append(answer, "p", lesson["feedback"])
    for heading in article.xpath('.//section[contains(@class,"lab")]/h2'):
        heading.text = "纸上实验：步骤与结果"
    for para in article.xpath('.//section[contains(@class,"lab")]/p'):
        if "当前浏览器没有执行" in para.text_content():
            para.text = "先按这些步骤比较结果；网页版本提供对应的可操作实验。"
    for anchor in article.xpath('.//a[@href]'):
        target = anchor.get("href")
        if not target.startswith(("https://", "http://", "#")):
            if anchor.getparent() is not None and "sources" in anchor.getparent().get("class", ""):
                anchor.drop_tree()
            else:
                anchor.drop_tag()
    for image in article.xpath('.//img'):
        image.set("src", "images/" + Path(image.get("src")).name)
    article.set("id", lesson["id"])
    article.set("class", "chapter")
    article.xpath('./p[@class="eyebrow"]')[0].set("class", "chapter-id")
    return article


def cover_svg():
    return '''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="1260" viewBox="0 0 900 1260" role="img" aria-labelledby="title desc">
  <title id="title">把大模型拆开看</title><desc id="desc">十二课手绘图解，从文字、生成和训练，走到检索、工具与资料核验。</desc>
  <rect width="900" height="1260" fill="#fbfaf6"/>
  <g fill="#1f2328" font-family="Microsoft YaHei,sans-serif">
    <text x="78" y="110" font-size="26">VIBE CODING 101 · 原理与应用</text>
    <text x="72" y="263" font-size="74">把大模型</text><text x="72" y="367" font-size="90">拆开看</text>
    <path d="M74 398 Q252 384 520 397 Q580 403 612 394" fill="none" stroke="#1f883d" stroke-width="8" stroke-linecap="round"/>
    <text x="78" y="466" font-size="32">从一句话，到能核对的资料助手</text>
    <path d="M94 575 L752 566 L784 594 L779 919 L86 925 Z M752 566 L750 603 L784 594" fill="#fffdf8" stroke="#1f2328" stroke-width="4"/>
    <path d="M126 626 Q430 621 738 630 M126 687 L733 683 M126 748 Q430 745 731 752 M126 815 L730 810 M126 878 L733 874" fill="none" stroke="#e6e1d4" stroke-width="3"/>
    <text x="142" y="666" font-size="33">文字 → 向量 → 候选 → 接下一步</text>
    <path d="M145 719 L688 715 L699 766 L141 771 Z" fill="#d3efd9"/>
    <text x="158" y="757" font-size="33">预测 → 比较目标 → 调整参数</text>
    <text x="142" y="846" font-size="33">找材料 → 用工具 → 回查依据</text>
    <path d="M124 951 Q384 980 732 950" fill="none" stroke="#1f2328" stroke-width="3"/>
    <text x="78" y="1034" font-size="32">十二课 · 手绘图解 · 纸上实验</text>
    <text x="78" y="1095" font-size="26">实际模型练习：DeepSeek V4.1 Flash · Kimi K3</text>
    <text x="78" y="1180" font-size="26">试读版 / 2026.11 / 含自测与来源</text>
  </g>
</svg>'''


def clean_review(guide=False, workbook=False):
    name = "review-guide" if guide else "check-understanding"
    page = html.fromstring((WEB / (name + ".html")).read_bytes())
    article = page.get_element_by_id("review-guide-content" if guide else "review-content")
    for node in article.xpath('.//*[contains(concat(" ",normalize-space(@class)," ")," no-print ")]'):
        node.drop_tree()
    if not workbook:
        for node in article.xpath('.//div[@class="answer-space"] | .//p[@class="reader-code"]'):
            node.drop_tree()
    for img in article.xpath('.//img'):
        img.set("src", "images/" + Path(img.get("src")).name)
    article.set("class", "reading-part review-guide" if guide else "reading-part review-appendix")
    article.set("id", "review-guide" if guide else "review")
    return article


def frontmatter(course, models, cover):
    cover_body = element("body", **{"class": "cover"})
    append(cover_body, "img", src="images/" + cover, alt="把大模型拆开看：十二课手绘图解")
    intro = element("body", **{"class": "reading-part"})
    append(intro, "h1", "怎么读这本小书")
    append(intro, "p", "从一段文字怎样被处理开始，亲手观察生成、注意力和参数更新，再把这些认识用到检索资料、调用工具和核对答案。正文保留公式，第一次读可以先看例子，之后再回到“再深一层”。")
    append(intro, "p", "想先走通一次，可以读 L02、L01、L07；想认真理解，从 L01 按课号读；要交付作品，最后完成 L12，并换一份没见过的通知独立核验。")
    figure_count = len({file for lesson in course["lessons"] for file in [lesson["figure"], *lesson.get("extraFigures", [])]})
    append(intro, "p", f"这份电子书收录十二课、{figure_count} 张手绘图、纸上实验步骤、静态结果、自测与来源。网页里的按钮不会在 PDF 或 EPUB 中执行；纸上实验已保留必要输入和结果，可离线对照。")
    append(intro, "p", "人工向量、教学矩阵和预置回答都注明范围；本课程没有采集 DeepSeek V4.1 Flash 或 Kimi K3 的实测输出，也不以教学数字推断它们的内部状态。真实初学者试读与学习效果验收仍待进行。")
    append(intro, "p", "版本：" + course["version"] + "；资料核验截至 " + models["checkedOn"] + "。这是试读版，不是学习成效或线上模型性能报告。")
    append(intro, "p", "书末附六道换材料练习，先独立作答再核对。参考答案与陪读记录另放在 llm-reading-guide.pdf；需要留白作答的 A4 版本是 llm-reading-tasks.pdf，和本书一起保存在交付目录中。")
    append(intro, "p", "十二课后附进阶回查：区分 KV 缓存与参数、MoE 专家与任务角色，以及预填充/解码的计算成本。第一次读可以先跳过，遇到相关问题再回查。")
    append(intro, "p", "应用回查进一步区分提示、少样本示例、检索和微调，并解释自检、引用与资料中命令的边界。它与旧书的提示词、RAG 修订章共享正文。")
    append(intro, "p", "系统回查把外部保存、当前输入和缓存分开说明，提供输出预算、摘要核验和本地两步工具流程的纸上结果。它与上下文、Agent 修订章共享正文；仓库读者还可直接运行所附 Node 示例。")
    append(intro, "p", "结构回查解释注意力如何接入网络层、多头结果怎样汇合，并分清原始编码器—解码器和 decoder-only 路线。双头矩阵的结果来自本地计算，仍是人工教学模型。")
    toc_body = element("body", **{"class": "reading-part"})
    append(toc_body, "h1", "十二课目录")
    nav = append(toc_body, "nav", id="toc")
    nav.set("{%s}type" % EPUB, "toc")
    listing = append(nav, "ol")
    for lesson in course["lessons"]:
        li = append(listing, "li")
        append(li, "a", lesson["id"] + " · " + lesson["title"], href=lesson["slug"] + ".xhtml#" + lesson["id"])
    li = append(listing, "li")
    append(li, "a", "进阶回查：缓存、专家与计算成本", href="advanced.xhtml#advanced")
    li = append(listing, "li")
    append(li, "a", "结构回查：注意力怎样拼成一层", href="architecture.xhtml#architecture")
    li = append(listing, "li")
    append(li, "a", "应用回查：提示、检索与核验", href="applications.xhtml#applications")
    li = append(listing, "li")
    append(li, "a", "系统回查：上下文与工具执行", href="execution.xhtml#execution")
    li = append(listing, "li")
    append(li, "a", "实际模型练习与使用说明", href="practice.xhtml")
    li = append(listing, "li")
    append(li, "a", "合上书，换一份材料试试", href="review.xhtml#review")
    practice = element("body", **{"class": "reading-part"})
    append(practice, "h1", "在实际模型里复做")
    append(practice, "p", "分别使用 DeepSeek V4.1 Flash 与 Kimi K3，给出同一份任务和通知。保存首次回答，再核对缺失项和每条引用。不把语气、自信或回答长度当作正确率。")
    append(practice, "pre", models["task"])
    for model in models["models"]:
        append(practice, "h2", model["name"])
        append(practice, "p", model["note"])
        p = append(practice, "p")
        append(p, "a", model["url"], href=model["url"])
    append(practice, "p", "记录：" + "、".join(models["recordFields"]) + "。如果产品已不再提供所指定版本，保留实际版本名称，不能把其他模型的结果写给它。")
    append(practice, "h2", "这本书的边界")
    append(practice, "p", models["limitations"])
    append(practice, "p", "课程图解为可编辑 SVG 原稿；EPUB 使用同图的高分辨率 PNG，便于不同阅读器显示中文。PDF 保留矢量图，字体由本地浏览器嵌入。EPUB 使用阅读器提供的中文字体，可调整字号。")
    append(practice, "p", "tokenizer 快照来自 js-tiktoken 1.0.21（MIT）。后附完整许可。页面审查方法参考 unslop，Damir Sokolovsky，CC BY 4.0；中文编辑参考本地 humanizer-zh，保留事实、范围与确定程度。")
    p = append(practice, "p")
    append(p, "a", "unslop 方法及归属", href="https://heydamir.design/unslop")
    append(practice, "h2", "js-tiktoken 许可")
    append(practice, "pre", (ROOT / "book/llm/fixtures/js-tiktoken-LICENSE").read_text(encoding="utf-8"))
    return {"cover.xhtml": ("封面", cover_body), "intro.xhtml": ("怎么读这本小书", intro), "nav.xhtml": ("目录", toc_body), "practice.xhtml": ("实际模型练习与使用说明", practice)}


def epub_package(course, docs, images, css, cover_name):
    package = etree.Element("{%s}package" % OPF, nsmap={None: OPF, "dc": DC}, version="3.0")
    package.set("unique-identifier", "book-id")
    metadata = etree.SubElement(package, "{%s}metadata" % OPF)
    for name, value in [("identifier", "urn:uuid:df2ecb0a-7212-4918-8af6-b66b20b6cdf4"), ("title", course["title"]), ("language", "zh-CN"), ("creator", "Vibe Coding 101 课程项目"), ("description", course["description"]), ("rights", "课程原创课文与图解；第三方素材与方法归属见正文及许可说明。")]:
        node = etree.SubElement(metadata, "{%s}%s" % (DC, name))
        node.text = value
        if name == "identifier":
            node.set("id", "book-id")
    modified = etree.SubElement(metadata, "{%s}meta" % OPF, property="dcterms:modified")
    modified.text = FIXED_DATE
    etree.SubElement(metadata, "{%s}meta" % OPF, name="cover", content="cover-image")
    manifest = etree.SubElement(package, "{%s}manifest" % OPF)
    for index, name in enumerate(docs):
        attrs = {"id": "doc-" + str(index), "href": name, "media-type": "application/xhtml+xml"}
        if name == "nav.xhtml":
            attrs["properties"] = "nav"
        etree.SubElement(manifest, "{%s}item" % OPF, **attrs)
    etree.SubElement(manifest, "{%s}item" % OPF, id="css", href="book.css", **{"media-type": "text/css"})
    etree.SubElement(manifest, "{%s}item" % OPF, id="ncx", href="toc.ncx", **{"media-type": "application/x-dtbncx+xml"})
    for i, name in enumerate(images):
        attrs = {"id": "cover-image" if name == cover_name else "image-" + str(i), "href": "images/" + name, "media-type": "image/png"}
        if name == cover_name:
            attrs["properties"] = "cover-image"
        etree.SubElement(manifest, "{%s}item" % OPF, **attrs)
    spine = etree.SubElement(package, "{%s}spine" % OPF, toc="ncx")
    for index, name in enumerate(docs):
        etree.SubElement(spine, "{%s}itemref" % OPF, idref="doc-" + str(index))
    guide = etree.SubElement(package, "{%s}guide" % OPF)
    etree.SubElement(guide, "{%s}reference" % OPF, type="cover", title="封面", href="cover.xhtml")
    etree.SubElement(guide, "{%s}reference" % OPF, type="toc", title="目录", href="nav.xhtml")
    ncx_ns = "http://www.daisy.org/z3986/2005/ncx/"
    ncx = etree.Element("{%s}ncx" % ncx_ns, nsmap={None: ncx_ns}, version="2005-1")
    head = etree.SubElement(ncx, "{%s}head" % ncx_ns)
    etree.SubElement(head, "{%s}meta" % ncx_ns, name="dtb:uid", content="urn:uuid:df2ecb0a-7212-4918-8af6-b66b20b6cdf4")
    title = etree.SubElement(ncx, "{%s}docTitle" % ncx_ns)
    etree.SubElement(title, "{%s}text" % ncx_ns).text = course["title"]
    navmap = etree.SubElement(ncx, "{%s}navMap" % ncx_ns)
    for index, (name, (title, _)) in enumerate(docs.items()):
        point = etree.SubElement(navmap, "{%s}navPoint" % ncx_ns, id="point-" + str(index), playOrder=str(index + 1))
        label = etree.SubElement(point, "{%s}navLabel" % ncx_ns)
        etree.SubElement(label, "{%s}text" % ncx_ns).text = title
        etree.SubElement(point, "{%s}content" % ncx_ns, src=name)
    container = b'<?xml version="1.0" encoding="utf-8"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>'
    target = OUT / (STEM + ".epub")
    with zipfile.ZipFile(target, "w") as archive:
        def put(name, data, compressed=True):
            info = zipfile.ZipInfo(name, (2026, 11, 7, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED if compressed else zipfile.ZIP_STORED
            info.external_attr = 0o644 << 16
            archive.writestr(info, data)
        put("mimetype", b"application/epub+zip", False)
        put("META-INF/container.xml", container)
        put("OEBPS/content.opf", etree.tostring(package, xml_declaration=True, encoding="utf-8", pretty_print=True))
        put("OEBPS/toc.ncx", etree.tostring(ncx, xml_declaration=True, encoding="utf-8", pretty_print=True))
        put("OEBPS/book.css", css)
        for name, (title, body) in docs.items():
            put("OEBPS/" + name, xhtml_document(title, body))
        for name in images:
            put("OEBPS/images/" + name, (REVIEW / "images" / name).read_bytes())
    return target


def source_hash():
    paths = [*(ROOT / "book/llm").rglob("*"), *(ROOT / "book/assets/handdraw/llm").glob("*"), *(ROOT / "scripts/llm").glob("*"), ROOT / "scripts/build-llm.mjs"]
    digest = hashlib.sha256()
    # Native WindowsPath ordering folds case; use the same relative POSIX order on every OS.
    for path in sorted(paths, key=lambda item: item.relative_to(ROOT).as_posix()):
        if path.is_file() and path.suffix in [".md", ".json", ".js", ".cjs", ".mjs", ".css", ".svg", ".py"] and not path.name.endswith(".test.js") and not path.name.startswith(("check_", "validate-")):
            digest.update(path.relative_to(ROOT).as_posix().encode())
            digest.update(path.read_bytes().replace(b"\r\n", b"\n"))
    return digest.hexdigest()


def run():
    sys.stdout.reconfigure(encoding="utf-8")
    course = json_file(ROOT / "book/llm/course.json")
    models = json_file(ROOT / "book/llm/models.json")
    lessons = [lesson for lesson in course["lessons"] if lesson["status"] == "ready"]
    assert len(lessons) == 12, "Only export when all twelve lessons are built"
    source_fingerprint = source_hash()
    OUT.mkdir(exist_ok=True)
    (REVIEW / "images").mkdir(parents=True, exist_ok=True)
    css = (ROOT / "scripts/llm/book.css").read_bytes()
    (REVIEW / "book.css").write_bytes(css)
    figures = sorted({file for lesson in lessons for file in [lesson["figure"], *lesson.get("extraFigures", [])]})
    (REVIEW / "images/cover.svg").write_text(cover_svg(), encoding="utf-8")
    for file in figures:
        shutil.copyfile(ROOT / "book/assets/handdraw/llm" / file, REVIEW / "images" / file)
    node = shutil.which("node")
    if node:
        os.environ.setdefault("PLAYWRIGHT_NODEJS_PATH", node)
    if os.name == "nt":
        current = os.environ.get("NODE_OPTIONS", "")
        os.environ["NODE_OPTIONS"] = current + " --preserve-symlinks --preserve-symlinks-main"
    errors = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(viewport={"width": 1000, "height": 1400}, device_scale_factor=2)
        context.set_offline(True)
        page = context.new_page()
        page.on("pageerror", lambda error: errors.append(str(error)))
        for file in ["cover.svg", *figures]:
            svg = (REVIEW / "images" / file).read_text(encoding="utf-8")
            page.set_content('<!doctype html><html><head><meta charset="utf-8"></head><body style="margin:0;display:inline-block">' + svg + "</body></html>")
            page.evaluate("document.fonts.ready")
            page.locator("svg").screenshot(path=str(REVIEW / "images" / file.replace(".svg", ".png")))
        chapters = {lesson["slug"] + ".xhtml": (lesson["title"], clean_chapter(lesson)) for lesson in lessons}
        front = frontmatter(course, models, "cover.svg")
        print_body = element("body")
        advanced_page = html.fromstring((WEB / "advanced.html").read_bytes())
        advanced = advanced_page.get_element_by_id("advanced-content")
        advanced.set("id", "advanced")
        advanced.set("class", "reading-part")
        application_page = html.fromstring((WEB / "applications-guide.html").read_bytes())
        applications = application_page.get_element_by_id("applications-content")
        applications.set("id", "applications")
        applications.set("class", "reading-part")
        for image in applications.xpath('.//img'):
            image.set("src", "images/" + Path(image.get("src")).name)
        for anchor in applications.xpath('.//a[@href]'):
            href = anchor.get("href")
            if href.endswith(".html") and href[:-5] in {lesson["slug"] for lesson in lessons}:
                target = next(lesson for lesson in lessons if lesson["slug"] == href[:-5])
                anchor.set("href", target["slug"] + ".xhtml#" + target["id"])
        execution_page = html.fromstring((WEB / "execution-guide.html").read_bytes())
        execution = execution_page.get_element_by_id("execution-content")
        execution.set("id", "execution")
        execution.set("class", "reading-part")
        for image in execution.xpath('.//img'):
            image.set("src", "images/" + Path(image.get("src")).name)
        architecture_page = html.fromstring((WEB / "architecture-guide.html").read_bytes())
        architecture = architecture_page.get_element_by_id("architecture-content")
        architecture.set("id", "architecture")
        architecture.set("class", "reading-part")
        for image in architecture.xpath('.//img'):
            image.set("src", "images/" + Path(image.get("src")).name)
        for anchor in architecture.xpath('.//a[@href]'):
            href = anchor.get("href")
            if href.endswith(".html") and href[:-5] in {lesson["slug"] for lesson in lessons}:
                target = next(lesson for lesson in lessons if lesson["slug"] == href[:-5])
                anchor.set("href", target["slug"] + ".xhtml#" + target["id"])
        ordered = [front["cover.xhtml"], front["intro.xhtml"], front["nav.xhtml"], *chapters.values(), ("进阶回查", advanced), ("结构回查", architecture), ("应用回查", applications), ("系统回查", execution), front["practice.xhtml"], ("换材料练习", clean_review())]
        for title, body in ordered:
            section = etree.fromstring(etree.tostring(body))
            section.tag = "section"
            # On paper, pair each chapter question with its main diagram.
            # Keeping a tall figure after the opening paragraphs leaves large
            # empty page tails when print layout moves it to the next page.
            article_body = section.find('.//div[@class="article-body"]')
            if article_body is None and section.get("id") in ["execution", "architecture"]:
                article_body = section
            if article_body is not None:
                primary = article_body.find('./figure')
                heading = article_body.find('./h1')
                if primary is not None and heading is not None:
                    article_body.remove(primary)
                    article_body.insert(list(article_body).index(heading) + 1, primary)
                    primary.set("class", "concept-figure chapter-figure")
            if section.get("id") in ["execution", "architecture"]:
                for diagram in section.findall('./figure')[1:]:
                    preceding = diagram.xpath('preceding-sibling::h2[1]')
                    if preceding:
                        section.remove(diagram)
                        section.insert(list(section).index(preceding[0]) + 1, diagram)
            for a in section.xpath('.//a[@href]'):
                href = a.get("href")
                if ".xhtml#" in href:
                    a.set("href", "#" + href.split("#", 1)[1])
                elif href == "practice.xhtml":
                    a.set("href", "#practice")
            if title == "实际模型练习与使用说明":
                section.set("id", "practice")
            print_body.append(section)
        print_path = REVIEW / "reading.html"
        print_path.write_bytes(xhtml_document(course["title"], print_body))
        page.goto(print_path.as_uri())
        page.evaluate("document.fonts.ready")
        assert page.evaluate("[...document.images].every(i => i.complete && i.naturalWidth > 0)")
        page.pdf(path=str(OUT / (STEM + ".pdf")), prefer_css_page_size=True, print_background=True, tagged=True, outline=True,
                 display_header_footer=True, header_template="<div></div>", footer_template='<div style="width:100%;text-align:center;font-size:9px;color:#57606a;font-family:sans-serif"><span class="pageNumber"></span> / <span class="totalPages"></span></div>')
        (REVIEW / "review-print.css").write_bytes((ROOT / "scripts/llm/review-print.css").read_bytes())
        for guide in [False, True]:
            stem = "llm-reading-guide" if guide else "llm-reading-tasks"
            body = clean_review(guide=guide, workbook=True)
            path = REVIEW / (stem + ".html")
            path.write_bytes(xhtml_document("陪读与核对记录" if guide else "换材料练习", body, stylesheet="review-print.css"))
            page.goto(path.as_uri())
            page.emulate_media(media="print")
            page.evaluate("document.fonts.ready")
            assert page.evaluate("[...document.images].every(i => i.complete && i.naturalWidth > 0)")
            if not guide:
                expected_lines = sum(task["lines"] for task in json_file(ROOT / "book/llm/review/tasks.json")["tasks"])
                assert page.locator(".answer-line").count() == expected_lines
                assert page.evaluate("""() => [...document.querySelectorAll('.answer-space')].every(space => {
                  const rows = [...space.querySelectorAll('.answer-line')].map(line => line.getBoundingClientRect());
                  return rows.every((row, i) => row.height >= 22 && (i === 0 || row.top >= rows[i-1].bottom - 1));
                })"""), "Writing lines collapsed or overlap in the print DOM"
            page.pdf(path=str(OUT / (stem + ".pdf")), prefer_css_page_size=True, print_background=True, tagged=True, outline=True,
                     display_header_footer=True, header_template="<div></div>", footer_template='<div style="width:100%;text-align:center;font-size:9px;color:#57606a;font-family:sans-serif"><span class="pageNumber"></span> / <span class="totalPages"></span></div>')
        assert not errors, errors
        browser.close()
    epub_front = frontmatter(course, models, "cover.png")
    docs = {name: epub_front[name] for name in ["cover.xhtml", "intro.xhtml", "nav.xhtml"]}
    for name, (title, body) in chapters.items():
        body = etree.fromstring(etree.tostring(body))
        for img in body.xpath('.//img'):
            img.set("src", img.get("src").replace(".svg", ".png"))
        docs[name] = (title, body)
    docs["advanced.xhtml"] = ("进阶回查：缓存、专家与计算成本", etree.fromstring(etree.tostring(advanced)))
    architecture_copy = etree.fromstring(etree.tostring(architecture))
    for image in architecture_copy.xpath('.//img'):
        image.set("src", image.get("src").replace(".svg", ".png"))
    docs["architecture.xhtml"] = ("结构回查：注意力怎样拼成一层", architecture_copy)
    application_copy = etree.fromstring(etree.tostring(applications))
    for image in application_copy.xpath('.//img'):
        image.set("src", image.get("src").replace(".svg", ".png"))
    docs["applications.xhtml"] = ("应用回查：提示、检索与核验", application_copy)
    execution_copy = etree.fromstring(etree.tostring(execution))
    for image in execution_copy.xpath('.//img'):
        image.set("src", image.get("src").replace(".svg", ".png"))
    docs["execution.xhtml"] = ("系统回查：上下文与工具执行", execution_copy)
    docs["practice.xhtml"] = epub_front["practice.xhtml"]
    docs["review.xhtml"] = ("换材料练习", clean_review())
    images = ["cover.png", *[file.replace(".svg", ".png") for file in figures]]
    epub = epub_package(course, docs, images, css, "cover.png")
    # Local unpacked reading preview is review output, not a runtime dependency.
    with zipfile.ZipFile(epub) as archive:
        archive.extractall(REVIEW / "epub")
    pdf = fitz.open(OUT / (STEM + ".pdf"))
    chapter_pages = {}
    for lesson in lessons:
        hits = [i + 1 for i, p in enumerate(pdf) if lesson["id"] in p.get_text() and lesson["title"] in p.get_text()]
        assert hits, "Missing chapter " + lesson["id"]
        chapter_pages[lesson["id"]] = hits[-1] if len(hits) > 1 else hits[0]
    for number in sorted({0, 1, 2, *[value - 1 for value in chapter_pages.values()]}):
        pdf[number].get_pixmap(matrix=fitz.Matrix(1.3, 1.3)).save(REVIEW / f"pdf-page-{number + 1}.png")
    review_pdfs = {}
    for name in ["llm-reading-tasks.pdf", "llm-reading-guide.pdf"]:
        with fitz.open(OUT / name) as supplement:
            review_pdfs[name] = len(supplement)
            for number, sheet in enumerate(supplement):
                sheet.get_pixmap(matrix=fitz.Matrix(0.9, 0.9)).save(REVIEW / (name.replace(".pdf", f"-page-{number+1}.png")))
    assert source_hash() == source_fingerprint, "Source changed during export; rebuild the pages and books"
    result = {"title": course["title"], "version": course["version"], "lessons": len(lessons), "figures": len(figures), "pdfPages": len(pdf), "chapterPages": chapter_pages, "reviewPdfPages": review_pdfs,
              "sourceHash": source_fingerprint, "files": {name: {"bytes": (OUT / name).stat().st_size, "sha256": hashlib.sha256((OUT / name).read_bytes()).hexdigest()} for name in [STEM + ".pdf", STEM + ".epub", *review_pdfs]},
              "limitations": ["真实初学者试读待进行", "实际模型输出未采集", "EPUB 使用阅读器字体，交互改为静态步骤"]}
    (OUT / (STEM + ".json")).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "built", "pages": len(pdf), "chapters": len(lessons), "figures": len(figures), "files": list(result["files"])}, ensure_ascii=False))


if __name__ == "__main__":
    run()
