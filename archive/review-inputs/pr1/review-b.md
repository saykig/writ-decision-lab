# Writ Decision Lab PR #1 — adversarial review

**Disposition: request targeted changes before merging. Preserve the implementation and the historical result; do not expand or restart the programme.**

Reviewed repository: `saykig/writ-decision-lab`  
PR: `https://github.com/saykig/writ-decision-lab/pull/1`  
Pinned head: `cd8016eda9ccf17ccda4cdb2c37b22f72660bf76`  
Base reported by GitHub: `6936f37bc8e3c890e5d85c82a0e7745d03198eb5`

## 1. Judgment

The implementation is more substantive than a hash wrapper. The producer evaluates posterior losses; the checker separately evaluates joint-mass identities and every deterministic observation policy. The public consumer requires independently supplied intended inputs and checks afresh. These mechanisms survived the additional mathematical and input-binding attacks executed in this review.

The audit reproduced boundary defects and identified a qualification needed for the completion/evaluation claims. These are not a counterexample to the decision mathematics and are not grounds to abandon the engineering programme. The appropriate next action is a small repair and regression pass on PR #1, not another architecture investigation.

The historical `BUILD1_SIMPLER_WORKFLOW_PREFERRED` verdict may remain as a documented implementer judgment about the eight-step workflow. It must not be promoted into evidence that the 145-line script provides the same assurance as the package, or that a separate checker has no value. The committed report already discloses this distinction; it should govern the practical recommendation as well.

## 2. Evidence and access

GitHub confirmed that PR #1 was open and unmerged, with the exact requested head. The review read its description and changed-file inventory; the complete ten-file runtime; the consumer example; baseline and comparison harness; all seven original test modules and their support module; the fixture generator; and `BUILD_1_REPORT.md`, `HANDOFF.md`, and `SPEC.md`. The original Build 1 packet and the outer execute-and-challenge directive were also available in this conversation.

Direct network retrieval from the execution container failed at DNS resolution. Rather than substitute a rewritten implementation, the review reconstructed the retrieved runtime files, baseline, and example in an isolated local snapshot and verified **all 12 files against their exact Git blob hashes**. The reconstructed ten-file runtime also produced the same reported source association:

```text
sha256:2ff46c7ae832a8b51d6bb038c3e324d7295950b820f3a9a5528e3ed2dc560431
```

This is exact-source execution of those files, not a complete Git clone. The original 44-test suite was read but **was not rerun by this reviewer**. Its reported 44 normal and 44 optimized passes remain implementer-reported evidence. The results below come from separate executed review probes instead.

Review runtime: **CPython 3.13.5**. The implementer reported **3.13.15**. Both are permitted patches in the original Build 1 specification. The review probes were executed under ordinary Python and `python -O`; their observations agreed apart from the recorded optimization flag. Child-process probes explicitly propagated `-O`.

No source files on GitHub, review state, branch, PR, Writ checkout, or user-local files were changed by this review. This review cannot independently verify the cleanliness of the developer's Mac, its Homebrew changes, or a comprehensive secret scan of all historical files.

## 3. Executed checks that passed

| Review check | Observed result | Scope |
|---|---|---|
| Exact source identity | All 10 runtime files, baseline, and consumer example matched GitHub blob IDs. | The executed files, not a whole-clone or supply-chain attestation. |
| Fixed mathematical cases | All exposed answer fields agreed with a separately written integer-policy reference on 12 required and 4 development fixtures. The original 12 contain 68 policies; the largest development case contains 4096. | Fixtures were recreated from the explicit packet/committed generator definitions. No KL grid search. |
| Both eight-step workflows | Both candidate and baseline reproduced the eight requested behaviors. | Separately written review harness, not a productivity study. |
| Whole-answer attacks | 52 answer/structure mutations were rejected as `invalid_input` or `computation_mismatch`. | Correlated development attacks, not 52 independent experiments. |
| Coherently wrong scalars | A forged result with mutually consistent but false observed risk, EVSI, net value, and acquisition risk was rejected. | Correct input hashes were retained. |
| Wrong full answer | A correct answer for F02, rebound to F01, failed mathematical checking. | More than a one-field consistency check. |
| Producer disabled | In a fresh process, making all producer-math entry points raise did not prevent checking a valid saved result or refusing a wrong one through the public interface. | The package and source files remained present; no artificial packaging failure. |
| Shared decoder | Six raw attacks, including escaped duplicate keys, numeric/boolean rational fields, a surrogate, NaN, and a noncanonical fraction, were rejected. | Normal and optimized runs. |
| Byte limits | Exactly 1 MiB of valid input and exactly 4 MiB of valid result bytes passed; one byte over each limit was `out_of_scope`. | Valid JSON plus trailing whitespace, not a reject-everything control. |
| Consumer processes | Valid input exited 0 and wrote a summary. Missing, unsupported, malformed, stale, and coherently wrong cases exited 6, 3, 2, 4, and 5 without a functional output. | Actual separate consumer processes. |
| Relocation/reproduction | Solve/check/consume artifacts matched across two temporary working directories. | Same retrieved source and review runtime. |
| Whitespace meaning | Old binding failed after whitespace changed; fresh calculation and correctly rebound numerically unchanged result passed. | Byte mismatch was not confused with a mathematical difference. |

