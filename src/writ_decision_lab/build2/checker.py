"""Independent exact checker. It never invokes the search backend."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
from types import MappingProxyType
from typing import Any

from .errors import CheckError, InputError
from .exact import fraction_text, rational, require_keys
from .model import Problem, Query, decode_problem, decode_query


@dataclass(frozen=True)
class CheckedResult:
    operation: str
    status: str
    family_kind: str
    model_sha256: str
    query_sha256: str
    conclusion: MappingProxyType


def _frac(value: Any, where: str) -> Fraction:
    try:
        return rational(value, where)
    except InputError as exc:
        raise CheckError(str(exc)) from exc


def _vec(values: Any, size: int, where: str) -> tuple[Fraction, ...]:
    if not isinstance(values, list) or len(values) != size:
        raise CheckError(f"dimension_mismatch:{where}")
    return tuple(_frac(v, f"{where}[{i}]") for i, v in enumerate(values))


def _feasible(problem: Problem, values: Any, where: str) -> tuple[Fraction, ...]:
    p = _vec(values, problem.dimension, where)
    if any(x < 0 for x in p):
        raise CheckError(f"negative_probability:{where}")
    for row in problem.equalities:
        if sum(a * x for a, x in zip(row.coefficients, p)) != row.rhs:
            raise CheckError(f"equality_violation:{row.label}")
    for row in problem.inequalities:
        if sum(a * x for a, x in zip(row.coefficients, p)) > row.rhs:
            raise CheckError(f"inequality_violation:{row.label}")
    return p


def _linear_combo(problem: Problem, y: tuple[Fraction, ...], z: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    return tuple(
        sum(row.coefficients[j] * value for row, value in zip(problem.equalities, y))
        + sum(row.coefficients[j] * value for row, value in zip(problem.inequalities, z))
        for j in range(problem.dimension)
    )


def _rhs_combo(problem: Problem, y: tuple[Fraction, ...], z: tuple[Fraction, ...]) -> Fraction:
    return sum(row.rhs * value for row, value in zip(problem.equalities, y)) + sum(
        row.rhs * value for row, value in zip(problem.inequalities, z)
    )


def _certificate(problem: Problem, obj: tuple[Fraction, ...], raw: Any, sense: str) -> Fraction:
    if not isinstance(raw, dict):
        raise CheckError("invalid_bound_certificate")
    require_keys(raw, {"y", "z", "bound"})
    y = _vec(raw["y"], len(problem.equalities), "certificate.y")
    z = _vec(raw["z"], len(problem.inequalities), "certificate.z")
    bound = _frac(raw["bound"], "certificate.bound")
    lhs = _linear_combo(problem, y, z)
    actual = _rhs_combo(problem, y, z)
    if actual != bound:
        raise CheckError("false_declared_bound")
    if sense == "max":
        if any(value < 0 for value in z) or any(a < b for a, b in zip(lhs, obj)):
            raise CheckError("invalid_upper_bound_certificate")
    else:
        if any(value > 0 for value in z) or any(a > b for a, b in zip(lhs, obj)):
            raise CheckError("invalid_lower_bound_certificate")
    return bound


def _endpoint(problem: Problem, obj: tuple[Fraction, ...], raw: Any, sense: str) -> tuple[Fraction, tuple[Fraction, ...]]:
    if not isinstance(raw, dict):
        raise CheckError("invalid_endpoint")
    require_keys(raw, {"witness", "objective", "certificate"})
    p = _feasible(problem, raw["witness"], f"{sense}.witness")
    objective = _frac(raw["objective"], f"{sense}.objective")
    if sum(a * x for a, x in zip(obj, p)) != objective:
        raise CheckError("false_primal_objective")
    bound = _certificate(problem, obj, raw["certificate"], sense)
    if bound != objective:
        raise CheckError("primal_dual_objective_disagreement")
    return objective, p


def _freeze(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


def check(bundle: dict, problem_raw: bytes, query_raw: bytes) -> CheckedResult:
    if not isinstance(bundle, dict):
        raise CheckError("bundle_must_be_object")
    required = {"schema", "operation", "model_sha256", "query_sha256", "family_kind", "backend", "status", "evidence"}
    optional = {"reason"}
    try:
        require_keys(bundle, required, optional)
        problem = decode_problem(problem_raw)
        query = decode_query(query_raw, problem.dimension)
    except InputError as exc:
        raise CheckError(str(exc)) from exc
    if bundle["schema"] != "finite-linear-uncertainty-result.v1":
        raise CheckError("unsupported_result_schema")
    if bundle["operation"] != query.operation or bundle["family_kind"] != problem.family_kind:
        raise CheckError("declared_profile_mismatch")
    model_hash, query_hash = sha256(problem_raw).hexdigest(), sha256(query_raw).hexdigest()
    if bundle["model_sha256"] != model_hash or bundle["query_sha256"] != query_hash:
        raise CheckError("stale_byte_binding")
    status, evidence = bundle["status"], bundle["evidence"]
    if not isinstance(evidence, dict):
        raise CheckError("evidence_must_be_object")

    conclusion: dict[str, Any]
    if status == "unresolved":
        if set(bundle) != required | {"reason"} or not isinstance(bundle["reason"], str) or evidence:
            raise CheckError("invalid_unresolved_bundle")
        conclusion = {"reason": bundle["reason"]}
    elif status == "compatible" and query.operation == "compatibility":
        require_keys(evidence, {"witness"})
        p = _feasible(problem, evidence["witness"], "compatibility.witness")
        conclusion = {"witness": tuple(fraction_text(x) for x in p)}
    elif status == "incompatible":
        require_keys(evidence, {"farkas"})
        cert = evidence["farkas"]
        if not isinstance(cert, dict):
            raise CheckError("invalid_farkas_certificate")
        require_keys(cert, {"y", "z", "contradiction"})
        y = _vec(cert["y"], len(problem.equalities), "farkas.y")
        z = _vec(cert["z"], len(problem.inequalities), "farkas.z")
        contradiction = _frac(cert["contradiction"], "farkas.contradiction")
        if any(value < 0 for value in z) or any(value < 0 for value in _linear_combo(problem, y, z)):
            raise CheckError("invalid_farkas_certificate")
        if _rhs_combo(problem, y, z) != contradiction or contradiction >= 0:
            raise CheckError("invalid_farkas_contradiction")
        conclusion = {"contradiction": fraction_text(contradiction)}
    elif query.operation == "linear_range" and status in {"identified", "partially_identified"}:
        require_keys(evidence, {"minimum", "maximum"})
        low, low_p = _endpoint(problem, query.coefficients, evidence["minimum"], "min")
        high, high_p = _endpoint(problem, query.coefficients, evidence["maximum"], "max")
        if low > high:
            raise CheckError("reversed_range")
        expected = "identified" if low == high else "partially_identified"
        if status != expected:
            raise CheckError("false_identification_status")
        conclusion = {
            "minimum": fraction_text(low),
            "maximum": fraction_text(high),
            "minimum_witness": tuple(fraction_text(x) for x in low_p),
            "maximum_witness": tuple(fraction_text(x) for x in high_p),
        }
    elif query.operation == "decision" and status == "decision_candidate":
        require_keys(evidence, {"pairs"})
        pairs = evidence["pairs"]
        if not isinstance(pairs, list):
            raise CheckError("invalid_decision_pairs")
        action_map = dict(query.actions)
        expected_pairs = {(a, b) for a in action_map for b in action_map if a != b}
        seen: set[tuple[str, str]] = set()
        maxima: dict[tuple[str, str], tuple[Fraction, tuple[Fraction, ...]]] = {}
        for index, item in enumerate(pairs):
            if not isinstance(item, dict):
                raise CheckError("invalid_decision_pair")
            require_keys(item, {"action", "competitor", "maximum_difference"})
            key = (item["action"], item["competitor"])
            if key not in expected_pairs or key in seen:
                raise CheckError("unexpected_or_duplicate_decision_pair")
            seen.add(key)
            obj = tuple(x - y for x, y in zip(action_map[key[0]], action_map[key[1]]))
            maxima[key] = _endpoint(problem, obj, item["maximum_difference"], "max")
        if seen != expected_pairs:
            raise CheckError("incomplete_decision_pairs")
        common = tuple(a for a in action_map if all(maxima[(a, b)][0] <= 0 for b in action_map if a != b))
        strict = tuple(a for a in action_map if all(maxima[(a, b)][0] < 0 for b in action_map if a != b))
        if len(strict) == 1:
            decision_status = "uniformly_strictly_optimal"
        elif len(common) == 1:
            decision_status = "uniformly_optimal"
        elif common:
            decision_status = "complete_common_minimizing_set"
        else:
            decision_status = "model_dependent"
        disagreements = []
        if not common:
            for a in action_map:
                for b in action_map:
                    if a != b and maxima[(a, b)][0] > 0:
                        disagreements.append({
                            "action": a,
                            "better_competitor": b,
                            "witness": tuple(fraction_text(x) for x in maxima[(a, b)][1]),
                        })
                        break
        conclusion = {
            "decision_status": decision_status,
            "common_minimizers": common,
            "strictly_optimal": strict,
            "pairwise_maxima": tuple((a, b, fraction_text(v[0])) for (a, b), v in maxima.items()),
            "disagreement_witnesses": tuple(_freeze(x) for x in disagreements),
        }
    else:
        raise CheckError("status_operation_mismatch")

    return CheckedResult(query.operation, status if status != "decision_candidate" else conclusion["decision_status"], problem.family_kind, model_hash, query_hash, _freeze(conclusion))

