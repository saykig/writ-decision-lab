# RUN THIS NEXT — Writ Engineering Build 1
## Exact decision-query computation, checking, and consumption

**Prepared for Sara · 6 September 2026**  
**Status:** Executable local implementation packet. Architecture and scope are selected. Do not return another strategic investigation.  
**Working name:** Writ Decision Lab (`writ_decision_lab`). This is an adjacent research component, not a new Writ record family.

## Operator instruction

Implement the build below in a new, isolated local directory. Exercise the complete path from input files to calculation, separate checking, and a second program’s checked consumption. Run the prescribed development checks and an equal-information simpler-workflow comparison. Produce working local code, tests, examples, and `BUILD_1_REPORT.md`.

The governing objective is:

> Make consequential decision-making mathematically inspectable, cumulative, and correctable.

Build 1 earns a smaller capability:

> Check a finite decision answer against the exact model and question the next program intends to use.

Do not require cumulative knowledge, external adoption, a new theorem, or immediate speed superiority to complete this build. Equally, do not call additional metadata a useful foundation without an exercised consumer.

## 1. Authorization and non-negotiable boundaries

You may create and edit code, tests, documentation, and synthetic fixtures **inside the isolated local build directory**; execute local checks; and create local result files there. A local Git repository is optional. Do not push, publish a package, open or merge a pull request, deploy, modify remote state, or change accepted canonical records.

Prefer a sibling directory named `writ-decision-lab-build1`, outside an existing Writ checkout. If the environment exposes only one writable workspace, use an explicitly isolated research directory without adding it to Writ’s package graph or changing its governed files. Record the placement. This contingency does not authorize modifying Writ’s invariants.

Preserve these inherited mathematical dispositions:

- KL5 remains `KL5_STOP_DEGENERATE`; primary and informative-interior evidence remain distinct.
- KL6 V2 remains `KL6_STOP_THEORY_ALREADY_SETTLES`, with programme disposition `KL6_STOP_STANDARD`. It is an analytic closure, not a completed enumeration.
- Do not reopen either branch, enlarge model grids, revive S04, or design KL7.

The fixtures in this packet are **engineering regression cases**. Enumeration of terminal action policies for a supplied fixed model is an algorithmic reference check, not a renewed search over observation-model grids.

No real-world priors, utility weights, source reliabilities, authority judgments, or institutional constraints may be inferred. Inputs must supply everything the calculation needs. The system makes no policy recommendation outside its explicit synthetic model.

## 2. Selected architecture — do not reopen these choices

Use **CPython 3.13**, its standard library, and `fractions.Fraction`. Record the actual patch version. The investigation probe ran on 3.13.5; another 3.13 patch is permitted with a fresh result record. Do not convert decision quantities through floats or use `limit_denominator` to approximate them.

The implementation has five responsibilities:

| Responsibility | Owns | Does not own |
|---|---|---|
| Strict input layer | Bytes, shape, labels, exact rationals, probability and dimension checks. | Source credibility or whether the model represents the world. |
| Solver | Posterior-based finite expected-loss calculation. | Verification or acceptance of its own output. |
| Separate checker | Direct joint-mass calculations, exhaustive terminal-policy reference, comparison of every exposed answer field. | General theorem proof, review, or real-world applicability. |
| Public consumer boundary | Fresh checking against caller-supplied intended inputs before exposing an answer. | Trusting a stored `checked` flag or choosing a new question for the caller. |
| CLI/examples | Read explicit local paths once, write new artifacts, demonstrate integration. | Network, arbitrary executable inputs, source ingestion, or a workflow service. |

Use ordinary JSON files, explicit version strings, and raw-byte SHA-256 associations. Do not build a registry, graph database, scheduler, agent system, acceptance ledger, or generalized plugin framework. These are **scope choices for this build**, not prohibitions on later architecture.

**Writ disposition:** no mandatory Writ runtime dependency and no Writ modifications. Its `@writ/provenance` package remains an available mechanical foundation. Adding a Node dependency only to hash bytes is not selected. Do not copy or reimplement Writ’s canonical JSON profile; do not pass computational answers through its review-artifact API and call that mathematical verification. A future Node adapter may use its existing `sha256Bytes` operation against these exact files without owning their mathematical meaning.

**External-system disposition:** keep computation native. Vela is the preferred investigated candidate if later work needs attributed scientific acceptance/correction. Lean/mathlib is the preferred formal-proof foundation when a reusable theorem justifies formalization. No Vela, Lean, MMT, Storm, RO-Crate, or AiiDA integration is part of this acceptance gate. Do not add decorative export stubs or claim compatibility that has not been tested.

## 3. Normative mathematical scope

Let `S` be a nonempty ordered list of state labels, `X` a nonempty ordered list of observation labels, and `A` a nonempty ordered list of available terminal-action labels.

Inputs specify:

- A rational prior `p[s] >= 0` with exact sum `1`.
- A rational observation channel `K[s][x] >= 0`; every state row sums exactly to `1`.
- Finite rational losses `L[a][s]`. Negative losses are permitted; no normalization is imposed.
- A rational fixed observation cost `c >= 0`, expressed in the same declared loss unit.

The decision-maker minimizes expected loss, may act immediately or obtain **exactly one** observation and then act, sees only `x` rather than the hidden state, and has the same available terminal actions after every observation. Observation does not change the state. Cost is paid once, regardless of outcome. There are no strategic opponents, state transitions, discounting, ambiguous-model mixtures, repeated sampling, or action-dependent observation channels in this profile.

Retain all minimizers; do not silently impose a tie-breaking rule. Randomized terminal policies need not be enumerated: their expected loss is a convex combination of deterministic-policy losses, so a deterministic minimizer exists under these finite linear assumptions. This argument is part of the specified mathematics, not a formal proof artifact generated by the software.

### Equations

