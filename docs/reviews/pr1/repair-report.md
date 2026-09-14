# PR #1 repair report

PR1_REPAIR_PARTIAL_OR_BLOCKED

All seven repairs explicitly requested by the user are implemented and their local regression
gates pass. The conservative disposition reflects an evidence gap: neither referenced reviewer
probe script, their observation JSON, nor the original outer execute-and-challenge directive was
supplied or found locally. Their exact replay and a completeness audit against that unavailable
outer document cannot be claimed. The documented challenges were independently reconstructed and
made durable; this is not a claim to have executed the missing scripts. No implementation failure
remains in the declared local test matrix.

## Authority, scope, and commits

The user's request authorizes the union of the two repair packets, local work on
`codex/build-1-review`, and local commits. It expressly prohibits push, merge, and Writ changes.
The documents are supplied task material: repair requirements are adopted within that scope;
reviewer observations are inherited evidence until reproduced, not instructions to change scope.
The existing clean adjacent checkout was used; no branch or additional worktree was created.
Its existing isolation from Writ satisfies the packet's isolation purpose.

- Repository: `saykig/writ-decision-lab`, local `writ-decision-lab-build1`.
- Starting commit: `cd8016eda9ccf17ccda4cdb2c37b22f72660bf76`; exactly the reviewed head, no intervening diff.
- Final source/test commit: `3b0ca2b05cbd0118662e50034e99c75aa49ad4a5`.
- The following evidence-only commit contains this report, response, matrix, supplied source copies,
  handoff appendix, and logs. Resolve its full identity with
  `git log -1 --format=%H -- PR1_REPAIR_REPORT.md`; the final task response also gives that identity.
  A report cannot contain the hash of its own enclosing commit without a self-reference problem.
- Observed runtime: CPython **3.13.15**, integer-string limit **4300**. Existing
  `/opt/homebrew/bin/python3.13` was used without installation or global setting changes.
- Writ started clean on its own branch. Final read-only status is in `evidence/pr1-repair/writ-status.txt`.
- No push, merge, remote write, publication, deployment, KL extension, mathematical expansion,
  architecture redesign, or Writ edit was performed.

## Starting evidence and repair results

Evidence below is relative to `evidence/pr1-repair/`. The new `reproduce.py` was run against
untouched `cd8016e` source normally and with `-O`; its results are
`reproduced-normal.json` and `reproduced-optimized.json`. It is a reproduction aid for the original
source, intentionally not an acceptance test for the repaired source.
The original suite passed **44/44** in both modes (`original-normal.log`,
`original-optimized.log`), including the frozen comparison. Those 44 tests did not contain the
new process challenges. Final repair suites passed **60/60** normally and optimized
(`final-normal.log`, `final-optimized.log`); all child launchers deliberately pass `-O` when the
parent is optimized.

Numbering follows review A (`WRIT_PR1_REVIEW.md`); the other review's numbering is cross-referenced.
Exact executable names and both mode results are in `PR1_CHALLENGE_MATRIX.md`.

