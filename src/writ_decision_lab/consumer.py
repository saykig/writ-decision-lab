"""Fail-closed checked-consumer boundary."""

from __future__ import annotations

from . import checker
from .decode import decode_result
from .errors import CheckFailure, Diagnostic, WdlError
from .identity import digest_bytes
from .types import CheckedAnswer


def check_and_load(model_bytes: bytes, query_bytes: bytes, result_bytes: bytes) -> CheckedAnswer:
    try:
        report = checker.check_bytes(model_bytes, query_bytes, result_bytes)
        if report.status != "checked":
            raise CheckFailure(report.status, report.diagnostics)
        claimed = decode_result(result_bytes)
        return CheckedAnswer(
            answer=claimed["answer"],
            model_sha256=digest_bytes(model_bytes),
            query_sha256=digest_bytes(query_bytes),
            result_sha256=digest_bytes(result_bytes),
        )
    except CheckFailure:
        raise
    except WdlError as error:
        raise CheckFailure(error.status, (error.diagnostic,)) from None
    except Exception:
        raise CheckFailure(
            "checker_error",
            (Diagnostic("E_CHECKER_INTERNAL", "$", "Unexpected checker failure."),),
        ) from None
