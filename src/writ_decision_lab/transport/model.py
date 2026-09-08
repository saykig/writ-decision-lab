"""Language-neutral bounded objects for Bellman certificate transport."""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any

from .exact import canonical_json_bytes, fail, fraction_text, integer, loads_canonical, rational, require_keys, sha256_hex, string

REQUEST_SCHEMA = "certificate-transport-request.v1"
EVIDENCE_SCHEMA = "certificate-transport-evidence.v1"
CHECK_SCHEMA = "certificate-transport-check.v1"
SUBJECT_SEMANTICS = "finite-observable-history.v1"
CRITERION = "expected-additive-total-cost"
GUARANTEE = "expected-additive-total-cost-regret"

History = tuple[tuple[str, str], ...]


def parse_history(value: Any, path: str) -> History:
    if not isinstance(value, list):
        fail("E_HISTORY", path, "History must be a list of [action, observation] pairs.")
    rows: list[tuple[str, str]] = []
    for index, row in enumerate(value):
        if not isinstance(row, list) or len(row) != 2:
            fail("E_HISTORY", f"{path}[{index}]", "History row must contain action and observation.")
        rows.append((string(row[0], f"{path}[{index}][0]"), string(row[1], f"{path}[{index}][1]")))
    return tuple(rows)


def wire_history(history: History) -> list[list[str]]:
    return [[action, observation] for action, observation in history]


@dataclass(frozen=True)
class Action:
    label: str
    cost: Fraction
    outcomes: tuple[tuple[str, Fraction], ...]

    @property
    def is_stop(self) -> bool:
        return not self.outcomes


@dataclass(frozen=True)
class Node:
    history: History
    terminal: Fraction
    actions: tuple[Action, ...]


@dataclass(frozen=True)
class Subject:
    name: str
    semantics: str
    criterion: str
    horizon: int
    unit: str
    premises: tuple[str, ...]
    nodes: tuple[Node, ...]


@dataclass(frozen=True)
class Policy:
    choices: tuple[tuple[History, str], ...]

    def map_for(self, subject: Subject) -> dict[History, str]:
        mapping = dict(self.choices)
        if len(mapping) != len(self.choices):
            fail("E_POLICY", "$.policy.choices", "Policy repeats a history.")
        required = {node.history for node in subject.nodes if node.actions}
        if set(mapping) != required:
            fail("E_POLICY", "$.policy.choices", "Policy must cover every and only decision history.")
        for node in subject.nodes:
            if node.actions and mapping[node.history] not in {action.label for action in node.actions}:
                fail("E_POLICY", "$.policy.choices", "Policy selects an unavailable action.")
        return mapping


@dataclass(frozen=True)
class Certificate:
    lower: tuple[Fraction, ...]
    upper: tuple[Fraction, ...]


@dataclass(frozen=True)
class Request:
    raw: bytes
    value: dict[str, Any]
    source_subject: Subject
    source_policy: Policy
    source_certificate: Certificate
    target_subject: Subject
    target_policy: Policy
    correspondence: tuple[tuple[History, History], ...]
    guarantee: str

    @property
    def sha256(self) -> str:
        return sha256_hex(self.raw)


@dataclass(frozen=True)
class Evidence:
    raw: bytes
    value: dict[str, Any]
    request_sha256: str
    source_subject_sha256: str
    source_policy_sha256: str
    source_certificate_sha256: str
    target_subject_sha256: str
    target_policy_sha256: str
    guarantee: str
    certificate: Certificate
    alpha: tuple[Fraction, ...]
    beta: tuple[Fraction, ...]

    @property
    def sha256(self) -> str:
        return sha256_hex(self.raw)


