import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { extname, join, relative, resolve } from "node:path";
import { marked } from "marked";

const root = resolve(import.meta.dirname, "..");
const failures = [];
const notes = [];
const draftStatus = JSON.parse(readFileSync(join(root, "media-status.json"), "utf8")).drafts;
const generatedDirectories = new Set([".git", "node_modules", ".hyperframes", ".thumbnails", ".waveform-cache", "archive", "renders", "tmp", "local-feedback"]);

function fail(message) {
  failures.push(message);
}

function requireFile(path, minimumBytes = 1) {
  const absolute = join(root, path);
  if (!existsSync(absolute)) {
    fail(`Missing required file: ${path}`);
    return null;
  }
  const size = statSync(absolute).size;
  if (size < minimumBytes) fail(`${path} is too small (${size} bytes)`);
  return absolute;
}

function text(path) {
  const absolute = requireFile(path);
  return absolute ? readFileSync(absolute, "utf8") : "";
}

function walk(directory) {
  const out = [];
  for (const entry of readdirSync(directory, { withFileTypes: true })) {
    const absolute = join(directory, entry.name);
    if (entry.isDirectory()) {
      if (!generatedDirectories.has(entry.name)) out.push(...walk(absolute));
    } else out.push(absolute);
  }
  return out;
}

