import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import api from "../../../scripts/llm/core.cjs";

function matrix(value) {
  if (!Array.isArray(value) || !value.length || !Array.isArray(value[0]) || !value[0].length ||
      !value.every(row => Array.isArray(row) && row.length === value[0].length && row.every(Number.isFinite))) {
    throw new TypeError("Expected a nonempty rectangular finite matrix");
  }
  return value;
}

export function multiply(left, right) {
  matrix(left);
  matrix(right);
  if (left[0].length !== right.length) throw new RangeError("Matrix dimensions do not match");
  return left.map(row => right[0].map((_, column) => row.reduce((sum, value, i) => sum + value * right[i][column], 0)));
}

export function multihead(input, heads, WO, position) {
  matrix(input);
  if (!Array.isArray(heads) || !heads.length) throw new RangeError("At least one head is required");
  const results = heads.map(({ WQ, WK, WV }) => {
    const Q = multiply(input, WQ);
    const K = multiply(input, WK);
    const V = multiply(input, WV);
    return { Q, K, V, ...api.attention(Q, K, V, position) };
  });
  const concatenated = results.flatMap(head => head.output);
  const output = multiply([concatenated], WO)[0];
  return { position, heads: results, concatenated, output };
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const fixture = JSON.parse(readFileSync(new URL("../fixtures/multihead.json", import.meta.url), "utf8"));
  console.log(JSON.stringify(multihead(fixture.input, fixture.heads, fixture.WO, fixture.position), null, 2));
}
