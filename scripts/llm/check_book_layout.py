"""Render extracted EPUB XHTML locally; this is not a dedicated e-reader test."""

import json
import os
import shutil
from pathlib import Path

from playwright.sync_api import sync_playwright

from export_books import ROOT, REVIEW


def run():
    node = shutil.which("node")
    if node:
        os.environ.setdefault("PLAYWRIGHT_NODEJS_PATH", node)
    if os.name == "nt":
        os.environ["NODE_OPTIONS"] = os.environ.get("NODE_OPTIONS", "") + " --preserve-symlinks --preserve-symlinks-main"
    course = json.loads((ROOT / "book/llm/course.json").read_text(encoding="utf-8"))
    chapters = [item["slug"] for item in course["lessons"]]
    results = []
    network = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel=os.environ.get("COURSE_BROWSER_CHANNEL", "chrome"), headless=True)
        context = browser.new_context(viewport={"width": 375, "height": 900}, java_script_enabled=True)
        context.set_offline(True)
        page = context.new_page()
        page.on("request", lambda request: network.append(request.url) if request.url.startswith(("http://", "https://")) else None)
        for width, size in [(375, 16), (375, 24), (320, 24), (768, 16)]:
            page.set_viewport_size({"width": width, "height": 900})
            for name in ["cover", "intro", "nav", *chapters, "advanced", "architecture", "applications", "execution", "practice", "review"]:
                page.goto((REVIEW / "epub/OEBPS" / (name + ".xhtml")).as_uri())
                page.evaluate("size => { document.documentElement.style.fontSize = size + 'px'; }", size)
                result = page.evaluate("""() => ({
                  width: document.documentElement.scrollWidth,
                  images: [...document.images].every(i => i.complete && i.naturalWidth > 0),
                  scripts: document.scripts.length
                })""")
                assert result["width"] <= width + 1, (name, width, size, result)
                assert result["images"] and result["scripts"] == 0, (name, result)
                results.append(f"{name}:{width}:{size}")
                if width == 375 and size == 16 and name in ["cover", "retrieval", "tools", "project", "architecture", "applications", "execution", "review"]:
                    page.screenshot(path=str(REVIEW / f"epub-{name}-375.png"), full_page=True)
        page.set_viewport_size({"width": 375, "height": 900})
        page.goto((REVIEW / "epub/OEBPS/nav.xhtml").as_uri())
        distillation = page.locator('a[href="training.xhtml#distillation"]')
        assert distillation.count() == 1, "EPUB section index must include distillation"
        distillation.click()
        assert page.url.endswith("training.xhtml#distillation")
        assert page.locator("#distillation").is_visible()
        assert page.locator("#distillation").bounding_box()["y"] < 100, "EPUB link did not land at its section"
        page.locator('.book-navigation a[href="nav.xhtml#toc"]').click()
        assert page.url.endswith("nav.xhtml#toc")
        page.goto((REVIEW / "epub/OEBPS/intro.xhtml").as_uri())
        page.locator('a[href="generation.xhtml#L02"]').click()
        assert page.url.endswith("generation.xhtml#L02")
        page.locator('.book-navigation a[href="vectors.xhtml#L03"]').click()
        assert page.url.endswith("vectors.xhtml#L03")
        assert not network, network
        browser.close()
    report = {"status": "passed", "layouts": len(results), "checks": results, "navigation": ["section index to distillation", "chapter to contents", "quick route to generation", "next chapter"], "limitation": "Extracted EPUB XHTML checked in Chrome, including 150% root font size at 320px; dedicated e-reader compatibility remains untested."}
    (REVIEW / "epub-layout-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "passed", "epubXhtmlLayouts": len(results), "navigationFlows": 4, "offlineRequests": len(network)}))


if __name__ == "__main__":
    run()
