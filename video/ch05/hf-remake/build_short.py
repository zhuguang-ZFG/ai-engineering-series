# -*- coding: utf-8 -*-
"""ch05 short-v1: 一个文件 vs 六层岩 · hard A/V sync off the TTS phrase times. No publish."""
from __future__ import annotations
import asyncio, html, json, shutil, subprocess, wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SHORT = ROOT / "short"
ASSETS = SHORT / "assets"
COMP = SHORT / "compositions"
OUT = ROOT.parent / "out" / "ch05-short-v1.mp4"
# the template is build input, not a composition: keeping it out of compositions/
# is what stops the linter from reading its unsubstituted $TOTAL$ tokens
TPL = ROOT / "tpl" / "dense-short-v3.tpl.html"
SAMPLE = ROOT.parent / "assets" / "sample-short.txt"
HOOK = 3.2
FPS = 30

# (band id, spoken keyword, kinetic colour) — bottom stratum first, same order as the chapter
LAYERS = [("bd1", "插件"), ("bd2", "用户"), ("bd3", "项目"),
          ("bd4", "本地"), ("bd5", "CLI"), ("bd6", "企业")]

# every scene anchor is one spoken phrase; a missing keyword is a build error,
# not a silently invented timestamp
ANCHORS = {
    "$T_ROCK$": ["配置不是", "六层岩"],
    "$T_COVER$": ["盖住"],
    "$T_RING$": ["猜一猜"],
    "$T_ANS$": ["不会"],
    "$T_RINGBOX$": ["拼接", "钥匙圈"],
    "$T_KEYRULE$": ["每层挂自己的", "摘不掉"],
    "$T_DENY$": ["deny"],
    "$T_CUT$": ["最后一刀", "不看它"],
    "$T_CTA$": ["完整版"],
}
# anchors whose search window is bounded by the next named scene
WINDOWS = {
    "$T_ROCK$": ("$T_CTA$",),
    "$T_ANS$": ("$T_RING$", "$T_CTA$"),
    "$T_RINGBOX$": ("$T_RING$", "$T_CTA$"),
    "$T_KEYRULE$": ("$T_RING$", "$T_CTA$"),
    "$T_DENY$": ("$T_RING$", "$T_CTA$"),
    "$T_GREY$": ("$T_CUT$", "$T_CTA$"),
    "$T_SIGN$": ("$T_CUT$", "$T_CTA$"),
    "$T_PRIO$": ("$T_ROCK$", "$T_COVER$"),
}
GREY_KW = ["项目那层"]
SIGN_KW = ["仓库", "别人的"]
PRIO_KW = ["越往上", "越大"]


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def ensure() -> None:
    for d in (SHORT, ASSETS, ASSETS / "sfx", COMP, ROOT.parent / "out", SHORT / ".hf-tmpdir"):
        d.mkdir(parents=True, exist_ok=True)


# Real library cues (Pixabay Content License, no attribution required), staged
# from the media-use skill's bundled offline set. durations come from that set's
# manifest.json, which is the documented offline timing source.
SFX_LIB = Path.home() / ".qoder" / "skills" / "media-use" / "audio" / "assets" / "sfx"

# Track gain per cue. The narration stem measures -24.9 LUFS integrated
# (ffmpeg -i assets/short-vo.mp3 -af loudnorm=print_format=summary), so every
# cue is placed a fixed number of LU under it: gain g lands the cue at
# (its own LUFS + 20*log10 g). Accents sit 9 LU under, the bass hits and the
# riser 6 LU under, glitch-3 10 LU under because it is texture, not an event.
# click and click-soft are shorter than the R128 gating window and report no
# integrated value, so those two are placed from their -4.8 dBTP peak instead.
# key-press is the library's quietest cue (-36.4 LUFS): it keeps full gain and
# still lands 11 LU under the voice.
SFX_GAIN = {
    "click": 0.22, "click-soft": 0.22, "pop": 0.23, "key-press": 1.00,
    "ping": 0.43, "chime": 0.56, "sparkle": 0.13, "whoosh-short": 0.13,
    "glitch-1": 0.14, "glitch-3": 0.24, "error": 0.66,
    "impact-bass-1": 0.07, "impact-bass-2": 0.09, "riser": 0.05,
}

