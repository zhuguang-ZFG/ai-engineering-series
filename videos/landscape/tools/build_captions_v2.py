# Build caption groups from the TTS engine's own word timings.
#
# assets/voice/<scene>.words.json comes from the same edge-tts request that made
# the clip, so every spoken word carries its real start and end. Nothing here is
# estimated from characters: groups break where the reader actually paused, and
# Latin terms (AI, JTBD, Stage 2, Claude Code) stay on screen because the engine
# reports them as words.
#
# WordBoundary drops punctuation, so annotate() walks the narration script to put
# it back; the packer then segments on that punctuation (a clause is never
# chopped) and only splits a clause wider than MAX_W. The last step replays the
# whole script from the groups — if any spoken character went missing, the build
# fails out loud instead of shipping silent gaps.
#
# Output: compositions/captions.html (--list prints the cue sheet, --write builds it).
import json, os, re, sys

# width classes: CJK ideographs, kana and fullwidth marks all occupy one em
CJK = re.compile(r"[　-〿぀-ヿ㐀-䶿一-鿿豈-﫿＀-￯]")
# word classes: only these continue a phrase; everything else is punctuation
WORD = re.compile(r"[぀-ヿ㐀-䶿一-鿿豈-﫿]")
LATIN_TAIL = re.compile(r"[A-Za-z0-9]$")
LATIN_HEAD = re.compile(r"^[A-Za-z0-9]")
THIN = " "  # CJK/Latin boundary, ~1/4 em per design/system/cjk-rules.md

HARD = "。！？；…"
SOFT = "，、：,."
DISPLAY = HARD + SOFT + "——"
DANGLE = "的了是在和与及把被给让向往从到这那每各其之一二三四五六七八九十第地得着吗呢吧啊呀喔啦"
# a continuation group must not open with a resultative complement ("练 / 出来")
LEAD = "出来到完好看见着起上下去成作得极"
MIN_TAIL = 4.0    # never split a segment so thin that a fragment is left behind
MIN_SOLO = 3.0    # a group narrower than this is an orphan, not a beat

MAX_W = float(os.environ.get("CAP_MAX_W", "18.0"))  # 18 CJK units × 46px ≈ 830px on a 1920 stage
TAIL_HOLD = 0.30
MERGE_GAP = 0.12


def offsets_from_index(path="index.html"):
    html = open(path, encoding="utf-8").read()
    found = {}
    for m in re.finditer(r'src="assets/voice/([^."]+)\.wav"\s+data-start="([0-9.]+)"', html):
        found[m.group(1)] = float(m.group(2))
    if not found:
        raise SystemExit("no voice clips found in index.html")
    return found


def width(text):
    return sum(1.0 if CJK.match(ch) else 0.5 for ch in text)


def merge_latin(words):
    out = []
    for start, end, text in words:
        if out:
            ps, pe, pt = out[-1]
            if LATIN_TAIL.search(pt) and LATIN_HEAD.search(text) and start - pe <= MERGE_GAP:
                out[-1] = (ps, end, pt + " " + text)
                continue
        out.append([start, end, text])
    return out


def is_latin(ch):
    return ch.isascii() and (ch.isalnum())


def is_word(ch):
    return bool(WORD.match(ch)) or is_latin(ch)


def sep(before, text):
    if not before:
        return ""
    a, b = before[-1], text[0]
    if not is_word(a):
        return ""              # sitting right after punctuation, which already spaces itself
    if is_latin(a) and is_latin(b):
        return " "
    if is_latin(a) or is_latin(b):
        return THIN
    return ""


def annotate(script, words):
    # WordBoundary drops punctuation; recover it (and quotes) from the script
    src = re.sub(r"\s+", "", script)
    pos = 0
    out = []
    for start, end, text in words:
        w = re.sub(r"\s+", "", text)
        if not w:
            continue
        at = src.find(w, pos)
        if at < 0:
            at = src.find(w)
            if at < 0:
                raise SystemExit(f"word {w!r} not found in the script")
        pos = at + len(w)
        tail = ""
        while pos < len(src) and not is_word(src[pos]):
            tail += src[pos]
            pos += 1
        out.append((start, end, text, tail))
    return out


def keep(tail):
    # the pill background already delimits a line, so quotes and brackets are dropped
    return "".join(ch for ch in tail if ch in DISPLAY)


def join(part):
    text = ""
    for _, _, t, tail in part:
        text += sep(text, t) + t + keep(tail)
    return text


def is_break(tail):
    return any(ch in HARD + SOFT for ch in tail)


def segments(annotated):
    # (words, ends_sentence) — break at any punctuation, HARD ones close a sentence
    cur = []
    for item in annotated:
        cur.append(item)
        if is_break(item[3]):
            yield cur, any(ch in HARD for ch in item[3])
            cur = []
    if cur:
        yield cur, True


