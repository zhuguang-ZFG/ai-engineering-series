# Build caption groups on the TTS engine's own word timings.
#   tools/tts_words.py caches [[start, end, word], ...] per voice clip from
#   edge-tts WordBoundary events, proven against the shipped WAV duration.
#   The shown text is the script minus clause punctuation, so it walks the same
#   characters in the same order; each displayed character takes the time of the
#   spoken character it came from. No character-ratio model, no VAD, no drift.
#   Clauses are packed into 4-8 character groups snapped to clause ends.
# Output: compositions/captions.html (groups inlined, global timeline times).
import json, os, re, glob
import soundfile as sf

OFFSETS = {
    "s1-hook": 0.0,
    "s2-why": 19.324,
    "s3-build": 43.304,
    "s4-host": 68.988,
    "s5-phone": 93.472,
    "s6-update": 115.868,
    "s7-pitfall": 138.336,
    "s8-next": 164.068,
}

PUNCT = (r"(?:[，。！？、；：—\,!\?]+"
         r"|(?<![A-Za-z0-9_])\.+(?![A-Za-z0-9_])"
         r"|(?<![A-Za-z0-9])-+"
         r"|-+(?![A-Za-z0-9]))")

WORD_CH = set("-_.")


def clauses(text):
    # keep latin/digits verbatim: they are spoken and must be shown; a hyphen
    # inside a latin token (easy-vibe) is part of the word, not a boundary
    t = " ".join(text.split())
    parts = [p for p in re.split(PUNCT, t) if p.strip()]
    return [" ".join(p.split()) for p in parts]


def load_words(seg_wav):
    path = seg_wav[:-4] + ".words.json"
    if not os.path.exists(path):
        raise SystemExit(f"{path} missing - run tools/tts_words.py first")
    words = json.load(open(path, encoding="utf-8"))
    if not words:
        raise SystemExit(f"{path} is empty")
    dur = sf.info(seg_wav).duration
    if words[-1][1] > dur + 1e-6:
        raise SystemExit(f"{path} outruns {seg_wav} ({words[-1][1]:.3f} > {dur:.3f})")
    return words


# characters the viewer never sees: the clause splitters plus spacing. The
# spoken stream carries them (attached to words), the shown stream does not, so
# the walk below steps over them instead of demanding a character match.
SKIPPABLE = set("\u3000 \t\n\u00a0")


def skippable(ch):
    """True for characters the engine never speaks: separators and spacing."""
    return ch in SKIPPABLE or not (ch.isalnum() or ch in WORD_CH or ch.isalpha())


def tolerable(ch):
    """Like skippable, plus the token punctuation the engine sometimes drops
    while pronouncing a name ('style.css' is spoken as 'style' + 'css')."""
    return skippable(ch) or ch in WORD_CH


def align(seg_wav, seg_txt):
    """Lay the shown text on the TTS engine's own word timings.

    Every spoken word carries [start, end]; its characters are spread inside
    that span. The shown text is the same script with clause punctuation gone,
    so it advances through the spoken stream one character at a time and each
    displayed character inherits its source character's timestamp.
    """
    words = load_words(seg_wav)
    spoken = []                       # (char, wall second) in speaking order
    for start, end, text in words:
        cc = [c for c in text if not skippable(c)]
        if not cc:
            continue
        for k, ch in enumerate(cc):
            spoken.append((ch, start + (end - start) * (k + 0.5) / len(cc)))
    cls = clauses(seg_txt)
    shown = [(ch, k == len(c) - 1) for c in cls for k, ch in enumerate(c)]
    chars = []
    pending = []                      # chars awaiting the next syllable's time
    si = 0
    for ch, clause_end in shown:
        if ch != " ":
            while si < len(spoken) and spoken[si][0] != ch and skippable(spoken[si][0]):
                si += 1
        if ch != " " and (si >= len(spoken) or spoken[si][0] != ch):
            if not tolerable(ch):
                raise SystemExit(
                    f"{seg_wav}: shown text diverges from the spoken script near "
                    f"'{''.join(c for c, _, _ in chars)[-10:]}' "
                    "(word timings and voice script disagree)")
            # a dot or hyphen the engine dropped while pronouncing the token
            chars.append([ch, None, clause_end])
            pending.append(len(chars) - 1)
            continue
        if ch == " ":
            # a space has no time of its own: it inherits the next syllable
            chars.append([ch, None, clause_end])
            pending.append(len(chars) - 1)
            continue
        t = spoken[si][1]
        si += 1
        for pi in pending:
            chars[pi][1] = t
        pending.clear()
        chars.append([ch, t, clause_end])
    for pi in pending:                # trailing punctuation inherits the last one
        chars[pi][1] = next(c[1] for c in reversed(chars) if c[1] is not None)
    return [(ch, t, ce) for ch, t, ce in chars]


