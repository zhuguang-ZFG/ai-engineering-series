"""Run original teaching fixtures without launching Codex or using a model."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from inspect_exec import inspect

HERE = Path(__file__).resolve().parent


def check(condition, message):
    if not condition:
        raise RuntimeError(message)


def main():
    cases = []
    packaged = HERE / "plugin-example/scripts/hook_guard.py"
    check(packaged.read_bytes() == (HERE / "hook_guard.py").read_bytes(),
          "packaged handler differs from the tested handler")
    manifest = json.loads((HERE / "plugin-example/.codex-plugin/plugin.json").read_text(encoding="utf-8"))
    check((HERE / "plugin-example" / manifest["hooks"]).is_file(), "missing declared hooks")
    check(all((HERE / "plugin-example" / path).is_dir() for path in manifest["skills"]),
          "missing declared skills")
    cases.append({"name": "plugin-files-and-handler-copy", "passed": True})
    with tempfile.TemporaryDirectory(prefix="codex-parcel-") as temporary:
        work = Path(temporary) / "parcel"
        shutil.copytree(HERE / "workshop", work)

        def tests():
            return subprocess.run([sys.executable, "-B", "-m", "unittest", "-v"],
                                  cwd=work, capture_output=True, text=True,
                                  encoding="utf-8", timeout=15)

        before = tests()
        check(before.returncode != 0 and "grams=1001" in before.stderr,
              "seed did not reproduce the intended failure")
        code = work / "parcel.py"
        original = code.read_text(encoding="utf-8")
        check(original.count("grams // 1000") == 1, "unexpected seed")
        code.write_text(original.replace("grams // 1000", "(grams + 999) // 1000"),
                        encoding="utf-8")
        after = tests()
        check(after.returncode == 0, after.stderr)
        cases.extend([{"name": "parcel-before", "exit_code": before.returncode, "passed": True},
                      {"name": "parcel-after", "exit_code": after.returncode, "passed": True}])

    fixtures = HERE / "fixtures"
    for name, expected in (("hook-read.json", None), ("hook-deny.json", "deny")):
        result = subprocess.run([sys.executable, "-B", str(HERE / "hook_guard.py")],
                                input=(fixtures / name).read_text(encoding="utf-8"),
                                capture_output=True, text=True, encoding="utf-8", timeout=10)
        check(result.returncode == 0, result.stderr)
        output = json.loads(result.stdout)
        check(output["hookSpecificOutput"].get("permissionDecision") == expected,
              "wrong hook result")
        cases.append({"name": name, "passed": True, "output": output})
    malformed = subprocess.run([sys.executable, "-B", str(HERE / "hook_guard.py")],
                               input="{bad", capture_output=True, text=True, timeout=10)
    check(malformed.returncode == 1 and not malformed.stdout, "malformed hook input accepted")
    cases.append({"name": "hook-malformed", "passed": True})
    for name, code, expected_ok, expected_review in (
        ("exec-success.jsonl", 0, True, False),
        ("exec-command-failed.jsonl", 0, True, True),
        ("exec-incomplete.jsonl", 0, False, True),
        ("exec-success.jsonl", 1, False, True),
    ):
        report = inspect((fixtures / name).read_text(encoding="utf-8").splitlines(), code)
        check(report["stream_ok"] == expected_ok and report["needs_review"] == expected_review,
              f"wrong stream classification: {name}")
        cases.append({"name": f"{name}:exit={code}", "passed": True, "result": report})
    for name, lines in (("reject-non-json", ["not json"]),
                        ("reject-missing-item-id", ['{"type":"item.completed","item":{}}'])):
        try:
            inspect(lines, 0)
        except ValueError:
            cases.append({"name": name, "passed": True})
        else:
            raise RuntimeError("invalid stream accepted")
    failed_patch = [json.dumps(event) for event in (
        {"type": "thread.started", "thread_id": "fixture-thread"},
        {"type": "turn.started"},
        {"type": "item.completed", "item": {"id": "patch-1", "type": "file_change",
         "status": "failed", "changes": [{"path": "parcel.py", "kind": "update"}]}},
        {"type": "turn.completed", "usage": {"input_tokens": 0, "cached_input_tokens": 0,
         "cache_write_input_tokens": 0, "output_tokens": 0, "reasoning_output_tokens": 0}},
    )]
    check(inspect(failed_patch, 0)["needs_review"], "failed patch accepted")
    cases.append({"name": "failed-patch-needs-review", "passed": True})
    inputs = sorted(p for p in HERE.rglob("*") if p.is_file()
                    and "__pycache__" not in p.parts and p.suffix in (".py", ".json", ".jsonl", ".md"))
    report = {"date": "2026-11-10", "kind": "original-offline-workshop",
              "model_used": False, "codex_host_started": False, "cases": cases,
              "inputs": {p.relative_to(HERE).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in inputs}, "passed": True}
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
