# -*- coding: utf-8 -*-
"""ch05 short-v1: 一个文件 vs 六层岩 · hard A/V sync off the TTS phrase times. No publish."""
from __future__ import annotations
import asyncio, html, json, math, struct, subprocess, wave
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


def synth_sfx() -> None:
    out = ASSETS / "sfx"
    specs = {
        "whoosh": (0.28, 900, 180),
        "impact": (0.22, 80, 40),
        "rein_snap": (0.12, 2200, 600),
        "gallop": (0.55, 120, 90),
        "ui_blip": (0.08, 1400, 1100),
        "punch": (0.18, 60, 30),
        "glitch": (0.15, 400, 1200),
        "tick": (0.06, 1800, 1600),
    }
    for name, (dur, f0, f1) in specs.items():
        path = out / f"{name}.wav"
        if path.exists() and path.stat().st_size > 500:
            continue
        sr = 44100
        n = int(sr * dur)
        frames = bytearray()
        for i in range(n):
            t = i / sr
            env = math.exp(-t * (8 if name != "whoosh" else 4))
            if name == "whoosh":
                freq = f0 + (f1 - f0) * (t / max(dur, 1e-6))
                sample = env * 0.45 * math.sin(2 * math.pi * freq * t)
            elif name == "gallop":
                hit = 0.0
                for k in (0.0, 0.18, 0.36):
                    dt = t - k
                    if 0 <= dt < 0.08:
                        hit += math.exp(-dt * 40) * math.sin(2 * math.pi * f0 * dt)
                sample = 0.55 * hit
            elif name in ("rein_snap", "glitch"):
                noise = ((i * 1103515245 + 12345) & 0x7FFF) / 32768.0 - 0.5
                sample = env * (0.35 * math.sin(2 * math.pi * f0 * t) + 0.4 * noise)
            elif name == "tick":
                sample = env * 0.5 * math.sin(2 * math.pi * f0 * t)
            else:
                sample = env * 0.6 * math.sin(2 * math.pi * f0 * t)
            sample = max(-1.0, min(1.0, sample))
            frames += struct.pack("<h", int(sample * 30000))
        with wave.open(str(path), "w") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            w.writeframes(frames)


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
    """One band per stratum name, keyed off the phrase that says it."""
    out = []
    for bid, kw in LAYERS:
        out.append((bid, find_time(phrases, [kw], t["$T_ROCK$"], t["$T_COVER$"], f"band:{bid}", 0)))
    return out


def sfx_on_phrases(phrases: list[dict], t: dict[str, float], total: float) -> list[tuple[float, str, float]]:
    ev: list[tuple[float, str, float]] = [
        (0.60, "ui_blip", 0.52), (1.10, "tick", 0.46), (1.60, "ui_blip", 0.50),
        (2.20, "glitch", 0.58), (2.32, "impact", 0.68), (3.50, "punch", 0.60),
    ]
    kinds = ["tick", "ui_blip", "whoosh", "impact", "punch", "glitch", "rein_snap"]
    for i, p in enumerate(phrases):
        ts = p["start"]
        if ts >= total - 0.15:
            continue
        name = kinds[i % len(kinds)]
        vol = 0.38 + (i % 3) * 0.05
        txt = p["text"]
        if any(k in txt for k in ("插件", "用户", "项目", "本地", "CLI", "企业")):
            name, vol = "rein_snap", 0.60
        if "盖住" in txt or "删掉" in txt:
            name, vol = "whoosh", 0.62
        if "钥匙圈" in txt or "摘" in txt or "挂" in txt:
            name, vol = "rein_snap", 0.64
        if "deny" in txt.lower() or "猜" in txt:
            name, vol = "punch", 0.58
        if "不看它" in txt or "仓库" in txt:
            name, vol = "impact", 0.66
        if "完整版" in txt or "六层岩" in txt:
            name, vol = "punch", 0.58
        ev.append((ts, name, vol))
    ev.sort(key=lambda x: x[0])
    out = []
    last = -1.0
    for hit in ev:
        if hit[0] - last < 0.08:
            continue
        out.append(hit)
        last = hit[0]
    return out


