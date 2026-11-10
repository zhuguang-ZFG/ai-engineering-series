"""Exercise the offline mechanism stories, including their static reading form.

These are browser checks, not evidence of comprehension or spoken screen-reader
acceptance. The actual story calculations also have independent Node tests.
"""

import json
import math
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "tmp/mechanism-review"
STORIES = [("generation", "generation"), ("attention", "attention"), ("training", "distillation")]


def expected_numbers(kind):
    """Recompute teaching numbers independently of the JavaScript renderer."""
    fixture = json.loads((ROOT / "book/llm/fixtures" / (kind + ".json")).read_text(encoding="utf-8"))

    def softmax(values, temperature=1):
        shifted = [math.exp((value - max(values)) / temperature) for value in values]
        return [value / sum(shifted) for value in shifted]

    def percent(value):
        return f"{100 * value:.2f}%"

    def vector(values):
        return "[" + ", ".join(f"{value:.4f}" for value in values) + "]"

    if kind == "generation":
        candidates = fixture["states"][fixture["prompt"]]
        distribution = softmax([item["logit"] for item in candidates])
        sample = ((1664525 * 42 + 1013904223) % 2 ** 32) / 2 ** 32
        selected = next(index for index in range(len(distribution)) if sample < sum(distribution[:index + 1]))
        new_text = fixture["prompt"] + candidates[selected]["piece"]
        following = softmax([item["logit"] for item in fixture["states"][new_text]])
        return {0: [percent(value) for value in distribution], 2: [new_text], 3: [percent(value) for value in following]}
    if kind == "attention":
        position = fixture["initialPosition"]
        scores = [sum(q * k for q, k in zip(fixture["Q"][position], key)) / math.sqrt(len(key)) for key in fixture["K"][:position + 1]]
        weights = softmax(scores)
        output = [sum(weight * value[column] for weight, value in zip(weights, fixture["V"])) for column in range(len(fixture["V"][0]))]
        return {1: [f"{value:.4f}" for value in scores], 2: [percent(value) for value in weights], 3: [vector(output)]}
    temperature, alpha, target = fixture["temperature"], fixture["alpha"], fixture["target"]
    teacher = softmax(fixture["teacher"], temperature)
    student = softmax(fixture["student"], temperature)
    inference = softmax(fixture["student"])
    gradient = [alpha * temperature * (q - p) + (1 - alpha) * (hard - int(index == target)) for index, (p, q, hard) in enumerate(zip(teacher, student, inference))]
    updated = [old - fixture["learningRate"] * grad for old, grad in zip(fixture["student"], gradient)]

    def loss(logits):
        soft = softmax(logits, temperature)
        kl = sum(p * math.log(p / q) for p, q in zip(teacher, soft))
        return alpha * temperature ** 2 * kl - (1 - alpha) * math.log(softmax(logits)[target])

    return {0: [percent(value) for value in teacher], 1: [vector(gradient)], 2: [vector(updated)], 3: [f"{loss(fixture['student']):.4f}", f"{loss(updated):.4f}", *[percent(value) for value in teacher], *[percent(value) for value in softmax(updated, temperature)]]}


