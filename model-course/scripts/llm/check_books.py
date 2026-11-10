"""Validate the actual local PDF/EPUB and optionally inspect reflow in Chrome."""

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

from export_books import ROOT, OUT, STEM, REVIEW, XHTML, source_hash


def check():
    metadata = json.loads((OUT / (STEM + ".json")).read_text(encoding="utf-8"))
    course = json.loads((ROOT / "book/llm/course.json").read_text(encoding="utf-8"))
    assert metadata["sourceHash"] == source_hash(), "Books are stale; run npm run export:books:llm"
    assert metadata["version"] == course["version"]
    epubcheck = json.loads((OUT / "llm-epubcheck.json").read_text(encoding="utf-8"))
    assert epubcheck["epubSha256"] == hashlib.sha256((OUT / (STEM + ".epub")).read_bytes()).hexdigest(), "EPUBCheck result is stale"
    assert epubcheck["status"] == "passed" and epubcheck["version"] == "5.3.0"
    assert all(epubcheck[key] == 0 for key in ["fatals", "errors", "warnings"])
    assert metadata["lessons"] == 12
    expected_figures = {file for lesson in course["lessons"] for file in [lesson["figure"], *lesson.get("extraFigures", [])]}
    for name in ['architecture-guide.html', 'applications-guide.html', 'execution-guide.html']:
        page = (ROOT / 'exports/llm' / name).read_text(encoding='utf-8')
        expected_figures.update(re.findall(r'src="[^\"]*/handdraw/llm/([^\"]+)"', page))
    assert metadata["figures"] == len(expected_figures)
    for name, expected in metadata["files"].items():
        data = (OUT / name).read_bytes()
        assert hashlib.sha256(data).hexdigest() == expected["sha256"], "Modified artifact " + name
        assert len(data) == expected["bytes"]
    pdf = fitz.open(OUT / (STEM + ".pdf"))
    assert len(pdf) == metadata["pdfPages"] and len(pdf) >= 15
    assert len(pdf.get_toc()) >= 12, "PDF outline missing"
    assert 2 <= metadata["contentsPasses"] <= 4, "PDF contents were not verified after filling page numbers"
    assert len(metadata["contentsPages"]) == len(course["lessons"]) + 6
    toc_pages = [page for page in pdf if "十二课目录" in page.get_text()]
    assert len(toc_pages) == 1, "Printed contents missing or ambiguous"
    toc_index = toc_pages[0].number
    first_chapter = min(metadata["chapterPages"].values()) - 1
    assert first_chapter == toc_index + 1, "Printed contents must fit on one A5 page"
    toc_text = "".join(pdf[i].get_text() for i in range(toc_index, first_chapter))
    compact_contents = "".join(toc_text.split())
    for target, number in metadata["contentsPages"].items():
        label = "".join(metadata["contentsLabels"][target].split())
        assert label + str(number) in compact_contents, ("Wrong printed contents page", target, number)
    for lesson in course["lessons"]:
        number = metadata["chapterPages"][lesson["id"]]
        assert metadata["contentsPages"][lesson["id"]] == number
        assert any(text == lesson["title"] and page_number == number for _, text, page_number in pdf.get_toc()), lesson["id"]
    all_text = "\n".join(page.get_text() for page in pdf)
    for lesson in course["lessons"]:
        assert lesson["title"] in all_text, "PDF missing chapter " + lesson["id"]
        assert lesson["question"] in all_text.replace("\n", ""), "PDF missing self-test " + lesson["id"]
    assert "DeepSeek" in all_text and "Kimi" in all_text
    assert "纸上实验" in all_text and "MIT" in all_text
    for phrase in ["教师的输出，怎样变成学生的参数", "KL(p(T)", "推理蒸馏", "硬标签", "学生第一步给水"]:
        assert phrase in all_text.replace("\n", ""), "PDF missing distillation explanation " + phrase
    assert "缓存、专家与计算成本" in all_text.replace("\n", "")
    assert "应用回查：提示、检索与核验" in all_text.replace("\n", "")
    assert "相似度分数不是事实置信度" in all_text.replace("\n", "")
    assert "系统回查：上下文与工具执行" in all_text.replace("\n", "")
    assert "结构回查：注意力怎样拼成一层" in all_text.replace("\n", "")
    assert "1.231059" in all_text and "-0.231059" in all_text
    assert "输入预算就是3584token" in all_text.replace("\n", "").replace(" ", "")
    review = json.loads((ROOT / "book/llm/review/tasks.json").read_text(encoding="utf-8"))
    for task in review["tasks"]:
        assert task["title"] in all_text.replace("\n", ""), "PDF missing transfer task " + task["id"]
    assert "一种答法" not in all_text, "Facilitator answers leaked into the reader book"
    compact_pages = ["".join(page.get_text().split()) for page in pdf]
    equation_pairs = [
        ("pᵢ(T)=exp(zᵢ/T)/Σⱼexp(zⱼ/T)", "先只看“水”这一项"),
        ("KL(p(T)‖q(T))=Σᵢpᵢ(T)×ln[pᵢ(T)/qᵢ(T)]", "ln是自然对数。读这条式子时"),
        ("L=α×T²×KL(p(T)‖q(T))", "+(1−α)×CE(y,q(1))", "α是调节两种信号份量的旋钮"),
        ("∂L/∂sᵢ=αT(qᵢ(T)−pᵢ(T))", "+(1−α)(qᵢ(1)−yᵢ)", "接着用前面学过的动作"),
        ("L文本=−Σₜlnq学生(ŷₜ|x,ŷ_<t)", "公式中的ŷ_<t就是示范里已经写在前面的部分"),
    ]
    for pieces in equation_pairs:
        assert any(all(piece in text for piece in pieces) for text in compact_pages), ("Formula separated from its explanation", pieces)
    sparse = []
    for i, page in enumerate(pdf):
        assert abs(page.rect.width - 419.53) < 2 and abs(page.rect.height - 595.28) < 2, "Wrong A5 size"
        text = page.get_text()
        assert "\ufffd" not in text, f"Replacement glyph on PDF page {i+1}"
        if len(text.strip()) < 25:
            sparse.append(i + 1)
        for block in page.get_text("dict")["blocks"]:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    assert not any(weight in span["font"].lower() for weight in ["heavy", "black"]), "Unexpected heavy body font"
                    x0, y0, x1, y1 = span["bbox"]
                    assert x0 >= -1 and x1 <= page.rect.width + 1 and y0 >= -1 and y1 <= page.rect.height + 1, (i+1, span)
    # A figure-only page can have little text; retain sparse-page evidence for visual review.
    links = 0
    with zipfile.ZipFile(OUT / (STEM + ".epub")) as archive:
        info = archive.infolist()
        assert info[0].filename == "mimetype" and info[0].compress_type == zipfile.ZIP_STORED
        assert archive.read("mimetype") == b"application/epub+zip"
        names = set(archive.namelist())
        assert len(names) == len(info), "Duplicate ZIP entries"
        assert not any(name.startswith("/") or ".." in name.split("/") for name in names)
        trees = {name: etree.fromstring(archive.read(name)) for name in names if name.endswith((".xhtml", ".xml", ".opf", ".ncx"))}
        opf = trees["OEBPS/content.opf"]
        ns = {"o": "http://www.idpf.org/2007/opf", "h": XHTML, "e": "http://www.idpf.org/2007/ops"}
        manifest = {item.get("id"): item for item in opf.xpath("//o:manifest/o:item", namespaces=ns)}
        for item in manifest.values():
            assert "OEBPS/" + item.get("href") in names
        for ref in opf.xpath("//o:spine/o:itemref", namespaces=ns):
            assert ref.get("idref") in manifest
        for slug, kind in [("generation", "generation"), ("attention", "attention"), ("training", "distillation")]:
            chapter = trees["OEBPS/" + slug + ".xhtml"]
            story = chapter.xpath('//h:section[@class="mechanism"]', namespaces=ns)
            assert len(story) == 1, (slug, "Static mechanism missing or duplicated")
            assert not story[0].xpath('.//h:button | .//h:svg | .//*[@class="mechanism-stage"] | .//*[@class="mechanism-controls"] | .//*[@class="mechanism-status"]', namespaces=ns), (slug, "Playback interface leaked into book")
            images = story[0].xpath('.//h:img/@src', namespaces=ns)
            assert images == ["images/" + kind + "-steps.png"], (slug, images)
            steps = story[0].xpath('.//h:ol/h:li', namespaces=ns)
            assert len(steps) == 4, (slug, "Incomplete mechanism sequence")
            for step in steps:
                assert "".join("".join(step.itertext()).split()) in "".join(all_text.split()), (slug, "PDF lost a static step")
        assert len(opf.xpath("//o:spine/o:itemref", namespaces=ns)) == len(course["lessons"]) + 9
        assert len(opf.xpath('//o:item[@properties="cover-image"]', namespaces=ns)) == 1
        nav = trees["OEBPS/nav.xhtml"]
        assert len(nav.xpath('//h:nav[@e:type="toc"]/h:ol/h:li', namespaces=ns)) == len(course["lessons"]) + 6
        ncx_namespace = {"n": "http://www.daisy.org/z3986/2005/ncx/"}
        ncx = trees["OEBPS/toc.ncx"]
        points = ncx.xpath("//n:navPoint", namespaces=ncx_namespace)
        assert [int(point.get("playOrder")) for point in points] == list(range(1, len(points) + 1)), "NCX reading order differs from document order"
        ncx_targets = ncx.xpath("//n:content/@src", namespaces=ncx_namespace)
        subheadings = 0
        for lesson in course["lessons"]:
            chapter = trees["OEBPS/" + lesson["slug"] + ".xhtml"]
            headings = chapter.xpath('//h:div[@class="article-body"]//h:h2[@id] | //h:div[@class="article-body"]//h:h3[@id]', namespaces=ns)
            headings = [heading for heading in headings if not any(set(parent.get("class", "").split()) & {"lab", "sources", "quiz", "lesson-toc"} for parent in heading.iterancestors())]
            assert headings, (lesson["id"], "Missing authored subheadings")
            expected_sections = [lesson["slug"] + ".xhtml#" + heading.get("id") for heading in headings]
            link = nav.xpath('//h:nav/h:ol/h:li/h:a[@href=$href]', namespaces=ns, href=lesson["slug"] + ".xhtml#" + lesson["id"])[0]
            sections = link.getparent().xpath('./h:ol//h:a/@href', namespaces=ns)
            assert sections == expected_sections, (lesson["id"], "EPUB section navigation missing or reordered")
            assert all(target in ncx_targets for target in expected_sections), (lesson["id"], "NCX omits sections")
            index_id = "contents-" + lesson["id"]
            assert link.getparent().get("id") == index_id, "Chapter index has no direct landing point"
            index_target = "nav.xhtml#" + index_id
            opening = chapter.xpath('//h:p[contains(concat(" ", @class, " "), " book-navigation-start ")]', namespaces=ns)
            assert len(opening) == 1 and opening[0].xpath('./h:a/@href', namespaces=ns) == [index_target, "nav.xhtml#toc"]
            for heading in headings:
                back = heading.getnext()
                assert back is not None and back.get("class") == "book-section-navigation", (lesson["id"], "Section has no nearby directory link")
                assert back.xpath('./h:a/@href', namespaces=ns) == [index_target]
            subheadings += len(sections)
            image_sources = chapter.xpath("//h:img/@src", namespaces=ns)
            for figure in [lesson["figure"], *lesson.get("extraFigures", [])]:
                expected = "images/" + Path(figure).with_suffix(".png").name
                assert image_sources.count(expected) == 1, (lesson["id"], "missing or repeated figure", expected)
        distillation_text = "".join(trees["OEBPS/training.xhtml"].itertext())
        assert "推理蒸馏" in distillation_text and "混合梯度" in distillation_text
        assert "distill-step" not in distillation_text
        architecture_text = "".join(trees["OEBPS/architecture.xhtml"].itertext())
        assert "1.231059" in architecture_text and "-0.231059" in architecture_text
        assert "post-norm" in architecture_text and "pre-norm" in architecture_text
        assert "OEBPS/advanced.xhtml" in names
        application_text = "".join(trees["OEBPS/applications.xhtml"].itertext())
        assert "索引需要维护" in application_text and "通常不更新参数" in application_text
        execution_text = "".join(trees["OEBPS/execution.xhtml"].itertext())
        assert "lookup-1: lookup_price → succeeded, 12.5" in execution_text
        assert "multiply-1: multiply → succeeded, 100" in execution_text
        assert "输入预算就是 3584 token" in execution_text
        assert "OEBPS/review.xhtml" in names
        assert "一种答法" not in "".join(trees["OEBPS/review.xhtml"].itertext())
        for name, tree in trees.items():
            if not name.endswith(".xhtml"):
                continue
            assert tree.tag == "{%s}html" % XHTML
            assert len(tree.findall("{%s}body" % XHTML)) == 1, "Invalid XHTML body " + name
            assert not tree.xpath("//*[local-name()='script' or local-name()='form' or local-name()='button' or local-name()='noscript']"), "Interactive leftovers " + name
            assert not tree.xpath("//*[local-name()='dialog' or local-name()='select'] | //*[contains(concat(' ', normalize-space(@class), ' '), ' reader-tools ') or contains(concat(' ', normalize-space(@class), ' '), ' figure-open ') or contains(concat(' ', normalize-space(@class), ' '), ' model-practice-fold ')]"), "Reading interface leaked into book " + name
            ids = tree.xpath("//@id")
            assert len(ids) == len(set(ids)), "Duplicate XHTML IDs " + name
            for node in tree.xpath("//*[@href or @src]"):
                target = node.get("href") or node.get("src")
                parsed = urlsplit(target)
                if parsed.scheme or target.startswith("//"):
                    assert parsed.scheme in ["https", "http"], target
                    continue
                dest = posixpath.normpath(posixpath.join(posixpath.dirname(name), unquote(parsed.path))) if parsed.path else name
                assert dest in names, (name, target)
                if parsed.fragment:
                    assert dest in trees and trees[dest].xpath("//*[@id=$value]", value=unquote(parsed.fragment)), (name, target)
                links += 1
            if name.rsplit("/", 1)[-1] in {lesson["slug"] + ".xhtml" for lesson in course["lessons"]}:
                assert "纸上实验" in "".join(tree.itertext())
        for name in names:
            if name.endswith(".png"):
                assert archive.read(name).startswith(b"\x89PNG\r\n\x1a\n")
    for name, count in metadata["reviewPdfPages"].items():
        with fitz.open(OUT / name) as supplement:
            assert len(supplement) == count
            text = "".join(page.get_text() for page in supplement).replace("\n", "")
            for task in review["tasks"]:
                assert task["title"] in text, (name, task["id"])
            assert ("一种答法" in text) == (name == "llm-reading-guide.pdf"), "Answers mixed with student tasks"
            for page in supplement:
                assert abs(page.rect.width - 595.28) < 2 and abs(page.rect.height - 841.89) < 2, "Wrong A4 size"
                assert len(page.get_text().strip()) > 25, "Sparse review PDF page"
                for block in page.get_text("blocks"):
                    assert block[0] >= -1 and block[2] <= page.rect.width + 1 and block[1] >= -1 and block[3] <= page.rect.height + 1, (name, block)
    record = json.loads((ROOT / "exports/llm/review-record.json").read_text(encoding="utf-8"))
    assert record["courseVersion"] == course["version"] and record["taskVersion"] == review["version"]
    assert not record["participantCode"] and not record["sessionDate"] and record["stage"] is None
    assert record["coreIndependent"] is None and record["endedEarly"] is None
    assert len(record["tasks"]) == len(review["tasks"])
    for task in record["tasks"]:
        assert task["status"] is None and task["hints"] == [] and not task["firstAnswer"] and not task["readerWords"]
    assert all(value is None for value in record["objectives"].values()), "Invented test result in template"
    print(json.dumps({"status": "passed", "pdfPages": len(pdf), "pdfOutlineEntries": len(pdf.get_toc()), "pdfContentsPages": len(metadata["contentsPages"]), "pdfFormulaGroups": len(equation_pairs), "epubSectionLinks": subheadings, "epubLocalLinks": links, "sparsePdfPagesForReview": sparse, "epubcheck": "5.3.0: zero errors and warnings; result bound to this EPUB hash"}, ensure_ascii=False))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    check()