def write_dense(total: float, t: dict[str, float], phrases: list[dict], bands: list[tuple[str, float]]) -> None:
    band_tl = []
    prev = t["$T_ROCK$"]
    for bid, ts in bands:
        ts = max(ts, prev + 0.06)
        prev = ts
        band_tl.append(
            f'tl.fromTo("#{bid}", {{opacity:0, x:-70, scale:0.9}}, '
            f'{{opacity:1, x:0, scale:1, duration:0.2, ease:"power2.out"}}, {ts:.3f});'
        )
        band_tl.append(f'flash({ts:.3f});')
        band_tl.append(f'tl.to("#{bid}", {{scale:1.05, duration:0.12, yoyo:true, repeat:1}}, {ts + 0.20:.3f});')

    # keys hang one per stratum across the sentence that explains the rule
    k0, k1 = t["$T_RINGBOX$"], t["$T_KEYRULE$"]
    step = max(0.16, (k1 - k0) / max(len(LAYERS), 1))
    key_tl = []
    for i in range(len(LAYERS)):
        kt = k0 + 0.15 + i * step
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


def write_index(total: float, sfx: list[tuple[float, str, float]]) -> None:
    durs = {"whoosh": 0.30, "impact": 0.24, "rein_snap": 0.14, "gallop": 0.58,
            "ui_blip": 0.10, "punch": 0.20, "glitch": 0.16, "tick": 0.07}
    tags = []
    for i, (t, name, vol) in enumerate(sfx):
        tags.append(
            f'<audio id="sfx-{i}" class="clip" src="assets/sfx/{name}.wav" data-start="{t:.3f}" '
            f'data-duration="{durs.get(name, 0.25):.3f}" data-track-index="{20 + (i % 8)}" '
            f'data-volume="{vol:.2f}"></audio>'
        )
    index = f'''<!doctype html>
<html lang="zh-CN" data-resolution="portrait"><head><meta charset="UTF-8"/>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>*{{margin:0;padding:0;box-sizing:border-box}}html,body{{width:1080px;height:1920px;overflow:hidden;background:#000}}</style>
</head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{total:.3f}" data-width="1080" data-height="1920" data-fps="{FPS}">
<div class="clip" id="scene-dense" data-composition-id="dense-short" data-composition-src="compositions/dense-short.html" data-start="0" data-duration="{total:.3f}" data-track-index="1" style="position:absolute;inset:0"></div>
<div class="clip" id="scene-caps" data-composition-id="captions-zh" data-composition-src="compositions/captions-zh.html" data-start="0" data-duration="{total:.3f}" data-track-index="10" data-track-kind="captions" style="position:absolute;inset:0;pointer-events:none;z-index:50"></div>
<audio id="a-roll-audio" src="assets/short-vo.mp3" data-start="0" data-duration="{total:.3f}" data-track-index="2" data-volume="1"></audio>
{chr(10).join(tags)}
</div>
<script>window.__timelines=window.__timelines||{{}};window.__timelines["main"]=gsap.timeline({{paused:true}});</script>
</body></html>
'''
    (SHORT / "index.html").write_text(index, encoding="utf-8")


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
    synth_sfx()
    total, phrases, sents = asyncio.run(make_vo())
    t = anchor_map(phrases, total)
    bands = band_times(phrases, t)
    sfx = sfx_on_phrases(phrases, t, total)
    write_dense(total, t, phrases, bands)
    write_captions(phrases, total)
    write_index(total, sfx)
    write_meta()
    (SHORT / "short-meta.json").write_text(json.dumps({
        "total": round(total, 3), "caps": len(phrases), "sents": len(sents), "sfx": len(sfx),
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
    (SHORT / "SYNC-MAP.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"OK short assembled total={total:.3f}s caps={len(phrases)} sents={len(sents)} sfx={len(sfx)}")
    print("anchors:", {k: round(v, 2) for k, v in sorted(t.items(), key=lambda kv: kv[1])})


if __name__ == "__main__":
    main()
