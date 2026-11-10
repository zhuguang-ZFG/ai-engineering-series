"""Validate the 30-chapter course PDF/EPUB and the separated answer editions.

This complements check_books.py (the twelve-lesson hand-drawn book). It checks
the artifacts that actually ship: source hash, file hashes, A5 pagination,
cover and stage plates, printed contents page numbers, chapter figures, EPUB
manifest/spine/navigation, local links and the bound EPUBCheck reports.
"""

import hashlib
import json
import posixpath
import re
import sys
import zipfile
from pathlib import Path
from urllib.parse import unquote, urlsplit

import fitz
from lxml import etree

from export_books import ROOT, OUT, source_hash

XHTML = "http://www.w3.org/1999/xhtml"
OPF = "http://www.idpf.org/2007/opf"
EPUB = "http://www.idpf.org/2007/ops"
DC = "http://purl.org/dc/elements/1.1/"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def check_pdf(name, metadata, course, answers):
    path = OUT / name
    pdf = fitz.open(path)
    edition = metadata["editions"][name[:-4]]
    assert len(pdf) == edition["pdfPages"], (name, len(pdf), edition["pdfPages"])
    assert len(pdf) >= (20 if answers else 250), name
    outline = pdf.get_toc()
    assert len(outline) == edition["outlineEntries"], (name, "outline count")
    first = pdf[0]
    assert abs(first.rect.width - 419.53) < 2 and abs(first.rect.height - 595.28) < 2, (name, "A5")
    if not answers:
        assert len(first.get_images(full=True)) == 1, (name, "cover image")
    text = "\n".join(page.get_text() for page in pdf)
    assert "\ufffd" not in text, (name, "replacement glyph")
    assert "大模型：从入门到精通" in text
    assert "五阶段 · 三十章" in text
    if not answers:
        assert "深读：五个不能再简化的问题" in text
        assert "S1 会使用" in text and "S5 独立交付" in text
        for stage in course["stages"]:
            assert stage["title"] in text
    for chapter in course["chapters"]:
        if answers:
            assert chapter["id"] in text, (name, "missing chapter", chapter["id"])
        else:
            assert chapter["title"] in text, (name, "missing chapter", chapter["id"])
        if not answers:
            page = edition["pages"][chapter["id"]]
            matches = [number for level, heading, number in outline if heading.strip() == chapter["title"]]
            assert matches and matches[0] == page, (name, chapter["id"], matches, page)
            assert "图 %s-1" % chapter["id"] in text, (name, "missing numbered figure", chapter["id"])
        else:
            page = edition["pages"][chapter["id"]]
            heading = next((item for item in outline if item[1].startswith(chapter["id"] + " ") and item[2] == page), None)
            assert heading, (name, chapter["id"], "answer outline")
    if not answers:
        map_page = edition["pages"]["map"]
        assert any(level == 1 and "全书地图" in heading and number == map_page for level, heading, number in outline), (name, "book map outline")
        deep_page = edition["pages"]["deep-reading"]
        assert any(level == 1 and "深读" in heading and number == deep_page for level, heading, number in outline), (name, "deep reading outline")
        glossary_page = edition["pages"]["glossary"]
        assert any(level == 1 and "术语" in heading and number == glossary_page for level, heading, number in outline), (name, "glossary outline")
        toc_marker = "术语"
    else:
        toc_marker = "C30"
    toc_start = next(number for level, heading, number in outline if heading == ("核对依据目录" if answers else "目录"))
    toc_text = "\n".join(pdf[number - 1].get_text() for number in range(toc_start, toc_start + edition["tocPages"]))
    assert toc_marker in toc_text, (name, "contents marker")
    for chapter in course["chapters"]:
        page = edition["pages"][chapter["id"]]
        assert re.search(r"(?m)^%d$" % page, toc_text), (name, "missing contents page", chapter["id"], page)
    if not answers:
        for stage in course["stages"]:
            lines = toc_text.splitlines()
            index = next((i for i, text in enumerate(lines) if ("%s · %s" % (stage["id"], stage["title"])) in text), None)
            assert index is not None and index + 1 < len(lines), (name, "missing stage page", stage["id"])
            assert lines[index + 1].strip() == str(edition["pages"][stage["id"]]), (name, "wrong stage page", stage["id"])
        map_page = edition["pages"]["map"]
        assert re.search(r"(?m)^%d$" % map_page, toc_text), (name, "missing map page")
        assert edition["tocPages"] <= 3, (name, "contents too long")
        # A normal chapter page carries the running head and its folio.
        sample = edition["pages"]["C01"] + 1
        sample_text = pdf[sample - 1].get_text()
        assert "大模型：从入门到精通" in sample_text and str(sample) in sample_text, (name, "running marks")
        # The cover and part plates must not show a visible folio in the margin.
        for page_number in [1, 7]:
            page = pdf[page_number - 1]
            covered = any(drawing.get("fill") == (1.0, 1.0, 1.0) and drawing["rect"].height > 20 and drawing["rect"].width > 400 for drawing in page.get_drawings())
            assert covered, (name, "display page keeps running marks", page_number)
    for index, page in enumerate(pdf):
        for block in page.get_text("dict")["blocks"]:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    x0, y0, x1, y1 = span["bbox"]
                    assert x0 >= -1 and x1 <= page.rect.width + 1 and y0 >= -1 and y1 <= page.rect.height + 1, (name, index + 1, span)
    return {"pages": len(pdf), "outline": len(outline), "tocPages": edition["tocPages"], "tocStart": toc_start}


