"""Check pinned Codex policy parsing and protocol generation without a model.

Only explicit policy files, --help, --version and static schema generation are
used. This does not start an agent session or test OS sandbox enforcement.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import uuid

VERSION = "codex-cli 0.167.0"
COMMIT = "086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a"
ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", required=True, type=Path)
    args = parser.parse_args()
    binary = args.binary.resolve(strict=True)
    output = ROOT / ".scratch/agent-series" / ("codex-local-" + uuid.uuid4().hex[:10])
    output.mkdir(parents=True)
    allowed = {"SYSTEMROOT", "WINDIR", "COMSPEC", "PATH", "PATHEXT",
               "TEMP", "TMP", "PROGRAMFILES", "PROGRAMFILES(X86)"}
    env = {key: value for key, value in os.environ.items() if key.upper() in allowed}
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0

    def run(command: list[str], expected: int = 0) -> subprocess.CompletedProcess:
        result = subprocess.run([str(binary), *command], cwd=output, env=env,
                                capture_output=True, text=True, encoding="utf-8",
                                timeout=45, creationflags=flags)
        if result.returncode != expected:
            raise AssertionError((command, result.returncode, result.stdout, result.stderr))
        return result

    version = run(["--version"]).stdout.strip()
    assert version == VERSION, version
    rules = Path(__file__).with_name("review.rules")
    cases = []
    for name, command, decision in (
        ("read-status", ["git", "status", "--short"], "allow"),
        ("read-diff", ["git", "diff", "--stat"], "allow"),
        ("publish", ["git", "push", "origin", "review"], "prompt"),
        ("force-publish", ["git", "push", "--force", "origin", "review"], "forbidden"),
        ("unmatched", ["git", "commit", "-m", "example"], None),
        ("absolute-unmatched", ["C:/book/bin/git.exe", "status"], None),
    ):
        result = json.loads(run(["execpolicy", "check", "--rules", str(rules), *command]).stdout)
        assert result.get("decision") == decision, (name, result)
        cases.append({"name": name, "command": command, "result": result, "passed": True})
    bad = output / "invalid.rules"
    bad.write_text('prefix_rule(pattern=["git","status"], match=[["git","push"]])\n', encoding="utf-8")
    rejected = subprocess.run([str(binary), "execpolicy", "check", "--rules", str(bad), "git", "status"],
                              cwd=output, env=env, capture_output=True, text=True,
                              encoding="utf-8", timeout=45, creationflags=flags)
    assert rejected.returncode != 0, rejected.stdout
    cases.append({"name": "invalid-positive-example", "exit_code": rejected.returncode, "passed": True})
    schema = output / "schema"
    run(["app-server", "generate-json-schema", "--out", str(schema)])
    schema_files = sorted(schema.rglob("*.json"))
    assert schema_files
    joined = "\n".join(path.read_text(encoding="utf-8") for path in schema_files)
    for method in ("initialize", "thread/start", "turn/start", "turn/interrupt"):
        assert method in joined, method
    cases.append({"name": "static-app-server-schema", "files": len(schema_files), "passed": True})
    for name, command in (("cli-help", ["--help"]), ("exec-help", ["exec", "--help"]),
                          ("plugin-help", ["plugin", "--help"]),
                          ("policy-help", ["execpolicy", "check", "--help"])):
        (output / (name + ".txt")).write_text(run(command).stdout, encoding="utf-8")
    report = {
        "date": "2026-11-10", "version": version, "source_commit": COMMIT,
        "platform": os.name, "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
        "cases": cases, "model_used": False, "agent_session_started": False,
        "sandbox_enforcement_tested": False, "passed": True,
        "fixtures": {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                     for path in (Path(__file__), rules)},
    }
    (output / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False), flush=True)
    print("Evidence:", output, flush=True)


if __name__ == "__main__":
    main()
