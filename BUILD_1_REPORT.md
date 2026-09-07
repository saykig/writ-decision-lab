BUILD1_SIMPLER_WORKFLOW_PREFERRED

# Build 1 report

## Verdict and plain-language result

Build 1 is complete and working locally. The behavior gate and foundation gate both pass: exact
answers were correct, the independently structured checker rejected every prescribed binding and
answer mutation, and the separate consumer exposed no functional answer on failure.

The simpler-workflow verdict is nevertheless required by the observed comparison. The competent
ordinary script passed the same frozen eight-step sequence with zero erroneous downstream uses and
maintained 145 source lines, versus 1,170 candidate/runtime-consumer lines. The candidate supplies a
stricter decoder and a genuinely separate checking algorithm, so the line counts do not represent
equal assurance. They do establish that the package boundary has not yet demonstrated enough
present comparative benefit for this small workflow. Retain the completed math, checker, tests,
fixtures, and consumer boundary; prefer the simpler script for present work unless a real consumer
specifically needs the stronger boundary.

This verdict is about current engineering cost, not mathematical failure or a decision about the
Bellman programme.

## Exact scope and contract implemented

The implementation accepts a complete finite rational model and query, minimizes expected loss,
and compares acting now with obtaining exactly one observation and then taking one terminal action.
It preserves ordered labels, all minimizers, exact rational arithmetic, impossible-outcome nulls,
raw input-byte identities, and the distinction between EVSI and net value.

The producer is posterior-based. The checker does not import producer math: it reconstructs direct
joint masses and joint losses, checks posterior/risk identities, compares every exposed answer
field, and exhaustively enumerates every deterministic function from outcomes to actions. The
public consumer supplies independently intended input bytes and checks the whole result afresh.

Strict JSON, rational, label, version, dimension, policy-count, byte-size, nesting, runtime, and
output contracts are specified in `SPEC.md`. Status behavior is `checked`/0,
`invalid_input`/2, `out_of_scope`/3, `input_mismatch`/4, `computation_mismatch`/5,
`not_checked`/6, and `checker_error`/70. A solve success is only a produced result.

## Bellman mathematical-substrate alignment

Build 1 implements the mathematical object consisting of a finite ordered state space, a finite
ordered observation space, an exact rational prior and state-conditioned observation channel, and
a query containing a finite ordered terminal-action set, exact rational loss matrix, common loss
unit, and one fixed observation cost.

Its exact operation is finite expected-loss minimization for the choice between acting immediately
and obtaining exactly one observation before selecting a terminal action. It returns prior risks,
all immediate minimizers, possible-outcome posteriors and conditional risks/minimizers, impossible
branches as null conditional objects, observed risk, EVSI, net value, and all minimizing acquisition
alternatives.

Its assumptions are frozen: exact supplied rationals; normalized nonnegative prior/channel;
unchanged hidden state; observation of `x` only; the same actions after every outcome; one cost paid
once; no opponents, transitions, discounting, ambiguity mixtures, repeated sampling, or
action-dependent channels; and no inferred real-world priors, losses, reliability, authority, or
constraints. Randomized policies add no lower value here because their losses are convex
combinations of deterministic-policy losses.

Subject to this contract and checker/runtime correctness, `checked` guarantees that every exposed
answer field agrees with the exact caller-supplied model/query bytes under
`finite-one-observation.v1`, using joint-mass identities and exhaustive deterministic-policy
enumeration. It does not guarantee source fidelity, real-world adequacy, formal proof, independent
authorship, scientific acceptance, or policy truth.

No composition of separately valid models, questions, risks, posteriors, EVSIs, net values, or
decisions is justified. Build 1 contains no theorem that transports or combines them, and it adds
no evidence-dependence, causal, robust-decision, graph, ontology, or other Bellman machinery.

