"""Static public evidence validation; no model files or CUDA required."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RECEIPT = ROOT / "evidence/runs/gnostral-q012-native-three-families-20261010.json"

class Q012PublicReceipt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = RECEIPT.read_text()
        cls.record = json.loads(cls.raw)

    def test_closed_gate_uses_one_real_binary(self):
        r = self.record
        self.assertEqual(r["verdict"], "THREE_FAMILIES_SAME_BINARY_PASS")
        self.assertEqual(len(r["native_binary_sha256"]), 64)
        for key in ("dense", "moe", "embedding"):
            self.assertEqual(r["profiles"][key]["status"], "PASS_FUNCTIONAL")
            self.assertEqual(r["profiles"][key]["binary_sha256"], r["native_binary_sha256"])
            self.assertLessEqual(abs(r["profiles"][key]["gpu_reclaim_delta_mib"]), 128)

    def test_moe_residency_and_negative_witness(self):
        r = self.record
        self.assertEqual(r["feature_regression"]["omitted_feature"], "gnostral-expert-residency")
        self.assertTrue(r["feature_regression"]["runtime_residency_witness"])
        self.assertGreater(r["feature_regression"]["first_attempt_moe_gpu_peak_mib"],
                           r["feature_regression"]["corrected_moe_gpu_peak_mib"])
        self.assertEqual(r["independent_controls"]["five_historical_negative_classes_kept"], 5)

    def test_embedding_numeric_oracle(self):
        emb = self.record["profiles"]["embedding"]
        self.assertEqual((emb["vector_count"], emb["dimensions"]), (3, 1024))
        self.assertGreater(emb["related_cosine"], emb["unrelated_cosine"])
        self.assertEqual(len(emb["raw_vector_sha256"]), 64)

    def test_no_private_host_paths_or_raw_vectors(self):
        self.assertNotIn("/home/", self.raw)
        self.assertNotIn("/mnt/", self.raw)
        self.assertNotIn("embedding-vectors-private.json", self.raw)

if __name__ == "__main__":
    unittest.main()
