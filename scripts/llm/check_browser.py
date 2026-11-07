"""Check the offline learning pages in Chrome. Requires Python Playwright.

Run after npm run build:llm: python scripts/llm/check_browser.py
Screenshots and the JSON report are local review artifacts under tmp/llm-review/.
"""

import json
import os
import shutil
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "tmp" / "llm-review"
COURSE = json.loads((ROOT / "book" / "llm" / "course.json").read_text(encoding="utf-8"))
PAGES = ["index", *[lesson["slug"] for lesson in COURSE["lessons"] if lesson["status"] == "ready"]]


def page_url(name):
    return (ROOT / "exports" / "llm" / f"{name}.html").as_uri()


def assert_layout(page, width):
    # Reading pages keep below-fold figures lazy in the browser. Trigger them
    # before checking the actual loaded images, rather than treating deferred
    # loading as a missing resource or weakening the image check.
    page.evaluate("[...document.images].forEach(image => image.loading = 'eager')")
    page.wait_for_function("[...document.images].every(image => image.complete)")
    dimensions = page.evaluate("""() => ({
      viewport: innerWidth,
      document: document.documentElement.scrollWidth,
      images: [...document.images].every(image => image.complete && image.naturalWidth > 0),
      interactiveText: [...document.querySelectorAll('.lab button, .lab select')]
        .filter(el => el.offsetWidth).map(el => parseFloat(getComputedStyle(el).fontSize))
    })""")
    assert dimensions["document"] <= width + 1, dimensions
    assert dimensions["images"], "An illustration failed to load"
    assert all(size >= 16 for size in dimensions["interactiveText"]), dimensions