For each terminal action:

```text
r[a] = sum_s p[s] * L[a][s]
R0   = min_a r[a]
A0   = all a attaining R0
```

For observation `x`:

```text
q[x]    = sum_s p[s] * K[s][x]
J[x][a] = sum_s p[s] * K[s][x] * L[a][s]
```

When `q[x] > 0`:

```text
posterior[s|x] = p[s] * K[s][x] / q[x]
conditional_risk[x][a] = J[x][a] / q[x]
Ax = all a minimizing conditional_risk[x][a]
```

When `q[x] = 0`, the outcome is impossible. The posterior, conditional risks, conditional minimum, and conditional action set are **null**, not zero-valued distributions, empty optimal sets, or ties.

```text
R1 = sum over possible x of q[x] * min_a conditional_risk[x][a]
EVSI = R0 - R1
net_value = EVSI - c
acquisition_risks = {act_now: R0, observe_once: R1 + c}
acquisition_argmin = all alternatives attaining the minimum
```

`EVSI` excludes cost; `net_value` includes it. `act_now` and `observe_once` refer only to these two alternatives. They are not a sequential stopping theorem.

### Bounded computational profile

Support 1–8 states, 1–8 actions, and 1–6 observations, additionally requiring `len(A) ** len(X) <= 4096`. These are transparent operational limits for this first checker, not mathematical limits on the theory.

Each input rational numerator and denominator may contain at most **32 decimal digits**, excluding a minus sign. Intermediate and output rationals must remain exact and may be larger; do not apply the input digit cap to valid computed outputs. For decoding a claimed result, allow up to **4096 digits per numerator or denominator**. These bounds accommodate values beyond floating-point integer precision while avoiding reliance on disabling Python’s integer-string safety limit. The fixed dimension bounds limit how many input denominators enter the finite sums; a conservative denominator-product bound for the exposed net value uses at most 113 input factors, or 3616 decimal digits, with additional numerator magnitude still below the result cap. Keep a regression for large intermediate rationals, not just large inputs. Input files are limited to 1 MiB each, result files to 4 MiB, and JSON nesting to 32 levels. These deterministic size limits are not a claim of comprehensive denial-of-service resistance. The archival probe’s 128-digit parser is not the Build 1 input contract. At startup, record `sys.get_int_max_str_digits()`; refuse a runtime configured with a nonzero limit below 4096 as `out_of_scope` rather than changing that process-wide setting. The default CPython limit is documented as 4300 (Python built-in-types source in §12).

## 4. Input contracts

### Encoding and identifiers

Decode valid UTF-8 JSON; reject a BOM, duplicate object keys, invalid Unicode scalar strings, non-JSON constants, trailing data, and excessive nesting. No input numeric literals are needed: all decision quantities are rational strings. Reject floats, integer literals, booleans, and null where a rational is required.

Canonical rational spelling is `n/d`, in lowest terms, with a positive denominator, no leading zeros, no `+`, no spaces, and zero written `0/1`. Examples: `1/4`, `-3/2`, `0/1`, `2/1`. Reject `0.25`, `2/4`, `-0/1`, `1/-2`, `1/0`, and `1e-3`. The implementation must enforce this stricter contract before calling the more permissive `Fraction` constructor.

State, action, observation, and unit identifiers match `[A-Za-z][A-Za-z0-9_.-]{0,63}`. Labels are exact and unique within their list. Do not case-fold, normalize, sort, infer aliases, or automatically repair them. Display descriptions and citations belong in separate notes, not extra executable fields.

Every object is closed to unspecified fields. Reject unknown fields rather than silently dropping what might be a constraint. Unsupported schema/semantics versions are `out_of_scope`, not an attempt to infer their meaning.

### `model.json`

```json
{
  "schema": "wdl.model.v1",
  "states": ["s0", "s1"],
  "outcomes": ["x0", "x1"],
  "prior": ["3/4", "1/4"],
  "likelihood": [["1/1", "0/1"], ["1/2", "1/2"]]
}
```

The exact required keys are `schema`, `states`, `outcomes`, `prior`, and `likelihood`. A likelihood row is a state; its columns follow `outcomes`. All dimensions must agree. No hash inside this input is needed; the runner binds the actual supplied bytes.

### `query.json`

```json
{
  "schema": "wdl.query.v1",
  "semantics": "finite-one-observation.v1",
  "state_order": ["s0", "s1"],
  "actions": ["a0", "a1"],
  "losses": [["0/1", "1/1"], ["1/1", "0/1"]],
  "loss_unit": "loss-unit",
  "cost": "0/1"
}
```

These seven keys are required and exhaustive. `state_order` must match `model.states` exactly. Rows follow `actions`; columns follow `state_order`. `loss_unit` identifies the common scale but does not perform unit conversion or establish an interpersonal utility comparison. Missing cost is invalid, not an implicit zero.

Losses and available actions are part of the question. A different question can be applied to the same model through a new invocation. A question can also be applied to another model with the same state ordering, but the result always binds the complete pair. This is a storage/interface choice, not a claim that losses cannot be considered part of a decision model in another formalization.

### Validation outcomes

Use explicit runtime exceptions/diagnostics, not `assert`, for validation. Running with `python -O` must not change rejection behavior. Do not accept rows whose sum is merely within a tolerance of one.

## 5. Result, checking record, and consumer contract

### Result content

`result.json` is a `wdl.result.v1` object with exactly these top-level fields:

```text
schema
semantics
input_bindings: {model_sha256, query_sha256}
producer: {name, version, code_sha256, python_version}
answer
```

`name` is `writ-decision-lab`; initial `version` is `0.1.0`. `code_sha256` identifies the producer source snapshot as defined below, not a signature or authenticity guarantee. Validate its shape but do not require another producer’s source hash to equal the checker’s source hash.

`answer` contains exactly:

