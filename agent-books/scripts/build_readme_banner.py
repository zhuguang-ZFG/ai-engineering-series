#!/usr/bin/env python3
"""Generate README banner SVGs — local, offline, no external services.

Produces two files referenced by README.md / en/README.md:
  docs/banner.svg      waving ink-gradient header with the book title
  docs/tagline.svg     looping brush-typing animation of the chapter arc

Technique: pure SVG (gradient + SMIL), self-hosted in the repo — the book's
own rule of 离线自包含 applies to its storefront, too. Palette = design
system v2 (C-32 charcoal / C-15 cinnabar).
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs"

GRAD = """
  <linearGradient id="ink" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#43392B"/>
    <stop offset=".55" stop-color="#26221B"/>
    <stop offset="1" stop-color="#B4472F"/>
  </linearGradient>"""

BANNER = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 210"
     font-family="'Noto Serif SC','Source Han Serif SC','思源宋体','SimSun',serif">
  <defs>{GRAD}
    <linearGradient id="wash" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#26221B" stop-opacity="0"/>
      <stop offset="1" stop-color="#26221B" stop-opacity=".55"/>
    </linearGradient>
  </defs>
  <path d="M0 0h850v158c-90 26-212 34-425 34S62 186 0 158Z" fill="url(#ink)"/>
  <path d="M0 158c90 26 212 34 425 34S760 184 850 158v52H0Z" fill="url(#wash)" opacity=".0"/>
  <g fill="#F5F0E6" opacity=".16">
    <circle cx="86" cy="118" r="34" fill="none" stroke="#F5F0E6" stroke-width="2.5"/>
    <circle cx="86" cy="118" r="10"/>
    <path d="M86 78v80M46 118h80" stroke="#F5F0E6" stroke-width="2" opacity=".35"/>
    <path d="M60 96q26-22 52 0M60 140q26 22 52 0" fill="none" stroke="#F5F0E6" stroke-width="1.6" opacity=".3"/>
  </g>
  <text x="425" y="86" text-anchor="middle" font-size="44" font-weight="650"
        fill="#FBF6EC" letter-spacing="5">御舆 · 解码 Agent Harness</text>
  <text x="425" y="128" text-anchor="middle" font-size="19" fill="#F5F0E6"
        opacity=".82" letter-spacing="3">Claude Code 架构深度剖析 —— 一本书，一条由浅入深的路</text>
  <g stroke="#F5F0E6" opacity=".5" fill="none" stroke-linecap="round">
    <path d="M60 176q106 18 213 8" stroke-width="1.6"/>
    <path d="M577 176q107 18 213 8" stroke-width="1.6"/>
  </g>
  <text x="425" y="196" text-anchor="middle" font-size="13" fill="#E9E4D8"
        opacity=".75" letter-spacing="2">LinTsinghua · CC BY-NC-SA 4.0</text>
</svg>
"""

# 打字动画：SMIL 循环揭示一行章名弧线（离线，无服务依赖）
TAGLINE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 46"
     font-family="'Noto Serif SC','Source Han Serif SC','思源宋体','SimSun',serif">
  <defs>
    <clipPath id="reveal"><rect x="8" y="0" width="0" height="46">
      <animate attributeName="width" values="0;0;660;660;0" keyTimes="0;.06;.72;.9;1"
               dur="9s" repeatCount="indefinite"/></rect>
    </clipPath>
  </defs>
  <g clip-path="url(#reveal)">
    <text x="12" y="31" font-size="21" fill="#26221B">对话循环 · 工具系统 · 权限管线 · 记忆 · 上下文 · 钩子 · 子智能体 · 编排 · 技能 · MCP · 流式 · Plan · 造一个 Harness</text>
  </g>
  <rect y="10" width="3" height="26" fill="#B4472F">
    <animate attributeName="x" values="8;8;668;668;8" keyTimes="0;.06;.72;.9;1"
             dur="9s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;.5;.56;.94;1"
             dur="1.1s" repeatCount="indefinite"/>
  </rect>
</svg>
"""


def main() -> None:
    (OUT / "banner.svg").write_text(BANNER, encoding="utf-8")
    (OUT / "tagline.svg").write_text(TAGLINE, encoding="utf-8")
    print(f"{OUT/'banner.svg'}\n{OUT/'tagline.svg'}")


if __name__ == "__main__":
    main()
