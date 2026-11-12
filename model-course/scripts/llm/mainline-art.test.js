// The seven running-example drawings may only carry numbers that the spec
// already publishes; a silent drift between picture and prose would teach a
// reader two different models.
import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { mainlineArtworks } from "./mainline-art.mjs";

const read = path => readFileSync(new URL(path, import.meta.url), "utf8").replaceAll("−", "-");
// A drawing may quote the spec or the chapter that draws it; both are checked
// so a number can never appear only inside an SVG.
const corpus = [
  read("../../specs/llm-running-example.md"),
  read("../../book/llm/guide.md"),
  ...["c05", "c06", "c07", "c08", "c09", "c10"].map(name => read(`../../book/llm/lessons/${name}.md`))
].join("\n");
const published = new Set((corpus.match(/-?\d+\.\d+/g) ?? []).map(value => Number(value).toFixed(4)));
const palette = new Set(["#26221B", "#5C5448", "#E3D8C1", "#F3EAD8", "#B4472F", "#FFFDF8"]);

test("every drawn number is published by the running-example spec", () => {
  for (const [file, svg] of mainlineArtworks) {
    assert.ok(svg.includes("<title") && svg.includes("<desc"), `${file}: missing accessible name`);
    assert.ok(!/width="480" height="\d+"[^>]*>\s*<rect width="480"/.test(svg), `${file}: plate fill returned`);
    for (const color of svg.match(/#[0-9a-fA-F]{6}/g) ?? []) {
      assert.ok(palette.has(color.toUpperCase().replace("#26221B", "#26221B")) || palette.has(color), `${file}: off-palette colour ${color}`);
    }
    const labels = [...svg.replaceAll("−", "-").matchAll(/<text[^>]*>([^<]*)<\/text>/g)].map(match => match[1]).join(" ");
    const numbers = labels.match(/-?\d+\.\d{2,6}/g) ?? [];
    for (const value of new Set(numbers)) {
      assert.ok(published.has(Number(value).toFixed(4)), `${file}: ${value} is not published by the spec or its chapter`);
    }
  }
});

test("the quantitative drawings keep their numbers on the page", () => {
  const withNumbers = mainlineArtworks.filter(([, svg]) =>
    (/<text[^>]*>[^<]*\d+\.\d{2,6}[^<]*<\/text>/.test(svg)));
  // six of the seven drawings are numeric; the four-lever page is conceptual
  assert.ok(withNumbers.length >= 6, `only ${withNumbers.length} drawings carry numbers`);
});

test("the drawings stay distinct files with one title each", () => {
  const files = mainlineArtworks.map(([file]) => file);
  assert.equal(new Set(files).size, files.length);
  for (const [file, svg] of mainlineArtworks) {
    assert.equal((svg.match(/<title/g) ?? []).length, 1, `${file}: multiple titles`);
    assert.ok(svg.startsWith("<svg xmlns"), `${file}: not a standalone svg`);
  }
});
