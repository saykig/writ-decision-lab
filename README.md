# Writ Decision Lab

Writ Decision Lab is a bounded research implementation for exact, consequential-decision
calculations. It currently contains three related slices:

- **Build 1:** finite expected-loss minimization with the choice to act now or obtain one
  observation and then act;
- **Build 2:** compatible-evidence and partial-identification calculations backed by an untrusted
  numerical candidate generator and an independent exact checker; and
- **certificate transport:** revalidation of a Bellman certificate after an explicitly supplied
  model or policy change.

The project is adjacent to Writ, but it is not a Writ record family, has no Writ runtime dependency,
and does not modify Writ production files.

## Repository map

| Path | Purpose |
| --- | --- |
| `src/writ_decision_lab/` | Active Python package, including Build 1, Build 2, and transport code |
| `tests/` | All active unit, adversarial, regression, and integration tests |
| `fixtures/` | Versioned Build 1 and Build 2 input fixtures |
| `examples/` | Runnable consumer, Build 2, weak-model, and transport examples |
| `comparison/` | Active equal-information/equal-assurance comparison programs |
| `docs/` | Specifications, reports, handoffs, reviews, and source notes; see [`docs/README.md`](docs/README.md) |
| `evidence/` | Preserved PR #1 repair and snapshot evidence |
| `outputs/` | Final checked Build 1 demonstration artifacts |
| `sources/` | Current external engineering-direction source material |
| `requirements/` | Optional dependency sets, currently Build 2's SciPy pin |
| `archive/` | Retired experiments, preliminary artifacts, instructions, and review inputs; see [`archive/README.md`](archive/README.md) |

## Set up and test

Build 1 and certificate transport require CPython 3.13. Build 2 additionally requires the pinned
SciPy backend:

```bash
python3.13 -m pip install -r requirements/build2.txt
export PYTHONPATH=src
python3.13 -m unittest discover -s tests -v
python3.13 -O -m unittest discover -s tests -v
```

The producer uses posterior-based calculation. The Build 1 checker does not import the producer
math; it uses direct joint-mass identities and exhaustively enumerates terminal policies. A consumer
must supply the model and query bytes it intends and call `check_and_load` before using an answer.
A saved check record is never accepted as authority.

## Build 1 quick start

Outputs are creation-only, so use a fresh directory for each run:

```bash
export PYTHONPATH=src
run_dir=$(mktemp -d)
python3.13 -m writ_decision_lab solve \
  --model examples/weak/model.json --query examples/weak/query.json \
  --output "$run_dir/result.json"
python3.13 -m writ_decision_lab check \
  --model examples/weak/model.json --query examples/weak/query.json \
  --result "$run_dir/result.json" --output "$run_dir/check.json"
python3.13 examples/consume_answer.py \
  --expected-model examples/weak/model.json \
  --expected-query examples/weak/query.json \
  --result "$run_dir/result.json" --output "$run_dir/consumer.json"
python3.13 comparison/run_sequence.py --output "$run_dir/comparison.json"
```

The public Build 1 Python interface is:

```python
from writ_decision_lab import check_and_load, check_bytes, solve_bytes
```

See the [Build 1 specification](docs/specifications/build1.md),
[report](docs/reports/build1.md), and [handoff](docs/handoffs/build1.md) for the frozen contract,
evidence, and continuation guidance.

## Certificate transport/revalidation

The bounded transport adapter distinguishes ordinary target-certificate validity from the stronger
anchored-transport warrant. Its mathematical authority and limits are pinned in the
[certificate transport specification](docs/specifications/certificate-transport.md).

```bash
export PYTHONPATH=src
run_dir=$(mktemp -d)
python3.13 -m writ_decision_lab.transport solve \
  --request examples/transport/comparator-change-request.json \
  --output "$run_dir/transport-evidence.json"
python3.13 -m writ_decision_lab.transport check \
  --request examples/transport/comparator-change-request.json \
  --evidence "$run_dir/transport-evidence.json" \
  --output "$run_dir/transport-check.json"
```

`checked` is conditional on the supplied bytes, documented semantics, and checker/runtime. It is
not source validation, scientific acceptance, a formal proof, or permission to compose separately
checked results.
