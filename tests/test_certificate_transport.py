from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from writ_decision_lab.transport import check_bytes, produce_bytes
from writ_decision_lab.transport.checker import check_report
from writ_decision_lab.transport.exact import TransportError, canonical_json_bytes
from writ_decision_lab.transport.model import decode_request


def action(label: str, cost: str, outcomes=None):
    return {"label": label, "cost": cost, "outcomes": outcomes or []}


def outcome(observation: str, probability: str):
    return {"observation": observation, "probability": probability}


def subject(name: str, nodes, horizon: int = 1, unit: str = "loss", premises=None):
    return {"name": name, "semantics": "finite-observable-history.v1", "criterion": "expected-additive-total-cost", "horizon": horizon, "unit": unit, "premises": premises or [], "nodes": nodes}


def policy(rows):
    return {"choices": [{"history": history, "action": selected} for history, selected in rows]}


def identity(nodes):
    return [{"source_history": node["history"], "target_history": node["history"]} for node in nodes]


def comparator_request() -> bytes:
    source_nodes = [{"history": [], "terminal": "0", "actions": [action("a", "1"), action("b", "2")]}]
    target_nodes = [{"history": [], "terminal": "0", "actions": [action("a", "1"), action("b", "0")]}]
    return canonical_json_bytes({
        "schema": "certificate-transport-request.v1",
        "guarantee": "expected-additive-total-cost-regret",
        "source": {"subject": subject("G", source_nodes, premises=["supplied source model"]), "policy": policy([([], "a")]), "certificate": {"lower": ["1"], "upper": ["1"]}},
        "target": {"subject": subject("F", target_nodes, premises=["explicitly revised target model"]), "policy": policy([([], "a")])},
        "correspondence": identity(source_nodes),
    })


def two_step_request() -> bytes:
    nodes = [
        {"history": [], "terminal": "0", "actions": [action("STOP", "3/4"), action("GO", "1/8", [outcome("L", "1/2"), outcome("R", "1/2")])]},
        {"history": [["GO", "L"]], "terminal": "0", "actions": [action("a", "0"), action("b", "1/2")]},
        {"history": [["GO", "R"]], "terminal": "0", "actions": [action("a", "1"), action("b", "1/4")]},
    ]
    return canonical_json_bytes({
        "schema": "certificate-transport-request.v1",
        "guarantee": "expected-additive-total-cost-regret",
        "source": {"subject": subject("two-step-source", nodes, horizon=2), "policy": policy([([], "GO"), ([["GO", "L"]], "a"), ([["GO", "R"]], "b")]), "certificate": {"lower": ["1/4", "0", "1/4"], "upper": ["1/4", "0", "1/4"]}},
        "target": {"subject": subject("two-step-target", copy.deepcopy(nodes), horizon=2, premises=["same model, changed executed policy"]), "policy": policy([([], "GO"), ([["GO", "L"]], "b"), ([["GO", "R"]], "a")])},
        "correspondence": identity(nodes),
    })


