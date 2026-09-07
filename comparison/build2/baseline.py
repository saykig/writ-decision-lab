"""Equal-assurance simpler direct workflow for Build 2.

It intentionally reuses the identical decoder, candidate backend, exact checker,
and fail-closed consumer. Its difference is orchestration: no reusable engine
facade and no additional result abstraction beyond the checked snapshot.
"""

from writ_decision_lab.build2 import backend
from writ_decision_lab.build2.checker import check
from writ_decision_lab.build2.consumer import consume
from writ_decision_lab.build2.engine import _unresolved
from writ_decision_lab.build2.model import decode_problem, decode_query


def run(problem_raw: bytes, query_raw: bytes, search=backend.search):
    problem = decode_problem(problem_raw)
    query = decode_query(query_raw, problem.dimension)
    try:
        bundle = search(problem_raw, query_raw, problem, query)
    except Exception:
        bundle = _unresolved(problem_raw, query_raw, problem, query, "backend_exception")
    try:
        checked = check(bundle, problem_raw, query_raw)
    except Exception:
        bundle = _unresolved(problem_raw, query_raw, problem, query, "candidate_evidence_failed_exact_check")
        checked = check(bundle, problem_raw, query_raw)
    displayed = consume(bundle, problem_raw, query_raw)
    return bundle, checked, displayed

