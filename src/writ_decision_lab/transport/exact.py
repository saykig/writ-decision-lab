"""Strict exact JSON and rational helpers for certificate transport."""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
import re
from typing import Any

MAX_BYTES = 1_048_576
MAX_JSON_DEPTH = 64
MAX_RATIONAL_BITS = 256
_RATIONAL = re.compile(r"(?:0|-?[1-9][0-9]*)(?:/[1-9][0-9]*)?\Z")


class TransportError(ValueError):
    def __init__(self, code: str, path: str, message: str):
        super().__init__(message)
        self.code = code
        self.path = path
        self.message = message

    def diagnostic(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "message": self.message}


def fail(code: str, path: str, message: str) -> None:
    raise TransportError(code, path, message)


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            fail("E_DUPLICATE_JSON_KEY", "$", f"Duplicate JSON key {key!r}.")
        out[key] = value
    return out


def _preflight_depth(text: str) -> None:
    depth = 0
    quoted = False
    escaped = False
    for char in text:
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
            continue
        if char == '"':
            quoted = True
        elif char in "[{":
            depth += 1
            if depth > MAX_JSON_DEPTH:
                fail("E_JSON_DEPTH", "$", "JSON nesting exceeds the bounded profile.")
        elif char in "]}":
            depth -= 1


def _validate_depth(value: Any) -> None:
    pending = [(value, 1, True)]
    active: set[int] = set()
    while pending:
        item, depth, entering = pending.pop()
        if not isinstance(item, (dict, list)):
            continue
        identity = id(item)
        if not entering:
            active.remove(identity)
            continue
        if identity in active:
            fail("E_JSON_CYCLE", "$", "JSON value contains a cycle.")
        if depth > MAX_JSON_DEPTH:
            fail("E_JSON_DEPTH", "$", "JSON nesting exceeds the bounded profile.")
        active.add(identity)
        pending.append((item, depth, False))
        children = item.values() if isinstance(item, dict) else item
        pending.extend((child, depth + 1, True) for child in children)


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def loads_canonical(raw: bytes, role: str) -> dict[str, Any]:
    if not isinstance(raw, bytes):
        fail("E_INPUT_TYPE", f"$.{role}", f"{role} must be supplied as bytes.")
    if not raw or len(raw) > MAX_BYTES:
        fail("E_INPUT_SIZE", f"$.{role}", f"{role} exceeds the bounded byte profile or is empty.")
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        fail("E_UTF8", f"$.{role}", f"{role} is not valid UTF-8.")
    _preflight_depth(text)
    try:
        value = json.loads(
            text,
            object_pairs_hook=_pairs,
            parse_constant=lambda token: fail("E_JSON_NUMBER", f"$.{role}", f"Unsupported JSON number {token}."),
        )
    except TransportError:
        raise
    except (json.JSONDecodeError, TypeError, ValueError, RecursionError):
        fail("E_JSON", f"$.{role}", f"{role} is not valid JSON.")
    _validate_depth(value)
    if not isinstance(value, dict):
        fail("E_JSON_ROOT", f"$.{role}", f"{role} root must be an object.")
    if canonical_json_bytes(value) != raw:
        fail("E_NONCANONICAL_JSON", f"$.{role}", f"{role} must use deterministic canonical JSON bytes.")
    return value


def require_keys(obj: dict[str, Any], required: set[str], path: str, optional: set[str] = frozenset()) -> None:
    missing = sorted(required - obj.keys())
    extra = sorted(obj.keys() - required - optional)
    if missing:
        fail("E_MISSING_KEY", path, "Missing keys: " + ", ".join(missing) + ".")
    if extra:
        fail("E_UNKNOWN_KEY", path, "Unknown keys: " + ", ".join(extra) + ".")


def string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value:
        fail("E_STRING", path, "Expected a non-empty string.")
    return value


def integer(value: Any, path: str, low: int, high: int) -> int:
    if type(value) is not int or not low <= value <= high:
        fail("E_INTEGER", path, f"Expected an integer in [{low}, {high}].")
    return value


def rational(value: Any, path: str) -> Fraction:
    if not isinstance(value, str) or not _RATIONAL.fullmatch(value):
        fail("E_RATIONAL", path, "Expected a canonical exact rational string.")
    if "/" in value:
        numerator_text, denominator_text = value.split("/", 1)
        numerator, denominator = int(numerator_text), int(denominator_text)
    else:
        numerator, denominator = int(value), 1
    if max(abs(numerator).bit_length(), denominator.bit_length()) > MAX_RATIONAL_BITS:
        fail("E_RATIONAL_LIMIT", path, "Rational coefficient exceeds the 256-bit bounded profile.")
    result = Fraction(numerator, denominator)
    if fraction_text(result) != value:
        fail("E_RATIONAL", path, "Rational string is not in reduced canonical form.")
    return result


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def sha256_hex(raw: bytes) -> str:
    return sha256(raw).hexdigest()
