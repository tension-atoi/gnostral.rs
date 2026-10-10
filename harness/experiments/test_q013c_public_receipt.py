"""Checks publication-safe metadata of the independently audited real dense pilot."""
import json
import unittest
from pathlib import Path

from q013c_real_dense import BINARY_SHA, MODEL_SHA, Q012_SHA

PUBLIC = Path(__file__).resolve().parents[2] / (
    "evidence/runs/gnostral-q013c-real-dense-single-server-20261010.json"
)

class Q013CPublicReceipt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=PUBLIC.read_text()
        cls.doc=json.loads(cls.raw)

    def test_exact_qualified_provenance(self):
        d=self.doc
        self.assertEqual(d["verdict"],"Q013C_REAL_DENSE_SINGLE_SERVER_PASS")
        self.assertEqual(d["schema"],"gnostral.q013c.independent-real-dense-audit.v1")
        self.assertEqual(d["exact_engine_sha256"],BINARY_SHA)
        self.assertEqual(d["exact_weight_sha256"],MODEL_SHA)
        self.assertEqual(d["q012_public_source_sha256"],Q012_SHA)
        self.assertTrue(d["model_weight_rehashed_independently"])

    def test_bound_runtime_and_gpu_recovery(self):
        d=self.doc
        self.assertGreater(d["runtime_wall_s"],0)
        self.assertLess(d["runtime_wall_s"],125)
        self.assertLessEqual(abs(d["gpu_ambient_delta_mib"]),128)
        self.assertEqual(d["gpu_card_after_mib"]-d["gpu_card_before_mib"],d["gpu_ambient_delta_mib"])
        self.assertTrue(d["process_reaped"])
        self.assertTrue(d["bounded_scope"])

    def test_no_private_traces_or_broad_claim(self):
        self.assertNotIn("/mnt/",self.raw)
        self.assertNotIn("/home/",self.raw)
        self.assertNotIn("engine.log",self.raw)
        self.assertNotIn("response-private.json",self.raw)
        self.assertEqual(self.doc["model_family"],"dense")
        self.assertIn("MoE or embedding runtime integration",self.doc["nonclaims"])
        self.assertEqual(len(self.doc["private_audit_sha256"]),64)

if __name__=="__main__":unittest.main()
