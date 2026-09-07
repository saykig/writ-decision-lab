# Build 1 handoff

## Outcome

The complete isolated Build 1 implementation works under CPython 3.13.15. The behavior and
foundation gates pass: exact fixture answers check, hostile mutations fail, and the separate
consumer uses only the public fresh-check interface. The equal-information ordinary script also
passes all eight comparison steps with fewer maintained lines, so the present recommendation is to
prefer the simpler workflow while retaining this tested implementation and its fixtures.

This is not a failure of the mathematical substrate. It is a stopping decision about current
wrapper cost and demonstrated benefit.

## Location and boundary

- Build: `/Users/kimchee/Documents/writ-decision-lab-build1`
- Writ baseline observed before build: `034a51edf6e716f89102d589a6f2c8c4d11a2cf2`
- Writ production files changed: none
- Remote state, package publication, deployment, branch, and pull request: none

## Re-run from frozen source

Use a fresh output directory because artifact writes are creation-only.

```bash
cd /Users/kimchee/Documents/writ-decision-lab-build1
export PATH=/opt/homebrew/opt/python@3.13/libexec/bin:$PATH
export PYTHONPATH=src
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -v
python comparison/run_sequence.py --output outputs/comparison-rerun.json
```

The exact acceptance CLI is in `README.md`. `outputs/weak/` contains the final solve/check/consumer
demonstration and `outputs/comparison.json` contains the measured eight-step comparison.

## Consumer rule

Pass independently chosen model/query bytes plus result bytes to `check_and_load`. Use only the
returned `CheckedAnswer`. Do not pass a saved `check.json` as permission, trust the hashes declared
by a result without recomputation, or carry an answer into a changed question. Status
`input_mismatch` does not refute the result under its original inputs; it refuses reuse under the
new intended pair.

## Mathematical stopping boundary

The sole object is the supplied finite model/query pair, and the sole operation is exact act-now
versus one-observation expected-loss evaluation. `checked` is conditional whole-answer agreement
under that profile. There is no theorem justifying composition of separately checked results. Do
not add evidence-dependence, causal, robust-decision, graph, ontology, sequential observation, or
other Bellman machinery under `finite-one-observation.v1`.

A future Bellman extension must use a new semantics version and prove or explicitly specify its new
composition rules while leaving this version's meaning unchanged.

## Known limitations and next gate

- Same author, parser, rational library, and specification are shared by producer/checker; this is
  not independent replication or formal proof.
- The baseline comparison is unblinded, same-author, trivial-duration, and captures no measured
  human effort. It establishes mechanism behavior, not productivity.
- Exact raw-byte identity is intentionally conservative and does not assert mathematical
  inequivalence when only whitespace changes.
- Operational bounds are deterministic, not comprehensive denial-of-service guarantees.
- No source fidelity, real-world assumption, cross-question sufficiency, scientific acceptance,
  or external-system interoperability has been established.

After three suitable real research tasks, reassess actual reuse and maintenance without bending
tasks to fit this profile. Continue the component only if a real consumer values the public checked
boundary; otherwise retain the math/tests/fixtures and use the simpler workflow. Vela or formal
proof work remains deferred until an actual accepted-state or theorem bottleneck warrants it.