```text
state_order                   labels matching the model
outcome_order                 labels matching the model
action_order                  labels matching the query
loss_unit                     exact query value
prior_risks                   rational array in action order
current_risk                  rational
current_argmin                every minimizer in action order
branches                      one entry per outcome in outcome order
observed_risk                 rational, excluding cost
evsi                          rational, excluding cost
net_value                     rational, including cost
acquisition_risks              {act_now: rational, observe_once: rational}
acquisition_argmin             ordered subsequence of [act_now, observe_once]
```

A branch has exactly `outcome`, `status`, `mass`, `posterior`, `risks`, `minimum_risk`, and `argmin`. A possible branch uses rational arrays/numbers and all action minimizers. An impossible branch has mass `0/1` and null in each of the four conditional fields. There must be no missing, duplicated, or reordered branch hidden by dictionary lookup.

**There is no result-level `verified`, `accepted`, `true`, or review field.** Successful solving produces a result, not an acceptance decision.

For the example above, the numerical answer must include:

```text
prior_risks       = [1/4, 3/4]
current_risk      = 1/4
current_argmin    = [a0]
x0 mass          = 7/8
x0 posterior     = [6/7, 1/7]
x0 risks         = [1/7, 6/7], minimum 1/7, argmin [a0]
x1 mass          = 1/8
x1 posterior     = [0/1, 1/1]
x1 risks         = [1/1, 0/1], minimum 0/1, argmin [a1]
observed_risk    = 1/8
evsi             = 1/8
net_value        = 1/8
acquisition_risks = {act_now: 1/4, observe_once: 1/8}
acquisition_argmin = [observe_once]
```

### Identity and deterministic output

Hash each **original input byte sequence** with SHA-256 and prefix its lowercase hexadecimal digest with `sha256:`. Do not hash reserialized inputs in their place. Whitespace changes therefore change byte identity, even when the parsed mathematics is the same. This conservative behavior is intentional, not proof that the models differ mathematically.

Serialize generated artifacts using Python JSON with sorted object keys, compact separators, ASCII escaping, `allow_nan=False`, and one final LF. Preserve array order. Call this `wdl-json-output.v1`; it is only a local output encoding profile, not Writ Canonical JSON or certified RFC 8785/JCS.

Compute `code_sha256` over the same deterministic encoding of a sorted list of `{path, sha256}` entries for every shipped `.py` file beneath `src/writ_decision_lab/`, with repository-relative forward-slash paths and raw file hashes. Exclude `__pycache__`, generated outputs, absolute locations, and timestamps. Record this as source association, not proof that the runtime executed those exact bytes. Read-only, frozen source/input snapshots are an assumption; stronger supply-chain attestation is deferred.

Core calculation/checking functions accept frozen inputs and metadata. They perform no file writes, wall-clock reads, random sampling, network access, or inference. The CLI may inspect runtime version and read/write explicit local paths. Benchmark timing belongs in a separate harness, never the deterministic result.

### Checking record

A fresh `wdl.check.v1` record contains:

```text
schema
semantics
subject: {model_sha256, query_sha256, result_sha256}
checker: {name, method, code_sha256, python_version}
status
diagnostics: [{code, path, message}]
policy_count
limitations
```

Use method `joint-mass-and-policy-enumeration.v1`. Hash the result’s actual bytes, not a selected subset of answer fields. `policy_count` is the actual number enumerated on a completed check; otherwise null. Subject hashes may be null only for unavailable bytes. Diagnostics must be stable, ordered, and avoid secrets, machine-specific absolute paths, or uncontrolled exception text.

Required limitations, in substance: this checks the supplied finite one-observation calculation; it does not validate source fidelity, real-world assumptions, cross-question sufficiency, a formal proof, independent authorship, or scientific acceptance. Method independence must disclose the shared parser, rational library, author, and specification.

A stored check record is descriptive evidence. It is not a capability token, signature, or permission to skip checking. Altering one must never grant consumer access to an unchecked answer.

### Public API and failure behavior

Expose these operations (equivalent type names are acceptable; semantics are fixed):

```python
solve_bytes(model_bytes: bytes, query_bytes: bytes) -> bytes
check_bytes(model_bytes: bytes, query_bytes: bytes, result_bytes: bytes) -> CheckReport
check_and_load(model_bytes: bytes, query_bytes: bytes, result_bytes: bytes) -> CheckedAnswer
```

Metadata needed for code/runtime identification can be injected through a small explicit immutable context. Do not add a generic user-executable plugin hook. `CheckedAnswer` is constructed only after the checker succeeds; it is a convenience type within a trusted process, not a defense against a caller deliberately bypassing the library.

The consumer supplies its intended model/question bytes independently of the result. A result that identifies its own inputs correctly does not establish that those are the inputs the consumer intended. `check_and_load` performs fresh whole-answer checking every time in v1. No cache and no `trust_previous_check` option.

| Status / exit code | Meaning | Consumer behavior |
|---|---|---|
| `checked` / 0 | All required checks passed for the exact supplied pair and supported profile. | Expose a checked answer; never label it accepted or real-world true. |
| `invalid_input` / 2 | Malformed JSON, invalid rational/shape/probability/labels, missing required field, or unknown field. Includes malformed result objects. | Expose no functional answer. |
| `out_of_scope` / 3 | Unsupported version/semantics or a declared deterministic resource bound exceeded. | No extrapolation or silent approximation. |
| `input_mismatch` / 4 | Well-formed result names model/question byte hashes different from the intended inputs. | Do not reuse it. Historical validity under its original inputs is not denied. |
| `computation_mismatch` / 5 | Correct target bindings but a well-formed claimed mathematical answer disagrees with the check. | Report the mismatched fields; disprove only those claimed outputs under these inputs. |
| `not_checked` / 6 | Required file bytes are unavailable in a CLI invocation. | No answer. A missing record is not a false mathematical statement. |
| `checker_error` / 70 | Unexpected checker/runtime failure. | Fail closed; no fallback to the producer’s answer. |

