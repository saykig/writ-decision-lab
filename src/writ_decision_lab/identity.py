"""Deterministic byte and source-snapshot identities."""

from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import sys
from typing import Any
from collections.abc import Mapping

from .types import RuntimeContext


def digest_bytes(data: bytes) -> str:
    return "sha256:" + sha256(data).hexdigest()


def wire(value: Any) -> Any:
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, Mapping):
        return {key: wire(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [wire(item) for item in value]
    return value


def output_bytes(value: Any) -> bytes:
    text = json.dumps(
        wire(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )
    return (text + "\n").encode("ascii")


def source_manifest(package_dir: Path | None = None) -> list[dict[str, str]]:
    base = package_dir or Path(__file__).resolve().parent
    entries: list[dict[str, str]] = []
    for path in sorted(base.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        entries.append(
            {
                "path": "src/writ_decision_lab/" + path.relative_to(base).as_posix(),
                "sha256": digest_bytes(path.read_bytes()),
            }
        )
    return entries


def code_digest(package_dir: Path | None = None) -> str:
    return digest_bytes(output_bytes(source_manifest(package_dir)))


def runtime_context(package_dir: Path | None = None) -> RuntimeContext:
    return RuntimeContext(
        code_sha256=code_digest(package_dir),
        python_version=sys.version.split()[0],
    )
