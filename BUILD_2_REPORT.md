BUILD2_CAPABILITY_ESTABLISHED

# Build 2 report

## Outcome

Build 2 establishes the bounded requested capability for small finite rational
linear uncertainty families. Compatibility, infeasibility, linear extrema, and
decision-relative identification are exposed only when exact independently
checked evidence supports them. Unsupported or uncertified computations return
`unresolved`. The optional conditional-query operation is explicitly deferred
rather than weakened.

This status means only that the implementation and its specified regression
evidence exist. It does not establish formal verification, mathematical novelty,
scientific acceptance, real-world model validity, productivity, cumulative
knowledge, or Writ integration.

## Comparative judgment

**Engineering judgment, high confidence within the test scope:** the competent
simpler workflow is clearer and produces equivalent checked answers. The
structured engine earns a reusable backend/checker/consumer boundary and
immutable byte-bound artifacts, but not stronger mathematics. There is no scalar
score. Evidence and qualifications are in
`comparison/build2/COMPARISON.md`.

This judgment would change if repeated independent consumers or a replacement
exact backend showed materially lower safeguard duplication or fewer stale-use
failures through the structured interface.

## Implemented results

- A: Bellman's binary triangle is `incompatible` with an exact checked
  Farkas-style contradiction.
- B: consistent `P(X,Y)` and `P(Y,Z)` are `compatible` with an exact eight-cell
  joint witness. Conditional independence is documented only as one Bellman
  construction, not inferred.
- C: `P(theta=1)=1/3` is `identified` with matching primal/dual certificates.
- D: `[1/4,3/4]` is `partially_identified` with two exact endpoint models and
  certified extrema.
- E: the supplied exact Bellman posterior family is `[4/7,8/11]`, while
  `predict_1` is uniformly strictly optimal under zero-one loss; the checked
  worst pairwise difference is `-1/7`, equivalent to the minimum strict gap
  `1/7`.
- F: changed asymmetric losses invalidate the old byte-bound result and make the
  decision model-dependent, with disagreement witnesses. The old result still
  checks under the old query.
- G: the exact family is identified at `1/2`; its larger declared outer
  enclosure varies over `[1/4,3/4]`. The implementation does not transfer outer
  variation to the exact family.
- H: missing exact certificate, backend exception, checker exception, deferred
  conditioning, and impossible conditioning paths fail closed or return
  unresolved as specified.

## Architecture evidence

The approximate SciPy/HiGHS backend searches once per requested operation and
may execute the finite LP batch needed for that operation. The exact checker
does not call the backend. It parses the independently supplied original bytes,
recomputes every constraint and objective with `fractions.Fraction`, verifies
Farkas or dual inequalities, and requires exact primal/dual agreement. The
consumer calls that checker afresh before display.

The backend investigation directly observed SciPy 1.17.0 and the absence of an
infeasibility-certificate field in its infeasible `linprog` result. SoPlex was
not installed. Upstream source reports make SoPlex a credible future exact
candidate, but its certificate interface was not reproduced here. See
`BACKEND_INVESTIGATION_BUILD_2.md`.

## Test evidence

Final reviewed-state commands and exact results:

- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m unittest discover -s
  tests_build2 -v` — 39 tests passed in 0.622 seconds.
- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -O -m unittest discover -s
  tests_build2 -v` — 39 tests passed in 0.649 seconds.
- `PYTHONPATH=src python examples/build2/change_and_recheck.py` — completed;
  stale reuse refused, new maximum changed from `3/4` to `1/2`, and the old
  checked result remained valid under the old bytes.
- `PYTHONPATH=src python -m compileall -q src comparison/build2 examples/build2
  tests_build2` — completed without error.

The suite includes positive controls beside malformed/noncanonical rationals,
duplicate labels and JSON keys, dimension mismatch, unsupported semantics,
stale family/query bytes, coherent false bundles, forged multipliers, witnesses
violating constraints, invalid Farkas evidence, primal/dual disagreement,
changed queries and families, impossible conditioning, endpoint ties, snapshot
mutation, backend/checker exceptions, absent certificates, relocation, and both
normal and optimized Python execution.

## Evidence classification

| Classification | Claims |
|---|---|
| Directly observed | PR #1 merged at `c85aebd79b455e84535a276ec78222064a66c5d0`; pinned Bellman files were inspected; cloud backend/package probes; exact fixture outputs; test and example executions recorded above once finalized |
| Mathematically derived from pinned Bellman | Polytope semantics, checked Farkas sufficiency, primal/dual endpoint conditions, pairwise action-risk criterion, posterior endpoints and `1/7` action margin |
| Inherited/source-reported | Bellman's broader programme standing; upstream SoPlex exact-rational features and Apache-2.0 license; upstream HiGHS packaging and MIT license |
| Engineering judgment | SciPy as an untrusted search adapter is fit for this bounded build when all conclusions are independently exact-checked; the simpler workflow is clearer/equivalent; confidence high in tested scope |
| Hypothesis | A packaged exact backend may reduce unresolved rational-reconstruction cases without changing the checker contract; repeated consumers may make the structured boundary more valuable |

## Limitations

- Conditional linear-fractional certification is deferred. Fixture E consumes a
  separately supplied exact posterior family after Bellman's derivation.
- Floating candidate search plus bounded rational reconstruction can fail on
  valid problems; that yields unresolved, not a false mathematical status.
- Limits are 32 state cells, 128 equalities, 128 inequalities, 16 actions, and
  256 KiB per JSON input. Enumeration can be exponential before these files
  reach the tool.
- Only rational linear constraints are supported. Nonlinear independence,
  causal, rank, sequential, acquisition, statistical coverage, strategic, and
  authority semantics are absent.
- Tests are authored regression/adversarial checks, not independent review or
  formal verification.
- No real-world data were ingested and no Writ repository or frozen Build 1
  artifact was modified.
