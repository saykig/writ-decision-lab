from __future__ import annotations

import json
import unittest

from writ_decision_lab.transport import produce_bytes
from writ_decision_lab.transport.exact import TransportError, canonical_json_bytes
from test_certificate_transport import comparator_request


class CertificateTransportLimitTests(unittest.TestCase):
    def test_model_coefficients_remain_capped_at_256_bits(self):
        value = json.loads(comparator_request())
        value["target"]["subject"]["nodes"][0]["actions"][0]["cost"] = str(2**300)
        with self.assertRaises(TransportError) as caught:
            produce_bytes(canonical_json_bytes(value))
        self.assertEqual(caught.exception.code, "E_RATIONAL_LIMIT")


if __name__ == "__main__":
    unittest.main()
