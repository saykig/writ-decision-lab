# PR1 current snapshot review

**PR1_CURRENT_SNAPSHOT_VERIFIED_WITH_ARCHIVAL_LIMITATION**

All nine obligations in this present bounded review passed source inspection and actual execution. No actionable current code defect was found in that scope. This is a new assessment of the exact snapshot below. The historical `PR1_REPAIR_PARTIAL_OR_BLOCKED` disposition remains unchanged; this review does not convert the original repair run into a historical pass.

The original reviewer scripts, their observation JSON, and the outer execute-and-challenge directive remain unavailable locally. Exact historical replay is **NOT RUN**; completeness against the unseen directive is **NOT ESTABLISHED**. This pass is limited to the available Build 1 contract, both supplied written reviews, and the nine obligations in the current request.

**Snapshot and runtime**

| Item | Observed identity |
|---|---|
| Reviewed checkout | `/Users/kimchee/Documents/writ-decision-lab-build1` |
| Original reviewed commit | `cd8016eda9ccf17ccda4cdb2c37b22f72660bf76` |
| Repair source/test commit | `3b0ca2b05cbd0118662e50034e99c75aa49ad4a5` |
| Resolved evidence commit and actual reviewed HEAD | `36b9bbf7dc3f92a647d9e6a341aa7334e0610cbd` |
| Ancestry | Original → repair → evidence/HEAD; both `git merge-base --is-ancestor` checks exited 0 |
| Working tree | Clean initially and after execution; all 112 tracked files match HEAD bytes |
| Interpreter command | `/opt/homebrew/bin/python3.13` |
| Resolved interpreter | `/opt/homebrew/opt/python@3.13/bin/python3.13` |
| Runtime | CPython `3.13.15 (main, Aug 5 2026, 12:25:43) [Clang 21.0.0 (clang-2100.1.1.101)]` |
| Integer-string limit | `4300`; unchanged |
| Current runtime source digest | `sha256:ed908ab025455918f41a80fd8689256486572a33255593c417fc7bf735dd74dd` |

There is no HEAD newer than the reported evidence commit. Relative to the repair commit, HEAD changes 37 paths: it appends 15 lines to `HANDOFF.md` and adds reports, matrix, supplied source copies, and repair evidence. It makes no runtime, test, fixture, or comparison-harness change. The full evidence-commit diff and original-to-HEAD diff are retained under `evidence/`.

This report and its scripts are newly created local review artifacts outside the checkout, under `/Users/kimchee/Documents/writ-decision-lab-current-review-20260907`. They are not part of any of the three prior commits. No production source was modified, no branch or commit was created, and no push, merge, remote repository, Writ edit, installation, or global interpreter change was performed. Process-local fault injection was confined to review processes. `PYTHONDONTWRITEBYTECODE=1` kept execution from creating Python caches in the source checkout.

**Material inspected and historical artifact search**

Read the original `sources/RUN_THIS_NEXT_WRIT_ENGINEERING_BUILD_1.md` packet, including its finite equations, wire and checking contracts, fixture definitions, execution/comparison obligations and archival appendix; the supplied engineering direction; current `SPEC.md`; both supplied written adversarial reviews and repair packets; `PR1_REPAIR_REPORT.md`, `PR1_REVIEW_RESPONSE.md`, and `PR1_CHALLENGE_MATRIX.md`; original `BUILD_1_REPORT.md`; all ten runtime modules; all current test modules/support; the example consumer; baseline and comparison harness; and relevant original diffs and preservation/identity records.

A single bounded historical-artifact search covered all supplied/local project working files, including ignored/hidden files outside `.git`, and path names in all locally reachable Git history. Its scope, requested names and matching references are in `evidence/historical-search.json`. It found references but no original `review_probe.py`, `extra_probes.py`, `reviewer_probes.py`, observation bundle, `source_verification.json`, or `RUN_THIS_NEXT_WRIT_BUILD_1_EXECUTE_AND_CHALLENGE.md`. No broader filesystem or remote recovery search was performed.

The available `evidence/pr1-repair/reproduce.py` identifies itself as a new repair-session probe, not an original reviewer script. It targets the original defects and is retained unchanged in the tracked export, with its exact SHA-256 in `TRACKED_SOURCE_SHA256SUMS`. It was not relabeled or run as repaired-source acceptance. The packet's archival `research_probe/spike.py` and old outputs were preserved rather than rerun over them. No hash guard was changed. No additional historical coverage is claimed merely from references in the supplied reviews.

**Per-obligation results**

