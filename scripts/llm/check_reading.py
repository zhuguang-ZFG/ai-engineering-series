"""Exercise the offline reader's actual navigation, preferences and image dialog.

This checks browser behavior, not human comprehension or screen-reader speech.
"""

import json
import os
import shutil
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "tmp/reading-review"
SIZE_KEY = "llm-reading-size-v1"
POSITION_KEY = "llm-reading-position-v1"


def run():
    node = shutil.which("node")
    if node:
        os.environ.setdefault("PLAYWRIGHT_NODEJS_PATH", node)
    if os.name == "nt":
        flags = os.environ.get("NODE_OPTIONS", "")
        os.environ["NODE_OPTIONS"] = flags + " --preserve-symlinks --preserve-symlinks-main"
    OUTPUT.mkdir(parents=True, exist_ok=True)
    course = json.loads((ROOT / "book/llm/course.json").read_text(encoding="utf-8"))
    report = {"flows": [], "layouts": [], "network": [], "limitations": ["Browser interaction checks; no claim of real-reader or spoken assistive-technology acceptance."]}

    def url(slug):
        return (ROOT / "exports/llm" / (slug + ".html")).as_uri()

    def layout(page, label):
        dims = page.evaluate("""() => ({width: innerWidth, document: document.documentElement.scrollWidth,
          font: parseFloat(getComputedStyle(document.querySelector('.article-body')).fontSize)})""")
        assert dims["document"] <= dims["width"] + 1, (label, dims)
        report["layouts"].append({"label": label, **dims})

    def wait_dialog_closed(page, selector):
        # Native close() removes `open` before dispatching its queued close
        # event. Wait for the reader's focus/scroll cleanup too, otherwise the
        # next programmatic scroll can be overwritten by that pending handler.
        page.wait_for_function("""selector => {
          const dialog = document.querySelector(selector);
          return dialog && !dialog.open
            && !document.documentElement.classList.contains('reader-modal-open')
            && (selector !== '.reader-toc-dialog'
              || document.getElementById('reader-toc-trigger').getAttribute('aria-expanded') === 'false');
        }""", arg=selector)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel=os.environ.get("COURSE_BROWSER_CHANNEL", "chrome"), headless=True)
        context = browser.new_context(viewport={"width": 375, "height": 900}, reduced_motion="reduce")
        context.set_offline(True)
        page = context.new_page()
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("request", lambda request: report["network"].append(request.url) if request.url.startswith(("http://", "https://")) else None)
        page.goto(url("generation"))
        assert page.locator(".reader-tools").is_visible()
        assert not page.locator("details.course-menu").evaluate("el => el.open")
        assert not page.locator("details.section-menu").evaluate("el => el.open")
        assert page.locator("h1").bounding_box()["y"] < 500, "Mobile navigation pushes the lesson below the first screen"
        assert page.evaluate("scrollY") == 0
        assert not page.locator("#reader-resume").is_visible()
        assert not page.locator("#reader-toc-trigger").is_visible()
        report["flows"].append("Mobile opens at the lesson, with both navigation menus collapsed")

        page.locator("#reader-size").select_option("22")
        assert page.evaluate("getComputedStyle(document.querySelector('.article-body')).fontSize") == "22px"
        page.reload()
        assert page.locator("#reader-size").input_value() == "22"
        page.goto(url("training"))
        assert page.locator("#reader-size").input_value() == "22", "Size preference did not persist across local lesson files"
        report["flows"].append("Text size persists on reload and across local lesson files")

        anchor = page.locator(".article-body > p").nth(4)
        anchor.evaluate("el => window.scrollTo({top:scrollY + el.getBoundingClientRect().top - 120,behavior:'instant'})")
        previous_top = anchor.bounding_box()["y"]
        page.evaluate("""() => { const select = document.getElementById('reader-size'); select.value='20'; select.dispatchEvent(new Event('change', {bubbles:true})); }""")
        page.wait_for_function("getComputedStyle(document.querySelector('.article-body')).fontSize === '20px'")
        page.evaluate("() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")
        assert abs(anchor.bounding_box()["y"] - previous_top) < 4, "Changing size lost the visible paragraph"
        page.evaluate("""() => { const select = document.getElementById('reader-size'); select.value='22'; select.dispatchEvent(new Event('change', {bubbles:true})); }""")
        report["flows"].append("Changing text size keeps the currently visible paragraph at the same viewport position")

        for width in [320, 375, 768, 1440]:
            page.set_viewport_size({"width": width, "height": 900})
            for lesson in course["lessons"]:
                page.goto(url(lesson["slug"]))
                layout(page, f"{lesson['slug']}:{width}:22")
        report["flows"].append("Largest text fits all twelve lessons at 320, 375, 768 and 1440 pixels")

        page.set_viewport_size({"width": 375, "height": 900})
        page.goto(url("training"))
        # Follow an actual contents entry and check keyboard focus, not just URL.
        page.locator("details.section-menu > summary").click()
        target_link = page.locator('.lesson-toc a[href="#distillation"]')
        assert target_link.count() == 1
        target_link.focus()
        page.keyboard.press("Enter")
        page.wait_for_function("document.activeElement.id === 'distillation'")
        assert not page.locator("details.section-menu").evaluate("el => el.open")
        assert abs(page.locator("#distillation").bounding_box()["y"]) < 130
        page.wait_for_function("JSON.parse(localStorage.getItem('llm-reading-position-v1'))?.section === 'distillation'")
        record = page.evaluate("JSON.parse(localStorage.getItem('llm-reading-position-v1'))")
        page.goto(url("generation"))
        assert page.evaluate("scrollY") == 0, "Saved position must not force scrolling"
        resume = page.locator("#reader-resume")
        assert resume.is_visible()
        assert resume.get_attribute("href") == "training.html#distillation"
        assert page.evaluate("JSON.parse(localStorage.getItem('llm-reading-position-v1'))") == record, "Initial page load overwrote the saved position"
        resume.click()
        page.wait_for_function("document.activeElement.id === 'distillation'")
        report["flows"].append("Contents and opt-in resume move focus to the section without auto-jumping or overwriting progress on load")

        # Figure stays readable at its own zoom, and modal focus returns safely.
        page.goto(url("generation"))
        trigger = page.locator("a.figure-open").first
        trigger.focus()
        page.keyboard.press("Enter")
        dialog = page.locator(".reader-figure-dialog")
        assert dialog.is_visible()
        assert page.evaluate("document.activeElement.id") == "reader-figure-close"
        dimensions = page.locator(".reader-figure-canvas").evaluate("el => ({scroll:el.scrollWidth, width:el.clientWidth})")
        assert dimensions["scroll"] > dimensions["width"], dimensions
        page.locator("#reader-figure-zoom").click()
        dimensions = page.locator(".reader-figure-canvas").evaluate("el => ({scroll:el.scrollWidth, width:el.clientWidth})")
        assert dimensions["scroll"] <= dimensions["width"] + 1, dimensions
        page.keyboard.press("Escape")
        wait_dialog_closed(page, ".reader-figure-dialog")
        assert not dialog.is_visible()
        assert trigger.evaluate("el => document.activeElement === el")
        assert not page.evaluate("document.documentElement.classList.contains('reader-modal-open')")
        report["flows"].append("Image opens enlarged, can fit the window, closes with Escape and returns focus")

        # The choice is accepted only from a known schema and local page list.
        for invalid in ["not-json", json.dumps({**record, "version": "obsolete"}), json.dumps({**record, "slug": "javascript:alert(1)"}), json.dumps({**record, "slug": "../private.html"}), json.dumps({**record, "lessonTitle": "<script>bad</script>"})]:
            page.evaluate("([key,value]) => localStorage.setItem(key,value)", [POSITION_KEY, invalid])
            page.evaluate("scrollTo({top:0,behavior:'instant'})")
            page.reload()
            assert not page.locator("#reader-resume").is_visible()
            assert page.evaluate("scrollY") == 0
        page.evaluate("key => localStorage.setItem(key,'99')", SIZE_KEY)
        page.reload()
        assert page.locator("#reader-size").input_value() == "18"
        assert page.evaluate("getComputedStyle(document.querySelector('.article-body')).fontSize") == "18px"
        report["flows"].append("Malformed, obsolete and non-local stored records are ignored; invalid sizes fall back")

        page.screenshot(path=str(OUTPUT / "reading-mobile.png"), full_page=False)
        page.set_viewport_size({"width": 1440, "height": 1000})
        page.goto(url("training"))
        assert page.locator("details.section-menu").evaluate("el => el.open")
        assert not page.locator("details.course-menu").evaluate("el => el.open")
        page.locator('.lesson-toc a[href="#distillation"]').click()
        page.wait_for_function("document.activeElement.id === 'distillation'")
        assert page.locator("details.section-menu").evaluate("el => el.open"), "Desktop contents should remain open after following a section"
        assert page.locator("#reader-size").bounding_box()["height"] >= 44
        report["flows"].append("Desktop contents remain open after section navigation and text controls retain a 44px target")
        page.wait_for_function("document.querySelector('.lesson-toc a[aria-current=location]')?.getAttribute('href') === '#distillation'")
        assert page.locator('.lesson-toc a[aria-current="location"]').count() == 1
        heading = page.locator(".article-body h3[id]").last
        heading_id = heading.get_attribute("id")
        heading.evaluate("el => window.scrollTo({top:scrollY + el.getBoundingClientRect().top - 80,behavior:'instant'})")
        page.wait_for_function("id => document.querySelector('.lesson-toc a[aria-current=location]')?.hash === '#' + id", arg=heading_id)
        assert not page.locator("#reader-toc-trigger").is_visible()
        report["flows"].append("Desktop contents quietly track the actual section in view, including ordinary scrolling")
        page.goto(url("training"))
        page.screenshot(path=str(OUTPUT / "reading-desktop.png"), full_page=False)

        for width in [320, 375]:
            page.set_viewport_size({"width": width, "height": 568})
            page.goto(url("training"))
            assert not page.locator("#reader-toc-trigger").is_visible()
            page.locator("#distillation").evaluate("el => window.scrollTo({top:scrollY + el.getBoundingClientRect().top - 80,behavior:'instant'})")
            shortcut = page.locator("#reader-toc-trigger")
            page.wait_for_function("!document.getElementById('reader-toc-trigger').hidden")
            position = page.evaluate("scrollY")
            shortcut.click()
            toc_dialog = page.locator(".reader-toc-dialog")
            assert toc_dialog.is_visible()
            assert page.locator("dialog[open]").count() == 1
            current = toc_dialog.locator('[aria-current="location"]')
            assert current.count() == 1 and current.get_attribute("href") == "#distillation"
            box = current.bounding_box()
            assert box["y"] >= 0 and box["y"] + box["height"] <= 568
            assert current.evaluate("el => document.activeElement === el")
            assert not shortcut.is_visible()
            assert page.evaluate("document.documentElement.scrollWidth") <= width + 1
            # Inert page controls cannot open a competing image modal, including
            # an attempted synthetic click from another page integration.
            page.locator("a.figure-open").first.evaluate("el => el.click()")
            assert page.locator("dialog[open]").count() == 1 and toc_dialog.is_visible()
            page.keyboard.press("Escape")
            wait_dialog_closed(page, ".reader-toc-dialog")
            assert not toc_dialog.is_visible()
            page.wait_for_function("document.activeElement.id === 'reader-toc-trigger'")
            assert abs(page.evaluate("scrollY") - position) < 2
            shortcut.click()
            toc_dialog.locator("#reader-toc-close").click()
            wait_dialog_closed(page, ".reader-toc-dialog")
            page.wait_for_function("document.activeElement.id === 'reader-toc-trigger'")
            assert abs(page.evaluate("scrollY") - position) < 2
            shortcut.click()
            later = toc_dialog.locator("a").last
            target_id = later.get_attribute("href")[1:]
            later.click()
            wait_dialog_closed(page, ".reader-toc-dialog")
            page.wait_for_function("id => document.activeElement.id === id", arg=target_id)
            assert not toc_dialog.is_visible()
            assert page.locator("dialog[open]").count() == 0
            assert abs(page.locator(f'[id="{target_id}"]').bounding_box()["y"]) < 130
            page.wait_for_function("id => document.querySelector('.lesson-toc a[aria-current=location]')?.hash === '#' + id", arg=target_id)

            # The existing dialog must refresh after reading another section;
            # cloning the initial current marker once is not sufficient.
            other_heading = page.locator(".article-body h3[id]").last
            other_id = other_heading.get_attribute("id")
            other_heading.evaluate("el => window.scrollTo({top:scrollY + el.getBoundingClientRect().top - 80,behavior:'instant'})")
            page.wait_for_function("!document.getElementById('reader-toc-trigger').hidden")
            shortcut.click()
            current = toc_dialog.locator('[aria-current="location"]')
            assert current.count() == 1 and current.get_attribute("href") == f"#{other_id}"
            assert current.evaluate("el => document.activeElement === el")
            box = current.bounding_box()
            assert box["y"] >= 0 and box["y"] + box["height"] <= 568
            page.keyboard.press("Escape")
            wait_dialog_closed(page, ".reader-toc-dialog")
            assert shortcut.evaluate("el => document.activeElement === el")

            # Resizing an open mobile dialog must leave a usable way back to
            # the same section, even though its original shortcut is hidden.
            page.locator("#distillation").evaluate("el => window.scrollTo({top:scrollY + el.getBoundingClientRect().top - 80,behavior:'instant'})")
            shortcut.click()
            assert toc_dialog.locator('[aria-current="location"]').get_attribute("href") == "#distillation"
            page.set_viewport_size({"width": 1440, "height": 900})
            assert toc_dialog.is_visible()
            toc_dialog.locator("#reader-toc-close").click()
            wait_dialog_closed(page, ".reader-toc-dialog")
            page.wait_for_function("document.activeElement.id === 'distillation'")
            assert not shortcut.is_visible()
            assert not page.locator("html").evaluate("el => el.classList.contains('reader-modal-open')")
            assert 0 <= page.locator("#distillation").bounding_box()["y"] <= 225
            page.set_viewport_size({"width": width, "height": 568})

            # A full-width calculation control close to the viewport edge must
            # remain uncovered; the shortcut moves aside or hides temporarily.
            control = page.locator("#train-run")
            control.evaluate("el => window.scrollTo({top:scrollY + el.getBoundingClientRect().top - innerHeight + 66,behavior:'instant'})")
            page.evaluate("() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")
            if shortcut.is_visible():
                button_box, control_box = shortcut.bounding_box(), control.bounding_box()
                assert not (button_box["x"] < control_box["x"] + control_box["width"] and button_box["x"] + button_box["width"] > control_box["x"] and button_box["y"] < control_box["y"] + control_box["height"] and button_box["y"] + button_box["height"] > control_box["y"])

            # Placement must not hide a keyboard-focused shortcut. It can
            # resume avoiding controls once the user moves focus elsewhere.
            page.locator("#distillation").evaluate("el => window.scrollTo({top:scrollY + el.getBoundingClientRect().top - 80,behavior:'instant'})")
            page.wait_for_function("!document.getElementById('reader-toc-trigger').hidden")
            shortcut.focus()
            focused_x = shortcut.bounding_box()["x"]
            control.evaluate("el => window.scrollTo({top:scrollY + el.getBoundingClientRect().top - innerHeight + 66,behavior:'instant'})")
            page.evaluate("() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")
            assert shortcut.is_visible() and shortcut.evaluate("el => document.activeElement === el")
            assert shortcut.bounding_box()["x"] == focused_x
            page.keyboard.press("Enter")
            assert toc_dialog.is_visible()
            page.keyboard.press("Escape")
            wait_dialog_closed(page, ".reader-toc-dialog")
            page.wait_for_function("document.activeElement.id === 'reader-toc-trigger'")
            assert shortcut.is_visible() and shortcut.evaluate("el => document.activeElement === el")
            control.focus()
            page.evaluate("() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")
            assert control.evaluate("el => document.activeElement === el")
            if shortcut.is_visible():
                button_box, control_box = shortcut.bounding_box(), control.bounding_box()
                assert not (button_box["x"] < control_box["x"] + control_box["width"] and button_box["x"] + button_box["width"] > control_box["x"] and button_box["y"] < control_box["y"] + control_box["height"] and button_box["y"] + button_box["height"] > control_box["y"])

            figure_link = page.locator("a.figure-open").first
            figure_number = figure_link.locator("xpath=ancestor::figure").locator(".figure-number").inner_text()
            figure_link.click()
            image_dialog = page.locator(".reader-figure-dialog")
            assert image_dialog.is_visible()
            assert page.locator("dialog[open]").count() == 1
            assert figure_number in image_dialog.locator("#reader-figure-caption").inner_text()
            assert "看大图" not in image_dialog.locator("#reader-figure-caption").inner_text()
            assert image_dialog.get_attribute("aria-describedby") == "reader-figure-caption reader-figure-hint"
            shortcut.evaluate("el => el.click()")
            assert page.locator("dialog[open]").count() == 1 and image_dialog.is_visible()
            close_box = image_dialog.locator("#reader-figure-close").bounding_box()
            assert 0 <= close_box["y"] and close_box["y"] + close_box["height"] <= 568
            assert image_dialog.locator(".reader-figure-canvas").bounding_box()["height"] >= 80
            page.screenshot(path=str(OUTPUT / f"figure-dialog-{width}.png"))
            page.keyboard.press("Escape")
            wait_dialog_closed(page, ".reader-figure-dialog")
            assert figure_link.evaluate("el => document.activeElement === el")
            page.locator("#distillation").evaluate("el => window.scrollTo({top:scrollY + el.getBoundingClientRect().top - 80,behavior:'instant'})")
            page.wait_for_function("!document.getElementById('reader-toc-trigger').hidden")
            shortcut.click()
            page.screenshot(path=str(OUTPUT / f"contents-dialog-{width}.png"))
            page.keyboard.press("Escape")
            wait_dialog_closed(page, ".reader-toc-dialog")
            report["layouts"].append({"label": f"reader-dialogs:{width}:568"})
        report["flows"].append("Mobile contents at 320/375 × 568 preserve position on cancel, focus selected headings, show the current section and avoid controls")
        report["flows"].append("Contents and figure dialogs stay mutually exclusive; large figures retain original caption and accessible explanation")
        report["flows"].append("Reopened contents refresh the current section; resizing an open mobile dialog returns to the same desktop section")
        report["flows"].append("A focused mobile shortcut remains operable while scrolling; control avoidance resumes after focus moves")
        assert not errors, errors
        context.close()

        blocked = browser.new_context(viewport={"width": 375, "height": 900}, reduced_motion="reduce")
        blocked.set_offline(True)
        blocked.add_init_script("Object.defineProperty(window, 'localStorage', {get(){throw new DOMException('Unavailable','SecurityError')}})")
        page = blocked.new_page()
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(url("generation"))
        page.locator("#reader-size").select_option("20")
        assert page.evaluate("getComputedStyle(document.querySelector('.article-body')).fontSize") == "20px"
        page.locator("a.figure-open").first.click()
        assert page.locator(".reader-figure-dialog").is_visible()
        page.keyboard.press("Escape")
        wait_dialog_closed(page, ".reader-figure-dialog")
        assert not errors, errors
        blocked.close()
        report["flows"].append("Storage-denied browsers retain text controls, navigation and image viewing")

        static = browser.new_context(java_script_enabled=False, viewport={"width": 375, "height": 900})
        static.set_offline(True)
        page = static.new_page()
        page.goto(url("generation"))
        assert not page.locator(".reader-tools").is_visible()
        assert page.locator("#reader-toc-trigger").count() == 0
        page.locator("details.section-menu > summary").click()
        assert page.locator(".lesson-toc a").first.is_visible()
        first_link = page.locator("a.figure-open").first
        expected = first_link.get_attribute("href")
        assert expected.endswith(".svg")
        first_link.click()
        assert page.url.endswith(".svg")
        static.close()
        report["flows"].append("Without JavaScript, contents expand and image links still open the original SVG")
        browser.close()
    assert not report["network"], report["network"]
    (OUTPUT / "reading-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "passed", "flows": len(report["flows"]), "layouts": len(report["layouts"]), "offlineRequests": len(report["network"])}))


if __name__ == "__main__":
    run()
