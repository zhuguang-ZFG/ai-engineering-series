"""Original prompt-book examples: business boundaries and honest evaluation."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

EXAMPLES = Path(__file__).resolve().parents[1] / "prompt/examples"
sys.path.insert(0, str(EXAMPLES))
import lab
import check_workshop
from workshop import transition
sys.path.remove(str(EXAMPLES))


class BusinessRules(unittest.TestCase):
    def test_reference_meets_frozen_business_cases(self):
        report = check_workshop.run("reference")
        self.assertEqual(report["passed"], report["total"])

    def test_faulty_example_exposes_the_intended_business_failures(self):
        report = check_workshop.run("faulty")
        failed = {item["id"] for item in report["results"] if not item["passed"]}
        self.assertEqual(failed, {"full", "zero", "duplicate-waiting", "cancel-promote"})

    def test_invalid_states_and_requests_leave_inputs_unchanged(self):
        base = dict(capacity=1, confirmed=["Q01"], waiting=[], person="Q02", action="register")
        for patch in ({"confirmed": ["Q01", "Q01"]}, {"waiting": ["Q01"]},
                      {"confirmed": [], "waiting": ["Q02"]}, {"person": False},
                      {"capacity": 1.0}, {"action": "send"}, {"confirmed": "Q01"}):
            request = {**base, **patch}
            before = copy.deepcopy(request)
            self.assertEqual(transition(**request)["status"], "invalid")
            self.assertEqual(request, before)

    def test_successful_transitions_preserve_invariants(self):
        # Exercise sequential register/cancel actions, including repeated requests.
        for capacity in range(4):
            confirmed, waiting = [], []
            for action, person in [("register", f"Q{i}") for i in range(5)] + [
                    ("register", "Q4"), ("cancel", "Q0"), ("cancel", "Q3"),
                    ("cancel", "Q0"), ("register", "Q0")]:
                before = (confirmed.copy(), waiting.copy())
                result = transition(capacity, confirmed, waiting, person, action)
                self.assertEqual((confirmed, waiting), before)
                confirmed, waiting = result["confirmed"], result["waiting"]
                self.assertLessEqual(len(confirmed), capacity)
                self.assertEqual(len(set(confirmed + waiting)), len(confirmed + waiting))
                self.assertTrue(not waiting or len(confirmed) == capacity)


class ContextAndChecks(unittest.TestCase):
    def setUp(self):
        self.context = lab.bundle("development", "D01")
        self.response = {"case_id": "D01", "answer": "活动免费。",
                         "evidence": [{"source": "N01-v1", "quote": "活动免费"}], "actions": []}

    def check(self, response):
        return lab.check_response(self.context, json.dumps(response, ensure_ascii=False))

    def test_splits_have_unique_ids_sources_and_criteria(self):
        seen = set()
        criteria = lab.read_json(lab.ROOT / "evaluation/criteria.json")["cases"]
        for split in ("development", "validation", "holdout"):
            for case in lab.cases(split):
                self.assertNotIn(case["id"], seen)
                seen.add(case["id"])
                self.assertTrue(lab.bundle(split, case["id"])["sources"])
                self.assertTrue(criteria[case["id"]])
        self.assertEqual(seen, set(criteria))

    def test_request_contains_no_evaluation_or_other_split_data(self):
        request = self.context["request"]
        for forbidden in ("criteria", "expected", "H01", "U02-v3", "L01-v1", "S01-v1"):
            self.assertNotIn(forbidden, request)
        self.assertEqual(set(self.context["sources"]), {"N01-v1", "R01-v1"})

    def test_unknown_or_wrong_split_case_rejected(self):
        with self.assertRaises(ValueError):
            lab.bundle("development", "H01")

    def test_selected_context_keeps_revision_and_rules(self):
        context = lab.bundle("development", "D02", "selected")
        self.assertEqual(list(context["sources"]), ["U01-v2", "N01-v1", "R01-v1"])
        self.assertEqual(context["omitted_sources"], ["C01-v1", "A01-v1", "D01-v1"])

    def test_summary_cannot_cite_unprovided_original(self):
        context = lab.bundle("development", "D02", "summary")
        response = {**self.response, "case_id": "D02"}
        checked = lab.check_response(context, json.dumps(response))
        self.assertFalse(checked["mechanical_ok"])
        self.assertIn("evidence: source was not provided", checked["errors"])

    def test_real_quote_with_false_answer_still_requires_human_review(self):
        self.response["answer"] = "活动收费 500 元。"
        result = self.check(self.response)
        self.assertTrue(result["mechanical_ok"])
        self.assertTrue(result["manual_review_required"])

    def test_malformed_json_and_duplicate_keys_fail(self):
        for raw in ('```json\n{}\n```', '{"a": 1, "a": 2}', '{"a": NaN}', '[]'):
            self.assertFalse(lab.check_response(self.context, raw)["mechanical_ok"])

    def test_schema_unprovided_quotes_and_actions_fail(self):
        for patch in ({"case_id": "D02"}, {"answer": []}, {"evidence": []},
                      {"evidence": [{"source": [], "quote": "x"}]},
                      {"evidence": [{"source": "N01-v1", "quote": "收费 500 元"}]},
                      {"actions": ["sent"]}, {"actions": {}}, {"extra": 1}):
            with self.subTest(patch=patch):
                self.assertFalse(self.check({**self.response, **patch})["mechanical_ok"])


class PairedAccounting(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name) / "experiment"
        lab.prepare(self.folder, "validation", 1, "synthetic unit-test fixtures; no model")

    def save_fixture(self, slot):
        context = lab.read_json(self.folder / slot / "context.json")
        source, text = next(iter(context["sources"].items()))
        response = {"case_id": context["case_id"], "answer": "Synthetic unit-test fixture",
                    "evidence": [{"source": source, "quote": text.splitlines()[0]}], "actions": []}
        lab.write_json(self.folder / slot / "response.txt", response)

    def test_preparation_performs_no_calls_and_missing_is_not_zero_delta(self):
        result = lab.compare(self.folder)
        self.assertFalse(result["complete"])
        self.assertIsNone(result["pass_count_delta_b_minus_a"])
        self.assertEqual(result["pairs"]["incomplete"], 7)
        self.assertEqual(result["scores"]["a"]["planned"], 7)

    def test_all_pairs_and_service_errors_stay_in_denominator(self):
        for run in lab.load_plan(self.folder)["runs"]:
            slot = run["slot"]
            if slot == "V01-01-a":
                lab.review(self.folder, slot, "error", "Synthetic timeout")
            else:
                self.save_fixture(slot)
                lab.review(self.folder, slot, "pass", "Synthetic test, not a semantic verdict")
        result = lab.compare(self.folder)
        self.assertTrue(result["complete"])
        self.assertEqual(result["scores"]["a"]["planned"], 7)
        self.assertEqual(result["scores"]["a"]["error"], 1)
        self.assertEqual(result["pairs"]["b_only_pass"], 1)
        self.assertEqual(result["pass_count_delta_b_minus_a"], 1)

    def test_duplicate_review_cannot_inflate_score(self):
        lab.review(self.folder, "V01-01-a", "error", "Synthetic failure")
        with self.assertRaisesRegex(ValueError, "already reviewed"):
            lab.review(self.folder, "V01-01-a", "error", "Again")
        path = self.folder / "reviews.jsonl"
        path.write_bytes(path.read_bytes() * 2)
        with self.assertRaisesRegex(ValueError, "Duplicate review"):
            lab.compare(self.folder)

    def test_missing_response_and_mechanical_failure_cannot_pass(self):
        with self.assertRaisesRegex(ValueError, "Missing raw response"):
            lab.review(self.folder, "V01-01-a", "pass", "Missing")
        (self.folder / "V01-01-a/response.txt").write_text("{}", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Mechanical failure"):
            lab.review(self.folder, "V01-01-a", "pass", "Bad fields")

    def test_changed_raw_output_is_detected(self):
        self.save_fixture("V01-01-a")
        lab.review(self.folder, "V01-01-a", "fail", "Synthetic semantic failure")
        (self.folder / "V01-01-a/response.txt").write_text("{}", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Response changed"):
            lab.compare(self.folder)

    def test_changed_request_criteria_context_and_plan_are_detected(self):
        for name in ("V01-01-a/request.txt", "V01-01-a/context.json", "criteria.json", "plan.json"):
            path = self.folder / name
            original = path.read_bytes()
            path.write_bytes(original + b" ")
            with self.assertRaises(ValueError):
                lab.compare(self.folder)
            path.write_bytes(original)

    def test_unknown_slot_environment_mismatch_and_invalid_outcome_are_rejected(self):
        lab.review(self.folder, "V01-01-a", "error", "Synthetic failure")
        row = lab.reviews(self.folder)[0]
        plan = lab.load_plan(self.folder)
        for patch in ({"slot": "V99-01-a"}, {"environment": "another model"},
                      {"outcome": True}, {"note": " "}):
            with self.assertRaises(ValueError):
                lab.check_review(self.folder, plan, {**row, **patch})

    def test_existing_experiment_cannot_be_overwritten(self):
        with self.assertRaises(FileExistsError):
            lab.prepare(self.folder, "validation", 1, "another experiment")


if __name__ == "__main__":
    unittest.main()
