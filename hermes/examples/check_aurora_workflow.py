"""Run the book's eight-step project workflow using the real local CLI example."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid

from aurora_lab import initialize


def main() -> None:
    repository = Path(__file__).resolve().parents[2]
    run = repository / ".scratch/agent-series" / ("aurora-" + uuid.uuid4().hex[:12])
    project = run / "project"
    initialize(project)
    script = Path(__file__).with_name("aurora_lab.py")
    cases = []

    def check(name: str, expected_code: int, *, issues: int, observations: int):
        process = subprocess.run(
            [sys.executable, str(script), "check", str(project)], capture_output=True,
            text=True, encoding="utf-8", env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            check=False,
        )
        assert process.returncode == expected_code, (name, process.returncode, process.stderr)
        output = json.loads(process.stdout)
        report_path = project / "reports/latest.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        assert len(report["issues"]) == issues
        assert len(report["observations"]) == observations
        cases.append({"step": name, "exit_code": process.returncode,
                      "stdout": output, "saved_report": report})
        return report

    initial = check("initial", 0, issues=0, observations=0)
    (project / "docs/setup.md").rename(project / "docs/install.md")
    broken = check("rename without updating index", 1, issues=1, observations=0)
    index = project / "docs/index.md"
    index.write_text(index.read_text(encoding="utf-8").replace("setup.md", "install.md"), encoding="utf-8")
    repaired = check("update index to install.md", 0, issues=0, observations=0)
    assert len({r["input_digest"] for r in (initial, broken, repaired)}) == 3
    rules_path = project / "rules.json"
    rules = json.loads(rules_path.read_text(encoding="utf-8"))
    rules["scan_examples"] = True
    rules_path.write_text(json.dumps(rules), encoding="utf-8")
    check("include example URLs", 0, issues=0, observations=1)
    rules["include_archive"] = True
    rules_path.write_text(json.dumps(rules), encoding="utf-8")
    check("include archived documents", 1, issues=1, observations=1)
    previous = (project / "reports/latest.json").read_bytes()
    rules["scan_examples"] = "false"
    rules_path.write_text(json.dumps(rules), encoding="utf-8")
    check("invalid JSON boolean leaves old report", 2, issues=1, observations=1)
    assert (project / "reports/latest.json").read_bytes() == previous
    rules.update(scan_examples=True, include_archive=False)
    rules_path.write_text(json.dumps(rules), encoding="utf-8")
    final = check("restore valid policy", 0, issues=0, observations=1)
    repeat = check("repeat unchanged input", 0, issues=0, observations=1)
    assert repeat == final
    result = {"date": "2026-11-10", "python": sys.version.split()[0],
              "scope": "Original Aurora CLI only; no Hermes host or model",
              "script_sha256": hashlib.sha256(script.read_bytes()).hexdigest(),
              "driver_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "passed": True, "cases": cases}
    (run / "report.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": True, "steps": len(cases), "report": str(run / "report.json")}))


if __name__ == "__main__":
    main()
