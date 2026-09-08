# Writ Decision Lab — Build 1

This isolated local research component implements and checks one exact mathematical operation:
finite expected-loss minimization with the choice to act now or obtain exactly one observation and
then act. It is adjacent to Writ, is not a Writ record family, has no Writ runtime dependency, and
does not modify Writ production files.

The producer uses posterior-based calculation. The checker does not import the producer math; it
uses direct joint-mass identities and exhaustively enumerates terminal policies. A consumer must
supply the model and query bytes it intends and call `check_and_load` before using an answer. A
saved check record is never accepted as authority.

## Run

CPython 3.13 and the standard library are sufficient. On this machine the frozen run used
`/opt/homebrew/bin/python3.13` (3.13.15).

```bash
export PATH=/opt/homebrew/opt/python@3.13/libexec/bin:$PATH
export PYTHONPATH=src
python --version
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -v

mkdir -p outputs/weak
python -m writ_decision_lab solve \
  --model examples/weak/model.json --query examples/weak/query.json \
  --output outputs/weak/result.json
python -m writ_decision_lab check \
  --model examples/weak/model.json --query examples/weak/query.json \
  --result outputs/weak/result.json --output outputs/weak/check.json
python examples/consume_answer.py \
  --expected-model examples/weak/model.json \
  --expected-query examples/weak/query.json \
  --result outputs/weak/result.json --output outputs/weak/consumer.json
python comparison/run_sequence.py --output outputs/comparison.json
```

Outputs are creation-only: commands refuse to overwrite existing artifacts. Use a fresh output
directory for another run.

## Public Python interface

```python
from writ_decision_lab import solve_bytes, check_bytes, check_and_load
```

- `solve_bytes(model_bytes, query_bytes)` produces deterministic `wdl.result.v1` bytes.
- `check_bytes(model_bytes, query_bytes, result_bytes)` returns a `CheckReport` after fresh checking.
- `check_and_load(model_bytes, query_bytes, result_bytes)` returns `CheckedAnswer` only for status
  `checked`; otherwise it fails closed.

`checked` is conditional on the supplied finite model/query bytes, the documented semantics, and
the checker/runtime. It is not source validation, scientific acceptance, a formal proof, or a rule
permitting separately checked results to be composed.

See `SPEC.md` for the frozen contract, `BUILD_1_REPORT.md` for evidence and verdict, and `HANDOFF.md`
for operational continuation guidance.

## Certificate transport/revalidation

A separate bounded adapter implements Bellman's hardened identity-skeleton certificate-transport
construction after an explicitly supplied model or policy change. It does not change Build 1 or
Build 2 semantics. Mathematical authority, exact contracts, and limits are pinned in
`CERTIFICATE_TRANSPORT_SPEC.md`.

```bash
export PYTHONPATH=src
python -m writ_decision_lab.transport solve \
  --request examples/transport/comparator-change-request.json \
  --output /tmp/transport-evidence.json
python -m writ_decision_lab.transport check \
  --request examples/transport/comparator-change-request.json \
  --evidence /tmp/transport-evidence.json \
  --output /tmp/transport-check.json
```

The transport checker does not import its producer. It distinguishes ordinary target-certificate
validity from the stronger anchored-transport warrant.
