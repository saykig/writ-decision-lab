"""Immutable mathematical and checking data types."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Mapping
from types import MappingProxyType

from .errors import Diagnostic


@dataclass(frozen=True)
class Model:
    states: tuple[str, ...]
    outcomes: tuple[str, ...]
    prior: tuple[Fraction, ...]
    likelihood: tuple[tuple[Fraction, ...], ...]


@dataclass(frozen=True)
class Query:
    state_order: tuple[str, ...]
    actions: tuple[str, ...]
    losses: tuple[tuple[Fraction, ...], ...]
    loss_unit: str
    cost: Fraction


@dataclass(frozen=True)
class RuntimeContext:
    code_sha256: str
    python_version: str


def _snapshot(value: Any) -> Any:
    """Detach and recursively freeze JSON data against ordinary caller mutation."""
    if isinstance(value, Mapping):
        return MappingProxyType({key: _snapshot(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_snapshot(item) for item in value)
    return value


@dataclass(frozen=True)
class CheckReport:
    record: Mapping[str, Any]
    status: str
    diagnostics: tuple[Diagnostic, ...]
    policy_count: int | None

    def __post_init__(self) -> None:
        object.__setattr__(self, "record", _snapshot(self.record))


@dataclass(frozen=True)
class CheckedAnswer:
    """Answer exposed only after fresh checking in this trusted process."""

    answer: Mapping[str, Any]
    model_sha256: str
    query_sha256: str
    result_sha256: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "answer", _snapshot(self.answer))

    def summary(self) -> dict[str, Any]:
        return {
            "schema": "wdl.consumer-summary.v1",
            "semantics": "finite-one-observation.v1",
            "current_argmin": list(self.answer["current_argmin"]),
            "evsi": self.answer["evsi"],
            "acquisition_argmin": list(self.answer["acquisition_argmin"]),
        }
