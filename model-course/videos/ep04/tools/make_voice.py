# Synthesise every assets/voice/<scene>.txt with the house voice.
#
# edge-tts streams MP3; the shipped files keep that payload under a .wav name
# (24 kHz mono), which is what the previous three episodes do and what
# tools/tts_words.py verifies against. Re-run only when a script changes: the
# WordBoundary cache is tied to the exact take, not to the text alone.
import asyncio, glob, os, sys
import edge_tts

VOICE = "zh-CN-XiaoxiaoNeural"
RATE = "+0%"


async def synth(text, out):
    comm = edge_tts.Communicate(text, VOICE, rate=RATE)
    audio = bytearray()
    async for chunk in comm.stream():
        if chunk["type"] == "audio":
            audio += chunk["data"]
    if not audio:
        sys.exit(f"{out}: no audio returned")
    with open(out, "wb") as f:
        f.write(audio)


def main():
    scenes = sorted(glob.glob("assets/voice/*.txt"))
    for txt in scenes:
        stem = os.path.basename(txt)[:-4]
        wav = f"assets/voice/{stem}.wav"
        text = open(txt, encoding="utf-8").read()
        asyncio.run(synth(text, wav))
        print(f"{stem:12s} -> {wav} {os.path.getsize(wav)} bytes", flush=True)


if __name__ == "__main__":
    main()
