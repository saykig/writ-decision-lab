# Writ Decision Lab Build 1 specification

`SPEC.md` is the normative local contract derived from the 6 September 2026 implementation packet.
The supported semantics identifier is permanently `finite-one-observation.v1`.

## 1. Mathematical objects

The complete executable object is a pair of byte-bound JSON inputs:

- a model containing ordered nonempty finite state labels `S`, ordered nonempty observation labels
  `X`, an exact rational prior `p`, and an exact rational channel `K`;
- a query containing the exact matching state order, ordered nonempty terminal actions `A`, exact
  rational losses `L[a][s]`, one loss-unit identifier, and exact rational observation cost `c`.

The result binds the raw bytes of both inputs. The model and query are jointly required for the
answer; their hashes do not make them separately composable premises.

## 2. Assumptions

- `p[s] >= 0` and `sum_s p[s] = 1` exactly.
- `K[s][x] >= 0` and every state row sums exactly to one.
- Losses are finite rationals and may be negative. Cost is nonnegative and uses the declared loss
  unit. No unit conversion or interpersonal comparison is supplied.
- The hidden state does not change. The decision-maker observes only `x`, pays cost once, and has
  the same terminal actions after each outcome.
- The choice is only act now versus exactly one observation. There are no opponents, transitions,
  discounting, ambiguous-model mixtures, repeated samples, or action-dependent channels.
- All minimizers are retained. No tie-break is inferred. A deterministic optimal terminal policy
  exists because randomized-policy loss is a convex combination under these finite linear
  assumptions.

## 3. Permitted operation and query

For action `a`, compute

```text
r[a] = sum_s p[s] L[a][s]
R0 = min_a r[a]
A0 = all minimizers in supplied action order
```

For outcome `x`, compute

```text
q[x] = sum_s p[s] K[s][x]
J[x][a] = sum_s p[s] K[s][x] L[a][s]
```

When `q[x] > 0`, compute exact posterior `p[s]K[s][x]/q[x]`, conditional risks
`J[x][a]/q[x]`, their minimum, and every minimizer. When `q[x] = 0`, status is `impossible`, mass is
`0/1`, and posterior, risks, minimum, and argmin are all null.

Then compute

```text
R1 = sum over possible x of q[x] times the conditional minimum
EVSI = R0 - R1
net_value = EVSI - c
act_now risk = R0
observe_once risk = R1 + c
```

The acquisition answer retains every minimizing alternative in the order `act_now`,
`observe_once`. EVSI excludes cost; net value includes it. No other question is supported.

## 4. Mathematical result

`wdl.result.v1` contains exactly `schema`, `semantics`, raw-byte `input_bindings`, producer
association, and `answer`. The answer contains exact label orders, loss unit, prior risks, current
risk/minimizers, one ordered branch per outcome, observed risk, EVSI, net value, both acquisition
risks, and all acquisition minimizers. There is no result-level verification, acceptance, truth,
or review field.

Generated JSON uses sorted object keys, compact separators, ASCII escaping, no NaN, and one final
LF (`wdl-json-output.v1`). Arrays preserve semantic order. Input bindings hash original bytes with
SHA-256; whitespace changes identity. `code_sha256` hashes the deterministic sorted manifest of
all shipped `.py` files under `src/writ_decision_lab`, using relative forward-slash paths and raw
file hashes. It is a source association, not runtime attestation or a signature.

## 5. Checking method

The checker method is `joint-mass-and-policy-enumeration.v1`. It shares the strict parser,
immutable input types, `Fraction`, specification, and author with the producer, but does not import
producer math.

It freshly checks the intended input byte bindings; all answer labels, order, fields, values, ties,
and impossible-branch nulls; posterior identities `q[x] posterior[s|x] = p[s]K[s][x]`; conditional
risk identities `q[x] risk[x][a] = J[x][a]`; and all scalar relations. It deterministically
enumerates every function from outcomes to actions and confirms that the least direct joint loss
equals claimed observed risk. This enumeration is valid here because actions selected at different
outcomes impose no cross-outcome constraint.

A `wdl.check.v1` record binds actual model/query/result bytes, identifies method/source/runtime,
states limitations, and records status and policy count. It is descriptive evidence only. The
consumer ignores stored check files and checks again.

## 6. Guarantee and limitations

Subject to this specification and correctness of the checker/runtime, `checked` means every
exposed answer field agrees with the exact supplied model/query bytes under the finite
one-observation semantics. It does not establish source fidelity, adequacy of real-world priors or
losses, cross-question sufficiency, formal proof, independent authorship, scientific acceptance,
or a policy recommendation outside the supplied synthetic model.

Statuses and exit codes are: `checked`/0, `invalid_input`/2, `out_of_scope`/3,
`input_mismatch`/4, `computation_mismatch`/5, `not_checked`/6, and `checker_error`/70. Solving exits
0 with a produced result, not a check. Unexpected failures fail closed.

Operational bounds are 1–8 states, 1–8 actions, 1–6 outcomes, and at most 4096 terminal policies.
Each input rational component has at most 32 digits; a claimed output component has at most 4096.
Model/query files are at most 1 MiB, result files 4 MiB, and JSON depth 32. A nonzero CPython
integer-string limit below 4096 is out of scope. These are deterministic Build 1 limits, not
mathematical or comprehensive security limits.

## 7. Reuse and composition

A result may be reused only by freshly calling `check_and_load` with the caller's independently
supplied intended model and query bytes. Historical validity under original inputs is not denied by
refusal under changed inputs. No cache, previous-check trust option, remote input, executable input,
or inferred alias exists.

Separately checked answers are not thereby composable. Build 1 supplies no theorem for composing
different models, queries, losses, costs, posteriors, EVSIs, or acquisition decisions. It also
supplies no evidence-dependence, causal, robust-decision, graph, ontology, or other Bellman
machinery. A future Bellman semantics version may introduce new objects and justified operations
under a new exact identifier; it must not reinterpret `finite-one-observation.v1`.

## Strict input profile

Model keys are exactly `schema`, `states`, `outcomes`, `prior`, `likelihood`. Query keys are exactly
`schema`, `semantics`, `state_order`, `actions`, `losses`, `loss_unit`, `cost`. Objects are closed.
Labels match `[A-Za-z][A-Za-z0-9_.-]{0,63}`, remain exact and unique within each list, and are never
normalized, sorted, case-folded, aliased, or repaired.

Decision quantities are strings in canonical lowest-term `n/d` spelling with positive denominator,
no leading zero, plus sign, spaces, decimal, exponent, negative zero, or noncanonical reduction;
zero is `0/1`. UTF-8 BOMs, malformed UTF-8, surrogate scalar strings, duplicate object keys,
non-JSON constants, trailing data, excessive nesting, numeric literals, booleans/null in rational
positions, missing fields, and unknown fields are rejected. Unsupported exact versions are out of
scope rather than guessed.