The pure API receives bytes, so `not_checked` normally arises in the I/O wrapper. For `solve`, a successful invocation exits 0 with a **produced** result, not a check record. Failure diagnostics follow the same relevant codes.

Evaluation order is: obtain bytes; validate intended inputs and supported scope; decode result and its declared versions; validate result shape; compare bindings; recompute/compare mathematics. Record the primary failure and deterministic diagnostics, without pretending later checks ran.

## 6. Separate implementation requirements

### Producer

Compute prior risks, posterior distributions for positive-mass observations, conditional risks, and their weighted minima. Derive EVSI and acquisition choice through §3. Keep exact arithmetic throughout.

### Checker

The checker must **not import the solver or call its posterior/minimum/result-construction helpers**. It may share the strict input decoder, rational parsing, immutable data types, and byte-hashing/encoding utilities; disclose those shared dependencies.

Independently calculate `q[x]` and `J[x][a]` from joint masses. Check the claimed posterior by the exact identities `q[x] * posterior[s|x] == p[s]*K[s][x]`, with normalization and nonnegativity. Check claimed conditional risks by `q[x]*risk[x][a] == J[x][a]`. Independently check all prior risks, minima, action sets, branch statuses, and ordering.

Enumerate every function `pi: X -> A` in deterministic order and evaluate:

```text
V(pi) = sum_s sum_x p[s] * K[s][x] * L[pi(x)][s]
```

The minimum must equal claimed `observed_risk`. Also recompute the remaining scalar relationships and both acquisition risks. Impossible outcomes can receive arbitrary actions within the enumeration because their joint mass is zero; do not translate those arbitrary assignments into a claimed conditional action answer.

The equality between this enumeration and the producer’s branchwise minimum follows because, within the specified scope, the action at one observation imposes no constraint on the action at another. This argument fails for many richer problems; do not widen the profile without a new contract and corresponding reasoning.

The checker must compare **every exposed answer field**, not just EVSI. Merely invoking the same solver twice is not a separate algorithm. Returning `checked` because hashes match is a fatal acceptance failure.

### Minimal module layout

```text
writ-decision-lab-build1/
  README.md
  SPEC.md
  SOURCES.md
  src/writ_decision_lab/
    __init__.py
    __main__.py
    errors.py
    decode.py
    types.py
    identity.py
    solver.py
    checker.py
    consumer.py
    cli.py
  examples/
    consume_answer.py
    weak/model.json
    weak/query.json
  fixtures/
    manifest.json
    ... versioned fixed fixture directories ...
  tests/
    test_decode.py
    test_solver.py
    test_checker.py
    test_consumer.py
    test_cli.py
    test_metamorphic.py
  comparison/
    baseline.py
    run_sequence.py
    README.md
  research_probe/
    spike.py
    ... generated reproduction outputs ...
  outputs/
  BUILD_1_REPORT.md
```

Use `unittest`; no package installation is required for the initial local run. Tests import the package through `PYTHONPATH=src`. `SPEC.md` is the normative local contract derived from this packet; types and tests implement it. Do not add a second, partially maintained schema system simply to create more artifacts.

Implementation-level refactoring is permitted inside this boundary. Any proposed change to the mathematics, mandatory checking, scope, dependency choices, or external authority must be documented as an unimplemented follow-up rather than silently substituted.

## 7. Required fixtures

Create a manifest naming each fixture, its origin, exact input files, and intended property. The first six are supplied KL4C-style regression definitions; the rest are engineering additions. None is sealed or held out.

For binary rows below, let `p = P(s1)`, and let `k = (P(x1|s0), P(x1|s1))`; therefore the model rows are `[[1-k0,k0],[1-k1,k1]]`. Unless stated otherwise use `p=1/4`, `c=0`, `L=[[0,1],[1,0]]`. Convert all numbers to canonical rational strings.

| ID | Exact change | Required result |
|---|---|---|
| F01 weak | `k=(0,1/2)` | Current action a0; conditional actions a0/a1; EVSI `1/8`. Full expected answer in §5. |
| F02 perfect | `k=(0,1)` | Same action answers as F01; EVSI `1/4`. |
| F03 no-signal-unit | `k=(0,0)` | Current/possible-branch action a0; x1 impossible; EVSI 0. |
| F04 no-signal-asymmetric | F03, `L=[[0,1],[2,0]]` | Same original action summary and EVSI as F03. |
| F05 revised-unit | F03, `L=[[1,1],[1,0]]` | Prior risks `(1,3/4)`; unique a1. |
| F06 revised-asymmetric | F04, `L=[[1,1],[2,0]]` | Prior risks `(1,3/2)`; unique a0. |
| F07 real-tie | `p=1/2`, `k=(1/2,1/2)` | Possible observations; both terminal actions minimize at every branch. |
| F08 zero-prior | `p=0`, `k=(0,1)` | x1 impossible, not a tie or uniform posterior. |
| F09 exactness | `p=500000000000000000/1000000000000000001`, `k=(0,0)` | Unique a0; risk gap `1/1000000000000000001`. No float tolerance. |
| F10 acquisition-tie | F01, `c=1/8` | Both `act_now` and `observe_once`; net value 0. |
| F11 three-state | Prior `(1/2,1/3,1/6)`; identity 3×3 K; `L=[[0,2,3],[1,0,2],[3,1,0]]` | Prior minimum `5/6` at a1; observed risk 0; EVSI `5/6`. |
| F12 restricted-actions | F02 but available actions only `[a0]`, losses only its row | EVSI 0; do not retain the removed action a1. |

