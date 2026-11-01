# -*- coding: utf-8 -*-
"""Synth ch02 long VO segments (Yunyang) for later densify. No publish."""
from __future__ import annotations
import asyncio, re
from pathlib import Path

ROOT = Path(r"D:\Users\claude\claude-code-book-main\video\ch02")
SRC = ROOT / "assets" / "vo" / "full-script.txt"
OUT = ROOT / "assets" / "vo"
OUT.mkdir(parents=True, exist_ok=True)

text = SRC.read_text(encoding="utf-8").strip()
# split into ~120-180 char chunks on sentence ends
parts: list[str] = []
buf = ""
for ch in text:
    buf += ch
    if ch in "。！？；" and len(buf) >= 90:
        parts.append(buf.strip())
        buf = ""
if buf.strip():
    parts.append(buf.strip())
# merge tiny tails
merged = []
for p in parts:
    if merged and len(p) < 40:
        merged[-1] += p
    else:
        merged.append(p)
parts = merged
(OUT / "chunks.json").write_text(
    __import__("json").dumps([{"i": i, "text": p, "chars": len(p)} for i, p in enumerate(parts)], ensure_ascii=False, indent=2),
    encoding="utf-8",
)
print(f"chunks={len(parts)} total_chars={sum(len(p) for p in parts)}")

async def one(i: int, p: str) -> None:
    import edge_tts
    mp3 = OUT / f"c{i:03d}.mp3"
    txt = OUT / f"c{i:03d}.txt"
    txt.write_text(p, encoding="utf-8")
    srt = OUT / f"c{i:03d}.srt"
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
    # rough srt from word boundaries
    srt_lines = []
    # group ~12 chars
    cur = []
    start = None
    idx = 1
    def fmt(t_100ns: int) -> str:
        ms = t_100ns / 10000
        h = int(ms // 3600000); ms %= 3600000
        m = int(ms // 60000); ms %= 60000
        s = int(ms // 1000); ms = int(ms % 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
    for w in words:
        if start is None:
            start = w["offset"]
        cur.append(w)
        if sum(len(x["text"]) for x in cur) >= 14:
            end = cur[-1]["offset"] + cur[-1]["duration"]
            srt_lines.append(f"{idx}\n{fmt(start)} --> {fmt(end)}\n{''.join(x['text'] for x in cur)}\n")
            idx += 1
            cur = []
            start = None
    if cur:
        end = cur[-1]["offset"] + cur[-1]["duration"]
        srt_lines.append(f"{idx}\n{fmt(start)} --> {fmt(end)}\n{''.join(x['text'] for x in cur)}\n")
    srt.write_text("\n".join(srt_lines), encoding="utf-8")
    print(f"ok {mp3.name} bytes={mp3.stat().st_size}")

async def main():
    for i, p in enumerate(parts):
        await one(i, p)
        await asyncio.sleep(0.2)

asyncio.run(main())
print("LONG VO DONE")