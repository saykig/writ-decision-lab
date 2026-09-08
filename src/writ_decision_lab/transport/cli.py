"""Creation-only command line boundary for certificate transport."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Sequence

from .checker import check_report
from .exact import TransportError, canonical_json_bytes
from .producer import produce_bytes


def _read(path: Path, role: str) -> bytes:
    try:
        return path.read_bytes()
    except OSError as exc:
        raise TransportError("E_FILE_UNAVAILABLE", f"$.{role}", f"Required {role} bytes are unavailable.") from exc


def _write_new(path: Path, data: bytes) -> None:
    try:
        with path.open("xb") as stream:
            stream.write(data)
    except FileExistsError as exc:
        raise TransportError("E_OUTPUT_EXISTS", "$.output", "Refusing to overwrite an existing output.") from exc
    except OSError as exc:
        raise TransportError("E_OUTPUT_WRITE", "$.output", "Could not write the requested output.") from exc


def _error(error: TransportError) -> int:
    sys.stderr.buffer.write(canonical_json_bytes({"status": "invalid_input", "diagnostics": [error.diagnostic()]}))
    return 2


def _solve(args: argparse.Namespace) -> int:
    try:
        _write_new(args.output, produce_bytes(_read(args.request, "request")))
        return 0
    except TransportError as error:
        return _error(error)
    except Exception:
        sys.stderr.buffer.write(canonical_json_bytes({"status": "checker_error", "diagnostics": [{"code": "E_PRODUCER_INTERNAL", "path": "$", "message": "Unexpected producer failure."}]}))
        return 3


def _check(args: argparse.Namespace) -> int:
    try:
        request_raw = _read(args.request, "request")
        evidence_raw = _read(args.evidence, "evidence")
        report = check_report(request_raw, evidence_raw)
        _write_new(args.output, canonical_json_bytes(report))
        return 0 if report["status"] == "checked" else (2 if report["status"] == "rejected" else 3)
    except TransportError as error:
        return _error(error)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="python -m writ_decision_lab.transport")
    commands = root.add_subparsers(dest="command", required=True)
    solve = commands.add_parser("solve")
    solve.add_argument("--request", required=True, type=Path)
    solve.add_argument("--output", required=True, type=Path)
    solve.set_defaults(handler=_solve)
    check = commands.add_parser("check")
    check.add_argument("--request", required=True, type=Path)
    check.add_argument("--evidence", required=True, type=Path)
    check.add_argument("--output", required=True, type=Path)
    check.set_defaults(handler=_check)
    return root


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    return int(args.handler(args))
