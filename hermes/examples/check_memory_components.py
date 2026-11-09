"""Run pinned Hermes MemoryStore and skill metadata components, without an LLM.

The real store, scanner, atomic writer and home resolver are imported unchanged.
Only tools.memory_tool's path/OS-lock facade is replaced to avoid CLI/registry
initialization. This is a component test, not a complete Hermes session.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import types
import uuid

COMMIT = "2bd378ed1b8d6bf2192cb26e0a55ff3091e6bd19"
FILES = ["tools/memory_tool_store.py", "tools/memory_tool.py", "tools/threat_patterns.py", "utils.py",
         "hermes_constants.py", "hermes_dir_acl.py", "hermes_yaml.py", "agent/skill_utils.py"]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--dependencies", type=Path)
    parser.add_argument("--without-yaml", action="store_true",
                        help="Leave unused YAML dependency unavailable; test frontmatter fallback only")
    args = parser.parse_args()
    source = args.upstream.resolve(strict=True)
    if args.dependencies:
        sys.path.insert(0, str(args.dependencies.resolve(strict=True)))
    sys.path.insert(0, str(source))
    if args.without_yaml:
        # MemoryStore/atomic writes never call YAML. The skill parser's real
        # fallback catches this missing safe_load import; no parser is faked.
        sys.modules["hermes_yaml"] = types.ModuleType("hermes_yaml")
    repo = Path(__file__).resolve().parents[2]
    run = repo / ".scratch/agent-series" / ("hermes-memory-" + uuid.uuid4().hex[:12])
    run.mkdir(parents=True)
    profile = run / "profile"
    profile.mkdir()
    os.environ["HERMES_HOME"] = str(profile)
    # Namespace adapters do not load the application package initializers.
    for name in ("tools", "agent"):
        package = types.ModuleType(name)
        package.__path__ = [str(source / name)]
        sys.modules[name] = package
    constants = load("hermes_constants", source / "hermes_constants.py")
    assert constants.get_hermes_home().resolve() == profile.resolve()
    facade = types.ModuleType("tools.memory_tool")
    facade.get_memory_dir = lambda: profile / "memories"
    if os.name == "nt":
        import msvcrt
        facade.fcntl, facade.msvcrt = None, msvcrt
    else:
        import fcntl
        facade.fcntl, facade.msvcrt = fcntl, None
    sys.modules["tools.memory_tool"] = facade
    store_module = load("tools.memory_tool_store", source / "tools/memory_tool_store.py")
    # Execute the original target validator's AST unchanged, without importing
    # the unrelated live-tool registry/approval surface around it.
    tree = ast.parse((source / "tools/memory_tool.py").read_text(encoding="utf-8"))
    validator = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                     and node.name == "_memory_target_error")
    isolated = ast.Module(body=[ast.ImportFrom(module="__future__",
        names=[ast.alias(name="annotations")], level=0), validator], type_ignores=[])
    namespace = {"FAILURE_CLASS": store_module.FAILURE_CLASS}
    exec(compile(ast.fix_missing_locations(isolated), "pinned-memory-target-validator", "exec"), namespace)
    facade._memory_target_error = namespace["_memory_target_error"]
    skill_module = load("agent.skill_utils", source / "agent/skill_utils.py")
    cases = []

    def passed(name: str, **evidence) -> None:
        cases.append({"case": name, "passed": True, **evidence})
        print("PASS", name, flush=True)

    store = store_module.MemoryStore(memory_char_limit=100, user_char_limit=70)
    store.load_from_disk()
    assert store.format_for_system_prompt("memory") is None
    assert store.add("memory", "Project Aurora uses pytest.")["success"]
    disk = profile / "memories/MEMORY.md"
    assert disk.read_text(encoding="utf-8") == "Project Aurora uses pytest."
    assert store.format_for_system_prompt("memory") is None
    restored = store_module.MemoryStore(memory_char_limit=100, user_char_limit=70)
    restored.load_from_disk()
    assert "pytest" in restored.format_for_system_prompt("memory")
    passed("write persists but prompt snapshot is frozen until load")

    assert restored.add("memory", "Project Aurora uses pytest.")["success"]
    assert len(restored.memory_entries) == 1
    assert restored.patch("memory", "pytest", "unittest")["success"]
    assert restored.memory_entries == ["Project Aurora uses unittest."]
    assert "pytest" in restored.format_for_system_prompt("memory")
    passed("duplicate add is idempotent and patch preserves entry context")

    before = disk.read_bytes()
    overflow = restored.add("memory", "x" * 101)
    assert overflow["success"] is False and disk.read_bytes() == before
    passed("character limit refuses overflow without changing disk")

    assert restored.add("memory", "Project Beacon uses unittest.")["success"]
    before = disk.read_bytes()
    ambiguous = restored.remove("memory", "unittest")
    assert ambiguous["success"] is False and disk.read_bytes() == before
    passed("ambiguous substring removal is refused")

    failed = restored.apply_batch("memory", [
        {"action": "add", "content": "A short note."},
        {"action": "patch", "old_text": "absent-needle", "content": "changed"},
    ])
    assert failed["success"] is False and disk.read_bytes() == before
    passed("failed batch commits none of its operations")

    assert restored.remove("memory", "Project Beacon uses unittest.")["success"]
    assert restored.add("user", "User prefers concise Chinese.")["success"]
    fresh = store_module.MemoryStore(memory_char_limit=100, user_char_limit=70)
    fresh.load_from_disk()
    assert fresh.memory_entries == ["Project Aurora uses unittest."]
    assert fresh.user_entries == ["User prefers concise Chinese."]
    passed("new store restores both targets after exact removal")

    # A damaged file must not be silently treated as an empty writable store.
    disk.write_bytes(b"\xff\xfe\x80")
    damaged = disk.read_bytes()
    result = fresh.add("memory", "another note")
    assert result["success"] is False and disk.read_bytes() == damaged
    passed("invalid UTF-8 refuses write without erasing the file")
    disk.write_text("Project Aurora uses unittest.", encoding="utf-8")

    meta, body = skill_module.parse_frontmatter(
        "\ufeff---\nname: book-review\ndescription: Review a local draft\n---\nRead the draft first.\n"
    )
    assert meta["name"] == "book-review" and "Read the draft" in body
    skill_root = profile / "skills/book-review"
    skill_root.mkdir(parents=True)
    (skill_root / "SKILL.md").write_text("# book-review\n", encoding="utf-8")
    support_path = skill_root / "references/example/SKILL.md"
    assert skill_module.is_skill_support_path(support_path)
    assert skill_module.is_excluded_skill_path(profile / "skills/.git/SKILL.md")
    passed("skill frontmatter handles BOM and support folders are excluded",
           yaml_path="fallback" if args.without_yaml else "upstream loader")

    report = {
        "date": "2026-11-10", "baseline": "Hermes v0.23.0", "commit": COMMIT,
        "platform": sys.platform, "python": sys.version.split()[0],
        "scope": "Real upstream storage and metadata components; no agent/model/gateway",
        "adapter": "tools.memory_tool path/OS-lock facade plus original validator AST; package initializers bypassed",
        "yaml_import_omitted": args.without_yaml,
        "budgets": {"memory_chars": 100, "user_chars": 70},
        "upstream_sha256": {p: hashlib.sha256((source / p).read_bytes()).hexdigest() for p in FILES},
        "cases": cases, "passed": True,
    }
    (run / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("Evidence:", run, flush=True)
    print(json.dumps(report), flush=True)


if __name__ == "__main__":
    main()
