"""Strict UTF-8 JSON decoding and Build 1 contract validation."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import json
import re
import sys
from typing import Any, Callable

from .errors import WdlError
from .types import Model, Query


INPUT_BYTE_LIMIT = 1024 * 1024
RESULT_BYTE_LIMIT = 4 * 1024 * 1024
MAX_JSON_DEPTH = 32
INPUT_RATIONAL_DIGITS = 32
RESULT_RATIONAL_DIGITS = 4096
MODEL_SCHEMA = "wdl.model.v1"
QUERY_SCHEMA = "wdl.query.v1"
RESULT_SCHEMA = "wdl.result.v1"
SEMANTICS = "finite-one-observation.v1"
IDENTIFIER = re.compile(r"[A-Za-z][A-Za-z0-9_.-]{0,63}\Z")
RATIONAL = re.compile(r"(?:0|-?[1-9][0-9]*)/[1-9][0-9]*\Z")
HASH = re.compile(r"sha256:[0-9a-f]{64}\Z")


@dataclass(frozen=True)
class JsonNumber:
    spelling: str


def _fail(status: str, code: str, path: str, message: str) -> None:
    raise WdlError(status, code, path, message)


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            _fail("invalid_input", "E_JSON_DUPLICATE_KEY", "$", "Duplicate object key.")
        result[key] = value
    return result


def _constant(_: str) -> Any:
    _fail("invalid_input", "E_JSON_CONSTANT", "$", "Non-JSON numeric constant.")


def _check_unicode(value: Any, path: str = "$") -> None:
    if isinstance(value, str):
        if any(0xD800 <= ord(char) <= 0xDFFF for char in value):
            _fail("invalid_input", "E_UNICODE_SCALAR", path, "String contains a surrogate code point.")
    elif isinstance(value, list):
        for item in value:
            _check_unicode(item, path)
    elif isinstance(value, dict):
        for key, item in value.items():
            _check_unicode(key, path)
            _check_unicode(item, path)


def _depth(value: Any, depth: int = 1) -> int:
    if isinstance(value, dict):
        return max([depth] + [_depth(item, depth + 1) for item in value.values()])
    if isinstance(value, list):
        return max([depth] + [_depth(item, depth + 1) for item in value])
    return depth


def _preflight_depth(text: str) -> None:
    """Bound parser recursion without treating quoted delimiters as containers.

    Resource rejection takes precedence once the bound is exceeded. Syntax
    validation below the bound remains the JSON decoder's responsibility.
    """
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
        elif char == '"':
            quoted = True
        elif char in "[{":
            depth += 1
            if depth > MAX_JSON_DEPTH:
                _fail("out_of_scope", "E_JSON_DEPTH", "$", "JSON nesting exceeds 32 levels.")
        elif char in "]}":
            depth -= 1


def decode_json(data: bytes, *, kind: str) -> Any:
    limit = RESULT_BYTE_LIMIT if kind == "result" else INPUT_BYTE_LIMIT
    if len(data) > limit:
        _fail("out_of_scope", "E_BYTE_LIMIT", "$", "Input exceeds its byte limit.")
    if data.startswith(b"\xef\xbb\xbf"):
        _fail("invalid_input", "E_UTF8_BOM", "$", "UTF-8 BOM is not permitted.")
    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        _fail("invalid_input", "E_UTF8", "$", "Input is not valid UTF-8.")
    _preflight_depth(text)
    try:
        value = json.loads(
            text,
            object_pairs_hook=_pairs,
            parse_int=lambda token: JsonNumber(token),
            parse_float=lambda token: JsonNumber(token),
            parse_constant=_constant,
        )
    except WdlError:
        raise
    except (json.JSONDecodeError, ValueError, RecursionError):
        _fail("invalid_input", "E_JSON", "$", "Malformed JSON or trailing data.")
    if _depth(value) > MAX_JSON_DEPTH:
        _fail("out_of_scope", "E_JSON_DEPTH", "$", "JSON nesting exceeds 32 levels.")
    _check_unicode(value)
    return value


def _object(value: Any, keys: set[str], path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        _fail("invalid_input", "E_OBJECT", path, "Expected an object.")
    actual = set(value)
    if actual != keys:
        missing = sorted(keys - actual)
        if actual - keys:
            _fail("invalid_input", "E_UNKNOWN_FIELD", path, "Unknown object field.")
        _fail("invalid_input", "E_REQUIRED_FIELD", path, f"Missing fields: {','.join(missing)}.")
    return value


def _string(value: Any, path: str) -> str:
    if not isinstance(value, str):
        _fail("invalid_input", "E_STRING", path, "Expected a string.")
    return value


def _identifier(value: Any, path: str) -> str:
    result = _string(value, path)
    if not IDENTIFIER.fullmatch(result):
        _fail("invalid_input", "E_IDENTIFIER", path, "Invalid identifier.")
    return result


def _labels(value: Any, path: str, *, minimum: int, maximum: int) -> tuple[str, ...]:
    if not isinstance(value, list):
        _fail("invalid_input", "E_ARRAY", path, "Expected an array.")
    if not minimum <= len(value) <= maximum:
        _fail("out_of_scope", "E_DIMENSION_LIMIT", path, "Label count is outside the supported profile.")
    labels = tuple(_identifier(item, f"{path}[{index}]") for index, item in enumerate(value))
    if len(set(labels)) != len(labels):
        _fail("invalid_input", "E_DUPLICATE_LABEL", path, "Labels must be unique.")
    return labels


def parse_rational(value: Any, path: str, *, digit_limit: int) -> Fraction:
    if not isinstance(value, str) or not RATIONAL.fullmatch(value):
        _fail("invalid_input", "E_RATIONAL", path, "Expected a canonical rational string.")
    numerator, denominator = value.split("/")
    if len(numerator.lstrip("-")) > digit_limit or len(denominator) > digit_limit:
        _fail("out_of_scope", "E_RATIONAL_LIMIT", path, "Rational exceeds the digit limit.")
    try:
        result = Fraction(int(numerator), int(denominator))
    except (ValueError, ZeroDivisionError):
        _fail("invalid_input", "E_RATIONAL", path, "Invalid rational.")
    if f"{result.numerator}/{result.denominator}" != value:
        _fail("invalid_input", "E_RATIONAL_CANONICAL", path, "Rational is not in canonical form.")
    return result


def _rational_array(value: Any, path: str, *, digit_limit: int) -> tuple[Fraction, ...]:
    if not isinstance(value, list):
        _fail("invalid_input", "E_ARRAY", path, "Expected an array.")
    return tuple(
        parse_rational(item, f"{path}[{index}]", digit_limit=digit_limit)
        for index, item in enumerate(value)
    )


def _runtime_supported() -> None:
    if sys.implementation.name != "cpython" or sys.version_info[:2] != (3, 13):
        _fail(
            "out_of_scope",
            "E_RUNTIME_VERSION",
            "$",
            "Build 1 requires CPython 3.13.",
        )
    maximum = sys.get_int_max_str_digits()
    if maximum != 0 and maximum < RESULT_RATIONAL_DIGITS:
        _fail(
            "out_of_scope",
            "E_RUNTIME_INTEGER_LIMIT",
            "$",
            "Runtime integer-string limit is below 4096.",
        )


def decode_model(data: bytes) -> Model:
    _runtime_supported()
    raw = _object(
        decode_json(data, kind="model"),
        {"schema", "states", "outcomes", "prior", "likelihood"},
        "$",
    )
    if _string(raw["schema"], "$.schema") != MODEL_SCHEMA:
        _fail("out_of_scope", "E_MODEL_SCHEMA", "$.schema", "Unsupported model schema.")
    states = _labels(raw["states"], "$.states", minimum=1, maximum=8)
    outcomes = _labels(raw["outcomes"], "$.outcomes", minimum=1, maximum=6)
    prior = _rational_array(raw["prior"], "$.prior", digit_limit=INPUT_RATIONAL_DIGITS)
    if len(prior) != len(states):
        _fail("invalid_input", "E_DIMENSION", "$.prior", "Prior length must match states.")
    if any(value < 0 for value in prior) or sum(prior, Fraction(0)) != 1:
        _fail("invalid_input", "E_PRIOR", "$.prior", "Prior must be nonnegative and sum exactly to one.")
    likelihood_raw = raw["likelihood"]
    if not isinstance(likelihood_raw, list) or len(likelihood_raw) != len(states):
        _fail("invalid_input", "E_DIMENSION", "$.likelihood", "Likelihood rows must match states.")
    rows: list[tuple[Fraction, ...]] = []
    for row_index, row in enumerate(likelihood_raw):
        values = _rational_array(
            row, f"$.likelihood[{row_index}]", digit_limit=INPUT_RATIONAL_DIGITS
        )
        if len(values) != len(outcomes):
            _fail("invalid_input", "E_DIMENSION", f"$.likelihood[{row_index}]", "Likelihood columns must match outcomes.")
        if any(value < 0 for value in values) or sum(values, Fraction(0)) != 1:
            _fail("invalid_input", "E_LIKELIHOOD", f"$.likelihood[{row_index}]", "Likelihood row must be nonnegative and sum exactly to one.")
        rows.append(values)
    return Model(states, outcomes, prior, tuple(rows))


def decode_query(data: bytes, model: Model) -> Query:
    _runtime_supported()
    raw = _object(
        decode_json(data, kind="query"),
        {"schema", "semantics", "state_order", "actions", "losses", "loss_unit", "cost"},
        "$",
    )
    if _string(raw["schema"], "$.schema") != QUERY_SCHEMA:
        _fail("out_of_scope", "E_QUERY_SCHEMA", "$.schema", "Unsupported query schema.")
    if _string(raw["semantics"], "$.semantics") != SEMANTICS:
        _fail("out_of_scope", "E_SEMANTICS", "$.semantics", "Unsupported semantics.")
    state_order = _labels(raw["state_order"], "$.state_order", minimum=1, maximum=8)
    if state_order != model.states:
        _fail("invalid_input", "E_STATE_ORDER", "$.state_order", "State order must exactly match the model.")
    actions = _labels(raw["actions"], "$.actions", minimum=1, maximum=8)
    if len(actions) ** len(model.outcomes) > 4096:
        _fail("out_of_scope", "E_POLICY_LIMIT", "$.actions", "Terminal policy count exceeds 4096.")
    losses_raw = raw["losses"]
    if not isinstance(losses_raw, list) or len(losses_raw) != len(actions):
        _fail("invalid_input", "E_DIMENSION", "$.losses", "Loss rows must match actions.")
    losses: list[tuple[Fraction, ...]] = []
    for row_index, row in enumerate(losses_raw):
        values = _rational_array(row, f"$.losses[{row_index}]", digit_limit=INPUT_RATIONAL_DIGITS)
        if len(values) != len(model.states):
            _fail("invalid_input", "E_DIMENSION", f"$.losses[{row_index}]", "Loss columns must match states.")
        losses.append(values)
    loss_unit = _identifier(raw["loss_unit"], "$.loss_unit")
    cost = parse_rational(raw["cost"], "$.cost", digit_limit=INPUT_RATIONAL_DIGITS)
    if cost < 0:
        _fail("invalid_input", "E_COST", "$.cost", "Observation cost must be nonnegative.")
    return Query(state_order, actions, tuple(losses), loss_unit, cost)


def decode_inputs(model_bytes: bytes, query_bytes: bytes) -> tuple[Model, Query]:
    model = decode_model(model_bytes)
    return model, decode_query(query_bytes, model)


def _hash(value: Any, path: str) -> str:
    result = _string(value, path)
    if not HASH.fullmatch(result):
        _fail("invalid_input", "E_HASH", path, "Expected a sha256: digest.")
    return result


def _string_array(value: Any, path: str, validator: Callable[[Any, str], str] = _identifier) -> list[str]:
    if not isinstance(value, list):
        _fail("invalid_input", "E_ARRAY", path, "Expected an array.")
    return [validator(item, f"{path}[{index}]") for index, item in enumerate(value)]


def decode_result(data: bytes) -> dict[str, Any]:
    _runtime_supported()
    raw = _object(
        decode_json(data, kind="result"),
        {"schema", "semantics", "input_bindings", "producer", "answer"},
        "$",
    )
    if _string(raw["schema"], "$.schema") != RESULT_SCHEMA:
        _fail("out_of_scope", "E_RESULT_SCHEMA", "$.schema", "Unsupported result schema.")
    if _string(raw["semantics"], "$.semantics") != SEMANTICS:
        _fail("out_of_scope", "E_SEMANTICS", "$.semantics", "Unsupported semantics.")
    bindings = _object(raw["input_bindings"], {"model_sha256", "query_sha256"}, "$.input_bindings")
    _hash(bindings["model_sha256"], "$.input_bindings.model_sha256")
    _hash(bindings["query_sha256"], "$.input_bindings.query_sha256")
    producer = _object(raw["producer"], {"name", "version", "code_sha256", "python_version"}, "$.producer")
    for key in ("name", "version", "python_version"):
        _string(producer[key], f"$.producer.{key}")
    if producer["name"] != "writ-decision-lab":
        _fail("invalid_input", "E_PRODUCER_NAME", "$.producer.name", "Unexpected producer name.")
    if producer["version"] != "0.1.0":
        _fail("invalid_input", "E_PRODUCER_VERSION", "$.producer.version", "Unexpected producer version.")
    _hash(producer["code_sha256"], "$.producer.code_sha256")
    answer = _object(
        raw["answer"],
        {
            "state_order", "outcome_order", "action_order", "loss_unit", "prior_risks",
            "current_risk", "current_argmin", "branches", "observed_risk", "evsi",
            "net_value", "acquisition_risks", "acquisition_argmin",
        },
        "$.answer",
    )
    for key in ("state_order", "outcome_order", "action_order", "current_argmin"):
        _string_array(answer[key], f"$.answer.{key}")
    _identifier(answer["loss_unit"], "$.answer.loss_unit")
    _rational_array(answer["prior_risks"], "$.answer.prior_risks", digit_limit=RESULT_RATIONAL_DIGITS)
    for key in ("current_risk", "observed_risk", "evsi", "net_value"):
        parse_rational(answer[key], f"$.answer.{key}", digit_limit=RESULT_RATIONAL_DIGITS)
    branches = answer["branches"]
    if not isinstance(branches, list):
        _fail("invalid_input", "E_ARRAY", "$.answer.branches", "Expected an array.")
    for index, branch_value in enumerate(branches):
        path = f"$.answer.branches[{index}]"
        branch = _object(branch_value, {"outcome", "status", "mass", "posterior", "risks", "minimum_risk", "argmin"}, path)
        _identifier(branch["outcome"], f"{path}.outcome")
        status = _string(branch["status"], f"{path}.status")
        if status not in ("possible", "impossible"):
            _fail("invalid_input", "E_BRANCH_STATUS", f"{path}.status", "Invalid branch status.")
        parse_rational(branch["mass"], f"{path}.mass", digit_limit=RESULT_RATIONAL_DIGITS)
        conditional = ("posterior", "risks", "minimum_risk", "argmin")
        if status == "impossible":
            if any(branch[key] is not None for key in conditional):
                _fail("invalid_input", "E_IMPOSSIBLE_BRANCH", path, "Impossible branch conditional fields must be null.")
        else:
            _rational_array(branch["posterior"], f"{path}.posterior", digit_limit=RESULT_RATIONAL_DIGITS)
            _rational_array(branch["risks"], f"{path}.risks", digit_limit=RESULT_RATIONAL_DIGITS)
            parse_rational(branch["minimum_risk"], f"{path}.minimum_risk", digit_limit=RESULT_RATIONAL_DIGITS)
            _string_array(branch["argmin"], f"{path}.argmin")
    acquisition = _object(answer["acquisition_risks"], {"act_now", "observe_once"}, "$.answer.acquisition_risks")
    for key in ("act_now", "observe_once"):
        parse_rational(acquisition[key], f"$.answer.acquisition_risks.{key}", digit_limit=RESULT_RATIONAL_DIGITS)
    acquisition_argmin = _string_array(answer["acquisition_argmin"], "$.answer.acquisition_argmin", _string)
    if any(item not in ("act_now", "observe_once") for item in acquisition_argmin):
        _fail("invalid_input", "E_ACQUISITION_LABEL", "$.answer.acquisition_argmin", "Invalid acquisition alternative.")
    if acquisition_argmin not in ([], ["act_now"], ["observe_once"], ["act_now", "observe_once"]):
        _fail("invalid_input", "E_ACQUISITION_ORDER", "$.answer.acquisition_argmin", "Acquisition alternatives must be an ordered subsequence.")
    return raw
