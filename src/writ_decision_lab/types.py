"""Immutable mathematical and checking data types."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Mapping

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


@dataclass(frozen=True)
class CheckReport:
    record: Mapping[str, Any]
    status: str
    diagnostics: tuple[Diagnostic, ...]
    policy_count: int | None


@dataclass(frozen=True)
class CheckedAnswer:
    """Answer exposed only after fresh checking in this trusted process."""

    answer: Mapping[str, Any]
    model_sha256: str
    query_sha256: str
    result_sha256: str

    def summary(self) -> dict[str, Any]:
        return {
            "schema": "wdl.consumer-summary.v1",
            "semantics": "finite-one-observation.v1",
            "current_argmin": list(self.answer["current_argmin"]),
            "evsi": self.answer["evsi"],
            "acquisition_argmin": list(self.answer["acquisition_argmin"]),
        }
