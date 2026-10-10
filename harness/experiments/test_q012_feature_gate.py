"""Q-012 compile-time capability gate with synthetic, no-GPU fixtures."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from q012_feature_gate import CACHELESS_GUARD, RESIDENCY_MARKER, qualify

class TestFeatureGate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.binary = self.root / "mistralrs"
        self.binary.write_bytes(b"header:" + RESIDENCY_MARKER + b":tail")
        self.expected = hashlib.sha256(self.binary.read_bytes()).hexdigest()
        self.fp = self.root / "lib-mistralrs_core.json"
        self.engine = self.root / "engine.rs"
        self.log = self.root / "moe-server.log"
        self.set_features(["cuda", "gnostral-expert-residency"])
        self.engine.write_text(CACHELESS_GUARD + "\n" + CACHELESS_GUARD + "\n")
        self.log.write_text(RESIDENCY_MARKER.decode() +
                            "\nnative expert residency engine counters initialized\n")

    def set_features(self, features):
        self.fp.write_text(json.dumps({"features": json.dumps(features)}))

    def test_compile_and_runtime_positive(self):
        result = qualify(self.binary, self.expected, self.fp, self.engine, self.log)
        self.assertEqual(result["verdict"], "RUNTIME_RESIDENCY_WITNESS_PASS")
        self.assertTrue(result["runtime_witness"])

    def test_feature_omission_rejected(self):
        self.set_features(["cuda"])
        with self.assertRaisesRegex(ValueError, "missing required compiled feature"):
            qualify(self.binary, self.expected, self.fp, self.engine)

    def test_marker_omission_rejected(self):
        self.binary.write_bytes(b"not a residency binary")
        with self.assertRaisesRegex(ValueError, "marker missing"):
            qualify(self.binary, self.expected, self.fp, self.engine)

    def test_missing_cacheless_guard_rejected(self):
        self.engine.write_text(CACHELESS_GUARD)
        with self.assertRaisesRegex(ValueError, "two guarded"):
            qualify(self.binary, self.expected, self.fp, self.engine)

    def test_binary_hash_mismatch_rejected(self):
        with self.assertRaisesRegex(ValueError, "binary digest mismatch"):
            qualify(self.binary, "0" * 64, self.fp, self.engine)

    def test_runtime_missing_counters_rejected(self):
        self.log.write_text(RESIDENCY_MARKER.decode())
        with self.assertRaisesRegex(ValueError, "counters"):
            qualify(self.binary, self.expected, self.fp, self.engine, self.log)

    def test_bad_expected_hash_rejected(self):
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            qualify(self.binary, "abc", self.fp, self.engine)

if __name__ == "__main__":
    unittest.main()
