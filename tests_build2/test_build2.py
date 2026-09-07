from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path
from types import MappingProxyType
import copy
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from writ_decision_lab.build2 import backend
from writ_decision_lab.build2.checker import check
from writ_decision_lab.build2.consumer import consume
from writ_decision_lab.build2.engine import produce, solve_and_check
from writ_decision_lab.build2.errors import CheckError, InputError
from writ_decision_lab.build2.exact import MAX_JSON_DEPTH, loads_strict


def raw(path):
    return (ROOT / path).read_bytes()


def child_argv(*args, inherit_optimization=True):
    optimization = ["-" + "O" * sys.flags.optimize] if inherit_optimization and sys.flags.optimize else []
    return [sys.executable, *optimization, *args]


class PositiveFixtures(unittest.TestCase):
    def test_a_triangle_has_checked_farkas_certificate(self):
        bundle, checked = solve_and_check(raw("fixtures/v2/A-triangle/model.json"), raw("fixtures/v2/A-triangle/query.json"))
        self.assertEqual("incompatible", checked.status)
        self.assertLess(bundle["evidence"]["farkas"]["contradiction"], "0")

    def test_b_gluing_has_exact_joint_witness(self):
        _, checked = solve_and_check(raw("fixtures/v2/B-gluing/model.json"), raw("fixtures/v2/B-gluing/query.json"))
        self.assertEqual("compatible", checked.status)
        self.assertEqual(8, len(checked.conclusion["witness"]))

    def test_c_identified_scalar(self):
        _, checked = solve_and_check(raw("fixtures/v2/C-identified/model.json"), raw("fixtures/v2/C-identified/query.json"))
        self.assertEqual(("1/3", "1/3"), (checked.conclusion["minimum"], checked.conclusion["maximum"]))
        self.assertEqual("identified", checked.status)

    def test_d_nonidentified_has_two_endpoints(self):
        _, checked = solve_and_check(raw("fixtures/v2/D-nonidentified/model.json"), raw("fixtures/v2/D-nonidentified/query.json"))
        self.assertEqual("partially_identified", checked.status)
        self.assertEqual("1/4", checked.conclusion["minimum"])
        self.assertEqual("3/4", checked.conclusion["maximum"])
        self.assertNotEqual(checked.conclusion["minimum_witness"], checked.conclusion["maximum_witness"])

    def test_e_probability_nonidentified(self):
        _, checked = solve_and_check(raw("fixtures/v2/E-integrated/posterior-model.json"), raw("fixtures/v2/E-integrated/probability-query.json"))
        self.assertEqual(("4/7", "8/11"), (checked.conclusion["minimum"], checked.conclusion["maximum"]))

    def test_e_action_identified_with_gap(self):
        _, checked = solve_and_check(raw("fixtures/v2/E-integrated/posterior-model.json"), raw("fixtures/v2/E-integrated/decision-query.json"))
        self.assertEqual("uniformly_strictly_optimal", checked.status)
        self.assertEqual(("predict_1",), checked.conclusion["common_minimizers"])
        self.assertIn(("predict_1", "predict_0", "-1/7"), checked.conclusion["pairwise_maxima"])

    def test_f_changed_losses_are_model_dependent(self):
        _, checked = solve_and_check(raw("fixtures/v2/E-integrated/posterior-model.json"), raw("fixtures/v2/F-changed-losses/changed-decision-query.json"))
        self.assertEqual("model_dependent", checked.status)
        self.assertEqual(2, len(checked.conclusion["disagreement_witnesses"]))

    def test_g_exact_and_outer_conclusions_stay_distinct(self):
        q = raw("fixtures/v2/G-exact-vs-outer/query.json")
        _, exact = solve_and_check(raw("fixtures/v2/G-exact-vs-outer/exact-model.json"), q)
        _, outer = solve_and_check(raw("fixtures/v2/G-exact-vs-outer/outer-model.json"), q)
        self.assertEqual(("exact_family", "identified"), (exact.family_kind, exact.status))
        self.assertEqual(("outer_enclosure", "partially_identified"), (outer.family_kind, outer.status))

    def test_h_impossible_conditioning_is_unresolved(self):
        _, checked = solve_and_check(raw("fixtures/v2/H-unresolved/model.json"), raw("fixtures/v2/H-unresolved/impossible-conditional-query.json"))
        self.assertEqual("unresolved", checked.status)
        self.assertEqual("conditioning_event_impossible", checked.conclusion["reason"])


