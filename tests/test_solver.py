from __future__ import annotations

from fractions import Fraction
import json
import unittest

from writ_decision_lab import check_bytes, solve_bytes

from support import encoded, fixture


class SolverFixtureTests(unittest.TestCase):
    def answer(self, identifier: str) -> dict:
        model, query = fixture(identifier)
        result = solve_bytes(model, query)
        report = check_bytes(model, query, result)
        self.assertEqual(report.status, "checked", report.diagnostics)
        return json.loads(result)["answer"]

    def test_all_required_and_development_fixtures_check(self) -> None:
        identifiers = [
            "F01-weak", "F02-perfect", "F03-no-signal-unit", "F04-no-signal-asymmetric",
            "F05-revised-unit", "F06-revised-asymmetric", "F07-real-tie", "F08-zero-prior",
            "F09-exactness", "F10-acquisition-tie", "F11-three-state", "F12-restricted-actions",
            "D01-minimum", "D02-negative-loss", "D03-cost-over-evsi", "D04-policy-limit",
        ]
        counts = []
        for identifier in identifiers:
            with self.subTest(identifier=identifier):
                model, query = fixture(identifier)
                report = check_bytes(model, query, solve_bytes(model, query))
                self.assertEqual(report.status, "checked", report.diagnostics)
                answer = json.loads(solve_bytes(model, query))["answer"]
                self.assertGreaterEqual(Fraction(answer["evsi"]), 0)
                counts.append(report.policy_count)
        self.assertEqual(sum(counts[:12]), 68)
        self.assertEqual(counts[-1], 4096)

    def test_f01_full_expected_answer(self) -> None:
        answer = self.answer("F01-weak")
        self.assertEqual(answer["prior_risks"], ["1/4", "3/4"])
        self.assertEqual(answer["current_risk"], "1/4")
        self.assertEqual(answer["current_argmin"], ["a0"])
        self.assertEqual(answer["branches"][0], {
            "outcome": "x0", "status": "possible", "mass": "7/8",
            "posterior": ["6/7", "1/7"], "risks": ["1/7", "6/7"],
            "minimum_risk": "1/7", "argmin": ["a0"],
        })
        self.assertEqual(answer["branches"][1], {
            "outcome": "x1", "status": "possible", "mass": "1/8",
            "posterior": ["0/1", "1/1"], "risks": ["1/1", "0/1"],
            "minimum_risk": "0/1", "argmin": ["a1"],
        })
        self.assertEqual(answer["observed_risk"], "1/8")
        self.assertEqual(answer["evsi"], "1/8")
        self.assertEqual(answer["net_value"], "1/8")
        self.assertEqual(answer["acquisition_risks"], {"act_now": "1/4", "observe_once": "1/8"})
        self.assertEqual(answer["acquisition_argmin"], ["observe_once"])

    def test_named_packet_expectations(self) -> None:
        weak, perfect = self.answer("F01-weak"), self.answer("F02-perfect")
        self.assertEqual(perfect["evsi"], "1/4")
        self.assertEqual(weak["current_argmin"], perfect["current_argmin"])
        self.assertEqual([branch["argmin"] for branch in weak["branches"]], [branch["argmin"] for branch in perfect["branches"]])
        no_signal, asymmetric = self.answer("F03-no-signal-unit"), self.answer("F04-no-signal-asymmetric")
        self.assertEqual(no_signal["branches"][1]["status"], "impossible")
        self.assertEqual(no_signal["current_argmin"], asymmetric["current_argmin"])
        self.assertEqual(no_signal["evsi"], asymmetric["evsi"])
        self.assertEqual(self.answer("F05-revised-unit")["prior_risks"], ["1/1", "3/4"])
        self.assertEqual(self.answer("F05-revised-unit")["current_argmin"], ["a1"])
        self.assertEqual(self.answer("F06-revised-asymmetric")["prior_risks"], ["1/1", "3/2"])
        self.assertEqual(self.answer("F06-revised-asymmetric")["current_argmin"], ["a0"])
        tied = self.answer("F07-real-tie")
        self.assertTrue(all(branch["argmin"] == ["a0", "a1"] for branch in tied["branches"]))
        self.assertIsNone(self.answer("F08-zero-prior")["branches"][1]["argmin"])
        self.assertEqual(self.answer("F10-acquisition-tie")["acquisition_argmin"], ["act_now", "observe_once"])
        exactness = self.answer("F09-exactness")
        self.assertEqual(Fraction(exactness["prior_risks"][1]) - Fraction(exactness["prior_risks"][0]), Fraction(1, 1000000000000000001))
        three_state = self.answer("F11-three-state")
        self.assertEqual((three_state["current_risk"], three_state["current_argmin"], three_state["observed_risk"], three_state["evsi"]), ("5/6", ["a1"], "0/1", "5/6"))
        self.assertEqual(self.answer("F12-restricted-actions")["evsi"], "0/1")
        minimum = self.answer("D01-minimum")
        self.assertEqual((minimum["current_risk"], minimum["observed_risk"], minimum["evsi"]), ("5/3", "5/3", "0/1"))
        self.assertEqual(self.answer("D02-negative-loss")["current_risk"], "-1/1")
        self.assertEqual(self.answer("D03-cost-over-evsi")["net_value"], "-1/8")

    def test_large_intermediate_rational_exceeds_input_digit_cap(self) -> None:
        # Two legal 31-digit input denominators multiply into a valid computed denominator >32 digits.
        p_den = 1000000000000000000000000000003
        loss_den = 1000000000000000000000000000039
        model = {
            "schema": "wdl.model.v1", "states": ["s0", "s1"], "outcomes": ["x0"],
            "prior": [f"1/{p_den}", f"{p_den - 1}/{p_den}"],
            "likelihood": [["1/1"], ["1/1"]],
        }
        query = {
            "schema": "wdl.query.v1", "semantics": "finite-one-observation.v1",
            "state_order": ["s0", "s1"], "actions": ["a0"],
            "losses": [["0/1", f"1/{loss_den}"]], "loss_unit": "loss-unit", "cost": "0/1",
        }
        model_bytes, query_bytes = encoded(model), encoded(query)
        result = solve_bytes(model_bytes, query_bytes)
        answer = json.loads(result)["answer"]
        denominator = answer["current_risk"].split("/")[1]
        self.assertGreater(len(denominator), 32)
        self.assertEqual(check_bytes(model_bytes, query_bytes, result).status, "checked")


if __name__ == "__main__":
    unittest.main()
