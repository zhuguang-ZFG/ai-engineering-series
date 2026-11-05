"""审计 omp 各章是否具备 SPEC 规定的六要素结构（不设字数地板）。

用法：python omp/overhaul/audit_structure.py [--csv] [--check]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

if __package__:
    from .markdown_scan import image_sources, scan_markdown
else:
    from markdown_scan import image_sources, scan_markdown

ROOT = Path(__file__).resolve().parents[1]

TABLE_SEPARATOR = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*$", re.M)
H2 = re.compile(r"^##\s+(.*)$")

# 每要素的判据：命中即视为「有」，但不保证质量——质量仍靠人工抽读。
Pit = re.compile(r"翻车|对照|陷阱|踩坑|常见误|误区|失败|排障|debug", re.I)
Yuyu = re.compile(r"御舆")
PinCheck = re.compile(r"版本核对")
Experiment = re.compile(r"实验|跟做|动手|试一下|演练")
VERIFIED = re.compile(r"本机已验|已实跑|实跑于|已验（|本机\s+(?:omp/|v)?\d+\.\d+\.\d+\s*(?:回|输出|返回|实测|实跑|验过)")


def fence_blocks(text: str) -> list[tuple[str, str]]:
    """[(lang, body)] for every fenced block."""
    return scan_markdown(text).blocks


def prose_before_first_h2(text: str) -> list[str]:
    paras, body = [], scan_markdown(text).prose.split("\n")
    cur = []
    for line in body:
        if H2.match(line):
            break
        if line.strip():
            cur.append(line.strip())
        elif cur:
            paras.append(" ".join(cur))
            cur = []
    if cur:
        paras.append(" ".join(cur))
    opening = []
    for p in paras:
        if p.startswith("#") or p.startswith("!") or p.startswith("*图") or p.startswith("<!--"):
            continue
        out = re.sub(r"\*[^*]+\*", "", p).strip()
        if out:
            opening.append(out)
    return opening


def audit(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    content = scan_markdown(text)
    prose, blocks = content.prose, content.blocks
    diagrams = sum(language == "mermaid" for language, _ in blocks)
    images = image_sources(prose)
    omp_cmds = [b for lang, b in blocks
                if (lang.split()[0].lower() if lang else "") in ("bash", "sh", "shell", "powershell", "ps1", "console", "")
                and re.search(r"^\s*(omp|PI_|~/.omp|\$ omp)\b", b, re.M)]
    # 按小节切，找「翻车/对照」小节里是否真有表格
    sections = re.split(r"(?m)^##\s+", prose)
    pit_table = False
    for sec in sections[1:]:
        title = sec.split("\n", 1)[0]
        if Pit.search(title) and TABLE_SEPARATOR.search(sec):
            pit_table = True
    verified = bool(VERIFIED.search(prose))
    unverified = bool(re.search(r"未验证", prose))
    opening = prose_before_first_h2(prose)
    return {
        "unit": path.stem,
        "e1_opening_scene": "Y" if len(opening) >= 1 and len(opening[0]) > 40 else "n",
        "e2_principle_figure": "Y" if images or diagrams else "n",
        "e3_runnable_experiment": "Y" if omp_cmds and Experiment.search(prose) else "n",
        "e3_cmd_blocks": len(omp_cmds),
        "e4_pit_table": "Y" if pit_table else "n",
        "e5_yuyu_isomorphism": "Y" if Yuyu.search(prose) else "n",
        "e6_pin_checklist": "Y" if PinCheck.search(prose) else "n",
        "mark_verified": "Y" if verified else ("~" if unverified else "n"),
        "han": len(re.findall(r"[一-鿿]", text)),
        "chars": len(text),
        "mermaid": diagrams,
        "imgs": len(images),
        "errors": content.errors,
    }


def main() -> int:
    files = sorted(ROOT.glob("ch*.md"))
    as_csv = "--csv" in sys.argv
    rows = [audit(p) for p in files]
    elements = ["e1_opening_scene", "e2_principle_figure", "e3_runnable_experiment",
                "e4_pit_table", "e5_yuyu_isomorphism", "e6_pin_checklist"]
    expected = {f"ch{number:02}.md" for number in range(1, 34)}
    found = {path.name for path in files}
    diagnostics = []
    if expected != found:
        diagnostics.append(f"chapter files: missing {sorted(expected - found)}, unexpected {sorted(found - expected)}")
    diagnostics.extend(f"{row['unit']}: {error}" for row in rows for error in row.get("errors", []))
    for diagnostic in diagnostics:
        print(diagnostic, file=sys.stderr)
    failed = (bool(diagnostics)
              or any(any(row[element] != "Y" for element in elements)
                     or row["mark_verified"] == "n" for row in rows))
    exit_code = int("--check" in sys.argv and failed)
    if as_csv:
        print("\t".join(["unit"] + elements + ["e3_cmd_blocks", "mark_verified", "han", "chars"]))
        for r in rows:
            print("\t".join(str(r[k]) for k in ["unit"] + elements + ["e3_cmd_blocks", "mark_verified", "han", "chars"]))
        return exit_code
    print(f"{'unit':10}" + "".join(f"{e[2:4]:>5}" for e in elements) + f"{'cmds':>6}{'mark':>6}{'han':>7}")
    missing_counts = {e: 0 for e in elements}
    for r in rows:
        print(f"{r['unit']:10}" + "".join(f"{r[e]:>5}" for e in elements)
              + f"{r['e3_cmd_blocks']:>6}{r['mark_verified']:>6}{r['han']:>7}")
        for e in elements:
            if r[e] == "n":
                missing_counts[e] += 1
    print("\n缺要素的章数（共 %d 章）:" % len(rows))
    labels = {"e1_opening_scene": "开场场景", "e2_principle_figure": "原理+图",
              "e3_runnable_experiment": "可跑实验", "e4_pit_table": "翻车对照表",
              "e5_yuyu_isomorphism": "与御舆同构点", "e6_pin_checklist": "版本核对清单"}
    for e in elements:
        print(f"  {labels[e]:12} 缺 {missing_counts[e]:>2} 章")
    full = [r["unit"] for r in rows if all(r[e] == "Y" for e in elements)]
    print(f"\n六要素齐（按判据）: {len(full)} 章 -> {', '.join(full) or '无'}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
