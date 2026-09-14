# PR #1 named challenge matrix

Paths below are repository-relative. Evidence is in `evidence/pr1-repair/`.
Normal command: `PYTHONPATH=src /opt/homebrew/bin/python3.13 -m unittest discover -s tests -v`.
Optimized command adds `-O` immediately after the interpreter. Full final logs are
`final-normal.log` and `final-optimized.log`: 60 distinct tests each. The original logs contain
44 tests each; no newly added obligation is attributed to those original runs.
The inventory was derived from actual final log lines and matched between modes.
No source-text grep is used as evidence of producer-disabled execution.

## Obligation coverage

| Original Build 1 / supplied repair obligation | Executable coverage or evidence | Status |
|---|---|---|
| §§3–5 exact F01 whole answer, F01–F12 plus D01–D04; ties/nulls/large intermediate rationals | All `test_solver.SolverFixtureTests` entries below; unchanged fixtures and specification | PASS both modes |
| §8 simultaneous state/action/outcome permutations, scaling losses and cost, constant loss translation; stale-byte refusal | All `test_metamorphic` entries below | PASS both modes |
| §§4,8 strict rational spellings, dimensions, cost, state order, labels, normalization, negative probabilities, Unicode/BOM/NaN/trailing data, closed fields, unsupported semantics | All `test_decode` entries below (use exact names in inventory); new canary and duplicate-key tests | PASS both modes |
| Declared input/result digit, byte, depth and policy limits with positive controls | `RepairTests.test_exact_byte_digit_limits_and_escaped_duplicate`, `test_depth_boundary_deep_arrays_objects_and_quoted_delimiters`; original decode limits, solver D04 and intermediate tests | PASS both modes |
| §8 each exposed scalar/array/branch field, omitted minimizers, impossible nulls, joint posterior/risk identities | Original `test_checker` mutation and identity entries | PASS both modes |
| §8 intended model/cost/loss/action/whitespace changes; wrong-answer rebindings; original historical validity | Original changed-input/rebinding tests plus `RepairTests.test_positive_whitespace_rebinding_and_other_producer_source` | PASS both modes |
| §§5,8 ignore forged/deleted/modified stored check authority; downstream sink untouched on failure | `ConsumerTests.test_forged_saved_check_cannot_grant_access`, `test_downstream_sink_spy_is_not_called_on_any_failure`; process success without any saved check input | PASS both modes |
| §§5,8 public API and separate consumer fail closed | `RepairProcessTests.test_consumer_process_all_statuses_and_post_check_faults`: success; missing=6, unsupported=3, invalid=2, stale=4, wrong=5, checker/decode/snapshot faults=70; no output on each failure | PASS both modes |
| Full post-check API guard; preserve expected typed failure | `RepairTests.test_entire_consumer_boundary_structures_failures` | PASS both modes |
| Deep snapshot protection, copies, constructor aliases, report consistency, ties/nulls, summaries | `RepairTests.test_deep_snapshots_and_summary_copies`, `test_check_record_snapshot_consistency` | PASS both modes |
| Repository-relative manifest, exact hashes, sorted paths, independent aggregate reconstruction, relocated root resolution | `RepairTests.test_manifest_independently_reconstructed_from_repository_root`, relocated-process test; `fresh-source-manifest-*.log` from a git archive export of the source commit | PASS both modes |
| Safe diagnostics: unknown/nested keys/values, invalid Unicode under unknown keys and in keys, persisted JSON/stderr | `RepairTests.test_diagnostics_never_echo_untrusted_keys_or_values`; process `test_cli_depth_and_canaries_in_stderr_and_records`, `test_cli_nested_query_and_result_canaries` | PASS both modes |
| Depth 32, next level, 995/1100/2000; arrays/objects, strings/escapes; distinct malformed syntax; direct/check/CLI | `RepairTests.test_depth_boundary_deep_arrays_objects_and_quoted_delimiters`, process `test_cli_depth_and_canaries_in_stderr_and_records` | PASS both modes |
| Correlated false observed-risk/EVSI/net/acquisition bundle with correct hashes | `RepairTests.test_correlated_wrong_answer_correct_hashes`; producer-disabled/process wrong cases | PASS both modes |
| Fresh process with all solver-defined producer entry points disabled: valid public load succeeds, wrong fails | `RepairProcessTests.test_fresh_process_producer_disabled` (inspects and replaces solver-defined functions, checks actual child optimization flag) | PASS both modes |
| Positive whitespace: fresh and correctly rebound unchanged mathematics; alternate declared producer source | `RepairTests.test_positive_whitespace_rebinding_and_other_producer_source` | PASS both modes |
| True source relocation: copied source trees and inputs, local source PYTHONPATH, solve/check/consume processes, manifest/file hashes | `RepairProcessTests.test_genuinely_relocated_sources_solve_check_consume` | PASS both modes |
| Explicit optimized child processes; normal/optimized artifacts identical | New process launcher and original CLI/comparison launchers pass `-O`; child mode assertions; `normal/` vs `optimized/` artifact hashes in identities | PASS |
| Creation-only outputs, missing-input check record, consumer public-only integration | Original `test_cli` entries and `examples/consume_answer.py` source inspection | PASS both modes |
| §9 equal-information original eight-step sequence, zero erroneous uses | `ComparisonTests.test_equal_information_frozen_sequence`; `comparison-normal.json`, `comparison-optimized.json` | PASS both modes |
| Baseline duplicate outcome/action labels, escaped conflicting cost key; injected shared-algorithm fault | Both `BaselineQualificationTests` below; baseline source unchanged from reviewed commit | PASS both modes |
| Preserve historical verdict/counts/artifacts; qualify assurance and cost inference | Report and handoff appendix; `preservation.json` checks baseline bytes, original outputs, report and fixtures unchanged | PASS |
| Original source reproduction and original 44-test results | `reproduced-normal.json`, `reproduced-optimized.json`, `original-normal.log`, `original-optimized.log`; new original-source probe retained | PASS, equivalent local reproductions |
| Exact original reviewer scripts/JSON and complete original outer directive audit | Not supplied or found; no claim that reconstructed checks are the original scripts | NOT RUN / source unavailable |
| Reviewer fixed-seed integer oracles / external source reconstruction claims | Inherited review observations, not necessary to change mathematics; not repeated as a new experiment | NOT RUN |
| No Writ edits, architecture/math expansion, global settings/tool installation, push/merge | Scope diff, `writ-status.txt`, command record; no runtime setting mutation or network test calls introduced | PASS scoped local inspection |
| §11 reports, source/runtime/input/output identities, evidence classifications, limitations, handoff | Both reports, this matrix, `source-manifest.json`, `identities.json`, supplied source register | COMPLETE with explicit missing-source gate |

