from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from writ_decision_lab import check_bytes, solve_bytes
from writ_decision_lab.identity import digest_bytes, output_bytes, source_manifest

from support import changed, encoded, fixture, parsed


class CheckerAdversarialTests(unittest.TestCase):
    def setUp(self) -> None:
        self.model_bytes, self.query_bytes = fixture("F01-weak")
        self.result_bytes = solve_bytes(self.model_bytes, self.query_bytes)

    def assert_not_checked(self, result: bytes, expected: tuple[str, ...] = ("invalid_input", "computation_mismatch")) -> None:
        report = check_bytes(self.model_bytes, self.query_bytes, result)
        self.assertIn(report.status, expected, report.diagnostics)
        self.assertNotEqual(report.status, "checked")

    def test_each_exposed_answer_field_is_checked(self) -> None:
        def mutate(function) -> bytes:
            value = parsed(self.result_bytes)
            function(value["answer"])
            return encoded(value)

        mutations = {
            "state_order": lambda a: a.__setitem__("state_order", ["s1", "s0"]),
            "outcome_order": lambda a: a.__setitem__("outcome_order", ["x1", "x0"]),
            "action_order": lambda a: a.__setitem__("action_order", ["a1", "a0"]),
            "loss_unit": lambda a: a.__setitem__("loss_unit", "other-unit"),
            "prior_risks": lambda a: a["prior_risks"].__setitem__(0, "1/2"),
            "current_risk": lambda a: a.__setitem__("current_risk", "1/2"),
            "current_argmin": lambda a: a.__setitem__("current_argmin", []),
            "branches": lambda a: a["branches"].reverse(),
            "observed_risk": lambda a: a.__setitem__("observed_risk", "1/4"),
            "evsi": lambda a: a.__setitem__("evsi", "1/4"),
            "net_value": lambda a: a.__setitem__("net_value", "1/4"),
            "acquisition_risks": lambda a: a["acquisition_risks"].__setitem__("observe_once", "1/4"),
            "acquisition_argmin": lambda a: a.__setitem__("acquisition_argmin", ["act_now"]),
        }
        for name, function in mutations.items():
            with self.subTest(field=name):
                self.assert_not_checked(mutate(function))

    def test_each_branch_field_is_checked(self) -> None:
        def mutate(function) -> bytes:
            value = parsed(self.result_bytes)
            function(value["answer"]["branches"][0])
            return encoded(value)

        mutations = {
            "outcome": lambda b: b.__setitem__("outcome", "x1"),
            "status": lambda b: b.__setitem__("status", "impossible"),
            "mass": lambda b: b.__setitem__("mass", "1/1"),
            "posterior": lambda b: b["posterior"].__setitem__(0, "5/7"),
            "risks": lambda b: b["risks"].__setitem__(0, "2/7"),
            "minimum_risk": lambda b: b.__setitem__("minimum_risk", "2/7"),
            "argmin": lambda b: b.__setitem__("argmin", ["a1"]),
        }
        for name, function in mutations.items():
            with self.subTest(field=name):
                self.assert_not_checked(mutate(function))

    def test_omitted_tie_minimizer_and_impossible_null_mutation_fail(self) -> None:
        tie_model, tie_query = fixture("F07-real-tie")
        tie_result = parsed(solve_bytes(tie_model, tie_query))
        tie_result["answer"]["branches"][0]["argmin"] = ["a0"]
        self.assertEqual(check_bytes(tie_model, tie_query, encoded(tie_result)).status, "computation_mismatch")
        impossible_model, impossible_query = fixture("F03-no-signal-unit")
        impossible = parsed(solve_bytes(impossible_model, impossible_query))
        impossible["answer"]["branches"][1]["posterior"] = []
        self.assertEqual(check_bytes(impossible_model, impossible_query, encoded(impossible)).status, "invalid_input")

    def test_joint_identities_detect_posterior_and_risk_tampering(self) -> None:
        posterior = parsed(self.result_bytes)
        posterior["answer"]["branches"][0]["posterior"] = ["5/7", "2/7"]
        report = check_bytes(self.model_bytes, self.query_bytes, encoded(posterior))
        self.assertEqual(report.status, "computation_mismatch")
        self.assertIn("E_POSTERIOR_IDENTITY", {item.code for item in report.diagnostics})
        risk = parsed(self.result_bytes)
        risk["answer"]["branches"][0]["risks"][0] = "2/7"
        report = check_bytes(self.model_bytes, self.query_bytes, encoded(risk))
        self.assertEqual(report.status, "computation_mismatch")
        self.assertIn("E_RISK_IDENTITY", {item.code for item in report.diagnostics})

    def test_changed_intended_inputs_and_whitespace_refuse_old_result(self) -> None:
        perfect_model, _ = fixture("F02-perfect")
        cost_query = changed(self.query_bytes, lambda query: query.__setitem__("cost", "1/8"))
        loss_query = changed(self.query_bytes, lambda query: query["losses"][0].__setitem__(1, "2/1"))
        action_query = changed(self.query_bytes, lambda query: (query.__setitem__("actions", ["a0"]), query.__setitem__("losses", [query["losses"][0]])))
        cases = [
            (perfect_model, self.query_bytes),
            (self.model_bytes, cost_query),
            (self.model_bytes, loss_query),
            (self.model_bytes, action_query),
            (self.model_bytes + b"\n", self.query_bytes),
            (self.model_bytes, self.query_bytes + b" "),
        ]
        for model_bytes, query_bytes in cases:
            with self.subTest(model=digest_bytes(model_bytes), query=digest_bytes(query_bytes)):
                self.assertEqual(check_bytes(model_bytes, query_bytes, self.result_bytes).status, "input_mismatch")
        self.assertEqual(check_bytes(self.model_bytes, self.query_bytes, self.result_bytes).status, "checked")

    def test_rebinding_old_answer_does_not_bypass_mathematical_check(self) -> None:
        changes = []
        perfect_model, _ = fixture("F02-perfect")
        changes.append((perfect_model, self.query_bytes))
        cost_query = changed(self.query_bytes, lambda query: query.__setitem__("cost", "1/8"))
        changes.append((self.model_bytes, cost_query))
        loss_query = changed(self.query_bytes, lambda query: query["losses"][0].__setitem__(1, "2/1"))
        changes.append((self.model_bytes, loss_query))
        action_query = changed(self.query_bytes, lambda query: (query.__setitem__("actions", ["a0"]), query.__setitem__("losses", [query["losses"][0]])))
        changes.append((self.model_bytes, action_query))
        for model_bytes, query_bytes in changes:
            with self.subTest(query=digest_bytes(query_bytes)):
                rebound = parsed(self.result_bytes)
                rebound["input_bindings"] = {
                    "model_sha256": digest_bytes(model_bytes),
                    "query_sha256": digest_bytes(query_bytes),
                }
                self.assertEqual(check_bytes(model_bytes, query_bytes, encoded(rebound)).status, "computation_mismatch")

    def test_same_hash_tampered_evsi_is_detected(self) -> None:
        tampered = changed(self.result_bytes, lambda result: result["answer"].__setitem__("evsi", "1/4"))
        report = check_bytes(self.model_bytes, self.query_bytes, tampered)
        self.assertEqual(report.status, "computation_mismatch")
        self.assertEqual(report.policy_count, 4)

    def test_checker_source_is_separate_from_producer_math(self) -> None:
        checker_source = (Path(__file__).resolve().parents[1] / "src" / "writ_decision_lab" / "checker.py").read_text()
        self.assertNotIn("from .solver", checker_source)
        self.assertNotIn("import solver", checker_source)

    def test_source_manifest_uses_relative_forward_slash_paths(self) -> None:
        entries = source_manifest()
        self.assertTrue(entries)
        for entry in entries:
            self.assertFalse(entry["path"].startswith("/"))
            self.assertNotIn("\\", entry["path"])

    def test_runtime_sources_have_no_network_client_imports(self) -> None:
        package = Path(__file__).resolve().parents[1] / "src" / "writ_decision_lab"
        forbidden = ("import socket", "import urllib", "import http.client", "import requests")
        for source in package.glob("*.py"):
            text = source.read_text()
            with self.subTest(source=source.name):
                self.assertFalse(any(item in text for item in forbidden))
                self.assertNotIn("assert ", text)


if __name__ == "__main__":
    unittest.main()
