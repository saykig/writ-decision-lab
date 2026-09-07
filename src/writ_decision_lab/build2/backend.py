"""Approximate candidate search using SciPy/HiGHS; never a source of truth."""

from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
from typing import Iterable

try:
    from scipy.optimize import linprog
except ImportError:  # checker-only installations remain usable
    linprog = None

from .exact import fraction_text
from .model import Problem, Query

BACKEND_ID = "scipy-1.17.0-highs-candidate-search"
MAX_DENOMINATOR = 10**9


def _f(value: float) -> Fraction:
    if abs(value) < 1e-10:
        return Fraction(0)
    return Fraction(float(value)).limit_denominator(MAX_DENOMINATOR)


def _texts(values: Iterable[Fraction]) -> list[str]:
    return [fraction_text(v) for v in values]


def _mat(problem: Problem):
    A = [[float(x) for x in row.coefficients] for row in problem.equalities]
    b = [float(row.rhs) for row in problem.equalities]
    C = [[float(x) for x in row.coefficients] for row in problem.inequalities]
    d = [float(row.rhs) for row in problem.inequalities]
    return A, b, C or None, d or None


def _primal(problem: Problem, objective: tuple[Fraction, ...]):
    if linprog is None:
        raise RuntimeError("scipy_backend_unavailable")
    A, b, C, d = _mat(problem)
    return linprog(
        [float(x) for x in objective],
        A_ub=C,
        b_ub=d,
        A_eq=A,
        b_eq=b,
        bounds=[(0, None)] * problem.dimension,
        method="highs",
    )


def _upper_certificate(problem: Problem, objective: tuple[Fraction, ...]):
    """Search for y free, z>=0: A^T y + C^T z >= objective."""
    if linprog is None:
        raise RuntimeError("scipy_backend_unavailable")
    m, k, n = len(problem.equalities), len(problem.inequalities), problem.dimension
    c = []
    for row in problem.equalities:
        c.append(float(row.rhs))
    for row in problem.equalities:
        c.append(float(-row.rhs))
    for row in problem.inequalities:
        c.append(float(row.rhs))
    aub = []
    bub = []
    for j in range(n):
        aub.append(
            [-float(problem.equalities[i].coefficients[j]) for i in range(m)]
            + [float(problem.equalities[i].coefficients[j]) for i in range(m)]
            + [-float(problem.inequalities[i].coefficients[j]) for i in range(k)]
        )
        bub.append(float(-objective[j]))
    result = linprog(c, A_ub=aub, b_ub=bub, bounds=[(0, None)] * (2 * m + k), method="highs")
    if not result.success:
        return None
    raw = [_f(x) for x in result.x]
    y = tuple(raw[i] - raw[m + i] for i in range(m))
    z = tuple(raw[2 * m + i] for i in range(k))
    bound = sum(row.rhs * yi for row, yi in zip(problem.equalities, y)) + sum(
        row.rhs * zi for row, zi in zip(problem.inequalities, z)
    )
    return {"y": _texts(y), "z": _texts(z), "bound": fraction_text(bound)}


def _farkas(problem: Problem):
    if linprog is None:
        raise RuntimeError("scipy_backend_unavailable")
    m, k, n = len(problem.equalities), len(problem.inequalities), problem.dimension
    c = [0.0] * (2 * m + k)
    aub, bub = [], []
    for j in range(n):
        aub.append(
            [-float(problem.equalities[i].coefficients[j]) for i in range(m)]
            + [float(problem.equalities[i].coefficients[j]) for i in range(m)]
            + [-float(problem.inequalities[i].coefficients[j]) for i in range(k)]
        )
        bub.append(0.0)
    aub.append(
        [float(problem.equalities[i].rhs) for i in range(m)]
        + [-float(problem.equalities[i].rhs) for i in range(m)]
        + [float(problem.inequalities[i].rhs) for i in range(k)]
    )
    bub.append(-1.0)
    result = linprog(c, A_ub=aub, b_ub=bub, bounds=[(0, None)] * (2 * m + k), method="highs")
    if not result.success:
        return None
    raw = [_f(x) for x in result.x]
    y = tuple(raw[i] - raw[m + i] for i in range(m))
    z = tuple(raw[2 * m + i] for i in range(k))
    value = sum(row.rhs * yi for row, yi in zip(problem.equalities, y)) + sum(
        row.rhs * zi for row, zi in zip(problem.inequalities, z)
    )
    return {"y": _texts(y), "z": _texts(z), "contradiction": fraction_text(value)}


