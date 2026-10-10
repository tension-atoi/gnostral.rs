#!/usr/bin/env python3
"""Negative fixtures: reject incomplete, forged and overclaimed placement evidence."""
import copy
import json
import unittest

import evidence


class TestPlacement(unittest.TestCase):
    raw = """Using automatic device mapping parameters: text[max_seq_len: 4096, max_batch_size: 1].
Layers 0-12: cuda[0] (8 GB)
Layers 13-47: cpu (32 GB)
native expert residency mixed-device admission cpu_layers=35 gpu_layers=13 excluded_cpu_profile_entries=140
Device mapping contains a mix of GPU and CPU. There is no CPU support for PagedAttention, disabling PagedAttention.
Model loaded.
"""

    def test_placement_parser(self):
        result = evidence.parse_mapping(self.raw)
        self.assertEqual((result["gpu_layers"], result["cpu_layers"], result["total_layers"]),
                         (13, 35, 48))
        self.assertEqual(result["placement_estimate_max_seq_len"], 4096)

    def test_noncontiguous_fails(self):
        with self.assertRaisesRegex(evidence.EvidenceError, "non-contiguous"):
            evidence.parse_mapping(self.raw.replace("Layers 13-47", "Layers 14-47"))

    def test_residency_mismatch_fails(self):
        with self.assertRaisesRegex(evidence.EvidenceError, "residency differs"):
            evidence.parse_mapping(self.raw.replace("gpu_layers=13", "gpu_layers=14"))

    def test_missing_automatic_mapping_fails(self):
        with self.assertRaisesRegex(evidence.EvidenceError, "parameters missing"):
            evidence.parse_mapping(self.raw.replace("Using automatic device mapping parameters:", "Other:"))

    def test_no_paged_attention_witness_fails(self):
        with self.assertRaisesRegex(evidence.EvidenceError, "PagedAttention"):
            evidence.parse_mapping(self.raw.replace("disabling PagedAttention.", "PagedAttention active."))

    def minimal_receipt(self):
        return {
            "status":"PASS_SAMPLES","engine":"candidate","repeat":1,
            "server_reaped":True,"ctx_requested":1024,"reclaim_delta_mib":12,
            "before":{"gpu":{"free_mib":4700,"used_mib":3300},"ram_available_mib":22100},
            "telemetry":{"samples":80,"peak_total_gpu_used_mib":4430,"peak_owned_process_tree_rss_mib":21000},
            "samples":{"128":{"tokens":52,"tps_engine":19.2,"separate_request_stream":{"first_text_ms":700}},
                       "512":{"tokens":198,"tps_engine":20.3}}
        }

    def test_audit_reclaim_fails_closed(self):
        d = self.minimal_receipt()
        evidence.verify_receipt(d, mode="pressure", repetition=1)
        bad = copy.deepcopy(d)
        bad["reclaim_delta_mib"] = 196
        with self.assertRaisesRegex(evidence.EvidenceError, "GPU reclaim"):
            evidence.verify_receipt(bad, mode="pressure", repetition=1)

    def test_missing_server_reap_fails(self):
        d = self.minimal_receipt()
        d["server_reaped"] = False
        with self.assertRaisesRegex(evidence.EvidenceError, "not reaped"):
            evidence.verify_receipt(d, mode="control", repetition=1)

    def test_pressure_missing_handshake_fails(self):
        parent = {"status":"PASS_SAMPLES","holder_alive_at_end":False}
        with self.assertRaisesRegex(evidence.EvidenceError, "reservation exited"):
            evidence.verify_pressure(None,"pressure",1,
                {"pre_server_gpu_used_mib":3401,"pre_server_gpu_free_mib":4486},2,parent,
                "TRIAL_BEGIN 2 6 pressure 1 GPU 1200",2048)


if __name__ == "__main__":
    unittest.main()
