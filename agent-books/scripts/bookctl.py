#!/usr/bin/env python3
"""One cross-platform entry point for the book's environment and checks.

The Makefile and both CI workflows call the same subcommands, so Windows, a
developer shell and Ubuntu CI cannot drift into different definitions of
"green":

    python scripts/bookctl.py doctor
    python scripts/bookctl.py check --fast
    python scripts/bookctl.py check --full
    python scripts/bookctl.py build --product book --lang both [--pdf]
    python scripts/bookctl.py clean
    python scripts/bookctl.py deps

doctor reports every missing piece in one pass with a fix command; it does not
stop at the first failure. `deps` compares yuyu-book/requirements.txt with
uv.lock, which is what keeps the exported pins from going stale.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
import tomllib
from importlib.metadata import distributions
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"
LOCK = ROOT / "uv.lock"
REQUIREMENTS = ROOT / "yuyu-book" / "requirements.txt"
DIST = ROOT / "yuyu-book" / "dist"
VENDOR = ROOT / "yuyu-book"
AGENT_PRODUCTS = ("opencode", "deepseek", "hermes", "codex", "kimi")
ZH_PRODUCTS = ("omp", "pi", *AGENT_PRODUCTS, "prompt")
BOOK_PRODUCTS = ("book", *ZH_PRODUCTS)
OUTPUT_PREFIXES = {"book": "yuyu-agent-harness",
                   **{product: f"yuyu-{product}" for product in ZH_PRODUCTS}}

NAME = re.compile(r"^(?P<name>[A-Za-z0-9_.-]+)(?:\[[^\]]+\])?=="
                  r"(?P<version>[^;\s]+)")
CJK_FALLBACK = ["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simsun.ttc",
                "C:/Windows/Fonts/simhei.ttf",
                "/System/Library/Fonts/PingFang.ttc",
                "/System/Library/Fonts/Supplemental/Songti.ttc",
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc"]


def norm(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def npm() -> str | None:
    return shutil.which("npm")


def python() -> str:
    return sys.executable


def read_requirements() -> tuple[dict[str, str], list[str]]:
    """{normalized name: version} plus any line that is not an exact pin."""
    pins: dict[str, str] = {}
    problems: list[str] = []
    for number, line in enumerate(REQUIREMENTS.read_text(encoding="utf-8")
                                 .splitlines(), 1):
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        match = NAME.match(line)
        if not match:
            problems.append(f"{REQUIREMENTS.name}:{number}: not an exact pin: {line}")
            continue
        pins[norm(match.group("name"))] = match.group("version")
    return pins, problems


def project_name() -> str:
    return tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["project"]["name"]


def read_lock() -> dict[str, str]:
    data = tomllib.loads(LOCK.read_text(encoding="utf-8"))
    project = norm(project_name())
    return {norm(pkg["name"]): pkg["version"] for pkg in data["package"]
            if norm(pkg["name"]) != project}


def installed() -> dict[str, str]:
    out = {}
    for dist in distributions():
        name = dist.metadata["Name"]
        if name:
            out[norm(name)] = dist.version
    return out


def direct_requirements() -> list[str]:
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    return list(data["project"]["dependencies"])


def dependency_problems() -> list[str]:
    """Everything that makes requirements.txt disagree with pyproject/uv.lock."""
    pins, problems = read_requirements()
    lock = read_lock()
    for name, version in pins.items():
        if name not in lock:
            problems.append(f"{name}=={version} is not in uv.lock")
        elif lock[name] != version:
            problems.append(f"{name}: requirements.txt has {version}, "
                            f"uv.lock has {lock[name]}")
    for name, version in lock.items():
        if name not in pins:
            problems.append(f"{name}=={version} is missing from requirements.txt")
    for spec in direct_requirements():
        match = NAME.match(spec)
        name = norm(match.group("name")) if match else norm(
            re.split(r"[<>=!~\s]", spec, 1)[0])
        if name not in pins:
            problems.append(f"pyproject dependency {spec} is not in requirements.txt")
        elif match and pins[name] != match.group("version"):
            problems.append(f"pyproject wants {spec}, requirements.txt has "
                            f"{name}=={pins[name]}")
    return problems


def run(cmd: list[str]) -> None:
    print("+ " + " ".join(cmd), flush=True)
    env = {**os.environ, "PYTHONPATH": str(VENDOR)}
    subprocess.run(cmd, cwd=ROOT, check=True, env=env)


def version_tuple(text: str) -> tuple[int, ...]:
    return tuple(int(part) for part in re.findall(r"\d+", text)[:3])


def report_artifacts(destination: Path) -> list[Path]:
    """Every built file the report may claim: PDF/EPUB and nested assets too.

    Reporting only ``destination/*.html`` dropped printed editions and nested
    site files from artifact-manifest.json, so a release could not prove what
    it shipped.
    """
    destination = Path(destination)
    if not destination.is_dir():
        return []
    return sorted(path for path in destination.rglob("*") if path.is_file())


def browser_probe() -> tuple[bool, str, str | None]:
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:  # noqa: BLE001 - report, don't crash the doctor
        return False, f"playwright import failed: {exc}", \
            "python -m pip install -r yuyu-book/requirements.txt"
    with sync_playwright() as pw:
        for kind in ("msedge", "chrome", None):
            try:
                browser = (pw.chromium.launch(channel=kind) if kind
                           else pw.chromium.launch())
            except Exception:  # noqa: BLE001 - try the next channel
                continue
            version = browser.version
            browser.close()
            return True, f"{kind or 'chromium'} {version}", None
    return False, "no launchable Edge, Chrome or Chromium", \
        "python -m playwright install --with-deps chromium"


def font_probe() -> tuple[bool, str, str | None]:
    candidates = CJK_FALLBACK
    try:
        sys.path.insert(0, str(VENDOR))
        from yuyu_book.pdf import CJK_FONTS  # noqa: PLC0415 - optional import
        candidates = CJK_FONTS
    except Exception:  # noqa: BLE001 - PyMuPDF missing is already a deps row
        pass
    for path in candidates:
        if Path(path).exists():
            return True, path, None
    return False, "no CJK face for the PDF running head", \
        "sudo apt-get install fonts-noto-cjk  (Linux) / use a system CJK font"


def writable_probe() -> tuple[bool, str, str | None]:
    try:
        DIST.mkdir(parents=True, exist_ok=True)
        probe = DIST / ".bookctl-write-test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        with tempfile.TemporaryDirectory(prefix="bookctl-") as tmp:
            (Path(tmp) / "probe").write_text("ok", encoding="utf-8")
        return True, str(DIST), None
    except OSError as exc:
        return False, f"{type(exc).__name__}: {exc}", \
            "check directory permissions or set a writable --out-dir"


def doctor() -> int:
    rows: list[tuple[bool, str, str, str | None]] = []

    def add(ok: bool, label: str, detail: str, hint: str | None = None):
        rows.append((ok, label, detail, hint))

    add(sys.version_info >= (3, 12), "python",
        platform.python_version(), "install Python 3.12+")

    node = shutil.which("node")
    if not node:
        add(False, "node", "not found", "install Node 22+")
    else:
        try:
            raw = subprocess.run([node, "--version"], check=True,
                                 capture_output=True, text=True).stdout.strip()
            add(version_tuple(raw) >= (22,), "node", raw, "install Node 22+")
        except (OSError, subprocess.CalledProcessError) as exc:
            add(False, "node", str(exc), "install Node 22+")

    add(bool(npm()), "npm", npm() or "not found", "install Node 22+")

    modules = ROOT / "node_modules" / "mermaid" / "package.json"
    add(modules.exists(), "npm deps", "node_modules/mermaid present"
        if modules.exists() else "node_modules/mermaid missing", "npm ci")

    pins, req_problems = read_requirements()
    have = installed()
    bad = [f"{name}=={want} (have {have.get(name, 'missing')})"
           for name, want in pins.items() if have.get(name) != want]
    add(not bad and not req_problems, "python deps",
        "all locked versions installed" if not bad and not req_problems
        else "; ".join(bad + req_problems),
        "python -m pip install -r yuyu-book/requirements.txt")

    problems = dependency_problems()
    add(not problems, "requirements/lock",
        "requirements.txt matches uv.lock" if not problems
        else "; ".join(problems[:3]) + (" ..." if len(problems) > 3 else ""),
        "uv lock && uv export --format requirements-txt --no-hashes "
        "--no-emit-project --no-annotate > yuyu-book/requirements.txt")

    ok, detail, hint = browser_probe()
    add(ok, "browser", detail, hint)

    ok, detail, hint = font_probe()
    add(ok, "cjk font", detail, hint)

    ok, detail, hint = writable_probe()
    add(ok, "writable", detail, hint)

    width = max(len(label) for _ok, label, _detail, _hint in rows)
    failures = 0
    for ok, label, detail, hint in rows:
        print(f"[{'ok' if ok else 'fail'}] {label:<{width}}  {detail}")
        if not ok:
            failures += 1
            if hint:
                print(f"       fix: {hint}")
    print(f"doctor: {len(rows) - failures} ok, {failures} failed")
    return 0 if failures == 0 else 1


def check(full: bool) -> int:
    steps = [
        ("dependencies", [python(), "scripts/bookctl.py", "deps"]),
        ("source build", [python(), "-m", "yuyu_book", "--check",
                          "--mermaid", "source"]),
        ("general tests", [python(), "-m", "unittest", "discover",
                           "-s", "tests"]),
        ("builder tests", [python(), "-m", "unittest", "discover",
                           "-s", "yuyu-book/tests"]),
        ("content", [python(), "scripts/check_book.py"]),
        ("mermaid", [npm() or "npm", "run", "check:diagrams"]),
        ("video configuration", [python(), "video/pipeline/cli.py", "check",
                                 "--config-only"]),
        ("product idempotence", [python(), "scripts/check_products.py"]),
    ]
    if full:
        steps += [
            ("render build", [python(), "-m", "yuyu_book", "--check"]),
            ("pdf", [python(), "-m", "yuyu_book", "--lang", "both", "--pdf"]),
        ]
    measurements = []
    try:
        for label, cmd in steps:
            print(f"\n== {label} ==", flush=True)
            started = time.perf_counter()
            run(cmd)
            measurements.append({"name": label, "command": cmd, "returncode": 0,
                                 "seconds": round(time.perf_counter() - started, 3)})
    except subprocess.CalledProcessError as exc:
        measurements.append({"name": label, "command": cmd,
                             "returncode": exc.returncode,
                             "seconds": round(time.perf_counter() - started, 3)})
        from build_reports import write_reports
        write_reports(ROOT / ".scratch/reports", measurements)
        print(f"\ncheck failed: {label} (exit {exc.returncode})", file=sys.stderr)
        return 1
    from build_reports import write_reports
    write_reports(ROOT / ".scratch/reports", measurements,
                  report_artifacts(DIST) if full else [])
    print(f"\ncheck {'full' if full else 'fast'}: {len(steps)} steps passed")
    return 0


def build(args) -> int:
    products = {"site": None, "reader": "build_beginner_reader.py",
                "gallery": "build_illustration_gallery.py",
                "cards": "build_knowledge_cards.py", "sample": "build_sample_chapter.py",
                "indices": "build_site_indices.py"}
    if args.product in products:
        names = (["build_beginner_reader.py", "build_illustration_gallery.py",
                  "build_knowledge_cards.py", "build_sample_chapter.py",
                  "build_site_indices.py", "build_site_portal.py"]
                 if args.product == "site" else [products[args.product]])
        try:
            for name in names:
                run([python(), "scripts/" + name])
        except subprocess.CalledProcessError as exc:
            return exc.returncode or 1
        return 0
    if args.product not in BOOK_PRODUCTS:
        print(f"unknown product: {args.product}", file=sys.stderr)
        return 2
    lang = args.lang
    cmd = [python(), "-m", "yuyu_book", "--mermaid", args.mermaid]
    if args.product in ZH_PRODUCTS:
        # Companion volumes currently publish only their Chinese edition.
        if lang == "en":
            print(f"{args.product} product is zh-only for now", file=sys.stderr)
            return 2
        lang = "zh"
        cmd += ["--lang", lang,
                "--manifest", f"manifest-{args.product}.json",
                "--sources", f"sources-{args.product}.json"]
    else:
        cmd += ["--lang", lang]
    if args.pdf:
        cmd.append("--pdf")
    if args.out_dir:
        cmd += ["--out-dir", args.out_dir]
    for flag in ("check", "no_plain", "regen_index"):
        if getattr(args, flag, False):
            cmd.append("--" + flag.replace("_", "-"))
    started = time.perf_counter()
    try:
        run(cmd)
    except subprocess.CalledProcessError as exc:
        return exc.returncode or 1
    if getattr(args, "epub", False) and not getattr(args, "check", False):
        result = epub(args)
        if result:
            return result
    from build_reports import write_reports
    destination = Path(args.out_dir) if args.out_dir else DIST
    # A check publishes nothing. A product build must not claim or open a
    # different book's output, which may still be written by another worker.
    artifacts = []
    if not getattr(args, "check", False):
        foreign_prefixes = tuple(prefix + "-" for product, prefix in
                                 OUTPUT_PREFIXES.items() if product != args.product)
        artifacts = [path for path in report_artifacts(destination)
                     if not path.name.startswith(foreign_prefixes)]
    write_reports(destination, [{"name": args.product, "command": cmd,
                  "returncode": 0, "seconds": round(time.perf_counter() - started, 3)}],
                  artifacts)
    return 0


def epub(args) -> int:
    """Convert the editions just built, respecting Chinese-only products."""
    langs = (["zh"] if args.product in ZH_PRODUCTS else
             ["zh", "en"] if args.lang == "both" else [args.lang])
    out_dir = Path(args.out_dir) if args.out_dir else DIST
    for lang in langs:
        html = out_dir / f"{OUTPUT_PREFIXES[args.product]}-{lang}.html"
        if not html.exists():
            print(f"epub: missing {html}", file=sys.stderr)
            return 1
        try:
            run([python(), "scripts/build_epub.py", "--html", str(html),
                 "--output", str(html.with_suffix(".epub")), "--lang", lang])
        except subprocess.CalledProcessError as exc:
            return exc.returncode or 1
    return 0


def clean() -> int:
    if DIST.exists():
        shutil.rmtree(DIST)
        print(f"removed {DIST.relative_to(ROOT)}")
    else:
        print("dist already clean")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="command", required=True)

    sub.add_parser("doctor", help="report environment problems in one pass")

    chk = sub.add_parser("check", help="run the verification suite")
    group = chk.add_mutually_exclusive_group()
    group.add_argument("--fast", action="store_true",
                       help="source-mode build, tests and content checks")
    group.add_argument("--full", action="store_true",
                       help="fast plus rendered HTML and both PDF editions")

    bl = sub.add_parser("build", help="build a product")
    bl.add_argument("--product", default="book", choices=[*BOOK_PRODUCTS, "site",
                    "reader", "gallery", "cards", "sample", "indices"])
    bl.add_argument("--lang", default="both", choices=["zh", "en", "both"])
    bl.add_argument("--pdf", action="store_true")
    bl.add_argument("--epub", action="store_true")
    bl.add_argument("--out-dir")
    bl.add_argument("--mermaid", default="render",
                    choices=["render", "source"])
    bl.add_argument("--check", action="store_true")
    bl.add_argument("--no-plain", action="store_true")
    bl.add_argument("--regen-index", action="store_true")

    video = sub.add_parser("video", help="chapter video factory")
    video.add_argument("arguments", nargs=argparse.REMAINDER)
    release = sub.add_parser("release", help="assemble a traceable release")
    release.add_argument("--version", required=True)
    release.add_argument("--out-dir")
    release.add_argument("--epub", action="store_true")

    sub.add_parser("clean", help="remove yuyu-book/dist")
    sub.add_parser("deps", help="compare requirements.txt with uv.lock")

    args = ap.parse_args(argv)
    if args.command == "doctor":
        return doctor()
    if args.command == "check":
        return check(args.full)
    if args.command == "build":
        return build(args)
    if args.command == "video":
        try:
            run([python(), "video/pipeline/cli.py", *args.arguments])
            return 0
        except subprocess.CalledProcessError as exc:
            return exc.returncode or 1
    if args.command == "release":
        from release import assemble
        return assemble(args.version, args.out_dir, epub=args.epub)
    if args.command == "clean":
        return clean()
    if args.command == "deps":
        problems = dependency_problems()
        if problems:
            print("\n".join(problems), file=sys.stderr)
            return 1
        print("requirements.txt matches uv.lock")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
