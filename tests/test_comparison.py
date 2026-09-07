from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from support import ROOT


class ComparisonTests(unittest.TestCase):
    def test_equal_information_frozen_sequence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "comparison.json"
            environment = dict(os.environ)
            environment["PYTHONPATH"] = str(ROOT / "src")
            run = subprocess.run(
                [sys.executable, str(ROOT / "comparison" / "run_sequence.py"), "--output", str(output)],
                cwd=ROOT,
                env=environment,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(run.returncode, 0, run.stderr)
            record = json.loads(output.read_bytes())
            self.assertTrue(record["candidate"]["all_passed"])
            self.assertTrue(record["simpler_baseline"]["all_passed"])
            self.assertEqual(record["candidate"]["erroneous_downstream_uses"], 0)
            self.assertEqual(record["simpler_baseline"]["erroneous_downstream_uses"], 0)
            baseline_source = (ROOT / "comparison" / "baseline.py").read_text()
            self.assertNotIn("import writ_decision_lab", baseline_source)
            self.assertNotIn("from writ_decision_lab", baseline_source)


if __name__ == "__main__":
    unittest.main()