def run():
    node = shutil.which("node")
    if node:
        os.environ.setdefault("PLAYWRIGHT_NODEJS_PATH", node)
    if os.name == "nt":
        os.environ["NODE_OPTIONS"] = os.environ.get("NODE_OPTIONS", "") + " --preserve-symlinks --preserve-symlinks-main"
    OUTPUT.mkdir(parents=True, exist_ok=True)
    report = {"flows": [], "layouts": [], "network": [], "limitations": ["No real-reader or spoken assistive-technology acceptance is inferred from these checks.", "The headless visibility check injects visibilitychange with document.hidden=true; it does not simulate minimizing a real browser window."]}
    errors = []

    def url(slug):
        return (ROOT / "exports/llm" / (slug + ".html")).as_uri()

    def attach(page):
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("request", lambda request: report["network"].append(request.url) if request.url.startswith(("http://", "https://")) else None)

    def state(story, step, playing=False):
        assert story.get_attribute("data-step") == str(step), story.get_attribute("data-step")
        assert story.get_attribute("data-playing") == str(playing).lower()
        assert story.locator(".mechanism-frame:not([hidden])").count() == 1
        assert story.locator(".mechanism-frame:not([hidden])").get_attribute("data-frame") == str(step)

    def action(story, name):
        return story.locator(f'button[data-action="{name}"]')

    def layout(page, label):
        metrics = page.evaluate("""() => ({width:innerWidth, document:document.documentElement.scrollWidth,
          font:getComputedStyle(document.querySelector('.article-body')).fontSize,
          buttons:[...document.querySelectorAll('.mechanism-controls button')].map(button => ({
            width:button.getBoundingClientRect().width, height:button.getBoundingClientRect().height
          }))})""")
        assert metrics["document"] <= metrics["width"] + 1, (label, metrics)
        for button in metrics["buttons"]:
            assert button["height"] >= 44 and button["width"] >= 44, (label, button)
        report["layouts"].append({"label": label, **metrics})

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel=os.environ.get("COURSE_BROWSER_CHANNEL", "chrome"), headless=True)
        context = browser.new_context(viewport={"width": 768, "height": 1000}, reduced_motion="no-preference")
        context.set_offline(True)
        page = context.new_page()
        attach(page)
        page.clock.install(time=datetime(2026, 11, 7, tzinfo=timezone.utc))
        page.clock.pause_at(datetime(2026, 11, 7, 0, 0, 1, tzinfo=timezone.utc))

        for slug, kind in STORIES:
            page.goto(url(slug))
            story = page.locator(f'[data-mechanism="{kind}"]')
            assert story.get_attribute("data-enhanced") == "true"
            assert story.locator(".mechanism-frame").count() == 4
            for index, values in expected_numbers(kind).items():
                frame_text = story.locator(f'.mechanism-frame[data-frame="{index}"]').text_content()
                for value in values:
                    assert value in frame_text, (kind, index, value, frame_text)
            assert story.locator(".mechanism-controls").is_visible()
            assert not story.locator(".mechanism-static").is_visible()
            state(story, 0)
            page.clock.run_for(18000)
            state(story, 0)

            action(story, "next").focus()
            page.keyboard.press("Enter")
            state(story, 1)
            assert action(story, "next").evaluate("el => el === document.activeElement")
            assert "2 / 4" in story.locator(".mechanism-status").inner_text()
            action(story, "previous").focus()
            page.keyboard.press("Space")
            state(story, 0)

            action(story, "play").click()
            state(story, 0, True)
            assert story.locator(".mechanism-status").get_attribute("aria-live") == "off"
            page.clock.run_for(5300)
            state(story, 1, True)
            action(story, "play").click()
            page.clock.run_for(20)
            state(story, 1)
            page.clock.run_for(12000)
            state(story, 1)

            action(story, "reset").click()
            state(story, 0)
            action(story, "play").click()
            page.clock.run_for(16000)
            state(story, 3)
            assert "已结束" in story.locator(".mechanism-status").inner_text()
            assert story.locator(".mechanism-status").get_attribute("aria-live") == "polite"
            assert action(story, "play").evaluate("el => el === document.activeElement")
            page.clock.run_for(18000)
            state(story, 3)

            action(story, "play").click()
            state(story, 0, True)
            action(story, "next").click()
            state(story, 1)
            page.clock.run_for(16000)
            state(story, 1)
            # Rapid toggles must not leave a second playback timer alive.
            action(story, "play").evaluate("el => { for(let i=0;i<10;i++) el.click(); }")
            page.clock.run_for(16000)
            state(story, 1)

            action(story, "all").click()
            assert story.get_attribute("data-mode") == "all"
            assert story.locator(".mechanism-static").is_visible()
            assert not story.locator(".mechanism-stage").is_visible()
            assert action(story, "all").get_attribute("aria-expanded") == "true"
            action(story, "all").click()
            state(story, 1)
            assert action(story, "all").evaluate("el => el === document.activeElement")

            action(story, "reset").click()
            action(story, "play").click()
            page.emulate_media(reduced_motion="reduce")
            expect(action(story, "play")).to_have_attribute("aria-disabled", "true")
            page.clock.run_for(100)
            state(story, 0)
            assert action(story, "play").get_attribute("aria-disabled") == "true"
            action(story, "play").focus()
            page.keyboard.press("Enter")
            page.clock.run_for(16000)
            state(story, 0)
            action(story, "next").click()
            state(story, 1)
            animations = story.locator(".mechanism-frame:not([hidden]) svg").evaluate("el => [el,...el.querySelectorAll('*')].map(node => getComputedStyle(node).animationName)")
            assert all(animation == "none" for animation in animations)
            page.emulate_media(reduced_motion="no-preference")
            expect(action(story, "play")).to_have_attribute("aria-disabled", "false")
            page.clock.run_for(100)
            state(story, 1)

            action(story, "play").click()
            page.evaluate("window.scrollTo({top:0,behavior:'instant'})")
            expect(story).to_have_attribute("data-playing", "false")
            page.clock.run_for(100)
            state(story, 1)
            page.clock.run_for(16000)
            state(story, 1)
            # Chromium's visibility is host controlled in headless mode. Inject
            # only that browser event; the same real event handler must cancel.
            action(story, "play").click()
            page.evaluate("""() => {
              Object.defineProperty(document, 'hidden', {configurable:true, get:() => true});
              document.dispatchEvent(new Event('visibilitychange'));
              delete document.hidden;
            }""")
            page.clock.run_for(16000)
            state(story, 1)
            action(story, "reset").click()

            page.emulate_media(media="print")
            assert story.locator(".mechanism-static").is_visible()
            assert not story.locator(".mechanism-stage").is_visible()
            assert not story.locator(".mechanism-controls").is_visible()
            page.emulate_media(media="screen", reduced_motion="reduce")
            expect(action(story, "play")).to_have_attribute("aria-disabled", "true")
            page.clock.run_for(100)
            for width in [320, 375, 768, 1440]:
                page.set_viewport_size({"width": width, "height": 1000})
                page.locator("#reader-size").select_option("22")
                action(story, "reset").click()
                for frame in range(4):
                    if frame:
                        action(story, "next").click()
                    layout(page, f"{kind}:{width}:22:step-{frame + 1}")
                action(story, "all").click()
                layout(page, f"{kind}:{width}:22:all")
                action(story, "all").click()
            page.set_viewport_size({"width": 375, "height": 1000})
            action(story, "reset").click()
            action(story, "next").click()
            story.locator(".mechanism-stage").screenshot(path=str(OUTPUT / f"{kind}-mobile-step-2.png"))
            if kind == "distillation":
                action(story, "next").click()
                action(story, "next").click()
                story.locator(".mechanism-stage").screenshot(path=str(OUTPUT / "distillation-mobile-step-4.png"))
            page.emulate_media(reduced_motion="no-preference")
            expect(action(story, "play")).to_have_attribute("aria-disabled", "false")
            page.clock.run_for(100)
            report["flows"].append({"story": kind, "checks": ["independently calculated fixture numbers", "no autoplay", "keyboard and retained focus", "manual steps", "play/pause/reset", "finite replay", "rapid toggles", "complete story", "live motion preference", "offscreen pause", "visibility event pause", "print static"]})

        static_context = browser.new_context(java_script_enabled=False, viewport={"width": 320, "height": 900})
        static_context.set_offline(True)
        static_page = static_context.new_page()
        attach(static_page)
        for slug, kind in STORIES:
            static_page.goto(url(slug))
            story = static_page.locator(f'[data-mechanism="{kind}"]')
            assert story.locator(".mechanism-static").is_visible()
            assert story.locator(".mechanism-static ol > li").count() == 4
            assert not story.locator(".mechanism-stage").is_visible()
            assert not story.locator(".mechanism-controls").is_visible()
            image = story.locator(".mechanism-static img")
            assert image.get_attribute("alt")
            assert image.evaluate("el => el.complete && el.naturalWidth > 0")
            assert static_page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
            report["flows"].append({"story": kind, "checks": ["no-script full static story", "offline local illustration"]})
        assert not errors, errors
        assert not report["network"], report["network"]
        browser.close()

    (OUTPUT / "results.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"flows": len(report["flows"]), "layouts": len(report["layouts"]), "remoteRequests": len(report["network"]), "output": "tmp/mechanism-review/results.json"}, ensure_ascii=False))


if __name__ == "__main__":
    run()
