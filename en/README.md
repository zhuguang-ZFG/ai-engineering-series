<div align="center">

<img src="../docs/banner.svg" width="100%" alt="Yù Yú: Decoding Agent Harness" />

# Yù Yú: Decoding Agent Harness

<a href="../docs/beginner-reader.en.html"><img src="../docs/tagline.svg" width="660" alt="Conversation loop · Tools · Permissions · Memory · Context · Hooks · Sub-agents · Orchestration · Skills · MCP · Streaming · Plan" /></a>

[中文](../README.md) · **English**

[![License](https://img.shields.io/badge/license-CC%20BY--NC--SA%204.0-9C4630)](../LICENSE)
[![Book CI](https://github.com/zhuguang-ZFG/claude-code-book/actions/workflows/book.yml/badge.svg)](https://github.com/zhuguang-ZFG/claude-code-book/actions/workflows/book.yml)
[![Reading site](https://img.shields.io/website?url=https%3A%2F%2Fzhuguang-zfg.github.io%2Fclaude-code-book%2F&label=reading%20site)](https://zhuguang-zfg.github.io/claude-code-book/)

<table align="center">
<tr><td><img src="../cover.png" width="420" alt="御舆：解码 Agent Harness — Claude Code 架构深度剖析，LinTsinghua" /></td></tr>
<tr><td align="center">📖 <a href="../docs/beginner-reader.en.html">Beginner reader · illustrated</a> (plain language, shallow-to-deep; download and open in a browser) ｜ 🎨 <a href="../docs/illustration-gallery.html">Illustration gallery</a> ｜ <a href="../docs/illustration-prompts.md">Prompt handbook</a></td></tr>
</table>

</div>

Explore how an agent runtime connects the conversation loop, tools, permissions, memory, and orchestration. Fifteen chapters and four appendices connect implementation details to design trade-offs and a hands-on harness project.

> *“Of all artifacts that bring many crafts together, the chariot calls upon the most.”* — *Kǎo Gōng Jì* (Book of Crafts)
>
> Two thousand years ago, building a chariot was already an exercise in systems engineering. The **yú** (舆, carriage body) carries the rider; shafts, spokes, and axle fittings each serve their purpose. Only together can the vehicle move.
>
> Building an AI Agent calls for similar coordination: the conversation loop advances the task, tools perform actions, and permissions set boundaries. The runtime framework that supports and organizes these capabilities—**Agent Harness**—plays the role of the **yú**.
>
> Chariot builders brought many crafts into one working whole. Agent builders, too, must understand how the parts work together. **Yù Yú** (御舆, “driving the chariot”) evokes both control and an understanding of the machinery that makes it possible.
>
> This is the idea behind the title **Yù Yú**, also known as **Yú Shū** (舆书, “The Chariot Book”).

## Start reading

- **First visit:** [Foreword](00-Foreword.md), then chapters 01 → 02 → 04 → 15.
- **Build an agent:** read Parts 1 and 4; use Parts 2 and 3 when adding memory and extensions.
- **Look up a concept:** use the four appendices below.
- **Website:** [Online reading](https://lintsinghua.github.io/). Repository chapters remain directly readable on GitHub.

## Second volume · Omp (in progress)

This repository now carries a second, separate volume: the Chinese-language 《Omp 从入门到精通：原理与实战》 — an unofficial tutorial for an open-source terminal agent. Its manuscript lives in [../omp/](../omp/README.md) and its artifacts use the `yuyu-omp-*` prefix. It is written against **omp/18.15.0**; [../omp/VERIFY.md](../omp/VERIFY.md) records what was checked against a real install (18.16.0 included).

Two commands, two books: `make book` / `make book-pdf` still build Yù Yú only (both languages), while `make book-omp` / `make book-omp-pdf` build the Chinese omp edition — the latter also prints an A4 PDF. The equivalent command is `python scripts/bookctl.py build --product omp --lang zh [--pdf]`. Both write into `yuyu-book/dist/` under different prefixes, so building one volume never overwrites the other. Build details, plus the sizes and page counts measured on this machine, are in [../omp/BUILD.md](../omp/BUILD.md); the mechanism and boundaries of the two-product setup are §3.6 of [../STRUCTURE.md](../STRUCTURE.md).

`make check` / `make check-full` (that is, `bookctl check --fast` / `--full`) cover Yù Yú assembly, shared tests and repository content checks. Omp has separate structure and delivery gates in `omp/overhaul/audit_structure.py --check` and `audit_delivery.py`. Content CI also assembles the Chinese Omp sources; Book CI has an independent `omp` job for HTML/PDF. On Windows, run `powershell -File omp/overhaul/ci-local.ps1` to build Yù Yú Chinese HTML and Omp Chinese HTML/PDF together.

Reading routes are available from the [Yù Yú side](../docs/COMPARE-OMP.md) and the [Omp side](../omp/COMPARE-YUYU.md), with a [shared terminology table](../docs/yuyu-overhaul/SHARED-TERMS.md). The Omp English edition has only a [reserved directory](omp/README.md); translation and English builds have not started.

Illustration strategy: Mermaid architecture diagrams and hand-drawn concept art on two tracks. Concepts can be read across the two volumes; implementations and pinned versions cannot be mixed.

## Reading notes

Readers should distinguish observed implementation, architectural interpretation, and teaching examples. Feature flags and tool availability depend on build and runtime configuration; counts and timing examples are not promises about current releases.

Claude Code belongs to Anthropic. This independent book is not an official Anthropic publication. The book’s license does not extend to third-party code.

## Contents

### Part 1. Foundations — Building Mental Models

> Understand the paradigm shift in Agent programming and establish a holistic cognitive framework.

| # | Chapter | Core Content |
|:-:|---------|-------------|
| 01 | [The New Paradigm of Agent Programming](Part-1-Foundations/01-The-New-Paradigm-of-Agent-Programming.md) | Copilot → Claude Code evolution; five design principles; Bun + React/Ink + Zod v4 stack |
| 02 | [The Dialog Loop — Agent's Heartbeat](Part-1-Foundations/02-The-Dialog-Loop-Heartbeat-of-an-Agent.md) | `while(true)` async generator loop; five yield events; ten termination reasons; `QueryDeps` DI |
| 03 | [The Tool System — Agent's Hands](Part-1-Foundations/03-The-Tool-System-Agent-Hands.md) | `Tool<I,O,P>` five-element protocol; fail-safe `buildTool` factory; 55 tools × 12 categories; concurrent partitioning |
| 04 | [The Permission Pipeline — Agent's Guardrails](Part-1-Foundations/04-The-Permission-Pipeline-Agent-Guardrails.md) | Four-stage pipeline; five permission modes; Bash rule matching; speculative classifier 2s Promise.race |

### Part 2. Core Systems — Deep Into Subsystems

> Dissect the four core subsystems — configuration, memory, context, and hooks.

| # | Chapter | Core Content |
|:-:|---------|-------------|
| 05 | [Settings & Configuration — Agent's DNA](Part-2-Core-Systems/05-Settings-and-Configuration-Agent-DNA.md) | Six-layer config priority chain; merge rules; security boundary & supply chain defense; dual-layer feature gating |
| 06 | [The Memory System — Agent's Long-Term Memory](Part-2-Core-Systems/06-The-Memory-System-Agent-Long-Term-Memory.md) | Four closed memory types; "only save non-derivable info"; MEMORY.md index; Fork memory mechanism |
| 07 | [Context Management — Agent's Working Memory](Part-2-Core-Systems/07-Context-Management-Agent-Working-Memory.md) | Effective window formula; four-level compression (Snip→MicroCompact→Collapse→AutoCompact); circuit breaker |
| 08 | [The Hook System — Agent's Lifecycle Extension Points](Part-2-Core-Systems/08-The-Hook-System-Agent-Lifecycle-Extension-Points.md) | Five hook types; 22 lifecycle events; JSON response protocol; six-layer priority; three-layer security |

### Part 3. Advanced Patterns — Composition & Extension

> Explore how Agents compose, orchestrate, and extend — from sub-agents to MCP protocol bridging.

| # | Chapter | Core Content |
|:-:|---------|-------------|
| 09 | [Sub-Agents and the Fork Pattern](Part-3-Advanced-Patterns/09-Sub-Agents-and-the-Fork-Pattern.md) | Three Agent sources; agent roles and availability gates; byte-level Fork context inheritance; recursive Fork protection |
| 10 | [The Coordinator Pattern — Multi-Agent Orchestration](Part-3-Advanced-Patterns/10-The-Coordinator-Pattern-Multi-Agent-Orchestration.md) | Coordinator-Worker dual gating; "orchestrate-only" constraint; four addressing modes; four-stage workflow |
| 11 | [The Skill System & Plugin Architecture](Part-3-Advanced-Patterns/11-The-Skill-System-and-Plugin-Architecture.md) | 11 core skills; SKILL.md frontmatter; three-level parameter substitution; layered loading; plugin cache |
| 12 | [MCP Integration & External Protocols](Part-3-Advanced-Patterns/12-MCP-Integration-and-External-Protocols.md) | 8 connection configuration variants; five-state connection management; three-part tool naming; Bridge bidirectional comms |

### Part 4. Engineering Practice — From Principles to Construction

> Performance optimization details and a practical roadmap for building a complete Harness from scratch.

| # | Chapter | Core Content |
|:-:|---------|-------------|
| 13 | [Streaming Architecture & Performance Optimization](Part-4-Engineering-Practice/13-Streaming-Architecture-and-Performance-Optimization.md) | QueryEngine lifecycle; concurrency control; parallel prefetching and startup estimates; lazy loading |
| 14 | [Plan Mode & Structured Workflows](Part-4-Engineering-Practice/14-Plan-Mode-and-Structured-Workflows.md) | "Think before you act" philosophy; plan file three-layer recovery; local scheduling & remote triggers |
| 15 | [Building Your Own Agent Harness](Part-4-Engineering-Practice/15-Building-Your-Own-Agent-Harness.md) | Six-step implementation roadmap; circular dependency solutions; four-layer observability; security threat model |

### Appendix — Reference Quick-Lookup

| | Content |
|:-:|---------|
| [A](Appendices/A-Architecture-Navigation-Map.md) | **Architecture Navigation Map** — 16 core modules, dependency tree, 6 data flow paths, 10 design patterns |
| [B](Appendices/B-Complete-Tool-Inventory.md) | **Complete Tool Inventory** — 50+ tools × 12 categories, readOnly/destructive/concurrencySafe attributes |
| [C](Appendices/C-Feature-Flag-Reference.md) | **Feature Flag Reference** — 89 flags × 13 categories, compile-time/runtime types, dependency graphs |
| [D](Appendices/D-Glossary.md) | **Glossary** — 122 bilingual term definitions with cross-references and chapter locations |


## The book as one file

`yuyu-book/` assembles the 20 units into **a single book you can read offline**: one self-contained HTML file (6.3 MB Chinese / 6.4 MB English) and an A4-typeset PDF (519 pages / 34.8 MB in Chinese, 559 pages / 23.7 MB in English). Artifacts land in `yuyu-book/dist/`. PDF page counts and sizes depend on the installed CJK font. These figures use CI's Noto CJK face, not a local Windows measurement; each build log reports the actual results.

These measurements come from the [merged Full run](https://github.com/zhuguang-ZFG/claude-code-book/actions/runs/42473136200). Its ten build checks passed. The final SVGs are smaller than the candidate artwork, taking the measured CI English HTML size from a rounded 6.5 MB to 6.4 MB; the unchanged README then failed reconciliation. Only the measured claims are corrected here, not the rules in `scripts/check_artifact_claims.py`. The published `v0.3.6` tag and assets remain unchanged.

| File | Language |
|------|----------|
| `yuyu-agent-harness-zh.html` / `.pdf` | Chinese |
| `yuyu-agent-harness-en.html` / `.pdf` | English |

The book includes a cover, imprint and license page, revision history, reading routes, a contents page with page numbers, and a full-book route map on its own sheet. The foreword is the wheel at the head of the road; fifteen chapters form four serpentine legs, with the appendices on a dashed siding. Each chapter opens with a compass card — its question, deliverable and boundary — and source anchors. All 160 diagrams per edition (320 across both) are pre-rendered Mermaid diagrams; 17 explanatory drawings bring the numbered figure count to 177 per edition. Code-language labels, footnotes, sources and a subject index complete the reading apparatus; the Chinese index also has a Chinese-term section after A–Z.

Artwork uses a mixed format. Emblems, the postman and explanatory figures remain hand-drawn animated SVG; the first two part openers use reviewed, generated transparent-ink PNGs. The cover and remaining part openers retain SVG. Unit-specific header strokes, closing wheel ruts and part-opening roads follow the reading route. Wide screens (≥1360 px) also have a persistent contents rail. All images travel inside the offline file; dark-screen inversion does not invert the ink on paper.

The PDF adds sidebar bookmarks, foot folios, recto/verso running heads, a subject index with target page numbers, and clickable “see Chapter N” references. Chapters do not leave a sheet containing only a running head and folio. A diagram too wide for the portrait column gets a landscape sheet, with selectable, searchable labels. Long names such as `KAIROS_GITHUB_WEBHOOKS`, `skipDangerousModePermissionPrompt` and `~/.claude/settings.json` gain break points at underscores, slashes and camel-case seams — not inside ordinary English words — to reduce stretched spacing and table overflow. The HTML opens with the network unplugged, without external fonts, images or scripts.

Engineers new to the material can enter through the **plain-language layer**: each chapter starts with one sentence and an everyday analogy, while a dotted underline opens a three-line explanation — what a term means, why it works that way, and a picture to hold onto. When a term appears only as inline code, the underline sits on the identifier, so names such as `AbortController` remain discoverable. Popovers pin to the bottom of narrow screens or scrolling tables rather than being clipped. On paper, chapter-end term panels and *Why It Works This Way* carry the explanations; the 44 core terms' reasons are filed under the chapters that argue for them. Start / Core / Advanced stamps correspond to the foreword's three reading routes.

An old postman closes each unit with one line of marginalia. The 20 lines live in `yuyu-book/notes.json`, and *The Keeper's Notes* collects them in reading order with links back to their chapters. A term lock requires each line to use a registered form actually present in that chapter. Chinese lines stay within 36 characters; English lines within 130, with no Han characters. The keeper does not become a second manuscript.

43 hand-drawn line illustrations remain as source SVGs: a cover, 20 unit emblems, four part openers, one postman, and seventeen plates inside the prose. Those figures explain relationships or states — pause versus cancel, permission gates, the memory funnel, a fork filmstrip, a state dial and a concurrency gate, among others. Apart from the two part openers now using ink PNGs, the drawings retain `currentColor` SVG and the same meaning in dark mode, reduced motion and print. The whole plain-language layer can be disabled with `--no-plain`.

```bash
npm ci                                              # diagrams need Mermaid 11.17.2
python -m pip install -r yuyu-book/requirements.txt
python scripts/bookctl.py doctor                    # list every missing piece and its fix
python scripts/bookctl.py check --fast              # full Fast tier: dependencies, source assembly, both suites, content/diagram syntax, video, product idempotence
python scripts/bookctl.py build --product book --lang zh
python scripts/bookctl.py build --product book --lang both --pdf
```

`requirements.txt` is exported from `uv.lock` with exact pins. To upgrade, edit `pyproject.toml`, then run `uv lock` and `uv export --format requirements-txt --no-hashes --no-emit-project --no-annotate > yuyu-book/requirements.txt`; do not edit the export by hand.

Rendering diagrams and building PDFs needs a local Chromium or Edge (auto-detected, or pass `--browser <path>`). The Markdown chapters are the single source of truth: the build reads them and never rewrites a file.

## Building and releasing

`scripts/bookctl.py` is the repository's single command entry point; `make` only wraps it, and the builder can also be run directly as `python -m yuyu_book` (from `yuyu-book/`, or with `PYTHONPATH=yuyu-book`). Checks are layered: **Fast** (pull-request tier: pinned dependencies, source-mode assembly, both unittest suites, content checks, Mermaid syntax, video configuration, product idempotence), **Full** (main-branch or manual: Fast plus rendered assembly and both PDF editions), and **Release** (tag or manual: Full plus artifact-claim reconciliation, then release assembly to produce checksums and the release directory). In CI these are the `Fast` / `Full` / `Omp` / `Bootstrap` jobs in `.github/workflows/book.yml` and `.github/workflows/release.yml`; the old `check-book.yml` has been folded into `Fast` and no longer exists.

The release directory is assembled atomically by the command below (its version must equal the `version` in `yuyu-book/manifest.json`; `--epub` is optional):

```bash
python scripts/bookctl.py release --version 0.3.6 --out-dir ../book-release --epub
```

It holds both HTML/PDF editions, the Chinese Omp HTML/PDF, optional EPUBs, `site.zip`, 15 chapter video manifests, `release-notes.json` plus `release-notes.md` (the body `gh release` publishes), `SHA256SUMS`, and `build-report.json` / `artifact-manifest.json`, which record commands, commit, browser/font identity and artifact hashes. A failed step never leaves a partial release directory.

**Status (2026-11-08):** `v0.3.6` was assembled and published by the tag-push run of `release.yml` ([run 42423483244](https://github.com/zhuguang-ZFG/claude-code-book/actions/runs/42423483244)) as a [GitHub Release](https://github.com/zhuguang-ZFG/claude-code-book/releases/tag/v0.3.6): 15 assets covering three editions of HTML/PDF/EPUB, `site.zip`, the 15 chapter video manifests, `SHA256SUMS`, and both build reports; all 14 published files match their `SHA256SUMS` entries. The P3/P5 gates still await independent review, and `task_verify` remains unverified. See the [architecture decisions](../docs/architecture-decisions.md), [P3 structural comparison](../docs/migrations/legacy-v2-structure.md), [product-page visual audit](../docs/migrations/product-visual-audit.md) and [release migration note](../docs/migrations/release-migration.md).

## Contributing

Issues and pull requests are welcome. Include the chapter, section, expected correction, and a source link; for rendering problems, include the viewer and reproduction steps. Keep Chinese and English changes aligned. English manuscripts must contain no Han text except the Chinese-translation column in Appendix D; the build tests scan every line.

Before submitting, run `python3 scripts/bookctl.py check --fast`; it runs dependency reconciliation, source-mode assembly, both unittest suites, `scripts/check_book.py`, `npm run check:diagrams`, video configuration and product idempotence. Use `check --full` when diagrams or PDFs are involved. Mermaid validation requires Node.js 22 or later; run `npm ci` first. See [STRUCTURE.md](../STRUCTURE.md) for the repository layout and [CONTRIBUTING.md](../CONTRIBUTING.md) for the full workflow.

## License and acknowledgements

Book content: [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/). Credit the author, use non-commercially, and share adaptations under the same license. Third-party material retains its own terms.

The technical narrative is checked against Claude Code `2.1.310` plus the official documentation, Anthropic research posts, the MCP specification, and community discussion. Every external source — with the tag or commit it is pinned to, the access date, and its licensing posture — is registered in [CREDITS.md](../CREDITS.md) and `yuyu-book/sources.json` (55 entries, 22 of them GitHub repositories), and reachable from the book's own sources page. Those repository entries do two different jobs: some are **authorities** (Claude Code itself, the official SDKs, the MCP specification, Anthropic's research posts); the rest are **cross-checks** — what the same boundary grows into in someone else's hands: a swappable model route, another context strategy, a second protocol, what permissions degrade to when nobody is watching, how large a packaged unit of capability can get. A cross-check supports no technical claim. It exists to test whether the seams the book names really are seams. Thanks to the [Linux.Do](https://linux.do/) community; most of the discussion happens in [the book's release thread](https://linux.do/t/topic/1870593).

## Star History

<a href="https://star-history.com/#lintsinghua/claude-code-book&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="../docs/images/star-history-dark.svg" />
   <source media="(prefers-color-scheme: light)" srcset="../docs/images/star-history-light.svg" />
   <img alt="Star History Chart" src="../docs/images/star-history-light.svg" />
 </picture>
</a>
