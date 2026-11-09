"""Build and select local release directories; never execute manifest commands."""
import argparse
import json
import os
import re
import shutil
import tempfile
from pathlib import Path

from check_package import check_package, sha256


def release_name(value):
    if not isinstance(value, str) or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._-]{0,63}", value):
        raise ValueError("release must be a simple name of 1 to 64 characters")
    return value


def files_in(root):
    """Inventory an explicitly prepared payload. Links are never packaged."""
    files = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
            raise ValueError("links are not supported in a release")
        if not path.resolve().is_relative_to(root):
            raise ValueError("file leaves the release directory")
        if path.is_file():
            files[path.relative_to(root).as_posix()] = path
        elif not path.is_dir():
            raise ValueError("payload contains a non-regular file")
    return files


def checked_release(directory):
    root = Path(directory).resolve()
    inventory = files_in(root)
    result = check_package(root)
    if result["status"] != "ok":
        raise ValueError("; ".join(result["problems"]))
    manifest = json.loads((root / "release.json").read_text(encoding="utf-8"))
    if set(inventory) != set(manifest["files"]) | {"release.json"}:
        raise ValueError("release contains unlisted or missing files")
    return manifest


def release_path(store, name):
    store = Path(store).resolve()
    releases = store / "releases"
    target = releases / release_name(name)
    if releases.is_symlink() or target.is_symlink():
        raise ValueError("release store must not contain directory links")
    if releases.resolve() != releases or target.resolve() != target:
        raise ValueError("release directory is redirected")
    return target


def build(payload, store, name, *, created, scope, start, health):
    source = Path(payload).resolve()
    target = release_path(store, name)
    if not source.is_dir() or target.is_relative_to(source):
        raise ValueError("payload must be a directory separate from the release store")
    if target.exists():
        raise ValueError("release already exists; use a new release name")
    inventory = files_in(source)
    if "release.json" in inventory:
        raise ValueError("payload must not include a pre-existing release.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".build-", dir=target.parent)).resolve()
    try:
        for relative, path in inventory.items():
            copied = staging / relative
            copied.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, copied)
        manifest = dict(release=name, created=created, scope=scope, start=start, health=health,
                        files={relative: sha256(staging / relative) for relative in inventory})
        (staging / "release.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        checked_release(staging)
        staging.rename(target)
    finally:
        if staging.exists():
            if not staging.is_relative_to(target.parent.resolve()):
                raise ValueError("unexpected staging directory")
            shutil.rmtree(staging)
    return {"status": "ok", "release": name, "files_checked": len(inventory)}


def select(store, name):
    """Check all bytes before atomically replacing the current-release pointer."""
    root = Path(store).resolve()
    target = release_path(root, name)
    manifest = checked_release(target)
    if manifest["release"] != name:
        raise ValueError("directory name does not match manifest release")
    state = {"release": name, "manifest_sha256": sha256(target / "release.json")}
    descriptor, temporary = tempfile.mkstemp(prefix=".current-", suffix=".json", dir=root)
    temporary = Path(temporary)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(state, ensure_ascii=False, indent=2) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, root / "current.json")
    finally:
        temporary.unlink(missing_ok=True)
    return {"status": "ok", **state}


def current(store):
    root = Path(store).resolve()
    pointer = root / "current.json"
    if pointer.is_symlink():
        raise ValueError("current pointer must not be a link")
    state = json.loads(pointer.read_text(encoding="utf-8"))
    if not isinstance(state, dict):
        raise ValueError("current pointer must be an object")
    target = release_path(root, state.get("release"))
    manifest = checked_release(target)
    if manifest["release"] != state["release"] or sha256(target / "release.json") != state.get("manifest_sha256"):
        raise ValueError("selected manifest changed; inspect the release before selecting again")
    return {"status": "ok", "release": state["release"], "directory": str(target)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    builder = commands.add_parser("build", help="copy an explicit payload and hash every file")
    builder.add_argument("--payload", required=True, type=Path)
    builder.add_argument("--store", required=True, type=Path)
    builder.add_argument("--release", required=True)
    for option in ("created", "scope", "start", "health"):
        builder.add_argument("--" + option, required=True)
    selector = commands.add_parser("select", help="select a validated version, including rollback")
    selector.add_argument("--store", required=True, type=Path)
    selector.add_argument("--release", required=True)
    resolver = commands.add_parser("current", help="validate and print the selected directory")
    resolver.add_argument("--store", required=True, type=Path)
    args = parser.parse_args()
    try:
        if args.command == "build":
            result = build(args.payload, args.store, args.release, created=args.created, scope=args.scope,
                           start=args.start, health=args.health)
        elif args.command == "select":
            result = select(args.store, args.release)
        else:
            result = current(args.store)
    except (OSError, ValueError, RuntimeError) as error:
        result = {"status": "failed", "error": str(error)}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
