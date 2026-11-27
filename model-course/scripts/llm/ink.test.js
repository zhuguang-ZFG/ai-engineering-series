import test from "node:test";
import assert from "node:assert/strict";

import { inkifySvg } from "./ink.mjs";

const figure = d => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300"><path d="${d}" stroke="#26221B" fill="none"/></svg>`;

// The ladder outlines use shallow Q curves whose control point sits ~0.01px
// off the chord midpoint. Earlier normalisation rounded that residue up and
// shifted the control point by 0.02px on every re-ink.

test("a bowed path keeps its moveto and closing command", () => {
  const d = "M 26 72 L 454 71 L 452.6 137 L 25 135.4 Z";
  const inked = inkifySvg(figure(d)).match(/ d="([^"]*)"/)[1];
  assert.match(inked, /^M 26 72 /);
  assert.match(inked, / Z$/);
  assert.ok(inked !== d, "the long segments should still be bowed");
});

test("re-inking a shallow curve leaves the figure unchanged", () => {
  const d = "M 118 266 Q 217.74 264.9 317.5 266 L 317.5 286 Q 217.74 283.82 118 286 Z";
  const once = inkifySvg(figure(d));
  assert.equal(inkifySvg(once), once);
});

test("the pen wobble is deterministic for the same stroke", () => {
  const d = "M 26 72 Q 146.72 67.4 454 71 L 452.6 137 Q 290.88 138.8 25 135.4 Z";
  assert.equal(inkifySvg(figure(d)), inkifySvg(figure(d)));
});

test("dashed strokes are not redrawn", () => {
  const svg = '<svg xmlns="http://www.w3.org/2000/svg"><path d="M28 532 Q240 530 452 532" stroke="#26221B" stroke-dasharray="7 6" fill="none"/></svg>';
  assert.equal(inkifySvg(svg), svg);
});
