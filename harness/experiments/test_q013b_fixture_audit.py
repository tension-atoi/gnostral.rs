"""Fail-closed audit tests against local test log excerpts, no inference needed."""
import os
import json
import unittest
from pathlib import Path
from q013b_fixture_audit import parse, PINNED_FIXTURE, PINNED_Q012_RECEIPT

class Q013BFixtureAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        d = Path(os.environ.get(
            "GNOSTRAL_Q013B_TEST_EVIDENCE_DIR",
            str(Path(__file__).resolve().parents[2] / "evidence/private/q013b")))
        if (d / "isolation-e2e-test-qualified.log").exists():
            # Real machine's retained private session, when available.
            cls.test_log = (d / "isolation-e2e-test-qualified.log").read_text()
            cls.inside = (d / "boundary-inside.log").read_text()
            cls.outside = (d / "boundary-outside.log").read_text()
            cls.exit_code = (d / "boundary-outside-exit-code.txt").read_text()
        else:
            # Clean-checkout parser fixtures derived from public, sanitized receipt.
            public = Path(__file__).resolve().parents[2] / (
                "evidence/runs/gnostral-q013b-fixture-process-20261010.json")
            runs = json.loads(public.read_text())["runs"]
            lines = [f"test case_{i} ... ok" for i in range(11)]
            for name, v in runs.items():
                lines.append(
                    "Q013B_SAMPLE "
                    f"name={name} outcome={v['outcome']} ms={v['duration_ms']} "
                    f"before_mem={v['cpu_cgroup_memory_before_bytes']} "
                    f"after_mem={v['cpu_cgroup_memory_after_bytes']} "
                    f"before_swap={v['cpu_cgroup_swap_before_bytes']} "
                    f"after_swap={v['cpu_cgroup_swap_after_bytes']} "
                    "oom_unchanged=true returned=true gpu_reclaim=false "
                    f"group_killed={str(v['group_killed']).lower()}"
                )
            lines.append("test result: ok. 11 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out;")
            cls.test_log = "\n".join(lines)
            cls.inside = "Q013B_BOUNDARY_PASS /user.slice/user@1000/gnu6-lab.slice/run-test.scope"
            cls.outside = "Q013B_BOUNDARY_DENIED Unisolated"
            cls.exit_code = "73"

    def audit(self, **kwargs):
        d = {"test_log": self.test_log, "inside": self.inside,
             "outside": self.outside, "exit_code": self.exit_code,
             "fixture_sha": PINNED_FIXTURE, "q012_sha": PINNED_Q012_RECEIPT}
        d.update(kwargs)
        return parse(**d)

    def test_eight_receipts_parse_in_real_or_clean_checkout_mode(self):
        self.assertEqual(self.audit()["observed_process_runs"], 8)

    def test_missing_group_kill_refused(self):
        damaged = self.test_log.replace("group_killed=true", "group_killed=false", 1)
        with self.assertRaisesRegex(ValueError, "kill-on-timeout"):
            self.audit(test_log=damaged)

    def test_oom_or_reclaim_regression_refused(self):
        with self.assertRaisesRegex(ValueError, "reclaim or OOM"):
            self.audit(test_log=self.test_log.replace("oom_unchanged=true", "oom_unchanged=false", 1))
        with self.assertRaisesRegex(ValueError, "reclaim or OOM"):
            self.audit(test_log=self.test_log.replace("returned=true", "returned=false", 1))

    def test_unwrapped_scope_no_longer_rejected_refused(self):
        with self.assertRaisesRegex(ValueError, "unwrapped execution"):
            self.audit(exit_code="0")

    def test_wrong_fixture_digest_refused(self):
        with self.assertRaisesRegex(ValueError, "identity drift"):
            self.audit(fixture_sha="0" * 64)

    def test_gpu_reclaim_overclaim_refused(self):
        with self.assertRaisesRegex(ValueError, "falsely promoted"):
            self.audit(test_log=self.test_log.replace("gpu_reclaim=false", "gpu_reclaim=true", 1))

if __name__ == "__main__":
    unittest.main()