# Music bed generated locally by facebook/musicgen-small (no credential, CPU):
# node <media-use>/audio/scripts/audio.mjs route, 12 s seed crossfade-looped to
# 51 s. Measured the same way as the cues, then placed 12 LU under the narration.
BGM = ASSETS / "bgm" / "track.wav"
# make_bgm.py --seed 7 measures -18.3 LUFS / -1.0 dBTP; the narration stem
# measures -24.9 LUFS, so 0.117 (-18.6 dB) parks the bed 12 LU under the voice.
BGM_GAIN = 0.117


def stage_sfx() -> dict[str, float]:
    """Copy every cue this film can use out of the library and return their
    durations. A missing library is a build error: the cues have no stand-in."""
    lib = SFX_LIB / "manifest.json"
    if not lib.exists():
        raise SystemExit(f"sfx library not installed: expected {lib}")
    manifest = json.loads(lib.read_text(encoding="utf-8"))
    durs: dict[str, float] = {}
    for name in sorted(SFX_GAIN):
        meta = manifest.get(name)
        if meta is None:
            raise SystemExit(f"sfx cue {name!r} is not in {lib}")
        src = SFX_LIB / meta["file"]
        if not src.exists():
            raise SystemExit(f"sfx library file missing: {src}")
        dst = ASSETS / "sfx" / meta["file"]
        if not dst.exists() or dst.stat().st_size != src.stat().st_size:
            shutil.copyfile(src, dst)
        durs[name] = float(meta["duration"])
    (ASSETS / "sfx" / "CREDITS.md").write_text(
        "# Sound cues\n\n"
        "Every cue here is copied from the media-use skill's bundled offline set "
        f"(`{SFX_LIB.as_posix()}`), sourced from Pixabay sound effects and used "
        "under the Pixabay Content License, which allows commercial and "
        "non-commercial use, modification and redistribution inside derivative "
        "works such as this render, with no attribution required.\n\n"
        "Cues this film uses:\n\n"
        + "".join(f"- `{name}.mp3`\n" for name in sorted(SFX_GAIN))
        + "\nNo cue is synthesised and no cue is generated: the film's soundtrack "
        "uses these files as they are, at the track gains recorded in "
        "`build_short.py` `SFX_GAIN`.\n",
        encoding="utf-8",
    )
    return durs


def split_phrases(text: str) -> list[str]:
    """Split on CN/EN punctuation; keep English tokens + 「」 quotes intact."""
    parts: list[str] = []
    buf = ""
    seps = set("，。；、！？,.!;:")
    in_quote = False
    for ch in text:
        if ch == "「":
            in_quote = True
            buf += ch
            continue
        if ch == "」":
            buf += ch
            in_quote = False
            continue
        buf += ch
        if (not in_quote) and ch in seps:
            parts.append(buf)
            buf = ""
    if buf:
        parts.append(buf)
    merged: list[str] = []
    for p in parts:
        stripped = p.strip()
        if not stripped:
            continue
        if merged and (len(stripped) <= 2 or stripped in "。！？.!?"):
            merged[-1] += p
        else:
            merged.append(p)
    return [p for p in merged if p.strip()]


def allocate_phrase_times(sent_start: float, sent_end: float, phrases: list[str]) -> list[dict]:
    def weight(s: str) -> float:
        w = 0.0
        i = 0
        while i < len(s):
            o = ord(s[i])
            if s[i].isspace() or s[i] in "，。；、！？,.!;:「」·—":
                i += 1
                continue
            if o < 128:
                j = i
                while j < len(s) and ord(s[j]) < 128 and not s[j].isspace():
                    j += 1
                w += max(1.0, (j - i) / 3.0)
                i = j
            else:
                w += 1.0
                i += 1
        return max(w, 1.0)

    weights = [weight(p) for p in phrases]
    total_w = sum(weights) or 1.0
    span = max(sent_end - sent_start, 0.2)
    t = sent_start
    out = []
    for p, w in zip(phrases, weights):
        dur = span * (w / total_w)
        out.append({"start": round(t, 3), "end": round(t + dur, 3), "text": p.strip()})
        t += dur
    if out:
        out[-1]["end"] = round(sent_end, 3)
    return out


