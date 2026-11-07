"""Screen rules for the shell, structure pages, TOC, part dividers and chapters."""
from __future__ import annotations

SCREEN_CSS = r"""*{box-sizing:border-box}
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
/* mermaid ships its own <style> inside each diagram, edge-dash loops included;
   a reader who asked for reduced motion gets the finished drawing */
@media (prefers-reduced-motion: reduce){svg *{animation:none!important}}

"""