| Obligation | Present result and reproducible evidence |
|---|---|
| 1. Diff, callers, mathematics and wire semantics | **PASS.** Runtime diff is confined to `types.py`, `identity.py`, `decode.py`, `consumer.py`. Solver and checker arithmetic, errors, CLI and example consumer are unchanged. Inspected the producer's posterior calculation, checker's joint-mass/whole-answer/policy path, report construction/serialization and public consumer. New `validate_export.py` executed all 16 existing fixtures against untouched original and current sources: results, statuses and policy counts are identical after removing only `producer.code_sha256`. No fixture numbers or limits were changed. See `fixture-compatibility.json` and both `fixture-results-*.json`. |
| 2. Full suite normal and optimized; child flags | **PASS.** Plain `unittest discover` ran **60 tests normally and 60 with `-O`**, all passing. An additional complete-suite run in each mode used a read-only audit hook to record actual subprocess arguments: **50 child launches in each**, all carrying the correct optimization mode. Existing fresh-process tests also read and assert `sys.flags.optimize` in children. These repeated executions are not 120 distinct tests. See `plain-suite-*.log`, `suite-*.log`, `suite-*.json`, and `run_suites.py`. |
| 3. Deep checked-answer/report protection | **PASS.** New `current_probes.py::test_01_snapshots_all_nested_collections` traversed **87 nested collections** across answer/report probes per mode, including F01, tied F07, impossible F08 and acquisition-tie F10. Mapping edits and tuple appends fail; deep edits to constructor inputs, wire copies, summaries and diagnostic dictionaries do not change retained state or serialization. Summary arrays retain JSON list shape. Supplementary `precedence_and_reports.py` verified typed and serialized status, policy count and diagnostics for **all seven statuses**. |
| 4. Manifest, raw hashes, aggregate, relocation | **PASS.** New probe 02 independently builds sorted `src/writ_decision_lab/...` entries from repository-relative paths, hashes raw file bytes, serializes the manifest using the specified JSON profile and hashes it. All **10 runtime files** and aggregate match production. Two genuinely relocated source/example trees per mode resolve imports from their own roots and produce identical solve/check/consumer bytes. Each manifest entry resolves and hashes correctly there. Normal and optimized artifacts also match. |
| 5. Depth, syntax, precedence and safe diagnostics | **PASS.** New probe 03 covers **29 depth/string/syntax cases** per mode: root/scalar level-32 boundary, empty leaf boundary, arrays/objects at 32/33/995/1100/2000 containers, quoted delimiters, escaped quotes/backslashes, malformed JSON, and preflight depth precedence over later malformed syntax/Unicode. Valid boundary controls decode. Deep inputs give `out_of_scope/E_JSON_DEPTH`; ordinary malformed cases give `invalid_input/E_JSON`. New probe 04 exercises **15 model/query/nested-result canaries** through API, persisted CLI check records and separate consumer stderr. Unknown keys, nested keys/values and surrogate keys/values are not echoed. The complete suite additionally exercises deep CLI cases and exact byte/digit limits. Supplementary precedence probes confirm inputs/scope → result syntax/version/shape → bindings → mathematics, with eight explicit controls. |
| 6. Entire consumer guard, including after successful checking | **PASS.** New probe 05 runs **13 separate processes per mode**: valid=0, missing=6, unsupported=3, invalid=2, stale=4, coherent wrong=5; injected checker, decoder, snapshot, and each of the three consumer hash operations=70; expected typed post-check decode failure=3. Trace files establish real `checked` results before every post-check injected fault and record actual optimization flags. Only valid input writes a functional summary. Failures leave no functional file or stdout, and internal exception canaries do not reach stderr. Durable tests separately check the public API's structured `CheckFailure` mapping and downstream sink non-use. |
| 7. Wrong answer with correct hashes, producer disabled, positive controls | **PASS.** New probe 06 uses the saved F01 result in a fresh process after disabling all solver-defined functions (`_argmin`, `calculate`, `solve_with_context`, `solve_bytes`). Valid public loading still succeeds. Mutually coherent false observed risk/EVSI/net/acquisition risk with correct input hashes fails `computation_mismatch`. Stale whitespace binding fails; correctly rebound unchanged mathematics with a different valid producer-source hash succeeds; original bytes still succeed. Fresh solving for whitespace-changed inputs also succeeds. This uses existing fixtures; no model-grid search or new oracle experiment was launched. |
| 8. Frozen eight-step comparison and qualifications | **PASS.** New probe 07 runs the current harness unchanged in both modes. Both arms pass all eight steps with zero reported erroneous downstream uses, and every step record equals `outputs/comparison.json`. The repair's list conversions only adapt the Python tuple API; the sequence and expected values remain unchanged. Baseline source is byte-identical to the original commit. Three independent duplicate-outcome/action/escaped-cost cases reproduce weaker baseline rejection assurance. An explicit shared `_compute` cost fault produces false net value `-3/8`/`act_now` in both baseline production and consumption; the candidate checker rejects that answer. This is injected behavior, not a naturally discovered baseline arithmetic defect. |
| 9. Preservation, identities and export | **PASS.** `validate_export.py` compares original/current Git blobs, current working bytes and archive members. All **47 protected historical paths**—original reports, fixtures, sources, baseline source, research probe and old outputs—are byte-unchanged; HANDOFF retains its entire original content with an appendix. All **112 tracked HEAD files** match the archive and working tree. New artifacts carry the selected runtime/source digest and exact input/result bindings; cross-mode and relocation byte equality is checked. Final export checks are recorded separately. |

