#!/usr/bin/env python3
"""Check that the portal's links have a publisher, and the front-door docs' links resolve.

The portal is deployed from an assembled `site/` directory, not from `docs/`, so
resolving `href="book.html"` next to `docs/portal.html` is the wrong question.
The right question is: does anything *put* that file at the site root? pages.yml's
"Assemble the site" step is the answer, so the publish inventory is read from there
rather than hand-copied. A portal reference with no publisher is a dead link in
production, and that is what this script fails on.

Local references in the front-door docs (FRONT_DOOR below) are checked against the
working tree instead, because those files are read in the repository.

External URLs are counted, not fetched; `--online` asks for a HEAD on each one.
Offline by default so the gate stays deterministic.

    python docs/yuyu-overhaul/check_site_links.py [--online]

Exit 0 prints the inventory it resolved; exit 1 prints one line per problem.
"""
from __future__ import annotations

import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PORTAL = ROOT / "docs" / "portal.html"
FRONT_DOOR = ["README.md", "en/README.md", "STRUCTURE.md", "omp/BUILD.md",
              "docs/COMPARE-OMP.md"]

REF = re.compile(r"""(?:href|src)\s*=\s*["']([^"'#]+)(?:#[^"']*)?["']""")
MD_REF = re.compile(r"\]\(\s*<?([^)\s#]+)>?(?:#[^)]*)?\)")
CARD = re.compile(r'<(a|div) class="card"')


def site_inventory() -> set[str]:
    """File names that pages.yml places at the site root, parsed from its own cp lines."""
    text = (ROOT / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")
    names = set()
    for src, dst in re.findall(r"cp\s+(\S+)\s+site/(\S+)", text):
        names.add(dst)
    if "index.html" not in names:  # written by build_site_portal.py site/index.html
        names |= {"index.html"}
    return names


def portal_refs() -> list[str]:
    html = PORTAL.read_text(encoding="utf-8")
    refs = []
    for m in REF.finditer(html):
        u = m.group(1).strip()
        if u and not u.startswith(("data:", "mailto:")):
            refs.append(u)
    return refs


def front_door_problems() -> list[str]:
    problems = []
    for rel in FRONT_DOOR:
        path = ROOT / rel
        if not path.exists():
            problems.append(f"{rel}: file missing")
            continue
        base = path.parent
        for m in MD_REF.finditer(path.read_text(encoding="utf-8")):
            u = m.group(1).strip()
            if not u or u.startswith(("http://", "https://", "mailto:", "#", "data:")):
                continue
            if not (base / u).exists():
                problems.append(f"{rel}: dead relative link -> {u}")
    return problems


def structure_problems() -> list[str]:
    html = PORTAL.read_text(encoding="utf-8")
    problems = []
    if re.search(r"@@[A-Z_]*@@", html):
        problems.append("portal.html: unexpanded @@TOKEN@@ left")
    if re.search(r"<a[^>]*>(?:(?!</a>).)*?<a", html, re.S):
        problems.append("portal.html: <a> nested inside <a> (parser hoists the inner link out)")
    cards = len(CARD.findall(html))
    if cards < 2:
        problems.append(f"portal.html: {cards} cards, SPEC M5 Step 2 wants at least two volumes")
    return problems


def main(argv: list[str]) -> int:
    inventory = site_inventory()
    refs = portal_refs()
    local = [u for u in refs if not u.startswith(("http://", "https://"))]
    external = [u for u in refs if u.startswith(("http://", "https://"))]

    problems = structure_problems() + front_door_problems()
    unpublished = [u for u in local if u not in inventory]
    for u in sorted(set(unpublished)):
        problems.append(f"portal.html: site root has no publisher for -> {u} (pages.yml does not cp it)")

    if "--online" in argv:
        for u in sorted(set(external)):
            req = urllib.request.Request(u, method="HEAD", headers={"User-Agent": "yuyu-links-check"})
            try:
                with urllib.request.urlopen(req, timeout=20) as r:
                    code = r.status
            except Exception as exc:  # noqa: BLE001 - report, do not guess
                code = f"error {exc}"
            if code != 200:
                problems.append(f"external: {code} -> {u}")

    print(f"portal refs: {len(local)} local, {len(set(external))} external")
    print(f"site inventory from pages.yml: {len(inventory)} names -> {sorted(inventory)}")
    print(f"front-door docs: {len(FRONT_DOOR)}")
    if problems:
        for p in problems:
            print("PROBLEM", p)
        return 1
    print("check_site_links OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