## Exact executable inventory

| Test | Source | Normal | Optimized |
|---|---|---|---|
| `test_checker.CheckerAdversarialTests.test_changed_intended_inputs_and_whitespace_refuse_old_result` | `tests/test_checker.py` | PASS | PASS |
| `test_checker.CheckerAdversarialTests.test_checker_source_is_separate_from_producer_math` | `tests/test_checker.py` | PASS | PASS |
| `test_checker.CheckerAdversarialTests.test_each_branch_field_is_checked` | `tests/test_checker.py` | PASS | PASS |
| `test_checker.CheckerAdversarialTests.test_each_exposed_answer_field_is_checked` | `tests/test_checker.py` | PASS | PASS |
| `test_checker.CheckerAdversarialTests.test_joint_identities_detect_posterior_and_risk_tampering` | `tests/test_checker.py` | PASS | PASS |
| `test_checker.CheckerAdversarialTests.test_omitted_tie_minimizer_and_impossible_null_mutation_fail` | `tests/test_checker.py` | PASS | PASS |
| `test_checker.CheckerAdversarialTests.test_rebinding_old_answer_does_not_bypass_mathematical_check` | `tests/test_checker.py` | PASS | PASS |
| `test_checker.CheckerAdversarialTests.test_runtime_sources_have_no_network_client_imports` | `tests/test_checker.py` | PASS | PASS |
| `test_checker.CheckerAdversarialTests.test_same_hash_tampered_evsi_is_detected` | `tests/test_checker.py` | PASS | PASS |
| `test_checker.CheckerAdversarialTests.test_source_manifest_uses_relative_forward_slash_paths` | `tests/test_checker.py` | PASS | PASS |
| `test_cli.CliIntegrationTests.test_failed_consumer_writes_no_functional_output` | `tests/test_cli.py` | PASS | PASS |
| `test_cli.CliIntegrationTests.test_missing_check_input_writes_not_checked_record` | `tests/test_cli.py` | PASS | PASS |
| `test_cli.CliIntegrationTests.test_refuses_overwriting_output` | `tests/test_cli.py` | PASS | PASS |
| `test_cli.CliIntegrationTests.test_separate_process_path_and_second_directory_are_byte_reproducible` | `tests/test_cli.py` | PASS | PASS |
| `test_cli.CliIntegrationTests.test_unsupported_two_observation_semantics_exits_three` | `tests/test_cli.py` | PASS | PASS |
| `test_comparison.ComparisonTests.test_equal_information_frozen_sequence` | `tests/test_comparison.py` | PASS | PASS |
| `test_consumer.ConsumerTests.test_checked_answer_exposes_small_summary` | `tests/test_consumer.py` | PASS | PASS |
| `test_consumer.ConsumerTests.test_downstream_sink_spy_is_not_called_on_any_failure` | `tests/test_consumer.py` | PASS | PASS |
| `test_consumer.ConsumerTests.test_forged_saved_check_cannot_grant_access` | `tests/test_consumer.py` | PASS | PASS |
| `test_consumer.ConsumerTests.test_tampered_answer_and_changed_question_expose_no_answer` | `tests/test_consumer.py` | PASS | PASS |
| `test_consumer.ConsumerTests.test_unexpected_checker_exception_fails_closed` | `tests/test_consumer.py` | PASS | PASS |
| `test_decode.StrictDecodeTests.test_accepts_complete_exact_inputs` | `tests/test_decode.py` | PASS | PASS |
| `test_decode.StrictDecodeTests.test_declared_resource_limits_are_out_of_scope` | `tests/test_decode.py` | PASS | PASS |
| `test_decode.StrictDecodeTests.test_invalid_identifier_is_rejected_without_normalization` | `tests/test_decode.py` | PASS | PASS |
| `test_decode.StrictDecodeTests.test_rejects_duplicate_keys` | `tests/test_decode.py` | PASS | PASS |
| `test_decode.StrictDecodeTests.test_rejects_duplicate_labels_and_mismatched_state_order` | `tests/test_decode.py` | PASS | PASS |
| `test_decode.StrictDecodeTests.test_rejects_invalid_unicode_nan_bom_and_trailing_data` | `tests/test_decode.py` | PASS | PASS |
| `test_decode.StrictDecodeTests.test_rejects_missing_cost` | `tests/test_decode.py` | PASS | PASS |
| `test_decode.StrictDecodeTests.test_rejects_nine_archival_malformed_rationals` | `tests/test_decode.py` | PASS | PASS |
| `test_decode.StrictDecodeTests.test_rejects_non_normalized_and_negative_probabilities` | `tests/test_decode.py` | PASS | PASS |
| `test_decode.StrictDecodeTests.test_rejects_other_nonstring_rational_literals` | `tests/test_decode.py` | PASS | PASS |
| `test_decode.StrictDecodeTests.test_rejects_unknown_input_and_result_fields` | `tests/test_decode.py` | PASS | PASS |
| `test_decode.StrictDecodeTests.test_rejects_wrong_dimensions` | `tests/test_decode.py` | PASS | PASS |
| `test_decode.StrictDecodeTests.test_result_rationals_have_larger_but_finite_cap` | `tests/test_decode.py` | PASS | PASS |
| `test_decode.StrictDecodeTests.test_unsupported_versions_are_out_of_scope` | `tests/test_decode.py` | PASS | PASS |
| `test_metamorphic.MetamorphicTests.test_action_permutation_preserves_values_and_labels` | `tests/test_metamorphic.py` | PASS | PASS |
| `test_metamorphic.MetamorphicTests.test_constant_loss_translation_preserves_values_of_information` | `tests/test_metamorphic.py` | PASS | PASS |
| `test_metamorphic.MetamorphicTests.test_outcome_permutation_preserves_relabelled_branches` | `tests/test_metamorphic.py` | PASS | PASS |
| `test_metamorphic.MetamorphicTests.test_positive_scale_factor_scales_losses_cost_and_values` | `tests/test_metamorphic.py` | PASS | PASS |
| `test_metamorphic.MetamorphicTests.test_simultaneous_state_permutation_preserves_relabelled_answer` | `tests/test_metamorphic.py` | PASS | PASS |
| `test_pr1_repairs.BaselineQualificationTests.test_duplicate_labels_and_escaped_cost_unequal_assurance` | `tests/test_pr1_repairs.py` | PASS | PASS |
| `test_pr1_repairs.BaselineQualificationTests.test_injected_shared_algorithm_fault_is_not_natural_bug` | `tests/test_pr1_repairs.py` | PASS | PASS |
| `test_pr1_repairs.RepairProcessTests.test_cli_depth_and_canaries_in_stderr_and_records` | `tests/test_pr1_repairs.py` | PASS | PASS |
| `test_pr1_repairs.RepairProcessTests.test_cli_nested_query_and_result_canaries` | `tests/test_pr1_repairs.py` | PASS | PASS |
| `test_pr1_repairs.RepairProcessTests.test_consumer_process_all_statuses_and_post_check_faults` | `tests/test_pr1_repairs.py` | PASS | PASS |
| `test_pr1_repairs.RepairProcessTests.test_fresh_process_producer_disabled` | `tests/test_pr1_repairs.py` | PASS | PASS |
| `test_pr1_repairs.RepairProcessTests.test_genuinely_relocated_sources_solve_check_consume` | `tests/test_pr1_repairs.py` | PASS | PASS |
| `test_pr1_repairs.RepairTests.test_check_record_snapshot_consistency` | `tests/test_pr1_repairs.py` | PASS | PASS |
| `test_pr1_repairs.RepairTests.test_correlated_wrong_answer_correct_hashes` | `tests/test_pr1_repairs.py` | PASS | PASS |
| `test_pr1_repairs.RepairTests.test_deep_snapshots_and_summary_copies` | `tests/test_pr1_repairs.py` | PASS | PASS |
| `test_pr1_repairs.RepairTests.test_depth_boundary_deep_arrays_objects_and_quoted_delimiters` | `tests/test_pr1_repairs.py` | PASS | PASS |
| `test_pr1_repairs.RepairTests.test_diagnostics_never_echo_untrusted_keys_or_values` | `tests/test_pr1_repairs.py` | PASS | PASS |
| `test_pr1_repairs.RepairTests.test_entire_consumer_boundary_structures_failures` | `tests/test_pr1_repairs.py` | PASS | PASS |
| `test_pr1_repairs.RepairTests.test_exact_byte_digit_limits_and_escaped_duplicate` | `tests/test_pr1_repairs.py` | PASS | PASS |
| `test_pr1_repairs.RepairTests.test_manifest_independently_reconstructed_from_repository_root` | `tests/test_pr1_repairs.py` | PASS | PASS |
| `test_pr1_repairs.RepairTests.test_positive_whitespace_rebinding_and_other_producer_source` | `tests/test_pr1_repairs.py` | PASS | PASS |
| `test_solver.SolverFixtureTests.test_all_required_and_development_fixtures_check` | `tests/test_solver.py` | PASS | PASS |
| `test_solver.SolverFixtureTests.test_f01_full_expected_answer` | `tests/test_solver.py` | PASS | PASS |
| `test_solver.SolverFixtureTests.test_large_intermediate_rational_exceeds_input_digit_cap` | `tests/test_solver.py` | PASS | PASS |
| `test_solver.SolverFixtureTests.test_named_packet_expectations` | `tests/test_solver.py` | PASS | PASS |
