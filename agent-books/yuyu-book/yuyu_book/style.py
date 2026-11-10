"""Single-file page shell; ornaments and CSS live in deco/style_css."""
from __future__ import annotations

from html import escape

from .deco import (INK_MARKS, WHEEL_SVG, ink_mark, itinerary, key_mark, knot,
                   route_map, rut, trace, wheel)
from .style_css import CSS

__all__ = ["CSS", "INK_MARKS", "WHEEL_SVG", "ink_mark", "itinerary", "key_mark",
           "knot", "route_map", "rut", "trace", "wheel", "page"]

def page(lang: str, title: str, css: str, body_class: str, content: str,
         rail: str, colophon: str, *, author: str = "LinTsinghua") -> str:
    fav = ('<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='
           "'http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Ccircle "
           "cx='16' cy='16' r='12' fill='none' stroke='%23B4472F' "
           "stroke-width='3'/%3E%3Ccircle cx='16' cy='16' r='4' "
           "fill='%23B4472F'/%3E%3C/svg%3E\">")
    desc = ("Claude Code 架构深度剖析——对话循环、工具、权限、记忆、上下文、"
            "钩子、子智能体、编排、技能、MCP、流式、Plan，逐步构建自己的 "
            "Agent Harness。" if lang == "zh" else
            "A deep architectural analysis of Claude Code — the conversation "
            "loop, tools, permissions, memory, context, hooks, sub-agents, "
            "orchestration, skills, MCP, streaming, Plan.")
    og = (f'<meta property="og:title" content="{title}">'
          f'<meta property="og:description" content="{desc}">'
          '<meta property="og:type" content="book">'
          '<meta property="og:image" content="cover.png">')
    return f"""<!doctype html>
<html lang="{'zh-CN' if lang == 'zh' else 'en'}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<meta name="author" content="{escape(author, quote=True)}">
<meta name="generator" content="yuyu-book">
{fav}
{og}
<title>{title}</title>
<style>{css}</style>
</head>
<body class="{body_class}">
{rail}
<main class="sheet">
{content}
{colophon}
</main>
</body>
</html>"""