def pack(chars, off, groups):
    cur, cur_start = [], None
    def flush():
        nonlocal cur, cur_start
        if cur:
            groups.append({"text": "".join(ch for ch, _ in cur),
                           "start": round(off + cur_start, 3),
                           "end": round(off + cur[-1][1] + 0.30, 3)})
        cur, cur_start = [], None
    n = len(chars)
    dist = [n + 1] * n                      # chars left until this clause ends
    for k in range(n - 1, -1, -1):
        dist[k] = 1 if chars[k][2] else (dist[k + 1] + 1 if k + 1 < n else 1)
    for k, (ch, t, ce) in enumerate(chars):
        prev = cur[-1][0] if cur else ""
        nxt = chars[k + 1][0] if k + 1 < n else ""
        if ch == " ":
            if not cur:
                continue          # never start a group with a space
            latin_nb = (prev.isascii() and prev.isalnum()
                        and nxt.isascii() and nxt.isalnum())
            next_latin = nxt.isascii() and (nxt.isalnum() or nxt in WORD_CH)
            if len(cur) >= 7 and not latin_nb and dist[k] > 4:
                flush()           # the space is the boundary; drop it
                continue
            if len(cur) >= 2 and next_latin and not latin_nb and dist[k] > 4:
                flush()           # don't glue a CJK phrase onto a latin token
                continue
        latin_split = (prev.isascii() and (prev.isalnum() or prev in WORD_CH)
                       and ch.isascii() and (ch.isalnum() or ch in WORD_CH))
        if (cur and len(cur) >= 8 and not latin_split and ch != " "
                and prev != " " and dist[k] >= 5):
            flush()
        if (cur and len(cur) >= 14 and not latin_split and ch != " "
                and prev != " "):
            flush()               # hard cap: a latin token can't overflow the pill
        if not cur:
            cur_start = t
        cur.append((ch, t))
        if ce or k == n - 1:
            flush()
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
def glue(a, b):
    # keep two latin tokens from fusing into one word when groups are merged
    if (a and b and a[-1].isascii() and a[-1].isalnum()
            and b[0].isascii() and b[0].isalnum()):
        return a + " " + b
    return a + b


merged = []
for g in groups:
    if len(g["text"]) < 2 and merged and g["start"] - merged[-1]["end"] < 0.6:
        merged[-1]["text"] = glue(merged[-1]["text"], g["text"])
        merged[-1]["end"] = g["end"]
    elif (merged and g["end"] - g["start"] < 0.40
          and g["start"] - merged[-1]["end"] < 0.20
          and len(merged[-1]["text"]) + len(g["text"]) <= 14):
        # a sub-0.4s flash is unreadable: fold it into the preceding group
        merged[-1]["text"] = glue(merged[-1]["text"], g["text"])
        merged[-1]["end"] = g["end"]
    else:
        merged.append(g)
groups = [g for g in merged if g["end"] > g["start"] + 0.05]
for g in groups:
    if g["start"] < 0.1:
        g["start"] = 0.1

# guard: every scene's cues must land on that scene's audio. A cue list that
# stops early is the "字幕和配音对不上" failure — and every cue before it drifts
# by the same amount, because the dropped time is the scene's pause budget.
for seg, off in OFFSETS.items():
    dur = sf.info(f"assets/voice/{seg}.wav").duration
    inside = [g for g in groups if off <= g["start"] < off + dur]
    assert inside, f"{seg}: no cues inside the clip"
    late_by = dur - (max(g["end"] for g in inside) - off)
    assert abs(late_by) <= 0.6, f"{seg}: last cue ends {late_by:+.2f}s off its audio"

print("TOTAL groups:", len(groups))
print("first:", groups[0])
print("last:", groups[-1])
assert all(groups[i]["end"] <= groups[i + 1]["start"] + 1e-6 for i in range(len(groups) - 1)), "overlap!"

data = json.dumps(groups, ensure_ascii=False)
tpl = open("tools/captions.template.html", encoding="utf-8").read()
html = tpl.replace("__DATA__", data)
open("compositions/captions.html", "w", encoding="utf-8", newline="\n").write(html)
print("wrote compositions/captions.html", len(html), "bytes")
