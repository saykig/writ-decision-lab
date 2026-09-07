"""Posterior-based producer for the frozen one-observation semantics."""

from __future__ import annotations

from fractions import Fraction
from typing import Any

from .decode import SEMANTICS, decode_inputs
from .identity import digest_bytes, output_bytes, runtime_context
from .types import Model, Query, RuntimeContext


PRODUCER_NAME = "writ-decision-lab"
PRODUCER_VERSION = "0.1.0"


def _argmin(labels: tuple[str, ...], values: list[Fraction]) -> list[str]:
    minimum = min(values)
    return [label for label, value in zip(labels, values) if value == minimum]


def calculate(model: Model, query: Query) -> dict[str, Any]:
    """Calculate the answer without I/O, inference, randomness, or approximation."""
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
    branches: list[dict[str, Any]] = []
    observed_risk = Fraction(0)
    for outcome in range(outcome_count):
        joint = [
            model.prior[state] * model.likelihood[state][outcome]
            for state in range(state_count)
        ]
        mass = sum(joint, Fraction(0))
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
        risks = [
            sum(
                (posterior[state] * query.losses[action][state] for state in range(state_count)),
                Fraction(0),
            )
            for action in range(action_count)
        ]
        minimum_risk = min(risks)
        observed_risk += mass * minimum_risk
        branches.append(
            {
                "outcome": model.outcomes[outcome],
                "status": "possible",
                "mass": mass,
                "posterior": posterior,
                "risks": risks,
                "minimum_risk": minimum_risk,
                "argmin": _argmin(query.actions, risks),
            }
        )
    evsi = current_risk - observed_risk
    net_value = evsi - query.cost
    acquisition_risks = {
        "act_now": current_risk,
        "observe_once": observed_risk + query.cost,
    }
    acquisition_minimum = min(acquisition_risks.values())
    return {
        "state_order": list(model.states),
        "outcome_order": list(model.outcomes),
        "action_order": list(query.actions),
        "loss_unit": query.loss_unit,
        "prior_risks": prior_risks,
        "current_risk": current_risk,
        "current_argmin": _argmin(query.actions, prior_risks),
        "branches": branches,
        "observed_risk": observed_risk,
        "evsi": evsi,
        "net_value": net_value,
        "acquisition_risks": acquisition_risks,
        "acquisition_argmin": [
            label
            for label in ("act_now", "observe_once")
            if acquisition_risks[label] == acquisition_minimum
        ],
    }


def solve_with_context(
    model_bytes: bytes, query_bytes: bytes, context: RuntimeContext
) -> bytes:
    model, query = decode_inputs(model_bytes, query_bytes)
    record = {
        "schema": "wdl.result.v1",
        "semantics": SEMANTICS,
        "input_bindings": {
            "model_sha256": digest_bytes(model_bytes),
            "query_sha256": digest_bytes(query_bytes),
        },
        "producer": {
            "name": PRODUCER_NAME,
            "version": PRODUCER_VERSION,
            "code_sha256": context.code_sha256,
            "python_version": context.python_version,
        },
        "answer": calculate(model, query),
    }
    return output_bytes(record)


def solve_bytes(model_bytes: bytes, query_bytes: bytes) -> bytes:
    """Public convenience boundary using the current frozen source snapshot."""
    return solve_with_context(model_bytes, query_bytes, runtime_context())
