# Build 2 handoff

## What is ready

Build 2 adds `finite-linear-uncertainty.v1` without changing Build 1. It supports
small exact rational finite polytopes, checked compatibility/incompatibility,
certified scalar ranges, and Bellman §4.3 action identification. The backend is
untrusted candidate search; the checker is exact and independent.

Run from repository root:

```sh
PYTHONPATH=src python -m unittest discover -s tests_build2 -v
PYTHONPATH=src python -O -m unittest discover -s tests_build2 -v
PYTHONPATH=src python examples/build2/change_and_recheck.py
```

Reproduce the dependency with:

```sh
python -m pip install -r requirements-build2.txt
```

## File map

- `BUILD_2_SPEC.md`: authoritative implemented scope and guarantees.
- `BACKEND_INVESTIGATION_BUILD_2.md`: observed backend evidence and selection.
- `src/writ_decision_lab/build2/`: strict decoder, adapter, exact checker,
  orchestration, and fail-closed consumer.
- `fixtures/v2/`: A–H regression inputs.
- `tests_build2/test_build2.py`: positive and adversarial checks.
- `examples/build2/change_and_recheck.py`: independent-byte stale refusal and
  revision sequence.
- `comparison/build2/`: equal-assurance simpler workflow and comparison.
- `BUILD_2_REPORT.md`: results, evidence classification, and judgment.

## Safe extension boundary

Do not add a new result status by trusting a solver code. Add the mathematical
certificate shape to the spec, make the independent checker verify it using
exact arithmetic against original bytes, place a positive case beside a forged
case, and keep missing evidence unresolved.

Do not treat `outer_enclosure` variation as exact-family nonidentification. Do
not infer omitted assumptions. Do not reuse a checked artifact after any model
or query byte change. Do not implement conditional queries unless positivity,
the transformed primal witness, and matching exact dual bounds are all checked.

## Known limitations

- conditional linear-fractional optimization is deferred;
- rational reconstruction is heuristic and may conservatively return unresolved;
- assignment enumeration is exponential and capped at 32 states;
- the backend dependency was reproduced only in this cloud image;
- no external implementation, proof assistant, or real-world data validated the
  code or model semantics;
- the simpler workflow is clearer and answer-equivalent in this tested scope.

No Build 3, Writ integration, PR merge, or real-world ingestion is authorized.

