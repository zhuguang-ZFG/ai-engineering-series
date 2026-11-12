#!/usr/bin/env python3
"""Standard-library command router for the two integrated book projects."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent
PROJECTS = ("agent-books", "model-course")
PRODUCTS = ("book", "omp", "pi", "opencode", "deepseek", "hermes", "codex", "kimi", "prompt", "llm")
ARTIFACT_SUFFIXES = {".html", ".pdf", ".epub", ".zip"}
SITE_SUFFIXES = {".html", ".css", ".js", ".cjs", ".mjs", ".json", ".jsonl", ".svg", ".png", ".jpg",
                 ".jpeg", ".webp", ".gif", ".md", ".txt", ".py", ".toml", ".yml", ".yaml", ".lock",
                 ".woff", ".woff2", ".ttf", ".otf"}
SKIP_PARTS = {".git", "node_modules", "__pycache__", ".hyperframes", ".thumbnails", ".waveform-cache",
              "tmp", "out", "archive", "renders", "local-feedback"}


def inside(base, relative):
    """Resolve only ordinary relative paths which remain inside base."""
    value = str(relative)
    parts = PurePosixPath(value.replace("\\", "/"))
    if not value or parts.is_absolute() or ".." in parts.parts or ":" in value:
        raise ValueError(f"Unsafe relative path: {value}")
    base = Path(base).resolve()
    target = (base / Path(*parts.parts)).resolve()
    if not target.is_relative_to(base):
        raise ValueError(f"Path leaves project: {value}")
    return target


def load_catalog(root=ROOT):
    data = json.loads((Path(root) / "series.json").read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or set(data.get("projects", {})) != set(PROJECTS):
        raise ValueError("series.json: expected schema 1 and the two known projects")
    ids = [book.get("id") for book in data.get("books", [])]
    if len(ids) != len(set(ids)) or set(ids) != set(PRODUCTS):
        raise ValueError("series.json: expected ten unique book IDs")
    for name, project in data["projects"].items():
        if project.get("path") != name:
            raise ValueError("Project paths must match their registered directory names")
        folder = inside(root, name)
        for path in project["required"]:
            inside(folder, path)
    for book in data["books"]:
        owner = "model-course" if book["id"] == "llm" else "agent-books"
        if book.get("project") != owner:
            raise ValueError(f"Unexpected project for {book['id']}")
        folder = inside(root, owner)
        for key in ("source_entry", "read_entry"):
            inside(folder, book[key])
        if not re.fullmatch(r"[a-z0-9-]+", book["artifact_prefix"]):
            raise ValueError("Invalid artifact prefix")
    return data


class LocalLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attributes):
        for name, value in attributes:
            if name in {"href", "src"} and value:
                self.links.append(value)


def entry_links(root, path):
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".html":
        parser = LocalLinks()
        parser.feed(text)
        links = parser.links
    else:
        links = re.findall(r"\]\(([^)]+)\)", text)
    problems = []
    for link in links:
        parsed = urlsplit(link)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        raw = unquote(parsed.path)
        if raw.startswith("/"):
            problems.append(f"Absolute local link in {path.name}: {link}")
            continue
        destination = (path.parent / raw).resolve()
        if not destination.is_relative_to(Path(root).resolve()):
            problems.append(f"Link leaves series: {path.name}: {link}")
        elif not destination.exists():
            problems.append(f"Missing entry link: {path.name}: {link}")
    return problems


def selected_projects(project):
    if project == "all":
        return PROJECTS
    if project not in PROJECTS:
        raise ValueError(f"Unknown project: {project}")
    return (project,)


def structure(root, catalog, project="all"):
    root = Path(root).resolve()
    problems = []
    for name in ("README.md", "index.html", "series.json", "series.py"):
        path = root / name
        if not path.is_file():
            problems.append(f"Missing series entry: {name}")
        elif name in ("README.md", "index.html"):
            problems.extend(entry_links(root, path))
    selected = selected_projects(project)
    for name in selected:
        folder = inside(root, name)
        if not folder.is_dir():
            problems.append(f"Missing project directory: {name}")
        for relative in catalog["projects"][name]["required"]:
            if not inside(folder, relative).exists():
                problems.append(f"Missing project entry: {name}/{relative}")
    for book in catalog["books"]:
        if book["project"] in selected:
            if not inside(root, f"{book['project']}/{book['source_entry']}").is_file():
                problems.append(f"Missing book source entry: {book['id']}")
    return problems


def npm_command():
    command = shutil.which("npm.cmd" if os.name == "nt" else "npm")
    if not command:
        raise FileNotFoundError("npm is not available on PATH")
    return command


def run(command, cwd):
    print(f"[{Path(cwd).name}] {subprocess.list2cmdline([str(part) for part in command])}", flush=True)
    # Each project keeps its own lock, imports, output paths and command semantics.
    environment = os.environ.copy()
    interpreter_directory = str(Path(sys.executable).parent)
    environment["PATH"] = interpreter_directory + os.pathsep + environment.get("PATH", "")
    environment["PYTHONUTF8"] = "1"
    return subprocess.run(command, cwd=cwd, env=environment, shell=False, check=False).returncode


def check_projects(root, catalog, project="all", structure_only=False):
    # A committed index can describe ignored artifacts from another checkout.
    # Refresh local links without building books or running project tests.
    index_script = inside(root, "scripts/build_index.py")
    if not index_script.is_file():
        raise FileNotFoundError("Missing scripts/build_index.py for the series reading entry")
    inside(root, "index.html")
    code = run([sys.executable, "scripts/build_index.py"], Path(root).resolve())
    if code:
        return code
    problems = structure(root, catalog, project)
    if problems:
        for problem in problems:
            print(problem, file=sys.stderr)
        return 1
    print("Series structure and entry links: passed")
    if structure_only:
        return 0
    for name in selected_projects(project):
        command = ([sys.executable, "scripts/bookctl.py", "check", "--fast"]
                   if name == "agent-books" else [npm_command(), "test"])
        code = run(command, inside(root, name))
        if code:
            return code
    return 0


def build(root, catalog, product, lang="zh", pdf=False, epub=False):
    book = next((item for item in catalog["books"] if item["id"] == product), None)
    if book is None:
        raise ValueError(f"Unknown product: {product}")
    if lang not in ("zh", "en", "both"):
        raise ValueError("Language must be zh, en or both")
    if lang == "en" and "en" not in book["languages"]:
        print(f"{product} currently has no English edition", file=sys.stderr)
        return 2
    folder = inside(root, book["project"])
    if not folder.is_dir():
        raise FileNotFoundError(f"Missing project directory: {folder}")
    if product == "llm":
        if lang == "both":
            print("llm currently builds the Chinese edition only")
        code = run([npm_command(), "run", "build:llm"], folder)
        if code or not (pdf or epub):
            return code
        print("The course exporter emits PDF and EPUB together, including the answer editions.")
        return run([sys.executable, "scripts/llm/export_books.py"], folder)
    command = [sys.executable, "scripts/bookctl.py", "build", "--product", product, "--lang", lang]
    if pdf:
        command.append("--pdf")
    if epub:
        command.append("--epub")
    return run(command, folder)


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def add_tree(files, project_root, relative, suffixes):
    folder = inside(project_root, relative)
    if not folder.exists():
        return
    for path in folder.rglob("*"):
        parts = path.relative_to(project_root).parts
        excluded = any(part in SKIP_PARTS and not (
            part == "renders" and parts[:3] == ("design", "handdraw", "renders")
        ) for part in parts)
        if excluded or parts[:3] == ("exports", "cards", "output"):
            continue
        license_file = not path.suffix and re.search(r"(?:^|[-_.])(?:licen[cs]e|copying|notice)(?:$|[-_.])", path.name, re.I)
        if path.is_file() and (path.suffix.lower() in suffixes or license_file or path.name == ".gitignore"):
            resolved = path.resolve()
            if not resolved.is_relative_to(project_root.resolve()):
                raise ValueError(f"Collection source leaves project: {path}")
            files.add(path)


def collection_sources(root, catalog, project):
    folder = inside(root, project)
    if not folder.is_dir():
        raise FileNotFoundError(f"Missing project directory: {folder}")
    files = set()
    if project == "agent-books":
        artifacts = inside(folder, "yuyu-book/dist")
        prefixes = tuple(book["artifact_prefix"] + "-" for book in catalog["books"] if book["project"] == project)
        if artifacts.exists():
            for path in artifacts.iterdir():
                if path.is_file() and path.suffix.lower() in ARTIFACT_SUFFIXES and path.name.startswith(prefixes):
                    if not path.resolve().is_relative_to(folder):
                        raise ValueError(f"Artifact leaves project: {path}")
                    files.add(path)
        if files:
            metadata = ["LICENSE", "CREDITS.md", "docs/agent-series/sources.lock.json"]
            metadata.extend(path.relative_to(folder).as_posix() for path in (folder / "yuyu-book").glob("sources*.json"))
            for relative in metadata:
                path = inside(folder, relative)
                if path.is_file():
                    files.add(path)
    else:
        # Preserve the website's ../../book and ../../deliverables relationships.
        for name in ("exports", "book", "specs", "scripts", "design"):
            add_tree(files, folder, name, SITE_SUFFIXES)
        add_tree(files, folder, "deliverables", ARTIFACT_SUFFIXES | {".json", ".png", ".jpg", ".jpeg", ".webp", ".svg"})
        for name in ("开始阅读.html", "README.md", "package.json", "package-lock.json", "LICENSE", "NOTICE", "COPYING"):
            path = inside(folder, name)
            if path.is_file():
                files.add(path)
    return sorted(files, key=lambda item: item.relative_to(folder).as_posix())


def collect(root, catalog, project="all"):
    root = Path(root).resolve()
    destination = root / "dist"
    if destination.is_symlink() or destination.resolve() != destination:
        raise ValueError("dist must be a real directory inside the series root")
    index_script = inside(root, "scripts/build_index.py")
    if not index_script.is_file():
        raise FileNotFoundError("Missing scripts/build_index.py for collected reading entry")
    pending = []
    for name in selected_projects(project):
        folder = inside(root, name)
        sources = collection_sources(root, catalog, name)
        if not sources:
            raise ValueError(f"No existing artifacts to collect for {name}; build the project first")
        for source in sources:
            relative_source = source.relative_to(folder)
            child = Path(source.name) if name == "agent-books" and relative_source.parts[:2] == ("yuyu-book", "dist") else relative_source
            relative = (Path(name) / child).as_posix()
            target = inside(destination, relative)
            pending.append((name, source, target, relative))
    # Check all source and destination boundaries before making any copies.
    destination.mkdir(parents=True, exist_ok=True)
    records = []
    for name, source, target, relative in pending:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        source_hash = sha256(source)
        if sha256(target) != source_hash:
            raise OSError(f"Copied artifact hash mismatch: {relative}")
        records.append({"project": name, "source": source.relative_to(root).as_posix(),
                        "path": relative, "bytes": target.stat().st_size, "sha256": source_hash})
    report = {"schema_version": 1, "collected_at": datetime.now(timezone.utc).isoformat(),
              "projects": list(selected_projects(project)), "files": records,
              "scope": "Copies of existing files; no build or model calls; video/audio excluded; hashes verify copying only.",
              "note": "Only listed files belong to this collection; unrelated older files are not removed."}
    manifest = inside(destination, "manifest.json" if project == "all" else f"manifest-{project}.json")
    manifest.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Collected {len(records)} files; manifest: {manifest}")
    code = run([sys.executable, "scripts/build_index.py", "--dist"], root)
    if code:
        raise subprocess.CalledProcessError(code, [sys.executable, str(index_script), "--dist"])
    return report


def main(argv=None, *, root=ROOT):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="show the ten books and local entry status")
    checker = commands.add_parser("check", help="run structure and existing project checks")
    checker.add_argument("--project", choices=("all", *PROJECTS), default="all")
    checker.add_argument("--structure-only", action="store_true")
    builder = commands.add_parser("build", help="build a book using its existing builder")
    builder.add_argument("--product", choices=PRODUCTS, required=True)
    builder.add_argument("--lang", choices=("zh", "en", "both"), default="zh")
    builder.add_argument("--pdf", action="store_true")
    builder.add_argument("--epub", action="store_true")
    collector = commands.add_parser("collect", help="copy existing books and course website to dist")
    collector.add_argument("--project", choices=("all", *PROJECTS), default="all")
    collected = commands.add_parser("collected", help="merge the ten books into one volume-numbered PDF")
    collected.add_argument("--lang", choices=("zh",), default="zh")
    collected.add_argument("--date", default=None)
    args = parser.parse_args(argv)
    try:
        catalog = load_catalog(root)
        if args.command == "list":
            for book in catalog["books"]:
                entry = inside(root, f"{book['project']}/{book['read_entry']}")
                print(f"{book['id']:10} {book['title']} | {book['project']}/{book['read_entry']} | "
                      f"{'available' if entry.is_file() else 'not built'}")
            return 0
        if args.command == "check":
            return check_projects(root, catalog, args.project, args.structure_only)
        if args.command == "build":
            return build(root, catalog, args.product, args.lang, args.pdf, args.epub)
        if args.command == "collected":
            command = [sys.executable, "scripts/collected.py", "--lang", args.lang]
            if args.date:
                command += ["--date", args.date]
            return run(command, root)
        collect(root, catalog, args.project)
        return 0
    except subprocess.CalledProcessError as exc:
        return exc.returncode
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 127
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