class StrictInputTests(unittest.TestCase):
    def setUp(self):
        self.model = raw("fixtures/v2/C-identified/model.json")
        self.query = raw("fixtures/v2/C-identified/query.json")

    def test_noncanonical_rational_rejected(self):
        with self.assertRaises(InputError):
            produce(self.model.replace(b'"1/3"', b'"2/6"'), self.query)

    def test_decimal_rational_rejected(self):
        with self.assertRaises(InputError):
            produce(self.model.replace(b'"1/3"', b'0.333'), self.query)

    def test_duplicate_json_key_rejected(self):
        bad = self.model.replace(b'{"semantics":', b'{"semantics":"finite-linear-uncertainty.v1","semantics":', 1)
        with self.assertRaises(InputError):
            produce(bad, self.query)

    def test_duplicate_state_label_rejected(self):
        with self.assertRaises(InputError):
            produce(self.model.replace(b'"theta=1"', b'"theta=0"'), self.query)

    def test_duplicate_constraint_label_rejected(self):
        obj = json.loads(self.model)
        obj["equalities"].append(copy.deepcopy(obj["equalities"][0]))
        with self.assertRaises(InputError):
            produce((json.dumps(obj)+"\n").encode(), self.query)

    def test_dimension_mismatch_rejected(self):
        with self.assertRaises(InputError):
            produce(self.model, self.query.replace(b'["0","1"]', b'["1"]'))

    def test_unsupported_semantics_rejected(self):
        with self.assertRaises(InputError):
            produce(self.model.replace(b"finite-linear-uncertainty.v1", b"invented.v9"), self.query)

    def test_missing_normalization_rejected(self):
        with self.assertRaises(InputError):
            produce(self.model.replace(b'"exact_one"', b'"implicit"'), self.query)

    def test_json_depth_boundary_and_hostile_inputs_are_controlled(self):
        def nested(depth):
            return (b'{"x":' + b'[' * (depth - 1) + b'0' + b']' * (depth - 1) + b'}')

        for depth in (MAX_JSON_DEPTH - 1, MAX_JSON_DEPTH):
            self.assertIsInstance(loads_strict(nested(depth)), dict)
        for depth in (MAX_JSON_DEPTH + 1, 2000):
            with self.assertRaisesRegex(InputError, "json_depth_limit") as caught:
                loads_strict(nested(depth))
            self.assertNotIsInstance(caught.exception, RecursionError)
            for model, query in ((nested(depth), self.query), (self.model, nested(depth))):
                with self.assertRaises(InputError) as decoded:
                    produce(model, query)
                self.assertNotIsInstance(decoded.exception, RecursionError)


