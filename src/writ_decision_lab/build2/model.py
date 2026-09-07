"""Decode the additive finite-linear-uncertainty.v1 profile."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any

from .errors import InputError
from .exact import loads_strict, rational, require_keys, vector

SEMANTICS = "finite-linear-uncertainty.v1"
MAX_STATES = 32
MAX_CONSTRAINTS = 128
MAX_ACTIONS = 16


@dataclass(frozen=True)
class LinearConstraint:
    label: str
    coefficients: tuple[Fraction, ...]
    rhs: Fraction


@dataclass(frozen=True)
class Problem:
    semantics: str
    family_kind: str
    family_label: str
    states: tuple[str, ...]
    equalities: tuple[LinearConstraint, ...]
    inequalities: tuple[LinearConstraint, ...]

    @property
    def dimension(self) -> int:
        return len(self.states)


@dataclass(frozen=True)
class Query:
    semantics: str
    operation: str
    label: str
    coefficients: tuple[Fraction, ...] = ()
    actions: tuple[tuple[str, tuple[Fraction, ...]], ...] = ()
    event: tuple[Fraction, ...] = ()
    numerator: tuple[Fraction, ...] = ()


def _label(value: Any, where: str) -> str:
    if not isinstance(value, str) or not value or len(value) > 128:
        raise InputError(f"invalid_label:{where}")
    return value


def _constraints(values: Any, n: int, where: str) -> tuple[LinearConstraint, ...]:
    if not isinstance(values, list):
        raise InputError(f"invalid_constraints:{where}")
    if len(values) > MAX_CONSTRAINTS:
        raise InputError(f"constraint_limit:{where}")
    result = []
    labels: set[str] = set()
    for index, item in enumerate(values):
        if not isinstance(item, dict):
            raise InputError(f"invalid_constraint:{where}[{index}]")
        require_keys(item, {"label", "coefficients", "rhs"})
        label = _label(item["label"], f"{where}[{index}].label")
        if label in labels:
            raise InputError(f"duplicate_constraint_label:{label}")
        labels.add(label)
        result.append(LinearConstraint(label, vector(item["coefficients"], n, f"{where}[{index}].coefficients"), rational(item["rhs"], f"{where}[{index}].rhs")))
    return tuple(result)


def decode_problem(raw: bytes) -> Problem:
    obj = loads_strict(raw)
    require_keys(obj, {"semantics", "family_kind", "family_label", "states", "normalization", "equalities", "inequalities"})
    if obj["semantics"] != SEMANTICS:
        raise InputError("unsupported_semantics")
    if obj["family_kind"] not in {"exact_family", "outer_enclosure"}:
        raise InputError("invalid_family_kind")
    if obj["normalization"] != "exact_one":
        raise InputError("normalization_must_be_exact_one")
    if not isinstance(obj["states"], list) or not 1 <= len(obj["states"]) <= MAX_STATES:
        raise InputError("state_limit_or_type")
    states = tuple(_label(v, f"states[{i}]") for i, v in enumerate(obj["states"]))
    if len(set(states)) != len(states):
        raise InputError("duplicate_state_label")
    equalities = _constraints(obj["equalities"], len(states), "equalities")
    inequalities = _constraints(obj["inequalities"], len(states), "inequalities")
    all_labels = [c.label for c in equalities + inequalities]
    if len(set(all_labels)) != len(all_labels):
        raise InputError("duplicate_constraint_label")
    normalization = LinearConstraint("__normalization__", (Fraction(1),) * len(states), Fraction(1))
    return Problem(SEMANTICS, obj["family_kind"], _label(obj["family_label"], "family_label"), states, (normalization,) + equalities, inequalities)


def decode_query(raw: bytes, n: int) -> Query:
    obj = loads_strict(raw)
    if obj.get("semantics") != SEMANTICS:
        raise InputError("unsupported_semantics")
    operation = obj.get("operation")
    if operation == "compatibility":
        require_keys(obj, {"semantics", "operation", "label"})
        return Query(SEMANTICS, operation, _label(obj["label"], "label"))
    if operation == "linear_range":
        require_keys(obj, {"semantics", "operation", "label", "coefficients"})
        return Query(SEMANTICS, operation, _label(obj["label"], "label"), coefficients=vector(obj["coefficients"], n, "coefficients"))
    if operation == "decision":
        require_keys(obj, {"semantics", "operation", "label", "actions"})
        actions_obj = obj["actions"]
        if not isinstance(actions_obj, list) or not 1 <= len(actions_obj) <= MAX_ACTIONS:
            raise InputError("action_limit_or_type")
        actions = []
        labels: set[str] = set()
        for index, action in enumerate(actions_obj):
            if not isinstance(action, dict):
                raise InputError(f"invalid_action:{index}")
            require_keys(action, {"label", "losses"})
            label = _label(action["label"], f"actions[{index}].label")
            if label in labels:
                raise InputError(f"duplicate_action_label:{label}")
            labels.add(label)
            actions.append((label, vector(action["losses"], n, f"actions[{index}].losses")))
        return Query(SEMANTICS, operation, _label(obj["label"], "label"), actions=tuple(actions))
    if operation == "conditional_range":
        require_keys(obj, {"semantics", "operation", "label", "event", "numerator"})
        return Query(SEMANTICS, operation, _label(obj["label"], "label"), event=vector(obj["event"], n, "event"), numerator=vector(obj["numerator"], n, "numerator"))
    raise InputError("unsupported_operation")

