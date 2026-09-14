# Writ Decision Lab PR #1 — adversarial review

**Disposition: REQUEST CHANGES before approving the declared Build 1 boundary.**

Reviewed repository: `saykig/writ-decision-lab`  
PR: `#1`, `codex/build-1-review` → `main`  
Exact head: `cd8016eda9ccf17ccda4cdb2c37b22f72660bf76`  
Base: `6936f37bc8e3c890e5d85c82a0e7745d03198eb5`  
Review date: 6 September 2026, America/Toronto.

The mathematical implementation survived the checks performed. This review found no candidate arithmetic error and no case where the unmodified checker accepted a well-formed, incorrect mathematical answer for the intended supported inputs. It did find a mutable checked-output boundary, an identity-profile mismatch, unsafe diagnostic echoing, a nesting-status defect, and missing durable evidence for some required challenges.

The eight-step baseline comparison reproduces. It does not establish that its 145-line implementation provides the candidate's 1,170-line assurance contract. Preserve the historical `BUILD1_SIMPLER_WORKFLOW_PREFERRED` verdict as a bounded engineering judgment, not as evidence that the separate checker is unnecessary or that this programme should stop.

No remote files, comments, reviews, branches, PR state, or Writ files were changed by this review. PR #1 was still open, unmerged, and at the exact head above when rechecked.

## 1. What was actually inspected and executed

GitHub connector reads covered all ten runtime Python files, the example consumer, baseline and comparison harness, fixture generator, test support and all seven test modules, and the specification, report, and handoff. The execution subset was reconstructed locally from fetched content; **22 Python files were verified against GitHub's Git blob hashes**. This was not a complete Git clone or a byte audit of all 74 changed files. Fixture files were regenerated with the verified generator; the generated manifest matched the pinned manifest's Git blob identity.

The reconstructed runtime's aggregate source association matched the report exactly:

```text
sha256:2ff46c7ae832a8b51d6bb038c3e324d7295950b820f3a9a5528e3ed2dc560431
```

Reviewer execution used **CPython 3.13.5**, not the author's 3.13.15. The original packet permits another 3.13 patch with a fresh record. Consequently, this review reproduces bounded behavior under a permitted patch; it does not claim identical runtime-dependent result hashes to the author's environment.

| Check | Observed result | Evidence |
|---|---|---|
| Original test suite, normal | 44 passed | `evidence/original_tests_normal.log` |
| Original test suite, optimized | 44 passed | `evidence/original_tests_optimized.log` |
| Frozen eight-step comparison | Both workflows passed; zero reported erroneous uses in that sequence | `evidence/comparison-rerun.json` |
| Additional integer-reference cases | 48 agreed on checked numerical quantities and minimizers | `integer_oracle_cases` in probe evidence |
| Additional review probes | 15 named groups, including defects and positive controls | Both `reviewer_probes_*.json` files |
| Relocated source-copy execution | Solve/check/consume artifacts identical between two source copies | `fresh_source_copy_reproduction` |

The 48 cases are fixed-seed engineering checks, not a new Kahneman Lab experiment, an uninspected holdout, a search for mathematical novelty, or an all-input proof. The reference computes using common-denominator integers without importing the candidate's decoder or mathematics helpers. Python execution and output JSON decoding remain shared dependencies.

Some initial reviewer execution attempts hit tool/process timeouts. They were rerun successfully; these were not classified as candidate defects or evidence of comparative performance. A transcription error while reconstructing a source file was detected by the blob-hash check and corrected before verified execution. Logs and source verification are included. Test durations are not productivity estimates.

## 2. Findings requiring correction

### R1 — Checked objects remain mutable after checking

**Priority: P2 — checked-state integrity. Confidence: high, reproduced.**

Locations: `src/writ_decision_lab/types.py:35–59`; `consumer.py:22–28`.

`CheckedAnswer` and `CheckReport` are frozen dataclasses, but their mappings contain ordinary dictionaries and lists. A caller can mutate their contents without reassigning the frozen field. `CheckedAnswer.summary()` then reads the modified contents.

