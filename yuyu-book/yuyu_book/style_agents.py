"""The four engineering volumes use architectural artwork and spare covers."""

AGENT_CSS = r"""
.agent-book{--cinnabar:#205C68;--paper:#FAFAF7;--paper-2:#F0F3F2;--card:#FFFFFC;--code-bg:#F2F4F2;--line:#DAE0DC;--line-2:#C6D1CC}
.agent-deepseek{--cinnabar:#315AA6}
.agent-hermes{--cinnabar:#79613B}
.agent-codex{--cinnabar:#326853}
.agent-book .ch-seal{border:0;border-radius:0;background:none;transform:none;font-size:2.2rem;line-height:1;font-family:var(--sans);font-weight:750;letter-spacing:-.06em;width:3.2rem}
.agent-book .ch-title{font-family:var(--sans);font-weight:700;letter-spacing:-.02em}
.agent-book article .chapter-body>p:first-of-type::first-letter{font-size:inherit;float:none;padding:0;color:inherit;font-weight:inherit;font-family:inherit;line-height:inherit}
.agent-book .compass{gap:0;margin-bottom:1.5rem;border-bottom:1px solid var(--line)}
.agent-book .compass-card{border:0;border-radius:0;box-shadow:none;background:none;padding:.6rem .9rem .8rem 0}
.agent-book .compass-card+.compass-card{padding-left:.9rem;border-left:1px solid var(--line)}
.agent-book .compass-card::before{display:none}
.agent-book .compass-card p{font-size:.86rem;line-height:1.65}
.agent-book .lead-band{border:0;border-radius:0;border-left:3px solid var(--cinnabar);box-shadow:none;background:var(--paper-2);padding:.7rem 1rem;margin-bottom:.6rem}
.agent-book .lead-band::before,.agent-book .lead-band::after{display:none}
.agent-book .cc-tag,.agent-book .lb-tag{letter-spacing:.12em;font-size:.67rem}
.agent-book .cc-src{padding:.7rem 0;font-size:.75rem}
.agent-book .codehilite{border-radius:0;border-left:2px solid var(--line-2)}
.agent-book .pd-inner{border-top:3px solid var(--cinnabar);padding-top:1.8rem}
.agent-book .pd-ghost{opacity:.02}
.agent-book .pd-title{font-family:var(--sans);letter-spacing:-.02em}
.agent-book .idx-row{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:.15rem .6rem;padding:.4rem 0;border-bottom:1px solid var(--line)}
.agent-book .idx-term{grid-column:1 / -1}
.agent-book .idx-refs{grid-column:1;white-space:normal;font-size:.85em;line-height:1.7;color:var(--ink-2)}
.agent-book .idx-refs a{display:inline-block;white-space:nowrap}
.agent-book .idx-row .leader{display:none}
.agent-book .idx-ref{grid-column:2;grid-row:2;align-self:end}
@media(max-width:860px){.agent-book .compass-card+.compass-card{padding-left:0;border-left:0;border-top:1px solid var(--line)}}
.agent-volume{--volume-ink:#205C68}
.av-deepseek{--volume-ink:#315AA6}
.av-hermes{--volume-ink:#79613B}
.av-codex{--volume-ink:#326853}
.agent-volume .cover-inner{
  text-align:left;background:var(--card);box-shadow:none;
  border-top:10px solid var(--volume-ink);border-bottom:1px solid var(--line);
  padding:2.6rem 2.2rem 1.6rem;width:100%;
}
.agent-volume .cover-inner::before,.agent-volume .cover-inner::after{display:none}
.agent-volume .cover-kicker{color:var(--volume-ink);letter-spacing:.2em;font-size:.67rem;margin:0 0 2.6rem;max-width:32rem}
.agent-volume .book-title{line-height:1.05}
.agent-volume .bt-main{font-family:var(--sans);font-size:clamp(2.4rem,7vw,4.5rem);font-weight:780;letter-spacing:-.055em;text-indent:0}
.agent-volume .bt-tail{font-size:1.25rem;letter-spacing:.13em;text-indent:0;margin-top:1.1rem}
.agent-volume .cover-rule{display:none}
.agent-volume .cover-art{width:100%;margin:3rem 0 2.5rem;color:var(--volume-ink)}
.agent-volume .cover-art svg{display:block;width:100%;height:auto;overflow:visible}
.agent-volume .book-sub{max-width:30rem;letter-spacing:.025em;line-height:1.8;margin-bottom:1.2rem}
.agent-volume .book-epi{margin:0 0 2rem;max-width:28rem;font-family:var(--sans);font-size:.88rem;line-height:1.8;color:var(--ink-3)}
.agent-volume .cover-foot{justify-content:space-between;gap:1rem;border-top:1px solid var(--line);align-items:center}
.agent-volume .cover-kicker,.agent-volume .book-title,.agent-volume .book-sub,
.agent-volume .book-epi,.agent-volume .cover-foot,.agent-volume .cover-art{
  animation:none!important;opacity:1;transform:none;
}
@media screen and (prefers-color-scheme:dark){
  body.agent-book:not(.force-light){--cinnabar:#75B5C1;--paper:#191E1E;--paper-2:#222B2A;--card:#1D2524;--code-bg:#202827;--line:#3B4945;--line-2:#4A5A55}
  body.agent-deepseek:not(.force-light){--cinnabar:#93B5F4}body.agent-hermes:not(.force-light){--cinnabar:#D5B987}body.agent-codex:not(.force-light){--cinnabar:#91C9AE}
  body:not(.force-light) .agent-volume{--volume-ink:#75B5C1}body:not(.force-light) .av-deepseek{--volume-ink:#93B5F4}
  body:not(.force-light) .av-hermes{--volume-ink:#D5B987}body:not(.force-light) .av-codex{--volume-ink:#91C9AE}
}
@media print{
  .agent-book{--cinnabar:#205C68;--paper:#FFF;--paper-2:#F1F4F2;--card:#FFF;--code-bg:#F3F5F3;--line:#D0D9D3;--line-2:#BDC9C0}
  .agent-deepseek{--cinnabar:#315AA6}.agent-hermes{--cinnabar:#79613B}.agent-codex{--cinnabar:#326853}
  .agent-book .compass{grid-template-columns:repeat(3,1fr);margin-bottom:5mm}
  .agent-book .compass-card+.compass-card{padding-left:3mm;border-left:1px solid var(--line);border-top:0}
  .agent-book .compass-card p{font-size:8pt}
  .agent-book .lead-band{padding:2.5mm 3mm}
  .agent-book .ch-seal{font-size:26pt}
  .agent-book .idx-letter{margin:.85rem 0 .3rem;font-size:1.1rem}
  .agent-book .idx-row{padding:.22rem 0;line-height:1.5;break-inside:avoid}
  .agent-book .idx-refs{line-height:1.5}
  .agent-volume{--volume-ink:#205C68}.av-deepseek{--volume-ink:#315AA6}
  .av-hermes{--volume-ink:#79613B}.av-codex{--volume-ink:#326853}
  .agent-volume .cover-inner{padding:12mm 8mm 6mm;box-shadow:none;border-top:3mm solid var(--volume-ink);border-bottom:1px solid var(--line);justify-content:flex-start}
  .agent-volume .cover-kicker{margin-bottom:18mm;font-size:8pt}
  .agent-volume .bt-main{font-size:40pt}
  .agent-volume .bt-tail{font-size:16pt;margin-top:5mm}
  .agent-volume .cover-art{margin:16mm 0 13mm}
  .agent-volume .book-sub{font-size:10pt;line-height:1.8}
  .agent-volume .book-epi{font-size:9pt;margin-top:3mm}
  .agent-volume .cover-foot{margin-top:auto}
}
"""