class HostileBundleTests(unittest.TestCase):
    def setUp(self):
        self.model = raw("fixtures/v2/D-nonidentified/model.json")
        self.query = raw("fixtures/v2/D-nonidentified/query.json")
        self.bundle, self.checked = solve_and_check(self.model, self.query)

    def assertRefused(self, bundle, model=None, query=None):
        with self.assertRaises(Exception):
            check(bundle, model or self.model, query or self.query)

    def test_stale_model_bytes_refused(self):
        changed = self.model.replace(b'"3/4"', b'"2/3"')
        self.assertRefused(self.bundle, model=changed)

    def test_changed_query_unchanged_family_refused(self):
        changed = self.query.replace(b'"0","1"', b'"1","0"')
        self.assertRefused(self.bundle, query=changed)

    def test_forged_primal_objective_refused(self):
        bad = copy.deepcopy(self.bundle)
        bad["evidence"]["maximum"]["objective"] = "2/3"
        self.assertRefused(bad)

    def test_primal_dual_disagreement_refused(self):
        bad = copy.deepcopy(self.bundle)
        bad["evidence"]["maximum"]["certificate"]["bound"] = "2/3"
        self.assertRefused(bad)

    def test_forged_certificate_multiplier_refused(self):
        bad = copy.deepcopy(self.bundle)
        bad["evidence"]["maximum"]["certificate"]["z"][0] = "0"
        self.assertRefused(bad)

    def test_witness_violating_omitted_constraint_refused(self):
        bad = copy.deepcopy(self.bundle)
        bad["evidence"]["maximum"]["witness"] = ["0", "1"]
        bad["evidence"]["maximum"]["objective"] = "1"
        self.assertRefused(bad)

    def test_coherent_but_false_identified_bundle_refused(self):
        bad = copy.deepcopy(self.bundle)
        bad["status"] = "identified"
        self.assertRefused(bad)

    def test_invalid_farkas_certificate_refused(self):
        m = raw("fixtures/v2/A-triangle/model.json")
        q = raw("fixtures/v2/A-triangle/query.json")
        bundle, _ = solve_and_check(m, q)
        bundle["evidence"]["farkas"]["y"] = ["0"] * len(bundle["evidence"]["farkas"]["y"])
        with self.assertRaises(Exception):
            check(bundle, m, q)

    def test_result_snapshot_is_immutable_and_detached(self):
        before = self.checked.conclusion["maximum"]
        self.bundle["evidence"]["maximum"]["objective"] = "0"
        self.assertEqual(before, self.checked.conclusion["maximum"])
        with self.assertRaises(TypeError):
            self.checked.conclusion["maximum"] = "0"
        with self.assertRaises(FrozenInstanceError):
            self.checked.status = "forged"


