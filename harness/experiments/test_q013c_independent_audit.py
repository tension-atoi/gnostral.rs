"""Q013-C independent gate: portable synthetic positives and fail-closed negatives.

Fixtures are deliberately synthetic; the published real-hardware verdict is
held separately and requires --rehash during its original audit.
"""
from __future__ import annotations
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from q013c_independent_audit import audit
from q013c_real_dense import BINARY_SHA, MODEL_SHA, Q012_SHA

class Q013CAuditContract(unittest.TestCase):
    def setUp(self):
        self.work=tempfile.TemporaryDirectory(prefix="q013c-negative-")
        self.addCleanup(self.work.cleanup)
        self.dir=Path(self.work.name)
        self.response={
            "choices":[{"message":{"role":"assistant","content":"GNOSTRAL"}}],
            "usage":{"completion_tokens":4,"prompt_tokens":42,"total_tokens":46},
        }
        self.pre={
            "binary_sha256":BINARY_SHA,"model_weight_sha256":MODEL_SHA,
            "q012_evidence_sha256":Q012_SHA,
            "gpu_before":{"used_mib":750,"free_mib":7120,"utilization_pct":1},
            "ram_available_mib":21000,
            "boundary":{"cgroup":"/user.slice/user@1000/gnu6-lab.slice/run-test.scope",
                        "memory.oom.group":1},
        }
        self.receipt={
            "schema":"gnostral.q013c.real-dense-pilot.v1",
            "status":"RUN_COMPLETED_PENDING_INDEPENDENT_AUDIT",
            "preflight":self.pre,"snapshot_sha256":BINARY_SHA,"process_reaped":True,
            "reclaim_within_128_mib":True,"gpu_ambient_delta_mib":8,
            "elapsed_s":17.0,
            "gpu_after":{"used_mib":758,"free_mib":7112},
            "lifecycle":["PREFLIGHT","SNAPSHOT_VERIFIED","STARTED","HTTP_READY",
                         "SEMANTIC_RESPONSE_RETAINED"],
        }
        self.write()

    def write(self):
        path=self.dir/"response-private.json"
        path.write_text(json.dumps(self.response,sort_keys=True))
        answer=self.response["choices"][0]["message"]["content"]
        self.receipt["raw_output_sha256"]=hashlib.sha256(answer.encode()).hexdigest()
        self.receipt["response_file_sha256"]=hashlib.sha256(path.read_bytes()).hexdigest()
        (self.dir/"preflight.json").write_text(json.dumps(self.pre,sort_keys=True))
        (self.dir/"session.json").write_text(json.dumps(self.receipt,sort_keys=True))

    def positive(self):
        return audit(self.dir,rehash=False)

    def test_portable_synthetic_reference(self):
        result=self.positive()
        self.assertEqual(result["verdict"],"Q013C_REAL_DENSE_SINGLE_SERVER_PASS")
        self.assertFalse(result["model_weight_rehashed_independently"])

    def test_semantic_wrong_word_rejected(self):
        self.response["choices"][0]["message"]["content"]="GNOSTRAI"
        self.write()
        with self.assertRaisesRegex(ValueError,"semantic oracle"):
            self.positive()

    def test_fake_completed_or_no_stop_rejected(self):
        self.receipt["process_reaped"]=False
        self.write()
        with self.assertRaisesRegex(ValueError,"reaping"):
            self.positive()

    def test_old_or_wrong_engine_sha_rejected(self):
        self.pre["binary_sha256"]="0"*64
        self.write()
        with self.assertRaisesRegex(ValueError,"identity drift"):
            self.positive()

    def test_model_weight_sha_drift_rejected(self):
        self.pre["model_weight_sha256"]="0"*64
        self.write()
        with self.assertRaisesRegex(ValueError,"identity drift"):
            self.positive()

    def test_reclaim_flag_without_sufficient_gpu_delta_rejected(self):
        self.receipt["gpu_ambient_delta_mib"]=129
        self.write()
        with self.assertRaisesRegex(ValueError,"GPU ambient recovery"):
            self.positive()

    def test_no_protected_cgroup_rejected(self):
        self.pre["boundary"]["cgroup"]="/user.slice/other.service"
        self.write()
        with self.assertRaisesRegex(ValueError,"scope identity"):
            self.positive()

    def test_response_tamper_after_session_rejected(self):
        self.write()
        with (self.dir/"response-private.json").open("a") as f:f.write(" ")
        with self.assertRaisesRegex(ValueError,"response bytes modified"):
            self.positive()

    def test_missing_semantic_lifecycle_gate_rejected(self):
        self.receipt["lifecycle"].remove("SEMANTIC_RESPONSE_RETAINED")
        self.write()
        with self.assertRaisesRegex(ValueError,"lifecycle incomplete"):
            self.positive()

    def test_wrong_token_budget_rejected(self):
        self.response["usage"]["completion_tokens"]=200
        self.write()
        with self.assertRaisesRegex(ValueError,"token envelope"):
            self.positive()

    def test_not_completed_status_refused(self):
        self.receipt["status"]="NOT_QUALIFIED"
        self.write()
        with self.assertRaisesRegex(ValueError,"no completed"):
            self.positive()

if __name__=="__main__":unittest.main()
