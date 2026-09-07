"""Separate direct-joint-mass and exhaustive-policy checker.

This module deliberately does not import the producer or its mathematical helpers.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import product
from typing import Any

from .decode import RESULT_RATIONAL_DIGITS, SEMANTICS, decode_inputs, decode_result, parse_rational
from .errors import Diagnostic, WdlError
from .identity import digest_bytes, output_bytes, runtime_context, wire
from .types import CheckReport, Model, Query, RuntimeContext


CHECKER_NAME = "writ-decision-lab"
CHECKER_METHOD = "joint-mass-and-policy-enumeration.v1"
LIMITATIONS = [
    "Checks the supplied finite one-observation calculation only.",
    "Does not validate source fidelity, real-world assumptions, or cross-question sufficiency.",
    "Is not a formal proof, independent authorship, scientific acceptance, or permission to skip fresh checking.",
    "Producer and checker share the strict parser, immutable input types, Fraction library, specification, and author.",
]


def _report(
    *,
    status: str,
    model_bytes: bytes | None,
    query_bytes: bytes | None,
    result_bytes: bytes | None,
    diagnostics: list[Diagnostic],
    policy_count: int | None,
    context: RuntimeContext,
) -> CheckReport:
    record = {
        "schema": "wdl.check.v1",
        "semantics": SEMANTICS,
        "subject": {
            "model_sha256": digest_bytes(model_bytes) if model_bytes is not None else None,
            "query_sha256": digest_bytes(query_bytes) if query_bytes is not None else None,
            "result_sha256": digest_bytes(result_bytes) if result_bytes is not None else None,
        },
        "checker": {
            "name": CHECKER_NAME,
            "method": CHECKER_METHOD,
            "code_sha256": context.code_sha256,
            "python_version": context.python_version,
        },
        "status": status,
        "diagnostics": [diagnostic.as_dict() for diagnostic in diagnostics],
        "policy_count": policy_count,
        "limitations": list(LIMITATIONS),
    }
    return CheckReport(record, status, tuple(diagnostics), policy_count)


def report_bytes(report: CheckReport) -> bytes:
    return output_bytes(dict(report.record))


def not_checked_report(
    model_bytes: bytes | None,
    query_bytes: bytes | None,
    result_bytes: bytes | None,
    missing_roles: list[str],
    context: RuntimeContext | None = None,
) -> CheckReport:
    diagnostics = [
        Diagnostic("E_FILE_UNAVAILABLE", f"$.{role}", f"Required {role} bytes are unavailable.")
        for role in ("model", "query", "result")
        if role in missing_roles
    ]
    return _report(
        status="not_checked",
        model_bytes=model_bytes,
        query_bytes=query_bytes,
        result_bytes=result_bytes,
        diagnostics=diagnostics,
        policy_count=None,
        context=context or runtime_context(),
    )


def _expected_answer(model: Model, query: Query) -> tuple[dict[str, Any], int, list[list[Fraction]], list[list[Fraction]]]:
    state_count = len(model.states)
    action_count = len(query.actions)
    outcome_count = len(model.outcomes)
    prior_risks = [
        sum(
            (model.prior[state] * query.losses[action][state] for state in range(state_count)),
            Fraction(0),
        )
        for action in range(action_count)
    ]
    current_risk = min(prior_risks)
    joints: list[list[Fraction]] = []
    joint_losses: list[list[Fraction]] = []
    branches: list[dict[str, Any]] = []
    for outcome in range(outcome_count):
        joint = [
            model.prior[state] * model.likelihood[state][outcome]
            for state in range(state_count)
        ]
        joints.append(joint)
        mass = sum(joint, Fraction(0))
        losses = [
            sum(
                (joint[state] * query.losses[action][state] for state in range(state_count)),
                Fraction(0),
            )
            for action in range(action_count)
        ]
        joint_losses.append(losses)
        if mass == 0:
            branches.append(
                {
                    "outcome": model.outcomes[outcome],
                    "status": "impossible",
                    "mass": Fraction(0),
                    "posterior": None,
                    "risks": None,
                    "minimum_risk": None,
                    "argmin": None,
                }
            )
            continue
        posterior = [value / mass for value in joint]
        conditional_risks = [value / mass for value in losses]
        minimum = min(conditional_risks)
        branches.append(
            {
                "outcome": model.outcomes[outcome],
                "status": "possible",
                "mass": mass,
                "posterior": posterior,
                "risks": conditional_risks,
                "minimum_risk": minimum,
                "argmin": [
                    query.actions[action]
                    for action, value in enumerate(conditional_risks)
                    if value == minimum
                ],
            }
        )
    policy_values: list[Fraction] = []
    for policy in product(range(action_count), repeat=outcome_count):
        policy_values.append(
            sum(
                (
                    model.prior[state]
                    * model.likelihood[state][outcome]
                    * query.losses[policy[outcome]][state]
                    for state in range(state_count)
                    for outcome in range(outcome_count)
                ),
                Fraction(0),
            )
        )
    observed_risk = min(policy_values)
    evsi = current_risk - observed_risk
    acquisition_risks = {
        "act_now": current_risk,
        "observe_once": observed_risk + query.cost,
    }
    acquisition_minimum = min(acquisition_risks.values())
    expected = {
        "state_order": list(model.states),
        "outcome_order": list(model.outcomes),
        "action_order": list(query.actions),
        "loss_unit": query.loss_unit,
        "prior_risks": prior_risks,
        "current_risk": current_risk,
        "current_argmin": [
            query.actions[action]
            for action, value in enumerate(prior_risks)
            if value == current_risk
        ],
        "branches": branches,
        "observed_risk": observed_risk,
        "evsi": evsi,
        "net_value": evsi - query.cost,
        "acquisition_risks": acquisition_risks,
        "acquisition_argmin": [
            label
            for label in ("act_now", "observe_once")
            if acquisition_risks[label] == acquisition_minimum
        ],
    }
    return wire(expected), len(policy_values), joints, joint_losses


def _claimed_rational(value: Any, path: str) -> Fraction:
    return parse_rational(value, path, digit_limit=RESULT_RATIONAL_DIGITS)


def _identity_diagnostics(
    claimed: dict[str, Any],
    model: Model,
    query: Query,
    joints: list[list[Fraction]],
    joint_losses: list[list[Fraction]],
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    branches = claimed["answer"]["branches"]
    for outcome in range(min(len(branches), len(model.outcomes))):
        branch = branches[outcome]
        path = f"$.answer.branches[{outcome}]"
        expected_mass = sum(joints[outcome], Fraction(0))
        if branch["status"] != "possible" or expected_mass == 0:
            continue
        mass = _claimed_rational(branch["mass"], f"{path}.mass")
        posterior = [
            _claimed_rational(value, f"{path}.posterior[{index}]")
            for index, value in enumerate(branch["posterior"])
        ]
        if len(posterior) != len(model.states) or any(value < 0 for value in posterior) or sum(posterior, Fraction(0)) != 1:
            diagnostics.append(Diagnostic("E_POSTERIOR_NORMALIZATION", f"{path}.posterior", "Claimed posterior is not a nonnegative distribution of the required length."))
        else:
            for state, value in enumerate(posterior):
                if mass * value != joints[outcome][state]:
                    diagnostics.append(Diagnostic("E_POSTERIOR_IDENTITY", f"{path}.posterior[{state}]", "Claimed posterior fails the exact joint-mass identity."))
        risks = [
            _claimed_rational(value, f"{path}.risks[{index}]")
            for index, value in enumerate(branch["risks"])
        ]
        if len(risks) != len(query.actions):
            diagnostics.append(Diagnostic("E_RISK_DIMENSION", f"{path}.risks", "Claimed conditional-risk length does not match actions."))
        else:
            for action, value in enumerate(risks):
                if mass * value != joint_losses[outcome][action]:
                    diagnostics.append(Diagnostic("E_RISK_IDENTITY", f"{path}.risks[{action}]", "Claimed conditional risk fails the exact joint-loss identity."))
    return diagnostics


def _compare(expected: Any, actual: Any, path: str, diagnostics: list[Diagnostic]) -> None:
    if isinstance(expected, dict) and isinstance(actual, dict):
        for key in expected:
            _compare(expected[key], actual[key], f"{path}.{key}", diagnostics)
        return
    if isinstance(expected, list) and isinstance(actual, list):
        if len(expected) != len(actual):
            diagnostics.append(Diagnostic("E_COMPUTATION_MISMATCH", path, "Claimed array length differs from the checked value."))
            return
        for index, (expected_item, actual_item) in enumerate(zip(expected, actual)):
            _compare(expected_item, actual_item, f"{path}[{index}]", diagnostics)
        return
    if expected != actual:
        diagnostics.append(Diagnostic("E_COMPUTATION_MISMATCH", path, "Claimed value differs from the checked value."))


def check_with_context(
    model_bytes: bytes,
    query_bytes: bytes,
    result_bytes: bytes,
    context: RuntimeContext,
) -> CheckReport:
    try:
        model, query = decode_inputs(model_bytes, query_bytes)
        claimed = decode_result(result_bytes)
    except WdlError as error:
        return _report(
            status=error.status,
            model_bytes=model_bytes,
            query_bytes=query_bytes,
            result_bytes=result_bytes,
            diagnostics=[error.diagnostic],
            policy_count=None,
            context=context,
        )
    except Exception:
        return _report(
            status="checker_error",
            model_bytes=model_bytes,
            query_bytes=query_bytes,
            result_bytes=result_bytes,
            diagnostics=[Diagnostic("E_CHECKER_INTERNAL", "$", "Unexpected checker failure.")],
            policy_count=None,
            context=context,
        )
    binding_diagnostics: list[Diagnostic] = []
    bindings = claimed["input_bindings"]
    if bindings["model_sha256"] != digest_bytes(model_bytes):
        binding_diagnostics.append(Diagnostic("E_MODEL_BINDING", "$.input_bindings.model_sha256", "Result is bound to different model bytes."))
    if bindings["query_sha256"] != digest_bytes(query_bytes):
        binding_diagnostics.append(Diagnostic("E_QUERY_BINDING", "$.input_bindings.query_sha256", "Result is bound to different query bytes."))
    if binding_diagnostics:
        return _report(
            status="input_mismatch",
            model_bytes=model_bytes,
            query_bytes=query_bytes,
            result_bytes=result_bytes,
            diagnostics=binding_diagnostics,
            policy_count=None,
            context=context,
        )
    try:
        expected, policy_count, joints, joint_losses = _expected_answer(model, query)
        diagnostics = _identity_diagnostics(claimed, model, query, joints, joint_losses)
        _compare(expected, claimed["answer"], "$.answer", diagnostics)
        status = "computation_mismatch" if diagnostics else "checked"
        return _report(
            status=status,
            model_bytes=model_bytes,
            query_bytes=query_bytes,
            result_bytes=result_bytes,
            diagnostics=diagnostics,
            policy_count=policy_count,
            context=context,
        )
    except WdlError as error:
        return _report(
            status=error.status,
            model_bytes=model_bytes,
            query_bytes=query_bytes,
            result_bytes=result_bytes,
            diagnostics=[error.diagnostic],
            policy_count=None,
            context=context,
        )
    except Exception:
        return _report(
            status="checker_error",
            model_bytes=model_bytes,
            query_bytes=query_bytes,
            result_bytes=result_bytes,
            diagnostics=[Diagnostic("E_CHECKER_INTERNAL", "$", "Unexpected checker failure.")],
            policy_count=None,
            context=context,
        )


def check_bytes(model_bytes: bytes, query_bytes: bytes, result_bytes: bytes) -> CheckReport:
    """Freshly check a result against the exact caller-supplied inputs."""
    return check_with_context(model_bytes, query_bytes, result_bytes, runtime_context())