class CertificateTransportTests(unittest.TestCase):
    def test_comparator_change_repairs_lower_bound(self):
        request = comparator_request()
        evidence = json.loads(produce_bytes(request))
        self.assertEqual(evidence["certificate"], {"lower": ["0"], "upper": ["1"]})
        self.assertEqual(evidence["alpha"], ["1"])
        self.assertEqual(evidence["beta"], ["0"])
        report = json.loads(check_bytes(request, canonical_json_bytes(evidence)))
        self.assertEqual(report["status"], "checked")
        self.assertEqual(report["bounds"], {"optimum_lower": "0", "policy_upper": "1", "regret_upper": "1"})

    def test_unchanged_subject_and_policy_have_zero_corrections(self):
        value = json.loads(comparator_request())
        value["target"]["subject"] = copy.deepcopy(value["source"]["subject"])
        value["target"]["policy"] = copy.deepcopy(value["source"]["policy"])
        request = canonical_json_bytes(value)
        evidence = json.loads(produce_bytes(request))
        self.assertEqual(evidence["certificate"], value["source"]["certificate"])
        self.assertEqual(evidence["alpha"], ["0"])
        self.assertEqual(evidence["beta"], ["0"])
        self.assertEqual(json.loads(check_bytes(request, canonical_json_bytes(evidence)))["status"], "checked")

    def test_policy_change_yields_seven_eighths_upper(self):
        request = two_step_request()
        evidence = json.loads(produce_bytes(request))
        self.assertEqual(evidence["certificate"]["lower"], ["1/4", "0", "1/4"])
        self.assertEqual(evidence["certificate"]["upper"], ["7/8", "1/2", "1"])
        self.assertEqual(evidence["beta"], ["5/8", "1/2", "3/4"])
        report = json.loads(check_bytes(request, canonical_json_bytes(evidence)))
        self.assertEqual(report["status"], "checked")
        self.assertEqual(report["bounds"]["regret_upper"], "5/8")

    def test_valid_target_certificate_with_false_transport_provenance_is_rejected(self):
        request = comparator_request()
        evidence = json.loads(produce_bytes(request))
        evidence["alpha"] = ["0"]
        report = json.loads(check_bytes(request, canonical_json_bytes(evidence)))
        self.assertEqual(report["status"], "rejected")
        self.assertIn(report["diagnostics"][0]["code"], {"E_TRANSPORT_CORRECTION", "E_TRANSPORT_ENVELOPE"})

    def test_tampered_request_hash_is_rejected(self):
        request = comparator_request()
        evidence = json.loads(produce_bytes(request))
        evidence["request_sha256"] = "0" * 64
        report = json.loads(check_bytes(request, canonical_json_bytes(evidence)))
        self.assertEqual(report["status"], "rejected")
        self.assertEqual(report["diagnostics"][0]["code"], "E_TRANSPORT_BINDING")

    def test_invalid_source_certificate_supplies_no_transport_warrant(self):
        value = json.loads(comparator_request())
        value["source"]["certificate"] = {"lower": ["2"], "upper": ["2"]}
        with self.assertRaises(TransportError):
            produce_bytes(canonical_json_bytes(value))

    def test_changed_action_menu_is_unsupported(self):
        value = json.loads(comparator_request())
        value["target"]["subject"]["nodes"][0]["actions"][1]["label"] = "c"
        with self.assertRaises(TransportError) as caught:
            decode_request(canonical_json_bytes(value))
        self.assertEqual(caught.exception.code, "E_UNSUPPORTED_TRANSPORT")

    def test_changed_unit_is_unsupported(self):
        value = json.loads(comparator_request())
        value["target"]["subject"]["unit"] = "different-unit"
        with self.assertRaises(TransportError) as caught:
            decode_request(canonical_json_bytes(value))
        self.assertEqual(caught.exception.code, "E_UNSUPPORTED_TRANSPORT")

    def test_noncanonical_request_bytes_are_rejected(self):
        with self.assertRaises(TransportError) as caught:
            produce_bytes(comparator_request().rstrip(b"\n") + b" \n")
        self.assertEqual(caught.exception.code, "E_NONCANONICAL_JSON")

    def test_checker_does_not_need_producer(self):
        request = comparator_request()
        evidence = produce_bytes(request)
        import writ_decision_lab.transport.producer as producer
        original = producer.produce
        try:
            producer.produce = lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("producer disabled"))
            report = check_report(request, evidence)
        finally:
            producer.produce = original
        self.assertEqual(report["status"], "checked")

    def test_cli_is_creation_only_and_checker_round_trips(self):
        request = comparator_request()
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            request_path = temp_path / "request.json"
            evidence_path = temp_path / "evidence.json"
            report_path = temp_path / "report.json"
            request_path.write_bytes(request)
            env = dict(__import__("os").environ)
            env["PYTHONPATH"] = str(root / "src")
            solve = subprocess.run([sys.executable, "-m", "writ_decision_lab.transport", "solve", "--request", str(request_path), "--output", str(evidence_path)], cwd=root, env=env, capture_output=True, check=False)
            self.assertEqual(solve.returncode, 0, solve.stderr.decode())
            second = subprocess.run([sys.executable, "-m", "writ_decision_lab.transport", "solve", "--request", str(request_path), "--output", str(evidence_path)], cwd=root, env=env, capture_output=True, check=False)
            self.assertEqual(second.returncode, 2)
            check = subprocess.run([sys.executable, "-m", "writ_decision_lab.transport", "check", "--request", str(request_path), "--evidence", str(evidence_path), "--output", str(report_path)], cwd=root, env=env, capture_output=True, check=False)
            self.assertEqual(check.returncode, 0, check.stderr.decode())
            self.assertEqual(json.loads(report_path.read_bytes())["status"], "checked")


if __name__ == "__main__":
    unittest.main()
