from __future__ import annotations

from unittest import mock
import unittest

from writ_decision_lab import check_and_load, solve_bytes
from writ_decision_lab.errors import CheckFailure
from writ_decision_lab.identity import output_bytes

from support import changed, fixture, parsed


class ConsumerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.model, self.query = fixture("F01-weak")
        self.result = solve_bytes(self.model, self.query)

    def test_checked_answer_exposes_small_summary(self) -> None:
        checked = check_and_load(self.model, self.query, self.result)
        self.assertEqual(checked.summary(), {
            "schema": "wdl.consumer-summary.v1",
            "semantics": "finite-one-observation.v1",
            "current_argmin": ["a0"],
            "evsi": "1/8",
            "acquisition_argmin": ["observe_once"],
        })

    def test_tampered_answer_and_changed_question_expose_no_answer(self) -> None:
        tampered = changed(self.result, lambda result: result["answer"].__setitem__("evsi", "1/4"))
        changed_query = changed(self.query, lambda query: query.__setitem__("cost", "1/8"))
        for model, query, result, status in (
            (self.model, self.query, tampered, "computation_mismatch"),
            (self.model, changed_query, self.result, "input_mismatch"),
        ):
            with self.subTest(status=status):
                with self.assertRaises(CheckFailure) as caught:
                    check_and_load(model, query, result)
                self.assertEqual(caught.exception.status, status)

    def test_forged_saved_check_cannot_grant_access(self) -> None:
        tampered = changed(self.result, lambda result: result["answer"].__setitem__("evsi", "1/4"))
        forged_check = output_bytes({"schema": "wdl.check.v1", "status": "checked"})
        self.assertIn(b'"checked"', forged_check)
        with self.assertRaises(CheckFailure) as caught:
            check_and_load(self.model, self.query, tampered)
        self.assertEqual(caught.exception.status, "computation_mismatch")

    def test_unexpected_checker_exception_fails_closed(self) -> None:
        with mock.patch("writ_decision_lab.consumer.checker.check_bytes", side_effect=RuntimeError("secret")):
            with self.assertRaises(CheckFailure) as caught:
                check_and_load(self.model, self.query, self.result)
        self.assertEqual(caught.exception.status, "checker_error")
        self.assertEqual(caught.exception.diagnostic.message, "Unexpected checker failure.")

    def test_downstream_sink_spy_is_not_called_on_any_failure(self) -> None:
        sink = mock.Mock()

        def workflow(model: bytes, query: bytes, result: bytes) -> None:
            checked = check_and_load(model, query, result)
            sink(checked.summary())

        malformed = b"{}\n"
        changed_query = changed(self.query, lambda query: query.__setitem__("cost", "1/8"))
        tampered = changed(self.result, lambda result: result["answer"].__setitem__("evsi", "1/4"))
        for model, query, result in (
            (malformed, self.query, self.result),
            (self.model, changed_query, self.result),
            (self.model, self.query, tampered),
        ):
            with self.assertRaises(CheckFailure):
                workflow(model, query, result)
        sink.assert_not_called()


if __name__ == "__main__":
    unittest.main()
