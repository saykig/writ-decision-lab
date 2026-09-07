"""End-to-end stale-refusal example for incomplete constraints."""

from __future__ import annotations

import json
from pathlib import Path

from writ_decision_lab.build2.consumer import consume
from writ_decision_lab.build2.engine import solve_and_check
from writ_decision_lab.build2.errors import CheckError

ROOT = Path(__file__).resolve().parents[2]


def plain(value):
    if isinstance(value, dict):
        return {k: plain(v) for k, v in value.items()}
    if hasattr(value, "items"):
        return {k: plain(v) for k, v in value.items()}
    if isinstance(value, tuple):
        return [plain(v) for v in value]
    return value


def main() -> dict:
    old_model = (ROOT / "fixtures/v2/D-nonidentified/model.json").read_bytes()
    query = (ROOT / "fixtures/v2/D-nonidentified/query.json").read_bytes()
    old_bundle, old_checked = solve_and_check(old_model, query)
    old_display = consume(old_bundle, old_model, query)

    changed = json.loads(old_model)
    changed["inequalities"][0]["rhs"] = "1/2"
    new_model = (json.dumps(changed, separators=(",", ":")) + "\n").encode()
    refused = False
    try:
        consume(old_bundle, new_model, query)
    except CheckError:
        refused = True
    if not refused:
        raise RuntimeError("stale result was displayed")

    new_bundle, new_checked = solve_and_check(new_model, query)
    new_display = consume(new_bundle, new_model, query)
    assert old_checked.conclusion["maximum"] == "3/4"
    assert new_checked.conclusion["maximum"] == "1/2"
    assert consume(old_bundle, old_model, query)["conclusion"]["maximum"] == "3/4"
    return plain({
        "old": old_display,
        "stale_reuse_refused": refused,
        "new": new_display,
        "prior_preserved_for_prior_bytes": True,
    })


if __name__ == "__main__":
    print(json.dumps(main(), indent=2, sort_keys=True))

