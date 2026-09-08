"""Independent receiver for ordinary and anchored Bellman certificate transport."""
from __future__ import annotations

from fractions import Fraction

from .exact import TransportError, canonical_json_bytes, fail, fraction_text, sha256_hex
from .model import CHECK_SCHEMA, Certificate, Evidence, Request, Subject, Policy, decode_evidence, decode_request, request_component_hashes


def _tables(subject: Subject, certificate: Certificate) -> tuple[dict, dict]:
    histories = [node.history for node in subject.nodes]
    return dict(zip(histories, certificate.lower)), dict(zip(histories, certificate.upper))


def _backup(node, action, values: dict) -> Fraction:
    result = action.cost
    for observation, probability in action.outcomes:
        if probability:
            result += probability * values[node.history + ((action.label, observation),)]
    return result


def check_certificate(subject: Subject, policy: Policy, certificate: Certificate) -> dict[str, Fraction]:
    choices = policy.map_for(subject)
    lower, upper = _tables(subject, certificate)
    for node in subject.nodes:
        if not node.actions:
            if not (lower[node.history] <= node.terminal <= upper[node.history]):
                fail("E_TARGET_CERTIFICATE", "$.certificate", "Terminal bounds do not cover the target terminal cost.")
            continue
        for action in node.actions:
            if lower[node.history] > _backup(node, action, lower):
                fail("E_TARGET_CERTIFICATE", "$.certificate.lower", "Lower table is not a subsolution for every target action.")
        selected = next(action for action in node.actions if action.label == choices[node.history])
        if upper[node.history] < _backup(node, selected, upper):
            fail("E_TARGET_CERTIFICATE", "$.certificate.upper", "Upper table does not bound the selected target policy action.")
    root = subject.nodes[0].history
    if upper[root] < lower[root]:
        fail("E_TARGET_CERTIFICATE", "$.certificate", "Certificate has a negative root gap.")
    return {"optimum_lower": lower[root], "policy_upper": upper[root], "regret_upper": upper[root] - lower[root]}


def check_transport(request: Request, evidence: Evidence) -> dict[str, Fraction]:
    check_certificate(request.source_subject, request.source_policy, request.source_certificate)
    expected_hashes = request_component_hashes(request)
    if evidence.request_sha256 != request.sha256:
        fail("E_TRANSPORT_BINDING", "$.request_sha256", "Evidence is bound to a different request.")
    for key, expected in expected_hashes.items():
        if getattr(evidence, key) != expected:
            fail("E_TRANSPORT_BINDING", f"$.{key}", f"Evidence {key} does not match the supplied request.")
    if evidence.guarantee != request.guarantee:
        fail("E_TRANSPORT_BINDING", "$.guarantee", "Evidence uses a different guarantee type.")
    answer = check_certificate(request.target_subject, request.target_policy, evidence.certificate)
    target = request.target_subject
    histories = [node.history for node in target.nodes]
    old_lower = dict(zip(histories, request.source_certificate.lower))
    old_upper = dict(zip(histories, request.source_certificate.upper))
    lower, upper = _tables(target, evidence.certificate)
    alpha = dict(zip(histories, evidence.alpha))
    beta = dict(zip(histories, evidence.beta))
    choices = request.target_policy.map_for(target)
    for node in target.nodes:
        history = node.history
        if alpha[history] < 0 or beta[history] < 0:
            fail("E_TRANSPORT_CORRECTION", "$.alpha", "Correction tables must be pointwise nonnegative.")
        if lower[history] != old_lower[history] - alpha[history] or upper[history] != old_upper[history] + beta[history]:
            fail("E_TRANSPORT_CORRECTION", "$.certificate", "Target tables are not exactly bound to the submitted corrections and source anchors.")
        if not node.actions:
            expected_lower = min(old_lower[history], node.terminal)
            expected_upper = max(old_upper[history], node.terminal)
        else:
            expected_lower = min([old_lower[history]] + [_backup(node, action, lower) for action in node.actions])
            selected = next(action for action in node.actions if action.label == choices[history])
            expected_upper = max(old_upper[history], _backup(node, selected, upper))
        if lower[history] != expected_lower or upper[history] != expected_upper:
            fail("E_TRANSPORT_ENVELOPE", "$.certificate", "Submitted target certificate is valid but is not the anchored extremal envelope required by the transport warrant.")
    return answer


def _report(status: str, request_raw: bytes, evidence_raw: bytes, *, answer=None, diagnostic=None) -> dict:
    report = {
        "schema": CHECK_SCHEMA,
        "status": status,
        "request_sha256": sha256_hex(request_raw),
        "evidence_sha256": sha256_hex(evidence_raw),
        "warrant": None,
        "bounds": None,
        "diagnostics": [],
        "limits": [
            "same completed observable-history skeleton only",
            "expected additive total cost only",
            "complete deterministic history policies only",
            "checked mathematics does not establish empirical premises or authority to act",
        ],
    }
    if answer is not None:
        report["warrant"] = "checked target certificate and anchored transport"
        report["bounds"] = {key: fraction_text(value) for key, value in answer.items()}
    if diagnostic is not None:
        report["diagnostics"] = [diagnostic]
    return report


def check_report(request_raw: bytes, evidence_raw: bytes) -> dict:
    try:
        request = decode_request(request_raw)
        evidence = decode_evidence(evidence_raw, request)
        return _report("checked", request_raw, evidence_raw, answer=check_transport(request, evidence))
    except TransportError as error:
        return _report("rejected", request_raw, evidence_raw, diagnostic=error.diagnostic())
    except Exception:
        return _report("checker_error", request_raw, evidence_raw, diagnostic={"code": "E_CHECKER_INTERNAL", "path": "$", "message": "Unexpected checker failure."})


def check_bytes(request_raw: bytes, evidence_raw: bytes) -> bytes:
    return canonical_json_bytes(check_report(request_raw, evidence_raw))