Appendix A generates the probe’s exact numerical versions of these 12 cases. Its schema is intentionally smaller than Build 1’s: add the required version fields, state ordering, and loss unit during migration. Do not change the numbers to make tests pass. Total reference enumeration across these cases is 68 deterministic policies; this is a reproducibility observation, not a scientific sample-size claim.

Add deterministic structural fixtures for the smallest case (one state/action/outcome), negative losses, observation cost greater than EVSI, and at least one valid configuration at the `4096`-policy limit. Compute those expectations from §3 using the separate checker and manually document a simple sanity argument; label them new development cases, not independent holdouts.

## 8. Acceptance checks

Record named checks and actual command results, not only a total count. Every failure category below needs a regression test.

### Arithmetic and semantics

All 12 required fixtures agree between algorithms, including all exposed fields. The additional minimum/negative-loss/cost/limit cases pass. EVSI is nonnegative under this profile because ignoring the observation is available; a negative computed EVSI is a bug, not a value to clamp to zero. Negative **net value** is valid.

Test explicit label-preserving transformations: simultaneous state permutation with prior/channel rows and loss columns; action permutation; and outcome permutation. Compare appropriately relabeled fresh answers, but require old byte bindings to fail after a permutation. Add a positive scale factor applied to both losses and cost, and a constant added to every loss cell. Derive their expected action/value relationships in the test comments; never call these a universal equivalence oracle.

### Strict input and boundary behavior

Reject the nine malformed rational values in Appendix A and additional duplicate keys, wrong dimensions, missing cost, duplicate labels, mismatched state order, non-normalized probability rows, negative probability, invalid Unicode, `NaN`, extra constraints/fields, and unknown fields in result objects. Test both normal and optimized Python execution. Over-limit but otherwise meaningful supported-shape requests return `out_of_scope`, not a fabricated approximate result.

Unsupported semantics such as `finite-two-observation.v1` must be refused. Do not add a sequential implementation to satisfy that test.

### Adversarial answer and intended-input checks

Change each answer field independently while retaining correct input hashes, including posterior components, branch mass, risk, minimum, EVSI, net value, action order, loss unit, omitted tie minimizer, and impossible-branch nulls. Each must fail with a shape or computation diagnostic; none may return `checked`.

Change the intended model, cost, losses, available actions, or even input whitespace while keeping an old result. Expect `input_mismatch`. Separately edit an old result’s header to name the changed inputs while retaining its old answer: identity now matches, so the mathematical checker must detect the wrong answer where the change affects it. Select mutations with a documented changed expected output.

Recheck the original result against the original bytes: it must still pass. A changed question does not retroactively refute the old calculation.

Forge, delete, or modify a saved `check.json`. The consumer must ignore its claimed success and perform the real check. Simulate an unexpected checker exception; the consumer must fail closed, not expose the producer’s answer. Verify through a spy/test double that the downstream output function was not called on any failure.

### Integration and reproducibility

`examples/consume_answer.py` must use only the public check-and-load interface, not internal solver functions. It receives explicit intended model/query paths and a result, then writes a small checked summary: current action set, EVSI, and acquisition action set. It must fail on the same-input-hash/tampered-value case and on changed-question reuse. This is the minimum demonstrated second consumer.

Run the solve/check/consume path in separate processes and again in a second temporary directory. With identical frozen input, source, and runtime bytes, generated result/check/consumer artifacts must be byte-identical. The code manifest must not contain absolute paths. Tests must perform no network access. Verify that no Writ files changed.

Do not claim cross-runtime compatibility merely because the encoding uses JSON. No second-language reader is required or established in this version.

## 9. Competent simpler comparison

Implement `comparison/baseline.py` as an ordinary exact-arithmetic script using the same substantive inputs, definitions, labels, fixtures, and access. It may use `Fraction`, a second calculation, assertions, raw hashes, Git notes, and explicit refusal of unsupported requests. Do not forbid sensible safeguards to manufacture a win. It must not import the candidate package, because the question is whether the package boundary adds value over a competent ordinary script.

The baseline can match every mathematical answer. That is expected, not a reason to invent a novelty claim. Do not feed the baseline only action summaries while giving the candidate the full model.

Freeze and run this sequence for both implementations:

1. Produce F01 and consume its answer.
2. Change to F02’s channel; obtain the new value rather than reuse the old one.
3. Change F01’s cost to `1/8`; preserve the acquisition tie.
4. Run the F03→F05 loss revision; preserve the old result under its old inputs.
5. Restrict F02’s available actions as in F12.
6. Attempt to use the original F01 result with the changed cost; refuse, then recheck it against its original question.
7. Alter F01’s EVSI while retaining correct input hashes; detect the error before downstream use.
8. Request unsupported two-observation semantics; refuse without solving or widening the profile.

Record mathematical correctness, erroneous downstream uses, refusal reasons, preparation steps, changed source/configuration files, duplicated checking logic, repairs, and actual execution times where measured. Count the cost of creating and maintaining both workflows. Separate measured machine duration from estimated human effort; do not invent model-token usage, hidden timing, independent participants, or future savings.

This is an implementer-run development comparison, not a blinded study. It can demonstrate mechanisms and costs; it cannot establish general human or agent productivity.

### Interpretation rules

- **Behavior gate:** zero erroneous downstream uses across the specified failures and all exact answers correct. Any failure blocks a successful-build claim.
- **Foundation gate:** the second consumer uses the public interface, passes all failures, and reuses that interface across the sequence without reaching into solver internals. Success supports a reusable local boundary, not broader accumulation.
- **Present comparative benefit:** fewer actual repairs, fewer duplicated consumer safeguards, or fewer wrong uses, without hiding greater preparation/maintenance. Report each cost separately; do not combine them through an arbitrary scalar score.
- **No demonstrated advantage:** both achieve the protections with comparable effort, or the simpler script is clearer/cheaper. Keep useful math/tests but simplify the wrapper or retain only the public function that earned use.
- **Uninformative:** trivial tasks/timing noise, unequal substantive inputs, incomplete cost capture, or a broken/underprepared baseline. Report the limitation; do not score it as a candidate victory.

