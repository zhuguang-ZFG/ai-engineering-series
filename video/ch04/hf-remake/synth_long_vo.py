# -*- coding: utf-8 -*-
"""ch04 long densify pipeline step1: extract full-script + synth VO (Yunyang)."""
from __future__ import annotations
import asyncio, json, re
from pathlib import Path

ROOT = Path(r"D:\Users\claude\claude-code-book-main")
SRC = ROOT / "docs/video/ch04/long-script.md"
VO = ROOT / "video/ch04/assets/vo"
VO.mkdir(parents=True, exist_ok=True)

raw = SRC.read_text(encoding="utf-8")
lines = []
for ln in raw.splitlines():
    s = ln.strip()
    if not s:
        lines.append("")
        continue
    if s.startswith("#") or s.startswith(">") or s.startswith("---"):
        continue
    if re.match(r"^\[(ANIM|CODE|QUIZ):", s):
        continue
    if s.startswith("## "):
        continue
    lines.append(s)
text = "\n".join(lines)
text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"
(VO / "full-script.txt").write_text(text, encoding="utf-8")
chars = len(re.sub(r"\s+", "", text))
print(f"full-script chars={chars} bytes={len(text.encode())}")

parts: list[str] = []
buf = ""
for ch in text.replace("\n", ""):
    buf += ch
    if ch in "。！？；" and len(buf) >= 90:
        parts.append(buf.strip())
        buf = ""
if buf.strip():
    parts.append(buf.strip())
merged = []
for p in parts:
    if merged and len(p) < 40:
        merged[-1] += p
    else:
        merged.append(p)
parts = merged
(VO / "chunks.json").write_text(
    json.dumps([{"i": i, "text": p, "chars": len(p)} for i, p in enumerate(parts)], ensure_ascii=False, indent=2),
    encoding="utf-8",
)
print(f"chunks={len(parts)} total_chars={sum(len(p) for p in parts)}")

async def one(i: int, p: str) -> None:
    import edge_tts
    mp3 = VO / f"c{i:03d}.mp3"
    txt = VO / f"c{i:03d}.txt"
    txt.write_text(p, encoding="utf-8")
    srt = VO / f"c{i:03d}.srt"
    if mp3.exists() and mp3.stat().st_size > 1000 and srt.exists() and srt.stat().st_size > 0:
        print(f"skip {mp3.name}")
        return
    words = []
    communicate = edge_tts.Communicate(p, "zh-CN-YunyangNeural", rate="-10%", pitch="-5Hz",
                                   boundary="WordBoundary")
    with open(mp3, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                words.append({"text": chunk["text"], "offset": chunk["offset"], "duration": chunk["duration"]})
    def fmt(t_100ns: int) -> str:
        ms = t_100ns / 10000
        h = int(ms // 3600000); ms %= 3600000
        m = int(ms // 60000); ms %= 60000
        s = int(ms // 1000); ms = int(ms % 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
    srt_lines = []
    cur = []; start = None; idx = 1
    for w in words:
        if start is None:
            start = w["offset"]
        cur.append(w)
        if sum(len(x["text"]) for x in cur) >= 14:
            end = cur[-1]["offset"] + cur[-1]["duration"]
            srt_lines.append(f"{idx}\n{fmt(start)} --> {fmt(end)}\n{''.join(x['text'] for x in cur)}\n")
            idx += 1
            cur = []; start = None
    if cur:
        end = cur[-1]["offset"] + cur[-1]["duration"]
        srt_lines.append(f"{idx}\n{fmt(start)} --> {fmt(end)}\n{''.join(x['text'] for x in cur)}\n")
    srt.write_text("\n".join(srt_lines), encoding="utf-8")
    print(f"ok {mp3.name} bytes={mp3.stat().st_size} words={len(words)}", flush=True)

async def main():
    for i, p in enumerate(parts):
        await one(i, p)
        await asyncio.sleep(0.15)

asyncio.run(main())

import subprocess
segs = []
total = 0.0
for i, p in enumerate(parts):
    f = VO / f"c{i:03d}.mp3"
    pr = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",str(f)], capture_output=True, text=True)
    dur = float(pr.stdout.strip())
    total += dur
    segs.append({"i": i, "text": p, "chars": len(p), "mp3": f"c{i:03d}.mp3", "bytes": f.stat().st_size, "duration_s": round(dur, 3)})
man = {"voice": "zh-CN-YunyangNeural", "rate": "-10%", "pitch": "-5Hz", "count": len(segs), "total_duration_s": round(total, 2), "segments": segs}
no_srt = [s["mp3"] for s in segs if not (VO / s["mp3"]).with_suffix(".srt").is_file()
                or (VO / s["mp3"]).with_suffix(".srt").stat().st_size == 0]
if no_srt:
    raise SystemExit("%d 片字幕为空：edge-tts 7.x 要 boundary='WordBoundary' 才回词级时间：%s"
                   % (len(no_srt), no_srt[:5]))
(VO / "vo-manifest.json").write_text(json.dumps(man, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"LONG VO DONE count={len(segs)} total_s={total:.2f} (~{total/60:.1f} min)")
