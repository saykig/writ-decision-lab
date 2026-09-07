# Writ Decision Lab PR #1 — repair verified boundaries and close the evidence gaps

## Operator instruction

Work in the existing `saykig/writ-decision-lab` checkout for PR #1. Read the accompanying `PR1_ADVERSARIAL_REVIEW.md`, the two review probe scripts and their observation JSON, and the repository's governing material. Implement and test targeted repairs; do not return another architecture proposal.

Reviewed starting commit: `cd8016eda9ccf17ccda4cdb2c37b22f72660bf76`. Verify the actual current branch/commit and working-tree state. Preserve any new user work. If the head has advanced, report the difference and determine which findings still apply; do not reset or force-push.

This packet authorizes local source/test/documentation changes and local commits in this adjacent repository. It does **not**, by itself, authorize pushing, merging, changing Writ, changing repository visibility, publishing packages, deploying, installing a system toolchain, or modifying global Python settings. Return the local commit and reviewable diff; use any separately supplied current publication authorization only within its exact scope.

## What must remain fixed

Retain the finite one-observation model, exact rational quantities, complete minimizing sets, impossible-event nulls, intended-input byte binding, and separate mathematical checking. Do not reopen KL5/KL6, design KL7, introduce repeated observations, build cumulative infrastructure, add war data, or make this a Writ integration task.

Preserve the historical `BUILD1_SIMPLER_WORKFLOW_PREFERRED` record and its original evidence. A review qualification or corrected result must be appended and clearly attributed; do not silently change historical counts or replace old artifacts with newly calculated ones.

## 1. Reproduce before repairing

On the untouched reviewed source, run `review_probe.py` and `extra_probes.py` normally and under `python -O`, plus the original repository test suite. Use fresh output paths. Save the observed results, runtime, and source/commit identities.

The review probes intentionally demonstrate current defects. Do not change their recorded observations to manufacture agreement with desired behavior. Turn the relevant reproductions into normal regression tests with the desired assertions for the repaired implementation.

The reviewer ran CPython 3.13.5; the original build reports 3.13.15. Use an available supported CPython 3.13 patch and report it. Do not install or globally reconfigure a toolchain to obtain a preferred patch. If unavailable, make useful source progress and accurately mark runtime validation blocked.

## 2. Required repairs

### R1 — checked state must not silently mutate

Protect the retained nested contents of `CheckedAnswer` and `CheckReport`, not merely their top-level attributes. A consumer must not be able to mutate returned dictionaries/lists and then emit a summary or check record inconsistent with the checked artifact and status.

Use a small recursively immutable representation or defensive interfaces that isolate edits from the retained checked state. Keep mathematical behavior and wire formats unchanged. Make serialization work with the selected immutable representation. A returned editable copy must not mutate the checked snapshot.

Regression coverage must include EVSI, nested action/minimizer lists, branch distributions, record status versus typed status, and mutations to returned summaries/copies. This is protection against ordinary data mutation, not an attempt to sandbox malicious Python callers or prove authenticity.

### R2 — enforce depth limits before recursive work

Repair `decode_json` so every excessively nested input reaches a deterministic bounded-depth rejection before an unguarded Unicode/tree traversal can exhaust the interpreter stack. Preserve distinct syntax, Unicode, and resource-limit failures. Do not simply catch every exception as `invalid_input`, increase recursion limits, or weaken the 32-level contract.

Add tests around the declared depth boundary and substantially beyond it (for example 995 and 1100 nested containers) in the direct decoder, checker, and CLI. Include arrays/objects and delimiter characters inside valid quoted strings so any preflight is JSON-string aware. Normal and optimized execution must agree.

### R3 — implement the specified source-manifest path base

The original contract requires repository-relative paths for the shipped files under `src/writ_decision_lab/`. Correct the implementation that currently emits `writ_decision_lab/...`, and explicitly name the base in `SPEC.md`.

Add a test that entries contain the required `src/` prefix, resolve from the repository root, have exact raw file hashes, are deterministically ordered, and are relocation-independent. A test that merely rejects leading slashes/backslashes is insufficient.

Changing the source changes its hash. Do not hard-code the review's hypothetical prefix-only digest as the new final implementation digest. Preserve old results and source associations as historical evidence; generate fresh outputs with the repaired final source. Document this as a correction to implementation conformance, not as mathematical refutation of earlier numerical results.

### R4 — guard the complete public consumer operation

Ensure unexpected failures during the consumer's post-check decode/snapshot construction are converted to the documented structured `checker_error`, without exposing a functional answer or uncontrolled exception text. Preserve expected typed failures and their meanings.

Either guard the complete operation or use a small internal verified-snapshot path that avoids the second parse. Do not weaken fresh checking or expose a stored check record as authorization. Test injected failures both in the checker and after it returns successfully.

## 3. Finish the strengthened execution checks

Make the passing extra review probes durable regressions:

- Coherently wrong numerical bundles with correct input hashes, not only one-field edits.
- Fresh-process checking and public consumption with producer-math entry points disabled; valid results still pass and wrong results fail. Do not confuse missing-package errors with a mathematical dependency.
- Escaped duplicate keys, true byte/digit/depth limits, and positive controls at supported boundaries.
- Separate-process consumer missing/unsupported/malformed/stale/wrong-result failure paths, with no functional output.
- Whitespace changes: old bindings fail, fresh answers pass, and correctly rebound unchanged mathematics is not rejected merely because whitespace changed.
- Explicit optimized child processes. Running a parent test runner with `-O` must not be represented as optimizing children that were launched without it.

Construct a compact obligation-to-test/command checklist with pass/fail/not-run and evidence paths. Do not use an inflated test count as a substitute.

## 4. Keep the baseline comparison honest

Re-run the original eight-step comparison without redesigning it to favor either arm. Preserve equal substantive inputs and the recorded historical outcome. Report the stronger package checks separately from those eight steps.

The review's duplicate-label/escaped-key and deliberate producer-fault examples demonstrate unequal assurance. They do not show a current arithmetic bug in the unmodified baseline and do not establish productivity superiority of the candidate.

Qualify any recommendation to use the baseline with its actual trusted-input and same-algorithm-recomputation limits. Do not treat physical line count as an equal-assurance or lifecycle-cost comparison. Retain the possibility of a small separate checker/public function without protecting every wrapper. Do not delete the baseline or force the package to win.

## 5. Repair the evidence record without erasing history

Append a `PR1_REPAIR_REPORT.md` and update the handoff with pointers to it. Distinguish the inner Build 1 packet's original reported checks from the outer directive's additional obligations and the review's newly executed evidence.

The old report states that it installed Homebrew Python and dependencies. The outer directive in this conversation prohibited system-toolchain installation. Record that as a reported deviation unless a separately documented local authorization resolves it. Do not invent that authorization, claim an unobserved host audit, or automatically uninstall anything.

The repair report must include:

1. Initial exact source and regression results; each confirmed finding and its scope.
2. Smallest implemented repair and exact test proving it.
3. Original suite results and strengthened acceptance matrix, ordinary and optimized.
4. Final source identities and fresh deterministic artifacts; old artifacts preserved.
5. Candidate/baseline comparison and the assurance qualification.
6. Observed, derived, inherited, and hypothetical claims, with confidence and limitations.
7. Actual working-tree/commit state, commands not run, and any unresolved issues.

Finish the local repairs and verification in this run. Do not request another planning pass, expand the mathematical programme, promise later background work, or claim formal proof/external validation. Do not merge PR #1.