Immediate speed superiority is not required. Additional permanent architecture requires additional evidence, not an indefinitely deferred payoff.

## 10. Execution order and commands

Proceed in this order; no second strategic audit is required.

1. Record placement, source references, runtime, and the no-production-write boundary. Save this packet locally. Reproduce Appendix A in `research_probe/`; preserve its outputs.
2. Write `SPEC.md` and the strict input/data types. Run rejection tests, including `python -O`.
3. Implement the producer directly from §3; add fixed numerical fixtures and tests.
4. Implement the checker without importing producer math. Add whole-answer mutations, same-hash/tampered-answer tests, and deterministic resource limits.
5. Implement `check_and_load`, the CLI, and the separate consumer. Exercise all refusal paths before accepting any downstream output.
6. Run reproducibility, metamorphic, and integration checks. Implement and execute the fair simpler baseline sequence.
7. Write `BUILD_1_REPORT.md`, documenting all failures, deviations, and unrun tests. Stop at the local gate. Do not publish or merge.

The following interface must exist after implementation:

```bash
# Run from the isolated build directory. No package installation is required.
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

Input locations come only from explicit local CLI arguments, not URLs or paths in a result payload. Read each input into bytes once and then operate on that snapshot. Refuse overwriting an existing output; use fresh directories for repeat runs. Do not execute strings from input documents or resolve remote references. A failure can write a diagnostic/check record, but it must not write a functional consumer answer.

These commands describe the interface to implement, not commands that have already succeeded. Appendix A records the only executed probe supplied by this investigation.

## 11. Reporting and continuation gate

`BUILD_1_REPORT.md` must start with one verdict:

```text
BUILD1_BEHAVIOR_AND_FOUNDATION_ESTABLISHED
BUILD1_BEHAVIOR_ONLY
BUILD1_SIMPLER_WORKFLOW_PREFERRED
BUILD1_BLOCKED_OR_FAILED
```

A successful behavior/foundation verdict does not imply comparative advantage. Report it separately. A simpler-workflow verdict can still retain useful tested functions and fixtures.

Use this reporting structure:

```markdown
# Build 1 report
## Verdict and plain-language result
## Exact scope and contract implemented
## Files created; source/runtime identities; local-only changes
## Evidence ledger
| Claim | Observed / derived / source-reported / hypothesized | Evidence | Limitation |
## Named test results and commands
## Whole-answer and intended-input mutation results
## Separate-consumer demonstration
## Equal-information baseline comparison, including preparation and maintenance
## Deviations, failures, unavailable sources, and tests not run
## What is established / what remains untested
## Continue, simplify, redirect, or retire
```

Do not count the producer and checker as independent authors or a formal proof. Cite the exact inputs and actual outputs behind numeric claims. Preserve a failing fixture and the correction explanation rather than changing the expected answer silently.

Continue the component when both gates pass and an actual consumer wants it. Simplify when an ordinary script provides the same protections with less maintenance. Redirect to Vela if accepted-state inheritance is the actual next difficulty; redirect to formal verification or a different solver only when a specific task justifies it. Do not silently expand the first semantics version.

After the next **three suitable real research tasks**, reassess actual reuse and maintenance. “Suitable” means they genuinely fall within this profile without distorting the research question. If there is no willing consumer, retire the component while retaining the regression fixtures. If the research has moved outside this profile, report that relevance limit rather than bending the research to feed the tool. A component’s retirement does not decide the programme’s fate.

## 12. Source requirements and inherited evidence

This packet is self-contained for implementation. Missing historical attachments must not block it. The original mathematical proofs are not required because the finite definitions and reference algorithms are explicit here. Do not reconstruct unprovided scientific findings.

The governing brief was `RUN_THIS_NEXT_WRIT_ENGINEERING_FOUNDATIONS_AND_FIRST_BUILD.md`, prepared 6 September 2026. Its §3.3 supplies the first two counterexample patterns; its §3.2 supplies the binding dispositions. Treat them as inherited unless separately checked, and call the fixture calculations here engineering reproductions.

The investigation inspected:

| Source | Version / exact scope | Relevance |
|---|---|---|
| Writ | `20f0473afa62ed3c6e0433a21b189d1d9d1712d6`; AGENTS, README, product definition; provenance README, hash implementation, package manifest, profile and packed-consumer tests. | Current boundary and component-reuse judgment; tests not executed. |
| Vela | `017bca6bfaa29e96d8e1b0819979c732d3320917`; evidence page, Cargo manifest, architecture lines 1–190, verification record source/tests. | Scoped checking distinct from acceptance; no local Vela execution. |
| Python | 3.13 `fractions` documentation; probe runtime 3.13.5. | Existing exact arithmetic; stricter input contract remains ours. |
| Lean/mathlib | Current proof-validation reference and nonnegative rational API. | Deferred stronger-verification foundation, not a local proof. |
| PROV / RO-Crate / nanopublications / AiiDA / MMT / Snakemake / Storm | Relevant primary specification/documentation sections, recorded in the direction report. | Alternatives and later interfaces, not dependencies silently added to this build. |

Relevant primary-source entry points:

`https://github.com/saykig/Writ/blob/20f0473afa62ed3c6e0433a21b189d1d9d1712d6/AGENTS.md`  
`https://github.com/saykig/Writ/blob/20f0473afa62ed3c6e0433a21b189d1d9d1712d6/packages/provenance/README.md`  
`https://github.com/vela-science/vela/blob/017bca6bfaa29e96d8e1b0819979c732d3320917/docs/EVIDENCE.md`  
`https://github.com/vela-science/vela/blob/017bca6bfaa29e96d8e1b0819979c732d3320917/crates/vela-protocol/src/objects/verification_record.rs`  
`https://docs.python.org/3.13/library/fractions.html`  
`https://docs.python.org/3.13/library/stdtypes.html#integer-string-conversion-length-limitation`  
`https://lean-lang.org/doc/reference/latest/ValidatingProofs/`

