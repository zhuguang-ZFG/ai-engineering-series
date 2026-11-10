"""Offline business and subprocess contracts, without a model account."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest

import check_inventory
import inventory_fixed

ROOT = Path(__file__).resolve().parent
PLUGIN = ROOT / "review-plugin"


class WorkshopTests(unittest.TestCase):
    def test_faults_are_reproducible_and_reference_passes(self):
        bad = check_inventory.check()
        self.assertEqual({r["case"] for r in bad["cases"] if not r["passed"]},
                         {"reserve_all", "negative_quantity", "zero_quantity",
                          "boolean_quantity", "fractional_quantity"})
        fixed = check_inventory.check(True)
        self.assertEqual(fixed["passed"], fixed["total"])

    def test_integer_inputs_conserve_stock(self):
        for stock in range(1, 25):
            for quantity in range(1, stock + 1):
                self.assertEqual(inventory_fixed.reserve(stock, quantity) + quantity, stock)

    def test_hook_blocks_writes_but_leaves_read_and_other_events(self):
        for event, tool, blocked in (("PreToolUse", "Edit", True),
                                     ("PreToolUse", "Write", True),
                                     ("PreToolUse", "Bash", True),
                                     ("PreToolUse", "Read", False),
                                     ("PostToolUse", "Edit", False)):
            with self.subTest(event=event, tool=tool):
                proc = subprocess.run([sys.executable, str(PLUGIN / "hooks/review_only.py")],
                                      input=json.dumps({"hook_event_name": event, "tool_name": tool}),
                                      text=True, capture_output=True, check=True, timeout=10)
                result = json.loads(proc.stdout)
                self.assertEqual(result.get("hookSpecificOutput", {}).get("permissionDecision")
                                 == "deny", blocked)

    def test_hook_invalid_input_is_an_error_not_a_deny(self):
        proc = subprocess.run([sys.executable, str(PLUGIN / "hooks/review_only.py")],
                              input="not json", text=True, capture_output=True, timeout=10)
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(proc.stdout, "")

    def test_mcp_stdio_roundtrip(self):
        requests = [
            {"id": 1, "method": "initialize", "params": {"protocolVersion": "2025-03-26"}},
            {"method": "notifications/initialized"},
            {"id": 2, "method": "tools/list"},
            {"id": 3, "method": "tools/call", "params": {
                "name": "get_rule", "arguments": {"rule": "boundary"}}},
            {"id": 4, "method": "tools/call", "params": {
                "name": "get_rule", "arguments": {"rule": "missing"}}},
            {"id": 5, "method": "unknown"},
        ]
        proc = subprocess.run([sys.executable, str(PLUGIN / "rules_server.py")],
                              input="".join(json.dumps({"jsonrpc": "2.0", **r}) + "\n"
                                            for r in requests), text=True, capture_output=True,
                              check=True, timeout=10)
        output = [json.loads(line) for line in proc.stdout.splitlines()]
        self.assertEqual([r["id"] for r in output], [1, 2, 3, 4, 5])
        self.assertEqual(output[0]["result"]["protocolVersion"], "2025-03-26")
        self.assertEqual(output[1]["result"]["tools"][0]["name"], "get_rule")
        self.assertIn("zero", output[2]["result"]["content"][0]["text"])
        self.assertFalse(output[2]["result"]["isError"])
        self.assertTrue(output[3]["result"]["isError"])
        self.assertEqual(output[4]["error"]["code"], -32601)


if __name__ == "__main__":
    unittest.main()
