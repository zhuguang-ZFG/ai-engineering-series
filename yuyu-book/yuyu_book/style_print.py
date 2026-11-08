"""The print overlay and its page furniture."""
from __future__ import annotations

PRINT_CSS = r"""/* ------- print / PDF ------- */
@media print{
  /* #B4472F is mixed against the screen's warm paper; on a laser printer's
     pure white it burns straight through the earth palette, so paper re-inks
     the accent one step deeper before anything else is drawn. The ink scale
     follows: the mid grey that carries traces and rules on screen washes out
     on white, so paper pulls the whole charcoal scale one step deeper too. */
  :root{--paper:#FFFFFF;--card:#FFFFFF;--paper-2:#F6F0E2;--code-bg:#F8F4EA;
    --code-fg:#26221B;--code-line:#E3D8C1;--cinnabar:#9C4630;
    --bronze-2:#6E6353;--bronze-3:#4A4234}
  body{background:#fff;font-size:10.2pt;line-height:1.74;padding:0!important}
  body.lang-en{font-size:10pt;line-height:1.6}
  /* the A4 text block is ~665px, narrower than either measure: on paper the
     column is the page, so the cap must stand down for both languages */
  body,body.lang-en{--measure:52rem;--furniture:60rem}
  nav.rail,.no-print{display:none!important}
  .sheet{max-width:none;padding:0}
  /* on screen the cover is a card in the page flow; on paper the frame should
     be the page, so it takes the whole text block (297mm - 2x17mm margins).
     The stack is then spent from edge to edge -- kicker against the top of the
     frame, the author line against the bottom -- because a centred stack left
     a third of the sheet below the foot, which is the one place a cover may
     not be empty. */
  .front-page.cover{min-height:250mm;display:flex;align-items:stretch}
  .cover-inner{margin:0;width:100%;border:none;box-shadow:inset 0 0 0 1px var(--line-2),inset 0 0 0 5px var(--card),inset 0 0 0 5.5px var(--bronze-2),inset 0 0 0 6px var(--card);
    display:flex;flex-direction:column;justify-content:space-between}
  .diagram-frame,.codehilite,.table-scroll,.compass-card,.route-card,.illu-frame{
    box-shadow:none}
  /* the reading-paths page carries the routes, the offline note, the parts list
     and the tier legend; the legend is the one block that must not be split.
     Rows lose a few points of air so the legend stays on the page it starts on,
     instead of opening a sheet of its own three lines deep. */
  .route-parts li{padding:.3rem 0}
  .ip-notice-t{margin:1rem 0 .3rem}
  .tier-legend{break-inside:avoid;margin-top:.8rem;padding-top:.7rem}
  .tl-hint{font-size:.84rem;line-height:1.5;margin:0 0 .5rem}
  .tl-list{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));
    column-gap:1.5rem}
  .tl-row{border-bottom:none;padding:.1rem 0;gap:.5rem}
  /* the screen lets a wide table scroll; paper has no scrollbars, so headers
     wrap and long code tokens break to fit the page box. Both properties are
     chosen to keep whole words: `anywhere` also feeds min-content width, which
     let the layout squeeze a column narrower than "FileWriteTool" or "章节" and
     then split them mid-word — `break-word` breaks only what cannot fit.
     CJK breaks between any two characters by default, so headers get keep-all
     to stop "模块名称" setting as "模块名/称". */
  th{white-space:normal;word-break:keep-all;overflow-wrap:break-word}
  table{font-size:8.6pt}
  table td{overflow-wrap:break-word}
  /* the screen drops to one index column below 52rem, but the printed page box
     is 665px of a much taller sheet — two columns is the book convention and
     halves the index */
  .idx-cols{columns:2;column-gap:2.2rem}
  /* the folio slot: a screen has no pages, so the row hides its page reference;
     paper reserves the box here and the PDF pass writes the number into it —
     nothing in the HTML can know the page a row lands on */
  .idx-row .page-ref{display:block}
  /* the printed sheet is 665px of text box: a 7.5rem gutter for a two-character
     term would be a third of the line gone, so the gutter narrows with the page.
     6.4rem is where the longest single-word English term ("immutability") still
     sets on one line; past that only terms with a space in them wrap, which
     reads as a term rather than as a break. The 44rem collapse above is a screen
     rule the page box also matches — 665px is under 704px — so paper has to put
     the gutter and the row pins back. */
  .pr-row{grid-template-columns:6.4rem 1fr;column-gap:.7rem;padding:.28rem 0 .32rem}
  .pr-term{grid-column:1;grid-row:1}
  .pr-why{grid-column:2;grid-row:1}
  .pr-ana{grid-column:2;grid-row:2}
  .pr-unit{margin-bottom:1.25rem}
  /* there is no hover on paper: the mark stays as a quiet dotted underline,
     and the chapter panel — which the build keeps in step with the marks —
     carries the plain wording. Two columns halves its height. */
  .gloss{border-bottom:1px dotted var(--line-2);color:inherit;cursor:auto}
  .gloss-pop{display:none}
  .lead-band{break-inside:avoid;background:var(--card);
    box-shadow:none;border-color:var(--line-2)}
  /* the corner wheel is a screen flourish; on paper a clipped circle at the
     edge of a boxed band reads as a printing artefact */
  .lead-band::after{display:none}
  /* the compass is a three-column row on screen and collapses below 860px —
     which the printed text block (665px) always is, so without this every
     chapter opener spent three full-width boxes down the sheet for what is
     one line of text each. Three columns keeps the opener on one page. */
  .compass{grid-template-columns:repeat(3,minmax(0,1fr));gap:.5rem;
    margin-bottom:.95rem;break-inside:avoid}
  .compass-card{padding:.6rem .7rem .65rem}
  .cc-tag{font-size:.66rem;letter-spacing:.14em;margin-bottom:.24rem}
  .compass-card p{font-size:.84rem;line-height:1.62}
  .cc-src{gap:.26rem .3rem}
  .ch-emblem{width:2.4rem;height:2.4rem;opacity:1;color:var(--bronze-3)}
  /* the trace's screen colour is a light bronze at three-quarter opacity, which
     a laser printer drops out entirely; on paper it runs full ink */
  .ch-trace{width:min(15rem,100%);opacity:.9;color:var(--bronze-3)}
  /* the ruts must never fall onto a sheet of their own: glued to the block they
     close, the pair moves together and the page ends short instead of emptying.
     Chromium honours break-inside, not break-before:avoid. A chapter ends on
     the tail of its last page, so the mark has to be big enough to be the
     reason the page stops there rather than a stray that fell into the void. */
  .ch-close{break-inside:avoid}
  .ch-rut{width:min(19rem,82%);margin-top:1.6rem;opacity:.9;color:var(--bronze-3)}
  /* the keeper keeps the ink it has on paper; the hover lean simply stops */
  .keeper{break-inside:avoid;margin:.9rem 0 0}
  .kp-art svg{transition:none}
  .pd-route{width:min(20rem,100%);opacity:.95;color:var(--bronze-3)}
  /* the map is the one page a reader consults before choosing a route, so on
     paper it takes the full measure and its station numbers grow a point */
  .itinerary{width:100%;opacity:.95;color:var(--bronze-3)}
  .itinerary text{font-size:12px}
  .rmk{color:var(--bronze-3);opacity:1}
  /* the page has to stay on one sheet: the map is the point, and a list that
     spills to a second page would leave the road drawn but unread */
  .rm-lead{font-size:.95rem;margin:.3rem auto .8rem}
  .rm-key{font-size:.7rem;margin-bottom:1rem}
  .rm-legs{padding-top:.5rem;max-width:38rem}
  .rm-legs li{padding:.18rem 0;gap:.05rem;line-height:1.5}
  .rm-head a{font-size:.86rem}
  .rm-nos{font-size:.75rem}
  /* the one line that does not survive the sheet: with the goals kept, the page
     ran to 994px against a 926px block and the last leg fell onto its own
     sheet. Every part repeats its goal in large type on its own divider page,
     so paper trades the reminder for the road fitting on one page */
  .rm-why{display:none}
  .hr-rule{color:var(--bronze-3);break-inside:avoid;margin:1.25rem 0 1.35rem}
  /* the opener owns a whole page on paper: lift the plate to the head of the
     sheet and let it draw bigger than it does beside the sticky rail */
  .pd-inner{padding-top:1.6rem}
  .pd-art{width:min(15rem,58%);margin-bottom:.7rem}
  .pd-art img{width:100%;height:auto;display:block}
  /* the card is a plate, so it moves as one: allowed to break, its last row
     overflowed the text block by a point and Chromium handed the chapter an
     extra sheet carrying nothing at all — the one thing the empty-page gate
     exists to catch. Twenty-two terms are eleven rows at two columns, which
     is a third of a sheet and always fits on one. */
  .new-terms{break-inside:avoid}
  .nt-list{grid-template-columns:repeat(2,minmax(0,1fr))}
  .nt-term{font-size:.8rem}
  .nt-plain{font-size:.83rem;line-height:1.6}
  .sec-tier,.tier-chip{font-size:6.6pt;padding:0 .34rem}
  /* the plate's corner marks belong to the frame that no longer prints; the
     caption's flanking hairlines stay — with the box gone they are what holds
     each figure to the page. */
  .diagram-frame::before,.diagram-frame::after{display:none}
  .illu-photo .illu-frame::after{display:none}
  .illu-photo .illu-frame{background:none;border:0;border-radius:0;
    padding:0;overflow:visible}
  .part-divider{background:none}
  .pd-ghost{opacity:.12}
  .cover-seal{print-color-adjust:exact;-webkit-print-color-adjust:exact}
  .codehilite pre{white-space:pre-wrap;word-break:break-word}
  .codehilite .c,.codehilite .c1{color:#7A6F58}
  .codehilite .k{color:#7A5B22}.codehilite .s{color:#4F6B3A}
  .codehilite .m{color:#8A5A2B}.codehilite .nt{color:#3A5F80}
  h1{bookmark-level:1;bookmark-label:content()}
  .page-title,.pd-title{bookmark-level:1;bookmark-label:content()}
  article h2,article h3,article h4,.rev-v,.reg-kind,.idx-letter{
    bookmark-level:none;bookmark-label:none}
  h1,h2,h3{break-after:avoid}
  /* the article's screen padding is air between chapters; on paper it is a
     trap. The last line of ch04 (en) ended 15pt above the box edge, the 2.2rem
     of bottom padding did not fit, and Chromium kept a sheet alive just to
     paint it -- an empty page, because the next unit opens with a forced break.
     The page box's own margin is the air here. */
  article.chapter,article.unit{padding-bottom:0}
  /* two, not three: the fold-out plates already start their own sheet, and a
     three-line tail cost four pages and produced one fully blank sheet */
  p{orphans:2;widows:2}
  /* one link of a chapter's citation list landing alone at the head of a fresh
     sheet reads as a printing slip; the block is short enough to move whole */
  .chapter-notes{break-inside:avoid}
  figure.diagram,figure{break-inside:avoid;max-height:none}
  /* An A4 text column here is 257mm tall. A plate capped at 200mm needs 78% of
     it, so almost no page can host one and the figure jumps to the next sheet,
     leaving the hole behind it. 150mm still shows a full architecture diagram
     legibly while fitting any page that has half its column left -- which is
     how most of the 318 plates get to stay where the prose put them. */
  .diagram-frame svg{max-height:var(--plate-cap,150mm);width:auto!important;
    min-width:0!important}
  /* a wide band is bound by the column, not by the cap, so standing taller
     cannot save it — the sheet turns instead. Chromium honours named pages: the
     plate gets a landscape sheet of its own and the prose returns to portrait
     on the next one. No break-after: the page name already ends the sheet, and
     asking for both cost an empty landscape page after every fold-out. The
     sheet is 170mm tall, so the plate keeps the 150mm default and the caption
     fits under it instead of spilling onto a second sheet. */
  @page plate-landscape{size:A4 landscape;margin:21mm 17mm 19mm}
  figure.landscape{page:plate-landscape;break-before:page;
    display:flex;flex-direction:column;justify-content:center;min-height:150mm}
  figure.landscape figcaption{margin-top:1.2rem}
  /* A capped plate is narrower than the column, so a bordered frame would print
     as a wide empty box around a small drawing. Paper has no surface to lift off
     and no scrollbar to hint at, so the box stands down entirely: the drawing
     sits on the page, centred, and the caption rule beneath it does the framing.
     (Shrinking the frame instead is not an option — every plate's root element
     is `width="100%"`, which a shrink-to-fit container resolves to nothing.) */
  .diagram-frame{background:none;border:0;border-radius:0;padding:0;overflow:visible}
  .fig-hint{display:none}
  .part-divider{padding:40mm 0 35mm}
  /* the plate has to hold its ground on one sheet: 40/35mm of air plus the big
     numeral pushed the last entry of a four-item list onto the next sheet as a
     line of its own. Same look, ~20mm shorter, and nothing escapes. */
  .part-divider{padding:26mm 0 24mm}
  .pd-num{-webkit-text-stroke:1.6px var(--bronze-2)}
  tbody tr:nth-child(2n){background:transparent}
  a.ext::after{content:""}
  @page{size:A4;margin:21mm 17mm 19mm}
}
"""
