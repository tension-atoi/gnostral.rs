"""Public documentation gate: real entrypoint acceptance and fail-closed negatives."""
from __future__ import annotations
import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("check-doc-links.py")
spec = importlib.util.spec_from_file_location("check_doc_links", SCRIPT)
gate = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(gate)

class TestPublicDocumentationGate(unittest.TestCase):
    def test_real_repository_active_entrypoints(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(gate.validate(root), [])

    def test_broken_link_is_detected_not_silently_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "README.md").write_text("# Example\n[bad relative link](does-not-exist.md)\n")
            errors = gate.validate(p)
            self.assertTrue(any("broken local link" in e for e in errors), errors)

    def test_absolute_local_link_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "README.md").write_text("[private local file](/tmp/secret-file.txt)\n")
            errors = gate.validate(p)
            self.assertTrue(any("absolute filesystem link" in e for e in errors), errors)

if __name__ == "__main__":
    unittest.main()