| Finding | Reproduction and scope | Smallest correction and exact regression | Final result / remaining limitation |
|---|---|---|---|
| R1 (both reviews): mutable snapshots | Summary changed to EVSI `999/1` and an added unchecked action; record status changed while typed status remained `checked`. | Recursively detach mappings into read-only mapping proxies and lists into tuples during construction; wire encoder accepts mappings and emits original JSON shapes. `RepairTests.test_deep_snapshots_and_summary_copies`, `test_check_record_snapshot_consistency`. | PASS in both modes. EVSI, minimizers, distributions, acquisition risks, ties, nulls, constructor aliases, summaries, and report diagnostics/subjects are covered. No sandbox against malicious process code. Python answer arrays now expose tuples. |
| R2 (review B R3): manifest path base | Original manifest emits `writ_decision_lab/...`, which does not resolve from the repository root. Old aggregate reproduced exactly. | Stable logical `src/writ_decision_lab/...` paths; explicit SPEC clarification. `RepairTests.test_manifest_independently_reconstructed_from_repository_root` and `RepairProcessTests.test_genuinely_relocated_sources_solve_check_consume`. | PASS; independent raw SHA-256/JSON manifest reconstruction, sorted entries, root resolution, and source relocation. Source association remains conditional on frozen source, not attestation. |
| R3 (review A): unsafe diagnostics | Unicode error under an unknown synthetic key copied that key into a persistent path. Source inspection also confirms raw unknown-key interpolation. | Fixed unknown-field message; early Unicode paths use `$`; byte-limit text no longer interpolates caller-supplied `kind`. Schema validation retains owned field/index paths and stable categories. `RepairTests.test_diagnostics_never_echo_untrusted_keys_or_values`, process `test_cli_depth_and_canaries_in_stderr_and_records`, `test_cli_nested_query_and_result_canaries`. | PASS for arbitrary unknown/nested keys, values, surrogate keys/values, API records, CLI records/stderr and consumer stderr. Only synthetic canaries used; input hashes remain intentionally recorded. No comprehensive secret-scanning claim. |
| R4 (review B R2): JSON depth | At 1100/2000 array containers direct decoding leaked `RecursionError`; checker returned `checker_error`. At 995 this runtime showed different direct/checker classifications because stack depth differs. | String/escape-aware linear preflight bounds JSON parser nesting; existing value-depth check runs before Unicode recursion. `RepairTests.test_depth_boundary_deep_arrays_objects_and_quoted_delimiters`, process `test_cli_depth_and_canaries_in_stderr_and_records`. | PASS for level 32, next level, 995/1100/2000 arrays/objects, quoted delimiters, syntax controls. Root and scalar depth semantics preserved. Once preflight exceeds the bound, resource rejection takes precedence over later syntax errors; documented in SPEC. No recursion setting changes or general DoS guarantee. |
| R5: durable verification gap | Original source had text-search separation and output-directory relocation tests; child launchers omitted `-O`. | Add correlated wrong-answer bundles with correct hashes, fresh-process producer disabling, all consumer statuses, relocation, positive whitespace/rebinding/different-source controls, byte/digit limits and escaped duplicates; repair existing CLI/comparison launchers. Exact matrix names identify each test. | PASS for all locally specified challenges. Exact missing reviewer scripts and unseen outer requirements remain NOT RUN / not audited. Additional fixed-seed reviewer oracle runs are inherited, not replayed or counted as new science. |
| R6: comparison interpretation | Original eight-step comparison passes; unchanged baseline additionally accepts duplicate outcome/action labels and escaped duplicate cost fields. Shared-calculation fault reproduced by deliberate injection. | Preserve old artifacts/verdict and append this qualification; `BaselineQualificationTests.test_duplicate_labels_and_escaped_cost_unequal_assurance`, `test_injected_shared_algorithm_fault_is_not_natural_bug`. | PASS; no natural arithmetic bug claimed. No equal-assurance, pure-wrapper-overhead, human productivity, or lifecycle-cost inference. |
| Review B R4: entire public consumer guard | Injected post-check decoder failure escaped as raw `RuntimeError`. | Guard check, status handling, decode, hashes, and snapshot construction together; preserve typed failures; map unexpected exceptions to fixed `CheckFailure(checker_error)` without exception text. `RepairTests.test_entire_consumer_boundary_structures_failures`, process `test_consumer_process_all_statuses_and_post_check_faults`. | PASS for checker, decoder, and snapshot-constructor injections. Each failed process produces no functional output; valid control does. Injections are tests of the boundary, not spontaneous runtime failures. |

## Fresh identities and historical preservation

Final runtime source digest:
`sha256:ed908ab025455918f41a80fd8689256486572a33255593c417fc7bf735dd74dd`.
The manifest test also passed from a fresh `git archive` export of the final source commit
in both modes (`fresh-source-manifest-normal.log`, `fresh-source-manifest-optimized.log`).
The complete independently tested profile is in `source-manifest.json`; `identities.json` records
runtime, source commit, exact input bindings, and all fresh output hashes.

| Artifact, same in normal and optimized fresh runs | SHA-256 |
|---|---|
| model bytes | `99f36e6aa9051c1584ecaad9489dd2cc60d39fadccc7c3cdf14cc2facef0b33e` |
| query bytes | `535fedc2dc34cd212a37b95469b721149f6402a9929d5fd2cabb5956ffc18c55` |
| result | `69ebfa76b8289b559e6b25e8888d505430794ed14b3f6c218f9503af17ba0deb` |
| check | `f85e91e4af1ddee661b5f5c01aa67fc9857e485bda6e3dd545d73e33ee12b188` |
| consumer | `c2f3f71bd443caafa5fd3614f86897a0dc44f3d938f993a0b0412b543dc3777c` |

Old digest `sha256:2ff46c7ae832a8b51d6bb038c3e324d7295950b820f3a9a5528e3ed2dc560431`
belongs to the original bytes/profile. The review's `sha256:48eb9c...` was a hypothetical
prefix-only correction on those old bytes, not the repaired source's expected identity.
Neither old identities nor `BUILD_1_REPORT.md`, baseline code, original fixtures, or `outputs/`
were rewritten. The historical result remains evidence under its original source association.
The numerical F01 answer is unchanged. New result/check/consumer bytes reside in `normal/` and
`optimized/`; independent relocated source copies also yield byte-identical artifacts in the test.

## Baseline qualification

