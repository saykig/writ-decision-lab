# RUN THIS NEXT — Repair and qualify Writ Decision Lab PR #1

## Assignment

Read `WRIT_PR1_REVIEW.md`, the original Build 1 contract, and the outer execute-and-challenge directive. Inspect the existing review branch of `saykig/writ-decision-lab`.

Reviewed baseline: `cd8016eda9ccf17ccda4cdb2c37b22f72660bf76`.

Reproduce the concrete findings, implement the smallest appropriate corrections, add regression tests, and produce an append-only review-response record. This is a repair and qualification run, not another architecture investigation or a new mathematical experiment.

## Authority and preservation

Work on the existing review branch in a clean, isolated checkout/worktree. If its head has changed, inspect the intervening diff and report which findings still apply; do not reset or overwrite unrelated work.

Local edits, tests, and local commits are authorized by execution of this packet. **Do not push, post a review, or merge without separate explicit authorization.** No Writ production changes, new remote repository, package publication, deployment, system toolchain installation, or global interpreter setting changes. Use an already available permitted CPython 3.13 runtime and record its patch version. If unavailable, do source work and report runtime verification blocked.

Preserve the original implementation report, original comparison output and verdict, and old result/source identities as historical evidence. Write new run outputs to new paths. Any current-status summary must distinguish original evidence from corrections. Do not claim the original report or 44 tests included newly added checks.

KL5/KL6 stopping decisions remain binding. Do not enlarge the mathematical profile, infer real-world inputs, or design another KL experiment. First-build scope is not a permanent ceiling on future engineering.

## Required repairs

### 1. Protect the checked snapshot

Reproduce ordinary nested mutations of `CheckedAnswer.answer` and the inconsistency between `CheckReport.record` and `CheckReport.status`.

Prevent exposed mutable data from altering what the checked wrapper summarizes or what the check record serializes. Use deeply immutable storage or protected snapshots with defensive-copy access; keep the solution small. Preserve all numerical values, labels, ties, impossible-event nulls, and the existing wire meaning.

Test top-level and nested mutation paths. Mutating a returned copy may be allowed, but must not mutate protected state or leave an altered answer presented under the original association. Include check-record consistency. Do not pretend this protects against malicious code with unrestricted process access.

### 2. Correct the source identity profile

Implement the governing packet's repository-relative logical paths such as `src/writ_decision_lab/__init__.py`. Independently reconstruct the manifest and aggregate hash, and test that paths identify the files from a fresh checkout root. Preserve relocation reproducibility.

Old digests belong to the historical implementation. Document the mismatch and the corrected profile; regenerate new evidence, never silently rewrite earlier identities. Do not hardcode the review's diagnostic digest as the repaired code's digest, since the repair changes source bytes too.

### 3. Make diagnostics safe and bounded

Reject unknown fields without echoing their arbitrary names or values in stored messages or paths. Examine Unicode validation as well as object-shape validation. Use schema-owned paths and fixed or bounded diagnostics; do not lose useful stable error categories.

Add synthetic canary tests for unknown/nested keys, invalid Unicode under unknown keys, and CLI stderr/check records. No real secrets should appear in test fixtures.

### 4. Enforce the JSON depth contract before recursive traversal

Add a deterministic bounded-depth strategy that rejects excessive nesting as `out_of_scope` with the designated depth diagnostic, rather than leaking `RecursionError` or returning `checker_error` for a known resource limit. Preserve distinct malformed-JSON rejection.

Exercise the documented depth boundary and much deeper syntactically valid JSON under normal and optimized execution. Do not change process-wide recursion settings to make the test pass. This repair does not claim comprehensive denial-of-service resistance.

## Close the verification gaps

Commit real tests for correlated wrong answers with correct input hashes; checker operation in a fresh process with producer-math calls disabled; escaped duplicate keys; positive whitespace/new-binding controls; and correct answers from a different declared producer source hash.

Run solve/check/consume from genuinely relocated source copies, not just different output directories. Propagate `-O` deliberately into child processes for the optimized checks. Exercise separate consumer success and failure cases: missing bytes, unsupported semantics, invalid inputs, stale result, wrong computation, and unexpected checker failure. Verify no functional output is written on each failure.

Build a named coverage matrix linking every original acceptance/challenge requirement to an executable test, command, or an explicit not-run status. Source-text grep is not a substitute for a producer-disabled execution check. Keep both required controls and negative cases; blanket refusal is not success.

## Qualify the baseline conclusion without changing history

Preserve the observed eight-step results and historical `BUILD1_SIMPLER_WORKFLOW_PREFERRED` verdict. Append the review's qualification: the comparison does not establish equal assurance or identify pure wrapper overhead.

Demonstrate the duplicate-label and duplicate-cost differences. Label any shared-algorithm fault injection as an injected failure, not a discovered natural arithmetic bug. State the baseline's intended input/trust contract and what guarantees are relinquished if it is selected. Do not inflate the baseline into a second package just to manufacture equality, and do not infer productivity or human maintenance cost from line counts alone.

Simplification is permitted where it preserves explicitly selected guarantees. No unsolicited rewrite is required for this repair.

## Deliverables and final gate

Deliver corrected code and regressions, fresh normal/optimized suite logs, the complete named challenge matrix, and `PR1_REVIEW_RESPONSE.md`.

For each R1–R6 finding, record: reproduced / not reproduced with evidence; smallest correction or justified bounded interpretation; exact test; final result; remaining limitation. Treat the host-installation discrepancy as source-reported execution governance, not a reason to alter the user's installed software.

Record the baseline and final commit, runtime, source manifest/digest, input/output identities, files changed, deviations, and any tests not run. Keep inherited, observed, derived, and hypothesized claims separate.

Finish with one of:

- `PR1_REPAIR_VERIFIED_LOCALLY`: all required corrections and declared gates pass.
- `PR1_REPAIR_PARTIAL_OR_BLOCKED`: some required correction or verification remains unresolved.

A verified local repair does not authorize merge, prove general correctness, or establish cumulative knowledge. Return the local commit and exact review evidence. Do not stop at a plan.
