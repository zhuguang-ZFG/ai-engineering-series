"""Design tokens, screen/component rules and the print overlay, as texts.

``CSS`` is exactly the concatenation of the two pieces; the build inlines the
combined stylesheet into the single file.
"""
from __future__ import annotations

SCREEN_CSS = r"""
:root{
  --paper:#FBF7EF; --paper-2:#F3EAD8; --paper-3:#EADFC7;
  --card:#FFFDF8; --ink:#26221B; --ink-2:#5C5448; --ink-3:#675F4F;
  --line:#E3D8C1; --line-2:#D2C4A6;
  /* the drawing inks, transposed from the style library's C-32 charcoal:
     the old bronze fitting colours now hold the ink scale (浓墨/次墨/淡墨)
     so every hand-inked line — emblems, routes, ruts, seals — reads as the
     same charcoal stick, with cinnabar left as the only accent (C-15). */
  --bronze:#43392B; --bronze-2:#8A7D68; --bronze-3:#5A5040;
  --cinnabar:#B4472F; --jade:#4E6E5D; --sky:#4C7093;
  --code-bg:#211E19; --code-fg:#EDE6D6; --code-line:#3A352C;
  --serif:"Noto Serif SC","Source Han Serif SC","思源宋体","Songti SC",
          "SimSun",Georgia,"Times New Roman",serif;
  --kai:"Kaiti SC","STKaiti","KaiTi","楷体","AR PL KaitiM GB",var(--serif);
  --sans:"PingFang SC","Microsoft YaHei","Segoe UI",system-ui,-apple-system,sans-serif;
  --mono:"JetBrains Mono","Cascadia Code","SF Mono",Consolas,Menlo,monospace;
  --measure:46rem;   /* the prose column — ~43 CJK characters a line */
  --furniture:56rem; /* plates, tables, code and reference grids fill this */
  /* two corners and a circle: --r-1 turns a tag, --r-2 turns a box, and 999px
     is left to the things that really are pills (a scrollbar, a 3px rule).
     A fifth radius is a fifth book on the same sheet. Both are cut by hand:
     four unequal corners apiece, so every card, seal and chip reads as cut
     paper rather than stamped metal. */
  --r-1:5px 4px 6px 3px/3px 6px 4px 5px;
  --r-2:13px 8px 12px 8px/8px 12px 8px 13px;
}
/* Latin needs a shorter measure than CJK for the same comfort: 46rem of 17px
   Palatino is a 90-character line, which no one reads without losing the
   place. Both languages keep a small furniture/prose gap so the wide blocks
   are a step up, not a chasm. */
body.lang-en{--measure:37rem;--furniture:53rem}
@media (prefers-color-scheme:dark){
  body:not(.force-light){
    --paper:#181814; --paper-2:#22221C; --paper-3:#2B2A22;
    --card:#1E1D18; --ink:#E9E4D8; --ink-2:#BDB4A2; --ink-3:#A59C8A;
    --line:#37342A; --line-2:#4A4536;
    --bronze:#CFC6B4; --bronze-2:#A89E8C; --bronze-3:#E2DBCB;
    --cinnabar:#E07B5F; --jade:#9DBFA9; --sky:#8FB2D4;
    --code-bg:#12110D; --code-fg:#E4DDCC;
  }
  body:not(.force-light) .diagram-frame{background:#F5EFE2}
}
*{box-sizing:border-box}
@media (prefers-reduced-motion: no-preference){html{scroll-behavior:smooth}}
body{margin:0;background:var(--paper);color:var(--ink);
  font:400 17px/1.8 var(--serif);
  font-feature-settings:"kern";text-rendering:optimizeLegibility;
  -webkit-font-smoothing:antialiased}
body.lang-en{font-family:"Iowan Old Style",Palatino,Georgia,var(--serif);
  line-height:1.75;font-size:17px}
/* book blocks: flush both edges; CJK breaks strictly, Latin hyphenates */
.chapter-body p,.chapter-body li{text-align:justify}
body.lang-zh .chapter-body p,body.lang-zh .chapter-body li,
body.lang-zh .chapter-body blockquote{line-break:strict;border-inline-start:2.5px solid rgba(180,71,47,.3);padding-inline-start:.8rem}
body.lang-en .chapter-body p,body.lang-en .chapter-body li{hyphens:auto}
/* ragged-right beats a grid of gaps once the line is short enough that one
   unbreakable token costs the whole row its spacing -- see the contract test */
@media (max-width:30rem){body.lang-zh .chapter-body p,body.lang-zh .chapter-body li{text-align:left}}
::selection{background:rgba(180,71,47,.16)}
::selection-dark{background:rgba(224,123,95,.2)}
a{color:inherit}
a.ext::after{content:"↗";font-size:.72em;vertical-align:.15em;
  margin-inline:.12em .2em;color:var(--bronze);font-family:var(--sans)}
a.xref{color:var(--bronze-3);text-decoration:none;
  border-bottom:1px dotted var(--bronze-2)}
a.xref:hover{color:var(--cinnabar);border-bottom-color:var(--cinnabar)}
h1,h2,h3,h4{font-family:var(--sans);font-weight:700;line-height:1.35;
  color:var(--ink);letter-spacing:.01em}

/* ------- shell & rail ------- */
.sheet{max-width:calc(var(--measure) + 4rem);margin:0 auto;padding:0 2rem}
/* A wide screen splits the column in two widths — see the reading-column rule
   at the end of this sheet, which has to come last because every component
   below sets its own `margin` shorthand. */
nav.rail{display:none;position:fixed;inset:0 auto 0 0;width:17rem;
  overflow-y:auto;background:var(--paper-2);border-right:1px solid var(--line);
  padding:1.6rem 1.1rem 3rem;font-family:var(--sans);font-size:.82rem;
  scrollbar-width:thin}
/* the wide-screen block has to come after the base rule above: `nav.rail` and
   `nav.rail` are equally specific, so a media query written first simply loses
   and the reader gets the reserved gutter with no rail in it */
@media (min-width:1360px){
  body{padding-left:17.5rem}
  .sheet{max-width:var(--furniture)}
  nav.rail{display:block}
}
nav.rail .rail-title{font-size:.72rem;letter-spacing:.35em;color:var(--bronze);
  text-transform:uppercase;margin:0 0 1rem;display:flex;gap:.5rem;align-items:center}
nav.rail .rail-part{margin:.95rem 0 .25rem;font-weight:700;color:var(--bronze-3);
  font-size:.78rem;letter-spacing:.08em}
nav.rail a{display:block;color:var(--ink-2);text-decoration:none;
  padding:.16rem .5rem;border-left:2px solid transparent;line-height:1.5}
nav.rail a:hover{color:var(--cinnabar);border-left-color:var(--cinnabar);
  background:var(--paper)}
/* the rail's only non-chapter link, wearing the same wheel the route map
   starts with, so the sidebar and the page it jumps to share one sign */
nav.rail .rail-map{display:flex;align-items:center;gap:.45rem;
  color:var(--bronze-3);font-weight:600;margin-bottom:.5rem}
nav.rail .rail-map .rmk{flex:none;width:.8rem;height:.8rem;color:var(--bronze)}

/* ------- structure pages ------- */
.front-page{padding:2.3rem 0 1.8rem}
.page-title{font-size:1.9rem;margin:0 0 1.05rem;color:var(--bronze-3)}
.page-title::after{content:"";display:block;width:3.6rem;height:3px;
  background:linear-gradient(90deg,var(--bronze),var(--bronze-2));
  margin-top:.55rem;border-radius:999px}
section.front-page{break-before:page}
.cover{text-align:center;padding:0;position:relative}
.cover .wheel{width:26px;height:26px;color:var(--bronze-2);opacity:.9;flex:0 0 auto}
/* one frame, not two: the outline used to draw a second line 5px outside the
   border, which at book size reads as a plate that printed twice */
.cover-inner{position:relative;display:inline-block;text-align:center;
  padding:clamp(2.2rem,5vw,4rem) clamp(1.6rem,5vw,4.2rem) 2.6rem;margin:2.4rem 0;
  border:none;
  background:linear-gradient(180deg,var(--card),var(--paper));
  box-shadow:inset 0 0 0 1px var(--line-2),inset 0 0 0 4px var(--card),
             inset 0 0 0 5.5px var(--bronze-2),inset 0 0 0 6.5px var(--card);
}
.cover-inner::before{content:"";position:absolute;top:0;bottom:0;left:0;
  width:5px;background:linear-gradient(180deg,var(--cinnabar),var(--bronze-2));
  border-radius:0}
.cover-inner::after{content:"";position:absolute;top:0;bottom:0;right:0;
  width:2px;background:linear-gradient(180deg,rgba(180,71,47,.15),rgba(67,57,43,.1));
  pointer-events:none}
.cover-kicker{font-family:var(--sans);font-size:.7rem;letter-spacing:.42em;
  color:var(--bronze);text-transform:uppercase;margin:0 0 1.6rem}
.book-title{margin:0;line-height:1.12;font-weight:750;letter-spacing:.06em}
.bt-main{display:block;font-size:clamp(3.1rem,9vw,4.9rem);letter-spacing:.14em;
  text-indent:.14em;color:var(--ink);font-weight:700;
  font-family:"STSong","Songti SC","Noto Serif SC",var(--serif)}
.bt-tail{display:block;font-family:var(--sans);font-weight:400;font-size:1.2rem;
  letter-spacing:.3em;text-indent:.3em;color:var(--ink-2);margin-top:.9rem}
.cover-seal{position:absolute;top:clamp(1.4rem,4vw,2.6rem);
  right:clamp(1.4rem,4vw,2.6rem);display:flex;flex-direction:column;
  align-items:center;justify-content:center;gap:.05rem;width:2.9rem;
  padding:.42rem 0;background:var(--cinnabar);color:#FBF7EF;
  font-family:var(--kai);font-size:1.05rem;line-height:1.15;letter-spacing:0;
  writing-mode:vertical-rl;border-radius:var(--r-1);transform:rotate(1.8deg);
  box-shadow:inset 0 0 0 2px rgba(251,247,239,.55)}
.cover-rule{display:flex;align-items:center;justify-content:center;gap:.9rem;
  margin:1.7rem auto 1.2rem;max-width:26rem}
.cover-rule i{height:1px;flex:1;background:linear-gradient(90deg,transparent,
  var(--bronze-2),transparent)}
.cover-art{width:min(34rem,94%);display:block;margin:.5rem auto 1.6rem;
  color:var(--ink-2)}
.book-sub{font-family:var(--sans);font-size:.95rem;color:var(--ink-2);
  margin:0 0 1.8rem;letter-spacing:.1em}
.book-epi{font-family:var(--kai);font-size:1.02rem;color:var(--bronze-3);
  margin:0 auto 1.9rem;line-height:2}
.book-epi .epi-src{display:block;font-size:.86rem;color:var(--ink-3);margin-top:.2rem}
.cover-foot{display:flex;align-items:baseline;justify-content:center;gap:.9rem;
  border-top:1px solid var(--line);padding-top:1.1rem}
.book-author{font-family:var(--sans);letter-spacing:.28em;text-indent:.28em;
  color:var(--ink);font-size:.95rem;font-weight:700}
.cover-ver{font-family:var(--sans);font-size:.76rem;letter-spacing:.12em;
  color:var(--ink-3)}
.cover-ver b{color:var(--cinnabar);font-weight:700}
.cover-tag{font-family:var(--sans);font-size:.74rem;letter-spacing:.36em;
  color:var(--bronze);text-transform:uppercase;margin:0 0 2.2rem}
.imprint-list{margin:0 0 1.6rem}
.ip-row{display:grid;grid-template-columns:8.5rem 1fr;gap:1rem;padding:.5rem 0;
  border-bottom:1px solid var(--line)}
.ip-row dt{font-family:var(--sans);font-size:.8rem;letter-spacing:.2em;
  color:var(--bronze);margin:0}
.ip-row dd{margin:0}
.ip-notice-t{margin:1.4rem 0 .4rem;font-size:.95rem;color:var(--cinnabar)}
.ip-notice{color:var(--ink-2);font-size:.95rem;border-left:3px solid var(--line-2);
  padding-left:1rem}
.rev-v{display:flex;justify-content:space-between;align-items:baseline;
  font-size:1.05rem;margin:1.15rem 0 .3rem;color:var(--bronze-3)}
.rev-v .rev-d{font-size:.78rem;color:var(--ink-3);font-weight:400}
.revisions ul{margin:.2rem 0 0;padding-left:1.4rem;font-size:.96rem;color:var(--ink-2);
  list-style-type:none}
ul>li{position:relative}
ul>li::before{content:"◆";position:absolute;left:-1.15em;top:0;
  font-size:.55em;color:var(--bronze-2);line-height:2.8}
.revisions li::marker{color:var(--bronze-2)}
/* four routes, one row: at 15rem the sheet broke 3+1 and the orphan card left
   two empty cells the reader scans as missing content */
.route-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(12.5rem,1fr));
  gap:.9rem;margin:1.1rem 0 1.6rem}
/* four routes never divide into a three-up row. Rather than leave the last
   row two-thirds empty, the fourth card takes the whole line and reads as the
   closing note it is */
.route-grid>:last-child:nth-child(4){grid-column:1/-1}
.route-card{background:var(--card);border:1px solid var(--line);border-radius:var(--r-2);
  padding:1rem 1.15rem;box-shadow:0 1px 4px rgba(38,34,27,.05)}
.route-card h3{margin:0 0 .35rem;font-size:.92rem;color:var(--cinnabar);
  letter-spacing:.05em}
.route-card p{margin:0;font-size:.95rem;color:var(--ink-2)}
/* the route map is its own leaf, not furniture on the reading-paths sheet:
   that page already carries the routes, the offline note, the parts list and
   the legend, and print has no room to spare for a second block that must not
   split. Here the map is the page, so it gets `break-inside:avoid` outright. */
.itinerary{display:block;width:min(46rem,100%);height:auto;break-inside:avoid;
  margin:.2rem auto 1.1rem;color:var(--bronze);opacity:.92}
.itinerary text{font-family:var(--sans);font-size:11px;fill:currentColor;
  stroke:none;letter-spacing:.02em}
.rm-lead{max-width:36rem;margin:.45rem auto 1.35rem;text-align:center;
  color:var(--ink-2);font-size:1.02rem}
/* the legend is read once and never looked at again, so it stays small, in the
   sans, and directly under the map it explains */
.rm-key{display:flex;flex-wrap:wrap;justify-content:center;gap:.35rem 1.5rem;
  list-style:none;margin:0 auto 1.6rem;padding:0;max-width:44rem;
  font-family:var(--sans);font-size:.76rem;letter-spacing:.02em;color:var(--ink-3)}
.rm-key li{display:flex;align-items:center;gap:.42rem}
.rmk{flex:none;width:1.05rem;height:1.05rem;color:var(--bronze)}
.rm-legs{list-style:none;margin:0 auto;padding:.85rem 0 0;max-width:34rem;
  border-top:1px solid var(--line)}
.rm-legs li{display:flex;flex-direction:column;gap:.15rem;padding:.42rem 0;
  border-bottom:1px solid var(--line);line-height:1.62}
.rm-legs li:last-child{border-bottom:0}
/* the two lines of a row are furniture text, not prose: the browser's own
   paragraph margins would otherwise spend more sheet than the sentences do */
.rm-legs p{margin:0}
.rm-head{display:flex;flex-wrap:wrap;align-items:baseline;gap:.15rem .6rem}
.rm-head a{font-family:var(--sans);font-weight:700;color:var(--bronze-3)}
.rm-nos{font-family:var(--sans);font-size:.8rem;color:var(--cinnabar);
  letter-spacing:.08em}
.rm-why{color:var(--ink-2);font-size:.92rem}
.route-parts{list-style:none;margin:0;padding:0}
.route-parts li{padding:.55rem 0;border-bottom:1px solid var(--line);
  display:flex;flex-direction:column;gap:.15rem}
.route-parts a{font-family:var(--sans);font-weight:700;color:var(--bronze-3);
  text-decoration:none}
.route-goal{font-size:.9rem;color:var(--ink-3)}

/* ------- TOC ------- */
.toc-part{display:flex;align-items:baseline;gap:.85rem;margin:1.6rem 0 .5rem;
  font-family:var(--sans);font-weight:700;font-size:.85rem;letter-spacing:.2em;
  color:var(--bronze);text-decoration:none}
.toc-part:hover .tp-tx,.toc-part:hover .tp-no{color:var(--cinnabar)}
.toc-part::after{content:"";flex:1;height:1px;background:var(--line-2);
  transform:translateY(-.32em);order:2}
.toc-part .page-ref{order:3}
/* the numeral is inked, not outlined: a hollow 1.9rem Ⅰ is the loudest mark on
   the contents page and, being empty inside, reads as a plate that failed to
   take ink */
.tp-no{font-family:var(--serif);font-size:1.15rem;font-weight:700;
  line-height:1;color:var(--bronze);letter-spacing:.06em}
.tp-tx{color:var(--bronze-3)}
.toc-part-plain{color:var(--cinnabar);margin-top:2.4rem}
.toc-hr{border:none;border-top:1px solid var(--line);margin:1.2rem 0}
.toc-group{break-inside:avoid}
.toc-row{display:flex;align-items:baseline;text-decoration:none;color:var(--ink);
  padding:.32rem 0 .3rem;font-size:.99rem;border-radius:var(--r-1)}
.toc-row:hover{color:var(--cinnabar)}
.toc-row:hover{transform:translateX(3px)}
.toc-row{transition:transform .16s ease,color .16s ease}
.toc-row:hover .toc-n{color:var(--cinnabar);border-color:var(--cinnabar)}
.toc-n{flex:0 0 auto;min-width:2.1rem;margin-inline-end:.75rem;text-align:center;
  font-family:var(--sans);font-size:.7rem;font-weight:700;color:var(--bronze-3);
  border:1px solid var(--line-2);border-radius:var(--r-1);padding:.1rem .2rem;
  transform:translateY(-.12em)}
.toc-t{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
/* the leader carries the eye from a title to its folio, so it is drawn in the
   ornament gold rather than in the rule grey it kept getting lost in */
.leader{flex:1;border-bottom:1px dotted var(--bronze-2);margin:0 .5rem;
  transform:translateY(-.28em)}
.page-ref{font-family:var(--sans);font-size:.86rem;color:var(--bronze-3);
  font-variant-numeric:tabular-nums;min-width:1.6rem;
  text-align:right}

/* ------- part dividers ------- */
.part-divider{position:relative;overflow:hidden;text-align:center;
  padding:clamp(2.4rem,6vw,4rem) 1rem clamp(2rem,5vw,3.2rem);
  break-before:page;break-after:page;
  background:
    radial-gradient(120% 90% at 50% 0%,var(--paper-2) 0%,transparent 62%),
    linear-gradient(180deg,transparent,rgba(200,164,92,.06))}
.part-divider::before,.part-divider::after{content:"";position:absolute;
  left:50%;transform:translateX(-50%);width:min(70%,44rem);
  border-top:1px solid var(--line-2)}
.part-divider::before{top:1.4rem}
.part-divider::after{bottom:1.4rem}
/* the ghost wheel bleeds off one corner instead of sitting behind the plate:
   concentric wheels would double the rim, an off-centre arc gives the page a
   second, larger drawing to rest against */
.pd-ghost{position:absolute;right:-14%;top:-9%;width:min(360px,58vw);
  color:var(--bronze-2);opacity:.11;pointer-events:none;user-select:none}
.pd-ghost svg{width:100%;height:auto;display:block}
.pd-inner{position:relative;max-width:38rem;margin:0 auto;padding-top:clamp(3.4rem,8vw,5rem)}
/* the part's own drawing sits over the faint wheel: crisp line on ghosted
   line, the same depth the cover plate gets. Everything here is inked in
   currentColor, so dark mode and paper re-ink the drawing on their own. */
.pd-art{width:min(13.5rem,62%);margin:0 auto 1.1rem;color:var(--bronze);opacity:.9}
.pd-art svg{width:100%;height:auto;display:block}
.pd-no{font-family:var(--sans);letter-spacing:.5em;text-indent:.5em;
  color:var(--bronze);font-size:.85rem;margin:0 0 .5rem}
.pd-title{font-size:clamp(2rem,5.5vw,2.7rem);margin:0;letter-spacing:.08em}
.pd-motto{font-family:var(--kai);color:var(--cinnabar);margin:.2rem 0 1.3rem;
  letter-spacing:.14em;font-size:1.02rem}
.pd-goal{max-width:30rem;margin:0 auto;color:var(--ink-2);font-size:.98rem;
  line-height:1.9;text-wrap:balance}
/* the leg's road, drawn once above the stop list: the reader sees how many
   chapters the part is before reading a single one of their titles */
.pd-route{display:block;width:min(23rem,92%);height:auto;margin:1.55rem auto .1rem;
  color:var(--bronze);opacity:.85}
.pd-list{list-style:none;margin:1.1rem auto 0;padding:.9rem 0 0;max-width:26rem;
  text-align:start;border-top:1px solid var(--line-2)}
.pd-list li{padding:.42rem 0;border-bottom:1px solid var(--line)}
.pd-list a{text-decoration:none;color:var(--ink-2);font-size:.95rem;
  display:flex;gap:.7rem;align-items:baseline}
.pd-list a:hover{color:var(--cinnabar)}
.pd-list a::before{content:attr(data-no);
  font-family:var(--sans);font-size:.74rem;color:var(--bronze);
  font-variant-numeric:tabular-nums;flex:0 0 auto}

/* ------- chapters ------- */
article.chapter,article.unit{padding:1.7rem 0 2.2rem;break-before:page;
  overflow-wrap:break-word}
.chapter-head .eyebrow{font-family:var(--sans);font-size:.78rem;
  letter-spacing:.3em;color:var(--bronze);text-transform:uppercase;
  margin:0 0 .3rem;display:flex;align-items:center;gap:.7rem}
.chapter-head .eyebrow::after{content:"";flex:1;height:1px;
  background:linear-gradient(90deg,var(--line-2),transparent)}
article h1{font-size:1.85rem;margin:.15rem 0 1.05rem;line-height:1.4}
.ch-head-row{display:flex;align-items:flex-start;gap:1.05rem}
.ch-seal{flex:0 0 auto;display:grid;place-items:center;width:3.05rem;height:3.05rem;
  margin-top:.25rem;border:2px solid var(--cinnabar);border-radius:var(--r-1);
  color:var(--cinnabar);background:var(--card);
  transform:rotate(-1.7deg);
  font-family:Georgia,var(--sans);font-weight:700;font-size:1.32rem;
  letter-spacing:.02em;font-variant-numeric:tabular-nums;
  box-shadow:inset 0 0 0 1px rgba(180,71,47,.16)}
.ch-head-row h1{margin-bottom:1.05rem}
.appendix .ch-seal{border-color:var(--cinnabar);color:var(--cinnabar)}
/* the unit emblem: drawn with currentColor so it re-inks itself in dark mode
   and on paper, and floats into the head row rather than eating a block of
   vertical space the way a full-width figure would */
.ch-emblem{flex:0 0 auto;align-self:center;margin-inline-start:auto;
  width:4.6rem;height:4.6rem;color:var(--bronze);opacity:.92}
.ch-emblem svg{width:100%;height:100%;display:block}
.appendix .ch-emblem{color:var(--cinnabar);opacity:.8}
@media (max-width:44rem){.ch-emblem{width:3.2rem;height:3.2rem}}
/* the ink draws itself as a unit scrolls into view. Triple-guarded so the
   drawing can never half-exist where motion cannot run: print/PDF (screen
   only), reduced-motion readers, and browsers without scroll-driven
   animations all fall through to the fully inked static drawing. The
   animation targets only shapes carrying pathLength="100" — dashed strokes
   keep their real-unit dash rhythm and fade instead, and ink dots pop. */
@media screen and (prefers-reduced-motion: no-preference) {
  @supports (animation-timeline: view()) {
    .ch-emblem path[pathLength],.ch-emblem circle[pathLength],
    .kp-art path[pathLength],.kp-art circle[pathLength],
    .pd-art path[pathLength],.pd-art circle[pathLength],
    .cover-art path[pathLength],.cover-art circle[pathLength],
    .ch-trace path[pathLength],.ch-trace circle[pathLength],
    .pd-route path[pathLength],.pd-route circle[pathLength],
    .illu-frame path[pathLength],.illu-frame circle[pathLength],
    .itinerary path[pathLength],.itinerary circle[pathLength]{
      stroke-dasharray:100 100;
      animation:ink-draw 1.2s ease-out both;
      animation-timeline:view();
      animation-range:cover 0% cover 60%}
    .ch-emblem [stroke-dasharray],.kp-art [stroke-dasharray],
    .pd-art [stroke-dasharray],.cover-art [stroke-dasharray],
    .illu-frame [stroke-dasharray],
    .itinerary [stroke-dasharray]{
      animation:ink-fade 1s ease-out both;
      animation-timeline:view();
      animation-range:cover 0% cover 55%}
    .ch-emblem [fill="currentColor"],.kp-art [fill="currentColor"],
    .pd-art [fill="currentColor"],.cover-art [fill="currentColor"],
    .ch-trace [fill="currentColor"],.pd-route [fill="currentColor"],
    .illu-frame [fill="currentColor"],
    .itinerary [fill="currentColor"]{
      transform-box:fill-box;transform-origin:center;
      animation:ink-pop .7s cubic-bezier(.2,1.4,.4,1) both;
      animation-timeline:view();
      animation-range:cover 8% cover 62%}
    .ch-rut,.hr-knot,.ink-mark,.rmk{
      animation:ink-fade 1s ease-out both;
      animation-timeline:view();
      animation-range:cover 0% cover 55%}
    /* a sequential plate carries its story in frames. Each group fades in on
       its own slice of the scroll, so the mechanism visibly moves instead of
       arriving as one frozen last frame; the strokes inside still ink
       themselves. Print and reduced-motion lose the stagger and keep every
       frame drawn — the strip still reads in order, which is the point. */
    .illu-seq .frame{animation:ink-fade 1s ease-out both;
      animation-timeline:view()}
    .illu-seq .frame:nth-child(1){animation-range:cover 0% cover 26%}
    .illu-seq .frame:nth-child(2){animation-range:cover 10% cover 40%}
    .illu-seq .frame:nth-child(3){animation-range:cover 22% cover 54%}
    .illu-seq .frame:nth-child(4){animation-range:cover 34% cover 68%}
    .illu-seq .frame:nth-child(5){animation-range:cover 46% cover 80%}
    .illu-seq .frame:nth-child(6){animation-range:cover 58% cover 92%}
    /* hovering runs the strip: one frame lit at a time, walking left to right.
       The scroll range is dropped for a plain clock, and the strokes stay
       inked, so only the light moves. */
    .illu-seq:hover .frame{animation:ink-cycle 2.8s linear infinite both;
      animation-timeline:auto;animation-range:normal}
    .illu-seq:hover .frame:nth-child(2){animation-delay:.7s}
    .illu-seq:hover .frame:nth-child(3){animation-delay:1.4s}
    .illu-seq:hover .frame:nth-child(4){animation-delay:2.1s}
    .illu-seq:hover .frame:nth-child(5){animation-delay:2.8s}
    .illu-seq:hover .frame:nth-child(6){animation-delay:3.5s}
    /* character: hovering wakes a drawing up. Spring easings, squash and
       stretch — the twelve-principles vocabulary in three-line keyframes.
       Each figure carries its pivot in a class, so one verb per drawing. */
    .a-compass:hover .spin{animation:ink-spin-c 26s linear infinite}
    .a-chase .spin{transform-box:view-box;transform-origin:32px 32px}
    .a-chase:hover .spin{animation:ink-spin 7s linear infinite}
    .a-nut .wiggle{transform-box:view-box;transform-origin:32px 32px}
    .a-nut:hover .wiggle{animation:ink-wiggle 1s cubic-bezier(.36,.07,.19,.97) infinite alternate}
    .a-gauge .sweep{transform-box:view-box;transform-origin:32px 44px}
    .a-gauge:hover .sweep{animation:ink-sweep 1.5s ease-in-out infinite alternate}
    .a-hook .nudge{transform-box:fill-box;transform-origin:center}
    .a-hook:hover .nudge{animation:ink-nudge .7s cubic-bezier(.36,.07,.19,.97) infinite alternate}
    .a-hub .pulse{transform-box:fill-box;transform-origin:center}
    .a-hub:hover .pulse{animation:ink-pulse 1.1s cubic-bezier(.34,1.56,.64,1) infinite}
    .a-wire .sway{transform-box:view-box;transform-origin:32px 14px}
    .a-wire:hover .sway{animation:ink-sway 1.7s ease-in-out infinite alternate}
    .a-funnel .drip{transform-box:fill-box;transform-origin:center}
    .a-funnel:hover .drip{animation:ink-drip 1s cubic-bezier(.55,0,1,.45) infinite}
    .a-flag .wave{transform-box:view-box;transform-origin:47px 12px}
    .a-flag:hover .wave{animation:ink-wave 1.3s ease-in-out infinite alternate}
    .a-toggle .knob{transform-box:fill-box;transform-origin:center}
    .a-toggle:hover .knob{animation:ink-toggle 1s cubic-bezier(.34,1.56,.64,1) infinite alternate}
    .a-keeper .swing{transform-box:view-box;transform-origin:45.2px 39.3px}
    /* row-level trigger: the hop moves the drawing itself, so hovering the
       small svg directly would push it out from under the cursor and flicker */
    .keeper:hover .a-keeper .swing,.keeper:focus-within .a-keeper .swing{
      animation:ink-swing 1.5s ease-in-out infinite alternate}
    .keeper:hover .a-keeper,.keeper:focus-within .a-keeper{
      animation:ink-hop .9s cubic-bezier(.36,.07,.19,.97) infinite alternate}
    /* the chariot rides as the reader does: wheels roll, the team bobs */
    .cover-art .roll{transform-box:view-box;transform-origin:668px 336px;
      animation:ink-roll 1.1s linear both;animation-timeline:view();
      animation-range:cover 0% cover 85%}
    .cover-art .bob{animation:ink-bob 1.3s ease-in-out both;
      animation-timeline:view();animation-range:cover 0% cover 70%}
    .pd-art .turn{transform-box:view-box;transform-origin:100px 64px;
      animation:ink-turn 1.2s ease-out both;animation-timeline:view();
      animation-range:cover 0% cover 70%}
    /* and the roads walk: a dashed route marches one period at a time, so
       the 驿路 itself travels under the reader's eye */
    .a-front:hover .m75{animation:ink-march-75 1s linear infinite}
    .a-flag:hover .m92{animation:ink-march-92 1.1s linear infinite}
    .a-path:hover .m80{animation:ink-march-80 1.05s linear infinite}
    .itinerary .m110{animation:ink-march-110 1.3s linear infinite}
    .a-gate:hover .redraw{animation:ink-redraw 1.1s ease-out infinite}
    .a-memo:hover .write{animation:ink-redraw 1.3s ease-out infinite}
    .a-list:hover .tick{animation:ink-redraw .8s ease-out infinite}
    .a-list:hover .t2{animation-delay:.15s}
    .a-list:hover .t3{animation-delay:.3s}
    .a-stack .ripple{transform-box:fill-box;transform-origin:center}
    .a-stack:hover .d1{animation:ink-ripple .9s ease-out infinite}
    .a-stack:hover .d2{animation:ink-ripple .9s ease-out .15s infinite}
    .a-fork .pulse,.a-locate .pulse{transform-box:fill-box;transform-origin:center}
    .a-fork:hover .pulse{animation:ink-pulse 1s cubic-bezier(.34,1.56,.64,1) infinite}
    .a-locate:hover .pulse{animation:ink-pulse 1.2s cubic-bezier(.34,1.56,.64,1) infinite}
    .a-plug:hover .blink{animation:ink-blink 1.1s linear infinite}
    .a-plug:hover .b2{animation-delay:.55s}
    .a-gloss .flutter{transform-box:fill-box;transform-origin:50% 0%}
    .a-gloss:hover .f1{animation:ink-flutter .8s ease-in-out infinite alternate}
    .a-gloss:hover .f2{animation:ink-flutter .8s ease-in-out .2s infinite alternate}
    /* text rises the way the drawings land: headings, callouts and cards
       settle onto the sheet as the reader reaches them */
    .ch-head-row h1,.h1-sub,.page-title,
    .chapter-body h2,.chapter-body h3,
    .callout,.lead-band,.compass-card,.route-card,.keeper-note,.new-terms,
    .pd-title,.pd-motto,.pd-goal,.rm-head,.pd-list li,
    .diagram-frame,.fig-cap{
      animation:ink-rise .9s cubic-bezier(.22,.9,.3,1) both;
      animation-timeline:view();
      animation-range:cover 0% cover 42%}
    /* the ghost wheel behind a part divider slowly turns as the reader rides */
    .pd-ghost svg{transform-box:view-box;transform-origin:100px 100px;
      animation:ink-ghost 1.6s ease-out both;animation-timeline:view();
      animation-range:cover 0% cover 80%}
  }
  /* load- and hover-driven text motion needs no scroll timeline, only the
     reduced-motion hand */
  .front-page.cover .cover-kicker{animation:ink-rise .7s ease-out both}
  .front-page.cover .book-title{animation:ink-rise .8s ease-out .12s both}
  .front-page.cover .book-sub{animation:ink-rise .8s ease-out .24s both}
  .front-page.cover .book-epi{animation:ink-rise .8s ease-out .36s both}
  .front-page.cover .cover-foot{animation:ink-rise .8s ease-out .48s both}
  .gloss:hover .gloss-pop,.gloss:focus .gloss-pop,
  .gloss:focus-within .gloss-pop{
    animation:ink-gloss .32s cubic-bezier(.34,1.56,.64,1)}
  .source-chip,.tier-chip{transition:transform .16s ease,box-shadow .16s ease}
  .source-chip:hover,.tier-chip:hover{transform:translateY(-1.5px);
    box-shadow:0 3px 8px rgba(38,34,27,.14)}
  .toc-row{transition:transform .18s ease}
  .toc-row:hover{transform:translateX(3px)}
  /* the compass ring keeps its hand-set phase even where motion is off */
  .a-compass .spin{transform:rotate(9deg);transform-box:view-box;
    transform-origin:32px 32px}
}
@keyframes ink-draw{from{stroke-dashoffset:100}}
@keyframes ink-fade{from{opacity:0}}
@keyframes ink-cycle{0%,100%{opacity:.26}12%,30%{opacity:1}}
@keyframes ink-pop{0%{transform:scale(0)}60%{transform:scale(1.25,.75)}
  80%{transform:scale(.92,1.12)}100%{transform:scale(1)}}
@keyframes ink-spin{to{transform:rotate(360deg)}}
@keyframes ink-spin-c{from{transform:rotate(9deg)}to{transform:rotate(369deg)}}
@keyframes ink-wiggle{from{transform:rotate(-7deg)}to{transform:rotate(7deg)}}
@keyframes ink-sweep{from{transform:rotate(-12deg)}to{transform:rotate(14deg)}}
@keyframes ink-nudge{from{transform:translateX(0)}to{transform:translateX(3px)}}
@keyframes ink-pulse{0%{transform:scale(1)}45%{transform:scale(1.3)}100%{transform:scale(1)}}
@keyframes ink-sway{from{transform:rotate(-1.4deg)}to{transform:rotate(1.4deg)}}
@keyframes ink-drip{0%{transform:translateY(0);opacity:.55}
  70%{opacity:.55}100%{transform:translateY(6px);opacity:0}}
@keyframes ink-wave{from{transform:rotate(-4deg)}to{transform:rotate(5deg)}}
@keyframes ink-toggle{0%{transform:translateX(0)}55%{transform:translateX(-25px)}
  75%{transform:translateX(-19px)}100%{transform:translateX(-21px)}}
@keyframes ink-swing{from{transform:rotate(-10deg)}to{transform:rotate(10deg)}}
@keyframes ink-hop{from{transform:translateY(0)}to{transform:translateY(-2px)}}
@keyframes ink-roll{to{transform:rotate(-160deg)}}
@keyframes ink-bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-3px)}}
@keyframes ink-turn{to{transform:rotate(45deg)}}
@keyframes ink-march-75{to{stroke-dashoffset:-7.5}}
@keyframes ink-march-92{to{stroke-dashoffset:-9.2}}
@keyframes ink-march-80{to{stroke-dashoffset:-8}}
@keyframes ink-march-110{to{stroke-dashoffset:-11}}
@keyframes ink-redraw{from{stroke-dashoffset:100}to{stroke-dashoffset:0}}
@keyframes ink-ripple{0%{transform:translateY(0)}
  55%{transform:translateY(2.5px)}100%{transform:translateY(0)}}
@keyframes ink-blink{0%,45%{opacity:1}50%,95%{opacity:.12}100%{opacity:1}}
@keyframes ink-flutter{from{transform:rotate(-5deg)}to{transform:rotate(6deg)}}
@keyframes ink-rise{from{opacity:0;transform:translateY(12px)}}
@keyframes ink-gloss{from{opacity:0;transform:translate(-50%,.5rem) scale(.9)}
  to{opacity:1;transform:translate(-50%,0) scale(1)}}
@keyframes ink-ghost{to{transform:rotate(26deg)}}
/* the wire the head closes on — a drawn line with pads, not a ruled one.
   Inline SVG, so it inherits currentColor like every other drawing here. */
.ch-trace{display:block;width:min(21rem,100%);height:auto;
  margin:-.15rem 0 .35rem;color:var(--bronze-2);opacity:.75}
.appendix .ch-trace{color:var(--cinnabar);opacity:.5}
/* and the ruts it ends on: a drawn full stop for the chapter, so the tail of
   the page closes on something the book inked rather than on blank paper */
.ch-rut{display:block;width:min(17rem,74%);height:auto;break-before:avoid;
  margin:2.1rem auto .15rem;color:var(--bronze);opacity:.8}
.appendix .ch-rut{color:var(--cinnabar);opacity:.62}
article h1 .h1-sub{display:block;font-weight:400;font-size:1.05rem;
  color:var(--ink-3);margin-top:.35rem;font-family:var(--serif)}
article h2{font-size:1.28rem;margin:1.9rem 0 .7rem;padding-left:.7rem;
  border-left:3.5px solid var(--cinnabar)}
article h3{font-size:1.06rem;margin:1.4rem 0 .45rem;color:var(--bronze-3)}
article h4{font-size:.95rem;margin:1.05rem 0 .35rem;color:var(--ink-2)}
article h2 .sec-no{color:var(--bronze);margin-right:.45rem;font-variant-numeric:tabular-nums}
article p{margin:0 0 1.05em}
article .chapter-body>p:first-of-type::first-letter{
  font-size:2.9em;line-height:.86;float:inline-start;padding:.08em .12em 0 0;
  color:var(--cinnabar);font-weight:700;font-family:var(--serif)}
ul,ol{padding-inline-start:1.6em;margin:0 0 1em}
li{margin:.24em 0}
li::marker{color:var(--bronze);font-family:var(--sans);font-size:.9em}
hr{border:none;text-align:center;margin:1.8rem 0}
/* the section break: hairline, drawn coupling, hairline. The coupling is an
   inline SVG rather than a typed glyph, so it re-inks in dark mode and on
   paper exactly like the emblems do. */
.hr-rule{display:flex;align-items:center;gap:.8rem;margin:1.7rem 0 1.8rem;
  color:var(--bronze-2)}
.hr-rule::before,.hr-rule::after{content:"";flex:1;height:1px;
  background:var(--line-2)}
/* plain 1px lines, not gradients: a gradient background is painted as a raster
   image by the print engine, and this rule appears 111 times per edition */
.hr-knot{flex:0 0 auto;width:3.4rem;height:auto}

/* ------- compass ------- */
.compass{display:grid;grid-template-columns:repeat(3,1fr);gap:.75rem;
  margin:0 0 1.1rem}
@media (max-width:860px){.compass{grid-template-columns:1fr}}
.compass-card{background:var(--card);border:1px solid var(--line);
  border-radius:var(--r-2);padding:.75rem .9rem .8rem;position:relative;overflow:hidden;
  box-shadow:0 1px 4px rgba(38,34,27,.05)}
.compass-card::before{content:"";position:absolute;inset:0 auto 0 0;width:4px;
  background:var(--bronze-2)}
.compass-card.question::before{background:var(--cinnabar)}
.compass-card.boundary::before{background:var(--ink-3)}
.cc-tag{margin:0 0 .3rem;font-size:.72rem;letter-spacing:.2em;
  color:var(--bronze);font-weight:700}
.compass-card.question .cc-tag{color:var(--cinnabar)}
.compass-card.boundary .cc-tag{color:var(--ink-3)}
.compass-card p{margin:0;font-size:.93rem;line-height:1.7;color:var(--ink-2)}
.cc-src{grid-column:1/-1;margin:0;font-family:var(--sans);font-size:.8rem;
  color:var(--ink-3);display:flex;flex-wrap:wrap;gap:.3rem;align-items:center}
.cc-src-t{letter-spacing:.14em;color:var(--bronze);margin-right:.4rem}
.source-chip{display:inline-block;background:var(--paper-2);color:var(--bronze-3);
  border:1px solid var(--line);border-radius:var(--r-1);padding:.08rem .68rem;
  text-decoration:none;font-size:.76rem;line-height:1.5;vertical-align:bottom}
.source-chip:hover{border-color:var(--cinnabar);color:var(--cinnabar)}

/* ------- callouts ------- */
.callout{margin:1.15rem 0;padding:.75rem 1.05rem .3rem;border-radius:var(--r-2);
.callout:hover{box-shadow:0 2px 8px rgba(38,34,27,.07)}
  border:1px solid var(--line);border-left-width:4px;background:var(--card);
  font-size:.96rem}
.callout .callout-tag{margin:0 0 .2rem;font-family:var(--sans);font-weight:700}
.callout .callout-tag strong{font-size:.86rem;letter-spacing:.08em}
.callout .callout-body{margin:.15rem 0 .65rem;color:var(--ink-2)}
.callout-icon{margin-right:.45rem}
/* the mark is drawn, not typed: it has to sit on the tag's baseline and scale
   with the tag's own font-size rather than a fixed pixel size */
.callout-icon .ink-mark{width:1.06em;height:1.06em;vertical-align:-.15em}
.callout-tip{border-left-color:var(--jade);background:linear-gradient(90deg,
  rgba(78,110,93,.09),var(--card) 46%)}
.callout-tip .callout-tag{color:var(--jade)}
.callout-warning{border-left-color:var(--cinnabar);background:linear-gradient(90deg,
  rgba(180,71,47,.10),var(--card) 46%)}
.callout:hover{box-shadow:0 2px 8px rgba(38,34,27,.06)}
.callout-warning .callout-tag{color:var(--cinnabar)}
.callout-info{border-left-color:var(--bronze);background:linear-gradient(90deg,
  rgba(138,107,63,.10),var(--card) 46%)}
.callout-info .callout-tag{color:var(--bronze)}
.callout-concept{border-left-color:var(--sky);background:linear-gradient(90deg,
  rgba(76,112,147,.09),var(--card) 46%)}
.callout-concept .callout-tag{color:var(--sky)}
.callout-note{border-left-color:var(--ink-3)}
.callout-note .callout-tag{color:var(--ink-2)}
blockquote{margin:1.15rem 0;padding:.8rem 1.1rem;border-left:3px solid var(--line-2);
  border-radius:var(--r-2);background:rgba(243,234,216,.5);color:var(--ink-2)}
blockquote p{margin:0 0 .5em}
/* A quotation follows its block's alignment, not the body's: justifying a
   Latin epigraph across the full measure stretches it into rivers, and it also
   defeated the right-aligned setting the first-quote rule asks for. */
.chapter-body blockquote p{text-align:inherit}
blockquote p:last-child{margin-bottom:0}
.chapter-body > blockquote:first-of-type{border-left:none;border-top:1px solid var(--line);
  border-bottom:1px solid var(--line);border-radius:0;background:none;
  padding:.8rem 0;margin:0 auto 1.6rem;text-align:end;font-family:var(--kai);
  font-size:1.04rem;line-height:2;color:var(--bronze-3)}
@media (prefers-color-scheme:dark){
  body:not(.force-light) blockquote{background:rgba(34,34,28,.55)}}

/* ------- code ------- */
code{font-family:var(--mono);font-size:.86em;background:var(--paper-2);
  border:1px solid var(--line);border-radius:var(--r-1);padding:.06em .34em;
  color:var(--bronze-3)}
.codehilite{margin:1.1rem 0 1.25rem;border-radius:var(--r-2);position:relative;
  overflow:hidden;background:var(--code-bg);border:1px solid var(--code-line);
  box-shadow:0 6px 18px -12px rgba(38,34,27,.55)}
.mermaid-source-wrap{margin:1rem 0 1.25rem;border-radius:var(--r-2);
  overflow-x:auto;background:var(--code-bg);border:1px solid var(--code-line);
  box-shadow:0 2px 10px -4px rgba(0,0,0,.35)}
.codehilite::after{content:attr(data-lang);position:absolute;top:0;right:0;
  font-family:var(--sans);font-size:.6rem;font-weight:600;letter-spacing:.16em;
  text-transform:uppercase;line-height:1;padding:.34rem .55rem .3rem;
  color:#B9AC8E;background:rgba(200,164,92,.13);
  border-inline-start:1px solid var(--code-line);
  border-bottom:1px solid var(--code-line);border-start-end-radius:0;
  border-start-start-radius:8px}
.codehilite:not([data-lang])::after{content:none}
.codehilite pre,.mermaid-source pre{margin:0;padding:1.05rem 1.2rem;
  color:var(--code-fg);font-family:var(--mono);font-size:.83rem;line-height:1.68;
  background:transparent;overflow-x:auto;white-space:pre;
  scrollbar-width:thin;scrollbar-color:rgba(200,164,92,.4) transparent}
.codehilite pre::-webkit-scrollbar{height:7px
  ::-webkit-scrollbar-thumb{background:var(--line-2);border-radius:999px}
  ::-webkit-scrollbar-thumb:hover{background:var(--bronze-2)}}
.codehilite pre::-webkit-scrollbar-thumb{background:rgba(200,164,92,.35);
  border-radius:999px}
/* the ring is drawn inside because the frame clips what sticks out, and in
   bronze-2 because the code plate is dark ink in both colour schemes */
.codehilite pre:focus-visible{outline:2px solid var(--bronze-2);outline-offset:-2px}
.codehilite code{background:none;border:none;color:inherit;padding:0}
.codehilite .c,.codehilite .cm,.codehilite .c1,.codehilite .cs{color:#93886F;font-style:italic}
.codehilite .k,.codehilite .kd,.codehilite .kn,.codehilite .kt{color:#D8B26A;font-weight:600}
.codehilite .nf,.codehilite .nc,.codehilite .fm{color:#E2C08D}
.codehilite .s,.codehilite .s1,.codehilite .s2,.codehilite .sb,.codehilite .sd{color:#A9C46C}
.codehilite .m,.codehilite .mi,.codehilite .mf,.codehilite .mh{color:#DFA878}
.codehilite .nt,.codehilite .tag{color:#8FB2D4}
.codehilite .na,.codehilite .attr{color:#C8A45C}
.codehilite .o,.codehilite .ow{color:#BDB4A2}
.codehilite .p{color:#9A917E}
.codehilite .err{color:#E07B5F}

/* ------- tables ------- */
.table-scroll{overflow-x:auto;margin:1.1rem 0;border:1px solid var(--line);
  border-radius:var(--r-2);background:var(--card);
  scrollbar-width:thin;scrollbar-color:var(--line-2) var(--paper-2);
  box-shadow:0 1px 5px rgba(38,34,27,.05)}
/* a phone paints no bar until the reader drags, so a column sliced in half
   reads as the end of the table: measured on a 390px screen, one appendix sheet
   hid 493px of columns behind a straight cut. Naming the bar makes Chrome and
   Firefox keep a classic one in layout, which is the cue the plate frames
   below already give. `tabindex` on the wrapper (render.py) is what makes the
   hidden columns reachable without a mouse -- the focus ring below is the
   reason that attribute is there. */
.table-scroll::-webkit-scrollbar{height:9px}
.table-scroll::-webkit-scrollbar-track{background:var(--paper-2);
  border-radius:var(--r-2)}
.table-scroll::-webkit-scrollbar-thumb{background:var(--line-2);border-radius:999px}
.table-scroll::-webkit-scrollbar-thumb:hover{background:var(--bronze-2)}
.table-scroll:focus-visible{outline:2px solid var(--bronze)}
table{border-collapse:collapse;width:100%;font-size:.9rem;line-height:1.6}
 tbody tr:nth-child(even){background:rgba(243,234,216,.35)}
th{font-family:var(--sans);font-weight:700;color:var(--bronze-3);
  background:var(--paper-2);text-align:start;padding:.6rem .9rem;
  border-bottom:2px solid var(--line-2);white-space:nowrap}
td{padding:.55rem .9rem;border-bottom:1px solid var(--line);vertical-align:top}
tbody tr:nth-child(2n){background:rgba(243,234,216,.45)}
@media (prefers-color-scheme:dark){
  body:not(.force-light) tbody tr:nth-child(2n){background:rgba(34,34,28,.6)}}
tr{break-inside:avoid}
table td code{font-size:.8rem}

/* ------- figures & diagrams ------- */
figure.diagram{margin:1.5rem 0;text-align:center;break-inside:avoid}
.diagram-frame{position:relative;background:
    linear-gradient(180deg,var(--card),var(--paper-2)),
    radial-gradient(100% 60% at 50% 0%,rgba(200,164,92,.07),transparent);
  border:1px solid var(--line-2);border-radius:var(--r-2);padding:1.1rem 1rem;
  box-shadow:0 6px 22px -12px rgba(38,34,27,.30),
    inset 0 0 0 1px rgba(255,255,255,.55);overflow-x:auto}
.diagram-frame::before,.diagram-frame::after{content:"";position:absolute;
  width:11px;height:11px;border:1px solid var(--bronze-2);opacity:.75}
.diagram-frame::before{left:7px;top:7px;border-right:none;border-bottom:none}
.diagram-frame::after{right:7px;bottom:7px;border-left:none;border-top:none}
/* no filter: the print engine rasterises a filtered subtree, which would turn
   every plate's labels into outlines — unsearchable, and most of a 31MB PDF */
.diagram-frame svg{display:block;margin:0 auto;max-width:100%;height:auto}
.diagram-frame::-webkit-scrollbar{height:8px}
.diagram-frame::-webkit-scrollbar-track{background:var(--paper-2);
  border-radius:var(--r-2)}
.diagram-frame::-webkit-scrollbar-thumb{background:var(--line-2);border-radius:999px}
.diagram-frame::-webkit-scrollbar-thumb:hover{background:var(--bronze-2)}
.diagram-frame .node rect,.diagram-frame .cluster rect{rx:8}
/* a hand-drawn plate borrows the diagram's caption furniture so the two read
   as one series, but not its sideways scroll: a drawing is looked at, not
   panned, and its lines already carry the eye across the sheet */
figure.illu{margin:1.6rem 0;text-align:center;break-inside:avoid}
.illu-frame{position:relative;background:
    linear-gradient(180deg,var(--card),var(--paper-2)),
    radial-gradient(100% 60% at 50% 0%,rgba(200,164,92,.07),transparent);
  border:1px solid var(--line-2);border-radius:var(--r-2);padding:1.3rem 1.2rem;
  box-shadow:0 6px 22px -12px rgba(38,34,27,.30),
    inset 0 0 0 1px rgba(255,255,255,.55)}
.illu-frame svg{display:block;margin:0 auto;max-width:100%;height:auto}
.illu-photo .illu-frame{padding:0;overflow:hidden}
.illu-photo img{display:block;width:100%;height:auto}
/* the frame numbers of a sequential plate: small, in the margin, so the
   drawing stays the thing you look at */
.illu-seq .frame-no{font-family:var(--sans);font-size:9px;
  fill:currentColor;opacity:.5;stroke:none}
figcaption{margin:.7rem auto 0;max-width:var(--measure);font-family:var(--sans);
  font-size:.83rem;color:var(--ink-2);line-height:1.7;
  display:flex;gap:.7rem;justify-content:center;align-items:baseline}
figcaption::before,.figcaption::after{content:"";flex:0 0 2.2rem;height:1px;
  background:linear-gradient(90deg,transparent,var(--line-2));
  transform:translateY(-.35em)}
figcaption::after{background:linear-gradient(90deg,var(--line-2),transparent)}
.fig-no{color:var(--bronze);font-weight:700;letter-spacing:.06em;white-space:nowrap}
.fig-cap{color:var(--ink-3)}
.fig-hint{font-size:.7rem;line-height:1.5;color:var(--ink-3);white-space:nowrap;
  border:1px solid var(--line-2);border-radius:var(--r-1);padding:.02rem .5rem;
  transform:translateY(-.12em)}
/* the caption is a centered flex row, and a nowrap hint chip is the widest
   unbreakable item on it — on a phone the row overflows past the right edge,
   so let the chip drop to a second line instead */
@media (max-width:44rem){figcaption{flex-wrap:wrap;row-gap:.2rem}}
.mermaid-missing{color:var(--cinnabar);border:1px dashed var(--cinnabar);
  padding:1rem;text-align:center;border-radius:var(--r-2);font-family:var(--sans)}
.mermaid-source{text-align:start}
img{max-width:100%;height:auto}

/* ------- chapter notes ------- */
.chapter-notes{margin:1.9rem 0 0;padding:.85rem 1.05rem .9rem;border:1px solid var(--line);
  border-radius:var(--r-2);background:var(--card)}
.notes-title{font-family:var(--sans);font-size:.75rem;letter-spacing:.25em;
  color:var(--bronze);margin:0 0 .5rem}
.notes-list{list-style:none;margin:0;padding:0;counter-reset:fn;
  font-family:var(--mono);font-size:.74rem;color:var(--ink-3)}
.notes-list li{display:flex;gap:.6rem;align-items:baseline;padding:.32rem 0;
  border-bottom:1px dotted var(--line);word-break:break-all;flex-wrap:wrap}
.notes-list li:last-child{border-bottom:none}
.notes-list code,.notes-list a{min-width:0;max-width:100%;overflow-wrap:anywhere}
.notes-list li::before{counter-increment:fn;content:counter(fn);flex:0 0 1.3rem;
  text-align:right;font-family:var(--sans);font-weight:700;color:var(--bronze)}
.notes-list a.fn-url{color:inherit;text-decoration:none}
.notes-list a.fn-url:hover{color:var(--cinnabar)}
.notes-list .backref{text-decoration:none;color:var(--bronze)}
sup.fnum{font-family:var(--sans);font-size:.68em}
sup.fnum a{text-decoration:none;color:var(--cinnabar)}

/* ------- source registry ------- */
.reg-note{color:var(--ink-3);font-size:.95rem;margin:0 0 1.6rem}
.reg-kind{display:flex;align-items:baseline;gap:.7rem;font-family:var(--sans);
  font-size:.95rem;color:var(--bronze-3);letter-spacing:.12em;
  margin:2.6rem 0 .8rem}
.reg-kind::after{content:"";flex:1;height:1px;background:var(--line-2);
  transform:translateY(-.3em)}
.rk-n{font-family:var(--mono);font-size:.7rem;color:var(--bronze);
  border:1px solid var(--line-2);border-radius:var(--r-1);padding:.06rem .45rem;
  letter-spacing:0}
.reg-list{list-style:none;margin:0;padding:0}
/* a row is a bordered card: cut by a page break it reads as two broken boxes */
.reg-list li{padding:.85rem 1rem .95rem;margin-bottom:.55rem;
  border:1px solid var(--line);border-inline-start:3px solid var(--bronze-2);
  border-radius:var(--r-2);background:var(--card);
  break-inside:avoid;transition:border-inline-start-color .15s ease}
.reg-list li:hover{border-inline-start-color:var(--cinnabar)}
.reg-head{display:flex;flex-wrap:wrap;gap:.55rem;align-items:baseline}
.reg-no{font-family:var(--mono);font-size:.72rem;color:var(--bronze-3);
  letter-spacing:.04em}
.reg-head a{font-weight:700;text-decoration:none;color:var(--ink)}
.reg-head a:hover{color:var(--cinnabar)}
.reg-auth{font-family:var(--sans);font-size:.78rem;color:var(--bronze);
  background:var(--paper-2);border-radius:var(--r-1);padding:.05rem .7rem}
.reg-pin{font-family:var(--sans);font-size:.78rem;color:var(--ink-3)}
.reg-pin code{font-size:.72rem}
.reg-meta{font-family:var(--sans);font-size:.76rem;color:var(--ink-3);margin-top:.3rem}
.reg-scope{font-size:.9rem;color:var(--ink-2);margin-top:.35rem}

/* ------- subject index ------- */
.idx-cols{columns:2;column-gap:3rem;column-rule:1px solid var(--line)}
.idx-block{break-inside:avoid}
.idx-letter{font-family:var(--sans);color:var(--cinnabar);font-size:1.3rem;
  margin:1.6rem 0 .4rem;border-bottom:2px solid var(--bronze-2);
  padding-bottom:.15rem;display:inline-block;min-width:2.2rem}
.idx-list{list-style:none;margin:0;padding:0;font-size:.9rem}
/* the Chinese block needs one line of instruction: nothing else in the book
   is filed by radical, and a reader who is not told will assume it is random */
.idx-note{font-size:.82rem;color:var(--ink-2);margin:-.15rem 0 .3rem;
  line-height:1.55;max-width:26rem}
.idx-row{display:flex;align-items:baseline;gap:.35rem;padding:.26rem 0}
.idx-term{flex:0 1 auto;min-width:0;font-family:var(--sans);font-weight:600;
  overflow-wrap:anywhere}
.idx-refs{white-space:nowrap}
.idx-refs a{margin-right:.5rem}
/* a long identifier used to squeeze the leader down to a stub; the term may
   break anywhere rather than eat the dots, so the row always reads as an entry
   with a leader */
.idx-row .leader{margin:0 .35rem;flex:1 1 1.2rem;min-width:1.2rem}
.idx-row .page-ref{display:none}
@media (max-width:52rem){.idx-cols{columns:1}}

/* ------- principles (原理札记) ------- */
/* a hover card cannot reach the printed book, so the reason line gets a page;
   the term sits in a gutter so the reasons align into one readable column
   instead of staircasing down the measure */
.pr-note{font-size:.9rem;color:var(--ink-2);line-height:1.75;max-width:34rem;
  margin:-.35rem 0 1.4rem}
.pr-unit{margin:0 0 1.6rem}
.pr-head{display:flex;flex-wrap:wrap;align-items:baseline;gap:.5rem;
  font-family:var(--sans);font-size:.95rem;font-weight:700;margin:0;
  padding:.2rem 0 .4rem;border-bottom:2px solid var(--bronze-2)}
.pr-head a{color:var(--bronze-3);text-decoration:none}
.pr-head a:hover{color:var(--cinnabar)}
.pr-n{margin-inline-start:auto;font-family:var(--mono);font-size:.66rem;
  color:var(--bronze-3);border:1px solid var(--line-2);border-radius:var(--r-1);
  padding:.05rem .45rem}
.pr-list{list-style:none;margin:.35rem 0 0;padding:0}
.pr-row{display:grid;grid-template-columns:7.5rem 1fr;column-gap:.9rem;
  padding:.45rem 0 .5rem;border-bottom:1px dotted var(--line-2);
  break-inside:avoid}
.pr-term{grid-column:1;grid-row:1;font-family:var(--sans);font-weight:700;
  font-size:.88rem;line-height:1.8;color:var(--bronze-3);overflow-wrap:anywhere}
.pr-why{grid-column:2;grid-row:1;padding-inline-start:.55rem;
  border-inline-start:2px solid var(--bronze-2);font-size:.95rem;line-height:1.8;
  color:var(--ink)}
.pr-ana{grid-column:2;grid-row:2;margin-top:.22rem;padding-inline-start:.55rem;
  font-family:var(--kai);font-size:.9rem;line-height:1.75;color:var(--cinnabar)}
.pr-t{font-style:normal;font-family:var(--sans);font-size:.62rem;
  letter-spacing:.14em;color:var(--bronze-3);margin-inline-end:.4rem}
/* the collapse has to release the row pin too: term and reason both sit on row
   1 by design at full width, and a shared cell is how they overlapped on a phone */
@media (max-width:44rem){
  .pr-row{grid-template-columns:1fr;row-gap:.15rem}
  .pr-term,.pr-why,.pr-ana{grid-column:1;grid-row:auto}
}

/* ------- keeper (按语) ------- */
/* the old postman at the foot of each unit: a narrow box floated to the far
   edge so the line reads as marginalia, not as a paragraph the manuscript
   grew; on paper the same box sits inline above the ruts it comments on */
.keeper{display:flex;align-items:flex-end;gap:.65rem;margin:1.4rem 0 .15rem;
  max-width:min(38ch,100%);margin-inline-start:auto}
.kp-art{flex:none;width:2.4rem;line-height:0;color:var(--ink-3)}
.kp-art svg{width:100%;height:auto;transition:transform .18s ease}
.keeper:hover .kp-art svg,.keeper:focus-within .kp-art svg{
  transform:translateY(-3px) rotate(-4deg)}
.keeper-note{margin:0;font-family:var(--kai);font-size:.92rem;line-height:1.75;
  color:var(--ink-2);border-inline-start:2px solid var(--bronze-2);
  padding-inline-start:.6rem}
.kn-list{list-style:none;margin:.35rem 0 0;padding:0}
.kn-row{display:grid;grid-template-columns:7.2rem 1fr;column-gap:.9rem;
  padding:.45rem 0 .5rem;border-bottom:1px dotted var(--line-2);
  break-inside:avoid;align-items:baseline}
.kn-head{font-family:var(--sans);font-weight:700;font-size:.88rem;
  line-height:1.8;overflow-wrap:anywhere}
.kn-head a{color:var(--bronze-3);text-decoration:none}
.kn-head a:hover{color:var(--cinnabar)}
.kn-note{padding-inline-start:.55rem;border-inline-start:2px solid
  var(--bronze-2);font-family:var(--kai);font-size:.92rem;line-height:1.75;
  color:var(--ink)}
@media (max-width:44rem){
  .kn-row{grid-template-columns:1fr;row-gap:.15rem}
  .kn-head,.kn-note{grid-column:1}
}

/* ------- footer ------- */
.colophon{margin:2.8rem 0 1.3rem;text-align:center;color:var(--ink-3);
  font-family:var(--sans);font-size:.78rem;letter-spacing:.1em}
.colophon .wheel{width:34px;height:34px;color:var(--bronze-2);opacity:.7;
  display:block;margin:0 auto .8rem}

/* ------- plain-language layer (通俗层) ------- */
/* the lead band is the one device that survives print unchanged, so it is
   deliberately the loudest block on a chapter opener */
.lead-band{position:relative;margin:0 0 1.1rem;padding:.9rem 1.2rem 1rem;
  border:1px solid var(--line);border-radius:var(--r-2);overflow:hidden;
  background:linear-gradient(135deg,var(--card),var(--paper-2) 82%);
  box-shadow:0 1px 4px rgba(38,34,27,.05)}
.lead-band::before{content:"";position:absolute;inset:0 auto 0 0;width:4px;
  background:linear-gradient(180deg,var(--cinnabar),var(--bronze-2))}
/* a faint wheel in the corner: the band is the loudest block on a chapter
   opener, and the ornament ties it to the rest of the book without adding a
   line of copy */
.lead-band::after{content:"";position:absolute;inset-block-end:-2.6rem;
  inset-inline-end:-2.4rem;width:8rem;height:8rem;border-radius:50%;
  border:1px solid var(--bronze-2);opacity:.16;pointer-events:none;
  box-shadow:0 0 0 .55rem var(--card),0 0 0 .6rem var(--bronze-2)}
.lb-tag{margin:0 0 .35rem;font-family:var(--sans);font-size:.7rem;font-weight:700;
  letter-spacing:.28em;color:var(--cinnabar)}
.lb-plain{margin:0;font-size:1.08rem;line-height:1.8;color:var(--ink);
  text-wrap:pretty}
/* the analogy tag is an inline chip, not a row: as a flex item the sentence
   after it became its own anonymous item and dropped to a second line, which
   cost the band a whole line of height on every chapter */
.lb-analogy{margin:.5rem 0 0;font-family:var(--kai);font-size:1rem;
  line-height:1.85;color:var(--bronze-3)}
.lb-a-tag{display:inline-block;font-family:var(--sans);font-size:.68rem;font-weight:700;
  letter-spacing:.14em;color:var(--bronze);background:var(--paper-2);
  border:1px solid var(--line);border-radius:var(--r-1);padding:.06rem .55rem;
  margin-inline-end:.45rem;vertical-align:.14em}
@media (max-width:860px){.lead-band{padding:.9rem 1rem 1rem}
  .lb-plain{font-size:1.02rem}}

/* dashed term + CSS-only popover: no JS, and focus works for tap and keyboard */
.gloss{position:relative;border-bottom:1px dashed var(--bronze-2);cursor:help}
.gloss:hover,.gloss:focus,.gloss:focus-within{border-bottom-color:var(--cinnabar);
  color:var(--cinnabar);outline:none}
.gloss-pop{position:absolute;left:50%;bottom:calc(100% + .55rem);
  transform:translate(-50%,.35rem);z-index:40;width:max-content;
  max-width:min(21rem,80vw);padding:.6rem .8rem .65rem;text-align:start;
  font-family:var(--sans);font-size:.8rem;line-height:1.65;font-weight:400;
  color:var(--ink);background:var(--card);border:1px solid var(--line-2);
  border-radius:var(--r-2);box-shadow:0 12px 28px -16px rgba(38,34,27,.6);
  opacity:0;visibility:hidden;pointer-events:none;
  transition:opacity .12s ease,transform .12s ease}
.gloss:hover .gloss-pop,.gloss:focus .gloss-pop,.gloss:focus-within .gloss-pop{
  opacity:1;visibility:visible;transform:translate(-50%,0)}
.gloss-pop::after{content:"";position:absolute;left:50%;top:100%;
  transform:translateX(-50%);border:6px solid transparent;
  border-top-color:var(--card)}
.gloss-pop b{display:block;margin-bottom:.15rem;font-size:.72rem;
  letter-spacing:.12em;color:var(--bronze-3)}
.gloss-pop .gp-plain{display:block;color:var(--ink)}
/* the reason line is the one a reader skims for, so it gets a rule rather than
   another font: the calligraphic analogy below must stay the softest of three */
.gloss-pop .gp-why{display:block;margin-top:.4rem;padding-inline-start:.5rem;
  border-inline-start:2px solid var(--bronze-2);color:var(--ink)}
.gloss-pop .gw-t{font-style:normal;font-size:.62rem;letter-spacing:.14em;
  color:var(--bronze-3);margin-inline-end:.35rem}
.gloss-pop .gp-analogy{display:block;margin-top:.35rem;font-family:var(--kai);
  color:var(--cinnabar)}
/* a centred popover next to the page edge would be cut off; below the width
   where one can fit it becomes a caption pinned to the bottom of the viewport
   instead. That width is arithmetic, not taste: a term may sit at the very end
   of the 46rem measure, and the bubble reaches 10.5rem past its centre, so the
   screen has to be measure + bubble = 67rem across before the bubble can be
   trusted. (720px screens used to hang 100px of it off the right edge, which
   the whole document then had to scroll sideways for.) */
@media (max-width:67rem){
  .gloss-pop{position:fixed;left:50%;bottom:.9rem;top:auto;
    width:min(22rem,92vw);max-width:92vw;transform:translate(-50%,.5rem)}
  .gloss-pop::after{display:none}
}
/* a sheet that scrolls sideways clips everything painted inside it, including a
   bubble whose term sits near its edge: measured at 1360px and above, 13 of the
   book's tables hid their bubbles entirely outside the visible cell area and
   one grew 78px of phantom scroll. Terms inside a table therefore take the
   caption at every width -- it is the one place the reader can always see it. */
.table-scroll .gloss-pop{position:fixed;left:50%;bottom:.9rem;top:auto;
  width:min(22rem,92vw);max-width:92vw;transform:translate(-50%,.5rem)}
.table-scroll .gloss-pop::after{display:none}
@media (prefers-color-scheme:dark){
  body:not(.force-light) .gloss-pop{box-shadow:0 12px 28px -14px rgba(0,0,0,.75)}}

/* the chapter's terms are a card you read across, not a box you look inside: a
   dashed frame round twenty-two dotted rows made a chapter open entirely on
   furniture, and the prose never reached the first page. It now trails the
   unit, so it needs the air a following block would have had */
.new-terms{margin:1.5rem 0 0;padding:.6rem 0 0;border-top:1px solid var(--line)}
.nt-title{display:flex;align-items:baseline;gap:.5rem;margin:0 0 .35rem;
  font-family:var(--sans);font-size:.72rem;letter-spacing:.25em;
  color:var(--bronze);font-weight:700}
.nt-n{font-family:var(--mono);font-size:.68rem;letter-spacing:0;color:var(--bronze-3)}
/* the panel is the one block that gets taller the more terms a chapter uses;
   at three columns a 20-term chapter is seven rows instead of twenty, which is
   the difference between a reference card and a wall of text */
.nt-list{list-style:none;margin:0;padding:0;display:grid;
  grid-template-columns:repeat(auto-fit,minmax(16rem,1fr));gap:0 1.6rem}
/* the air between rows sits above them, not below: a row's bottom padding is
   the last thing the card leaves on a sheet, and 1.6px that will not fit was
   enough for Chromium to strand a whole empty page after the chapter */
.nt-row{display:flex;flex-wrap:wrap;align-items:baseline;
  padding:.32rem 0 0;min-width:0;break-inside:avoid}
.nt-term{flex:0 1 auto;min-width:0;font-family:var(--sans);font-weight:700;
  font-size:.84rem;color:var(--bronze-3)}
/* the tie between a term and its plain wording is one gold dot: the drawn
   dash it replaces cost a row of its own colour in every one of 20 panels */
.nt-term::after{content:"·";color:var(--bronze-2);font-weight:700;
  margin-inline:.18rem .22rem}
.nt-plain{flex:1 1 6rem;min-width:0;font-size:.86rem;line-height:1.6;
  color:var(--ink-2)}
.nt-note{margin:0 0 .3rem;font-family:var(--sans);font-size:.74rem;
  color:var(--ink-3)}
@media (max-width:44rem){.nt-list{grid-template-columns:1fr}}

/* section level chips — flex puts the chip at the end of the heading line
   without a float, which would fight page breaks in print */
article h2{display:flex;flex-wrap:wrap;align-items:baseline;column-gap:.6rem}
.sec-tier,.tier-chip{flex:0 0 auto;align-self:center;margin-inline-start:auto;
  font-family:var(--sans);font-size:.62rem;font-weight:700;letter-spacing:.14em;
  color:var(--ink-3);border:1px solid var(--line-2);border-radius:var(--r-1);
  padding:.08rem .5rem;white-space:nowrap}
.t-start{color:var(--jade);border-color:var(--jade)}
.t-core{color:var(--bronze-3);border-color:var(--bronze-2)}
.t-deep{color:var(--sky);border-color:var(--sky)}
.tier-legend{margin:2.4rem 0 0;padding-top:1.4rem;border-top:1px solid var(--line)}
.tier-legend .page-sub{font-size:1.2rem;margin:0 0 .4rem;color:var(--bronze-3)}
.tl-hint{margin:0 0 1rem;color:var(--ink-2);font-size:.94rem;max-width:34rem}
.tl-list{list-style:none;margin:0;padding:0}
.tl-row{display:flex;align-items:baseline;gap:.75rem;padding:.4rem 0;
  border-bottom:1px solid var(--line)}
.tl-row .tier-chip{margin-inline-start:0}
.tl-desc{flex:1;color:var(--ink-2);font-size:.92rem}
.tl-n{font-family:var(--mono);font-size:.76rem;color:var(--ink-3)}

/* ------- the reading column -------
   Only the running prose steps in to the measure; the chapter furniture above
   the body, and the plates, tables and code inside it, keep the sheet width. An
   inset lead band over full-width compass cards reads as a mistake rather than
   a hierarchy, and the 159 plates need the room. This block is deliberately
   last: every component above sets its own `margin` shorthand, which would
   reset the centring. */
.chapter-body>p,.chapter-body>ul,.chapter-body>ol,.chapter-body>dl,
.chapter-body>blockquote,.chapter-body>h2,.chapter-body>h3,.chapter-body>h4,
.chapter-body .ch-close,.chapter-body .callout,.chapter-notes,.tier-legend,
.reg-note,.tl-hint,.ip-notice,.revisions ul{
  max-width:var(--measure);margin-inline:auto}

"""

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
  .diagram-frame,.codehilite,.table-scroll,.compass-card,.route-card{
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

CSS = SCREEN_CSS + PRINT_CSS
