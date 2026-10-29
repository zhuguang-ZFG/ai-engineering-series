import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { extname, join, relative, resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const failures = [];
const notes = [];

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
    if (entry.isDirectory()) out.push(...walk(absolute));
    else out.push(absolute);
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
  const chapters = markdown.match(/^###\s+/gm)?.length ?? 0;
  if (chapters < 190) fail(`Expected at least 190 assembled chapters, found ${chapters}`);
  const staleImages = markdown.match(/!\[[^\]]*\]\(\.\.\/easy-vibe\/docs\//g)?.length ?? 0;
  if (staleImages) fail(`Found ${staleImages} unresolved upstream image paths`);
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
  if (!index.includes(`data-duration="${expected.duration}"`)) fail(`${prefix} root duration mismatch`);
  if (!index.includes(`data-width="${expected.width}"`) || !index.includes(`data-height="${expected.height}"`)) {
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
  if (audio?.codec_name !== "aac" || audio?.sample_rate !== "48000" || audio?.channels !== 2) {
    fail(`${path} must contain 48 kHz stereo AAC audio`);
  }
  if (Math.abs(duration - expected.duration) > 0.05) fail(`${path} duration ${duration}s does not match ${expected.duration}s`);
  notes.push(`${path}: ${video.width}x${video.height}, ${duration.toFixed(1)}s, H.264 + AAC`);
}

function validateCleanTree() {
  const forbidden = [".hyperframes", ".thumbnails", ".waveform-cache", "archive", "node_modules"];
  for (const path of walk(root)) {
    const normalized = relative(root, path).replaceAll("\\", "/");
    if (forbidden.some((part) => normalized.split("/").includes(part))) fail(`Forbidden generated path committed: ${normalized}`);
  }
}

validateBook();
validateVideoSource("landscape", { width: 1920, height: 1080, duration: 215.5, minimumCompositions: 8 });
validateVideoSource("vertical", { width: 1080, height: 1920, duration: 39.5, minimumCompositions: 3 });
validateDelivery("deliverables/vibe-coding-101-landscape.mp4", { width: 1920, height: 1080, duration: 215.5, minimumBytes: 10_000_000 });
validateDelivery("deliverables/vibe-coding-101-vertical.mp4", { width: 1080, height: 1920, duration: 39.5, minimumBytes: 1_500_000 });
requireFile("deliverables/landscape-cover.webp", 10_000);
requireFile("deliverables/vertical-cover.webp", 10_000);
validateCleanTree();

for (const note of notes) console.log(`✓ ${note}`);
if (failures.length) {
  for (const failure of failures) console.error(`✗ ${failure}`);
  process.exit(1);
}
console.log("✓ Repository validation passed");
