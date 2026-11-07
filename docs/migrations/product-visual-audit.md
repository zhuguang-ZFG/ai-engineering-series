# Product-page visual audit (P4.6)

Scope: the three page families that pre-date P4 — the site portal, the two
beginner readers, and the illustration gallery. The knowledge cards and the
sample chapter were rebuilt in P4 and already ship the same tokens and the
same accessibility contracts; they are checked by the same suites but are not
re-audited here.

Method: computed-style probes and full-page screenshots in Chrome at
1280×900 and at an emulated 320×640 mobile viewport, in light and dark
preference, with the host's reduced-motion setting on (`matchMedia` reported
`reduce`, so every still-state below is the state a reduce user actually
gets). Static review of every stylesheet rule and inline script. No source
page was restyled to taste; differences that survive are deliberate and are
now pinned by tests.

## The shared ink language

| Token | Value | Where it shows |
|---|---|---|
| paper | `#F5F0E6` | body sheet on all three pages |
| ink | `#26221B` | body text, rules, illustration strokes |
| card paper | `#FFFDF8` | station, portal card, resume bar |
| cinnabar | `#B4472F` | accent: links' rule, brush, focus ring, progress |
| sky-deep | `#3A5A78` | in-text links (reader nav rows, video links) |
| muted inks | `#5C5448` / `#675F4F` / `#6E6353` / `#8A7D68` | captions, hints, counters |
| dark sheet (gallery only) | `#1E1D18` on `#E9E4D8` | the “DARK · 夜读” section |
| corners | `RADIUS_CARD`, `RADIUS_STATION`, `RADIUS_CHIP`, `RADIUS_RESUME` | hand-cut, never a single radius |
| shadow | `2px 3px 0 rgba(38,34,27,.1…)` | paper lifted off paper, never a blur |
| focus | `2px solid #B4472F`, offset 3px | every link and button |

All values come from `yuyu_book.products.tokens`; `tests/test_product_tokens.py`
fails on any hex the module does not list, and compares the shared colours with
the book's own custom properties. The seal favicon and the brush rule are
written once in the tokens module and injected into every page.

## Measured results

### Portal (`docs/portal.html`)

- Type: 16px/1.9 serif (zh stack), h1 28px. Cards 260px wide in a single
  column at 320px; page scroll width exactly 320. Seven cards, all reachable
  with the keyboard, entrance animation cancelled under reduce.
- Dark preference changes nothing: paper stays `rgb(245,240,230)` on
  `rgb(38,34,27)`, and the sheet declares no dark media rule (colour-scheme
  `light`). This is the intended light-only front door.
- The cover image resolves only in the assembled `site/` directory, where
  `pages.yml` copies `cover.png` beside `index.html`. Opened as the committed
  `docs/portal.html` it shows its alt text — a deployment boundary, not a page
  defect.

### Beginner readers (`docs/beginner-reader{,.en}.html`)

- Station rows at 1280px: art 300px, body text 432px, gap 26px. At 320px the
  sheet switches to a column (art and body 198px, card 260px, nav row 198px)
  with no horizontal scroll; this column switch is the P4.5 fix for the
  one-character-per-line squeeze.
- The resume bar is a 50px fixed paper chip in the ink style; the last
  station's nav row still clears it by 350px, so it never hides the way
  forward.
- Three scripts are progressive only: art replay, the resume banner
  (`display:none` until the script reads storage), and the progress bar
  (width 0 until scroll). The 25 prev/next rows are static markup, so with
  scripting off every station is still reachable in order.
- Type registers differ by edition on purpose and are pinned by test: zh
  16px/1.9 Noto Serif SC, en 16px/1.8 Iowan Old Style.

### Gallery (`docs/illustration-gallery.html`)

- A deliberate sans contact-sheet (14px/1.6 system stack, h1 18px) rather
  than the reader's serif: the page is a plate index, and the smaller sans
  keeps 42 bilingual captions legible per screen. Pinned by
  `test_each_page_sets_the_shared_type_and_corner`.
