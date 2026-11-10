"""Create an independent faulty exercise and capture real local check receipts."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
FROZEN_FILES = ("check.py", "cases.json", "rules.md")
FAULTY_SOURCE = '''"""Qinghe registration exercise. Apply the rules in rules.md."""


def valid_state(capacity, confirmed, waiting, person, action):
    if type(capacity) is not int or capacity < 0:
        return False
    if not isinstance(confirmed, list) or not isinstance(waiting, list):
        return False
    people = confirmed + waiting + [person]
    if any(not isinstance(item, str) or not item.strip() for item in people):
        return False
    registered = confirmed + waiting
    return (len(set(registered)) == len(registered)
            and len(confirmed) <= capacity
            and (not waiting or len(confirmed) == capacity)
            and action in ("register", "cancel"))


def transition(capacity, confirmed, waiting, person, action):
    if not valid_state(capacity, confirmed, waiting, person, action):
        return {"status": "invalid", "confirmed": confirmed, "waiting": waiting}
    confirmed, waiting = confirmed.copy(), waiting.copy()
    if action == "register":
        if person in confirmed:
            status = "duplicate"
        elif len(confirmed) <= capacity:
            confirmed.append(person)
            status = "confirmed"
        else:
            waiting.append(person)
            status = "waiting"
    elif person in confirmed:
        confirmed.remove(person)
        status = "cancelled"
    elif person in waiting:
        waiting.remove(person)
        status = "cancelled"
    else:
        status = "not_found"
    return {"status": status, "confirmed": confirmed, "waiting": waiting}
'''
CHECK_SOURCE = '''"""Run the public business contract without changing the candidate."""
from copy import deepcopy
import json
from pathlib import Path

from registration import transition


def main():
    cases = json.loads(Path(__file__).with_name("cases.json").read_text(encoding="utf-8"))
    results = []
    for case in cases:
        request = deepcopy(case["input"])
        try:
            actual = transition(**request)
            exception = None
        except Exception as exc:
            actual = None
            exception = f"{type(exc).__name__}: {exc}"
        unchanged = request == case["input"]
        results.append({"id": case["id"],
                        "passed": exception is None and actual == case["expected"] and unchanged,
                        "input_unchanged": unchanged, "actual": actual,
                        "expected": case["expected"], "exception": exception})
    report = {"kind": "public_business_contract", "passed": sum(row["passed"] for row in results),
              "total": len(results), "results": results}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] == report["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
'''


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def prepare(project):
    project = Path(project).resolve()
    payloads = {
        "registration.py": FAULTY_SOURCE.encode("utf-8"),
        "check.py": CHECK_SOURCE.encode("utf-8"),
        "cases.json": (ROOT / "evaluation/business-cases.json").read_bytes(),
        "rules.md": (ROOT / "materials/rules-v1.md").read_bytes(),
    }
    project.mkdir(parents=True, exist_ok=False)
    for name, data in payloads.items():
        (project / name).write_bytes(data)
    lock = {"version": 1, "frozen": {name: sha256(payloads[name]) for name in FROZEN_FILES},
            "initial_candidate_sha256": sha256(payloads["registration.py"])}
    (project / "exercise-lock.json").write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
    return {"kind": "exercise_prepared", "project": str(project),
            "files": sorted([*payloads, "exercise-lock.json"]), "model_calls": 0}


def frozen_hashes(project):
    lock = json.loads((project / "exercise-lock.json").read_text(encoding="utf-8"))
    if lock.get("version") != 1 or set(lock.get("frozen", {})) != set(FROZEN_FILES):
        raise ValueError("Invalid exercise lock")
    observed = {name: sha256((project / name).read_bytes()) for name in FROZEN_FILES}
    if observed != lock["frozen"]:
        raise ValueError("Frozen checker, cases or rules changed")
    return observed


def text_output(value):
    return value.decode("utf-8", errors="replace") if isinstance(value, bytes) else value or ""


def check(project, timeout=10.0):
    project = Path(project).resolve()
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("Timeout must be a finite positive number")
    receipt = {"kind": "local_process_receipt", "started_at": datetime.now(timezone.utc).isoformat(),
               "project": str(project), "command": [sys.executable, "-X", "utf8", "-B", "check.py"],
               "status": "not_started", "returncode": None, "stdout": "", "stderr": "",
               "timeout_seconds": timeout, "model_calls": 0}
    try:
        receipt["frozen_sha256"] = frozen_hashes(project)
        receipt["candidate_sha256"] = sha256((project / "registration.py").read_bytes())
    except (OSError, ValueError, TypeError) as exc:
        receipt.update(status="invalid_project", error=str(exc), elapsed_seconds=0.0)
        return receipt
    started = time.perf_counter()
    try:
        result = subprocess.run(receipt["command"], cwd=project, shell=False,
                                capture_output=True, timeout=timeout)
        receipt.update(returncode=result.returncode, stdout=text_output(result.stdout),
                       stderr=text_output(result.stderr))
        try:
            report = json.loads(receipt["stdout"])
            valid_report = (isinstance(report, dict) and report.get("kind") == "public_business_contract"
                            and type(report.get("total")) is int and report["total"] == 12
                            and type(report.get("passed")) is int and 0 <= report["passed"] <= 12
                            and isinstance(report.get("results"), list) and len(report["results"]) == 12)
        except ValueError:
            valid_report = False
        if valid_report and result.returncode in (0, 1):
            receipt["status"] = "passed" if result.returncode == 0 and report["passed"] == 12 else "business_failed"
            receipt["business"] = {key: report[key] for key in ("passed", "total")}
        else:
            receipt["status"] = "execution_failed"
    except subprocess.TimeoutExpired as exc:
        receipt.update(status="timeout", stdout=text_output(exc.stdout), stderr=text_output(exc.stderr))
    except OSError as exc:
        receipt.update(status="execution_failed", error=str(exc))
    receipt["elapsed_seconds"] = round(time.perf_counter() - started, 6)
    try:
        frozen_hashes(project)
        after = sha256((project / "registration.py").read_bytes())
        receipt["candidate_unchanged_during_check"] = after == receipt["candidate_sha256"]
        if not receipt["candidate_unchanged_during_check"]:
            receipt.update(status="input_changed_during_check", error="Candidate changed during execution")
    except (OSError, ValueError, TypeError) as exc:
        receipt.update(status="input_changed_during_check", error=str(exc))
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prep = commands.add_parser("prepare")
    prep.add_argument("--out", type=Path, required=True)
    run = commands.add_parser("check")
    run.add_argument("--project", type=Path, required=True)
    run.add_argument("--receipt", type=Path)
    run.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args()
    try:
        if args.command == "prepare":
            result = prepare(args.out)
        else:
            if args.receipt and args.receipt.exists():
                raise ValueError("Receipt already exists; choose a new path")
            result = check(args.project, args.timeout)
            if args.receipt:
                args.receipt.parent.mkdir(parents=True, exist_ok=True)
                with args.receipt.open("x", encoding="utf-8") as stream:
                    stream.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get("status", "passed") == "passed" else 1
    except (OSError, ValueError) as exc:
        parser.exit(2, f"error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