The oracle uses integer-scaled joint losses for exhaustive policy comparisons and Python `Fraction` for normalized outputs. It shares the mathematical specification, runtime, and rational library with the implementation. This is an additional review computation, not a formal proof or an externally independent scientific replication.

## 4. Findings

All code locations below refer to the pinned commit. Severity is scoped to this bounded research tool; no internet-facing deployment or operational policy use is assumed.

### R1 — A checked object can silently cease to represent its checked bytes

**Priority: P2 — checked-state integrity / accidental-mutation protection.**  
Locations: `src/writ_decision_lab/consumer.py:22–27`; `src/writ_decision_lab/types.py:35–58`; `src/writ_decision_lab/checker.py:33–61`.

The dataclasses are frozen, but their `answer` and `record` fields hold ordinary mutable dictionaries and nested lists. The public consumer returns the decoded dictionary without freezing it. `summary()` subsequently reads that mutable structure.

Executed reproducer:

```python
checked = check_and_load(model_bytes, query_bytes, result_bytes)
original_identity = checked.result_sha256
checked.answer['evsi'] = '999/1'
checked.answer['current_argmin'].append('never_checked')
print(checked.summary())
print(checked.result_sha256 == original_identity)
```

Observed: the summary reported EVSI `999/1` and the added action, while the result hash remained unchanged. The original saved result's EVSI was `1/8`.

The same issue exists for `CheckReport`: after mutating `report.record['status']`, serialized report bytes use the modified status while `report.status` remains `checked`. There are two disagreeing representations of one check object.

**Qualification:** this does not show that the numerical checker accepted wrong result bytes. It also does not create a security boundary against a caller who deliberately rewrites trusted Python code; the packet explicitly excludes that goal. It is an ordinary post-check mutation hazard, especially when consumers pass the returned nested mapping to another helper. Freezing the outer dataclass is not enough to prevent it.

**Repair:** expose a recursively immutable checked snapshot or defensive views/copies whose edits cannot alter the retained checked state. Keep the check's status and serialized record consistent. Add nested mutation regressions, not only attribute-reassignment tests. Preserve the existing JSON wire shapes and mathematics.

### R2 — Depth-limit inputs escape the promised failure classification

**Priority: P2 — deterministic input/failure contract.**  
Location: `src/writ_decision_lab/decode.py:83–100`.

`decode_json` recursively calls `_check_unicode` before its guarded depth check. For sufficiently deep but small valid JSON, that Unicode walk raises an unhandled `RecursionError`. The checker converts this into an internal `checker_error` rather than the promised `out_of_scope` depth rejection.

On the review runtime:

| Nested array containers | Direct decoder result | `check_bytes` result |
|---:|---|---|
| 33 | `out_of_scope` | `out_of_scope` |
| 500 | `out_of_scope` | `out_of_scope` |
| 990 | `out_of_scope` | `out_of_scope` |
| 995 | `RecursionError` | `checker_error` |
| 1000 | `RecursionError` | `checker_error` |
| 1100 | `RecursionError` | `checker_error` |

The 995-container JSON is only 1,994 bytes, well below the file-size cap. The precise recursion threshold is environment/call-stack dependent; the structural defect is not.

**Qualification:** these cases still fail closed. They do not expose a wrong answer. The failure is the advertised distinction between an unsupported input and a broken checker, plus a raw exception at the decoder interface. The packet specifically assigns exceeded deterministic limits to `out_of_scope`.

**Repair:** enforce the structural depth bound before any unbounded recursive traversal, preferably using a bounded iterative walk or a correctly string-aware depth preflight. Keep JSON syntax errors distinct. Test near the documented limit and far beyond it in the direct API and CLI, under normal and optimized Python. Do not change the interpreter recursion limit or simply map every exception to `invalid_input`.