def check_epub(name, metadata, course, answers):
    path = OUT / name
    with zipfile.ZipFile(path) as archive:
        info = archive.infolist()
        assert info[0].filename == "mimetype" and info[0].compress_type == zipfile.ZIP_STORED
        assert archive.read("mimetype") == b"application/epub+zip"
        names = set(archive.namelist())
        assert len(names) == len(info), (name, "duplicate zip entries")
        assert not any(name.startswith("/") or ".." in name.split("/") for name in names)
        trees = {item: etree.fromstring(archive.read(item)) for item in names if item.endswith((".xhtml", ".xml", ".opf"))}
        opf = trees["OEBPS/content.opf"]
        ns = {"o": OPF, "h": XHTML, "e": EPUB}
        manifest = {item.get("id"): item for item in opf.xpath("//o:manifest/o:item", namespaces=ns)}
        covers = opf.xpath('//o:manifest/o:item[@properties="cover-image"]', namespaces=ns)
        assert len(covers) == 1 and "OEBPS/" + covers[0].get("href") in names, (name, "cover image")
        for item in manifest.values():
            assert "OEBPS/" + item.get("href") in names, (name, "missing manifest item", item.get("href"))
        spine = opf.xpath("//o:spine/o:itemref", namespaces=ns)
        assert len(spine) == len([name for name in names if name.endswith(".xhtml")]), (name, "spine length")
        nav = trees["OEBPS/nav.xhtml"]
        nav_text = "".join(nav.itertext())
        assert ("深读" in nav_text) == (not answers), (name, "deep reading nav")
        assert ("全书地图" in nav_text) == (not answers), (name, "book map nav")
        assert ("术语" in nav_text) == (not answers), (name, "glossary nav")
        if not answers:
            for stage in course["stages"]:
                assert stage["title"] in nav_text, (name, "stage nav", stage["id"])
        for chapter in course["chapters"]:
            if answers:
                assert chapter["id"] in nav_text, (name, "chapter nav", chapter["id"])
            else:
                assert chapter["title"] in nav_text, (name, "chapter nav", chapter["id"])
        links = 0
        for item, tree in trees.items():
            if not item.endswith(".xhtml"):
                continue
            assert tree.tag == "{%s}html" % XHTML
            assert len(tree.findall("{%s}body" % XHTML)) == 1, (name, "invalid body", item)
            assert not tree.xpath("//*[local-name()='script' or local-name()='form' or local-name()='button' or local-name()='select' or local-name()='noscript']"), (name, "interactive leftover", item)
            for node in tree.xpath("//*[@href or @src]"):
                target = node.get("href") or node.get("src")
                parsed = urlsplit(target)
                if parsed.scheme or target.startswith("//"):
                    assert parsed.scheme in ["http", "https"], (name, target)
                    continue
                dest = posixpath.normpath(posixpath.join(posixpath.dirname(item), unquote(parsed.path))) if parsed.path else item
                assert dest in names, (name, item, target)
                if parsed.fragment:
                    assert dest in trees and trees[dest].xpath("//*[@id=$value]", value=unquote(parsed.fragment)), (name, item, target)
                links += 1
        for item in names:
            if item.endswith(".png"):
                assert archive.read(item).startswith(b"\x89PNG\r\n\x1a\n"), (name, item)
        assert any(item.endswith("images/cover-course.png") for item in names), (name, "course cover asset")
    return {"documents": len(spine), "links": links, "images": len([name for name in names if name.endswith(".png")])}


def check():
    metadata = read_json(OUT / "llm-course.json")
    course_data = read_json(ROOT / "book/llm/course.json")
    course = course_data["curriculum"]
    assert metadata["version"] == course["version"]
    assert metadata["sourceHash"] == source_hash(), "Course books are stale; run npm run export:books:llm"
    for name, expected in metadata["files"].items():
        data = (OUT / name).read_bytes()
        assert len(data) == expected["bytes"], (name, "size")
        assert hashlib.sha256(data).hexdigest() == expected["sha256"], (name, "sha256")
    for stem in ["llm-course", "llm-course-answers"]:
        report = read_json(OUT / (stem + "-epubcheck.json"))
        assert report["status"] == "passed" and all(report[key] == 0 for key in ["fatals", "errors", "warnings"]), (stem, "EPUBCheck")
        assert report["epubSha256"] == hashlib.sha256((OUT / (stem + ".epub")).read_bytes()).hexdigest(), (stem, "EPUBCheck hash")

    pdf = check_pdf("llm-course.pdf", metadata, course, False)
    answers_pdf = check_pdf("llm-course-answers.pdf", metadata, course, True)
    epub = check_epub("llm-course.epub", metadata, course, False)
    answers_epub = check_epub("llm-course-answers.epub", metadata, course, True)
    print(json.dumps({"status": "passed", "coursePdf": pdf, "answersPdf": answers_pdf, "courseEpub": epub, "answersEpub": answers_epub, "epubcheck": "5.3.0: 0 fatal / 0 error / 0 warning for both editions; hashes bound"}, ensure_ascii=False))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    check()
