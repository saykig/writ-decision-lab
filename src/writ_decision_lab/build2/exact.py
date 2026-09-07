"""Strict JSON and canonical rational handling for Build 2."""

from __future__ import annotations

from fractions import Fraction
import json
import re
from typing import Any

from .errors import InputError

MAX_BYTES = 262_144
MAX_ABS_INTEGER = 10**12
_RATIONAL = re.compile(r"(?:0|-?[1-9][0-9]*)(?:/[1-9][0-9]*)?\Z")


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise InputError(f"duplicate_json_key:{key}")
        out[key] = value
    return out


def loads_strict(raw: bytes) -> dict[str, Any]:
    if not isinstance(raw, bytes):
        raise InputError("input_must_be_bytes")
    if len(raw) > MAX_BYTES:
        raise InputError("input_too_large")
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise InputError("invalid_utf8") from exc
    try:
        value = json.loads(
            text,
            object_pairs_hook=_pairs,
            parse_constant=lambda value: (_ for _ in ()).throw(InputError(f"invalid_json_number:{value}")),
        )
    except InputError:
        raise
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        raise InputError("invalid_json") from exc
    if not isinstance(value, dict):
        raise InputError("root_must_be_object")
    return value


def require_keys(obj: dict[str, Any], required: set[str], optional: set[str] = frozenset()) -> None:
    missing = required - obj.keys()
    extra = obj.keys() - required - optional
    if missing:
        raise InputError("missing_keys:" + ",".join(sorted(missing)))
    if extra:
        raise InputError("unknown_keys:" + ",".join(sorted(extra)))


def rational(value: Any, where: str) -> Fraction:
    if not isinstance(value, str) or not _RATIONAL.fullmatch(value):
        raise InputError(f"noncanonical_rational:{where}")
    if "/" in value:
        n_text, d_text = value.split("/", 1)
        n, d = int(n_text), int(d_text)
    else:
        n, d = int(value), 1
    if abs(n) > MAX_ABS_INTEGER or d > MAX_ABS_INTEGER:
        raise InputError(f"rational_limit:{where}")
    result = Fraction(n, d)
    if fraction_text(result) != value:
        raise InputError(f"noncanonical_rational:{where}")
    return result


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def vector(values: Any, size: int, where: str) -> tuple[Fraction, ...]:
    if not isinstance(values, list) or len(values) != size:
        raise InputError(f"dimension_mismatch:{where}")
    return tuple(rational(value, f"{where}[{index}]") for index, value in enumerate(values))


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")

