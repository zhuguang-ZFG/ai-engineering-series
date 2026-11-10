# Task 1 Review — 第 01 章长讲大纲与口播脚本

**Reviewer:** executor subagent (task-scoped gate)  
**Base:** `560e960163b54565595b07c543cee23ab3bf9dcd`  
**Head (initial):** `480d4143ceab28696cb892e2824fd2b6a3593b32`  
**Head (after fix):** `ef75a5a5d32bb13905740954aaf5e00f76721c08`  
**Diff scope:** `docs/video/ch01/long-outline.md`, `docs/video/ch01/long-script.md` only  
**Reviewed against:** `task-1-brief.md`, Global Constraints, source chapter 01  
**Date:** 2026-10-27 (America/Adak)

---

## Verdicts (initial review @ 480d414)

### 1) Spec compliance: ✅ (with ⚠️)

See prior review body below historical notes. Two Important defects were opened.

### 2) Task quality: **Changes required**

#### Critical
- None.

#### Important (opened @ 480d414)
1. Outline install command typo: `pm install` → must be `npm install`.
2. Outline vs script timing drift: spoken ~3366 汉字 / ~15.3 min vs outline 18:45; blocks 3–4 thin.

#### Minor
1. Header `[ANIM:…]` / `[CODE:…]` ellipsis fake marker ids.
2. Empty `video/ch01/assets` / `out` untracked.
3. Untracked `_write_long_script.py`.
4. Opening hook longer than 45s outline slot.

---

## Re-review (after fix @ ef75a5a)

**Re-reviewer:** executor subagent  
**Confirm HEAD:** `ef75a5a5d32bb13905740954aaf5e00f76721c08` (`docs(video): tighten ch01 long script timing and npm install typo`)  
**Ancestor check:** `560e960` ⊂ `480d414` ⊂ `ef75a5a`  
**Method:** independent UTF-8 read of outline/script; Python han recount (excl. headings / blockquotes / `---` / `[ANIM|CODE:…]` marker lines; strip `*`); marker set equality; forbidden-string scan. Did not trust report alone.

### Prior Important — verification

| # | Finding | Status | Evidence |
|---|---------|--------|----------|
| 1 | `pm install` → `npm install` | **Fixed** | Outline block 5 now `npm install -g @anthropic-ai/claude-code → claude --version`. Diff `480d414..ef75a5a` is a one-line fix. Note: naive substring `"pm install" in text` still matches inside `npm install` — not a remaining typo. |
| 2 | Spoken length / timing for 15–20 min (target ~3600–4200 汉字) | **Fixed** | Independent recount **3964** 汉字 → **18.02 min** @ 220字/分 (was 3366 / 15.30). Within brief band 3300–4400 and preferred ~3600–4200. Outline table still sums **18:45**; spoken + ANIM/CODE pause budget aligns. |

### Spec compliance (re-review): ✅

| Check | Result | Evidence |
|-------|--------|----------|
| Files created | ✅ | `long-outline.md`, `long-script.md` |
| Outline six blocks | ✅ | Blocks 1–6 present |
| Outline estimates sum 15–20 | ✅ | 18:45 |
| Script spoken 3300–4400 汉字 | ✅ | **3964** |
| 沉稳男声 only; no 晓晓/女声 | ✅ | Meta line; forbidden scan false |
| 基于开源书稿 + 驭者·Agent Harness in ending | ✅ | Block 6 outro |
| Real numbers 1,884 / 512,664 | ✅ | Outline digits; spoken 一千八百八十四 / 五十一万二千六百六十四 |
| ANIM/CODE ids aligned | ✅ | 15 ANIM + 4 CODE; outline ≡ script |
| Header fake ellipsis markers | ✅ cleared | Prose form `ANIM:id / CODE:id` |
| Helper `_write_long_script.py` | ✅ removed | Path absent |
| Sample = Ch01 only | ✅ | |

### Task quality (re-review): **Approved**

#### Critical
- None.

#### Important
- None remaining.

#### Minor (non-blocking; optional for later tasks)
1. **Per-block vs outline slot still uneven** (spoken @ 220字/分): block1 1.2 vs 0:45; block3 5.10 vs 5:00; **block4 4.87 vs 6:00 (~1.1 min short)**; block5 1.36 vs 2:00; block6 1.52 vs 1:00. Total spoken ~18.0 vs outline 18:45 — overall runway OK if Task 4 treats ANIM/CODE as pause budget rather than pure speech. Preferable to further pad block 4 unless production timing runs short.
2. Opening hook still longer than the labeled 45s slot — content-fine; outline label is aspirational.
3. Empty `video/ch01/assets` and `out` remain untracked (no `.gitkeep`) — fine until asset tasks.

### Suggested action
- Gate **PASS** for Task 1. Proceed to Task 2 (short-script). No further Task-1 rewrite required for Spec or Important quality.

---

## Historical detail (initial review @ 480d414, preserved)

Initial Spec ✅ with ⚠️; Quality Changes required. Important: (1) `pm install` typo in outline block 5; (2) spoken 3366 near floor / outline–script timing drift (~15.3 vs 18:45), especially blocks 3–4. Fix commit `ef75a5a` addressed both; see Re-review above.