When accessing a newer Writ checkout, record its actual commit and respect its current governing files. Do not reset the user’s repository to the inspected commit. The standalone build does not depend on Writ being accessible. Any later modification to Writ requires a separate explicit scope and, where guarantees change, an ADR.

## Appendix A — Reproduce the executed investigation probe

**This is not Build 1.** It is a compact fixed-fixture calculation used to test feasibility during the investigation. It uses assertions for internal checks, has no full hostile-input decoder, validates only a subset of result quantities through its reference algorithm, and hashes its own deterministic encoding rather than arbitrary original input files. Build 1 must strengthen those boundaries as specified above.

Save the exact Python code below as `research_probe/spike.py`, with a final LF. Then run:

```bash
python research_probe/spike.py
python - <<'PY'
from hashlib import sha256
from pathlib import Path
for name in ('spike.py', 'spike_results.json', 'spike_fixtures.json'):
    p = Path('research_probe') / name
    print(sha256(p.read_bytes()).hexdigest(), p)
PY
```

Observed stdout under Python 3.13.5:

```json
{"binding_mutations_rejected": 2, "enumerated_policies": 68, "fixed_fixtures": 12, "python": "3.13.5", "rational_rejections": 9, "tampered_value_detected_by_recomputation": true}
```

Observed SHA-256 values:

```text
spike.py           bf8ede7d901cafb20dda96f3c3824cfe48e446a8308cdaad361a25a9673977d8
spike_results.json 4775493a22c3dd98773582ae4ea566543e1a052d73d8e8525f9dd3d3b2badd2b
```

The results JSON contains the Python patch-version string, so its hash legitimately differs under a different patch version; the numerical fixture answers should not. Do not update recorded historical hashes to hide a difference. Record the new environment and comparison.

