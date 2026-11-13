// Build the spoken track for the two LLM explainers and mux it into the
// delivered MP4s. Narration text comes from scripts/llm/build-media.mjs via
// videos/<project>/narration.json; this script only turns it into sound.
//
// Voice: Microsoft Huihui (zh-CN SAPI). Output: 48 kHz stereo AAC, one 10.8 s
// slot per scene, total 32.4 s, so the picture never has to be re-timed.
import { readFileSync, writeFileSync, copyFileSync, mkdtempSync, rmSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { resolve, join } from "node:path";
import { tmpdir } from "node:os";

const root = resolve(import.meta.dirname, "../..");
const projects = ["llm-principles", "llm-applications"];
const SLOT = 10.8;
const TOTAL = 32.4;
const VOICE = "Microsoft Huihui Desktop";
const checking = process.argv.includes("--check");

const run = (command, args) => {
  const result = spawnSync(command, args, { encoding: "utf8" });
  if (result.status !== 0) throw new Error(`${command} failed: ${result.stderr || result.stdout}`);
  return result.stdout;
};

const durationOf = file => Number(run("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", file]).trim());

function speak(text, wav) {
  const quoted = value => value.replace(/'/g, "''");
  const script = [
    "Add-Type -AssemblyName System.Speech",
    "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer",
    `$s.SelectVoice('${VOICE}')`,
    "$s.Rate = 1",
    `$s.SetOutputToWaveFile('${quoted(wav)}')`,
    `$s.Speak('${quoted(text)}')`,
    "$s.Dispose()"
  ].join("; ");
  run("powershell", ["-NoProfile", "-Command", script]);
}

for (const project of projects) {
  const deliverable = join(root, "deliverables", `${project}.mp4`);
  if (checking) {
    const audio = run("ffprobe", ["-v", "error", "-select_streams", "a", "-show_entries", "stream=codec_name,sample_rate,channels", "-of", "csv=p=0", deliverable]).trim();
    if (audio !== "aac,48000,2") throw new Error(`${project}: expected aac/48000/2, found "${audio}"`);
    console.log(`${project}: ${audio}`);
    continue;
  }

  const narration = JSON.parse(readFileSync(join(root, "videos", project, "narration.json"), "utf8"));
  const work = mkdtempSync(join(tmpdir(), `narrate-${project}-`));
  try {
    const slots = narration.map((entry, index) => {
      const wav = join(work, `${index}.wav`);
      speak(entry.text, wav);
      const spoken = durationOf(wav);
      if (spoken > SLOT - 0.5) throw new Error(`${project}/${entry.id}: narration ${spoken.toFixed(2)}s does not fit a ${SLOT}s slot`);
      const slot = join(work, `${index}.slot.wav`);
      run("ffmpeg", ["-y", "-v", "error", "-i", wav, "-af", `adelay=400|400,apad=whole_dur=${SLOT},atrim=0:${SLOT}`, "-ar", "48000", "-ac", "2", slot]);
      return slot;
    });
    const list = join(work, "list.txt");
    writeFileSync(list, slots.map(path => `file '${path.replace(/\\/g, "/")}'`).join("\n"));
    const track = join(work, "narration.m4a");
    run("ffmpeg", ["-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", list, "-af", `apad=whole_dur=${TOTAL},atrim=0:${TOTAL}`, "-ar", "48000", "-ac", "2", "-c:a", "aac", "-b:a", "160k", track]);
    const staged = join(work, "muxed.mp4");
    run("ffmpeg", ["-y", "-v", "error", "-i", deliverable, "-i", track, "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "copy", "-shortest", "-movflags", "+faststart", staged]);
    copyFileSync(staged, deliverable);
    const probe = JSON.parse(run("ffprobe", ["-v", "error", "-show_entries", "stream=codec_type,codec_name,sample_rate,channels:format=duration", "-of", "json", deliverable]));
    console.log(`${project}: ${probe.streams.map(s => `${s.codec_type}:${s.codec_name}${s.sample_rate ? `/${s.sample_rate}/${s.channels}` : ""}`).join(" ")} ${probe.format.duration}s`);
  } finally {
    rmSync(work, { recursive: true, force: true });
  }
}
