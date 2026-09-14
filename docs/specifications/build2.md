# Build 2 mathematical and engineering specification

## Authority and scope

Build 2 is an additive executable profile for small finite rational uncertainty
models. It is derived from Bellman commit
`63a741fce5bb1457f8ae7bf6edbe95dbeaaf52ef`, principally
`BELLMAN_NEXT_MATHEMATICAL_BUILDOUT.md` §§3, 4.1–4.3, and 15, together with
`BELLMAN_NORTH_STAR.md`. The pinned build-out blob is
`0842250b13fdd936986a3ff9ea7d8b7a5754a48f`; the North Star blob is
`88a80df2dd626f3ab0c7e0cf0b9629b2d7f334d2`.

This profile does not replace or modify Build 1's
`finite-one-observation.v1`. It adds `finite-linear-uncertainty.v1` and makes no
Writ integration decision.

## Mathematical object

The caller explicitly labels a finite state/world-assignment list `Omega`. One
probability mass is associated with each list position:

`P = {p >= 0 : A p = b, C p <= d}`,

with exact normalization `1^T p = 1` added by the declared semantics. All
coefficients and right-hand sides are canonical rational strings. The input
must declare either:

- `exact_family`: the listed constraints are asserted to be all constraints of
  the intended family; or
- `outer_enclosure`: the listed family is only a sound relaxation.

No missing independence, conditional independence, stationarity, reliability,
causality, rank, authority, or mechanism constraint is inferred. The family
label is descriptive and does not alter the mathematics.

An exact-family witness proves that the declared finite constraints are jointly
compatible. An outer-enclosure witness proves only that the relaxation is
nonempty. An empty sound outer enclosure proves the enclosed exact family is
empty; a nonempty outer enclosure does not prove that exact family is nonempty.
Variation within an outer enclosure is not evidence of variation within a
smaller exact family.

## Input profile

Problem objects have exactly these fields:

- `semantics`: `finite-linear-uncertainty.v1`;
- `family_kind`: `exact_family` or `outer_enclosure`;
- `family_label`: nonempty string;
- `states`: unique, nonempty labels, dimension 1–32;
- `normalization`: exactly `exact_one`;
- `equalities`, `inequalities`: at most 128 each; every row has a globally
  unique label, a coefficient vector of the exact state dimension, and an exact
  rational right-hand side.

Canonical rationals are reduced strings such as `0`, `-2`, or `3/7`. Decimal
JSON numbers, `2/4`, `01`, `-0`, non-UTF-8, duplicate JSON keys, unknown fields,
and out-of-range integers are malformed input and are not repaired.

Query operations are:

1. `compatibility`;
2. `linear_range`, with one rational coefficient per state;
3. `decision`, with 1–16 uniquely labeled actions and one loss per state;
4. `conditional_range`, syntactically reserved as a separate operation.

## Compatibility guarantee

A result is `compatible` only when the checker verifies an exact rational
`p >= 0`, normalization, every equality, and every inequality.

A result is `incompatible` only when the checker verifies Bellman's Farkas-style
certificate `(y,z)`:

`z >= 0`, `A^T y + C^T z >= 0`, and `b^T y + d^T z < 0`.

If candidate search reports infeasibility but no such certificate survives the
exact checker, the result is `unresolved`. Solver status is never sufficient.

## Linear-query guarantee

For `r^T p`, the backend searches for both endpoints. Each claimed endpoint
must contain:

- an exact feasible primal witness;
- an exact recomputation of the claimed objective;
- an exact dual bound certificate; and
- exact equality of the primal objective and dual bound.

For a maximum, the certificate satisfies `z >= 0`,
`A^T y + C^T z >= r`, with upper bound `b^T y + d^T z`. For a minimum it
satisfies `z <= 0`, `A^T y + C^T z <= r`, giving the lower bound with the same
right-hand expression. Equal checked endpoints return `identified`; different
checked endpoints return `partially_identified` and retain both feasible endpoint
models. There is no midpoint output. Missing or invalid evidence returns
`unresolved`.

## Decision-relative identification

For every ordered action pair `(a,b)`, the checker certifies

`max_{p in P} (loss_a - loss_b)^T p`.

This is Bellman §4.3's pairwise condition. After every ordered pair is checked:

- one action with every comparison strictly below zero is
  `uniformly_strictly_optimal`;
- a unique action with every comparison at most zero is `uniformly_optimal`;
- two or more such actions return their complete
  `complete_common_minimizing_set`;
- no common minimizer is `model_dependent`, with exact witnesses showing each
  excluded action loses somewhere when available;
- an incomplete or invalid pair batch is `unresolved`.

The result is bound to the exact loss-query bytes. A changed loss invalidates
reuse even when the model family is unchanged.

## Conditional-query boundary

`conditional_range` remains a separate operation and is deliberately deferred.
Bellman permits the positive-mass Charnes–Cooper transform only with an exact
certificate over the transformed family. This implementation does not weaken
that condition. A syntactically zero event returns unresolved with
`conditioning_event_impossible`; other requests return unresolved with
`conditional_profile_deferred`.

Fixture E starts after Bellman's supplied positive-mass derivation: the prior
interval and likelihoods give the exact posterior family `[4/7,8/11]`. Build 2
checks that separately supplied posterior family; it does not claim to execute
or certify the upstream fractional transform.

## Producer, checker, and consumer

The SciPy/HiGHS adapter is candidate search only. One adapter invocation produces
the complete operation bundle; its internal finite batch may solve feasibility,
endpoint, dual, or pairwise LPs. The exact checker never calls the backend and
reconstructs the problem and query from caller-supplied original bytes. It
distrusts solver exit status, result fields, declared objectives, and hashes
alone. Hashes bind bytes but do not prove their mathematical content.

Checked snapshots are frozen and recursively detach conclusions from mutable
result bundles. The separate consumer freshly checks the untrusted bundle
against independently supplied intended problem/query bytes before displaying
anything. Checker failure is fail-closed. A prior result remains valid for its
prior bytes after a revision but is not silently transferred to new bytes.

## Operational limits and failure boundary

- maximum 262,144 bytes per JSON input;
- 32 states, 128 equality rows, 128 inequality rows, 16 actions;
- numerator magnitude and denominator at most `10^12` on input;
- backend rational reconstruction denominator at most `10^9`;
- finite linear constraints only;
- no tolerance is used by the checker;
- candidate reconstruction failure, backend exception, absent certificate, or
  unsupported operation returns `unresolved` when the input itself is valid.

The exponential assignment table is intentional and small-scope. Feasibility
does not establish empirical truth or real-world membership. The implementation
is not formally verified and does not cover nonlinear fibers, causal
identification, sequential policies, acquisition value, authority, or real-world
data.