A future Bellman semantics version can add new mathematical objects, operations, or explicit
composition theorems behind a new exact semantics identifier and corresponding checker. Exact
version dispatch must continue to route `finite-one-observation.v1` to this unchanged meaning;
new fields or rules must never silently upgrade or reinterpret it.

## Files created; source/runtime identities; local-only changes

The isolated build is `/Users/kimchee/Documents/writ-decision-lab-build1`. Major outputs are:

- `src/writ_decision_lab/`: strict decoder/types, producer, separate checker, consumer, identity,
  diagnostics, and CLI;
- `fixtures/manifest.json` plus 12 packet cases and four development cases under `fixtures/v1/`;
- `examples/consume_answer.py` and the F01 example bytes;
- seven test modules covering decoding, solving, checking, consuming, CLI/reproducibility,
  metamorphic relations, and comparison;
- `comparison/baseline.py`, `comparison/run_sequence.py`, and comparison documentation;
- the exact saved packet/rationale, reproduced archival probe, final outputs, `SPEC.md`, this
  report, and `HANDOFF.md`.

Observed runtime: CPython 3.13.15 with `sys.get_int_max_str_digits() == 4300`. Homebrew Python 3.13
was absent and was installed to run the mandated environment; Homebrew also upgraded its local
`ca-certificates` and `openssl@3` dependencies. This changed the local tool environment, not Writ.

Final producer source association:
`sha256:2ff46c7ae832a8b51d6bb038c3e324d7295950b820f3a9a5528e3ed2dc560431`.
The manifest contains only repository-relative forward-slash paths.

The Writ checkout was clean at observed commit
`034a51edf6e716f89102d589a6f2c8c4d11a2cf2` before work and remained unmodified after the isolated
build. No Writ production file, canonical record, remote state, branch, pull request, package,
deployment, or publication was created or changed.

## Evidence ledger

| Claim | Observed / derived / source-reported / hypothesized | Evidence | Limitation |
|---|---|---|---|
| The archival source was reproduced exactly. | Observed | `research_probe/spike.py` SHA-256 `bf8ede7d...977d8`, equal to packet. | Source equality is not independent validation. |
| The archival numerical probe reproduces under 3.13.15. | Observed | 12 fixtures, 68 policies, nine rational rejections, two binding rejections, tamper detected. | Same author/spec/library; not a holdout. |
| F01 has current `a0`, EVSI `1/8`, and observe-once acquisition. | Observed | Final `outputs/weak/result.json`, bound to exact example bytes. | Synthetic supplied model only. |
| Every required and development fixture agrees between algorithms. | Observed | `test_all_required_and_development_fixtures_check`; D04 enumerates 4096 policies. | Finite test set, not proof over all inputs. |
| EVSI cannot be negative in this profile. | Derived | Ignoring the observation is an available terminal policy; tests also check all fixtures. | Derivation depends on frozen action availability and linear finite loss. |
| Branchwise minimization equals policy enumeration here. | Derived | An action choice at one outcome constrains no other outcome; checker enumerates all functions `X -> A`. | Does not transport to richer sequential/constrained problems. |
| `checked` blocks wrong target bytes and wrong answers. | Observed | Binding, rebinding, every-answer-field, joint-identity, saved-check, and fail-closed tests. | Conditional on checker/runtime correctness. |
| The separate consumer establishes a reusable local boundary. | Deduction | It imports only the public interface; altered EVSI and changed cost produce no output; frozen artifacts reproduce byte-for-byte. | One same-author consumer is not general adoption. |
| The simpler workflow is presently preferred. | Deduction | Both workflows passed eight steps with zero wrong uses; maintained source was 145 versus 1170 lines. | Assurance differs; human effort unmeasured; timings trivial. |
| KL5/KL6 stopping dispositions remain binding. | Inherited/source-reported | Execution packet states `KL5_STOP_DEGENERATE`, `KL6_STOP_THEORY_ALREADY_SETTLES`, and `KL6_STOP_STANDARD`. | Original proofs/findings were not reconstructed or re-audited. |
| The 3.13.5 archival result hash was `4775493a...dd2b`. | Inherited/source-reported | Packet's recorded probe output. | Current result hash differs because the recorded patch version is embedded. |
| Repeated checked handoff may reduce future repair or misuse. | Hypothesized | Architecture and future three-task gate. | No real repeated-use evidence yet. |

