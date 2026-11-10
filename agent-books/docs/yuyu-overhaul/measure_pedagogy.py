"""Y-M1 观测：逐单元字数（改前 = git HEAD，改后 = 工作树）与补丁结构在否。

用法（仓根）：
    python docs/yuyu-overhaul/measure_pedagogy.py            # 全 20 单元
    python docs/yuyu-overhaul/measure_pedagogy.py ch01 ch02  # 只看点名的单元

只看，不改任何文件。改前那一列来自当前 HEAD 中的项目文件，
改后来自工作树；提交后再运行时，对比基线也随 HEAD 更新。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "yuyu-book"))
sys.path.insert(0, str(ROOT / "scripts"))

from book_history import HistoryError, RevisionFiles  # noqa: E402
from yuyu_book.core import unit_stream  # noqa: E402

HAN = re.compile(r"[㐀-䶿一-鿿]")
SCENE = re.compile(r"翻车现场|先设想|你让\s*Agent|Picture the|scene:", re.I)
TABLE = re.compile(r"^\s*\|.*\|\s*$", re.M)
OBJECTIVES = re.compile(r"学习目标|Learning Objectives|读完这章|By the end")
DIFFICULTY = re.compile(r"难度定位|Difficulty")
CROSSREF = re.compile(r"omp 分册|the omp volume|Cross-ref.*omp", re.I)


def git_head(path: str, history: RevisionFiles | None = None) -> str:
    return (history or RevisionFiles(ROOT, "HEAD")).read_text(path, missing_ok=True) or ""


def units() -> list[tuple[str, str, str]]:
    manifest = json.loads((ROOT / "yuyu-book" / "manifest.json")
                          .read_text(encoding="utf-8"))
    out = []
    for unit, _kind, _part in unit_stream(manifest):
        for lang in ("zh", "en"):
            if lang in unit:
                out.append((unit["id"], lang, unit[lang]))
    return out


def report(want: set[str]) -> int:
    history = RevisionFiles(ROOT, "HEAD")
    rows = []
    for uid, lang, rel in units():
        if want and uid not in want:
            continue
        now_p = ROOT / rel
        now = now_p.read_text(encoding="utf-8") if now_p.exists() else ""
        before = git_head(rel, history)
        b = dict(chars=len(before), han=len(HAN.findall(before)),
                 scene=bool(SCENE.search(before)), tables=len(TABLE.findall(before)))
        c = dict(chars=len(now), han=len(HAN.findall(now)),
                 scene=bool(SCENE.search(now)), tables=len(TABLE.findall(now)))
        delta = "-" if not b["chars"] else round(100 * (c["chars"] - b["chars"]) / b["chars"], 1)
        rows.append((uid, lang, b, c, delta))
    print(f"{'unit':6} {'lang':4} {'chars 前→后':>16} {'Δ%':>6} "
          f"{'han 前→后':>14} {'场景':>8} {'表行 前→后':>12} {'目标':>4} {'难度':>4} {'互链':>4}")
    over = []
    for uid, lang, b, c, delta in rows:
        if not b["chars"] and not c["chars"]:
            continue
        now_text = (ROOT / next(r for u, l, r in units() if u == uid and l == lang)
                    ).read_text(encoding="utf-8")
        mark = lambda rx: "Y" if rx.search(now_text) else "."  # noqa: E731
        if isinstance(delta, float) and abs(delta) > 10:
            over.append((uid, lang, delta))
        print(f"{uid:6} {lang:4} {b['chars']:>7}→{c['chars']:<7} {delta!s:>6} "
              f"{b['han']:>6}→{c['han']:<6} "
              f"{'.' if not b['scene'] and not c['scene'] else ('+' if c['scene'] and not b['scene'] else ('-' if b['scene'] and not c['scene'] else 'Y')):>8} "
              f"{b['tables']:>5}→{c['tables']:<5} {mark(OBJECTIVES):>4} {mark(DIFFICULTY):>4} {mark(CROSSREF):>4}")
    if over:
        print("\n超出 ±10% 字数门的单元（Y-M1 禁止灌水）:")
        for uid, lang, delta in over:
            print(f"  {uid} {lang}: {delta:+.1f}%")
        return 1
    return 0


if __name__ == "__main__":
    try:
        sys.exit(report(set(sys.argv[1:])))
    except HistoryError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