async def make_vo() -> tuple[float, list[dict], list[dict]]:
    import edge_tts

    text = SAMPLE.read_text(encoding="utf-8").strip()
    raw = ASSETS / "short-vo-raw.mp3"
    sentences: list[dict] = []
    # sentence boundaries are the scene anchors here, so ask for them explicitly
    communicate = edge_tts.Communicate(text, "zh-CN-YunyangNeural", rate="-10%", pitch="-5Hz",
                                      boundary="SentenceBoundary")
    with open(raw, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "SentenceBoundary":
                s = chunk["offset"] / 10_000_000
                e = s + chunk["duration"] / 10_000_000
                sentences.append({"start": s, "end": e, "text": chunk["text"]})

    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(raw)],
        capture_output=True, text=True, check=True,
    )
    vo_dur = float(probe.stdout.strip())
    if not sentences:
        raise SystemExit("edge-tts 没回任何 SentenceBoundary：场景锚点无从取，检查 boundary 参数")

    silence = ASSETS / "silence5.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=24000:cl=mono", "-t", str(HOOK),
         "-c:a", "libmp3lame", "-q:a", "4", str(silence)],
        check=True, capture_output=True,
    )
    vo = ASSETS / "short-vo.mp3"
    concat = ASSETS / "vo-concat.txt"
    concat.write_text(f"file '{silence.name}'\nfile '{raw.name}'\n", encoding="utf-8")
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
         "-c:a", "libmp3lame", "-q:a", "2", str(vo)],
        check=True, capture_output=True,
    )

    phrases: list[dict] = []
    sent_shifted: list[dict] = []
    for sent in sentences:
        s0, e0 = sent["start"] + HOOK, sent["end"] + HOOK
        sent_shifted.append({"start": round(s0, 3), "end": round(e0, 3), "text": sent["text"]})
        phrases.extend(allocate_phrase_times(s0, e0, split_phrases(sent["text"])))

    (ASSETS / "short-caps.json").write_text(json.dumps(phrases, ensure_ascii=False, indent=2), encoding="utf-8")
    (ASSETS / "short-sents.json").write_text(json.dumps(sent_shifted, ensure_ascii=False, indent=2), encoding="utf-8")
    return HOOK + vo_dur, phrases, sent_shifted


def find_time(phrases: list[dict], keywords: list[str], lo: float, hi: float, label: str,
              total: float) -> float:
    """First phrase inside [lo, hi) whose text carries one of the keywords."""
    for kw in keywords:
        for p in phrases:
            if lo - 0.05 <= p["start"] < hi and kw.lower() in p["text"].lower():
                return p["start"]
    raise SystemExit(
        f"锚点 {label}（关键词 {keywords}）在口播里没有对应的一拍；"
        f"要么文案改了、要么分句变了。现有 {len(phrases)} 拍：\n"
        + "\n".join(f"  {p['start']:6.2f} {p['text']}" for p in phrases)
    )


def anchor_map(phrases: list[dict], total: float) -> dict[str, float]:
    """Scene anchors, each bounded by the anchor of the scene it lives in."""
    order = ["$T_ROCK$", "$T_COVER$", "$T_RING$", "$T_CUT$", "$T_CTA$"]
    # resolve the backbone in speech order first: a later anchor may not reach back
    t: dict[str, float] = {}
    for key in order:
        lo = t[order[order.index(key) - 1]] if order.index(key) else 0.0
        t[key] = find_time(phrases, ANCHORS[key], lo, total, key, total)
    for key, kws in (("$T_GREY$", GREY_KW), ("$T_SIGN$", SIGN_KW)):
        lo, hi = WINDOWS[key]
        t[key] = find_time(phrases, kws, t[lo], t[hi], key, total)
    for key, kws in (("$T_PRIO$", PRIO_KW),):
        lo, hi = WINDOWS[key]
        t[key] = find_time(phrases, kws, t[lo], t[hi], key, total)
    for key in ANCHORS:
        w = WINDOWS.get(key)
        lo = t[w[0]] if w else 0.0
        hi = t[w[1]] if w and len(w) > 1 else total
        if key in order:
            continue
        t[key] = find_time(phrases, ANCHORS[key], lo, hi, key, total)
    return t


