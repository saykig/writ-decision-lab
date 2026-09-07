"""Command-line entry points over explicit local byte snapshots."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Sequence

from .checker import check_bytes, not_checked_report, report_bytes
from .errors import EXIT_CODES, Diagnostic, WdlError
from .identity import output_bytes
from .solver import solve_bytes


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


def _stderr(status: str, diagnostic: Diagnostic) -> None:
    sys.stderr.buffer.write(output_bytes({"status": status, "diagnostics": [diagnostic.as_dict()]}))


def _solve(args: argparse.Namespace) -> int:
    try:
        model_bytes = _read(args.model, "model")
        query_bytes = _read(args.query, "query")
        result_bytes = solve_bytes(model_bytes, query_bytes)
        _write_new(args.output, result_bytes)
        return 0
    except WdlError as error:
        _stderr(error.status, error.diagnostic)
        return EXIT_CODES[error.status]
    except Exception:
        diagnostic = Diagnostic("E_PRODUCER_INTERNAL", "$", "Unexpected producer failure.")
        _stderr("checker_error", diagnostic)
        return EXIT_CODES["checker_error"]


def _check(args: argparse.Namespace) -> int:
    values: dict[str, bytes | None] = {"model": None, "query": None, "result": None}
    missing: list[str] = []
    for role in ("model", "query", "result"):
        try:
            values[role] = _read(getattr(args, role), role)
        except WdlError:
            missing.append(role)
    if missing:
        report = not_checked_report(values["model"], values["query"], values["result"], missing)
    else:
        try:
            report = check_bytes(values["model"], values["query"], values["result"])  # type: ignore[arg-type]
        except Exception:
            diagnostic = Diagnostic("E_CHECKER_INTERNAL", "$", "Unexpected checker failure.")
            _stderr("checker_error", diagnostic)
            return EXIT_CODES["checker_error"]
    try:
        _write_new(args.output, report_bytes(report))
    except WdlError as error:
        _stderr(error.status, error.diagnostic)
        return EXIT_CODES[error.status]
    return EXIT_CODES[report.status]


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(prog="python -m writ_decision_lab")
    commands = result.add_subparsers(dest="command", required=True)
    solve = commands.add_parser("solve")
    solve.add_argument("--model", required=True, type=Path)
    solve.add_argument("--query", required=True, type=Path)
    solve.add_argument("--output", required=True, type=Path)
    solve.set_defaults(handler=_solve)
    check = commands.add_parser("check")
    check.add_argument("--model", required=True, type=Path)
    check.add_argument("--query", required=True, type=Path)
    check.add_argument("--result", required=True, type=Path)
    check.add_argument("--output", required=True, type=Path)
    check.set_defaults(handler=_check)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    return int(args.handler(args))