def _decode_action(value: Any, path: str) -> Action:
    if not isinstance(value, dict):
        fail("E_ACTION", path, "Action must be an object.")
    require_keys(value, {"label", "cost", "outcomes"}, path)
    label = string(value["label"], f"{path}.label")
    cost = rational(value["cost"], f"{path}.cost")
    outcomes_raw = value["outcomes"]
    if not isinstance(outcomes_raw, list) or len(outcomes_raw) > 4:
        fail("E_ACTION", f"{path}.outcomes", "Outcome menu must contain at most four rows.")
    outcomes: list[tuple[str, Fraction]] = []
    for index, row in enumerate(outcomes_raw):
        row_path = f"{path}.outcomes[{index}]"
        if not isinstance(row, dict):
            fail("E_ACTION", row_path, "Outcome row must be an object.")
        require_keys(row, {"observation", "probability"}, row_path)
        outcomes.append((string(row["observation"], f"{row_path}.observation"), rational(row["probability"], f"{row_path}.probability")))
    if len({observation for observation, _ in outcomes}) != len(outcomes):
        fail("E_ACTION", f"{path}.outcomes", "Outcome labels must be unique within one action.")
    if outcomes:
        if any(probability < 0 for _, probability in outcomes) or sum((p for _, p in outcomes), Fraction(0)) != 1:
            fail("E_ACTION", f"{path}.outcomes", "Continuing action probabilities must be nonnegative and sum exactly to one.")
    return Action(label, cost, tuple(outcomes))


def decode_subject(value: Any, path: str) -> Subject:
    if not isinstance(value, dict):
        fail("E_SUBJECT", path, "Subject must be an object.")
    require_keys(value, {"name", "semantics", "criterion", "horizon", "unit", "premises", "nodes"}, path)
    name = string(value["name"], f"{path}.name")
    semantics = string(value["semantics"], f"{path}.semantics")
    criterion = string(value["criterion"], f"{path}.criterion")
    if semantics != SUBJECT_SEMANTICS or criterion != CRITERION:
        fail("E_UNSUPPORTED_SEMANTICS", path, "Subject does not use the supported finite observable-history additive-cost semantics.")
    horizon = integer(value["horizon"], f"{path}.horizon", 0, 4)
    unit = string(value["unit"], f"{path}.unit")
    premises_raw = value["premises"]
    if not isinstance(premises_raw, list) or any(not isinstance(p, str) for p in premises_raw):
        fail("E_SUBJECT", f"{path}.premises", "Premises must be a list of strings.")
    premises = tuple(premises_raw)
    nodes_raw = value["nodes"]
    if not isinstance(nodes_raw, list) or not 1 <= len(nodes_raw) <= 64:
        fail("E_SUBJECT", f"{path}.nodes", "Subject must contain one to 64 completed nodes.")
    nodes: list[Node] = []
    for index, raw_node in enumerate(nodes_raw):
        node_path = f"{path}.nodes[{index}]"
        if not isinstance(raw_node, dict):
            fail("E_NODE", node_path, "Node must be an object.")
        require_keys(raw_node, {"history", "terminal", "actions"}, node_path)
        history = parse_history(raw_node["history"], f"{node_path}.history")
        terminal = rational(raw_node["terminal"], f"{node_path}.terminal")
        actions_raw = raw_node["actions"]
        if not isinstance(actions_raw, list) or len(actions_raw) > 4:
            fail("E_NODE", f"{node_path}.actions", "Action menu must contain at most four actions.")
        actions = tuple(_decode_action(action, f"{node_path}.actions[{i}]") for i, action in enumerate(actions_raw))
        if len({action.label for action in actions}) != len(actions):
            fail("E_NODE", f"{node_path}.actions", "Action labels must be unique within one node.")
        if actions and terminal != 0:
            fail("E_NODE", f"{node_path}.terminal", "Decision nodes cannot also carry terminal cost.")
        if len(history) > horizon or (len(history) == horizon and actions):
            fail("E_NODE", node_path, "Node exceeds the declared horizon or acts at the horizon.")
        nodes.append(Node(history, terminal, actions))
    histories = [node.history for node in nodes]
    if histories[0] != () or len(set(histories)) != len(histories):
        fail("E_SUBJECT", f"{path}.nodes", "Nodes need a unique root-first ordered history list.")
    children: list[History] = []
    for node in nodes:
        for action in node.actions:
            children.extend(node.history + ((action.label, observation),) for observation, _ in action.outcomes)
    if len(set(children)) != len(children) or set(children) != set(histories[1:]):
        fail("E_SUBJECT", f"{path}.nodes", "Subject must be a complete tree with no missing, duplicate, or inaccessible histories.")
    return Subject(name, semantics, criterion, horizon, unit, premises, tuple(nodes))


