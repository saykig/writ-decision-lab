"""Run the frozen eight-step candidate/baseline comparison with equal information."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from time import perf_counter_ns
from typing import Any, Callable

import baseline
from writ_decision_lab import check_and_load, solve_bytes
from writ_decision_lab.errors import CheckFailure, WdlError


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures" / "v1"


def fixture(identifier: str) -> tuple[bytes, bytes]:
    directory = FIXTURES / identifier
    return (directory / "model.json").read_bytes(), (directory / "query.json").read_bytes()


def encoded(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("ascii")


def changed_semantics(query_bytes: bytes) -> bytes:
    value = json.loads(query_bytes)
    value["semantics"] = "finite-two-observation.v1"
    return encoded(value)


def tamper_candidate(result_bytes: bytes) -> bytes:
    value = json.loads(result_bytes)
    value["answer"]["evsi"] = "1/4"
    return encoded(value)


def tamper_baseline(result_bytes: bytes) -> bytes:
    value = json.loads(result_bytes)
    value["answer"]["evsi"] = "1/4"
    return encoded(value)


def expected_failure(function: Callable[[], Any], expected: str) -> dict[str, Any]:
    try:
        function()
    except (CheckFailure, WdlError, baseline.BaselineFailure) as error:
        status = error.status
        return {"expected": expected, "observed": status, "passed": status == expected, "downstream_used": False}
    return {"expected": expected, "observed": "no_failure", "passed": False, "downstream_used": True}


def run_candidate() -> dict[str, Any]:
    steps = []
    start = perf_counter_ns()
    f01_model, f01_query = fixture("F01-weak")
    f01_result = solve_bytes(f01_model, f01_query)
    f01 = check_and_load(f01_model, f01_query, f01_result).answer
    steps.append({"step": 1, "passed": f01["evsi"] == "1/8", "evsi": f01["evsi"]})
    f02_model, f02_query = fixture("F02-perfect")
    f02 = check_and_load(f02_model, f02_query, solve_bytes(f02_model, f02_query)).answer
    steps.append({"step": 2, "passed": f02["evsi"] == "1/4", "evsi": f02["evsi"]})
    f10_model, f10_query = fixture("F10-acquisition-tie")
    f10 = check_and_load(f10_model, f10_query, solve_bytes(f10_model, f10_query)).answer
    steps.append({"step": 3, "passed": f10["acquisition_argmin"] == ["act_now", "observe_once"], "acquisition_argmin": f10["acquisition_argmin"]})
    f03_model, f03_query = fixture("F03-no-signal-unit")
    f03_result = solve_bytes(f03_model, f03_query)
    f03 = check_and_load(f03_model, f03_query, f03_result).answer
    f05_model, f05_query = fixture("F05-revised-unit")
    f05 = check_and_load(f05_model, f05_query, solve_bytes(f05_model, f05_query)).answer
    old_still_valid = check_and_load(f03_model, f03_query, f03_result).answer["current_argmin"] == ["a0"]
    steps.append({"step": 4, "passed": f03["current_argmin"] == ["a0"] and f05["current_argmin"] == ["a1"] and old_still_valid, "old_result_preserved": old_still_valid})
    f12_model, f12_query = fixture("F12-restricted-actions")
    f12 = check_and_load(f12_model, f12_query, solve_bytes(f12_model, f12_query)).answer
    steps.append({"step": 5, "passed": f12["action_order"] == ["a0"] and f12["evsi"] == "0/1", "actions": f12["action_order"]})
    refused = expected_failure(lambda: check_and_load(f01_model, f10_query, f01_result), "input_mismatch")
    original_rechecked = check_and_load(f01_model, f01_query, f01_result).answer["evsi"] == "1/8"
    refused.update({"step": 6, "original_rechecked": original_rechecked, "passed": refused["passed"] and original_rechecked})
    steps.append(refused)
    tampered = expected_failure(lambda: check_and_load(f01_model, f01_query, tamper_candidate(f01_result)), "computation_mismatch")
    tampered["step"] = 7
    steps.append(tampered)
    unsupported = expected_failure(lambda: solve_bytes(f01_model, changed_semantics(f01_query)), "out_of_scope")
    unsupported["step"] = 8
    steps.append(unsupported)
    elapsed = perf_counter_ns() - start
    return {"steps": steps, "all_passed": all(step["passed"] for step in steps), "erroneous_downstream_uses": sum(bool(step.get("downstream_used")) for step in steps), "measured_machine_duration_ns": elapsed}


def run_baseline() -> dict[str, Any]:
    steps = []
    start = perf_counter_ns()
    f01_model, f01_query = fixture("F01-weak")
    f01_result = baseline.produce(f01_model, f01_query)
    f01 = baseline.consume(f01_model, f01_query, f01_result)
    steps.append({"step": 1, "passed": f01["evsi"] == "1/8", "evsi": f01["evsi"]})
    f02_model, f02_query = fixture("F02-perfect")
    f02 = baseline.consume(f02_model, f02_query, baseline.produce(f02_model, f02_query))
    steps.append({"step": 2, "passed": f02["evsi"] == "1/4", "evsi": f02["evsi"]})
    f10_model, f10_query = fixture("F10-acquisition-tie")
    f10 = baseline.consume(f10_model, f10_query, baseline.produce(f10_model, f10_query))
    steps.append({"step": 3, "passed": f10["acquisition_argmin"] == ["act_now", "observe_once"], "acquisition_argmin": f10["acquisition_argmin"]})
    f03_model, f03_query = fixture("F03-no-signal-unit")
    f03_result = baseline.produce(f03_model, f03_query)
    f03 = baseline.consume(f03_model, f03_query, f03_result)
    f05_model, f05_query = fixture("F05-revised-unit")
    f05 = baseline.consume(f05_model, f05_query, baseline.produce(f05_model, f05_query))
    old_still_valid = baseline.consume(f03_model, f03_query, f03_result)["current_argmin"] == ["a0"]
    steps.append({"step": 4, "passed": f03["current_argmin"] == ["a0"] and f05["current_argmin"] == ["a1"] and old_still_valid, "old_result_preserved": old_still_valid})
    f12_model, f12_query = fixture("F12-restricted-actions")
    f12 = baseline.consume(f12_model, f12_query, baseline.produce(f12_model, f12_query))
    steps.append({"step": 5, "passed": f12["action_order"] == ["a0"] and f12["evsi"] == "0/1", "actions": f12["action_order"]})
    refused = expected_failure(lambda: baseline.consume(f01_model, f10_query, f01_result), "input_mismatch")
    original_rechecked = baseline.consume(f01_model, f01_query, f01_result)["evsi"] == "1/8"
    refused.update({"step": 6, "original_rechecked": original_rechecked, "passed": refused["passed"] and original_rechecked})
    steps.append(refused)
    tampered = expected_failure(lambda: baseline.consume(f01_model, f01_query, tamper_baseline(f01_result)), "computation_mismatch")
    tampered["step"] = 7
    steps.append(tampered)
    unsupported = expected_failure(lambda: baseline.produce(f01_model, changed_semantics(f01_query)), "out_of_scope")
    unsupported["step"] = 8
    steps.append(unsupported)
    elapsed = perf_counter_ns() - start
    return {"steps": steps, "all_passed": all(step["passed"] for step in steps), "erroneous_downstream_uses": sum(bool(step.get("downstream_used")) for step in steps), "measured_machine_duration_ns": elapsed}


def line_count(paths: list[Path]) -> int:
    return sum(len(path.read_text().splitlines()) for path in paths)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    candidate = run_candidate()
    ordinary = run_baseline()
    candidate_files = sorted((ROOT / "src" / "writ_decision_lab").glob("*.py")) + [ROOT / "examples" / "consume_answer.py"]
    baseline_files = [ROOT / "comparison" / "baseline.py"]
    record = {
        "schema": "wdl.comparison.v1",
        "comparison_design": "same-author implementer-run, equal-information, unblinded development comparison",
        "candidate": candidate,
        "simpler_baseline": ordinary,
        "preparation_and_maintenance": {
            "candidate": {
                "source_files": [path.relative_to(ROOT).as_posix() for path in candidate_files],
                "source_lines": line_count(candidate_files),
                "safeguard": "separate direct-joint/policy-enumeration checker plus public fresh-check consumer",
                "confirmed_implementation_repairs_before_frozen_run": [
                    "enforced the required CPython 3.13 runtime instead of merely recording it",
                    "enforced fixed producer metadata and ordered acquisition alternatives during result decoding",
                    "made the CLI convert an unexpected checker exception into fail-closed exit 70",
                ],
                "test_harness_corrections_before_frozen_run": ["constructed the NaN fixture explicitly after an ineffective byte substitution"],
            },
            "simpler_baseline": {
                "source_files": [path.relative_to(ROOT).as_posix() for path in baseline_files],
                "source_lines": line_count(baseline_files),
                "safeguard": "raw input hashes plus fresh whole-answer recalculation in the same ordinary script",
                "confirmed_implementation_repairs_before_frozen_run": [],
                "test_harness_corrections_before_frozen_run": [],
            },
            "shared_inputs": "the same frozen fixture bytes and section 3 definitions",
            "human_effort_minutes": None,
            "human_effort_note": "not measured; no estimate or scalar cost score is invented",
        },
        "interpretation": {
            "behavior_gate": candidate["all_passed"] and ordinary["all_passed"] and candidate["erroneous_downstream_uses"] == ordinary["erroneous_downstream_uses"] == 0,
            "foundation_gate": candidate["all_passed"] and candidate["erroneous_downstream_uses"] == 0,
            "present_comparative_benefit": "not demonstrated by this same-author trivial-duration run; the baseline maintained fewer lines while duplicating a same-algorithm recalculation",
            "timing_limitation": "nanosecond durations are observed harness timings but too small and noisy for a productivity claim",
        },
    }
    data = encoded(record)
    try:
        with args.output.open("xb") as stream:
            stream.write(data)
    except FileExistsError:
        return 2
    return 0 if record["interpretation"]["behavior_gate"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
