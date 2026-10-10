"""Offline Q-013 replay tests over the actual published Q-012 receipt."""
import copy
import json
import unittest

from q013_evidence_replay import SOURCE, PINNED_SOURCE_SHA256, replay, sha256

class Q013EvidenceReplay(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = SOURCE.read_bytes()
        cls.doc = json.loads(cls.raw)

    def mutate(self, transform):
        document = copy.deepcopy(self.doc)
        transform(document)
        tampered = json.dumps(document).encode()
        # Synthetic tests supply a test digest: the actual CLI accepts only the pinned digest.
        return replay(tampered, expected_digest=sha256(tampered))

    def test_real_q012_source_matches_pinned_hash_and_exact_three(self):
        self.assertEqual(sha256(self.raw), PINNED_SOURCE_SHA256)
        result = replay(self.raw)
        self.assertEqual(result["verdict"], "EXACT_PROBE_PLANS_ONLY")
        self.assertEqual(result["plan_count"], 3)
        self.assertEqual({x["operation"] for x in result["plans"]},
                         {"DenseSentinel", "EmbeddingTriple1024", "MoeExpertSentence"})
        self.assertTrue(all(x["execution_authorized"] is False for x in result["plans"]))

    def test_mutated_source_bytes_refused_by_frozen_hash(self):
        with self.assertRaisesRegex(ValueError, "pinned Q-012 digest"):
            replay(self.raw + b" ")

    def test_moe_regression_or_wrong_binary_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "unqualified"):
            self.mutate(lambda v: v["profiles"]["moe"].update(status="NOT_QUALIFIED"))
        with self.assertRaisesRegex(ValueError, "unqualified"):
            self.mutate(lambda v: v["profiles"]["dense"].update(binary_sha256="0" * 64))

    def test_extra_model_or_missing_model_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "missing or extra"):
            self.mutate(lambda v: v["profiles"].update(other=v["profiles"]["moe"]))
        with self.assertRaisesRegex(ValueError, "missing or extra"):
            self.mutate(lambda v: v["profiles"].pop("embedding"))

    def test_unknown_probe_and_embedding_dimensions_refused(self):
        with self.assertRaisesRegex(ValueError, "unsupported exact probe"):
            self.mutate(lambda v: v["profiles"]["moe"].update(probe_kind="text.chat"))
        with self.assertRaisesRegex(ValueError, "triple-vector"):
            self.mutate(lambda v: v["profiles"]["embedding"].update(dimensions=768))

    def test_missing_independent_rehash_and_reclaim_failure_refused(self):
        with self.assertRaisesRegex(ValueError, "independent attestation"):
            self.mutate(lambda v: v["independent_controls"].update(three_model_weight_hashes_revalidated=False))
        with self.assertRaisesRegex(ValueError, "resource observation"):
            self.mutate(lambda v: v["profiles"]["dense"].update(gpu_reclaim_delta_mib=129))

if __name__ == "__main__":
    unittest.main()
