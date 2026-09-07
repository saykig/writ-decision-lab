"""Stable diagnostics and status-bearing failures for Build 1."""

from __future__ import annotations

from dataclasses import dataclass


EXIT_CODES = {
    "checked": 0,
    "produced": 0,
    "invalid_input": 2,
    "out_of_scope": 3,
    "input_mismatch": 4,
    "computation_mismatch": 5,
    "not_checked": 6,
    "checker_error": 70,
}


@dataclass(frozen=True)
class Diagnostic:
    code: str
    path: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "message": self.message}


class WdlError(Exception):
    """Expected, stable failure that is safe to expose in a check record."""

    def __init__(self, status: str, code: str, path: str, message: str):
        super().__init__(message)
        self.status = status
        self.diagnostic = Diagnostic(code, path, message)


class CheckFailure(WdlError):
    """Raised when a caller asks to load a result that did not check."""

    def __init__(self, status: str, diagnostics: tuple[Diagnostic, ...]):
        diagnostic = diagnostics[0] if diagnostics else Diagnostic(
            "E_CHECK_FAILED", "$", "The result was not checked."
        )
        super().__init__(status, diagnostic.code, diagnostic.path, diagnostic.message)
        self.diagnostics = diagnostics
