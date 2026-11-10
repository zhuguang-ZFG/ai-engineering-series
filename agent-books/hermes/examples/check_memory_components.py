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

    # A second object is stale in memory, but each mutation reloads under the lock.
    disk.write_text("Aurora uses unittest.", encoding="utf-8")
    left = store_module.MemoryStore(memory_char_limit=500)
    right = store_module.MemoryStore(memory_char_limit=500)
    left.load_from_disk()
    right.load_from_disk()
    assert left.add("memory", "Aurora docs are under docs/.")["success"]
    assert right.add("memory", "Aurora archives are excluded.")["success"]
    merged = disk.read_text(encoding="utf-8")
    assert "docs/" in merged and "archives are excluded" in merged
    assert "docs/" not in right.format_for_system_prompt("memory")
    passed("sequential stale writers preserve each other's additions",
           concurrency_scope="Two instances, deterministic interleaving; not simultaneous processes")

    approval = right.resolve_entry("memory", "Aurora uses", "patch")
    assert approval["matched_entry"] == "Aurora uses unittest."
    assert left.patch("memory", "unittest", "pytest")["success"]
    before = disk.read_bytes()
    rejected = right.patch("memory", "Aurora uses", "Aurora prefers",
                           matched_entry=approval["matched_entry"])
    assert rejected["success"] is False and disk.read_bytes() == before
    passed("a staged edit refuses an entry changed after resolution")

    disk.write_text("Aurora\n§\nAurora backup", encoding="utf-8")
    exact = store_module.MemoryStore(memory_char_limit=500)
    exact.load_from_disk()
    assert exact.remove("memory", "Aurora")["success"]
    assert disk.read_text(encoding="utf-8") == "Aurora backup"
    passed("whole-entry exact match wins over substring matches")

    disk.write_text("Aurora builds docs; Beacon builds docs.", encoding="utf-8")
    before = disk.read_bytes()
    result = exact.patch("memory", "builds docs", "checks docs")
    assert result["success"] is False and disk.read_bytes() == before
    passed("repeated spans inside one entry are refused")

    disk.write_text("\ufeffAurora uses § literally.\n§\nAurora uses § literally.", encoding="utf-8")
    bom = store_module.MemoryStore(memory_char_limit=500)
    bom.load_from_disk()
    assert bom.memory_entries == ["Aurora uses § literally."]
    before = disk.read_bytes()
    assert bom.resolve_entry("memory", "Aurora uses", "remove")["success"]
    assert disk.read_bytes() == before
    passed("BOM and duplicates normalize in memory while resolve leaves disk untouched")

    disk.write_text("A" * 120, encoding="utf-8")
    drift = store_module.MemoryStore(memory_char_limit=100)
    drift.load_from_disk()
    before = disk.read_bytes()
    blocked = drift.replace("memory", "A" * 120, "Short note")
    assert blocked["success"] is False and disk.read_bytes() == before
    backup = Path(blocked["drift_backup"])
    assert backup.read_bytes() == before
    removed = drift.remove("memory", "A" * 120)
    assert removed["success"] and Path(removed["drift_backup"]).read_bytes() == before
    assert disk.read_text(encoding="utf-8") == ""
    passed("oversized foreign entry blocks rewrite and requires backup before deletion")

    disk.write_text("Aurora tests", encoding="utf-8")
    capped = store_module.MemoryStore(memory_char_limit=100)
    capped.load_from_disk()
    failures = [capped.patch("memory", "missing", "replacement") for _ in range(4)]
    assert all(item["success"] is False for item in failures)
    assert failures[-1].get("done") is True
    capped.reset_consolidation_failures()
    assert "done" not in capped.patch("memory", "missing", "replacement")
    passed("consecutive consolidation failures terminate and turn reset restores budget")

    disk.write_text("Old stable entry", encoding="utf-8")
    fault = store_module.MemoryStore(memory_char_limit=500)
    fault.load_from_disk()
    original_writer = store_module.atomic_write_text

    def fail_before_replace(*args, **kwargs):
        raise OSError("injected write failure before replacement")

    store_module.atomic_write_text = fail_before_replace
    try:
        try:
            fault.add("memory", "New tentative entry")
            raise AssertionError("write failure was not surfaced")
        except RuntimeError as error:
            assert "Failed to write memory file" in str(error)
        assert disk.read_text(encoding="utf-8") == "Old stable entry"
        assert "New tentative entry" in fault.memory_entries
    finally:
        store_module.atomic_write_text = original_writer
    fault.load_from_disk()
    assert fault.memory_entries == ["Old stable entry"]
    passed("write failure preserves disk but requires reload to reconcile live state",
           injection="atomic_write_text replaced by a function raising OSError before disk mutation")

    disk.write_text("Old project note has thirty chars", encoding="utf-8")
    compact = store_module.MemoryStore(memory_char_limit=100)
    compact.load_from_disk()
    replacement = "N" * 90
    result = compact.apply_batch("memory", [
        {"action": "add", "content": replacement},
        {"action": "remove", "old_text": "Old project note has thirty chars"},
    ])
    assert result["success"] and disk.read_text(encoding="utf-8") == replacement
    passed("batch enforces the final budget rather than a temporary intermediate size",
           final_chars=len(replacement), limit=100)

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
