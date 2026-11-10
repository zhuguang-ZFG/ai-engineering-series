"""Offline context export, mechanical checks and paired manual-review accounting."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ('输出约定：仅有 case_id、answer、evidence、actions 四个字段。'
            'case_id 为题目编号；answer 为非空说明文字；evidence 为至少一项'
            ' {"source": "材料 ID", "quote": "逐字原文"} 的数组；'
            'actions 为数组，本次只读任务必须为空。引用必须来自本次提供的文字。')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    def constant(value):
        raise ValueError(f"Invalid JSON constant: {value}")

    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)


def read_json(path):
    return strict_json(Path(path).read_text(encoding="utf-8-sig"))


def write_json(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                          encoding="utf-8")


def cases(split):
    return read_json(ROOT / "cases" / f"{split}.json")


def bundle(split, case_id, mode="full", variant="a"):
    case = next((item for item in cases(split) if item["id"] == case_id), None)
    if case is None:
        raise ValueError(f"Unknown case in {split}: {case_id}")
    catalog = read_json(ROOT / "materials/catalog.json")["documents"]
    all_sources = {key: (ROOT / "materials" / catalog[key]).read_text(encoding="utf-8")
                   for key in case["sources"]}
    if mode == "summary":
        if "summary" not in case:
            raise ValueError("This case has no authored teaching summary")
        sources = {"S01-v1": case["summary"]}
    elif mode == "selected":
        if "selected" not in case:
            raise ValueError("This case has no curated selection")
        sources = {key: all_sources[key] for key in case["selected"]}
    else:
        sources = all_sources
    prompt = (ROOT / "prompts" / f"{variant}.txt").read_text(encoding="utf-8").strip()
    blocks = [prompt, f"题目：{case_id}\n任务：{case['task']}", CONTRACT]
    blocks += [f"材料开始 [{key}]\n{value}\n材料结束 [{key}]"
               for key, value in sources.items()]
    request = "\n\n".join(blocks) + "\n"
    return {"case_id": case_id, "split": split, "mode": mode, "variant": variant,
            "request": request, "request_sha256": digest(request.encode("utf-8")),
            "characters": len(request), "utf8_bytes": len(request.encode("utf-8")),
            "sources": sources,
            "source_hashes": {key: digest(value.encode("utf-8"))
                              for key, value in all_sources.items()},
            "omitted_sources": [key for key in all_sources if key not in sources],
            "note": "字符数不是 token 数；摘要为人工教学材料，来源哈希不表示原文已送入。"}


def export_context(folder, context):
    folder.mkdir(parents=True, exist_ok=False)
    (folder / "request.txt").write_bytes(context["request"].encode("utf-8"))
    write_json(folder / "context.json", context)


def check_response(context, raw):
    errors = []
    try:
        value = strict_json(raw)
    except (ValueError, TypeError) as exc:
        return {"mechanical_ok": False, "errors": [f"invalid_json: {exc}"],
                "manual_review_required": True}
    required = {"case_id", "answer", "evidence", "actions"}
    if not isinstance(value, dict) or set(value) != required:
        errors.append("fields: expected exactly case_id, answer, evidence, actions")
    else:
        if value["case_id"] != context["case_id"]:
            errors.append("case_id: mismatch")
        if not isinstance(value["answer"], str) or not value["answer"].strip():
            errors.append("answer: nonempty string required")
        if value["actions"] != []:
            errors.append("actions: this task permits no executed actions")
        evidence = value["evidence"]
        if not isinstance(evidence, list) or not evidence:
            errors.append("evidence: nonempty array required")
        else:
            for item in evidence:
                if (not isinstance(item, dict) or set(item) != {"source", "quote"}
                        or not isinstance(item["source"], str)
                        or not isinstance(item["quote"], str) or not item["quote"].strip()):
                    errors.append("evidence: invalid entry")
                elif item["source"] not in context["sources"]:
                    errors.append("evidence: source was not provided")
                elif item["quote"] not in context["sources"][item["source"]]:
                    errors.append("evidence: quote not present verbatim")
    return {"mechanical_ok": not errors, "errors": errors, "manual_review_required": True}


def prepare(folder, split, repeats, environment):
    if type(repeats) is not int or repeats < 1 or not environment.strip():
        raise ValueError("Positive repeats and an environment description are required")
    prepared = [(case["id"], variant, bundle(split, case["id"], variant=variant))
                for case in cases(split) for variant in ("a", "b")]
    folder.mkdir(parents=True, exist_ok=False)
    criteria = (ROOT / "evaluation/criteria.json").read_bytes()
    (folder / "criteria.json").write_bytes(criteria)
    runs = []
    for repeat in range(1, repeats + 1):
        # Alternate which variant is visited first; retain the same task order.
        for case_id in [case["id"] for case in cases(split)]:
            for variant in (("a", "b") if repeat % 2 else ("b", "a")):
                context = next(item[2] for item in prepared
                               if item[0] == case_id and item[1] == variant)
                slot = f"{case_id}-{repeat:02d}-{variant}"
                export_context(folder / slot, context)
                runs.append({"slot": slot, "case_id": case_id, "repeat": repeat,
                             "variant": variant, "request_sha256": context["request_sha256"],
                             "context_sha256": digest((folder / slot / "context.json").read_bytes())})
    plan = {"kind": "unexecuted_manual_experiment_plan", "split": split,
            "environment": environment, "repeats": repeats,
            "criteria_sha256": digest(criteria), "runs": runs}
    write_json(folder / "plan.json", plan)
    # This detects accidental edits, not deliberate tampering. Archive externally when needed.
    (folder / "plan.sha256").write_text(digest((folder / "plan.json").read_bytes()), encoding="ascii")
    return {"planned_responses": len(runs), "executed_model_calls": 0}


def load_plan(folder):
    if digest((folder / "plan.json").read_bytes()) != (folder / "plan.sha256").read_text(encoding="ascii"):
        raise ValueError("Plan changed after preparation")
    plan = read_json(folder / "plan.json")
    if digest((folder / "criteria.json").read_bytes()) != plan["criteria_sha256"]:
        raise ValueError("Criteria changed after preparation")
    for run in plan["runs"]:
        directory = folder / run["slot"]
        if digest((directory / "request.txt").read_bytes()) != run["request_sha256"]:
            raise ValueError(f"Request changed: {run['slot']}")
        if digest((directory / "context.json").read_bytes()) != run["context_sha256"]:
            raise ValueError(f"Context changed: {run['slot']}")
    return plan


def reviews(folder):
    path = folder / "reviews.jsonl"
    return [strict_json(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()] if path.exists() else []


def check_review(folder, plan, row):
    fields = {"slot", "outcome", "note", "response_sha256", "environment"}
    if not isinstance(row, dict) or set(row) != fields:
        raise ValueError("Invalid review fields")
    known = {run["slot"] for run in plan["runs"]}
    if not isinstance(row["slot"], str) or row["slot"] not in known:
        raise ValueError("Unknown review slot")
    if row["outcome"] not in ("pass", "fail", "error"):
        raise ValueError("Invalid review outcome")
    if not isinstance(row["note"], str) or not row["note"].strip():
        raise ValueError("A review needs an evidence or failure note")
    if row["environment"] != plan["environment"]:
        raise ValueError("Environment mismatch; create a separate experiment")
    response = folder / row["slot"] / "response.txt"
    if response.exists():
        if digest(response.read_bytes()) != row["response_sha256"]:
            raise ValueError("Response changed after review")
        if row["outcome"] == "pass":
            context = read_json(response.parent / "context.json")
            if not check_response(context, response.read_text(encoding="utf-8-sig"))["mechanical_ok"]:
                raise ValueError("Mechanical failure cannot be scored pass")
    elif row["outcome"] != "error" or row["response_sha256"] is not None:
        raise ValueError("Missing raw response")


def review(folder, slot, outcome, note):
    plan = load_plan(folder)
    existing = reviews(folder)
    for row in existing:
        check_review(folder, plan, row)
    if any(row["slot"] == slot for row in existing):
        raise ValueError("Slot already reviewed; retain the first review")
    if slot not in {run["slot"] for run in plan["runs"]}:
        raise ValueError("Unknown review slot")
    response = folder / slot / "response.txt"
    row = {"slot": slot, "outcome": outcome, "note": note,
           "response_sha256": digest(response.read_bytes()) if response.exists() else None,
           "environment": plan["environment"]}
    check_review(folder, plan, row)
    with (folder / "reviews.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def compare(folder):
    plan = load_plan(folder)
    observed = {}
    for row in reviews(folder):
        check_review(folder, plan, row)
        if row["slot"] in observed:
            raise ValueError("Duplicate review slot")
        observed[row["slot"]] = row
    scores = {variant: {key: 0 for key in ("planned", "pass", "fail", "error", "missing")}
              for variant in ("a", "b")}
    pairs = {}
    for run in plan["runs"]:
        outcome = observed.get(run["slot"], {}).get("outcome", "missing")
        scores[run["variant"]]["planned"] += 1
        scores[run["variant"]][outcome] += 1
        pairs.setdefault((run["case_id"], run["repeat"]), {})[run["variant"]] = outcome
    paired = {"both_pass": 0, "a_only_pass": 0, "b_only_pass": 0,
              "neither_pass": 0, "incomplete": 0}
    for pair in pairs.values():
        if "missing" in pair.values():
            key = "incomplete"
        elif pair["a"] == "pass" and pair["b"] == "pass":
            key = "both_pass"
        elif pair["a"] == "pass":
            key = "a_only_pass"
        elif pair["b"] == "pass":
            key = "b_only_pass"
        else:
            key = "neither_pass"
        paired[key] += 1
    complete = paired["incomplete"] == 0
    return {"kind": "manual_review_accounting", "complete": complete,
            "scores": scores, "pairs": paired,
            "pass_count_delta_b_minus_a": scores["b"]["pass"] - scores["a"]["pass"] if complete else None,
            "note": "统计人工评审记录，不自动判定语义、模型来源或显著性；error 保留在分母内。"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    context = commands.add_parser("context")
    context.add_argument("case_id")
    context.add_argument("--split", choices=("development", "validation", "holdout"), default="development")
    context.add_argument("--mode", choices=("full", "selected", "summary"), default="full")
    context.add_argument("--variant", choices=("a", "b"), default="a")
    context.add_argument("--out", type=Path, required=True)
    check = commands.add_parser("check")
    check.add_argument("context", type=Path)
    check.add_argument("response", type=Path)
    prep = commands.add_parser("prepare")
    prep.add_argument("--split", choices=("validation", "holdout"), default="validation")
    prep.add_argument("--repeats", type=int, default=2)
    prep.add_argument("--environment", required=True)
    prep.add_argument("--out", type=Path, required=True)
    rev = commands.add_parser("review")
    rev.add_argument("experiment", type=Path)
    rev.add_argument("slot")
    rev.add_argument("--outcome", choices=("pass", "fail", "error"), required=True)
    rev.add_argument("--note", required=True)
    comp = commands.add_parser("compare")
    comp.add_argument("experiment", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "context":
            result = bundle(args.split, args.case_id, args.mode, args.variant)
            export_context(args.out, result)
            result = {key: result[key] for key in ("case_id", "mode", "characters", "utf8_bytes", "omitted_sources")}
        elif args.command == "check":
            result = check_response(read_json(args.context), args.response.read_text(encoding="utf-8-sig"))
        elif args.command == "prepare":
            result = prepare(args.out, args.split, args.repeats, args.environment)
        elif args.command == "review":
            result = review(args.experiment, args.slot, args.outcome, args.note)
        else:
            result = compare(args.experiment)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if result.get("mechanical_ok") is False else 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(2, f"error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