def _endpoint(problem: Problem, objective: tuple[Fraction, ...], sense: str):
    sign = Fraction(1) if sense == "min" else Fraction(-1)
    solved = _primal(problem, tuple(sign * x for x in objective))
    if not solved.success or solved.x is None:
        return None
    witness = tuple(_f(x) for x in solved.x)
    value = sum(c * p for c, p in zip(objective, witness))
    if sense == "max":
        certificate = _upper_certificate(problem, objective)
    else:
        upper_for_negative = _upper_certificate(problem, tuple(-x for x in objective))
        if upper_for_negative is None:
            certificate = None
        else:
            certificate = {
                "y": _texts(-Fraction(x) for x in map(Fraction, upper_for_negative["y"])),
                "z": _texts(-Fraction(x) for x in map(Fraction, upper_for_negative["z"])),
                "bound": fraction_text(-Fraction(upper_for_negative["bound"])),
            }
    if certificate is None:
        return None
    return {"witness": _texts(witness), "objective": fraction_text(value), "certificate": certificate}


def _base(problem_raw: bytes, query_raw: bytes, problem: Problem, query: Query) -> dict:
    return {
        "schema": "finite-linear-uncertainty-result.v1",
        "operation": query.operation,
        "model_sha256": sha256(problem_raw).hexdigest(),
        "query_sha256": sha256(query_raw).hexdigest(),
        "family_kind": problem.family_kind,
        "backend": BACKEND_ID,
    }


def search(problem_raw: bytes, query_raw: bytes, problem: Problem, query: Query) -> dict:
    """One adapter invocation. It may solve the finite batch needed by the operation."""
    out = _base(problem_raw, query_raw, problem, query)
    if query.operation == "conditional_range":
        out.update(
            status="unresolved",
            reason="conditioning_event_impossible" if all(v == 0 for v in query.event) else "conditional_profile_deferred",
            evidence={},
        )
        return out

    zero = (Fraction(0),) * problem.dimension
    feasible = _primal(problem, zero)
    if not feasible.success:
        certificate = _farkas(problem)
        if certificate is None:
            out.update(status="unresolved", reason="absent_exact_infeasibility_certificate", evidence={})
        else:
            out.update(status="incompatible", evidence={"farkas": certificate})
        return out

    feasibility_witness = tuple(_f(x) for x in feasible.x)
    if query.operation == "compatibility":
        out.update(status="compatible", evidence={"witness": _texts(feasibility_witness)})
        return out

    if query.operation == "linear_range":
        low = _endpoint(problem, query.coefficients, "min")
        high = _endpoint(problem, query.coefficients, "max")
        if low is None or high is None:
            out.update(status="unresolved", reason="absent_exact_endpoint_certificate", evidence={})
        else:
            status = "identified" if low["objective"] == high["objective"] else "partially_identified"
            out.update(status=status, evidence={"minimum": low, "maximum": high})
        return out

    if query.operation == "decision":
        pairs = []
        for a_label, a_loss in query.actions:
            for b_label, b_loss in query.actions:
                if a_label == b_label:
                    continue
                endpoint = _endpoint(problem, tuple(x - y for x, y in zip(a_loss, b_loss)), "max")
                if endpoint is None:
                    out.update(status="unresolved", reason="absent_exact_action_certificate", evidence={})
                    return out
                pairs.append({"action": a_label, "competitor": b_label, "maximum_difference": endpoint})
        out.update(status="decision_candidate", evidence={"pairs": pairs})
        return out
    raise AssertionError("decoded operation not handled")