Reproduction using the ordinary public interface and valid F01 inputs:

```python
checked = check_and_load(model_bytes, query_bytes, result_bytes)
bound_hash = checked.result_sha256
checked.answer['current_argmin'].clear()
checked.answer['current_argmin'].append('a1')
checked.answer['evsi'] = '999/1'
print(checked.summary())
assert checked.result_sha256 == bound_hash
```

Observed: the summary changes from action `a0`, EVSI `1/8`, to action `a1`, EVSI `999/1`, while the original result association stays unchanged. A nested list mutation requires no reflection or monkeypatching. An accidental consumer transformation can therefore retain the checked wrapper while changing what it exposes.

The same underlying issue lets `report.record['status']` disagree with `report.status`. The reviewer changed the record status to `computation_mismatch`; the attribute stayed `checked` while `report_bytes(report)` serialized the changed status.

**Limit:** this is not an untrusted JSON bypass of the checker. The original result still checks; altered result bytes are rejected. The wrapper is explicitly not a security capability against malicious code inside its own process. The issue is protection against ordinary mutation and misleading checked-state association.

**Minimal repair:** keep a deeply immutable internal snapshot, or expose defensive copies while deriving summaries and check serialization from protected state. Protect nested collections, not just the outer dictionary. Add tests for mutation attempts, mutations of returned copies, and consistent check-record serialization. Do not invent an in-process authentication framework.

### R2 — The source manifest does not use the promised repository-relative paths

**Priority: P2 — deterministic identity contract. Confidence: high, reproduced.**

Location: `src/writ_decision_lab/identity.py:40–57`.

`source_manifest()` takes paths relative to the `src` directory, yielding:

```text
writ_decision_lab/__init__.py
```

The actual repository path is:

```text
src/writ_decision_lab/__init__.py
```

The governing packet requires repository-relative paths, and the report claims that requirement. The emitted path does not resolve from the repository root. The existing regression checks only that the path is not absolute and contains no backslash; both incorrect and correct profiles pass that test.

On the current, unchanged source files, adding the specified `src/` prefix produces a different manifest digest:

```text
Current implemented profile:
sha256:2ff46c7ae832a8b51d6bb038c3e324d7295950b820f3a9a5528e3ed2dc560431
Repository-relative profile on those same pre-repair files:
sha256:48eb9cbae612f7dcfab409b93a0f898b88e1d0a649c542dac33650d1cc0da4fb
```

The latter is a diagnostic calculation, not the expected digest of repaired code: editing `identity.py` will itself change the source snapshot.

**Limit:** current identities are deterministic; this is not a hash collision or numerical error. It is a mismatch between documented and implemented identity profiles that another reader would reproduce differently.

**Minimal repair:** specify and implement stable logical repository paths, verify every manifest entry against a fresh checkout, and independently reconstruct the aggregate. Preserve previous outputs and digests as historical artifacts under the old implementation. Append the correction and generate newly identified evidence; never rewrite historical hashes to make them appear compliant.

### R3 — Diagnostics echo arbitrary untrusted field names

**Priority: P2 — diagnostic handling. Confidence: high, reproduced.**

Locations: `src/writ_decision_lab/decode.py:104–113`; related path construction at `52–62`.

The unknown-field error joins raw input keys into its message. The Unicode traversal also places arbitrary keys into diagnostic paths before schema validation.

The reviewer added the synthetic unknown key `REVIEW_ONLY_CANARY_DO_NOT_LOG` to a query. The checker correctly rejected the query, but its stored diagnostic contained:

```text
Unknown fields: REVIEW_ONLY_CANARY_DO_NOT_LOG.
```

This contradicts the stated aim of diagnostics that avoid secrets and machine-private paths. A value accidentally supplied as a key can be copied into a persistent check record or stderr. No actual credentials or private information were used or observed in this test.

**Minimal repair:** use generic bounded messages and schema-owned paths for unknown fields. Ensure early Unicode validation does not reintroduce arbitrary keys through its path. Test synthetic canaries in both message and path, including nested inputs and CLI output. Valid rejection must remain distinguishable from a checker failure.