def band_times(phrases: list[dict], t: dict[str, float]) -> list[tuple[str, float]]:
    """One band per stratum name, keyed off the phrase that says it, then spaced
    so no two strata land inside 0.06 s of each other. This is the list the
    tweens animate and the cues sit on, so the spacing rule lives here."""
    out = []
    prev = t["$T_ROCK$"]
    for bid, kw in LAYERS:
        ts = max(find_time(phrases, [kw], t["$T_ROCK$"], t["$T_COVER$"], f"band:{bid}", 0), prev + 0.06)
        prev = ts
        out.append((bid, ts))
    return out


def key_times(t: dict[str, float]) -> list[float]:
    """One key per stratum hung across the sentence that explains the rule."""
    k0, k1 = t["$T_RINGBOX$"], t["$T_KEYRULE$"]
    step = max(0.16, (k1 - k0) / max(len(LAYERS), 1))
    return [k0 + 0.15 + i * step for i in range(len(LAYERS))]


# A cue per visible action, never a cue per spoken clause. Everything after the
# hook reads an anchor or a band/key landing, so a re-spoken narration moves the
# soundtrack with the picture; the five opening cues read tween times written in
# tpl/dense-short-v3.tpl.html (#b-edit 0.60, #mval 1.10, #b-restart 1.60,
# #xmark 2.30, #ftitle 3.50) and are stated here as those times.
BAND_CUES = ["pop", "click-soft", "pop", "click-soft", "pop", "ping"]


def sfx_events(t: dict[str, float], bands: list[tuple[str, float]],
               durs: dict[str, float], total: float) -> list[tuple[float, str]]:
    ev: list[tuple[float, str]] = [
        (0.60, "click"), (1.10, "key-press"), (1.60, "click"),
        (2.30, "error"), (3.50, "impact-bass-1"),
        (t["$T_ROCK$"], "whoosh-short"),
        *[(ts, cue) for (_, ts), cue in zip(bands, BAND_CUES)],
        (t["$T_PRIO$"], "sparkle"),
        (t["$T_COVER$"], "whoosh-short"), (t["$T_COVER$"] + 0.55, "impact-bass-1"),
        (t["$T_RING$"], "ping"), (t["$T_ANS$"], "impact-bass-1"),
        (t["$T_RINGBOX$"], "whoosh-short"),
        *[(kt, "key-press") for kt in key_times(t)],
        (t["$T_KEYRULE$"], "click"),
        (t["$T_SIGN$"] - 10.03, "riser"),
        (t["$T_DENY$"], "error"), (t["$T_CUT$"], "glitch-1"),
        (t["$T_GREY$"], "glitch-3"), (t["$T_SIGN$"], "impact-bass-2"),
        (t["$T_CTA$"], "sparkle"), (t["$T_CTA$"] + 0.70, "chime"),
    ]
    ev = [(ts, name) for ts, name in ev if ts > 0 and ts + durs[name] <= total]
    ev.sort(key=lambda x: x[0])
    out, last = [], -1.0
    for ts, name in ev:
        if ts - last < 0.08:
            continue
        out.append((ts, name))
        last = ts
    return out


