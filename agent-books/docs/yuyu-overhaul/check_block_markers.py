"""御舆书稿改动护栏：确认你没弄丢证据锚点，也没弄丢术语锁。

用法：

    python docs/yuyu-overhaul/check_block_markers.py                 # 不传参 = 查全部单元（双语）
    python docs/yuyu-overhaul/check_block_markers.py 第一部分-基础篇/01-*.md en/Part-1-Foundations/01-*.md

退出 0 = 锚点齐、锁定的词形在、围栏数未变；非 0 = 打印丢的东西。

「注册词形从正文消失」只在两种情况下算违规：这个词形的证据锚点就落在这个文件
里（删掉它，虚线标注会悬空），或这一章的按语引用了它（术语锁失效）。其余同形
字按提示打印、不计违规——散文里换个动词不该由术语表负责。不传参时过去是「零文
件通过」，读起来像全绿，其实什么都没查；现在默认查满 manifest 的 20 个单元。
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from book_history import HistoryError, RevisionFiles  # noqa: E402

BLOCK = re.compile(r"<!--\s*block:\s*([A-Za-z0-9_.\-]+)\s*-->")


def head_text(rel: str, history: RevisionFiles | None = None) -> str | None:
    return (history or RevisionFiles(ROOT, "HEAD")).read_text(rel, missing_ok=True)


def read(rel: str) -> str:
    path = ROOT / rel
    return path.read_text(encoding="utf-8") if path.exists() else ""


def unit_files() -> list[tuple[str, str | None, str | None]]:
    """(unit id, zh path, en path) for every book unit, foreword and appendices included."""
    m = json.loads((ROOT / "yuyu-book" / "manifest.json").read_text(encoding="utf-8"))
    rows: list[tuple[str, str | None, str | None]] = []
    front = m.get("front") or {}
    if isinstance(front, dict) and front.get("zh"):
        rows.append(("front", front["zh"], front.get("en")))
    for part in m.get("parts", []):
        for u in part.get("units", []):
            rows.append((u["id"], u.get("zh"), u.get("en")))
    for a in m.get("appendices", []):
        rows.append((a["id"], a.get("zh"), a.get("en")))
    return rows


def zh_forms(glosses: dict) -> list[str]:
    forms: list[str] = []
    for entry in glosses.values():
        if isinstance(entry, dict):
            forms += (entry.get("forms") or {}).get("zh") or []
    return sorted(set(forms), key=len, reverse=True)


def anchored_files(glosses: dict, rows) -> dict[str, set[str]]:
    """zh path -> the registered forms whose evidence block lives in that file."""
    block_home: dict[str, str] = {}
    for _uid, zh, _en in rows:
        if zh:
            for bid in BLOCK.findall(read(zh)):
                block_home.setdefault(bid, zh)
    needed: dict[str, set[str]] = defaultdict(set)
    for entry in glosses.values():
        if not isinstance(entry, dict):
            continue
        forms = (entry.get("forms") or {}).get("zh") or []
        for eid in entry.get("evidence") or []:
            home = block_home.get(eid)
            if home:
                needed[home] |= set(forms)
    return needed


def note_locked_files(glosses: dict, forms: list[str], rows) -> dict[str, set[str]]:
    """zh path -> the registered forms this unit's 按语 leans on."""
    notes_path = ROOT / "yuyu-book" / "notes.json"
    notes = json.loads(notes_path.read_text(encoding="utf-8")) if notes_path.exists() else {}
    by_unit = {zh: (notes.get(uid) or {}).get("zh", "") for uid, zh, _en in rows if zh}
    needed: dict[str, set[str]] = defaultdict(set)
    for zh, note in by_unit.items():
        needed[zh] |= {f for f in forms if f in note}
    return needed


def check(rel: str, forms: list[str], required: set[str], history: RevisionFiles | None = None) -> int:
    path = ROOT / rel
    if not path.exists():
        print(f"!! 文件不存在（改名或删了？）: {path.relative_to(ROOT).as_posix()}")
        return 1
    problems = 0
    now = path.read_text(encoding="utf-8")
    before = head_text(rel, history)

    if before is None:
        print(f"   {rel}: 不在 HEAD 里（新文件），跳过锚点对比")
    else:
        lost = set(BLOCK.findall(before)) - set(BLOCK.findall(now))
        added = set(BLOCK.findall(now)) - set(BLOCK.findall(before))
        if lost:
            print(f"!! {rel}: 丢了 {len(lost)} 个 block 锚点（glosses evidence 会悬空）:")
            for x in sorted(lost):
                print(f"     - {x}")
            problems += 1
        if added:
            print(f"   {rel}: 新增 {len(added)} 个锚点（可以，但需登记证据）")

    if not rel.startswith("en/"):
        gone = [f for f in forms if f in (before or "") and f not in now]
        hard = sorted(set(gone) & required)
        soft = sorted(set(gone) - required)
        if hard:
            print(f"!! {rel}: 这些词形是本章的锚点或按语在用，现在正文里没了（虚线/术语锁会失效）:")
            for f in hard:
                print(f"     - {f}")
            problems += 1
        if soft:
            print(f"   {rel}: 这些注册词形从散文里消失了，但不归本章管，仅作提示: {', '.join(soft)}")

    if before and "```mermaid" in before:
        dn, dm = before.count("```mermaid"), now.count("```mermaid")
        if dn != dm:
            print(f"!! {rel}: mermaid 围栏数 {dm}，HEAD 是 {dn}（双语对拍会红）")
            problems += 1
    return problems


def main(argv: list[str]) -> int:
    history = RevisionFiles(ROOT, "HEAD")
    glosses = json.loads((ROOT / "yuyu-book" / "glosses.json").read_text(encoding="utf-8"))
    rows = unit_files()
    forms = zh_forms(glosses)
    anchored = anchored_files(glosses, rows)
    locked = note_locked_files(glosses, forms, rows)

    if argv:
        targets: list[str] = []
        for pattern in argv:
            hits = sorted(ROOT.glob(pattern)) if any(c in pattern for c in "*?") else [ROOT / pattern]
            targets += [h.relative_to(ROOT).as_posix() for h in hits]
    else:
        targets = [p for _u, zh, en in rows for p in (zh, en) if p]

    problems = 0
    for rel in targets:
        problems += check(rel, forms, anchored.get(rel, set()) | locked.get(rel, set()), history)
    print(f"\n（共检查 {len(targets)} 个文件）")
    if problems:
        print(f"护栏未过：{problems} 处。补回来再交。")
        return 1
    print("护栏通过：锚点齐、锁定的词形在、围栏数未变。")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except HistoryError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
