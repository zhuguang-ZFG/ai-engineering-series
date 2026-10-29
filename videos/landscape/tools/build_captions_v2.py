# Build caption groups for the film using forced alignment:
#   TTS audio is VAD-segmented into speech blocks; the KNOWN source text is
#   split into clauses; clauses are laid onto the speech-time axis by character
#   ratio (speech time, not wall clock), boundaries snapped to VAD block edges;
#   chars are spread evenly inside each clause. Groups are 4-8 chars.
# Output: compositions/captions.html (groups inlined, global timeline times).
import json, os, re, glob
import numpy as np
import soundfile as sf

OFFSETS = {
    "s1-hook": 0.0,
    "s2-what": 17.2,
    "s3-snake": 46.4,
    "s4-tools": 71.6,
    "s5-clone": 90.2,
    "s6-map": 115.4,
    "s7-myth": 157.2,
    "s8-next": 185.6,
}

def vad_blocks(path, gap_s=0.16, min_s=0.22):
    audio, sr = sf.read(path)
    audio = np.abs(audio.astype(np.float32))
    hop = int(0.01 * sr)
    frames = [audio[i:i + hop].mean() for i in range(0, len(audio), hop)]
    th = max(frames) * 0.10
    speech = [f > th for f in frames]
    n = len(speech); g = int(gap_s / 0.01)
    segs = []; start = None; i = 0
    while i < n:
        if speech[i] and start is None:
            start = i
        elif not speech[i] and start is not None:
            j = i
            while j < n and not speech[j]:
                j += 1
            if j - i < g and j < n:
                i = j
                continue
            segs.append((start * 0.01, i * 0.01)); start = None
            i = j
            continue
        i += 1
    if start is not None:
        segs.append((start * 0.01, n * 0.01))
    return [s for s in segs if s[1] - s[0] >= min_s]

def clauses(text):
    # strip latin/digits (TTS reads them but our clauses skip exact spelling),
    # then split on punctuation
    t = re.sub(r"[A-Za-z0-9]+", " ", text)
    parts = [p for p in re.split(r"[，。！？、；：—\-\.\,\!\?]+", t) if p.strip()]
    return [p.strip() for p in parts]

def align(seg_wav, seg_txt):
    blocks = vad_blocks(seg_wav)
    cls = clauses(seg_txt)
    if not blocks or not cls:
        return []
    # speech-time axis: cumulative speech seconds
    speech_total = sum(b - a for a, b in blocks)
    total_chars = sum(len(c) for c in cls)
    # map speech-time -> wall-clock
    def speech_to_wall(s):
        acc = 0.0
        for a, b in blocks:
            d = b - a
            if s <= acc + d:
                return a + (s - acc)
            acc += d
        return blocks[-1][1]
    # clause boundaries in speech time, snapped to nearest block edge
    edges = [0.0]
    acc = 0.0
    for c in cls[:-1]:
        acc += speech_total * len(c) / total_chars
        edges.append(acc)
    edges.append(speech_total)
    snap_win = 0.35
    block_edges = []
    acc = 0.0
    for a, b in blocks:
        acc += b - a
        block_edges.append(acc)
    def snap(s):
        best, bd = s, 1e9
        for be in block_edges:
            if abs(be - s) < bd:
                best, bd = be, abs(be - s)
        return best if bd <= snap_win else s
    edges = [0.0] + [snap(e) for e in edges[1:-1]] + [speech_total]
    edges = sorted(set(edges))
    if len(edges) != len(cls) + 1:
        # snap caused a merge: fall back to unsnapped
        edges = [0.0]
        acc = 0.0
        for c in cls[:-1]:
            acc += speech_total * len(c) / total_chars
            edges.append(acc)
        edges.append(speech_total)
    # char-level times inside each clause
    chars = []
    for ci, c in enumerate(cls):
        cs, ce = edges[ci], edges[ci + 1]
        n = len(c)
        for k, ch in enumerate(c):
            chars.append((ch, cs + (ce - cs) * k / max(n - 1, 1)))
    return chars

def pack(chars, off, groups):
    cur, cur_start = [], None
    def flush():
        nonlocal cur, cur_start
        if cur:
            groups.append({"text": "".join(ch for ch, _ in cur),
                           "start": round(off + cur_start, 3),
                           "end": round(off + cur[-1][1] + 0.30, 3)})
        cur, cur_start = [], None
    for ch, t in chars:
        if cur and len(cur) >= 8:
            flush()
        if not cur:
            cur_start = t
        cur.append((ch, t))
    flush()

groups = []
for seg, off in OFFSETS.items():
    wav = f"assets/voice/{seg}.wav"
    txt = open(f"assets/voice/{seg}.txt", encoding="utf-8").read()
    chars = align(wav, txt)
    pack(chars, off, groups)
    print(seg, len(chars), "chars", flush=True)

for i in range(len(groups) - 1):
    if groups[i]["end"] > groups[i + 1]["start"]:
        groups[i]["end"] = round(groups[i + 1]["start"] - 0.02, 3)
groups = [g for g in groups if g["end"] > g["start"] + 0.05 and len(g["text"]) >= 2]
for g in groups:
    if g["start"] < 0.1:
        g["start"] = 0.1

print("TOTAL groups:", len(groups))
print("first:", groups[0])
print("last:", groups[-1])
assert all(groups[i]["end"] <= groups[i + 1]["start"] + 1e-6 for i in range(len(groups) - 1)), "overlap!"

data = json.dumps(groups, ensure_ascii=False)
tpl = open("tools/captions.template.html", encoding="utf-8").read()
html = tpl.replace("__DATA__", data)
open("compositions/captions.html", "w", encoding="utf-8", newline="\n").write(html)
print("wrote compositions/captions.html", len(html), "bytes")
