"""Check actual Chrome accessibility trees and keyboard flows after build:llm.

This verifies exposed browser semantics, not screen-reader speech or a full WCAG
audit. No network requests are allowed. Evidence stays in tmp/llm-review/.
"""

import json
import os
import shutil
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "tmp/llm-review"
NAMED_ROLES = {
    "button", "checkbox", "combobox", "DisclosureTriangle", "image", "link",
    "radio", "slider", "spinbutton", "textbox",
}


def run():
    node = shutil.which("node")
    if node:
        os.environ.setdefault("PLAYWRIGHT_NODEJS_PATH", node)
    if os.name == "nt":
        current = os.environ.get("NODE_OPTIONS", "")
        flags = [flag for flag in ["--preserve-symlinks", "--preserve-symlinks-main"] if flag not in current.split()]
        os.environ["NODE_OPTIONS"] = " ".join([current, *flags]).strip()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    report = {
        "pages": [], "flows": [],
        "limitations": ["Chrome CDP accessibility trees and keyboard interactions; real screen-reader speech remains untested."],
    }
    network = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel=os.environ.get("COURSE_BROWSER_CHANNEL", "chrome"), headless=True)
        context = browser.new_context(viewport={"width": 375, "height": 900}, reduced_motion="reduce")
        context.set_offline(True)
        page = context.new_page()
        page.on("request", lambda request: network.append(request.url) if request.url.startswith(("http://", "https://")) else None)
        cdp = context.new_cdp_session(page)
        cdp.send("Accessibility.enable")

        def visit(slug):
            page.goto((ROOT / "exports/llm" / f"{slug}.html").as_uri())

        def tree():
            return [node for node in cdp.send("Accessibility.getFullAXTree")["nodes"] if not node.get("ignored")]

        for path in sorted((ROOT / "exports/llm").glob("*.html")):
            page.goto(path.as_uri())
            nodes = tree()
            named = [node for node in nodes if node.get("role", {}).get("value") in NAMED_ROLES]
            assert all(node.get("name", {}).get("value", "").strip() for node in named), path.name
            assert sum(node.get("role", {}).get("value") == "main" for node in nodes) == 1, path.name
            for node in nodes:
                properties = {entry["name"]: entry["value"].get("value") for entry in node.get("properties", [])}
                if node.get("role", {}).get("value") == "status":
                    assert properties.get("live") == "polite", (path.name, node)
                if node.get("role", {}).get("value") == "DisclosureTriangle":
                    assert isinstance(properties.get("expanded"), bool), (path.name, node)
            semantics = page.evaluate("""() => {
              const ids = [...document.querySelectorAll('[id]')].map(el => el.id);
              const attributes = ['aria-labelledby', 'aria-describedby', 'aria-controls'];
              return {
                duplicates: ids.filter((id, index) => ids.indexOf(id) !== index),
                brokenReferences: [...document.querySelectorAll('*')].flatMap(el => attributes.flatMap(attribute =>
                  (el.getAttribute(attribute) || '').split(/\\s+/).filter(id => id && !document.getElementById(id)))),
                unnamedImages: [...document.images].filter(image => !image.getAttribute('alt')?.trim()).length,
                positiveTabindex: [...document.querySelectorAll('[tabindex]')].filter(el => el.tabIndex > 0).length,
                language: document.documentElement.lang,
                headings: document.querySelectorAll('h1').length
              };
            }""")
            assert semantics == {"duplicates": [], "brokenReferences": [], "unnamedImages": 0, "positiveTabindex": 0, "language": "zh-CN", "headings": 1}, (path.name, semantics)
            page.locator(".skip").focus()
            page.keyboard.press("Enter")
            assert page.evaluate("document.activeElement.id") == "main", (path.name, "skip link did not move focus")
            report["pages"].append({"page": path.name, "namedAccessibleNodes": len(named)})

        visit("training")
        page.evaluate("""() => {
          window.liveMutations = [];
          for (const id of ['training-status', 'learning-rate-value']) {
            new MutationObserver(() => window.liveMutations.push(id)).observe(document.getElementById(id), {childList:true, characterData:true, subtree:true});
          }
        }""")
        page.locator("#train-run").focus()
        page.keyboard.press("Enter")
        assert page.evaluate("document.activeElement.id") == "train-pause"
        page.wait_for_function("parseInt(document.querySelector('#training-metrics dd').textContent) >= 20")
        mutations = page.evaluate("window.liveMutations")
        assert mutations.count("training-status") == 1 and "learning-rate-value" not in mutations, mutations
        page.keyboard.press("Enter")
        assert page.evaluate("document.activeElement.id") == "train-run"
        assert "已暂停" in page.locator("#training-status").inner_text()
        paused = page.locator("#training-metrics").inner_text()
        page.wait_for_timeout(100)
        assert page.locator("#training-metrics").inner_text() == paused
        page.keyboard.press("Enter")
        page.wait_for_function("document.querySelector('#training-metrics dd').textContent === '500 / 500'")
        assert page.evaluate("document.activeElement.id") == "train-reset"
        page.keyboard.press("Enter")
        assert page.locator("#training-metrics dd").first.inner_text() == "0 / 500"
        report["flows"].append("Training start/pause/cap/reset preserves useful keyboard focus and avoids per-frame live-region announcements")

        page.locator("#distill-step").focus()
        page.keyboard.press("Enter")
        assert "已更新学生 1 步" in page.locator("#distill-status").inner_text()
        assert page.evaluate("document.activeElement.id") == "distill-step"
        page.locator("#distill-temperature").focus()
        page.keyboard.press("ArrowRight")
        assert page.locator("#distill-temperature").input_value() == "2.5"
        assert "重置" in page.locator("#distill-status").inner_text()
        assert any(node.get("role", {}).get("value") == "rowheader" and node.get("name", {}).get("value") == "水" for node in tree())
        report["flows"].append("Distillation controls expose names, keyboard values, row headers and concise live status")

        visit("tools")
        page.locator("#tool-request").fill("{")
        page.locator("#load-tool").focus()
        page.keyboard.press("Enter")
        assert page.evaluate("document.activeElement.id") == "tool-request"
        assert page.locator("#tool-request").get_attribute("aria-invalid") == "true"
        request_node = next(node for node in tree() if node.get("role", {}).get("value") == "textbox")
        assert "JSON 格式无效" in request_node.get("description", {}).get("value", ""), request_node
        assert any(prop["name"] == "invalid" and prop["value"]["value"] == "true" for prop in request_node["properties"])
        page.locator("#tool-request").fill('{"tool":"multiply","args":{"a":12.5,"b":8}}')
        assert page.locator("#tool-request").get_attribute("aria-invalid") is None
        page.locator("#reset-tool").focus()
        page.keyboard.press("Enter")
        assert page.locator("#tool-request").get_attribute("aria-invalid") is None
        report["flows"].append("Invalid tool JSON exposes aria-invalid, related error text and focus for correction; editing clears stale invalid state")

        visit("retrieval")
        source_link = page.locator('#retrieval-hits a[href^="#source-"]').first
        target = source_link.get_attribute("href")[1:]
        source_link.focus()
        page.keyboard.press("Enter")
        assert page.locator(f"#{target}").evaluate("el => el.closest('details').open")
        assert page.evaluate("document.activeElement.id") == target
        report["flows"].append("Keyboard evidence link expands its source and focuses the referenced material")
        assert not network, network
        browser.close()
    report["status"] = "passed"
    report["offlineRequests"] = len(network)
    (OUTPUT / "accessibility-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "passed", "pages": len(report["pages"]), "keyboardFlows": len(report["flows"]), "offlineRequests": len(network)}))


if __name__ == "__main__":
    run()