The seven new unittest methods are grouped probes, not seven individual input cases or seven independent experiments. Their full names, failures/errors and observations are in `probes-*.log` and `{normal,optimized}/observations.json`. The logs show **7/7 groups passing in each mode**. No harness or source failure occurred during these current review runs.

**Code review conclusions and compatibility**

`types.py:36–43` recursively detaches JSON mappings into mapping proxies and sequences into tuples. The `CheckReport` and `CheckedAnswer` post-init paths snapshot incoming record/answer aliases. Checker `_report` constructs typed status/diagnostics/policy count from the same values placed in the record; freezing prevents subsequent ordinary nested mutation from splitting those representations. Public report production was checked across every status. Deliberately constructing inconsistent wrappers or bypassing frozen dataclasses in trusted Python is outside the stated ordinary-mutation boundary.

`identity.py:20–37` converts generic mappings and tuples back to ordinary JSON objects/arrays before deterministic encoding, preserving array order, exact rational strings, nulls, ASCII escaping, sorted keys and final LF. Python callers now receive **tuples instead of mutable lists** in checked answers/reports. This is a disclosed Python API compatibility change: direct list equality and mutating list methods require caller adaptation. It changes neither decision mathematics nor JSON wire arrays. Existing caller adaptations in `comparison/run_sequence.py` preserve their expected values.

`identity.py:41–60` emits the required logical repository-relative path prefix and hashes actual shipped source bytes. The resulting digest correction is a source identity/profile repair, not a refutation of previous numerical answers. Source association remains conditional on the frozen-source assumption, not execution attestation.

`decode.py:73–91` bounds container nesting before recursive JSON/tree work and tracks quoted strings/escapes. The subsequent value-depth check preserves scalar and empty-container depth semantics. At excessive preflight depth the resource diagnostic wins over later malformed syntax, as current SPEC explicitly states. Within supported depth syntax validation remains the JSON decoder's responsibility. Unicode traversal uses `$`; unknown-field diagnostics are generic; later paths use schema-owned names and indices. No uncontrolled input key/value interpolation was found in these diagnostic call paths.

`consumer.py:12–32` now guards checking, report status handling, second decode, all hashes and snapshot construction. It preserves `CheckFailure`, translates expected `WdlError`, and maps unexpected exceptions to the fixed internal diagnostic. The example consumes only after `check_and_load` returns. No saved check artifact is accepted as authority. Separate-process injected faults and direct API regressions support this inspected behavior.

**No current code findings require correction in the assessed scope.** No broader security subsystem, semantics version, theorem checker or implementation change is proposed.

**Fresh artifact identities**

The independently reconstructed runtime source digest is `sha256:ed908ab025455918f41a80fd8689256486572a33255593c417fc7bf735dd74dd`. This agrees with the repair report, but that agreement was established from raw current source bytes rather than presumed from the report.

| Artifact | SHA-256, excluding the `sha256:` prefix |
|---|---|
| F01 example model bytes | `99f36e6aa9051c1584ecaad9489dd2cc60d39fadccc7c3cdf14cc2facef0b33e` |
| F01 example query bytes | `535fedc2dc34cd212a37b95469b721149f6402a9929d5fd2cabb5956ffc18c55` |
| Fresh result | `69ebfa76b8289b559e6b25e8888d505430794ed14b3f6c218f9503af17ba0deb` |
| Fresh check | `f85e91e4af1ddee661b5f5c01aa67fc9857e485bda6e3dd545d73e33ee12b188` |
| Fresh consumer summary | `c2f3f71bd443caafa5fd3614f86897a0dc44f3d938f993a0b0412b543dc3777c` |
| Exact tracked HEAD archive, `tracked-source.tar` | `1375a96203fb697713eac6d87da314d1262e34bd3d6e3b077bed3fd3bdd8dbab` |

Fresh result/check/consumer files are retained under `evidence/normal/relocated-one/` and the corresponding optimized and second-relocation directories. Their source and input bindings are checked in probe 02. Historical source digest `sha256:2ff46c7ae832a8b51d6bb038c3e324d7295950b820f3a9a5528e3ed2dc560431` still belongs to the original implementation/path profile. Neither it nor original outputs were rewritten.