## Named test results and commands

Final frozen commands all exited 0:

```text
python --version
Python 3.13.15

python -m unittest discover -s tests -v
Ran 44 tests in 0.688s — OK

python -O -m unittest discover -s tests -v
Ran 44 tests in 0.671s — OK
```

Targeted hostile runs also exited 0:

```text
test_decode.py: 14 tests — OK
test_checker.py: 10 tests — OK
test_consumer.py: 5 tests — OK
test_cli.py: 5 tests — OK
```

Named coverage includes all 12 packet fixtures; the minimum, negative-loss, cost-over-EVSI, and
4096-policy development fixtures; a computed denominator beyond the 32-digit input cap; exact
ties/impossible outcomes; state/action/outcome permutations; positive scaling; constant loss
translation; duplicate keys; malformed rationals; invalid Unicode/NaN/BOM/trailing data; closed
objects; dimension, byte, digit, nesting, and runtime limits; optimized rejection behavior;
unsupported semantics; every exposed result/branch field; intended-input changes; rebinding;
fail-closed exceptions; output overwrite refusal; and separate-directory byte reproducibility.

The first development suite run was 40/41: the NaN rejection test had not actually inserted NaN
because it assumed a JSON suffix inconsistent with sorted keys. The hostile fixture was corrected
to construct NaN explicitly; the decoder then rejected it. This was a confirmed test-harness
defect, not an implementation defect, and is retained in this report and the comparison's
pre-freeze correction ledger.

Contract review also confirmed and repaired three implementation gaps before the frozen run: an
initial runtime check recorded but did not refuse non-CPython-3.13 execution; result decoding did
not yet enforce fixed producer metadata and ordered acquisition alternatives; and the CLI lacked an
exit-70 guard for an unexpected checker exception outside the report path. The final suite covers
the associated boundaries; no confirmed implementation defect remains open.

## Whole-answer and intended-input mutation results

With correct input hashes retained, independent mutations to every top-level answer field and every
branch field failed as `invalid_input` or `computation_mismatch`. Explicit posterior and risk
mutations also produced joint-identity diagnostics. Removing a tie minimizer failed; changing an
impossible branch's null conditional field failed.

Old F01 output was refused as `input_mismatch` after changes to the model, cost, losses, available
actions, model whitespace, or query whitespace. After forged rebinding to mathematically changed
inputs, old answers failed `computation_mismatch` for channel, cost, loss, and action-set changes.
The original result continued to check under the original bytes. A changed question therefore did
not retroactively refute its historical calculation.

Forged/modified/absent stored check evidence could not grant access because neither the public
consumer API nor example consumer accepts it as input. An injected unexpected checker exception
became `checker_error`; a downstream-output spy remained uncalled across malformed-input,
input-mismatch, and computation-mismatch failures.

## Separate-consumer demonstration

The prescribed solve/check/consume commands ran as separate processes against F01. Final artifact
SHA-256 values are:

```text
result.json   e14f7b1452b113aba0ea6508884997db729a630589882cea7053592a70785530
check.json    78783cc926835f56e98df88f7a8b0fadb40995115f47f4cc1cef423a8051c698
consumer.json c2f3f71bd443caafa5fd3614f86897a0dc44f3d938f993a0b0412b543dc3777c
```

The check status is `checked`, with policy count 4 and no diagnostics. The separate consumer wrote
only current argmin `[a0]`, EVSI `1/8`, and acquisition argmin `[observe_once]`. The integration test
repeated the three-process path in a second temporary directory and observed byte-identical result,
check, and consumer artifacts.

