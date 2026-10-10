"""Static regression contract for Q012's narrow no-KV-cache initialization guard.

Not a substitute for a rebuilt CUDA binary and live embedding inference.
"""
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PATCH = ROOT/"patches/q012/mistralrs-engine-embedding-no-kv-startup.patch"


class Q012NoKvStartupPatch(unittest.TestCase):
    def test_patch_only_changes_two_is_hybrid_evaluations(self):
        text = PATCH.read_text()
        self.assertEqual(text.count("+                !pipeline_metadata.no_kv_cache && pipeline.cache().is_hybrid(),"), 2)
        self.assertEqual(text.count("-                pipeline.cache().is_hybrid(),"), 2)
        self.assertIn("mistralrs-core/src/engine/mod.rs", text)
        self.assertNotIn("src/pipeline/embedding.rs", text)

    def test_explicit_cacheless_contract_and_protected_call(self):
        source = ROOT/"vendor/mistralrs-strata/mistralrs-core/src/pipeline/embedding.rs"
        engine = ROOT/"vendor/mistralrs-strata/mistralrs-core/src/engine/mod.rs"
        if not source.is_file() or not engine.is_file():
            self.skipTest("optional vendor source not populated; patch-level assertions remain")
        text=source.read_text()
        self.assertIn("no_kv_cache: true",text)
        self.assertTrue(text.split("fn cache(&self) -> &EitherCache {", 1)[1].lstrip().startswith("unreachable!()"))
        self.assertEqual(engine.read_text().count("!pipeline_metadata.no_kv_cache && pipeline.cache().is_hybrid(),"),2)


if __name__=="__main__":
    unittest.main()
