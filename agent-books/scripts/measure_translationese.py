#!/usr/bin/env python3
"""One reproducible count of the two translationese shapes the book sweeps.

Rounds 39 and 40 both wrote down a number that did not match the thing measured
(once a leftover 被 that was really a lifecycle label, once a boundary-gated
pattern that quietly disagreed with the ungated one the ledger had been using).
The fix is not a better memory: it is the same script every round, so a figure
in a commit message or in revisions.json can be re-produced by anyone.

What counts as prose is `check_book.prose_walls` — the running text between two
visual breaks. Tables, fenced code and Mermaid sources are excluded because a
passive cell in a comparison table is not a sentence a reader hears.

    python scripts/measure_translationese.py              # both languages
    python scripts/measure_translationese.py --lang=zh    # one edition
    python scripts/measure_translationese.py --sample=12  # audit the count
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_book import prose_walls  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BOOK = ROOT / "yuyu-book"

# 被 + 一个汉字, ungated: 「hooks 被跳过」 and 「会被移除」 are the same fault.
ZH_PASSIVE = re.compile(r"被[一-龥]")
# Terms where 被 is the honest word, not a calque: an adjective (被动的) or a
# role name (被调用者). Listed rather than filtered silently, so the script
# prints what it set aside and a reader can disagree.
ZH_KEEP = ("被动的", "被动地", "被调用者", "被调用方", "被测系统")

BE = r"(?:is|are|was|were|be|been|being)"
MODAL = r"(?:can|could|may|might|must|should|will|would|has|have|had)"
# A regular past participle, or one of the irregulars that actually show up in
# this book. A generic `-n/-de/-te` branch was tried first and counted "is ready"
# and "is wide" as passive, which inflated the total past usefulness.
PP = (r"(?:[a-z]+ed|been|seen|known|given|taken|made|built|drawn|shown|found|"
      r"brought|carried|paid|sent|left|kept|set|put|read|done|written|chosen|"
      r"split|thrown|grown|bound|held)")
# Two shapes, as measured since round 39: plain be + participle, and a modal
# + be + participle. An adverb between them is allowed ("is often dropped").
# The participle is closed with a boundary so `...found` stops at a word end
# rather than reaching into "foundation".
EN_PASSIVE = re.compile(rf"\b{BE}\s+(?:\w+ly\s+)?(?:{PP})\b")
EN_MODAL_PASSIVE = re.compile(rf"\b(?:{MODAL})\s+be\s+(?:\w+ly\s+)?(?:{PP})\b")
# Copular uses where the -ed word is a adjective of state, not an action done
# to the subject; these read fine in English and are reported separately.
EN_COPULAR = re.compile(rf"\b{BE}\s+(?:\w+ly\s+)?(?:based|related|called|named|"
                        r"known|used|supposed|limited|interested|involved)\b")


def units():
    """The 20 manifest units, from the builder's own reader — the same list
    the sweeps have always covered, so a count cannot drift onto new ground."""
    sys.path.insert(0, str(BOOK))
    from yuyu_book.core import load_configs, unit_stream
    manifest, _sources = load_configs()
    return [(u["id"], u["zh"], u["en"]) for u, _kind, _part in unit_stream(manifest)]


def walls(path: Path):
    lines = path.read_text(encoding="utf-8").splitlines()
    rows = set()
    for _chars, first, last, _heading in prose_walls(lines):
        rows.update(range(first, last + 1))
    return {i: line for i, line in enumerate(lines, 1) if i in rows}


def line_counts(line: str) -> dict:
    """Everything one prose line contributes to the totals, in one place.

    The counter and the sampler both read this, so a sample can never show a
    line the table did not count — the two had drifted apart once already.
    """
    zh_all = [m.group() for m in ZH_PASSIVE.finditer(line)]
    zh_kept = [h for h in zh_all if any(k.startswith(h) for k in ZH_KEEP)]
    copular = [m.group() for m in EN_COPULAR.finditer(line)]
    passive = ([m.group() for m in EN_PASSIVE.finditer(line)]
               + [m.group() for m in EN_MODAL_PASSIVE.finditer(line)])
    return {
        "zh_lines": 1 if len(zh_all) > len(zh_kept) else 0,
        "zh_hits": len(zh_all),
        "zh_kept": len(zh_kept),
        "zh_frags": zh_all,
        "en_lines": 1 if len(passive) > len(copular) else 0,
        "en_hits": max(len(passive) - len(copular), 0),
        "en_frags": passive,
        "en_copular": len(copular),
    }


TOTAL_KEYS = ("zh_lines", "zh_hits", "zh_kept", "en_lines", "en_hits",
              "en_copular")


def measure(rel: str, limit: int = 0):
    """Lines, not occurrences: a sweep rewrites one line for one line, so the
    line is the unit of work and the unit of the promise in a commit message.

    With a limit, also returns that many of the counted lines, each with the
    fragments that put it in the total — from the same pass, not a second one.
    """
    total = dict.fromkeys(TOTAL_KEYS, 0)
    shown = []
    for no, line in walls(ROOT / rel).items():
        row = line_counts(line)
        for key in TOTAL_KEYS:
            total[key] += row[key]
        if limit and len(shown) < limit and (row["zh_lines"] or row["en_lines"]):
            frags = row["zh_frags"] if row["zh_lines"] else row["en_frags"]
            shown.append((no, frags, line.strip()))
    return total, shown


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--lang", choices=("zh", "en", "both"), default="both")
    ap.add_argument("--json", action="store_true", help="machine-readable rows")
    ap.add_argument("--sample", type=int, default=0, metavar="N",
                    help="print N counted lines per language so a count can be "
                         "eyeballed for false positives")
    args = ap.parse_args(argv)

    rows = []
    samples = {"zh": [], "en": []}
    for uid, zh_rel, en_rel in units():
        for lang, rel in (("zh", zh_rel), ("en", en_rel)):
            if args.lang != "both" and args.lang != lang:
                continue
            if not (ROOT / rel).exists():
                continue
            counts, shown = measure(rel, args.sample)
            rows.append((uid, lang, counts))
            for no, frags, line in shown:
                if len(samples[lang]) < args.sample:
                    samples[lang].append((f"{uid}:{no}", frags, line))

    if args.json:
        print(json.dumps([{"unit": u, "lang": l,
                           **{k: m[k] for k in TOTAL_KEYS}} for u, l, m in rows],
                         ensure_ascii=False))
        return 0

    if args.lang in ("both", "zh"):
        zh = sorted((r for r in rows if r[1] == "zh"),
                    key=lambda r: -r[2]["zh_lines"])
        print("中文「被x」：行=确有可改的一处；处=全部命中；术语=被动的/被调用者一类，另列不改")
        print(f"{'unit':8} {'行':>4} {'处':>4} {'术语':>5}")
        for uid, _l, m in zh:
            if m["zh_lines"]:
                print(f"{uid:8} {m['zh_lines']:4} {m['zh_hits']:4} {m['zh_kept']:5}")
        print(f"{'TOTAL':8} {sum(m['zh_lines'] for *_x, m in zh):4} "
              f"{sum(m['zh_hits'] for *_x, m in zh):4} "
              f"{sum(m['zh_kept'] for *_x, m in zh):5}")
    if args.lang in ("both", "en"):
        en = sorted((r for r in rows if r[1] == "en"),
                    key=lambda r: -r[2]["en_lines"])
        print("\n英文被动：be+过去分词 / 情态+be+过去分词；系词用法（is based on 一类）另列")
        print(f"{'unit':8} {'行':>4} {'处':>4} {'系词':>5}")
        for uid, _l, m in en:
            if m["en_lines"] or m["en_copular"]:
                print(f"{uid:8} {m['en_lines']:4} {m['en_hits']:4} {m['en_copular']:5}")
        print(f"{'TOTAL':8} {sum(m['en_lines'] for *_x, m in en):4} "
              f"{sum(m['en_hits'] for *_x, m in en):4} "
              f"{sum(m['en_copular'] for *_x, m in en):5}")
    for lang in ("zh", "en"):
        if samples[lang]:
            print(f"\n{lang} 样张（计入行数的原句，方括号内是命中的片段）")
            for where, frags, line in samples[lang]:
                print(f"  {where} [{'/'.join(frags)}] {line[:96]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
