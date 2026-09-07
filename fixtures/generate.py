"""Generate the frozen Build 1 regression fixtures from the packet definitions."""

from __future__ import annotations

from fractions import Fraction as F
import json
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures" / "v1"


def rational(value: F | int) -> str:
    value = F(value)
    return f"{value.numerator}/{value.denominator}"


def encoded(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("ascii")


def binary(
    k0: F | int,
    k1: F | int,
    *,
    prior_s1: F = F(1, 4),
    losses: tuple[tuple[F | int, ...], ...] = ((0, 1), (1, 0)),
    cost: F | int = 0,
    actions: tuple[str, ...] = ("a0", "a1"),
) -> tuple[dict[str, object], dict[str, object]]:
    k0, k1 = F(k0), F(k1)
    model = {
        "schema": "wdl.model.v1",
        "states": ["s0", "s1"],
        "outcomes": ["x0", "x1"],
        "prior": [rational(1 - prior_s1), rational(prior_s1)],
        "likelihood": [
            [rational(1 - k0), rational(k0)],
            [rational(1 - k1), rational(k1)],
        ],
    }
    query = {
        "schema": "wdl.query.v1",
        "semantics": "finite-one-observation.v1",
        "state_order": ["s0", "s1"],
        "actions": list(actions),
        "losses": [[rational(value) for value in row] for row in losses],
        "loss_unit": "loss-unit",
        "cost": rational(cost),
    }
    return model, query


def cases() -> list[tuple[str, str, str, dict[str, object], dict[str, object]]]:
    packet = "source-reported: Build 1 packet fixture"
    development = "new development case derived from section 3"
    values: list[tuple[str, str, str, dict[str, object], dict[str, object]]] = []

    def add(identifier: str, origin: str, property_text: str, pair: tuple[dict[str, object], dict[str, object]]) -> None:
        values.append((identifier, origin, property_text, pair[0], pair[1]))

    add("F01-weak", packet, "a0 now; a0/a1 by branch; EVSI 1/8", binary(0, F(1, 2)))
    add("F02-perfect", packet, "same action answers as F01; EVSI 1/4", binary(0, 1))
    add("F03-no-signal-unit", packet, "a0; x1 impossible; EVSI 0", binary(0, 0))
    add("F04-no-signal-asymmetric", packet, "same action summary and EVSI as F03", binary(0, 0, losses=((0, 1), (2, 0))))
    add("F05-revised-unit", packet, "prior risks 1 and 3/4; unique a1", binary(0, 0, losses=((1, 1), (1, 0))))
    add("F06-revised-asymmetric", packet, "prior risks 1 and 3/2; unique a0", binary(0, 0, losses=((1, 1), (2, 0))))
    add("F07-real-tie", packet, "both actions minimize at both possible branches", binary(F(1, 2), F(1, 2), prior_s1=F(1, 2)))
    add("F08-zero-prior", packet, "x1 impossible, not a tie or posterior", binary(0, 1, prior_s1=F(0)))
    add("F09-exactness", packet, "unique a0 with exact risk gap 1/1000000000000000001", binary(0, 0, prior_s1=F(500000000000000000, 1000000000000000001)))
    add("F10-acquisition-tie", packet, "act-now and observe-once tie; net value 0", binary(0, F(1, 2), cost=F(1, 8)))
    model11 = {
        "schema": "wdl.model.v1",
        "states": ["s0", "s1", "s2"],
        "outcomes": ["x0", "x1", "x2"],
        "prior": ["1/2", "1/3", "1/6"],
        "likelihood": [["1/1", "0/1", "0/1"], ["0/1", "1/1", "0/1"], ["0/1", "0/1", "1/1"]],
    }
    query11 = {
        "schema": "wdl.query.v1",
        "semantics": "finite-one-observation.v1",
        "state_order": ["s0", "s1", "s2"],
        "actions": ["a0", "a1", "a2"],
        "losses": [["0/1", "2/1", "3/1"], ["1/1", "0/1", "2/1"], ["3/1", "1/1", "0/1"]],
        "loss_unit": "loss-unit",
        "cost": "0/1",
    }
    values.append(("F11-three-state", packet, "prior minimum 5/6 at a1; observed risk 0; EVSI 5/6", model11, query11))
    add("F12-restricted-actions", packet, "only a0 remains; EVSI 0", binary(0, 1, actions=("a0",), losses=((0, 1),)))

    model_min = {"schema": "wdl.model.v1", "states": ["s0"], "outcomes": ["x0"], "prior": ["1/1"], "likelihood": [["1/1"]]}
    query_min = {"schema": "wdl.query.v1", "semantics": "finite-one-observation.v1", "state_order": ["s0"], "actions": ["a0"], "losses": [["5/3"]], "loss_unit": "loss-unit", "cost": "0/1"}
    values.append(("D01-minimum", development, "one state/action/outcome; both risks 5/3 and EVSI 0", model_min, query_min))
    model_negative = {"schema": "wdl.model.v1", "states": ["s0", "s1"], "outcomes": ["x0"], "prior": ["1/2", "1/2"], "likelihood": [["1/1"], ["1/1"]]}
    query_negative = {"schema": "wdl.query.v1", "semantics": "finite-one-observation.v1", "state_order": ["s0", "s1"], "actions": ["a0", "a1"], "losses": [["-3/1", "1/1"], ["0/1", "-1/1"]], "loss_unit": "loss-unit", "cost": "0/1"}
    values.append(("D02-negative-loss", development, "a0 uniquely minimizes at -1; EVSI 0", model_negative, query_negative))
    add("D03-cost-over-evsi", development, "EVSI 1/8, cost 1/4, net value -1/8; act now", binary(0, F(1, 2), cost=F(1, 4)))
    model_limit = {"schema": "wdl.model.v1", "states": ["s0"], "outcomes": ["x0", "x1", "x2", "x3"], "prior": ["1/1"], "likelihood": [["1/4", "1/4", "1/4", "1/4"]]}
    query_limit = {"schema": "wdl.query.v1", "semantics": "finite-one-observation.v1", "state_order": ["s0"], "actions": [f"a{i}" for i in range(8)], "losses": [[f"{i}/1"] for i in range(8)], "loss_unit": "loss-unit", "cost": "0/1"}
    values.append(("D04-policy-limit", development, "8^4 = 4096 policies; a0 minimizes everywhere; EVSI 0", model_limit, query_limit))
    return values


def main() -> None:
    manifest_entries = []
    for identifier, origin, property_text, model, query in cases():
        directory = FIXTURES / identifier
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "model.json").write_bytes(encoded(model))
        (directory / "query.json").write_bytes(encoded(query))
        manifest_entries.append(
            {
                "id": identifier,
                "origin": origin,
                "model": f"v1/{identifier}/model.json",
                "query": f"v1/{identifier}/query.json",
                "intended_property": property_text,
            }
        )
    (ROOT / "fixtures" / "manifest.json").write_bytes(
        encoded({"schema": "wdl.fixture-manifest.v1", "fixtures": manifest_entries})
    )
    example = ROOT / "examples" / "weak"
    example.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(FIXTURES / "F01-weak" / "model.json", example / "model.json")
    shutil.copyfile(FIXTURES / "F01-weak" / "query.json", example / "query.json")


if __name__ == "__main__":
    main()
