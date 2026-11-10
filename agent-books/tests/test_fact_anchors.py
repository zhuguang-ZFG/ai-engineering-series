"""Anchors the dates and the printed arithmetic to sources the reader can check.

Two kinds of claim fail silently when prose is edited, so each one is
re-derived here rather than restated:

* Chapter 1's milestone timeline. Every date below was read off the page the
  announcing party itself publishes (listed next to each row). The list also
  has to stay in chronological order, which is how "MCP came after Claude
  Code" survived once: the spec revision tag `2025-11-25` was read as the
  protocol's publication date.
* The cost examples in Chapters 6 and 13. The prices are parsed out of the
  chapter's own table and every total in the worked examples is recomputed
  from them, so a table edited without recomputing the totals -- or a total
  edited without recomputing the table -- goes red.

The Node floor is taken from CREDITS.md, which records what the npm package's
`engines.node` field said on the day it was read, so the chapter and the
source registry cannot drift apart.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CH01 = {
    "zh": ROOT / "第一部分-基础篇" / "01-智能体编程的新范式.md",
    "en": ROOT / "en/Part-1-Foundations" /
          "01-The-New-Paradigm-of-Agent-Programming.md",
}
CH06 = {
    "zh": ROOT / "第二部分-核心系统篇" / "06-记忆系统-Agent的长期记忆.md",
    "en": ROOT / "en/Part-2-Core-Systems" /
          "06-The-Memory-System-Agent-Long-Term-Memory.md",
}
CH13 = {
    "zh": ROOT / "第四部分-工程实践篇" / "13-流式架构与性能优化.md",
    "en": ROOT / "en/Part-4-Engineering-Practice" /
          "13-Streaming-Architecture-and-Performance-Optimization.md",
}

# substring that identifies the node in either edition, its month, and where
# the month comes from
MILESTONES = [
    ("GitHub Copilot", "2021.06", "github.blog Introducing GitHub Copilot"),
    ("ChatGPT", "2022.11", "openai.com/index/chatgpt, 2022-11-30"),
    ("GPT-4", "2023.03", "openai.com/index/gpt-4, 2023-03-14"),
    ("Function Calling", "2023.06",
     "openai.com/index/function-calling-and-other-api-updates, 2023-06-13"),
    ("Code Interpreter", "2023.07",
     "help.openai.com ChatGPT release notes, 2023-07-06"),
    ("Claude 2.1", "2023.11", "anthropic.com/news/claude-2-1, 2023-11-21"),
    ("Devin", "2024.03", "cognition.com/blog/introducing-devin, 2024-03-12"),
    ("Computer Use", "2024.10",
     "anthropic.com/news/3-5-models-and-computer-use, 2024-10-22"),
    ("Cursor Agent", "2024.11", "cursor.com/changelog/0-43-x, 2024-11-24"),
    ("MCP", "2024.11", "anthropic.com/news/model-context-protocol, 2024-11-25"),
    ("Claude Code", "2025.02",
     "anthropic.com/news/claude-3-7-sonnet, 2025-02-24"),
    # the disclosure this book's own foreword dates, so it is pinned to that
    ("Agent Harness", "2026.03", "00-foreword, npm source map disclosure"),
]

NODE_RX = re.compile(r'^\s*[A-Z]\["(\d{4}\.\d{2}) ([^"]*)', re.M)
CASE_ROW = re.compile(
    r"^\s*(\d+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+\$([\d.]+)", re.M)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def number(text: str) -> float:
    return float(text.replace(",", ""))


def fenced_blocks(text: str) -> list:
    """Every fenced block, opened and closed on its own line."""
    blocks, current = [], None
    for line in text.splitlines():
        if line.strip().startswith("```"):
            if current is None:
                current = []
            else:
                blocks.append("\n".join(current))
                current = None
        elif current is not None:
            current.append(line)
    return blocks


def mermaid_block(text: str, must_contain: str) -> str:
    blocks = [b for b in fenced_blocks(text) if must_contain in b
              and "flowchart" in b]
    if len(blocks) != 1:
        raise AssertionError(
            f"expected one mermaid block containing a marker, found {len(blocks)}")
    return blocks[0]


def fenced_block(text: str, must_contain: str) -> str:
    blocks = [b for b in fenced_blocks(text) if must_contain in b]
    if len(blocks) != 1:
        raise AssertionError(
            f"expected one fenced block containing a marker, found {len(blocks)}")
    return blocks[0]


def chapter1_nodes(text: str) -> list:
    nodes = NODE_RX.findall(mermaid_block(text, "GitHub Copilot"))
    if len(nodes) != len(MILESTONES):
        raise AssertionError(
            f"timeline has {len(nodes)} dated nodes, the pinned list has "
            f"{len(MILESTONES)}; add or remove the matching row in this test")
    return nodes


def ch13_prices(text: str) -> dict:
    """input / write / read / output, in dollars per 1M tokens."""
    block = fenced_block(text, "(+25%)")
    rows = [line for line in block.splitlines()
            if line.strip().startswith("|") and "$" in line
            and "per 1M" not in line]
    if len(rows) != 4:
        raise AssertionError(
            f"the price table should list 4 token types, found {len(rows)}")
    picked = [re.findall(r"\$([\d.]+)", line) for line in rows]
    for line, found in zip(rows, picked):
        if not found:
            raise AssertionError("a price row parsed to no dollar amount")
    prices = {"input": number(picked[0][0]), "write": number(picked[1][0]),
              "read": number(picked[2][0]), "output": number(picked[3][0])}
    assert "(+25%)" in rows[1] and "(-90%)" in rows[2], \
        "the cache rows are no longer marked with their premium and discount"
    return prices


class ChapterOneTimeline(unittest.TestCase):
    def test_milestone_dates_match_their_primary_sources(self):
        for lang in ("zh", "en"):
            with self.subTest(edition=lang):
                diffs = []
                for marker, expected, source in MILESTONES:
                    found = [date for date, label
                             in chapter1_nodes(read(CH01[lang]))
                             if marker in label]
                    if len(found) != 1:
                        diffs.append((marker, f"{len(found)} nodes", expected))
                    elif found[0] != expected:
                        diffs.append((marker, found[0], expected, source))
                self.assertEqual(
                    diffs, [],
                    "Chapter 1 milestone (marker, printed, expected, source)")

    def test_nodes_run_in_chronological_order(self):
        for lang in ("zh", "en"):
            with self.subTest(edition=lang):
                dates = [date for date, _label in
                         chapter1_nodes(read(CH01[lang]))]
                self.assertEqual(dates, sorted(dates),
                                 "a later node carries an earlier month")


class ChapterThirteenPrices(unittest.TestCase):
    def test_cache_premium_and_discount_follow_the_api(self):
        for lang in ("zh", "en"):
            with self.subTest(edition=lang):
                p = ch13_prices(read(CH13[lang]))
                self.assertAlmostEqual(p["write"] / p["input"], 1.25, places=6,
                                       msg="cache write is billed at 1.25x input")
                self.assertAlmostEqual(p["read"] / p["input"], 0.10, places=6,
                                       msg="cache read is billed at 0.1x input")
                self.assertLess(p["read"], p["input"], "a hit must be cheaper")

    def test_session_table_recomputes_from_the_price_table(self):
        for lang in ("zh", "en"):
            with self.subTest(edition=lang):
                p = ch13_prices(read(CH13[lang]))
                rows = CASE_ROW.findall(fenced_block(read(CH13[lang]), "63,000"))
                self.assertEqual(len(rows), 8, "the worked session has 8 turns")
                bad, cumulative = [], 0.0
                for turn, inp, out, rd, wr, printed in rows:
                    inp, out, rd, wr = (number(inp), number(out),
                                        number(rd), number(wr))
                    if inp - rd != wr:
                        bad.append((turn, "cache create != input - cache read"))
                    cumulative += (rd * p["read"] + wr * p["write"]
                                   + out * p["output"]) / 1_000_000
                    if abs(cumulative - float(printed)) > 0.005:
                        bad.append((turn, f"printed ${printed}, "
                                          f"recomputed ${cumulative:.5f}"))
                self.assertEqual(bad, [], "turn problems as (turn, detail)")

    def test_hit_rate_savings_line_follows_the_price_table(self):
        for lang in ("zh", "en"):
            with self.subTest(edition=lang):
                p = ch13_prices(read(CH13[lang]))
                lines = [line for line in read(CH13[lang]).splitlines()
                         if "0.168" in line]
                self.assertEqual(len(lines), 1, "one sentence quotes $0.168")
                line = lines[0]
                base = 200_000 * p["input"] / 1_000_000
                hit_cost = base * 0.8 * (p["read"] / p["input"])
                self.assertAlmostEqual(base, 0.60, places=3)
                self.assertAlmostEqual(hit_cost, 0.048, places=6)
                self.assertAlmostEqual(base * 0.2 + hit_cost, 0.168, places=3)
                self.assertAlmostEqual(
                    round((1 - (base * 0.2 + hit_cost) / base) * 100),
                    72, places=0)
                miss_as_write = base * 0.2 * (p["write"] / p["input"])
                self.assertAlmostEqual(miss_as_write + hit_cost, 0.198, places=3)
                self.assertAlmostEqual(
                    round((1 - (miss_as_write + hit_cost) / base) * 100),
                    67, places=0)
                for token in ("$0.60", "$0.168", "72%", "$0.048", "$0.198",
                              "67%"):
                    self.assertIn(token, line)


class ChapterSixCacheSharing(unittest.TestCase):
    def test_simplified_calculation_adds_up(self):
        for lang in ("zh", "en"):
            with self.subTest(edition=lang):
                block = fenced_block(read(CH06[lang]), "/ MTok")
                parts = [number(n) for n in
                         re.findall(r"([\d,]+) tokens", block)]
                self.assertEqual(parts[:2], [30_000, 50_000],
                                 "the two prefix components")
                rates = [float(n) for n in re.findall(r"\$([\d.]+) / MTok", block)]
                self.assertEqual(len(rates), 2, "one cached and one plain rate")
                billed = re.findall(r"\$([\d.]+)",
                                    "\n".join(line for line in block.splitlines()
                                              if "->" in line or "\u2192" in line))
                self.assertEqual(len(billed), 2, "the no-cache and cached totals")
                tokens = parts[0] + parts[1]
                self.assertEqual(len(parts), 3, "two components and one total")
                self.assertEqual(parts[2], tokens,
                                 "the resent token count is not the sum of the "
                                 "system prompt and the message history")
                no_cache, cached = float(billed[0]), float(billed[1])
                self.assertEqual(tokens, 80_000, "resend = system prompt + history")
                self.assertAlmostEqual(tokens * max(rates) / 1_000_000,
                                       no_cache, places=6)
                self.assertAlmostEqual(tokens * min(rates) / 1_000_000,
                                       cached, places=6)
                self.assertAlmostEqual(min(rates) / max(rates), 0.10, places=6)
                percent = [int(n) for n in re.findall(r"(\d+)%", block)]
                self.assertEqual(percent[-1], 90, "savings line")
                self.assertAlmostEqual(round((1 - cached / no_cache) * 100),
                                       percent[-1], places=0)


class InstallInstructions(unittest.TestCase):
    def test_node_floor_matches_the_registered_package_metadata(self):
        anchor = re.search(r"`engines\.node >= (\d+)`", read(ROOT / "CREDITS.md"))
        if anchor is None:
            anchor = re.search(r"engines\.node >= (\d+)", read(ROOT / "CREDITS.md"))
        self.assertIsNotNone(
            anchor, "CREDITS.md no longer records the npm engines.node floor; "
                    "re-read the registry and re-pin both the anchor and this test")
        floor = int(anchor.group(1))
        self.assertEqual(floor, 22, "the package this book anchors to")
        for lang in ("zh", "en"):
            with self.subTest(edition=lang):
                lines = read(CH01[lang]).splitlines()
                at = [i for i, line in enumerate(lines)
                      if "npm install -g @anthropic-ai/claude-code" in line]
                self.assertEqual(len(at), 1, "one install command in Chapter 1")
                window = "\n".join(lines[max(0, at[0] - 5):at[0]])
                self.assertIn(f"Node.js {floor}", window,
                              "the install step must state the package's floor")
                self.assertNotIn("18", window,
                                 "a superseded Node floor is still in prose")


if __name__ == "__main__":
    unittest.main()