function validateFences(markdown) {
  let open = null;
  for (const [index, line] of markdown.split(/\r?\n/).entries()) {
    const match = line.match(/^(\s*)(`{3,}|~{3,})(.*)$/);
    if (!match) continue;
    const indent = match[1].replaceAll("\t", "    ").length;
    const marker = match[2];
    const rest = match[3].trim();
    if (!open && indent <= 3) {
      open = { char: marker[0], length: marker.length, indent, line: index + 1 };
    } else if (
      open &&
      marker[0] === open.char &&
      marker.length >= open.length &&
      indent <= open.indent + 3 &&
      rest === ""
    ) {
      open = null;
    }
  }
  if (open) fail(`Unclosed Markdown fence opened at line ${open.line}`);
}

function validateBook() {
  requireFile("book/assets/cover.webp", 10_000);
  requireFile("book/assets/cover.svg", 1_000);
  const markdown = text("book/book.md").replace(/^\uFEFF/, "");
  if (Buffer.byteLength(markdown) < 4_000_000) fail("book/book.md is unexpectedly small");
  if (!markdown.startsWith("![Vibe Coding 101 封面](assets/cover.webp)")) fail("Book must begin with the current cover");
  if (!markdown.includes("# Vibe Coding 101：从一句需求到第一个可用作品")) fail("Current book title is missing");
  if (!markdown.includes("## 目录")) fail("Book table of contents is missing");
  const chapters = marked.lexer(markdown).filter(token => token.type === "heading" && token.depth === 3).length;
  if (chapters < 190) fail(`Expected at least 190 assembled chapters, found ${chapters}`);
  const staleImages = markdown.match(/!\[[^\]]*\]\(\.\.\/easy-vibe\/docs\//g)?.length ?? 0;
  if (staleImages) fail(`Found ${staleImages} unresolved upstream image paths`);
  const externalImages = markdown.match(/!\[[^\]]*\]\(https?:\/\//g)?.length ?? 0;
  if (externalImages) fail(`Found ${externalImages} externally hosted images`);
  if (markdown.includes("../easy-vibe/")) fail("Found stale upstream relative paths");
  let localImages = 0;
  for (const match of markdown.matchAll(/!\[[^\]]*\]\((assets\/[^)]+)\)/g)) {
    requireFile(join("book", match[1]));
    localImages += 1;
  }
  for (const match of markdown.matchAll(/src="(assets\/[^"]+)"/g)) {
    requireFile(join("book", match[1]));
    localImages += 1;
  }
  notes.push(`Book images: ${localImages} local references resolved`);
  validateFences(markdown);
  notes.push(`Book: ${chapters} chapter headings, fences balanced`);
}

function validateVideoSource(directory, expected) {
  const prefix = `videos/${directory}`;
  const index = text(`${prefix}/index.html`);
  requireFile(`${prefix}/package.json`, 100);
  requireFile(`${prefix}/hyperframes.json`, 100);
  requireFile(`${prefix}/REVIEW.md`, 1_000);
  const compositionsDir = join(root, prefix, "compositions");
  const assetsDir = join(root, prefix, "assets");
  if (!existsSync(compositionsDir)) fail(`Missing ${prefix}/compositions`);
  if (!existsSync(assetsDir)) fail(`Missing ${prefix}/assets`);
  const rootTag = index.match(/<div\b[^>]*\sid="root"[^>]*>/)?.[0] ?? "";
  const draft = draftStatus.find((item) => item.project === directory);
  const expectedDuration = draft?.sourceDuration ?? expected.duration;
  if (Number(rootTag.match(/\sdata-duration="([^"]+)"/)?.[1]) !== expectedDuration) fail(`${prefix} root duration mismatch`);
  if (!rootTag.includes(`data-width="${expected.width}"`) || !rootTag.includes(`data-height="${expected.height}"`)) {
    fail(`${prefix} root dimensions mismatch`);
  }
  if (!index.includes('window.__timelines["main"]')) fail(`${prefix} does not register its main timeline`);
  const htmlFiles = existsSync(compositionsDir)
    ? readdirSync(compositionsDir, { withFileTypes: true })
        .filter((entry) => entry.isFile() && extname(entry.name) === ".html")
        .map((entry) => join(compositionsDir, entry.name))
    : [];
  if (htmlFiles.length < expected.minimumCompositions) fail(`${prefix} has too few compositions (${htmlFiles.length})`);
  for (const file of htmlFiles) {
    const body = readFileSync(file, "utf8");
    if (!body.includes("<template>")) fail(`${relative(root, file)} is missing <template>`);
    if (!body.includes("window.__timelines")) fail(`${relative(root, file)} is missing timeline registration`);
  }
  notes.push(`${directory}: ${htmlFiles.length} editable compositions`);
  if (draft) {
    if (draft.status !== "awaiting-render-and-review" || !draft.reason || !Number.isFinite(draft.sourceDuration)) fail(`${prefix}: invalid draft status`);
    notes.push(`DRAFT ${directory}: source ${draft.sourceDuration}s, existing delivery ${draft.deliveryDuration}s; NOT synchronized or re-rendered (media-status.json)`);
  }
}

function ffprobe(path) {
  const command = spawnSync(
    "ffprobe",
    [
      "-v", "error",
      "-show_entries", "format=duration,size",
      "-show_entries", "stream=codec_name,codec_type,width,height,r_frame_rate,sample_rate,channels",
      "-of", "json",
      path,
    ],
    { encoding: "utf8" },
  );
  if (command.error || command.status !== 0) {
    fail(`ffprobe failed for ${relative(root, path)}: ${command.stderr || command.error?.message}`);
    return null;
  }
  return JSON.parse(command.stdout);
}

function validateDelivery(path, expected) {
  const draft = draftStatus.find((item) => item.delivery === path);
  if (draft && draft.deliveryDuration !== expected.duration) fail(`${path}: draft manifest delivery duration differs from validation`);
  const absolute = requireFile(path, expected.minimumBytes);
  if (!absolute) return;
  const data = ffprobe(absolute);
  if (!data) return;
  const video = data.streams.find((stream) => stream.codec_type === "video");
  const audio = data.streams.find((stream) => stream.codec_type === "audio");
  const duration = Number(data.format.duration);
  if (video?.codec_name !== "h264") fail(`${path} must use H.264 video`);
  if (video?.width !== expected.width || video?.height !== expected.height) fail(`${path} dimensions are incorrect`);
  if (video?.r_frame_rate !== "30/1") fail(`${path} must be 30 fps`);
  if (expected.audio === false && audio) fail(`${path} is declared as a silent illustrated lesson`);
  if (expected.audio !== false && (audio?.codec_name !== "aac" || audio?.sample_rate !== "48000" || audio?.channels !== 2)) {
    fail(`${path} must contain 48 kHz stereo AAC audio`);
  }
  if (Math.abs(duration - expected.duration) > 0.05) fail(`${path} duration ${duration}s does not match ${expected.duration}s`);
  notes.push(`${path}: ${video.width}x${video.height}, ${duration.toFixed(1)}s, H.264${audio ? " + AAC" : " (silent illustrated lesson)"}`);
}

function validateCleanTree() {
  const forbidden = [".hyperframes", ".thumbnails", ".waveform-cache", "archive", "node_modules"];
  const tracked = spawnSync("git", ["ls-files", "-z"], { cwd: root, encoding: "utf8" });
  if (tracked.error || tracked.status !== 0) {
    fail(`Cannot inspect tracked paths: ${tracked.error?.message || tracked.stderr}`);
    return;
  }
  for (const normalized of tracked.stdout.split("\0").filter(Boolean)) {
    if (forbidden.some((part) => normalized.split("/").includes(part))) fail(`Forbidden generated path committed: ${normalized}`);
  }
}

validateBook();
validateVideoSource("landscape", { width: 1920, height: 1080, duration: 250.4, minimumCompositions: 8 });
validateVideoSource("vertical", { width: 1080, height: 1920, duration: 47.5, minimumCompositions: 3 });
validateVideoSource("llm-principles", { width: 1920, height: 1080, duration: 32.4, minimumCompositions: 3 });
validateVideoSource("llm-applications", { width: 1920, height: 1080, duration: 32.4, minimumCompositions: 3 });
validateVideoSource("ep02", { width: 1920, height: 1080, duration: 194.5, minimumCompositions: 8 });
validateVideoSource("ep03", { width: 1920, height: 1080, duration: 191.2, minimumCompositions: 8 });
validateVideoSource("ep04", { width: 1920, height: 1080, duration: 187.472, minimumCompositions: 8 });
validateDelivery("deliverables/vibe-coding-101-landscape.mp4", { width: 1920, height: 1080, duration: 250.4, minimumBytes: 10_000_000 });
validateDelivery("deliverables/vibe-coding-101-vertical.mp4", { width: 1080, height: 1920, duration: 47.5, minimumBytes: 1_500_000 });
validateDelivery("deliverables/llm-principles.mp4", { width: 1920, height: 1080, duration: 32.4, minimumBytes: 100_000, audio: false });
validateDelivery("deliverables/llm-applications.mp4", { width: 1920, height: 1080, duration: 32.4, minimumBytes: 100_000, audio: false });
validateDelivery("deliverables/ep02-landscape.mp4", { width: 1920, height: 1080, duration: 194.5, minimumBytes: 5_000_000 });
validateDelivery("deliverables/ep03-landscape.mp4", { width: 1920, height: 1080, duration: 191.2, minimumBytes: 5_000_000 });
validateDelivery("deliverables/ep04-landscape.mp4", { width: 1920, height: 1080, duration: 187.5, minimumBytes: 5_000_000 });
requireFile("deliverables/landscape-cover.webp", 10_000);
requireFile("deliverables/vertical-cover.webp", 10_000);
requireFile("deliverables/ep02-cover.webp", 10_000);
requireFile("deliverables/ep03-cover.webp", 10_000);
requireFile("deliverables/ep04-cover.webp", 10_000);
function validateNoMachinePaths() {
  const scanned = new Set([".md", ".txt", ".json", ".yml", ".yaml", ".mjs"]);
  const leaks = [];
  for (const path of walk(root)) {
    const parts = relative(root, path).split(/[\\/]/);
    if (parts.includes(".git") || parts[0] === "book") continue;
    if (!scanned.has(extname(path))) continue;
    const body = readFileSync(path, "utf8");
    for (const match of body.matchAll(/(?:[A-Za-z]:[\\/]Users[\\/]|\/home\/|\/Users\/)([^\\/\s`"'）)，。]+)/g)) {
      const account = match[1];
      if (!account) continue;
      if (/^[<\[{$%]/.test(account) || /^[^\x00-\x7F]/.test(account)) continue;
      const line = body.slice(0, match.index).split("\n").length;
      leaks.push(`${relative(root, path).replaceAll("\\", "/")}:${line} ${match[0].trim()}`);
    }
  }
  if (leaks.length) fail(`Machine-specific home paths are committed:\n  ${leaks.slice(0, 10).join("\n  ")}`);
  else notes.push("No machine-specific home paths outside book/ (book/ is the upstream mirror)");
}

validateNoMachinePaths();
validateCleanTree();

for (const note of notes) console.log(`✓ ${note}`);
if (failures.length) {
  for (const failure of failures) console.error(`✗ ${failure}`);
  process.exit(1);
}
console.log("✓ Repository validation passed");