### R4 — Excessive JSON nesting can bypass the typed depth rejection

**Priority: P2, lower impact — status/resource contract. Confidence: high under the tested runtime.**

Location: `src/writ_decision_lab/decode.py:73–101`.

The decoder runs recursive Unicode traversal before its depth check. Syntactically valid JSON consisting of 2,000 nested arrays around `0` is only 4,001 bytes, below the byte limit, but well above the declared 32-level limit.

```python
nested = b'[' * 2000 + b'0' + b']' * 2000
```

Under CPython 3.13.5's default recursion limit, direct `decode_json` raises `RecursionError`. The public checker converts that to `checker_error`, instead of the specified `out_of_scope` / `E_JSON_DEPTH`. Extremely deep parsing can also take the generic malformed-JSON exception path before the later depth check.

**Limit:** no mathematical answer is exposed. Failure remains closed. The defect is uncontrolled recursion and incorrect classification of a deterministic operational limit, not evidence of comprehensive denial-of-service vulnerability.

**Minimal repair:** enforce bounded depth before recursive traversal, using a bounded or iterative strategy; give excessive-depth input the specified status consistently. Preserve distinct malformed-JSON diagnostics. Add exact boundary and much-deeper regressions, including optimized subprocess execution, without changing the process-wide recursion limit.

## 3. Missing challenges and overbroad completion language

**R5 — Verification gap, not a demonstrated arithmetic failure. Confidence: high about committed coverage.**

The outer execute-and-challenge directive requires coherently wrong answers, a fresh process with producer mathematics disabled, a genuinely relocated source copy, and a named challenge matrix. The committed checker-separation test (`tests/test_checker.py:133–136`) merely searches source text for solver imports. The reproducibility test (`tests/test_cli.py:15–60`) changes output directories but still uses the original source tree and input locations. Its subprocess builder also omits `-O`, even when the enclosing suite runs optimized.

The report discloses that the outer file was unavailable to the implementation session. That explains the evidence gap; it does not turn the omitted executable challenges into completed checks. The original 44 tests genuinely pass, but that count is not evidence for every instruction in the missing directive.

The reviewer exercised the following additional controls successfully:

- A correlated edit to observed risk, EVSI, net value, and acquisition risk was rejected despite correct input hashes and consistent edited scalar relationships.
- With producer mathematics disabled in a fresh process, the valid saved answer still loaded and a tampered answer failed.
- A raw escaped duplicate key was rejected; changed whitespace required new binding; a different valid producer source hash did not prevent checking a correct answer.
- Separate consumer processes exposed output only for the valid case, and refused missing, malformed, unsupported, stale, incorrect, and injected-checker-error cases. Consumer and relocated-copy cases also ran with `-O` propagated.
- Two genuinely different source-directory copies produced identical result/check/consumer artifacts under the same runtime.

Commit durable regressions for these requirements. Record original execution, reviewer verification, and repaired-commit verification separately. Do not retrospectively enlarge the original 44-test claim.

## 4. What the simpler baseline does—and does not—establish

**R6 — Narrow the interpretation, preserving the historical comparison. Confidence: high on observed differences; moderate on the best workflow choice.**

The frozen eight-step test is equal-information and reproduces. The baseline is not secretly importing candidate code. Its lower source count is real. The report also explicitly admits unequal assurance and unmeasured human maintenance effort, which are important qualifications.

Nevertheless, the statement that the preference is “required” by the observation is too strong. A workflow that performs fewer checks and uses the same algorithm to produce and recheck an answer has a different assurance contract. Lines of code do not isolate the cost of a package interface from the cost of those additional checks.

Two direct probes demonstrate the difference:

