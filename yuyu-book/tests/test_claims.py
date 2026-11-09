"""Claim Ledger: one shared claim_id, two separately anchored editions.

The ledger's job is to make a one-sided prose edit fail. These tests pin the
schema rules, the locator checks and the two severities of expiry; the shipped
ledger is then validated against the real manuscript.
"""
import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from yuyu_book import claims, registry  # noqa: E402
from yuyu_book.core import BuildError  # noqa: E402

TODAY = date(2026, 11, 6)
SOURCES = {"src": {"title": "source"}}
TEXTS = {
    "zh": {
        "ch01": "<!-- block: ch01.anchor -->\n工具共 55 个，默认 Manual。\n",
        "ch02": "<!-- block: ch02.anchor -->\n工具共 55 个，默认 Manual。\n",
    },
    "en": {
        "ch01": ("<!-- block: ch01.anchor -->\n"
                 "The tool count is 55, default Manual.\n"),
        "ch02": ("<!-- block: ch02.anchor -->\n"
                 "The tool count is 55, default Manual.\n"),
    },
}


def make(cid="tool-count", **over):
    entry = {
        "id": cid,
        "kind": "count",
        "risk": "high",
        "value": "55",
        "applies_to": "0.3.x",
        "source": "src",
        "verified": "2026-11-02",
        "review_days": 90,
        "status": "active",
        "zh": {"unit": "ch01", "block": "ch01.anchor",
               "quote": "工具共 55 个"},
        "en": {"unit": "ch01", "block": "ch01.anchor",
               "quote": "tool count is 55"},
    }
    entry.update(over)
    return entry


def ledger(*entries):
    return {"claims": list(entries)}


def run(*entries, **kwargs):
    kwargs.setdefault("today", TODAY)
    return claims.validate(ledger(*entries), TEXTS, SOURCES, **kwargs)


class Shape(unittest.TestCase):
    def test_a_healthy_claim_passes(self):
        self.assertEqual(run(make()), [])

    def test_claim_ids_are_lowercase_slugs_and_unique(self):
        with self.assertRaises(BuildError) as raised:
            run(make("Tool_Count"))
        self.assertIn("lowercase slug", str(raised.exception))
        with self.assertRaises(BuildError) as raised:
            run(make(), make())
        self.assertIn("duplicate claim id", str(raised.exception))

    def test_kind_risk_and_status_are_closed_sets(self):
        for field, bad in (("kind", "rumour"), ("risk", "medium"),
                           ("status", "draft")):
            with self.assertRaises(BuildError) as raised:
                run(make(**{field: bad}))
            self.assertIn(f"{field} must be one of", str(raised.exception))

    def test_source_must_exist(self):
        with self.assertRaises(BuildError) as raised:
            run(make(source="nope"))
        self.assertIn("unknown source", str(raised.exception))

    def test_verified_and_review_days_are_machine_readable(self):
        with self.assertRaises(BuildError) as raised:
            run(make(verified="last week"))
        self.assertIn("ISO date", str(raised.exception))
        with self.assertRaises(BuildError) as raised:
            run(make(review_days=0))
        self.assertIn("positive integer", str(raised.exception))


class Locators(unittest.TestCase):
    def test_a_missing_block_is_named(self):
        entry = make()
        entry["zh"]["block"] = "ch01.missing"
        with self.assertRaises(BuildError) as raised:
            run(entry)
        self.assertIn("no block 'ch01.missing'", str(raised.exception))

    def test_a_quote_that_left_its_block_is_refused(self):
        entry = make()
        entry["zh"]["quote"] = "工具共 54 个"
        with self.assertRaises(BuildError) as raised:
            run(entry)
        self.assertIn("quote not found", str(raised.exception))

    def test_one_edition_updated_without_the_other(self):
        entry = make(value="56")
        entry["zh"]["quote"] = "工具共 56 个"
        with self.assertRaises(BuildError) as raised:
            run(entry)
        self.assertIn("en: value '56' is absent from the quote",
                      str(raised.exception))

    def test_both_editions_must_anchor_the_same_unit(self):
        entry = make()
        entry["en"]["unit"] = "ch02"
        entry["en"]["block"] = "ch02.anchor"
        with self.assertRaises(BuildError) as raised:
            run(entry)
        self.assertIn("different units", str(raised.exception))

    def test_a_retired_claim_no_longer_chases_the_prose(self):
        entry = make(status="retired")
        entry["zh"]["block"] = "ch01.gone"
        entry["en"]["block"] = "ch01.gone"
        self.assertEqual(run(entry), [])


class Expiry(unittest.TestCase):
    def stale(self, **over):
        return make(verified="2020-01-01", review_days=30, **over)

    def test_ci_warns_where_release_blocks(self):
        warnings = run(self.stale(), release=False)
        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0].code, "claim-expired")
        self.assertEqual(warnings[0].severity, "warning")
        with self.assertRaises(BuildError) as raised:
            run(self.stale(), release=True)
        self.assertIn("review was due", str(raised.exception))

    def test_a_normal_risk_claim_never_blocks_a_release(self):
        warnings = run(self.stale(risk="normal"), release=True)
        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0].code, "claim-stale")
        self.assertEqual(warnings[0].severity, "warning")

    def test_a_retired_claim_does_not_expire(self):
        self.assertEqual(run(make(verified="2020-01-01", review_days=30,
                                  status="retired"), release=True), [])

    def test_review_deadline_outside_date_range_is_a_named_input_error(self):
        for verified, days in (("9999-12-31", 1), ("2026-11-02", 10**30)):
            with self.subTest(verified=verified, review_days=days):
                with self.assertRaises(BuildError) as raised:
                    run(make(verified=verified, review_days=days), release=True)
                self.assertIn("claim-review", str(raised.exception))
                self.assertIn("tool-count", str(raised.exception))
                self.assertIn("date range", str(raised.exception))


class ShippedLedger(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = registry.load("manifest.json")
        cls.ledger = claims.load()
        cls.sources = registry.load("sources.json")
        cls.texts = claims.manuscript_texts(cls.manifest)

    def test_the_ledger_is_a_registry(self):
        self.assertIn("claims.json", registry.FILES)
        self.assertIsInstance(self.ledger["claims"], list)

    def test_every_kind_the_spec_names_is_represented(self):
        kinds = {entry["kind"] for entry in self.ledger["claims"]}
        self.assertEqual(kinds, set(claims.KINDS))

    def test_the_shipped_claims_stand_in_the_manuscript(self):
        self.assertEqual(
            claims.validate(self.ledger, self.texts, self.sources,
                            today=TODAY), [])

    def test_every_active_claim_pairs_both_editions(self):
        for entry in self.ledger["claims"]:
            if entry["status"] != "active":
                continue
            self.assertEqual(entry["zh"]["unit"], entry["en"]["unit"],
                             entry["id"])
            self.assertTrue(entry["zh"]["quote"].strip(), entry["id"])
            self.assertTrue(entry["en"]["quote"].strip(), entry["id"])


if __name__ == "__main__":
    unittest.main()
