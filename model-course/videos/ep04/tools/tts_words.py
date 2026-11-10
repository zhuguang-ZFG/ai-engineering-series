# Cache the TTS engine's own word timings for every voice clip.
#
# edge-tts streams WordBoundary events alongside the audio: the offset/duration
# of each spoken word. Those are the ground truth for cue placement — better
# than any estimate derived from characters, VAD, or an external ASR pass.
#
# The WAVs in assets/voice/ were produced by the same text, voice and rate, so
# the synthesis is reproducible; the duration check below proves each cached
# timeline belongs to the shipped audio before anything is written.
#
# Output: assets/voice/<scene>.words.json  =  [[start, end, text], ...]
import asyncio, json, subprocess, sys
import edge_tts, soundfile as sf

VOICE = "zh-CN-XiaoxiaoNeural"
RATE = "+0%"
DURATION_TOLERANCE = 0.03  # seconds; a different take shows up as a longer gap


async def synth_words(text):
    comm = edge_tts.Communicate(text, VOICE, rate=RATE, boundary="WordBoundary")
    words = []
    audio = bytearray()
    async for chunk in comm.stream():
        if chunk["type"] == "audio":
            audio += chunk["data"]
        elif chunk["type"] == "WordBoundary":
            start = chunk["offset"] / 1e7
            words.append([round(start, 3),
                          round(start + chunk["duration"] / 1e7, 3),
                          chunk["text"]])
    return words, bytes(audio)


def main(scenes):
    manifest = {}
    for scene in scenes:
        txt = open(f"assets/voice/{scene}.txt", encoding="utf-8").read()
        wav = f"assets/voice/{scene}.wav"
        words, audio = asyncio.run(synth_words(txt))
        if not words:
            sys.exit(f"{scene}: no WordBoundary events; cannot time captions")
        # prove the regenerated take is the shipped take
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "pipe:0",
                        "-f", "wav", "D:/Temp/tts_probe.wav"],
                       input=audio, check=True)
        got = sf.info("D:/Temp/tts_probe.wav").duration
        shipped = sf.info(wav).duration
        if abs(got - shipped) > DURATION_TOLERANCE:
            sys.exit(f"{scene}: regenerated {got:.3f}s != shipped {shipped:.3f}s; "
                     "voice script or rate changed — recut the video first")
        if words[-1][1] > shipped + 1e-6:
            sys.exit(f"{scene}: last word ends after the audio")
        json.dump(words, open(f"assets/voice/{scene}.words.json", "w",
                              encoding="utf-8", newline="\n"),
                  ensure_ascii=False)
        manifest[scene] = (len(words), round(shipped, 3), words[-1][1])
        print(f"{scene:12s} words={len(words):3d} dur={shipped:6.3f} "
              f"last_word_end={words[-1][1]:6.3f}", flush=True)
    return manifest


if __name__ == "__main__":
    # scene order and offsets live in one place: the caption builder
    import re
    src = open("tools/build_captions_v2.py", encoding="utf-8").read()
    block = re.search(r"OFFSETS = \{(.*?)\}", src, re.S).group(1)
    main(re.findall(r'"([^"]+)":', block))
