"""Screen rules for components: compass, callouts, code, tables, plates, notes, registries and the plain layer."""
from __future__ import annotations

COMPONENTS_CSS = r"""/* ------- compass ------- */
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
