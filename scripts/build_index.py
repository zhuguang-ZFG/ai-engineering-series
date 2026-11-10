"""Build the local series bookshelf from the shared catalog and existing files."""
from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]

CSS = """
:root{color-scheme:light dark;--paper:#f6f3ec;--ink:#272923;--muted:#62665c;--line:#cbcdbf;--accent:#26594f;--sheet:#fffdf7}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font-family:'Microsoft YaHei',system-ui,sans-serif;line-height:1.8}
main{max-width:1120px;margin:auto;padding:48px 28px 72px}a{color:var(--accent);text-underline-offset:4px}a:hover{text-decoration-thickness:2px}a:focus-visible{outline:3px solid var(--accent);outline-offset:5px}
header{border-top:5px solid var(--accent);padding-top:22px}.eyebrow{font-size:13px;letter-spacing:.14em;color:var(--muted)}h1{font-family:'Noto Serif CJK SC','Songti SC',serif;font-size:clamp(30px,5vw,52px);line-height:1.3;margin:18px 0}header p{max-width:750px;margin:12px 0 24px}.nav{display:flex;gap:12px 24px;flex-wrap:wrap;font-size:14px}
.route-map{margin:34px 0 38px}.route-map h2{font-size:20px;font-weight:600;margin:0 0 12px}.map-window{overflow-x:auto;border:1px solid var(--line);background:#f6f3ec}.map-window:focus-visible{outline:3px solid var(--accent);outline-offset:4px}.map-window svg{display:block;width:100%;min-width:860px;height:auto}.route-map figcaption{font-size:14px;color:var(--muted);margin-top:12px;max-width:850px}.map-scroll-hint{display:none}
.books{border-top:1px solid var(--ink)}article{display:grid;grid-template-columns:1fr auto;gap:20px;padding:20px 0;border-bottom:1px solid var(--line);align-items:center}article h2{font-size:18px;line-height:1.5;margin:0 0 5px;font-weight:600}.meta{font-size:13px;color:var(--muted)}.formats{display:flex;gap:8px 14px;flex-wrap:wrap;justify-content:flex-end;max-width:310px;font-size:14px}.formats a{white-space:nowrap}.empty{color:var(--muted)}footer{padding-top:26px;font-size:13px;color:var(--muted)}footer p{margin:6px 0}
@media(max-width:650px){main{padding:26px 18px 48px}.route-map{margin:28px 0}.map-scroll-hint{display:block;font-size:13px;color:var(--muted);margin:0 0 8px}article{grid-template-columns:1fr;gap:10px}.formats{justify-content:flex-start;max-width:none}}
@media(prefers-color-scheme:dark){:root{--paper:#20251f;--ink:#efeee5;--muted:#bdc6b8;--line:#4f5b4c;--accent:#98d2b7;--sheet:#283026}}
@media print{main{padding:0;max-width:none}a{color:inherit}.route-map{margin:20px 0;break-inside:avoid}.map-window svg{min-width:0}.map-scroll-hint{display:none}article{break-inside:avoid}header{border-top-width:2px}}
"""


def build(*, distribution=False):
    catalog = json.loads((ROOT / "series.json").read_text(encoding="utf-8"))
    # Embed the authored diagram so a collected index remains a standalone page.
    route_map = (ROOT / "assets/series-map.svg").read_text(encoding="utf-8")
    output = ROOT / "dist" if distribution else ROOT
    output.mkdir(parents=True, exist_ok=True)
    count = 0

    def link(relative, label):
        nonlocal count
        if not (output / relative).is_file():
            return ""
        count += 1
        return f'<a href="{quote(relative, safe="/")}">{escape(label)}</a>'

    cards = []
    priority = {"llm": 0, "prompt": 1}
    books = sorted(catalog["books"], key=lambda book: priority.get(book["id"], 2))
    for book in books:
        project = book["project"]
        if project == "agent-books":
            links = []
            if distribution:
                prefix = f'agent-books/{book["artifact_prefix"]}-zh'
                links = [link(prefix + ".html", "阅读"), link(prefix + ".pdf", "PDF"), link(prefix + ".epub", "EPUB"), link(prefix + "-examples.zip", "练习包")]
                if "en" in book["languages"]:
                    links.append(link(f'agent-books/{book["artifact_prefix"]}-en.html', "English"))
            elif book["id"] == "book":
                links = [link("agent-books/docs/sample-chapter.html", "中文样章"), link("agent-books/docs/sample-chapter.en.html", "English sample")]
            kind = "任务与协作方法 · 十八章" if book["id"] == "prompt" else "Agent 实战与机制"
        else:
            links = [link("model-course/exports/llm/course.html", "阅读"), link("model-course/deliverables/llm-course.pdf", "PDF"), link("model-course/deliverables/llm-course.epub", "EPUB"), link("model-course/deliverables/llm-course-answers.pdf", "答案册")]
            kind = "模型与应用工程 · 五阶段三十章"
        if not distribution:
            links.append(link(f'{project}/{book["source_entry"]}', "书稿与说明"))
        available = "".join(filter(None, links)) or '<span class="empty">尚未生成本册阅读文件</span>'
        cards.append(f'<article><div><h2>{escape(book["title"])}</h2><div class="meta">{escape(kind)}</div></div><div class="formats">{available}</div></article>')

    navigation = "" if distribution else '<nav class="nav" aria-label="项目导航">' + "".join([link("README.md", "项目说明"), link("docs/reading-routes.md", "跨书阅读路线"), link("docs/integration/README.md", "整合记录"), link("LICENSES.md", "来源与许可")]) + "</nav>"
    output_note = "" if distribution else "<p>已构建的 HTML、PDF、EPUB 和练习包可用 <code>python series.py collect</code> 汇集，阅读入口是 <code>dist/index.html</code>。</p>"
    text = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="color-scheme" content="light dark"><title>大模型与智能体工程 · 系列书架</title><style>{CSS}</style></head>
<body><main><header><div class="eyebrow">大模型与智能体工程 / 系列书架</div><h1>选一本，解决手头的问题</h1><p>这里有大模型课程、提示词方法册和八本 Agent 读物。想系统学模型，从课程 C01 开始；正在整理任务或使用工具，可以直接查对应分册。</p>{navigation}</header>
<figure class="route-map" aria-labelledby="route-map-heading"><h2 id="route-map-heading">几本书怎样配合读</h2><p class="map-scroll-hint" id="map-scroll-hint">路线图可横向滚动，或阅读图下的文字说明。</p><div class="map-window" tabindex="0" role="region" aria-label="选读路线图，可横向滚动">{route_map}</div><figcaption>提示词册帮助你说明交付、整理材料；需要执行命令时，再配读正在使用的工具册。文本回答可以直接核对依据，工具结果还要核对差异与测试回执。发现缺项，回到任务或材料补充。跨书选读不替代 C01–C30 的先修要求与阶段作业。</figcaption></figure>
<section class="books" aria-label="书籍目录">{"".join(cards)}</section>
<footer>{output_note}<p>本页可在本地打开，各册的版本和来源见书内说明。程序检查、模型实验与独立读者验收的结果分别记录，验证范围以各册记录为准。</p></footer></main></body></html>
'''
    (output / "index.html").write_text(text, encoding="utf-8")
    return {"page": str((output / "index.html").relative_to(ROOT)), "books": len(books), "existing_links": count}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist", action="store_true")
    args = parser.parse_args()
    print(json.dumps(build(distribution=args.dist), ensure_ascii=False))
