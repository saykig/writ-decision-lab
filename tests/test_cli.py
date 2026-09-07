from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from support import ROOT, changed, fixture


class CliIntegrationTests(unittest.TestCase):
    def command(self, *arguments: str, cwd: Path | None = None) -> subprocess.CompletedProcess[bytes]:
        environment = dict(os.environ)
        environment["PYTHONPATH"] = str(ROOT / "src")
        return subprocess.run(
            [sys.executable, *arguments],
            cwd=cwd or ROOT,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def full_path(self, directory: Path) -> tuple[bytes, bytes, bytes]:
        directory.mkdir(parents=True)
        result = directory / "result.json"
        check = directory / "check.json"
        consumer = directory / "consumer.json"
        solve_run = self.command(
            "-m", "writ_decision_lab", "solve",
            "--model", str(ROOT / "examples/weak/model.json"),
            "--query", str(ROOT / "examples/weak/query.json"),
            "--output", str(result),
        )
        self.assertEqual(solve_run.returncode, 0, solve_run.stderr)
        check_run = self.command(
            "-m", "writ_decision_lab", "check",
            "--model", str(ROOT / "examples/weak/model.json"),
            "--query", str(ROOT / "examples/weak/query.json"),
            "--result", str(result), "--output", str(check),
        )
        self.assertEqual(check_run.returncode, 0, check_run.stderr)
        consume_run = self.command(
            str(ROOT / "examples/consume_answer.py"),
            "--expected-model", str(ROOT / "examples/weak/model.json"),
            "--expected-query", str(ROOT / "examples/weak/query.json"),
            "--result", str(result), "--output", str(consumer),
        )
        self.assertEqual(consume_run.returncode, 0, consume_run.stderr)
        return result.read_bytes(), check.read_bytes(), consumer.read_bytes()

    def test_separate_process_path_and_second_directory_are_byte_reproducible(self) -> None:
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            artifacts1 = self.full_path(Path(first) / "run")
            artifacts2 = self.full_path(Path(second) / "run")
        self.assertEqual(artifacts1, artifacts2)
        self.assertEqual(json.loads(artifacts1[1])["status"], "checked")
        self.assertEqual(json.loads(artifacts1[2])["evsi"], "1/8")

    def test_refuses_overwriting_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "result.json"
            output.write_bytes(b"keep\n")
            run = self.command(
                "-m", "writ_decision_lab", "solve",
                "--model", str(ROOT / "examples/weak/model.json"),
                "--query", str(ROOT / "examples/weak/query.json"),
                "--output", str(output),
            )
            self.assertEqual(run.returncode, 2)
            self.assertEqual(output.read_bytes(), b"keep\n")

    def test_missing_check_input_writes_not_checked_record(self) -> None:
        model, query = fixture("F01-weak")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            result = root / "result.json"
            output = root / "check.json"
            result.write_bytes(self._solve(model, query))
            run = self.command(
                "-m", "writ_decision_lab", "check",
                "--model", str(root / "missing-model.json"),
                "--query", str(ROOT / "examples/weak/query.json"),
                "--result", str(result), "--output", str(output),
            )
            self.assertEqual(run.returncode, 6)
            record = json.loads(output.read_bytes())
            self.assertEqual(record["status"], "not_checked")
            self.assertIsNone(record["subject"]["model_sha256"])

    def _solve(self, model: bytes, query: bytes) -> bytes:
        from writ_decision_lab import solve_bytes
        return solve_bytes(model, query)

    def test_failed_consumer_writes_no_functional_output(self) -> None:
        model, query = fixture("F01-weak")
        result = changed(self._solve(model, query), lambda value: value["answer"].__setitem__("evsi", "1/4"))
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            result_path = root / "tampered.json"
            output = root / "consumer.json"
            result_path.write_bytes(result)
            run = self.command(
                str(ROOT / "examples/consume_answer.py"),
                "--expected-model", str(ROOT / "examples/weak/model.json"),
                "--expected-query", str(ROOT / "examples/weak/query.json"),
                "--result", str(result_path), "--output", str(output),
            )
            self.assertEqual(run.returncode, 5)
            self.assertFalse(output.exists())

    def test_unsupported_two_observation_semantics_exits_three(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            query = root / "query.json"
            query.write_bytes(changed((ROOT / "examples/weak/query.json").read_bytes(), lambda value: value.__setitem__("semantics", "finite-two-observation.v1")))
            run = self.command(
                "-m", "writ_decision_lab", "solve",
                "--model", str(ROOT / "examples/weak/model.json"),
                "--query", str(query), "--output", str(root / "result.json"),
            )
            self.assertEqual(run.returncode, 3)
            self.assertFalse((root / "result.json").exists())


if __name__ == "__main__":
    unittest.main()
