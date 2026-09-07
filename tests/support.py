from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures" / "v1"


def fixture(identifier: str) -> tuple[bytes, bytes]:
    directory = FIXTURES / identifier
    return (directory / "model.json").read_bytes(), (directory / "query.json").read_bytes()


def parsed(data: bytes) -> dict[str, Any]:
    return json.loads(data)


def encoded(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("ascii")


def changed(data: bytes, update) -> bytes:
    value = copy.deepcopy(parsed(data))
    update(value)
    return encoded(value)