### R3 — The source identity is computed using the wrong path base

**Priority: P2 — conformance with the selected source-association contract.**  
Location: `src/writ_decision_lab/identity.py:40–57`.  
Normative source: original Build 1 packet, identity section: manifest paths are repository-relative, for shipped files below `src/writ_decision_lab/`.

The implementation sets `src_root = base.parent` and writes paths relative to that directory. Its first path is:

```text
writ_decision_lab/__init__.py
```

The required repository-relative path is:

```text
src/writ_decision_lab/__init__.py
```

The published relative-path test only checks that the string is not absolute and contains no backslash. It does not check that it resolves from the repository root or matches the prescribed manifest representation.

For the exact old source bytes, merely applying the prescribed prefix changes the manifest digest from:

```text
actual:       sha256:2ff46c7ae832a8b51d6bb038c3e324d7295950b820f3a9a5528e3ed2dc560431
contract:     sha256:48eb9cbae612f7dcfab409b93a0f898b88e1d0a649c542dac33650d1cc0da4fb
```

The second value is **not** the future repaired implementation's digest: changing `identity.py` changes its own source bytes too. It isolates today's encoding disagreement.

**Qualification:** the current scheme is internally deterministic, and its hashes agree within its own convention. This finding is not a cryptographic collision or incorrect decision result. It is an undocumented divergence between a normative identity profile and its implementation.

**Repair:** implement the originally specified path convention and add a golden manifest/path-resolution test. Preserve old artifacts as historical outputs; generate new outputs from the final repaired source. Do not silently rewrite old hashes or claim the old outputs used the repaired profile. The abbreviated local `SPEC.md` should name the base explicitly rather than leaving “relative” ambiguous.

### R4 — The public consumer's final decoding step is outside its error guard

**Priority: P2 — structured failure behavior, observed under fault injection.**  
Location: `src/writ_decision_lab/consumer.py:12–28`.

The checker invocation is guarded, but the second `decode_result(result_bytes)` and subsequent construction are outside that guard. With a simulated unexpected failure in that second decode, the public `check_and_load` raises raw `RuntimeError`, not `CheckFailure(status='checker_error')`.

```python
with patch('writ_decision_lab.consumer.decode_result',
           side_effect=RuntimeError('simulated second-decode failure')):
    check_and_load(model_bytes, query_bytes, result_bytes)
```

Observed: raw `RuntimeError`. The existing regression only injects a failure in `consumer.checker.check_bytes`, the portion already guarded.

**Qualification:** the separate example program has a catch-all and still fails closed. There is no demonstrated wrong-answer release. This finding concerns the public Python API's advertised stable failure behavior. The second failure is injected, not observed spontaneously for valid immutable bytes.

**Repair:** cover the entire public check/decode/snapshot boundary with the intended structured failure mapping, without concealing existing typed failures or weakening checking. Alternatively, avoid the second parse through a small internal verified-snapshot handoff. Do not expose unchecked data or use stored check records as authority.

## 5. Completion and protocol qualification

The committed report says that the outer `RUN_THIS_NEXT_WRIT_BUILD_1_EXECUTE_AND_CHALLENGE.md` file was unavailable as a separate attachment. It reports implementing the inner packet and the visible instructions. That is a disclosed limitation, not evidence of dishonesty.

However, the broader completion claim must distinguish the inner packet's test suite from the outer directive's strengthened acceptance matrix. The published tests inspect checker imports with string searches; they do not perform the requested fresh-process producer-disabled check. They contain one-field mutations and wrong-answer rebinding, but not the specifically requested coherently wrong scalar bundle. Several full consumer failure paths are covered at different layers rather than all through the requested separate process.

This review executed those additional checks, and they passed. That supplies new evidence now; it does not mean they were part of the original 44-test acceptance run. Add durable regressions and a per-obligation checklist rather than retroactively renaming the old evidence.

The report also states that Homebrew Python and related dependencies were installed. The outer directive available in this conversation expressly prohibited installing a system toolchain. This is a **source-reported environment deviation**, not something the reviewer could independently inspect on the developer's Mac. Whether the local session had additional separate user authorization is unknown. Record the applicable authorization accurately; do not automatically uninstall or roll back the user's tools.

Finally, the original subprocess tests construct child commands with `sys.executable` without passing `-O`. A parent suite run under `python -O` does not itself establish that those child processes used optimized mode. This review explicitly propagated the flag; ordinary and optimized review observations matched. The repository's own tests should do so when claiming child-process optimized coverage.