def run():
    # Prefer the host Node executable when available. Preserve symlink paths on
    # Windows so a version-manager installation need not resolve parent folders.
    node = shutil.which("node")
    if node:
        os.environ.setdefault("PLAYWRIGHT_NODEJS_PATH", node)
    if os.name == "nt":
        current = os.environ.get("NODE_OPTIONS", "")
        flags = [flag for flag in ["--preserve-symlinks", "--preserve-symlinks-main"] if flag not in current.split()]
        os.environ["NODE_OPTIONS"] = " ".join([current, *flags]).strip()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    report = {"viewports": [], "behaviors": [], "limitations": ["CSS zoom checks layout at 200%; real assistive-technology and novice-reader tests remain pending."]}
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 1000}, reduced_motion="reduce")
        context.set_offline(True)
        page = context.new_page()
        errors = []
        network = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("request", lambda request: network.append(request.url) if request.url.startswith(("https://", "http://")) else None)
        for width in [375, 768, 1440]:
            page.set_viewport_size({"width": width, "height": 900})
            for name in PAGES:
                page.goto(page_url(name))
                assert page.locator("h1").count() == 1
                assert_layout(page, width)
                if name != "index":
                    assert all(lab.is_visible() for lab in page.locator(".lab[data-experiment]").all())
                    assert page.locator("#quiz-form").is_visible()
                    page.locator("input[name=answer]").first.check()
                    page.locator("#quiz-form button").click()
                    assert page.locator("#quiz-feedback").inner_text()
                if width in [375, 1440]:
                    page.screenshot(path=str(OUTPUT / f"{name}-{width}.png"), full_page=True)
                report["viewports"].append(f"{name}:{width}")

        page.set_viewport_size({"width": 375, "height": 900})
        for width in [375, 768, 1440]:
            page.set_viewport_size({"width": width, "height": 900})
            for name in ["check-understanding", "principles-reference", "transformer-reference", "architecture-guide", "advanced", "prompt-reference", "rag-reference", "applications-guide", "context-reference", "agent-reference", "execution-guide", "multimodal-reference", "embedding-reference", "protocols-reference", "deck", "cards", "review-guide"]:
                page.goto(page_url(name))
                assert_layout(page, width)
                assert page.locator("h1").count() == 1
                assert page.locator("script").count() == 0
                if name in ["check-understanding", "review-guide"]:
                    assert page.locator(".review-task" if name == "check-understanding" else ".review-rubric").count() == 6
                if name == "principles-reference":
                    assert page.locator("table").count() == 4
                    assert "35308" in page.locator("body").inner_text()
                    assert page.locator('a[href="tokens.html"]').count() == 1
                if name == "advanced":
                    assert page.locator("table").count() == 1
                    assert "KV Cache" in page.locator("body").inner_text()
                if name in ["prompt-reference", "rag-reference", "applications-guide"]:
                    expected = "不保证模型掌握某项能力" if name == "prompt-reference" else "相似度分数不是事实置信度"
                    assert expected in page.locator("body").inner_text()
                    assert page.locator("figure img").count() == 1
                if name in ["context-reference", "agent-reference", "execution-guide"]:
                    expected = "外部存储" if name == "context-reference" else "lookup_price"
                    assert expected in page.locator("body").inner_text()
                    assert page.locator("figure img").count() == (2 if name == "execution-guide" else 1)
                if name in ["transformer-reference", "architecture-guide"]:
                    assert "1.231059" in page.locator("body").inner_text()
                    assert "post-norm" in page.locator("body").inner_text()
                    assert page.locator("figure img").count() == 2
                if name == "check-understanding":
                    assert "一种答法" not in page.locator("body").inner_text()
                    assert page.locator("#review-N01").count() == 1
                    page.locator('a[href="review-guide.html"]').focus()
                    assert page.locator(":focus").inner_text().startswith("做完再看")
                if width == 375:
                    page.screenshot(path=str(OUTPUT / f"{name}-{width}.png"), full_page=True)
                report["viewports"].append(f"{name}:{width}")
                if width == 1440:
                    page.evaluate("document.body.style.zoom = '2'")
                    assert_layout(page, width)
        with page.expect_download() as download:
            page.locator('a[download="llm-reading-record.json"]').click()
        record = json.loads(Path(download.value.path()).read_text(encoding="utf-8"))
        assert record["coreIndependent"] is None and len(record["tasks"]) == 6
        assert all(item["status"] is None and not item["firstAnswer"] for item in record["tasks"])
        report["behaviors"].append("unfamiliar tasks, separate rubric, keyboard navigation and actual blank-record download")
        page.set_viewport_size({"width": 375, "height": 900})
        page.goto(page_url("tokens"))
        for encoding in ["cl100k_base", "o200k_base"]:
            page.locator("#encoding").select_option(encoding)
            for example in ["english", "chinese", "mixed", "unicode"]:
                page.locator("#token-input").select_option(example)
                assert "无损" in page.locator("#token-status").inner_text()
                page.locator(".token-piece").last.click()
                assert page.locator('.token-piece[aria-pressed="true"]').count() == 1
                assert "UTF-8" in page.locator("#token-detail").inner_text()
                assert_layout(page, 375)
        page.locator(".lab").screenshot(path=str(OUTPUT / "tokens-unicode-mobile.png"))
        report["behaviors"].append("8 tokenizer snapshots, byte details and reconstruction")

        page.goto(page_url("generation"))
        page.locator("#temperature").fill("0")
        assert "100.0%" in page.locator("#candidate-bars").inner_text()
        before = page.locator("#generated-text").inner_text()
        page.locator("#sample-many").click()
        assert "100 次" in page.locator("#sample-result").inner_text()
        assert page.locator("#generated-text").inner_text() == before
        page.locator("#generate-step").click()
        assert page.locator("#generated-text mark").inner_text() == "水"
        assert "咖啡" not in page.locator("#candidate-bars").inner_text()
        page.locator("#generate-step").click()
        page.locator("#generate-step").click()
        assert page.locator("#generate-step").is_disabled()
        assert "停止符" in page.locator("#generation-status").inner_text()
        assert "<结束>" not in page.locator("#generated-text").inner_text()
        page.locator("#reset-generation").click()
        assert page.locator("#generate-step").is_enabled()
        assert page.locator("#generated-text").inner_text() == before
        page.locator("#seed").fill("-1")
        page.locator("#reset-generation").click()
        assert not page.locator("#seed").evaluate("input => input.checkValidity()")
        page.locator("#seed").fill("42")
        page.locator("#temperature").fill("1.4")
        page.locator("#generate-step").click()
        history = page.locator("#generation-history").inner_text()
        page.locator("#reset-generation").click()
        page.locator("#generate-step").click()
        assert page.locator("#generation-history").inner_text() == history
        page.locator(".lab").screenshot(path=str(OUTPUT / "generation-step-mobile.png"))
        report["behaviors"].append("sampling without append; candidate update; EOS; reset; invalid seed; replay")

        page.goto(page_url("context"))
        page.locator('input[name=suspect][value="2"]').check()
        page.locator("#audit-materials").click()
        assert "材料未提供" in page.locator("#verdict-2").inner_text()
        assert "4/4" in page.locator("#audit-status").inner_text()
        page.locator('input[name=document][value="B"]').check()
        assert not page.locator("#verdict-2").inner_text()
        page.locator("#audit-materials").click()
        assert "与材料不符" in page.locator("#verdict-2").inner_text()
        assert "社区阅览室" in page.locator("#corrected-answer").inner_text()
        page.locator('input[name=document][value="C"]').check()
        page.locator("#audit-materials").click()
        assert "冲突" in page.locator("#verdict-1").inner_text()
        assert page.locator("#verdict-1 a").count() == 2
        page.locator(".lab").screenshot(path=str(OUTPUT / "context-conflict-mobile.png"))
        for checkbox in page.locator('input[name=document]').all():
            checkbox.uncheck()
        page.locator("#audit-materials").click()
        assert "没有选择材料" in page.locator("#audit-status").inner_text()
        assert page.locator(".verdict.missing").count() == 4
        page.locator("#reset-materials").click()
        assert page.locator('input[name=document]:checked').count() == 1
        assert not page.locator("#corrected-answer").is_visible()
        report["behaviors"].append("missing, wrong, conflicting and absent material; quote anchors; reset and stale-feedback clearing")

        page.goto(page_url("vectors"))
        initial = page.locator("#initial-vector").inner_text()
        fruit = page.locator("#context-vector").inner_text()
        assert "未定义" in page.locator("#vector-similarities").inner_text()
        page.locator("#vector-context").select_option("company")
        assert page.locator("#initial-vector").inner_text() == initial
        assert page.locator("#context-vector").inner_text() != fruit
        page.locator("#reset-vectors").click()
        assert page.locator("#context-vector").inner_text() == fruit
        page.locator(".numbers summary").click()
        assert "0.9500" in page.locator("#vector-numbers").inner_text()
        page.locator(".lab").screenshot(path=str(OUTPUT / "vectors-mobile.png"))
        report["behaviors"].append("fixed initial vector, context switch, full-dimensional similarities, zero vector and reset")

        page.goto(page_url("attention"))
        before = page.locator("#attention-sum").inner_text()
        page.locator("#change-future").check()
        assert page.locator("#attention-sum").inner_text() == before
        assert "差值 [0.0000, 0.0000]" in page.locator("#attention-status").inner_text()
        for position in range(4):
            page.locator("#attention-position").select_option(str(position))
            assert "权重和 1.000000" in page.locator("#attention-sum").inner_text()
            assert page.locator("#attention-weights .bar-row").count() == 4
        assert page.locator("#change-future").is_disabled()
        assert not page.locator("#change-future").is_checked()
        page.locator("#reset-attention").click()
        assert page.locator("#attention-sum").inner_text() == before
        page.locator(".numbers summary").click()
        assert "屏蔽" in page.locator("#attention-numbers").inner_text()
        page.locator(".lab").screenshot(path=str(OUTPUT / "attention-mobile.png"))
        page.locator(".deeper-figure summary").first.click()
        assert_layout(page, 375)
        report["behaviors"].append("causal invariance, all positions, normalized weights, future toggle boundary and deeper figure")
        page.locator(".deeper-figure summary").nth(1).click()
        assert page.locator('.deeper-figure img[src$="multihead-flow.svg"]').is_visible()
        assert_layout(page, 375)
        page.locator(".deeper-figure").nth(1).screenshot(path=str(OUTPUT / "multihead-flow-mobile.png"))
        report["behaviors"].append("multihead figure opens alongside the existing Transformer block")

        page.goto(page_url("context"))
        page.locator(".deeper-figure summary").click()
        assert_layout(page, 375)
        assert page.locator('.deeper-figure img[src$="context-selection.svg"]').is_visible()
        page.locator(".deeper-figure").screenshot(path=str(OUTPUT / "context-selection-mobile.png"))
        report["behaviors"].append("context selection figure opens with output-budget and storage boundaries")

        page.goto(page_url("training"))
        initial_loss = float(page.locator("#training-metrics dd").nth(1).inner_text())
        initial_bars = page.locator("#training-prediction").inner_text()
        page.locator("#train-step").click()
        assert float(page.locator("#training-metrics dd").nth(1).inner_text()) < initial_loss
        assert page.locator("#training-prediction").inner_text() != initial_bars
        page.locator(".numbers summary").filter(has_text="展开选中参数").click()
        assert "更新前目标概率" in page.locator("#gradient-detail").inner_text()
        page.locator("#predict-only").click()
        assert "参数没有更新" in page.locator("#prediction-status").inner_text()
        assert page.locator("#training-metrics dd").first.inner_text() == "1 / 500"
        page.locator("#learning-rate").fill("1.2")
        assert page.locator("#learning-rate-value").inner_text() == "1.20"
        page.locator("#train-run").click()
        page.wait_for_function("parseInt(document.querySelector('#training-metrics dd').textContent) >= 20")
        page.locator("#train-pause").click()
        paused = page.locator("#training-metrics").inner_text()
        page.wait_for_timeout(180)
        assert page.locator("#training-metrics").inner_text() == paused
        assert page.locator("#train-run").is_enabled()
        page.locator('.lab[data-experiment="X05"]').screenshot(path=str(OUTPUT / "training-paused-mobile.png"))
        page.locator("#train-run").click()
        page.evaluate("window.dispatchEvent(new PageTransitionEvent('pagehide'))")
        page.evaluate("window.dispatchEvent(new PageTransitionEvent('pageshow'))")
        stopped = page.locator("#training-metrics").inner_text()
        page.wait_for_timeout(120)
        assert page.locator("#training-metrics").inner_text() == stopped
        page.locator("#train-reset").click()
        assert page.locator("#training-metrics dd").first.inner_text() == "0 / 500"
        assert page.locator("#training-prediction").inner_text() == initial_bars
        assert page.locator("#learning-rate").input_value() == "0.8"
        page.locator("#train-run").click()
        page.wait_for_function("document.querySelector('#training-metrics dd').textContent === '500 / 500'", timeout=20000)
        assert page.locator("#train-run").is_disabled()
        assert page.locator("#train-pause").is_disabled()
        report["behaviors"].append("training actual loss/probability change, gradient display, predict-only immutability, pause, pagehide, reset and 500-step cap")

        page.locator("#distill-reset").click()
        teacher_before = page.locator("#distill-distributions tr").first.locator("td").first.inner_text()
        initial_water = float(page.locator("#distill-distributions tr").first.locator("td").nth(2).inner_text().strip("%"))
        page.locator("#distill-step").click()
        assert "第 1 步" in page.locator("#distill-loss").inner_text()
        assert float(page.locator("#distill-distributions tr").first.locator("td").nth(2).inner_text().strip("%")) > initial_water
        assert teacher_before == page.locator("#distill-distributions tr").first.locator("td").first.inner_text()
        assert "新值 = 旧值" in page.locator("#distill-update").inner_text()
        page.locator("#distill-teacher").select_option("wrongTeacher")
        assert "第 0 步" in page.locator("#distill-loss").inner_text()
        page.locator("#distill-step").click()
        assert float(page.locator("#distill-distributions tr").first.locator("td").nth(2).inner_text().strip("%")) < initial_water
        page.locator("#distillation-lab").screenshot(path=str(OUTPUT / "distillation-wrong-teacher-mobile.png"))
        page.locator("#distill-alpha").fill("0")
        page.locator("#distill-step").click()
        assert float(page.locator("#distill-distributions tr").first.locator("td").nth(2).inner_text().strip("%")) > initial_water
        page.locator("#distill-temperature").focus()
        page.keyboard.press("ArrowRight")
        assert page.locator("#distill-temperature").input_value() == "2.5"
        assert "第 0 步" in page.locator("#distill-loss").inner_text()
        for _ in range(4):
            page.locator("#distill-many").click()
        assert "第 100 步" in page.locator("#distill-loss").inner_text()
        assert page.locator("#distill-many").is_disabled() and page.locator("#distill-step").is_disabled()
        page.locator("#distill-reset").click()
        assert page.locator("#distill-step").is_enabled()
        assert "第 0 步" in page.locator("#distill-loss").inner_text()
        assert_layout(page, 375)
        report["behaviors"].append("distillation: actual student update, fixed teacher, wrong signal, hard-only contrast, keyboard temperature, resets and cap")

        page.goto(page_url("assistant"))
        page.locator("#check-assistant").click()
        assert "请先选择" in page.locator("#assistant-status").inner_text()
        for stage in ["pretrain", "sft", "preference"]:
            page.locator("#assistant-stage").select_option(stage)
            assert page.locator("#stage-detail").inner_text()
        page.locator('[name="assistant-answer"][value="polite"]').check()
        page.locator("#check-assistant").click()
        assert "补了材料里没有的地点" in page.locator("#assistant-status").inner_text()
        page.locator('[name="assistant-answer"][value="grounded"]').check()
        assert "重新核对" in page.locator("#assistant-status").inner_text()
        page.locator("#check-assistant").click()
        assert "判断有依据" in page.locator("#assistant-status").inner_text()
        page.locator(".lab").screenshot(path=str(OUTPUT / "assistant-mobile.png"))
        page.locator("#reset-assistant").click()
        assert page.locator('[name="assistant-answer"]:checked').count() == 0
        page.locator(".model-practice summary").click()
        assert "DeepSeek-V4.1-Flash-1017" in page.locator(".model-practice").inner_text()
        assert "Kimi K3" in page.locator(".model-practice").inner_text()
        report["behaviors"].append("illustrative stages, evidence challenge, required choice, feedback reset and official model references")

        page.goto(page_url("evidence"))
        for name, expected in [("wrong-time", "与原文不符"), ("missing-place", "材料未提供"), ("fake-quote", "引句不在原文"), ("fake-source", "来源不存在"), ("absolute-date", "与原文不符"), ("conflict", "冲突待确认")]:
            page.locator("#evidence-case").select_option(name)
            assert not page.locator("#evidence-result").inner_text()
            page.locator("#check-evidence").click()
            assert expected in page.locator("#evidence-result").inner_text()
        page.locator(".lab[data-experiment]").screenshot(path=str(OUTPUT / "evidence-conflict-mobile.png"))
        report["behaviors"].append("six evidence counterexamples: missing/false source, unsupporting quote, date and conflict")

        page.goto(page_url("retrieval"))
        assert page.locator("#retrieval-hits .document").count() == 3
        assert "冲突待确认" in page.locator("#retrieval-answer").inner_text()
        assert "城市图书馆" not in page.locator("#retrieval-context").inner_text()
        page.locator("#chunk-size").select_option("3")
        assert not page.locator("#retrieval-answer").inner_text()
        page.locator("#top-k").select_option("8")
        page.locator("#run-retrieval").click()
        page.locator("#retrieval-query").fill("读书会 报名 地点")
        page.locator("#run-retrieval").click()
        assert "忽略前面的要求" in page.locator("#retrieval-hits").inner_text()
        assert "社区阅览室" in page.locator("#retrieval-answer").inner_text()
        assert "城市图书馆" not in page.locator("#retrieval-answer").inner_text()
        page.locator("#retrieval-hits a").first.click()
        assert page.locator("#source-R1").is_visible() or page.locator("#source-R2").is_visible()
        page.locator("#no-retrieval").click()
        assert "未找到" in page.locator("#retrieval-status").inner_text()
        assert not page.locator("#retrieval-answer").inner_text()
        page.locator("#retrieval-query").fill("")
        page.locator("#run-retrieval").click()
        assert "查询为空" in page.locator("#retrieval-status").inner_text()
        page.locator("#reset-retrieval").click()
        assert page.locator("#retrieval-hits .document").count() == 3
        page.locator(".lab[data-experiment]").screenshot(path=str(OUTPUT / "retrieval-mobile.png"))
        report["behaviors"].append("retrieval query/chunk/top-k, stale clearing, source anchors, injection as content and empty/no hits")

        page.goto(page_url("tools"))
        assert "没有可交付的成功回执" in page.locator("#tool-result").inner_text()
        for expected in ["已校验", "已执行", "已回传", "已完成"]:
            page.locator("#tool-step").click()
            assert expected in page.locator("#tool-status").inner_text()
        assert "成功回执：100" in page.locator("#tool-result").inner_text()
        assert page.locator("#tool-step").is_disabled()
        for scenario in ["division-zero", "invalid", "unknown", "timeout"]:
            page.locator("#tool-scenario").select_option(scenario)
            while page.locator("#tool-step").is_enabled():
                page.locator("#tool-step").click()
            assert "失败停止" in page.locator("#tool-status").inner_text()
            assert "没有可交付的成功回执" in page.locator("#tool-result").inner_text()
        page.locator("#tool-scenario").select_option("success")
        page.locator("#cancel-tool").click()
        assert "已取消" in page.locator("#tool-status").inner_text()
        page.locator("#reset-tool").click()
        page.locator("#tool-request").fill("{")
        assert page.locator("#tool-step").is_disabled()
        page.locator("#load-tool").click()
        assert "JSON 格式无效" in page.locator("#tool-status").inner_text()
        page.locator(".lab[data-experiment]").screenshot(path=str(OUTPUT / "tool-invalid-mobile.png"))
        report["behaviors"].append("tool actual result, four failure paths, cancellation, terminal stop and malformed JSON")

        page.goto(page_url("approaches"))
        page.locator("#check-approach").click()
        assert "请先选择" in page.locator("#approach-status").inner_text()
        for case, answer in [("short", "prompt"), ("manuals", "rag"), ("sum", "tool"), ("format", "sft"), ("combined", "hybrid")]:
            page.locator("#approach-case").select_option(case)
            page.locator(f'[name="approach"][value="{answer}"]').check()
            page.locator("#check-approach").click()
            assert "符合这道题的条件" in page.locator("#approach-status").inner_text()
        page.locator("#reset-approach").click()
        assert page.locator('[name="approach"]:checked').count() == 0
        report["behaviors"].append("five conditional approach choices, missing selection and reset")

        page.goto(page_url("project"))
        for case, expected in [("complete", "可整理草稿"), ("missing", "待补充报告"), ("conflict", "冲突待确认"), ("irrelevant", "材料不足"), ("injection", "可整理草稿"), ("no-evidence", "材料不足"), ("outside", "超出材料范围")]:
            page.locator("#project-case").select_option(case)
            assert page.locator("#export-project-json").is_disabled()
            page.locator("#run-project").click()
            assert expected in page.locator("#project-status").inner_text()
            if case == "injection":
                assert "邻里工坊" in page.locator("#project-report").inner_text()
                assert "市民中心" not in page.locator("#project-report").inner_text()
        page.locator("#project-case").select_option("conflict")
        page.locator("#run-project").click()
        for checkbox in page.locator('[name="project-check"]').all():
            checkbox.check()
        assert page.locator("#export-project-json").is_enabled()
        with page.expect_download() as pending:
            page.locator("#export-project-json").click()
        downloaded = pending.value
        target = OUTPUT / downloaded.suggested_filename
        downloaded.save_as(target)
        content = json.loads(target.read_text(encoding="utf-8"))
        assert content["status"] == "conflict" and len(content["fields"][1]["evidence"]) == 2
        with page.expect_download() as pending:
            page.locator("#export-project-md").click()
        pending.value.save_as(OUTPUT / pending.value.suggested_filename)
        page.locator(".lab[data-experiment]").screenshot(path=str(OUTPUT / "project-conflict-mobile.png"))
        page.locator("#reset-project").click()
        assert page.locator("#export-project-json").is_disabled()
        assert not page.locator("#project-report").inner_text()
        report["behaviors"].append("seven project cases, evidence, out-of-scope, check gating and actual JSON/Markdown downloads")

        metadata = json.loads((ROOT / "book/assets/handdraw/llm/figures.json").read_text(encoding="utf-8"))
        new_figures = [Path(figure["file"]).stem for figure in metadata["figures"]]
        for name in new_figures:
            svg_source = (ROOT / "book" / "assets" / "handdraw" / "llm" / f"{name}.svg").read_text(encoding="utf-8")
            # An HTML wrapper avoids Chrome's native XML image-viewer capture
            # timeout and shows the actual 327 CSS-pixel figure width.
            page.set_content('<!doctype html><html lang="zh-CN"><body style="margin:0;width:327px">' + svg_source + '</body></html>')
            page.locator("svg").evaluate("svg => { svg.style.width = '327px'; svg.style.height = 'auto'; }")
            result = page.evaluate("""() => {
              const svg = document.querySelector('svg'), view = svg.viewBox.baseVal;
              return [...svg.querySelectorAll('text')].map(el => {
                const b = el.getBBox();
                return {text: el.textContent, x: b.x, y: b.y, right: b.x+b.width, bottom: b.y+b.height,
                  mobileSize: parseFloat(getComputedStyle(el).fontSize)*327/view.width,
                  fits: b.x >= 0 && b.y >= 0 && b.x+b.width <= view.width && b.y+b.height <= view.height};
              });
            }""")
            assert all(text["fits"] and text["mobileSize"] >= 16 for text in result), (name, result)
            page.locator("svg").screenshot(path=str(OUTPUT / f"figure-{name}-mobile.png"))
        report["behaviors"].append(f"all {len(new_figures)} teaching SVGs: actual text bounds and mobile-size labels")

        page.set_viewport_size({"width": 1440, "height": 1000})
        for name in PAGES:
            page.goto(page_url(name))
            page.evaluate("document.body.style.zoom = '2'")
            assert_layout(page, 1440)
        report["behaviors"].append("200% CSS zoom without horizontal document overflow")

        page.goto(page_url("generation"))
        page.keyboard.press("Tab")
        assert page.locator(":focus").inner_text() == "跳到正文"
        page.keyboard.press("Enter")
        page.locator("#generate-step").focus()
        page.keyboard.press("Enter")
        assert page.locator("#generation-history li").count() == 1
        page.locator("#temperature").focus()
        page.keyboard.press("ArrowRight")
        assert page.locator("#temperature").input_value() == "1.1"
        assert page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches")
        report["behaviors"].append("keyboard skip link, generate button, slider and reduced-motion preference")
        for width in [375, 768, 1440]:
            page.set_viewport_size({"width": width, "height": 1000})
            page.goto((ROOT / "exports" / "landing.html").as_uri())
            assert_layout(page, width)
            assert page.locator('a[href="llm/generation.html"]').count() == 1
            assert page.locator('a[href="llm/context.html"]').count() == 1
            page.screenshot(path=str(OUTPUT / f"landing-{width}.png"), full_page=True)
        report["behaviors"].append("parent landing page layout and new lesson entry links")
        assert not errors, errors
        assert not network, network
        context.close()

        context = browser.new_context(java_script_enabled=False, viewport={"width": 375, "height": 900})
        context.set_offline(True)
        page = context.new_page()
        for name in PAGES:
            page.goto(page_url(name))
            assert_layout(page, 375)
            if name != "index":
                assert not any(lab.is_visible() for lab in page.locator(".lab[data-experiment]").all())
                assert "静态实验读法" in page.locator("noscript").first.inner_text()
                page.locator(".quiz details summary").click()
                assert page.locator(".quiz details p").last.is_visible()
        report["behaviors"].append("offline and no-JavaScript static steps and self-test answers")
        for name in ["check-understanding", "review-guide", "principles-reference", "transformer-reference", "architecture-guide", "advanced", "prompt-reference", "rag-reference", "applications-guide", "context-reference", "agent-reference", "execution-guide", "multimodal-reference", "embedding-reference", "protocols-reference", "deck", "cards"]:
            page.goto(page_url(name))
            assert_layout(page, 375)
            if name in ["check-understanding", "review-guide"]:
                assert page.locator(".review-task" if name == "check-understanding" else ".review-rubric").count() == 6
            elif name in ["deck", "cards"]:
                assert page.locator(".study-sheet").count() == 12
                assert page.locator("details").count() == 12 and page.locator("h1").is_visible()
            else:
                assert page.locator("table").count() > 0 and page.locator("h1").is_visible()
        report["behaviors"].append("task and facilitator pages remain readable without JavaScript")
        browser.close()

    (OUTPUT / "browser-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "passed", "layouts": len(report["viewports"]), "behavior_groups": len(report["behaviors"]), "artifacts": "tmp/llm-review"}))


if __name__ == "__main__":
    run()