def decode_policy(value: Any, subject: Subject, path: str) -> Policy:
    if not isinstance(value, dict):
        fail("E_POLICY", path, "Policy must be an object.")
    require_keys(value, {"choices"}, path)
    raw_choices = value["choices"]
    if not isinstance(raw_choices, list):
        fail("E_POLICY", f"{path}.choices", "Policy choices must be a list.")
    choices: list[tuple[History, str]] = []
    for index, row in enumerate(raw_choices):
        row_path = f"{path}.choices[{index}]"
        if not isinstance(row, dict):
            fail("E_POLICY", row_path, "Policy row must be an object.")
        require_keys(row, {"history", "action"}, row_path)
        choices.append((parse_history(row["history"], f"{row_path}.history"), string(row["action"], f"{row_path}.action")))
    policy = Policy(tuple(choices))
    policy.map_for(subject)
    return policy


def decode_certificate(value: Any, subject: Subject, path: str) -> Certificate:
    if not isinstance(value, dict):
        fail("E_CERTIFICATE", path, "Certificate must be an object.")
    require_keys(value, {"lower", "upper"}, path)
    lower_raw, upper_raw = value["lower"], value["upper"]
    if not isinstance(lower_raw, list) or not isinstance(upper_raw, list) or len(lower_raw) != len(subject.nodes) or len(upper_raw) != len(subject.nodes):
        fail("E_CERTIFICATE", path, "Certificate tables must cover every subject node in subject order.")
    lower = tuple(rational(item, f"{path}.lower[{i}]") for i, item in enumerate(lower_raw))
    upper = tuple(rational(item, f"{path}.upper[{i}]") for i, item in enumerate(upper_raw))
    return Certificate(lower, upper)


def wire_certificate(certificate: Certificate) -> dict[str, Any]:
    return {"lower": [fraction_text(v) for v in certificate.lower], "upper": [fraction_text(v) for v in certificate.upper]}


def skeleton(subject: Subject) -> tuple[Any, ...]:
    return (
        subject.semantics,
        subject.criterion,
        subject.horizon,
        subject.unit,
        tuple((node.history, bool(node.actions), tuple((action.label, tuple(observation for observation, _ in action.outcomes), action.is_stop) for action in node.actions)) for node in subject.nodes),
    )


def _component_hash(value: dict[str, Any]) -> str:
    return sha256_hex(canonical_json_bytes(value))


def request_component_hashes(request: Request) -> dict[str, str]:
    source = request.value["source"]
    target = request.value["target"]
    return {
        "source_subject_sha256": _component_hash(source["subject"]),
        "source_policy_sha256": _component_hash(source["policy"]),
        "source_certificate_sha256": _component_hash(source["certificate"]),
        "target_subject_sha256": _component_hash(target["subject"]),
        "target_policy_sha256": _component_hash(target["policy"]),
    }


