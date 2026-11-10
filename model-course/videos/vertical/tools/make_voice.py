# Synthesise every assets/voice/<scene>.txt with the house voice.
#
# edge-tts streams MP3; the clips shipped by this project are 24 kHz mono PCM,
# so the payload is decoded before it lands. The same stream carries the
# engine's own WordBoundary events, and those are written next to the clip as
# <scene>.words.json — the caption builder times its groups from them instead of
# estimating speech from characters.
#
# Re-run when a script changes: index.html derives every scene duration from the
# lengths these files end up with, so the timeline has to be recut afterwards.
import asyncio, glob, json, os, subprocess, sys
import edge_tts

VOICE = "zh-CN-XiaoxiaoNeural"
RATE = "+0%"


async def synth(text):
    comm = edge_tts.Communicate(text, VOICE, rate=RATE, boundary="WordBoundary")
    audio = bytearray()
    words = []
    async for chunk in comm.stream():
        if chunk["type"] == "audio":
            audio += chunk["data"]
        elif chunk["type"] == "WordBoundary":
            start = chunk["offset"] / 1e7
            words.append([round(start, 3),
                          round(start + chunk["duration"] / 1e7, 3),
                          chunk["text"]])
    if not audio:
        sys.exit("no audio returned")
    if not words:
        sys.exit("no WordBoundary events; cannot time captions")
    return bytes(audio), words


def main():
    for txt in sorted(glob.glob("assets/voice/*.txt")):
        stem = os.path.basename(txt)[:-4]
        wav = f"assets/voice/{stem}.wav"
        mp3, words = asyncio.run(synth(open(txt, encoding="utf-8").read()))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "pipe:0",
                        "-ar", "24000", "-ac", "1", "-c:a", "pcm_s16le", wav],
                       input=mp3, check=True)
        json.dump(words, open(f"assets/voice/{stem}.words.json", "w",
                              encoding="utf-8", newline="\n"), ensure_ascii=False)
        print(f"{stem:12s} -> {wav} {os.path.getsize(wav)} bytes "
              f"words={len(words)} last_end={words[-1][1]:.3f}", flush=True)


if __name__ == "__main__":
    main()
