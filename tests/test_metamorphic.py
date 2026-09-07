from __future__ import annotations

from fractions import Fraction
import json
import unittest

from writ_decision_lab import check_bytes, solve_bytes

from support import encoded, fixture, parsed


def rat(value: str) -> Fraction:
    numerator, denominator = value.split("/")
    return Fraction(int(numerator), int(denominator))


def wire(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


class MetamorphicTests(unittest.TestCase):
    def setUp(self) -> None:
        self.model_bytes, self.query_bytes = fixture("F01-weak")
        self.old_result = solve_bytes(self.model_bytes, self.query_bytes)
        self.old_answer = json.loads(self.old_result)["answer"]

    def fresh(self, model: dict, query: dict) -> tuple[bytes, bytes, dict]:
        model_bytes, query_bytes = encoded(model), encoded(query)
        result = solve_bytes(model_bytes, query_bytes)
        self.assertEqual(check_bytes(model_bytes, query_bytes, result).status, "checked")
        self.assertEqual(check_bytes(model_bytes, query_bytes, self.old_result).status, "input_mismatch")
        return model_bytes, query_bytes, json.loads(result)["answer"]

    def test_simultaneous_state_permutation_preserves_relabelled_answer(self) -> None:
        model, query = parsed(self.model_bytes), parsed(self.query_bytes)
        model["states"].reverse()
        model["prior"].reverse()
        model["likelihood"].reverse()
        query["state_order"].reverse()
        for row in query["losses"]:
            row.reverse()
        _, _, answer = self.fresh(model, query)
        for key in ("prior_risks", "current_risk", "current_argmin", "observed_risk", "evsi", "net_value", "acquisition_risks", "acquisition_argmin"):
            self.assertEqual(answer[key], self.old_answer[key])
        self.assertEqual(answer["state_order"], ["s1", "s0"])
        for new, old in zip(answer["branches"], self.old_answer["branches"]):
            self.assertEqual(new["posterior"], list(reversed(old["posterior"])))
            self.assertEqual(new["risks"], old["risks"])

    def test_action_permutation_preserves_values_and_labels(self) -> None:
        model, query = parsed(self.model_bytes), parsed(self.query_bytes)
        query["actions"].reverse()
        query["losses"].reverse()
        _, _, answer = self.fresh(model, query)
        self.assertEqual(answer["action_order"], ["a1", "a0"])
        self.assertEqual(answer["prior_risks"], list(reversed(self.old_answer["prior_risks"])))
        self.assertEqual(answer["current_argmin"], self.old_answer["current_argmin"])
        self.assertEqual(answer["evsi"], self.old_answer["evsi"])
        for new, old in zip(answer["branches"], self.old_answer["branches"]):
            self.assertEqual(new["risks"], list(reversed(old["risks"])))
            self.assertEqual(new["argmin"], old["argmin"])

    def test_outcome_permutation_preserves_relabelled_branches(self) -> None:
        model, query = parsed(self.model_bytes), parsed(self.query_bytes)
        model["outcomes"].reverse()
        for row in model["likelihood"]:
            row.reverse()
        _, _, answer = self.fresh(model, query)
        self.assertEqual(answer["outcome_order"], ["x1", "x0"])
        self.assertEqual(answer["branches"], list(reversed(self.old_answer["branches"])))
        for key in ("current_risk", "observed_risk", "evsi", "net_value", "acquisition_risks", "acquisition_argmin"):
            self.assertEqual(answer[key], self.old_answer[key])

    def test_positive_scale_factor_scales_losses_cost_and_values(self) -> None:
        # Positive scaling preserves all minimizers and multiplies every risk/value by the factor.
        model, query = parsed(self.model_bytes), parsed(self.query_bytes)
        factor = Fraction(3)
        query["losses"] = [[wire(rat(value) * factor) for value in row] for row in query["losses"]]
        query["cost"] = wire(rat(query["cost"]) * factor)
        _, _, answer = self.fresh(model, query)
        self.assertEqual(answer["current_argmin"], self.old_answer["current_argmin"])
        self.assertEqual(answer["acquisition_argmin"], self.old_answer["acquisition_argmin"])
        for key in ("current_risk", "observed_risk", "evsi", "net_value"):
            self.assertEqual(rat(answer[key]), factor * rat(self.old_answer[key]))

    def test_constant_loss_translation_preserves_values_of_information(self) -> None:
        # Adding one constant to every loss shifts risks but cancels in EVSI and net value.
        model, query = parsed(self.model_bytes), parsed(self.query_bytes)
        constant = Fraction(2)
        query["losses"] = [[wire(rat(value) + constant) for value in row] for row in query["losses"]]
        _, _, answer = self.fresh(model, query)
        self.assertEqual(answer["current_argmin"], self.old_answer["current_argmin"])
        self.assertEqual(answer["acquisition_argmin"], self.old_answer["acquisition_argmin"])
        self.assertEqual(answer["evsi"], self.old_answer["evsi"])
        self.assertEqual(answer["net_value"], self.old_answer["net_value"])
        self.assertEqual(rat(answer["current_risk"]), rat(self.old_answer["current_risk"]) + constant)
        self.assertEqual(rat(answer["observed_risk"]), rat(self.old_answer["observed_risk"]) + constant)


if __name__ == "__main__":
    unittest.main()