def write_dense(total: float, t: dict[str, float], phrases: list[dict], bands: list[tuple[str, float]]) -> None:
    band_tl = []
    for bid, ts in bands:
        band_tl.append(
            f'tl.fromTo("#{bid}", {{opacity:0, x:-70, scale:0.9}}, '
            f'{{opacity:1, x:0, scale:1, duration:0.2, ease:"power2.out"}}, {ts:.3f});'
        )
        band_tl.append(f'flash({ts:.3f});')
        band_tl.append(f'tl.to("#{bid}", {{scale:1.05, duration:0.12, yoyo:true, repeat:1}}, {ts + 0.20:.3f});')

    key_tl = []
    for i, kt in enumerate(key_times(t)):
        key_tl.append(
            f'tl.fromTo("#ky{i+1}", {{opacity:0, y:-46, rotation:-14}}, '
            f'{{opacity:1, y:0, rotation:0, duration:0.2, ease:"bounce.out", transformOrigin:"50% 0%"}}, {kt:.3f});'
        )
        key_tl.append(f'flash({kt + 0.02:.3f});')

    palette = ["#6cf", "#f8a", "#ff6", "#9f8", "#fc6"]
    t_cta = t["$T_CTA$"]
    kinetic_items = []
    for i, p in enumerate(phrases):
        # the end card gets the last beats to itself: no punch word over the outro
        if p["start"] >= t_cta:
            continue
        core = p["text"].replace('"', "").strip("，。；、！？,.!;:「」— ")
        # a punch line repeats the caption pill when it is a whole clause: keep it short
        if len(core) < 2 or len(core) > 9:
            continue
        kinetic_items.append((p["start"], p["end"], core, palette[i % len(palette)]))
    kinetic_lines = []
    for j, (s, e, core, color) in enumerate(kinetic_items):
        nxt = kinetic_items[j + 1][0] if j + 1 < len(kinetic_items) else max(e, s + 0.35)
        enter, fade = 0.12, 0.12
        # the fade must land before the next hit starts, or the tweens overlap on opacity/y
        start_out = max(s + enter, nxt - fade - 0.01)
        dur_out = min(fade, max(0.04, nxt - 0.005 - start_out))
        kinetic_lines.append(
            f'tl.fromTo("#kx", {{opacity:0, scale:0.7, y:30}}, '
            f'{{opacity:1, scale:1.05, y:0, duration:0.12}}, {s:.3f});')
        kinetic_lines.append(
            f'tl.call(() => {{ const el=document.getElementById("kx"); if(el){{ '
            f'el.textContent={json.dumps(core[:16], ensure_ascii=False)}; el.style.color="{color}"; }} }}, '
            f'null, {s:.3f});')
        kinetic_lines.append(
            f'tl.to("#kx", {{opacity:0, y:-24, duration:{dur_out:.3f}}}, {start_out:.3f});')

    shake_lines = [
        f'tl.fromTo("#root", {{x:0}}, {{x:6, duration:0.04, yoyo:true, repeat:1}}, {p["start"]:.3f});'
        for p in phrases if p["start"] <= t_cta + 0.01
    ]

    doc = TPL.read_text(encoding="utf-8")
    subs = {
        "$TOTAL$": f"{total:.3f}",
        "$FPS$": str(FPS),
        "$BAND_TL$": "\n".join(band_tl),
        "$KEY_TL$": "\n".join(key_tl),
        "$KINETIC$": "\n".join(kinetic_lines),
        "$SHAKE$": "\n".join(shake_lines),
    }
    subs.update({k: f"{v:.3f}" for k, v in t.items()})
    for k, v in subs.items():
        doc = doc.replace(k, v)
    leftover = [m for m in ("$T_", "$BAND", "$KEY", "$KINETIC", "$SHAKE", "$TOTAL", "$FPS") if m in doc]
    if leftover:
        raise SystemExit(f"模板里有没被替换的 token：{leftover}")
    (COMP / "dense-short.html").write_text(doc, encoding="utf-8")


