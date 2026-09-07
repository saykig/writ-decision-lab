"""Fail-closed end-to-end consumer; checked fields are never trusted directly."""

from __future__ import annotations

from types import MappingProxyType

from .checker import check
from .errors import CheckError


def consume(bundle: dict, intended_problem_raw: bytes, intended_query_raw: bytes, checker=check) -> MappingProxyType:
    try:
        checked = checker(bundle, intended_problem_raw, intended_query_raw)
    except Exception as exc:
        raise CheckError("consumer_refused_unchecked_or_stale_result") from exc
    if checked.status == "unresolved":
        return MappingProxyType({"display": "unresolved", "reason": checked.conclusion["reason"]})
    return MappingProxyType({"display": checked.status, "family_kind": checked.family_kind, "conclusion": checked.conclusion})

