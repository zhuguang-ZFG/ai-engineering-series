"""Design tokens: colour, type, measure and radius, plus dark-mode overrides."""
from __future__ import annotations

TOKENS_CSS = r"""
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
"""