def write_captions(caps: list[dict], total: float) -> None:
    lines = []
    tl_lines = []
    for i, c in enumerate(caps):
        lines.append(f'<div class="cap" id="cap{i}">{esc(c["text"])}</div>')
        s, e = c["start"], c["end"]
        tl_lines.append(f'tl.set("#cap{i}", {{opacity:0, scale:0.92}}, 0);')
        tl_lines.append(f'tl.to("#cap{i}", {{opacity:1, scale:1, duration:0.08}}, {s:.3f});')
        tl_lines.append(f'tl.to("#cap{i}", {{opacity:0, scale:0.96, duration:0.08}}, '
                        f'{max(e - 0.04, s + 0.08):.3f});')
    doc = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="UTF-8"/>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
@font-face{{font-family:'Noto Sans SC';src:local('Noto Sans SC'),local('Microsoft YaHei');font-weight:100 900}}
@font-face{{font-family:'Microsoft YaHei';src:local('Microsoft YaHei'),local('Noto Sans SC');font-weight:100 900}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:transparent}}
.wrap{{position:absolute;left:40px;right:40px;bottom:150px;text-align:center;z-index:55;pointer-events:none;height:120px}}
.cap{{position:absolute;left:0;right:0;bottom:0;margin:auto;width:fit-content;max-width:100%;
  font-family:"Noto Sans SC","Microsoft YaHei",sans-serif;
  font-size:38px;font-weight:800;color:#fff;padding:14px 26px;opacity:0;
  text-shadow:0 2px 10px #000,0 0 16px #000a;white-space:nowrap;
  background:linear-gradient(90deg,#1a90ffee,#7a3dffee);border-radius:999px}}
</style></head><body>
<div id="root" class="clip" data-composition-id="captions-zh" data-start="0" data-duration="{total:.3f}" data-width="1080" data-height="1920" data-fps="{FPS}">
  <div class="wrap">{chr(10).join(lines)}</div>
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(tl_lines)}
window.__timelines["captions-zh"] = tl;
</script></body></html>
'''
    (COMP / "captions-zh.html").write_text(doc, encoding="utf-8")


def bgm_tag(total: float) -> tuple[str, dict | None]:
    """The music bed, if one was generated.

    It holds one level for the whole film instead of a ducking lane: the
    narration stem leaves only six silences of 0.6 s or longer, the longest 0.8 s,
    so a per-sentence lane would move inaudibly. The 12 LU gap under the voice is
    the duck."""
    if not BGM.exists():
        return "", None
    with wave.open(str(BGM), "rb") as w:
        bed = w.getnframes() / w.getframerate()
    dur = min(bed, total)
    tag = (f'<audio id="bgm" class="clip" src="assets/bgm/track.wav" data-start="0" '
           f'data-duration="{dur:.3f}" data-track-index="4" data-volume="{BGM_GAIN:.3f}" '
           f'data-fade-in="0.8" data-fade-out="1.5"></audio>')
    return tag, {"path": "assets/bgm/track.wav", "duration": round(dur, 3), "gain": BGM_GAIN}


def write_index(total: float, t: dict[str, float], sfx: list[tuple[float, str]],
                durs: dict[str, float]) -> dict | None:
    tags = []
    for i, (at, name) in enumerate(sfx):
        tags.append(
            f'<audio id="sfx-{i}" class="clip" src="assets/sfx/{name}.mp3" data-start="{at:.3f}" '
            f'data-duration="{durs[name]:.3f}" data-track-index="{20 + (i % 8)}" '
            f'data-volume="{SFX_GAIN[name]:.2f}"></audio>'
        )
    bed, bed_meta = bgm_tag(total)
    audio = ([bed] if bed else []) + tags
    index = f'''<!doctype html>
<html lang="zh-CN" data-resolution="portrait"><head><meta charset="UTF-8"/>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>*{{margin:0;padding:0;box-sizing:border-box}}html,body{{width:1080px;height:1920px;overflow:hidden;background:#000}}</style>
</head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{total:.3f}" data-width="1080" data-height="1920" data-fps="{FPS}">
<div class="clip" id="scene-dense" data-composition-id="dense-short" data-composition-src="compositions/dense-short.html" data-start="0" data-duration="{total:.3f}" data-track-index="1" style="position:absolute;inset:0"></div>
<div class="clip" id="scene-caps" data-composition-id="captions-zh" data-composition-src="compositions/captions-zh.html" data-start="0" data-duration="{total:.3f}" data-track-index="10" data-track-kind="captions" style="position:absolute;inset:0;pointer-events:none;z-index:50"></div>
<audio id="a-roll-audio" src="assets/short-vo.mp3" data-start="0" data-duration="{total:.3f}" data-track-index="2" data-volume="1"></audio>
{chr(10).join(audio)}
</div>
<script>window.__timelines=window.__timelines||{{}};window.__timelines["main"]=gsap.timeline({{paused:true}});</script>
</body></html>
'''
    (SHORT / "index.html").write_text(index, encoding="utf-8")
    return bed_meta


def write_meta() -> None:
    (SHORT / "package.json").write_text(json.dumps({
        "name": "ch05-short", "private": True, "type": "module",
        "scripts": {"render": "npx --yes hyperframes@0.8.210 render",
                    "check": "npx --yes hyperframes@0.8.210 check"},
    }, indent=2), encoding="utf-8")
    (SHORT / "hyperframes.json").write_text(json.dumps({
        "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
        "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
        "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
        "media": {"autoProxy": True}, "authoringSkill": "hyperframes", "registryItems": [],
    }, indent=2), encoding="utf-8")
    (SHORT / "meta.json").write_text(json.dumps({"id": "ch05-short", "name": "ch05-short"}, indent=2), encoding="utf-8")


def main() -> None:
    ensure()
    durs = stage_sfx()
    total, phrases, sents = asyncio.run(make_vo())
    t = anchor_map(phrases, total)
    bands = band_times(phrases, t)
    sfx = sfx_events(t, bands, durs, total)
    write_dense(total, t, phrases, bands)
    write_captions(phrases, total)
    bed = write_index(total, t, sfx, durs)
    write_meta()
    (SHORT / "short-meta.json").write_text(json.dumps({
        "total": round(total, 3), "caps": len(phrases), "sents": len(sents), "sfx": len(sfx),
        "bgm": bed,
        "hook": HOOK, "out": str(OUT), "anchors": {k: round(v, 3) for k, v in t.items()},
        "bands": {b: round(v, 3) for b, v in bands},
        "sent_starts": [s["start"] for s in sents],
        "phrase_texts": [p["text"] for p in phrases],
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    order = sorted(t.items(), key=lambda kv: kv[1])
    lines = ["# short A/V sync map", "", "| t | 锚点 | 口播一拍 |", "|---|---|---|"]
    for ph in phrases:
        sc = "hook"
        for name, ts in order:
            if ph["start"] + 1e-6 >= ts:
                sc = name.strip("$")
        lines.append(f"| {ph['start']:.2f}–{ph['end']:.2f} | {sc} | {ph['text']} |")
    lines += ["", "## 场景锚点", "", "| 锚点 | 秒 |", "|---|---|"]
    lines += [f"| {name} | {ts:.2f} |" for name, ts in order]
    bed_line = (f"背景音乐：{bed['path']} · {bed['duration']:.2f}s · data-volume {bed['gain']}"
                if bed else "背景音乐：未生成")
    lines += ["", "## 音效点位", "", bed_line, "",
              "| 秒 | 素材 | 轨增益 | 当时在播的口播 |", "|---|---|---|---|"]
    for ts, name in sfx:
        said = next((p["text"] for p in phrases if p["start"] - 0.05 <= ts < p["end"]), "（无）")
        lines.append(f"| {ts:.2f} | {name} | {SFX_GAIN[name]:.2f} | {said} |")
    (SHORT / "SYNC-MAP.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"OK short assembled total={total:.3f}s caps={len(phrases)} sents={len(sents)} sfx={len(sfx)} "
          f"bgm={'yes' if bed else 'no'}")
    print("anchors:", {k: round(v, 2) for k, v in sorted(t.items(), key=lambda kv: kv[1])})


if __name__ == "__main__":
    main()