class FailureAndConsumerTests(unittest.TestCase):
    def setUp(self):
        self.model = raw("fixtures/v2/H-unresolved/model.json")
        self.query = raw("fixtures/v2/H-unresolved/query.json")

    def test_backend_exception_is_unresolved(self):
        def boom(*args):
            raise RuntimeError("backend exploded")
        bundle, checked = solve_and_check(self.model, self.query, search=boom)
        self.assertEqual("unresolved", checked.status)
        self.assertEqual("backend_exception", bundle["reason"])

    def test_missing_backend_is_unresolved(self):
        original = backend.linprog
        backend.linprog = None
        try:
            bundle, checked = solve_and_check(self.model, self.query)
        finally:
            backend.linprog = original
        self.assertEqual("unresolved", checked.status)
        self.assertEqual("backend_exception", bundle["reason"])

    def test_absent_backend_certificate_is_unresolved(self):
        def absent(problem_raw, query_raw, problem, query):
            from writ_decision_lab.build2.engine import _unresolved
            return _unresolved(problem_raw, query_raw, problem, query, "absent_exact_endpoint_certificate")
        _, checked = solve_and_check(self.model, self.query, search=absent)
        self.assertEqual("unresolved", checked.status)

    def test_mathematically_false_backend_candidate_downgrades_to_unresolved(self):
        real = backend.search
        def forged(*args):
            bundle = real(*args)
            bundle["evidence"]["minimum"]["objective"] = "99"
            return bundle
        bundle, checked = solve_and_check(self.model, self.query, search=forged)
        self.assertEqual("candidate_evidence_failed_exact_check", bundle["reason"])
        self.assertEqual("unresolved", checked.status)

    def test_every_malformed_backend_shape_downgrades_to_checked_unresolved(self):
        malformed = (
            None,
            [],
            {"status": "invented"},
            {"schema": "finite-linear-uncertainty-result.v1", "status": "unresolved"},
        )
        for payload in malformed:
            with self.subTest(payload=payload):
                bundle, checked = solve_and_check(
                    self.model, self.query, search=lambda *_args, value=payload: value
                )
                self.assertEqual("candidate_evidence_failed_exact_check", bundle["reason"])
                self.assertEqual("unresolved", checked.status)

    def test_invalid_certificate_values_and_structures_do_not_leak_validation_errors(self):
        real = backend.search
        mutations = (
            lambda bundle: bundle["evidence"].__setitem__("minimum", []),
            lambda bundle: bundle["evidence"]["minimum"].__setitem__("objective", "2/4"),
            lambda bundle: bundle.__setitem__("status", ["partially_identified"]),
        )
        for mutate in mutations:
            def forged(*args, mutate=mutate):
                bundle = real(*args)
                mutate(bundle)
                return bundle
            with self.subTest(mutate=mutate):
                fallback, checked = solve_and_check(self.model, self.query, search=forged)
                self.assertEqual("candidate_evidence_failed_exact_check", fallback["reason"])
                self.assertEqual("unresolved", checked.status)

    def test_unresolved_reason_codes_are_closed_and_operation_specific(self):
        def unresolved(reason):
            def search(problem_raw, query_raw, problem, query):
                from writ_decision_lab.build2.engine import _unresolved
                return _unresolved(problem_raw, query_raw, problem, query, reason)
            return search

        cases = (
            (raw("fixtures/v2/A-triangle/model.json"), raw("fixtures/v2/A-triangle/query.json"), "absent_exact_infeasibility_certificate", "absent_exact_endpoint_certificate"),
            (self.model, self.query, "absent_exact_endpoint_certificate", "absent_exact_action_certificate"),
            (raw("fixtures/v2/E-integrated/posterior-model.json"), raw("fixtures/v2/E-integrated/decision-query.json"), "absent_exact_action_certificate", "conditioning_event_impossible"),
            (self.model, raw("fixtures/v2/H-unresolved/impossible-conditional-query.json"), "conditioning_event_impossible", "absent_exact_action_certificate"),
        )
        for model, query, valid_reason, wrong_reason in cases:
            with self.subTest(valid_reason=valid_reason):
                _, checked = solve_and_check(model, query, search=unresolved(valid_reason))
                self.assertEqual(valid_reason, checked.conclusion["reason"])
            for hostile in (wrong_reason, "backend said: secret details"):
                bundle, result = solve_and_check(model, query, search=unresolved(hostile))
                self.assertEqual("candidate_evidence_failed_exact_check", bundle["reason"])
                self.assertEqual("candidate_evidence_failed_exact_check", result.conclusion["reason"])
                self.assertNotIn(hostile, repr(result.conclusion))

    def test_deep_backend_result_is_controlled_without_recursion_error(self):
        real = backend.search
        def hostile(*args):
            bundle = real(*args)
            value = "untrusted backend text"
            for _ in range(2000):
                value = [value]
            bundle["evidence"] = value
            return bundle
        fallback, checked = solve_and_check(self.model, self.query, search=hostile)
        self.assertEqual("candidate_evidence_failed_exact_check", fallback["reason"])
        self.assertEqual("unresolved", checked.status)
        self.assertNotIn("untrusted", repr(checked.conclusion))

    def test_cyclic_backend_result_is_controlled_without_text_laundering(self):
        for cyclic in ({}, []):
            if isinstance(cyclic, dict):
                cyclic["backend secret"] = cyclic
            else:
                cyclic.append(cyclic)

            def hostile(*_args, cyclic=cyclic):
                return cyclic

            with self.subTest(container=type(cyclic).__name__):
                fallback, checked = solve_and_check(self.model, self.query, search=hostile)
                self.assertEqual("candidate_evidence_failed_exact_check", fallback["reason"])
                self.assertEqual("unresolved", checked.status)
                self.assertNotIn("backend secret", repr(checked.conclusion))

    def test_consumer_freshly_checks(self):
        bundle, _ = solve_and_check(self.model, self.query)
        display = consume(bundle, self.model, self.query)
        self.assertIsInstance(display, MappingProxyType)
        self.assertEqual("partially_identified", display["display"])

    def test_consumer_refuses_stale_loss_query(self):
        model = raw("fixtures/v2/E-integrated/posterior-model.json")
        old_q = raw("fixtures/v2/E-integrated/decision-query.json")
        new_q = raw("fixtures/v2/F-changed-losses/changed-decision-query.json")
        bundle, _ = solve_and_check(model, old_q)
        with self.assertRaises(CheckError):
            consume(bundle, model, new_q)
        self.assertEqual("uniformly_strictly_optimal", consume(bundle, model, old_q)["display"])

    def test_consumer_refuses_checker_exception(self):
        bundle, _ = solve_and_check(self.model, self.query)
        def broken(*args):
            raise RuntimeError("checker failed")
        with self.assertRaises(CheckError):
            consume(bundle, self.model, self.query, checker=broken)

    def test_end_to_end_changed_constraint(self):
        spec = importlib.util.spec_from_file_location("change", ROOT / "examples/build2/change_and_recheck.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.main()
        self.assertTrue(result["stale_reuse_refused"])
        self.assertTrue(result["prior_preserved_for_prior_bytes"])


class DecisionBoundaryTests(unittest.TestCase):
    def test_exact_endpoint_tie_returns_complete_common_set(self):
        model = raw("fixtures/v2/C-identified/model.json").replace(b'"1/3"', b'"1/2"')
        query = b'{"semantics":"finite-linear-uncertainty.v1","operation":"decision","label":"tie","actions":[{"label":"a","losses":["0","1"]},{"label":"b","losses":["1","0"]}]}\n'
        _, checked = solve_and_check(model, query)
        self.assertEqual("complete_common_minimizing_set", checked.status)
        self.assertEqual(("a", "b"), checked.conclusion["common_minimizers"])

    def test_changed_losses_invalidate_old_certificate(self):
        model = raw("fixtures/v2/E-integrated/posterior-model.json")
        old_q = raw("fixtures/v2/E-integrated/decision-query.json")
        changed_q = raw("fixtures/v2/F-changed-losses/changed-decision-query.json")
        bundle, _ = solve_and_check(model, old_q)
        with self.assertRaises(Exception):
            check(bundle, model, changed_q)


class BaselineAndReproducibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("baseline", ROOT / "comparison/build2/baseline.py")
        cls.baseline = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.baseline)

    def test_equal_assurance_baseline_matches_candidate(self):
        model = raw("fixtures/v2/D-nonidentified/model.json")
        query = raw("fixtures/v2/D-nonidentified/query.json")
        _, candidate = solve_and_check(model, query)
        _, baseline, display = self.baseline.run(model, query)
        self.assertEqual(candidate, baseline)
        self.assertEqual(candidate.status, display["display"])

    def test_relocation(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "relocated"
            shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
            result = subprocess.run(
                child_argv("examples/build2/change_and_recheck.py"),
                cwd=target,
                env={"PYTHONPATH": str(target / "src")},
                text=True,
                capture_output=True,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn('"stale_reuse_refused": true', result.stdout)

    def test_subprocess_optimization_flag_propagation_and_normal_control(self):
        inherited = subprocess.run(
            child_argv("-c", "import sys; print(sys.flags.optimize)"),
            text=True,
            capture_output=True,
        )
        self.assertEqual(0, inherited.returncode, inherited.stderr)
        self.assertEqual(sys.flags.optimize, int(inherited.stdout))
        normal = subprocess.run(
            child_argv("-c", "import sys; print(sys.flags.optimize)", inherit_optimization=False),
            text=True,
            capture_output=True,
        )
        self.assertEqual(0, normal.returncode, normal.stderr)
        self.assertEqual(0, int(normal.stdout))

    def test_checker_import_does_not_load_scipy_backend(self):
        result = subprocess.run(
            child_argv("-c", "import sys; from writ_decision_lab.build2.checker import check; print('scipy' in sys.modules)"),
            cwd=ROOT,
            env={"PYTHONPATH": str(ROOT / "src")},
            text=True,
            capture_output=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("False", result.stdout.strip())


if __name__ == "__main__":
    unittest.main()