<!-- BEGIN EXECUTED PROBE -->
```python
"""Isolated engineering probe, not Build 1 and not a KL experiment.
Python 3.13 standard library only. Fixed fixtures; no grid search.
"""
from __future__ import annotations
import copy
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import re
import sys


def rat(s: str) -> F:
    if not isinstance(s, str) or not re.fullmatch(r'(?:0|-?[1-9][0-9]*)/[1-9][0-9]*', s):
        raise ValueError('E_RATIONAL')
    a, b = s.split('/')
    if len(a.lstrip('-')) > 128 or len(b) > 128:
        raise ValueError('E_RATIONAL_LIMIT')
    f = F(int(a), int(b))
    if f'{f.numerator}/{f.denominator}' != s:
        raise ValueError('E_RATIONAL_CANONICAL')
    return f


def wire(value):
    if isinstance(value, F):
        return f'{value.numerator}/{value.denominator}'
    if isinstance(value, dict):
        return {k: wire(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [wire(v) for v in value]
    return value


def encoded(value) -> bytes:
    return (json.dumps(wire(value), sort_keys=True, separators=(',', ':'), ensure_ascii=True)+'\n').encode('ascii')


def digest(b: bytes) -> str:
    return 'sha256:' + sha256(b).hexdigest()


def inputs(model, query):
    p = list(map(rat, model['prior']))
    k = [list(map(rat, row)) for row in model['likelihood']]
    l = [list(map(rat, row)) for row in query['losses']]
    c = rat(query['cost'])
    ns, nx, na = len(p), len(model['outcomes']), len(query['actions'])
    assert len(model['states']) == ns and len(k) == ns and all(len(row) == nx for row in k)
    assert len(l) == na and all(len(row) == ns for row in l)
    assert all(v >= 0 for v in p) and sum(p) == 1
    assert all(all(v >= 0 for v in row) and sum(row) == 1 for row in k)
    assert c >= 0
    return p, k, l, c


def solve(model, query):
    p, k, l, c = inputs(model, query)
    ns, nx, na = len(p), len(k[0]), len(l)
    prior_risks = [sum(p[s]*l[a][s] for s in range(ns)) for a in range(na)]
    current = min(prior_risks)
    branches, observed = [], F(0)
    for x in range(nx):
        joint = [p[s]*k[s][x] for s in range(ns)]
        mass = sum(joint)
        if mass == 0:
            branches.append({'outcome': model['outcomes'][x], 'status': 'impossible', 'mass': F(0), 'posterior': None, 'risks': None, 'argmin': None})
            continue
        post = [j/mass for j in joint]
        risks = [sum(post[s]*l[a][s] for s in range(ns)) for a in range(na)]
        best = min(risks)
        observed += mass*best
        branches.append({'outcome': model['outcomes'][x], 'status': 'possible', 'mass': mass, 'posterior': post, 'risks': risks, 'argmin': [query['actions'][a] for a in range(na) if risks[a] == best]})
    alternatives = {'act_now': current, 'observe_once': observed+c}
    return {'prior_risks': prior_risks, 'current_argmin': [query['actions'][a] for a in range(na) if prior_risks[a] == current], 'current_risk': current, 'branches': branches, 'observed_risk': observed, 'evsi': current-observed, 'net_value': current-observed-c, 'acquisition_argmin': [a for a, risk in alternatives.items() if risk == min(alternatives.values())]}


def enumerate_policies(model, query):
    # Deliberately does not call solve or posterior/branch-risk helpers.
    # It shares the parser, rational library, specification and author.
    p, k, l, c = inputs(model, query)
    ns, nx, na = len(p), len(k[0]), len(l)
    values = []
    for policy in product(range(na), repeat=nx):
        values.append(sum(p[s]*k[s][x]*l[policy[x]][s] for s in range(ns) for x in range(nx)))
    current = min(sum(p[s]*l[a][s] for s in range(ns)) for a in range(na))
    return {'current_risk': current, 'observed_risk': min(values), 'evsi': current-min(values), 'policies': len(values)}


def binary(k0, k1, loss=((0, 1), (1, 0)), prior=F(1, 4), cost=0):
    k0, k1 = F(k0), F(k1)
    model = {'states': ['s0', 's1'], 'outcomes': ['x0', 'x1'], 'prior': [1-prior, prior], 'likelihood': [[1-k0, k0], [1-k1, k1]]}
    query = {'actions': ['a0', 'a1'], 'losses': [[F(v) for v in row] for row in loss], 'cost': F(cost)}
    return wire(model), wire(query)


def check_binding(model, query, result):
    return result['model_hash'] == digest(encoded(model)) and result['query_hash'] == digest(encoded(query))


def run():
    fixtures = {
        'weak': binary(0, F(1, 2)),
        'perfect': binary(0, 1),
        'base_unit': binary(0, 0),
        'base_asymmetric': binary(0, 0, ((0, 1), (2, 0))),
        'revised_unit': binary(0, 0, ((1, 1), (1, 0))),
        'revised_asymmetric': binary(0, 0, ((1, 1), (2, 0))),
        'tie': binary(F(1, 2), F(1, 2), prior=F(1, 2)),
        'zero_prior': binary(0, 1, prior=F(0)),
        'large_rational': binary(0, 0, prior=F(500000000000000000, 1000000000000000001)),
        'acquisition_tie': binary(0, F(1, 2), cost=F(1, 8)),
    }
    model = {'states': ['s0', 's1', 's2'], 'outcomes': ['x0', 'x1', 'x2'], 'prior': ['1/2', '1/3', '1/6'], 'likelihood': [['1/1', '0/1', '0/1'], ['0/1', '1/1', '0/1'], ['0/1', '0/1', '1/1']]}
    query = {'actions': ['a0', 'a1', 'a2'], 'losses': [['0/1', '2/1', '3/1'], ['1/1', '0/1', '2/1'], ['3/1', '1/1', '0/1']], 'cost': '0/1'}
    fixtures['three_state'] = (model, query)
    model, query = binary(0, 1)
    query['actions'], query['losses'] = ['a0'], [query['losses'][0]]
    fixtures['restricted_action'] = (model, query)
    results, policies = {}, 0
    for name, (model, query) in fixtures.items():
        result, reference = solve(model, query), enumerate_policies(model, query)
        for key in ('current_risk', 'observed_risk', 'evsi'):
            assert result[key] == reference[key], (name, key)
        policies += reference['policies']
        results[name] = result
    assert results['weak']['evsi'] == F(1, 8)
    assert results['perfect']['evsi'] == F(1, 4)
    def policy(r): return [r['current_argmin']] + [b['argmin'] for b in r['branches']]
    assert policy(results['weak']) == policy(results['perfect'])
    assert results['base_unit']['evsi'] == results['base_asymmetric']['evsi'] == 0
    assert policy(results['base_unit']) == policy(results['base_asymmetric'])
    assert results['revised_unit']['prior_risks'] == [F(1), F(3, 4)]
    assert results['revised_asymmetric']['prior_risks'] == [F(1), F(3, 2)]
    assert results['revised_unit']['current_argmin'] == ['a1']
    assert results['revised_asymmetric']['current_argmin'] == ['a0']
    assert results['base_unit']['branches'][1]['status'] == 'impossible'
    assert results['tie']['branches'][1]['argmin'] == ['a0', 'a1']
    assert results['three_state']['evsi'] == F(5, 6)
    assert results['restricted_action']['evsi'] == 0
    assert results['acquisition_tie']['acquisition_argmin'] == ['act_now', 'observe_once']
    near = results['large_rational']['prior_risks']
    assert near[0] < near[1] and float(near[0]) == float(near[1])
    rejected = 0
    for bad in [0.25, '0.25', '2/4', '1/0', '-0/1', '1/-2', '1e-3', ' 1/2 ', True]:
        try: rat(bad)
        except ValueError: rejected += 1
        else: raise AssertionError(('accepted malformed rational', bad))
    model, query = fixtures['weak']
    envelope = {'model_hash': digest(encoded(model)), 'query_hash': digest(encoded(query)), 'answer': wire(results['weak'])}
    assert check_binding(model, query, envelope)
    assert not check_binding(fixtures['perfect'][0], query, envelope)
    changed = copy.deepcopy(query); changed['cost'] = '1/8'
    assert not check_binding(model, changed, envelope)
    tampered = copy.deepcopy(envelope); tampered['answer']['evsi'] = '1/4'
    assert check_binding(model, query, tampered)  # Identity of inputs alone is insufficient.
    assert rat(tampered['answer']['evsi']) != enumerate_policies(model, query)['evsi']
    output = {'python': sys.version.split()[0], 'fixed_fixtures': len(fixtures), 'enumerated_policies': policies, 'rational_rejections': rejected, 'binding_mutations_rejected': 2, 'tampered_value_detected_by_recomputation': True, 'results': wire(results)}
    out = Path(__file__).parent
    (out/'spike_results.json').write_bytes(encoded(output))
    (out/'spike_fixtures.json').write_bytes(encoded(fixtures))
    print(json.dumps({k: v for k, v in output.items() if k != 'results'}, sort_keys=True))


if __name__ == '__main__':
    run()
```
<!-- END EXECUTED PROBE -->

The probe source and generated fixture inputs are sufficient to reproduce its calculations. No GitHub checkout, external dataset, hidden evaluator, or historical mathematical packet is required. Reproducing it does not satisfy the full implementation, whole-answer checker, consumer, or comparison gates above.
