import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { createHash } from "node:crypto";
import { Tiktoken } from "js-tiktoken/lite";
import cl100k from "js-tiktoken/ranks/cl100k_base";
import o200k from "js-tiktoken/ranks/o200k_base";

// Read bytes from the public rank data, rather than decoding individual tokens
// to strings: a token may contain only part of a UTF-8 character.
export function rankBytes(ranks) {
  const result = new Map();
  for (const line of ranks.bpe_ranks.split("\n").filter(Boolean)) {
    const [first, offset, ...encoded] = line.split(" ");
    encoded.forEach((value, index) => {
      result.set(Number(offset) + index, [...Buffer.from(value, "base64")]);
    });
    if (first !== "!") throw new Error("Unsupported rank data format");
  }
  return result;
}

const inputs = [
  { id: "english", label: "英文与空格", text: "Hello, world!\n" },
  { id: "chinese", label: "一句中文", text: "今天天气真不错！" },
  { id: "mixed", label: "中英文混合", text: "我用 AI 写了一封 email。" },
  { id: "unicode", label: "生僻字与 emoji", text: "龘 👩🏽‍💻 e\u0301" },
];
const fixtures = {
  id: "X01", kind: "recorded", source: "js-tiktoken rank data (MIT)",
  version: "js-tiktoken@1.0.21", capturedOn: "2026-11-06",
  limitations: "锁定文本的本地编码快照，不运行语言模型；两种编码不代表所有模型。",
  expectedObservations: ["分词数依编码而变", "token 可包含部分 UTF-8 字节", "拼接字节能无损还原输入"],
  encodings: {},
};
const legacy = {
  id: "A06",
  kind: "recorded",
  source: "js-tiktoken rank data (MIT)",
  version: fixtures.version,
  capturedOn: "2026-11-07",
  text: "The quick brown fox jumps over the lazy dog. \n今天天气真不错！",
  limitations: "旧章原始混合输入的本地复算，不代表任何在线产品当前的编码。",
  encodings: {}
};
for (const [name, ranks] of [["cl100k_base", cl100k], ["o200k_base", o200k]]) {
  const encoder = new Tiktoken(ranks);
  const bytes = rankBytes(ranks);
  fixtures.encodings[name] = {
    rankSha256: createHash("sha256").update(ranks.bpe_ranks).digest("hex"),
    examples: inputs.map((input) => {
      const tokens = encoder.encode(input.text).map((id) => {
        const raw = bytes.get(id);
        if (!raw) throw new Error(`No bytes for ${name}:${id}`);
        let label;
        try { label = new TextDecoder("utf-8", { fatal: true }).decode(Uint8Array.from(raw)); }
        catch { label = "〈字节片段〉"; }
        return { id, bytes: raw, label };
      });
      const restored = Buffer.from(tokens.flatMap((token) => token.bytes)).toString("utf8");
      if (restored !== input.text || encoder.decode(tokens.map((token) => token.id)) !== input.text) {
        throw new Error(`Roundtrip failed: ${name}/${input.id}`);
      }
      return { ...input, codePoints: [...input.text].length, utf8Bytes: Buffer.byteLength(input.text), tokens };
    }),
  };
  const tokens = encoder.encode(legacy.text).map(id => ({ id, bytes: bytes.get(id) }));
  if (Buffer.from(tokens.flatMap(token => token.bytes)).toString("utf8") !== legacy.text || encoder.decode(tokens.map(token => token.id)) !== legacy.text) throw new Error(`Legacy roundtrip failed: ${name}`);
  legacy.encodings[name] = { rankSha256: fixtures.encodings[name].rankSha256, tokens };
}
for (const [file, data] of [["tokens", fixtures], ["legacy-tokenization", legacy]]) {
  const target = new URL(`../../book/llm/fixtures/${file}.json`, import.meta.url);
  const serialized = JSON.stringify(data, null, 2) + "\n";
  if (process.argv.includes("--check")) {
    if (readFileSync(target, "utf8") !== serialized) throw new Error(`${file} fixtures are stale; run npm run fixtures:llm`);
  } else {
    mkdirSync(new URL("../../book/llm/fixtures/", import.meta.url), { recursive: true });
    writeFileSync(target, serialized);
  }
}
console.log(`${process.argv.includes("--check") ? "Verified" : "Wrote"} four course examples and original mixed input × two encodings; byte roundtrips passed`);
