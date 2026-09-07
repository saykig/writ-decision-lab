"""Competent ordinary-script baseline using exact arithmetic and equal inputs.

This module intentionally does not import ``writ_decision_lab``. It keeps a small
input-binding and fresh-recalculation safeguard in the ordinary script itself.
"""

from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
import re
from typing import Any


RATIONAL = re.compile(r"(?:0|-?[1-9][0-9]*)/[1-9][0-9]*\Z")


class BaselineFailure(Exception):
    def __init__(self, status: str):
        super().__init__(status)
        self.status = status


def _digest(value: bytes) -> str:
    return "sha256:" + sha256(value).hexdigest()


def _rat(value: Any) -> Fraction:
    if not isinstance(value, str) or not RATIONAL.fullmatch(value):
        raise BaselineFailure("invalid_input")
    numerator, denominator = value.split("/")
    if len(numerator.lstrip("-")) > 32 or len(denominator) > 32:
        raise BaselineFailure("out_of_scope")
    result = Fraction(int(numerator), int(denominator))
    if f"{result.numerator}/{result.denominator}" != value:
        raise BaselineFailure("invalid_input")
    return result


def _wire(value: Any) -> Any:
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, dict):
        return {key: _wire(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_wire(item) for item in value]
    return value


def _encoded(value: Any) -> bytes:
    return (json.dumps(_wire(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("ascii")


def _inputs(model_bytes: bytes, query_bytes: bytes) -> tuple[dict[str, Any], dict[str, Any], list[Fraction], list[list[Fraction]], list[list[Fraction]], Fraction]:
    try:
        model = json.loads(model_bytes)
        query = json.loads(query_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise BaselineFailure("invalid_input")
    if set(model) != {"schema", "states", "outcomes", "prior", "likelihood"}:
        raise BaselineFailure("invalid_input")
    if set(query) != {"schema", "semantics", "state_order", "actions", "losses", "loss_unit", "cost"}:
        raise BaselineFailure("invalid_input")
    if model["schema"] != "wdl.model.v1" or query["schema"] != "wdl.query.v1":
        raise BaselineFailure("out_of_scope")
    if query["semantics"] != "finite-one-observation.v1":
        raise BaselineFailure("out_of_scope")
    if query["state_order"] != model["states"]:
        raise BaselineFailure("invalid_input")
    states, outcomes, actions = model["states"], model["outcomes"], query["actions"]
    if not 1 <= len(states) <= 8 or not 1 <= len(outcomes) <= 6 or not 1 <= len(actions) <= 8:
        raise BaselineFailure("out_of_scope")
    if len(actions) ** len(outcomes) > 4096:
        raise BaselineFailure("out_of_scope")
    prior = list(map(_rat, model["prior"]))
    likelihood = [[_rat(item) for item in row] for row in model["likelihood"]]
    losses = [[_rat(item) for item in row] for row in query["losses"]]
    cost = _rat(query["cost"])
    if len(prior) != len(states) or len(likelihood) != len(states) or any(len(row) != len(outcomes) for row in likelihood):
        raise BaselineFailure("invalid_input")
    if len(losses) != len(actions) or any(len(row) != len(states) for row in losses):
        raise BaselineFailure("invalid_input")
    if any(item < 0 for item in prior) or sum(prior, Fraction(0)) != 1:
        raise BaselineFailure("invalid_input")
    if any(any(item < 0 for item in row) or sum(row, Fraction(0)) != 1 for row in likelihood):
        raise BaselineFailure("invalid_input")
    if cost < 0:
        raise BaselineFailure("invalid_input")
    return model, query, prior, likelihood, losses, cost


def _compute(model_bytes: bytes, query_bytes: bytes) -> dict[str, Any]:
    model, query, prior, likelihood, losses, cost = _inputs(model_bytes, query_bytes)
    ns, nx, na = len(prior), len(model["outcomes"]), len(query["actions"])
    prior_risks = [sum((prior[s] * losses[a][s] for s in range(ns)), Fraction(0)) for a in range(na)]
    current = min(prior_risks)
    branches = []
    observed = Fraction(0)
    for x in range(nx):
        joint = [prior[s] * likelihood[s][x] for s in range(ns)]
        mass = sum(joint, Fraction(0))
        if mass == 0:
            branches.append({"outcome": model["outcomes"][x], "status": "impossible", "mass": Fraction(0), "posterior": None, "risks": None, "minimum_risk": None, "argmin": None})
            continue
        posterior = [value / mass for value in joint]
        risks = [sum((posterior[s] * losses[a][s] for s in range(ns)), Fraction(0)) for a in range(na)]
        minimum = min(risks)
        observed += mass * minimum
        branches.append({"outcome": model["outcomes"][x], "status": "possible", "mass": mass, "posterior": posterior, "risks": risks, "minimum_risk": minimum, "argmin": [query["actions"][a] for a in range(na) if risks[a] == minimum]})
    evsi = current - observed
    acquisition = {"act_now": current, "observe_once": observed + cost}
    acquisition_minimum = min(acquisition.values())
    return _wire({
        "state_order": model["states"], "outcome_order": model["outcomes"], "action_order": query["actions"],
        "loss_unit": query["loss_unit"], "prior_risks": prior_risks, "current_risk": current,
        "current_argmin": [query["actions"][a] for a in range(na) if prior_risks[a] == current],
        "branches": branches, "observed_risk": observed, "evsi": evsi, "net_value": evsi - cost,
        "acquisition_risks": acquisition,
        "acquisition_argmin": [name for name in ("act_now", "observe_once") if acquisition[name] == acquisition_minimum],
    })


def produce(model_bytes: bytes, query_bytes: bytes) -> bytes:
    return _encoded({
        "model_sha256": _digest(model_bytes),
        "query_sha256": _digest(query_bytes),
        "answer": _compute(model_bytes, query_bytes),
    })


def consume(model_bytes: bytes, query_bytes: bytes, result_bytes: bytes) -> dict[str, Any]:
    _inputs(model_bytes, query_bytes)
    try:
        result = json.loads(result_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise BaselineFailure("invalid_input")
    if set(result) != {"model_sha256", "query_sha256", "answer"}:
        raise BaselineFailure("invalid_input")
    if result["model_sha256"] != _digest(model_bytes) or result["query_sha256"] != _digest(query_bytes):
        raise BaselineFailure("input_mismatch")
    # The ordinary script's safeguard is a fresh full recalculation with the same implementation.
    if result["answer"] != _compute(model_bytes, query_bytes):
        raise BaselineFailure("computation_mismatch")
    return result["answer"]
