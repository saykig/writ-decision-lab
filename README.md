# Writ Decision Lab

Writ Decision Lab is an isolated research/test-bench repository for bounded mathematical components that can produce candidates and independently check them against exact supplied subjects. It is adjacent to Writ, is not a Writ record family, and does not make scientific, evidentiary, human, or authority claims merely because a mathematical check passes.

## Current executable slices

### Builds 1–2 — finite static uncertainty

The existing Build 1 and Build 2 paths cover the repository's finite one-observation and `finite-linear-uncertainty.v1` static decision/compatibility profiles. They remain unchanged by the certificate-transport adapter. See `SPEC.md`, `BUILD_1_REPORT.md`, `BUILD_2_SPEC.md`, `BUILD_2_REPORT.md`, and the existing handoff documents for their exact boundaries.

### Certificate transport/revalidation — sequential guarantee revision

The bounded adapter implements one hardened Bellman capability: after an explicit model or policy change on the same completed observable-history skeleton, construct a new target sequential certificate and independently check both ordinary target validity and the claimed anchored transport from the old checked certificate.

Mathematical authority and exact limits are pinned in `CERTIFICATE_TRANSPORT_SPEC.md`.

```bash
export PYTHONPATH=src
python -m writ_decision_lab.transport solve --request examples/transport/comparator-change-request.json --output /tmp/transport-evidence.json
python -m writ_decision_lab.transport check --request examples/transport/comparator-change-request.json --evidence /tmp/transport-evidence.json --output /tmp/transport-check.json
```

The checker does not import the transport producer. Outputs are creation-only.

## Existing Build 1 interface

The original producer uses posterior-based calculation. Its checker does not import the producer math; it uses direct joint-mass identities and exhaustively enumerates terminal policies. A consumer must supply the model and query bytes it intends and call `check_and_load` before using an answer. A saved check record is never accepted as authority.

CPython 3.13 and the standard library are sufficient for Build 1 and certificate transport. Build 2 uses its separately documented SciPy backend.

```bash
export PATH=/opt/homebrew/opt/python@3.13/libexec/bin:$PATH
export PYTHONPATH=src
python --version
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -v
```

## Public Build 1 Python interface

```python
from writ_decision_lab import solve_bytes, check_bytes, check_and_load
```

- `solve_bytes(model_bytes, query_bytes)` produces deterministic `wdl.result.v1` bytes.
- `check_bytes(model_bytes, query_bytes, result_bytes)` returns a `CheckReport` after fresh checking.
- `check_and_load(model_bytes, query_bytes, result_bytes)` returns `CheckedAnswer` only for status `checked`; otherwise it fails closed.

`checked` is conditional on the supplied model/query bytes, the documented semantics, and the checker/runtime. It is not source validation, scientific acceptance, a formal proof, or a rule permitting separately checked results to be composed.
