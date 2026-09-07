"""Producer/checker orchestration with a single backend-adapter invocation."""

from __future__ import annotations

from hashlib import sha256
from typing import Callable

from . import backend
from .checker import CheckedResult, check
from .model import decode_problem, decode_query


def _unresolved(problem_raw: bytes, query_raw: bytes, problem, query, reason: str) -> dict:
    return {
        "schema": "finite-linear-uncertainty-result.v1",
        "operation": query.operation,
        "model_sha256": sha256(problem_raw).hexdigest(),
        "query_sha256": sha256(query_raw).hexdigest(),
        "family_kind": problem.family_kind,
        "backend": backend.BACKEND_ID,
        "status": "unresolved",
        "reason": reason,
        "evidence": {},
    }


def produce(problem_raw: bytes, query_raw: bytes, search: Callable = backend.search) -> dict:
    problem = decode_problem(problem_raw)
    query = decode_query(query_raw, problem.dimension)
    try:
        return search(problem_raw, query_raw, problem, query)
    except Exception:
        return _unresolved(problem_raw, query_raw, problem, query, "backend_exception")


def solve_and_check(problem_raw: bytes, query_raw: bytes, search: Callable = backend.search) -> tuple[dict, CheckedResult]:
    problem = decode_problem(problem_raw)
    query = decode_query(query_raw, problem.dimension)
    try:
        bundle = search(problem_raw, query_raw, problem, query)
    except Exception:
        bundle = _unresolved(problem_raw, query_raw, problem, query, "backend_exception")
    try:
        return bundle, check(bundle, problem_raw, query_raw)
    except Exception:
        fallback = _unresolved(problem_raw, query_raw, problem, query, "candidate_evidence_failed_exact_check")
        return fallback, check(fallback, problem_raw, query_raw)