## 6. What the baseline comparison actually establishes

The ordinary script and candidate both completed the eight documented steps in the review harness. Both also matched the integer-policy oracle on all 16 fixed cases. There is no evidence here of an incorrect ordinary baseline calculation on the original valid fixtures.

The assurance difference is concrete:

| Additional review probe | Candidate | Baseline |
|---|---|---|
| Duplicate action labels in query | `invalid_input` | Produces and consumes an answer |
| Conflicting cost keys, with the duplicate spelled using a Unicode escape | `invalid_input` | Uses the decoder's surviving value and consumes the result |
| Deliberately injected wrong producer calculation | Separate checker returns `computation_mismatch` | Same altered calculation is used for production and recomputation; the false EVSI is returned |

The last row is **fault injection**. It demonstrates common-mode error exposure; it does not assert that the unmodified baseline presently has that arithmetic bug. The first two rows demonstrate limitations of its intentionally smaller input boundary. The report already says that the candidate provides stronger decoding and a separate checker.

Therefore:

- Preserve the observed eight-step comparison and the historical preference judgment.
- Describe the 145-line baseline as a candidate for explicitly trusted, validated-input workflows, not a general substitute for the full checked boundary.
- Do not infer implementation equivalence, lifecycle cost, productivity, or future adoption from 145 versus 1,170 physical source lines. The files use notably different formatting densities and provide different protections.
- Do not reverse the experiment into a claimed candidate victory. The review identifies a real assurance tradeoff, not a measured productivity benefit.

A useful near-term direction is to retain the tested arithmetic and separate-checker mechanism while simplifying wrappers only where their guarantees are preserved or their loss is explicitly accepted. No atlas, graph system, new mathematical branch, or Writ integration is required to fix this PR.

## 7. Confidence

**High:** the exact runtime identity, fixed-fixture arithmetic agreement, reproduced boundary behavior, preserved failure-before-consumption controls, and the explicit difference between the baseline's and candidate's checking algorithms.

**Moderate:** the recommendation to repair and retain the separate-checker capability while qualifying the present baseline preference. It depends on what the next actual consumer needs.

**Not established:** all-input correctness, an externally independent verification, formal proof, comprehensive security, research productivity, cumulative knowledge, adoption, or the correctness of the developer's account of local machine changes.

## 8. Reproduction

Use an unchanged local checkout of the pinned commit and CPython 3.13. Run the supplied scripts outside the package source directory:

```bash
python review_probe.py --repo /path/to/writ-decision-lab --output observations.json
python -O review_probe.py --repo /path/to/writ-decision-lab --output observations-opt.json
python extra_probes.py /path/to/writ-decision-lab extra.json
python -O extra_probes.py /path/to/writ-decision-lab extra-opt.json
```

`review_probe.py` verifies its 12 executed source files against pinned Git blob IDs and refuses changed versions. `extra_probes.py` assumes the same checkout was already verified. Both scripts create only explicit observation outputs and disposable temporary files. The defect observations deliberately record current failures; they are not a replacement for post-repair regressions with the desired behavior.

The bundle includes the actual normal/optimized JSON observations. The code snapshot is not included; use the user's repository.

## 9. Source register

All repository paths are anchored to `cd8016eda9ccf17ccda4cdb2c37b22f72660bf76`.

- PR metadata and changed-file inventory: GitHub connector, read only.
- Runtime: all ten `src/writ_decision_lab/*.py` files; verified blob IDs are in the observation JSON.
- Consumer and comparison: `examples/consume_answer.py`, `comparison/baseline.py`, `comparison/run_sequence.py`.
- Original tests: `tests/support.py` and all seven `tests/test_*.py` modules; inspected, not rerun as a suite.
- Definitions: `fixtures/generate.py`, `SPEC.md`, original Build 1 packet in this conversation.
- Claims: `BUILD_1_REPORT.md`, `HANDOFF.md`, PR description; developer-machine claims are source-reported.
- Execution authorization: outer execute-and-challenge directive supplied in this conversation; not claimed to have been available in the prior local executor's filesystem.
- Primary Python documentation consulted: `https://docs.python.org/3.13/library/dataclasses.html` and `https://docs.python.org/3.13/library/json.html`. The former describes the scope of frozen-field protection; the latter documents JSON decoder behavior and implementation limits. The concrete findings above were established by source inspection and local probes, not inferred solely from documentation.