- Each of the 42 plates appears twice in the DOM — once on the paper sheet,
  once re-inked on the dark sheet by `currentColor` — for 84 figures total.
  The dark band is a section of a light page, not a theme.
- At 320px the toolbar wraps to 129px and the widest plate renders 264px;
  page scroll width is exactly 320. Inline plate widths are capped by the
  P4.5 `max-width:100%` rule.
- Under reduce the plates stay as finished drawings and the hint explains
  why; under scripting off the plates, captions and footer links are all
  static, only the replay hint stays empty.

## Defects found, fixed, and pinned

1. **English reader lost the nav-row sheet.** `.st-navrow` and `.prog` were
   added to the Chinese stylesheet in P4.5 but not the English one: the
   counter collided with the link (`1 / 25next →`) and the link fell back to
   UA blue with an underline. Both rules are now in both sheets;
   `StationNavigation.test_both_editions_style_the_nav_rows_and_progress_bar`
   fails on the drift.
2. **A stray `站` in the English resume banner** (“You stopped at station 站”).
   Removed; `test_the_english_resume_banner_speaks_english` fails on any CJK
   character in that banner.
3. **The readers had no way back to the front door.** Both footers now link
   `portal.html`, completing the scriptless loop portal → reader → gallery /
   book → portal. `test_every_page_links_back_into_the_site` now requires
   that specific link on every page except the portal itself.

## Deliberate differences kept

- Three heading scales — portal 28px, readers 24px, gallery 18px — track
  page density (a front door, a long read, a contact sheet), not drift.
- The gallery alone carries a dark sheet and a sans register; both are its
  identity and both are asserted, not tolerated.
- The readers alone keep the fixed resume chip; the cards use the same
  `RADIUS_RESUME` shape for their own dock, so the family resemblance holds.

## Gate evidence

- Six generators rerun (`build_site_portal`, `build_beginner_reader`,
  `build_illustration_gallery`, `build_knowledge_cards`,
  `build_sample_chapter`, `build_site_indices`); SHA-256 of all eleven
  committed artifacts (`docs/*.html`, the three JSON indices) is unchanged
  after the second run — byte-deterministic.
- Scriptless inventory: portal 0 scripts; each reader 3 progressive scripts
  with static station nav; gallery 1 progressive script with static plates
  and captions.
- Suites: `tests/test_site_accessibility.py` 12 passed,
  `tests/test_beginner_reader.py` 13 passed,
  `tests/test_product_tokens.py` 7 passed.

Verdict: GREEN. The three pages share one ink language, every measured
deviation was either fixed or is a pinned, declared choice, and the
generators reproduce their outputs byte for byte.

## 2026-11-07：重播遵守减少动效偏好

本轮画廊有 43 张源图、纸面与夜读共 86 个图版实例；前述 42 / 84 是先前审计时的清单，不是当前数量。

实际浏览器复现：系统减少动效开启后点击「重播全部」，仍有 1,923 个运行中动画。CSS 的 `animation:none` 不能阻止 JavaScript 创建的 Web Animations。现在重播入口检查同一媒体偏好；减少动效时禁用播放与速度按钮，图版标记 `aria-disabled`，保留完整静态图。运行中切换偏好会取消动画、清理墨点与延迟提示；恢复普通偏好后可以主动重播。

独立 Edge / Playwright 上下文实测：Enter 重播产生 1,936 个运行中动画，切换减少动效后为 0，恢复偏好后按钮重播有效；320 px 视口无横向溢出。禁用脚本后仍有 86 个完整图版与 4 个页脚链接。旧版复现与修复后检查构成本次运行时回归证据，未新增或修改永久测试与门禁策略。

本轮 Fast 八步通过：192 项通用测试、542 项构建器测试、333 张 Mermaid、15 章配置以及 11 个产物字节幂等。以上为手工命令证据；`task_verify` 基线不可用，不据此宣称受管验证通过。
