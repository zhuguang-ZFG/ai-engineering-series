// The three applied-chapter drawings may only carry numbers that the hosting
// chapter already publishes; a silent drift between picture and prose would
// teach a reader two different models.
import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { appliedArtworks, ladder, ocrStates, faults } from "./applied-art.mjs";

const read = path => readFileSync(new URL(path, import.meta.url), "utf8").replaceAll("−", "-");
const chapters = Object.fromEntries(["c18", "c19", "c22", "c27", "c28", "c29", "c30"].map(id => [id, read(`../../book/llm/lessons/${id}.md`)]));
const host = {
  "c18-retrieval-scores.svg": "c18",
  "c19-failure-ladder.svg": "c19",
  "c22-latency-spread.svg": "c22",
  "c27-ocr-failures.svg": "c27",
  "c28-context-budget.svg": "c28",
  "c29-fault-matrix.svg": "c29",
  "c30-rubric-weights.svg": "c30"
};
const decimals = text => new Set((text.match(/-?\d+\.\d+/g) ?? []).map(value => Number(value).toFixed(4)));
const palette = new Set(["#26221B", "#5C5448", "#E3D8C1", "#F3EAD8", "#B4472F", "#FFFDF8"]);

test("every drawn number is published by the chapter that hosts the drawing", () => {
  for (const [file, svg] of appliedArtworks) {
    assert.ok(svg.includes("<title") && svg.includes("<desc"), `${file}: missing accessible name`);
    assert.ok(!/width="480" height="\d+"[^>]*>\s*<rect width="480"/.test(svg), `${file}: plate fill returned`);
    for (const color of svg.match(/#[0-9a-fA-F]{6}/g) ?? []) {
      assert.ok(palette.has(color.toUpperCase()), `${file}: off-palette colour ${color}`);
    }
    const corpus = chapters[host[file]];
    assert.ok(corpus, `${file}: no host chapter`);
    const published = decimals(corpus);
    const labels = [...svg.matchAll(/<text[^>]*>([^<]*)<\/text>/g)].map(match => match[1]).join(" ");
    for (const value of new Set(labels.match(/-?\d+\.\d{2,6}/g) ?? [])) {
      assert.ok(published.has(Number(value).toFixed(4)), `${file}: ${value} is not published by ${host[file]}`);
    }
  }
});

test("the rubric drawing sums to the published total", () => {
  const svg = appliedArtworks.find(([file]) => file === "c30-rubric-weights.svg")[1];
  const points = [...svg.matchAll(/<text[^>]*>(\d+)<\/text>/g)].map(match => Number(match[1]));
  const weights = points.filter(value => [10, 15, 20].includes(value));
  assert.equal(weights.reduce((sum, value) => sum + value, 0), 100, `weights sum to ${weights.reduce((sum, value) => sum + value, 0)}`);
});

test("the drawings stay distinct files with one title each", () => {
  const files = appliedArtworks.map(([file]) => file);
  assert.equal(new Set(files).size, files.length);
  for (const [, svg] of appliedArtworks) assert.equal((svg.match(/<title/g) ?? []).length, 1);
});

// 三幅图的行数由章节自身的清单决定：多一行或漏一行都是图与正文分家。
test("row counts follow the lists published by each chapter", () => {
  const stepRows = chapters.c19.split("\n").filter(line => /^\| \d+ \|/.test(line));
  assert.equal(ladder.length, stepRows.length, `ladder has ${ladder.length} rows, c19 publishes ${stepRows.length}`);

  const headings = (text, from, to) => text.slice(text.indexOf(from), text.indexOf(to)).split("\n").filter(line => line.startsWith("### ")).length;
  const injections = headings(chapters.c29, "## 故障注入", "## 回退");
  assert.equal(faults.length, injections, `fault matrix has ${faults.length} rows, c29 publishes ${injections}`);
  const states = headings(chapters.c27, "## 看不清、看不懂、看错", "## 改一个条件");
  assert.equal(ocrStates.length, states, `OCR drawing has ${ocrStates.length} states, c27 publishes ${states}`);
});