def decode_request(raw: bytes) -> Request:
    value = loads_canonical(raw, "request")
    require_keys(value, {"schema", "guarantee", "source", "target", "correspondence"}, "$")
    if value["schema"] != REQUEST_SCHEMA:
        fail("E_SCHEMA", "$.schema", f"Expected {REQUEST_SCHEMA}.")
    guarantee = string(value["guarantee"], "$.guarantee")
    if guarantee != GUARANTEE:
        fail("E_GUARANTEE", "$.guarantee", "Unsupported guarantee type.")
    source_raw, target_raw = value["source"], value["target"]
    if not isinstance(source_raw, dict) or not isinstance(target_raw, dict):
        fail("E_REQUEST", "$", "Source and target must be objects.")
    require_keys(source_raw, {"subject", "policy", "certificate"}, "$.source")
    require_keys(target_raw, {"subject", "policy"}, "$.target")
    source_subject = decode_subject(source_raw["subject"], "$.source.subject")
    source_policy = decode_policy(source_raw["policy"], source_subject, "$.source.policy")
    source_certificate = decode_certificate(source_raw["certificate"], source_subject, "$.source.certificate")
    target_subject = decode_subject(target_raw["subject"], "$.target.subject")
    target_policy = decode_policy(target_raw["policy"], target_subject, "$.target.policy")
    if skeleton(source_subject) != skeleton(target_subject):
        fail("E_UNSUPPORTED_TRANSPORT", "$", "Source and target do not have the same completed observable-history skeleton, horizon, unit, or criterion.")
    raw_correspondence = value["correspondence"]
    if not isinstance(raw_correspondence, list):
        fail("E_CORRESPONDENCE", "$.correspondence", "Correspondence must be an ordered list.")
    correspondence: list[tuple[History, History]] = []
    for index, row in enumerate(raw_correspondence):
        path = f"$.correspondence[{index}]"
        if not isinstance(row, dict):
            fail("E_CORRESPONDENCE", path, "Correspondence row must be an object.")
        require_keys(row, {"source_history", "target_history"}, path)
        correspondence.append((parse_history(row["source_history"], f"{path}.source_history"), parse_history(row["target_history"], f"{path}.target_history")))
    identity = tuple((node.history, node.history) for node in source_subject.nodes)
    if tuple(correspondence) != identity:
        fail("E_CORRESPONDENCE", "$.correspondence", "Only the complete ordered identity correspondence is supported.")
    return Request(raw, value, source_subject, source_policy, source_certificate, target_subject, target_policy, tuple(correspondence), guarantee)


def decode_evidence(raw: bytes, request: Request) -> Evidence:
    value = loads_canonical(raw, "evidence")
    required = {"schema", "request_sha256", "source_subject_sha256", "source_policy_sha256", "source_certificate_sha256", "target_subject_sha256", "target_policy_sha256", "guarantee", "certificate", "alpha", "beta"}
    require_keys(value, required, "$")
    if value["schema"] != EVIDENCE_SCHEMA:
        fail("E_SCHEMA", "$.schema", f"Expected {EVIDENCE_SCHEMA}.")
    for key in required - {"schema", "certificate", "alpha", "beta"}:
        string(value[key], f"$.{key}")
    certificate = decode_certificate(value["certificate"], request.target_subject, "$.certificate")
    alpha_raw, beta_raw = value["alpha"], value["beta"]
    if not isinstance(alpha_raw, list) or not isinstance(beta_raw, list) or len(alpha_raw) != len(request.target_subject.nodes) or len(beta_raw) != len(request.target_subject.nodes):
        fail("E_EVIDENCE", "$", "Correction tables must cover every target node.")
    alpha = tuple(rational(item, f"$.alpha[{i}]") for i, item in enumerate(alpha_raw))
    beta = tuple(rational(item, f"$.beta[{i}]") for i, item in enumerate(beta_raw))
    return Evidence(raw, value, value["request_sha256"], value["source_subject_sha256"], value["source_policy_sha256"], value["source_certificate_sha256"], value["target_subject_sha256"], value["target_policy_sha256"], value["guarantee"], certificate, alpha, beta)


def wire_evidence(request: Request, certificate: Certificate, alpha: tuple[Fraction, ...], beta: tuple[Fraction, ...]) -> dict[str, Any]:
    return {
        "schema": EVIDENCE_SCHEMA,
        "request_sha256": request.sha256,
        **request_component_hashes(request),
        "guarantee": request.guarantee,
        "certificate": wire_certificate(certificate),
        "alpha": [fraction_text(value) for value in alpha],
        "beta": [fraction_text(value) for value in beta],
    }