**Commands and reproduction**

All execution used the already available CPython 3.13 interpreter with process-local `PYTHONDONTWRITEBYTECODE=1`. The plain suite commands, run with cwd `/Users/kimchee/Documents/writ-decision-lab-build1`, were:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src /opt/homebrew/bin/python3.13 -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src /opt/homebrew/bin/python3.13 -O -m unittest discover -s tests -v
```

The review-only scripts and output location used for this run are exact local artifacts. Equivalent shell notation for their actual invocations is:

```sh
review_root=/Users/kimchee/Documents/writ-decision-lab-current-review-20260907
source_root=/Users/kimchee/Documents/writ-decision-lab-build1
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src /opt/homebrew/bin/python3.13 "$review_root/evidence/run_suites.py" . "$review_root/evidence"
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src /opt/homebrew/bin/python3.13 -O "$review_root/evidence/run_suites.py" . "$review_root/evidence"
PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 "$review_root/evidence/current_probes.py" "$source_root" "$review_root/evidence"
PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -O "$review_root/evidence/current_probes.py" "$source_root" "$review_root/evidence"
PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 "$review_root/evidence/precedence_and_reports.py" "$source_root" "$review_root/evidence"
PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -O "$review_root/evidence/precedence_and_reports.py" "$source_root" "$review_root/evidence"
PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 "$review_root/evidence/validate_export.py"
```

Use a **new** review output root for another run; the probes intentionally require new directories and CLI outputs. `validate_export.py` records its exact fixed-fixture command and source roots. All probe child invocations, exits, stdout and stderr are retained in `evidence/{normal,optimized}/commands.json`. They include the unchanged `comparison/run_sequence.py --output NEW_PATH` command, real relocated solve/check/consume invocations, and explicit `-O` in optimized children. `suite-*.json` records every actual suite child command without replacing its launcher.

Git identity/export checks used `git rev-parse`, `git log`, `git merge-base --is-ancestor`, `git diff`, `git status --porcelain=v1`, `git ls-tree`, `git show`, and:

```sh
git -C /Users/kimchee/Documents/writ-decision-lab-build1 archive --format=tar --output=/Users/kimchee/Documents/writ-decision-lab-current-review-20260907/tracked-source.tar 36b9bbf7dc3f92a647d9e6a341aa7334e0610cbd
```

`git diff --check` passed for the untouched working tree. The review does not impose a new whitespace/style gate on the historical source diff.

**Historical limits and interpretation**

Preserve `BUILD1_SIMPLER_WORKFLOW_PREFERRED` as the historical implementer's bounded judgment. Both workflows still pass the eight steps, but their assurance differs. The baseline requires a caller to choose and provide a trusted, externally validated input workflow; it does not supply the candidate's full duplicate-key/label, Unicode/resource, immutable-snapshot and structured public boundary guarantees. Both baseline production and consumption invoke `_compute`, so the deliberate shared fault survives its recalculation. The comparison measures neither equal-assurance implementation cost nor pure wrapper overhead, human productivity, adoption or lifecycle maintenance. Current timings remain machine observations only, not a new preference score or a candidate victory.

The original report says Homebrew installed CPython and upgraded certificate/OpenSSL dependencies. Both supplied reviews describe an outer prohibition on system-toolchain installation; separate resolving authorization has not been supplied. This is **source-reported historical host activity and an unresolved authorization discrepancy**, not a host audit. Passing current regression tests does not resolve it. This review used the installed runtime without installing, uninstalling or reconfiguring anything.

Original 44-test evidence, reviewer 12/16/48-case claims, GitHub observations and historical KL dispositions remain inherited/source-reported. The complete-suite runs, seven grouped probes, explicit precedence/status checks, 16 original/current fixture comparisons, Git ancestry, byte preservation and export checks described here are this review's own observations. Manifest aggregation and bounded code conclusions are derived from those bytes and observations. Internal-failure and shared-algorithm examples are explicitly injected tests. No fixed-seed reviewer oracle or missing original script is claimed as replayed.

**Export and stop gate**

`tracked-source.tar` is an exact export of all 112 tracked files at the reviewed HEAD, without `.git`, untracked files or files drawn from outside that commit. `TRACKED_SOURCE_SHA256SUMS` identifies every tracked file. The separately packaged `review-evidence.tar` contains this new report and review evidence; `EXPORT_SHA256SUMS` identifies both archives and the tracked-file manifest. `evidence/final-export-validation.json` records final archive and preservation checks. The report is deliberately outside the tracked-source archive because it was not present at that commit. No untracked/private working files were included.

The pass supports this **bounded research implementation only**. It does not prove all-input correctness, formal verification, independent authorship, real-world model validity, productivity, cumulative knowledge, or permission to merge into either repository. Work ends with this review and local export.