## Equal-information baseline comparison, including preparation and maintenance

`outputs/comparison.json` SHA-256 is
`a5e1237e0f6007fe3a75674563ce8476c54ed3b5fd4ceca25d0cab2758197cce`.
Both workflows passed all eight prescribed steps and recorded zero erroneous downstream uses:
F01 production/consumption, F02 channel change, F10 cost/acquisition tie, F03→F05 loss revision with
old-result preservation, F12 action restriction, changed-cost refusal plus original recheck,
same-binding EVSI tamper detection, and unsupported two-observation refusal.

The candidate used the public solve/check-and-load interface and did not reach into solver
internals. The baseline imported no candidate code; it used equal model/query bytes, `Fraction`,
raw hashes, and same-script fresh whole-answer recalculation.

Observed final harness durations were 15,339,625 ns for the candidate and 1,609,667 ns for the
baseline. These are recorded machine durations, but the tasks are too short and the run too small
for a speed or productivity inference. Human preparation/maintenance effort was not timed or
estimated. Candidate maintained source was 1,170 lines across runtime and example consumer;
baseline calculation/consumer source was 145 lines. The candidate's separate algorithm and strict
hostile boundary are additional assurance, so the counts are reported separately rather than
collapsed into a score.

## Deviations, failures, unavailable sources, and tests not run

- CPython 3.13.5 from the archival record was unavailable; the permitted newer patch 3.13.15 was
  installed and used. Current `spike_results.json` SHA-256 is
  `9aa1fac30ae92311c4b4ad66c14fce71cb9c35fe3b10bd60d4486a66bd8bda8b`, differing from the
  inherited 3.13.5 result hash because the patch string is data. Numerical results match.
- The user-referenced outer filename `RUN_THIS_NEXT_WRIT_BUILD_1_EXECUTE_AND_CHALLENGE.md` was not
  present as a separate filesystem attachment. Its user-message instructions and both explicitly
  attached documents were available and followed; the self-contained engineering packet was
  copied byte-for-byte into `sources/`.
- The initial NaN test-fixture failure and three repaired pre-freeze contract gaps are reported
  above. No final acceptance or hostile check failed.
- No external historical proof, Writ/Vela remote commit, Vela/Lean/MMT/Storm integration, formal
  proof, source dataset, second-language reader, network behavior, real-world decision model, or
  independent participant was run. Those are outside Build 1, not silently successful tests.
- Writ's production suite was not rerun because no Writ file changed; repository cleanliness was
  checked instead. No prescribed Build 1 acceptance command was omitted.

## What is established / what remains untested

Established: exact finite one-observation computation; strict deterministic local contracts;
whole-answer joint-mass/policy-enumeration checking; exact intended-input binding; fail-closed public
consumption; required fixtures and hostile behavior; deterministic frozen artifacts; and a reusable
local interface exercised by a separate program.

Untested: real-world model fidelity, research frequency/cost of prevented mistakes, independent
implementation or authorship, formal verification, cross-runtime/language behavior, external
acceptance/correction systems, long-term maintenance, actual multi-result mathematical composition,
and adoption across three suitable real tasks.

## Continue, simplify, redirect, or retire

Simplify for present use: the ordinary script earned the eight demonstrated protections at lower
maintained-code cost. Retain the candidate implementation, exact fixtures, checker, and tests as the
first executable Bellman substrate and as evidence for what a stronger boundary costs.

Continue the packaged boundary only when an actual consumer needs its strict decoder, separate
checker, stable diagnostics, or portable checked handoff. After three suitable real research tasks,
reassess reuse and maintenance. If no willing consumer appears, retire the component while keeping
the regression fixtures. Do not redirect to Vela, formal proof, or a richer solver without a
specific accepted-state or theorem bottleneck, and never widen `finite-one-observation.v1`.