def split_wide(part):
    total = width(join(part))
    if total <= MAX_W or len(part) < 2:
        return [part]
    best = None
    run = 0.0
    for i in range(1, len(part)):
        run += width(join([part[i - 1]]))
        if run >= MIN_TAIL and total - run >= MIN_TAIL:
            score = abs(run - (total - run))
            # a forced mid-phrase cut may not strand a modifier ("你的第一个 / 作品")
            # or open on a complement ("练 / 出来") — either reads as a broken line
            if part[i - 1][2][-1] in DANGLE or part[i][2][0] in LEAD:
                score += 25.0
            if best is None or score < best[0]:
                best = (score, i)
    if best is None:
        return [part]
    i = best[1]
    return split_wide(part[:i]) + split_wide(part[i:])


def pack(annotated, off, out):
    cur = []
    cur_t = ""

    def flush():
        nonlocal cur, cur_t
        if not cur:
            return
        out.append({"text": join(cur),
                    "start": round(off + cur[0][0], 3),
                    "end": round(off + cur[-1][1] + TAIL_HOLD, 3)})
        cur, cur_t = [], ""

    for part, ends_sentence in segments(annotated):
        pieces = split_wide(part)
        for k, piece in enumerate(pieces):
            pt = join(piece)
            if cur and width(cur_t) + width(pt) > MAX_W:
                flush()
            cur.extend(piece)
            cur_t = join(cur)
            if ends_sentence and k == len(pieces) - 1:
                flush()
    flush()
    for g in out:
        g["w"] = width(g["text"])


def bare(text):
    # everything that is not a spoken word character: punctuation, quotes, spaces
    return "".join(ch for ch in text if is_word(ch))


def build():
    out = []
    scripts = {}
    OFFSETS = offsets_from_index()
    for seg, off in OFFSETS.items():
        wf = f"assets/voice/{seg}.words.json"
        if not os.path.exists(wf):
            raise SystemExit(f"{wf} missing — run tools/make_voice.py first")
        script = open(f"assets/voice/{seg}.txt", encoding="utf-8").read()
        scripts[seg] = script
        words = merge_latin(json.load(open(wf, encoding="utf-8")))
        pack(annotate(script, words), off, out)

    merged = []
    for g in out:
        if merged and g["w"] < MIN_SOLO and merged[-1]["w"] + g["w"] <= MAX_W + 2.0 \
                and merged[-1]["text"][-1] not in HARD:
            prev = merged[-1]
            prev["text"] += sep(prev["text"], g["text"]) + g["text"]
            prev["w"] = width(prev["text"])
            prev["end"] = g["end"]
            continue
        merged.append(g)
    out = merged

    for i in range(len(out) - 1):
        if out[i]["end"] > out[i + 1]["start"]:
            out[i]["end"] = round(out[i + 1]["start"] - 0.02, 3)
    out = [g for g in out if g["end"] > g["start"]]
    for g in out:
        if g["start"] < 0.1:
            g["start"] = 0.1
    assert all(out[i]["end"] <= out[i + 1]["start"] + 1e-6 for i in range(len(out) - 1)), "overlap!"

    # nothing spoken may vanish: the groups, stripped of punctuation, replay the script
    spoken = bare("".join(scripts.values()))
    shown = bare("".join(g["text"] for g in out))
    if shown != spoken:
        for i in range(min(len(shown), len(spoken))):
            if shown[i] != spoken[i]:
                raise SystemExit(f"caption text diverges at {i}: "
                                 f"{shown[i:i+24]!r} vs {spoken[i:i+24]!r}")
        raise SystemExit(f"caption text is a prefix only ({len(shown)}/{len(spoken)} chars)")
    return out


groups = build()
wide = [g for g in groups if g["w"] > MAX_W + 2.0]
short = [g for g in groups if len(g["text"]) <= 4]
print("TOTAL groups:", len(groups))
print("over-wide:", len(wide), [f'{g["w"]:.1f}:{g["text"]}' for g in wide[:6]])
print("narrow (<=4 chars):", len(short), [g["text"] for g in short[:14]])
print("shortest on-screen:", min(round(g["end"] - g["start"], 2) for g in groups))
print("text integrity: ok")
if "--list" in sys.argv:
    for g in groups:
        print(f"{g['start']:7.2f} → {g['end']:6.2f}  {g['text']}")
if "--write" in sys.argv:
    data = json.dumps([{k: g[k] for k in ("text", "start", "end")} for g in groups],
                      ensure_ascii=False)
    tpl = open("tools/captions.template.html", encoding="utf-8").read()
    open("compositions/captions.html", "w", encoding="utf-8", newline="\n").write(
        tpl.replace("__DATA__", data))
    print("wrote compositions/captions.html")
