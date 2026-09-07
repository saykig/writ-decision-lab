"""A separate program that consumes only freshly checked Build 1 answers."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from writ_decision_lab import check_and_load
from writ_decision_lab.errors import EXIT_CODES, CheckFailure, Diagnostic, WdlError
from writ_decision_lab.identity import output_bytes


def _read(path: Path, role: str) -> bytes:
    try:
        return path.read_bytes()
    except OSError:
        raise WdlError("not_checked", "E_FILE_UNAVAILABLE", f"$.{role}", f"Required {role} bytes are unavailable.")


def _write_new(path: Path, data: bytes) -> None:
    try:
        with path.open("xb") as stream:
            stream.write(data)
    except FileExistsError:
        raise WdlError("invalid_input", "E_OUTPUT_EXISTS", "$.output", "Refusing to overwrite an existing output.")
    except OSError:
        raise WdlError("invalid_input", "E_OUTPUT_WRITE", "$.output", "Could not write the requested output.")


def _failure(status: str, diagnostics: tuple[Diagnostic, ...]) -> int:
    sys.stderr.buffer.write(
        output_bytes({"status": status, "diagnostics": [item.as_dict() for item in diagnostics]})
    )
    return EXIT_CODES[status]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-model", type=Path, required=True)
    parser.add_argument("--expected-query", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        model_bytes = _read(args.expected_model, "model")
        query_bytes = _read(args.expected_query, "query")
        result_bytes = _read(args.result, "result")
        checked = check_and_load(model_bytes, query_bytes, result_bytes)
        _write_new(args.output, output_bytes(checked.summary()))
        return 0
    except CheckFailure as error:
        return _failure(error.status, error.diagnostics)
    except WdlError as error:
        return _failure(error.status, (error.diagnostic,))
    except Exception:
        return _failure(
            "checker_error",
            (Diagnostic("E_CONSUMER_INTERNAL", "$", "Unexpected consumer failure."),),
        )


if __name__ == "__main__":
    raise SystemExit(main())
