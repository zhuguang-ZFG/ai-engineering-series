# Transcribe all 11 voice segments with faster-whisper (word-level, zh).
# Output: assets/transcripts/<seg>.json  [{id,text,start,end}, ...] local to the segment.
import json, os, glob
import numpy as np
import soundfile as sf
from faster_whisper import WhisperModel

model = WhisperModel("small", device="cpu", compute_type="int8")
os.makedirs("assets/transcripts", exist_ok=True)

for wav in sorted(glob.glob("assets/voice/s*.wav")):
    base = os.path.basename(wav)[:-4]
    out = f"assets/transcripts/{base}.json"
    if os.path.exists(out):
        print(base, "cached", flush=True)
        continue
    audio, sr = sf.read(wav)
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    audio = audio.astype(np.float32)
    if sr != 16000:
        from scipy.signal import resample_poly
        audio = resample_poly(audio, 16000, sr).astype(np.float32)
    segments, info = model.transcribe(audio, language="zh", word_timestamps=True, beam_size=5)
    words = []
    i = 0
    for seg in segments:
        for w in (seg.words or []):
            t = (w.word or "").strip()
            if not t:
                continue
            words.append({"id": f"w{i}", "text": t, "start": round(w.start, 3), "end": round(w.end, 3)})
            i += 1
    with open(out, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False)
    print(base, len(words), "words", flush=True)
print("TRANSCRIBE_DONE", flush=True)
