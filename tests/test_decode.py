from __future__ import annotations

import json
from unittest import mock
import unittest

from writ_decision_lab.decode import decode_inputs, decode_json, decode_model, decode_query, decode_result, parse_rational
from writ_decision_lab.errors import WdlError
from writ_decision_lab.solver import solve_bytes

from support import changed, encoded, fixture, parsed


class StrictDecodeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.model_bytes, self.query_bytes = fixture("F01-weak")

    def assert_rejected(self, function, status: str, code: str | None = None) -> WdlError:
        with self.assertRaises(WdlError) as caught:
            function()
        self.assertEqual(caught.exception.status, status)
        if code is not None:
            self.assertEqual(caught.exception.diagnostic.code, code)
        return caught.exception

    def test_accepts_complete_exact_inputs(self) -> None:
        model, query = decode_inputs(self.model_bytes, self.query_bytes)
        self.assertEqual(model.states, ("s0", "s1"))
        self.assertEqual(str(query.cost), "0")

    def test_rejects_nine_archival_malformed_rationals(self) -> None:
        bad_values = [0.25, "0.25", "2/4", "1/0", "-0/1", "1/-2", "1e-3", " 1/2 ", True]
        for value in bad_values:
            with self.subTest(value=value):
                query_bytes = changed(self.query_bytes, lambda query, value=value: query.__setitem__("cost", value))
                self.assert_rejected(lambda: decode_inputs(self.model_bytes, query_bytes), "invalid_input")

    def test_rejects_other_nonstring_rational_literals(self) -> None:
        for value in (1, None, False):
            with self.subTest(value=value):
                query_bytes = changed(self.query_bytes, lambda query, value=value: query.__setitem__("cost", value))
                self.assert_rejected(lambda: decode_inputs(self.model_bytes, query_bytes), "invalid_input", "E_RATIONAL")

    def test_rejects_duplicate_keys(self) -> None:
        duplicate = b'{"schema":"wdl.model.v1","schema":"wdl.model.v1","states":["s0"],"outcomes":["x0"],"prior":["1/1"],"likelihood":[["1/1"]]}\n'
        self.assert_rejected(lambda: decode_model(duplicate), "invalid_input", "E_JSON_DUPLICATE_KEY")

    def test_rejects_wrong_dimensions(self) -> None:
        bad_model = changed(self.model_bytes, lambda model: model["prior"].pop())
        self.assert_rejected(lambda: decode_model(bad_model), "invalid_input", "E_DIMENSION")
        bad_query = changed(self.query_bytes, lambda query: query["losses"][0].pop())
        model = decode_model(self.model_bytes)
        self.assert_rejected(lambda: decode_query(bad_query, model), "invalid_input", "E_DIMENSION")

    def test_rejects_missing_cost(self) -> None:
        bad = changed(self.query_bytes, lambda query: query.pop("cost"))
        self.assert_rejected(lambda: decode_inputs(self.model_bytes, bad), "invalid_input", "E_REQUIRED_FIELD")

    def test_rejects_duplicate_labels_and_mismatched_state_order(self) -> None:
        duplicate = changed(self.model_bytes, lambda model: model.__setitem__("states", ["s0", "s0"]))
        self.assert_rejected(lambda: decode_model(duplicate), "invalid_input", "E_DUPLICATE_LABEL")
        mismatch = changed(self.query_bytes, lambda query: query.__setitem__("state_order", ["s1", "s0"]))
        self.assert_rejected(lambda: decode_inputs(self.model_bytes, mismatch), "invalid_input", "E_STATE_ORDER")

    def test_rejects_non_normalized_and_negative_probabilities(self) -> None:
        bad_prior = changed(self.model_bytes, lambda model: model.__setitem__("prior", ["1/2", "1/4"]))
        self.assert_rejected(lambda: decode_model(bad_prior), "invalid_input", "E_PRIOR")
        bad_row = changed(self.model_bytes, lambda model: model["likelihood"].__setitem__(0, ["1/2", "1/4"]))
        self.assert_rejected(lambda: decode_model(bad_row), "invalid_input", "E_LIKELIHOOD")
        negative = changed(self.model_bytes, lambda model: model.__setitem__("prior", ["5/4", "-1/4"]))
        self.assert_rejected(lambda: decode_model(negative), "invalid_input", "E_PRIOR")
        negative_cost = changed(self.query_bytes, lambda query: query.__setitem__("cost", "-1/1"))
        self.assert_rejected(lambda: decode_inputs(self.model_bytes, negative_cost), "invalid_input", "E_COST")

    def test_rejects_invalid_unicode_nan_bom_and_trailing_data(self) -> None:
        surrogate = self.model_bytes.replace(b'"s0"', b'"\\ud800"', 1)
        self.assert_rejected(lambda: decode_model(surrogate), "invalid_input", "E_UNICODE_SCALAR")
        nan_value = parsed(self.query_bytes)
        nan_value["cost"] = float("nan")
        nan = encoded(nan_value)
        self.assert_rejected(lambda: decode_inputs(self.model_bytes, nan), "invalid_input", "E_JSON_CONSTANT")
        self.assert_rejected(lambda: decode_model(b"\xef\xbb\xbf" + self.model_bytes), "invalid_input", "E_UTF8_BOM")
        self.assert_rejected(lambda: decode_model(self.model_bytes + b"{}"), "invalid_input", "E_JSON")

    def test_rejects_unknown_input_and_result_fields(self) -> None:
        bad_model = changed(self.model_bytes, lambda model: model.__setitem__("constraint", "ignored"))
        self.assert_rejected(lambda: decode_model(bad_model), "invalid_input", "E_UNKNOWN_FIELD")
        result_bytes = solve_bytes(self.model_bytes, self.query_bytes)
        bad_result = changed(result_bytes, lambda result: result["answer"].__setitem__("verified", True))
        self.assert_rejected(lambda: decode_result(bad_result), "invalid_input", "E_UNKNOWN_FIELD")

    def test_unsupported_versions_are_out_of_scope(self) -> None:
        bad_model = changed(self.model_bytes, lambda model: model.__setitem__("schema", "wdl.model.v2"))
        self.assert_rejected(lambda: decode_model(bad_model), "out_of_scope", "E_MODEL_SCHEMA")
        bad_query = changed(self.query_bytes, lambda query: query.__setitem__("semantics", "finite-two-observation.v1"))
        self.assert_rejected(lambda: decode_inputs(self.model_bytes, bad_query), "out_of_scope", "E_SEMANTICS")

    def test_declared_resource_limits_are_out_of_scope(self) -> None:
        too_many_states = {
            "schema": "wdl.model.v1",
            "states": [f"s{i}" for i in range(9)],
            "outcomes": ["x0"],
            "prior": ["1/9"] * 9,
            "likelihood": [["1/1"]] * 9,
        }
        self.assert_rejected(lambda: decode_model(encoded(too_many_states)), "out_of_scope", "E_DIMENSION_LIMIT")
        too_many_outcomes = parsed(self.model_bytes)
        too_many_outcomes["outcomes"] = [f"x{i}" for i in range(7)]
        too_many_outcomes["likelihood"] = [["1/7"] * 7, ["1/7"] * 7]
        self.assert_rejected(lambda: decode_model(encoded(too_many_outcomes)), "out_of_scope", "E_DIMENSION_LIMIT")
        model = parsed(self.model_bytes)
        model["outcomes"] = [f"x{i}" for i in range(5)]
        model["likelihood"] = [["1/5"] * 5, ["1/5"] * 5]
        query = parsed(self.query_bytes)
        query["actions"] = [f"a{i}" for i in range(6)]
        query["losses"] = [["0/1", "0/1"]] * 6
        self.assert_rejected(lambda: decode_inputs(encoded(model), encoded(query)), "out_of_scope", "E_POLICY_LIMIT")
        self.assert_rejected(lambda: decode_model(b" " * (1024 * 1024 + 1)), "out_of_scope", "E_BYTE_LIMIT")
        self.assert_rejected(lambda: decode_result(b" " * (4 * 1024 * 1024 + 1)), "out_of_scope", "E_BYTE_LIMIT")
        nested: object = None
        for _ in range(33):
            nested = [nested]
        self.assert_rejected(lambda: decode_json(encoded(nested), kind="model"), "out_of_scope", "E_JSON_DEPTH")
        over_digits = changed(self.query_bytes, lambda query: query.__setitem__("cost", "1/" + "9" * 33))
        self.assert_rejected(lambda: decode_inputs(self.model_bytes, over_digits), "out_of_scope", "E_RATIONAL_LIMIT")
        with mock.patch("writ_decision_lab.decode.sys.get_int_max_str_digits", return_value=1000):
            self.assert_rejected(lambda: decode_model(self.model_bytes), "out_of_scope", "E_RUNTIME_INTEGER_LIMIT")

    def test_invalid_identifier_is_rejected_without_normalization(self) -> None:
        invalid = changed(self.model_bytes, lambda model: model["states"].__setitem__(0, "s 0"))
        self.assert_rejected(lambda: decode_model(invalid), "invalid_input", "E_IDENTIFIER")

    def test_result_rationals_have_larger_but_finite_cap(self) -> None:
        self.assertEqual(parse_rational("1/" + "9" * 4096, "$.x", digit_limit=4096).numerator, 1)
        self.assert_rejected(
            lambda: parse_rational("1/" + "9" * 4097, "$.x", digit_limit=4096),
            "out_of_scope",
            "E_RATIONAL_LIMIT",
        )


if __name__ == "__main__":
    unittest.main()
