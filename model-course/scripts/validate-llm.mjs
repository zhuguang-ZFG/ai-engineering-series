import { readFileSync, existsSync, readdirSync } from "node:fs";
import { resolve, dirname, basename, join, extname } from "node:path";
import { gzipSync } from "node:zlib";
import assert from "node:assert/strict";
import { validateData } from "./llm/validate-data.mjs";

const root = resolve(import.meta.dirname, "..");
const { ready } = validateData(root);
const output = join(root, "exports/llm");
const colors = new Set(readFileSync(join(root, "design/system/tokens.css"), "utf8").match(/#[0-9a-fA-F]{6}/g).map((value) => value.toLowerCase()));
const figures = JSON.parse(readFileSync(join(root, "book/assets/handdraw/llm/figures.json"), "utf8")).figures;
let figureCount = 0;
for (const lesson of ready) for (const file of [lesson.figure, ...(lesson.extraFigures ?? [])]) {
  const metadata = figures.find((entry) => entry.lesson === lesson.id && entry.file === file);
  assert.ok(metadata, `${lesson.id}: missing figure metadata`);
  for (const field of ["id", "purpose", "source", "limitations", "alt", "mobile"]) assert.ok(metadata[field]?.length, `${lesson.figure}: missing ${field}`);
  const svg = readFileSync(join(root, "book/assets/handdraw/llm", file), "utf8");
  for (const color of svg.match(/#[0-9a-fA-F]{6}/g) ?? []) assert.ok(colors.has(color.toLowerCase()), `${lesson.figure}: unknown color ${color}`);
  assert.ok(!/<text[^>]*fill="(#1f883d|#e2601f)"/.test(svg), `${lesson.figure}: display color used for small text`);
  assert.ok(svg.includes("<title") && svg.includes("<desc"), `${lesson.figure}: accessible description missing`);
  const page = readFileSync(join(output, `${lesson.slug}.html`), "utf8");
  assert.equal(page.split(`src="../../book/assets/handdraw/llm/${file}"`).length - 1, 1, `${lesson.id}: figure must appear exactly once: ${file}`);
  assert.ok(!/<!--\s*figure:/.test(page), `${lesson.id}: unexpanded inline illustration`);
  figureCount++;
}

let links = 0;
const assetDir = join(root, "book/assets/handdraw/llm");
const assetsSvg = readdirSync(assetDir).filter((name) => extname(name) === ".svg");
for (const name of assetsSvg) {
  const svg = readFileSync(join(assetDir, name), "utf8");
  for (const color of svg.match(/#[0-9a-fA-F]{6}/g) ?? []) assert.ok(colors.has(color.toLowerCase()), `${name}: color ${color} is not in design/system/tokens.css`);
  assert.ok(svg.includes("<title") && svg.includes("<desc"), `${name}: accessible description missing`);
}
const latex = /\\\[|\\\]|\\\(|\\\)|\\(?:text|frac|lceil|rceil|times|approx|cdot|sum)\s*[{(]/;
let markdownCount = 0;
const walk = (dir) => readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
  const path = join(dir, entry.name);
  return entry.isDirectory() ? walk(path) : [path];
});
for (const path of walk(join(root, "book/llm")).filter((name) => extname(name) === ".md")) {
  const source = readFileSync(path, "utf8");
  const hit = source.match(latex);
  assert.ok(!hit, `${path.slice(root.length + 1)}: raw LaTeX ${hit?.[0]} — the course pipeline has no math renderer; use inline code or a text block`);
  markdownCount++;
}

const pages = [...readdirSync(output).filter((file) => extname(file) === ".html").map(name => join(output, name)), join(root, "开始阅读.html")];
for (const path of pages) {
  const name = basename(path);
  const html = readFileSync(path, "utf8");
  assert.equal((html.match(/<h1[\s>]/g) ?? []).length, 1, `${name}: expected one h1`);
  const assets = new Set([path]);
  for (const match of html.matchAll(/\s(?:href|src)="([^"]+)"/g)) {
    const target = match[1];
    if (target.startsWith("data:")) {
      assert.equal(name, "review-guide.html", "Unexpected inline download");
      assert.equal(target, "data:application/json;base64," + Buffer.from(readFileSync(join(output, "review-record.json"))).toString("base64"), "Record download differs from the generated blank template");
      continue;
    }
    if (/^(?:https?:|mailto:|#)/.test(target)) continue;
    const local = resolve(dirname(path), target.split("#")[0]);
    assert.ok(existsSync(local), `${name}: missing link ${target}`);
    links++;
    assets.add(local);
  }
  const css = join(output, "lab.css");
  assets.add(join(root, "design/system/tokens.css"));
  assert.ok(readFileSync(css, "utf8").includes("prefers-reduced-motion"));
  let size = 0;
  for (const asset of assets) {
    if ([".html", ".js", ".css", ".svg"].includes(extname(asset))) size += gzipSync(readFileSync(asset)).length;
  }
  assert.ok(size <= 500 * 1024, `${name}: exceeds 500KB compressed budget`);
  console.log(`${name}: local links resolved, compressed page resources ${(size / 1024).toFixed(1)} KB`);
}
assert.ok(existsSync(join(root, "book/llm/fixtures/js-tiktoken-LICENSE")), "Missing tokenizer license");
console.log(`Course metadata, fixture branches, ${figureCount} chapter SVGs, ${assetsSvg.length} asset SVGs, ${markdownCount} Markdown sources without raw LaTeX and ${links} local links passed`);