Preserve historical **BUILD1_SIMPLER_WORKFLOW_PREFERRED** and all eight observed outcomes as the
original implementer's bounded preference judgment. Both arms again pass all eight steps with zero
reported erroneous uses in `comparison-normal.json` and `comparison-optimized.json`.
The sequence, fixtures, arithmetic expectations, and baseline code are unchanged. Four candidate
assertion expressions adapt tuple-backed checked arrays to list-value comparisons; no expected
answer was relaxed. Early repair suite runs exposed these representation-only assertion failures;
their logs remain under `development-*`. A subsequent 59-test pass predates the final added nested
CLI-canary test; final logs contain 60 tests, not an inflated duplicate inherited test count.

The baseline is suitable only if the caller explicitly selects a trusted, externally validated
input workflow: unique valid labels, unambiguous JSON object keys, valid scalar Unicode, canonical
rational values, normalized probabilities, supported dimensions/versions, and controlled byte and
depth limits. The script performs some checks itself but does not establish the full package input
boundary. Selecting it relinquishes the demonstrated duplicate-key/label rejection and separate
algorithm fault detection, as well as the package's protected checked snapshot and structured
public boundary. Production and checking share its `_compute` function.

The injected baseline fault computes cost `1/2` while retaining the original zero-cost input
binding. Its producer and consumer agree on false net value `-3/8` and `act_now`; the separate
checker rejects the transferred answer. This is **injected failure**, not a discovered natural
arithmetic defect. Differences in physical source size do not isolate wrapper overhead or measure
human maintenance, productivity, adoption, or lifecycle cost. Simplification is still reasonable
where retained guarantees or deliberately relinquished guarantees are explicit. No second package,
new experiment, or blanket candidate victory is justified.

## Claims, deviations, and remaining gate

- **Observed (high confidence within this execution):** exact initial commit/source identity;
  original 44-test passes; documented boundary reproductions; final 60-test passes in both modes;
  original and fresh comparison success; deterministic fresh artifacts; no Writ edits.
- **Derived:** the corrected manifest aggregate follows independently hashed repository-relative
  file bytes; tests support protection against ordinary nested mutation and the specified failure
  categories. They do not prove every possible program/input behavior.
- **Inherited/source-reported:** reviewers' 12/16/48 reference-case counts and GitHub/host observations;
  original engineering judgment; historical KL5/KL6 stopping decisions. Nothing here reopens them.
- **Injected/hypothetical:** unexpected checker/decode/snapshot failures and shared baseline math
  faults; these are explicit fault simulations. No spontaneous mathematical error was observed.
- **Governance discrepancy:** the old report says Homebrew Python and related dependencies were
  installed. The reviews report that the outer directive prohibited system toolchain installation.
  No separate authorization resolving this was supplied. This is source-reported host activity and
  an unresolved historical scope discrepancy, not a host audit. No software was installed, removed,
  rolled back, or globally reconfigured during this repair.
- **Unavailable / not run:** exact `review_probe.py`, `extra_probes.py`, `reviewer_probes.py`, and their
  observation JSON; exhaustive checklist comparison with the original outer directive. The four
  supplied documents and stored original Build 1 contract were read; their source copies/hashes
  are retained. Missing material was not fabricated. The new baseline probe and durable regressions
  implement the challenges described in the available packets.
- **Not claimed:** formal proof, externally independent validation, exhaustive security/DoS
  resistance, real-world input fidelity, mathematical expansion, cumulative knowledge, or merge
  readiness. No Writ commands were run because Writ was outside the authorized change scope.

The only remaining gate is exact source-limited reviewer replay/completeness audit. It requires the
missing artifacts; no new architecture or mathematical work is needed. A local repair does not
supply publication or merge authorization.

## Reviewable changes and commands

Runtime changes are confined to `types.py`, `identity.py`, `decode.py`, and `consumer.py`.
Other changes: SPEC clarification, tuple comparison compatibility in `comparison/run_sequence.py`,
optimized subprocess flags in existing CLI/comparison tests, new `tests/test_pr1_repairs.py`, and
append-only repair evidence/documentation. The baseline implementation is byte-unchanged.
`files-changed.txt` records the source commit's paths; the evidence commit adds the report artifacts.

```sh
PYTHONPATH=src /opt/homebrew/bin/python3.13 -m unittest discover -s tests -v
PYTHONPATH=src /opt/homebrew/bin/python3.13 -O -m unittest discover -s tests -v
PYTHONPATH=src /opt/homebrew/bin/python3.13 comparison/run_sequence.py --output NEW_NORMAL_PATH
PYTHONPATH=src /opt/homebrew/bin/python3.13 -O comparison/run_sequence.py --output NEW_OPTIMIZED_PATH
git diff --check
```

Use fresh output paths for CLI reproduction; creation-only writes remain in force. Exact
solve/check/consume invocations and source relocation are executable in `RepairProcessTests`.