1. **Duplicate outcome labels.** Giving the baseline F01 with outcome labels `['x', 'x']` produces and consumes two branches both called `x`, one choosing `a0` and the other `a1`, with EVSI `1/8`. The candidate rejects the input. This falls outside the declared unique-label profile; the baseline has not established equivalent protection at that boundary.
2. **Duplicate cost fields.** A raw query with both `"cost":"1/1"` and later `"cost":"0/1"` is accepted by the baseline using the latter value. The candidate rejects the duplicate. An ambiguity in an economically meaningful input is therefore silently resolved in the baseline.

A separate **deliberate fault injection**, not a naturally occurring baseline bug, changed its shared `_compute` function to calculate with cost `1/2` while keeping original cost-zero input bindings. Because production and consumption call that same function, both agreed on the incorrect net value `-3/8` and `act_now`. The candidate rejected the same claimed answer by separate recomputation. This illustrates a protection that exists beyond packaging.

These probes do not invalidate the eight original outcomes, prove a productivity advantage for the candidate, or require turning the baseline into a duplicate package. They limit its suitability as a replacement.

The defensible conclusion is:

> The smaller script suffices for the demonstrated trusted-fixture sequence. The stronger boundary has not demonstrated a productivity benefit, but the baseline has not demonstrated the same validation and fault-detection protections. Simplification remains a choice about retained guarantees, not a conclusion that those guarantees are unnecessary.

Keep `BUILD1_SIMPLER_WORKFLOW_PREFERRED` as the historical author's judgment and append this narrower review. Retain useful arithmetic, checking, fixtures, and consumer protections. Do not force new research to fit the tool, and do not use this small comparison to reject infrastructure whose additional responsibilities have not been evaluated.

## 5. Separate execution-governance observation

The build report says that Homebrew installed CPython 3.13 and upgraded local certificate/OpenSSL dependencies. The outer directive prohibited system toolchain installation and required blocked-runtime reporting if no permitted interpreter existed. The same report says that outer directive was unavailable.

This is **source-reported host activity**, not something independently checked on Sara's computer. No separate authorization was supplied to this review. Record it as an execution-scope discrepancy, not merely a Python patch-version difference. Do not uninstall or roll back host software as part of the code repair. Future runs should surface missing runtime authorization explicitly.

## 6. Recommended disposition and confidence

Request changes for the bounded contract defects and missing regression evidence. Keep this as a research implementation, preserve the historical comparison, and do not merge or promote it into Writ during the repair.

**High confidence:** the reproduced defects, original-suite results in the reviewer environment, and assurance differences described here. **Moderate confidence:** the proposed minimal repairs and the judgment that the comparison warrants narrower wording rather than abandonment. **Not established:** independent external validation, formal proof, all-input correctness, real-world model fidelity, user productivity, repeated adoption, or cumulative knowledge.

No new mathematical track, schema family, graph, registry, acceptance system, or KL5/KL6 reopening is needed to address these findings. Cumulative knowledge remains the destination; preserving a checked result's meaning through one real handoff is a legitimate foundational responsibility.

## Source and evidence register

All repository paths and line references above refer to the pinned head, not moving `main`.

- PR metadata: GitHub connector, PR #1; head and unmerged state checked twice.
- Runtime and test source: verified Git blob IDs in `source_verification.json`.
- Governing contracts: supplied `RUN_THIS_NEXT_WRIT_ENGINEERING_BUILD_1.md`, especially §§4–6 and 8–11; supplied outer execute-and-challenge directive §§3–5; pinned `SPEC.md`.
- Author-reported evidence: pinned `BUILD_1_REPORT.md`, `HANDOFF.md`, PR description. Not every historical claim was independently reproduced.
- Reviewer execution: accompanying `reviewer_probes.py`, JSON evidence, original-suite logs, and comparison rerun. Source reconstruction and fixture regeneration are disclosed above.
- Language-reference cross-check: official CPython 3.13 documentation for dataclasses and JSON. Frozen dataclasses do not recursively freeze field contents; JSON's default repeated-key handling is relevant to the baseline. The concrete findings were established against the inspected code and local probes, not inferred from documentation alone.

The accompanying reproduction script records findings in the original snapshot; it is **not** an after-repair acceptance suite. Convert its relevant cases into durable tests with the corrected expected behavior.
