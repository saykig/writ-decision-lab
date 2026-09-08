"""Producer for Bellman's bounded anchored certificate transport recurrence."""
from __future__ import annotations

from fractions import Fraction

from .checker import check_certificate
from .exact import canonical_json_bytes
from .model import Certificate, Request, decode_request, wire_evidence


def produce(request: Request) -> tuple[Certificate, tuple[Fraction, ...], tuple[Fraction, ...]]:
    check_certificate(request.source_subject, request.source_policy, request.source_certificate)
    target = request.target_subject
    histories = [node.history for node in target.nodes]
    old_lower = dict(zip(histories, request.source_certificate.lower))
    old_upper = dict(zip(histories, request.source_certificate.upper))
    choices = request.target_policy.map_for(target)
    alpha: dict = {}
    beta: dict = {}
    for node in sorted(target.nodes, key=lambda item: len(item.history), reverse=True):
        history = node.history
        if not node.actions:
            alpha[history] = max(Fraction(0), old_lower[history] - node.terminal)
            beta[history] = max(Fraction(0), node.terminal - old_upper[history])
            continue
        alpha[history] = max([Fraction(0)] + [
            old_lower[history] - action.cost
            - sum(probability * old_lower[history + ((action.label, observation),)] for observation, probability in action.outcomes)
            + sum(probability * alpha[history + ((action.label, observation),)] for observation, probability in action.outcomes)
            for action in node.actions
        ])
        selected = next(action for action in node.actions if action.label == choices[history])
        beta[history] = max(Fraction(0),
            selected.cost
            + sum(probability * old_upper[history + ((selected.label, observation),)] for observation, probability in selected.outcomes)
            - old_upper[history]
            + sum(probability * beta[history + ((selected.label, observation),)] for observation, probability in selected.outcomes)
        )
    alpha_vector = tuple(alpha[history] for history in histories)
    beta_vector = tuple(beta[history] for history in histories)
    certificate = Certificate(
        tuple(value - correction for value, correction in zip(request.source_certificate.lower, alpha_vector)),
        tuple(value + correction for value, correction in zip(request.source_certificate.upper, beta_vector)),
    )
    return certificate, alpha_vector, beta_vector


def produce_bytes(request_raw: bytes) -> bytes:
    request = decode_request(request_raw)
    certificate, alpha, beta = produce(request)
    return canonical_json_bytes(wire_evidence(request, certificate, alpha, beta))
