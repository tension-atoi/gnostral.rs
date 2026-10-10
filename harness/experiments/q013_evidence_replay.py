#!/usr/bin/env python3
"""Q-013-A: fail-closed replay of published Q-012 evidence into probe-only plans.

This tool never runs a model or grants execution/OS authority.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "evidence/runs/gnostral-q012-native-three-families-20261010.json"
PINNED_SOURCE_SHA256 = "48241e35df171941e5d80a8f3832a55642de43d96abad04c0a000208e1cd3164"
PINNED_ENGINE_SHA256 = "64eec222ccefff4cd4c0067bd83348f1d22eebda27d0d857e352ee090cf19723"
OPERATIONS = {
    "dense": ("DenseSentinel", "text.chat"),
    "embedding": ("EmbeddingTriple1024", "embedding.vector"),
    "moe": ("MoeExpertSentence", "text.moe"),
}

def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()

def valid_sha(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(x in "0123456789abcdef" for x in value)

def replay(raw: bytes, *, expected_digest: str = PINNED_SOURCE_SHA256) -> dict:
    measured = sha256(raw)
    if not valid_sha(expected_digest) or measured != expected_digest:
        raise ValueError("evidence bytes disagree with pinned Q-012 digest")
    source = json.loads(raw)
    if source.get("schema") != "gnostral.q012.public-qualification.v1":
        raise ValueError("unsupported Q-012 public evidence schema")
    if source.get("verdict") != "THREE_FAMILIES_SAME_BINARY_PASS" or source.get("native_binary_sha256") != PINNED_ENGINE_SHA256:
        raise ValueError("Q-012 three-family gate or pinned engine identity not qualified")
    controls = source.get("independent_controls", {})
    if not all(controls.get(k) is True for k in
               ("all_servers_reaped", "single_binary_verified", "three_model_weight_hashes_revalidated")):
        raise ValueError("independent attestation incomplete")
    profiles = source.get("profiles", {})
    if not isinstance(profiles, dict) or set(profiles) != set(OPERATIONS):
        raise ValueError("missing or extra model operation")
    plans = []
    for key, (operation, probe_kind) in OPERATIONS.items():
        p = profiles[key]
        if p.get("status") != "PASS_FUNCTIONAL" or p.get("binary_sha256") != PINNED_ENGINE_SHA256:
            raise ValueError(f"{key}: unqualified profile or executable mismatch")
        if not valid_sha(p.get("model_weight_sha256")) or p.get("probe_kind") != probe_kind:
            raise ValueError(f"{key}: unsupported exact probe/model digest")
        peak = p.get("gpu_card_peak_mib")
        reclaim = p.get("gpu_reclaim_delta_mib")
        if not isinstance(peak, int) or peak <= 0 or not isinstance(reclaim, int) or abs(reclaim) > 128:
            raise ValueError(f"{key}: missing qualified resource observation")
        if key == "embedding" and (p.get("vector_count"), p.get("dimensions")) != (3, 1024):
            raise ValueError("embedding exact triple-vector oracle missing")
        plans.append({
            "operation": operation, "engine_sha256": PINNED_ENGINE_SHA256,
            "model_sha256": p["model_weight_sha256"],
            "evidence_ref": "sha256:" + measured,
            "profile": "Q012_SEQUENTIAL_FUNCTIONAL",
            "qualification": "Qualified",
            "observed_card_gpu_peak_mib": peak,
            "serving_mode": "OneShot",
            "execution_authorized": False,
        })
    return {
        "schema": "gnostral.q013.evidence-bound-plans.v1",
        "verdict": "EXACT_PROBE_PLANS_ONLY",
        "q012_source_sha256": measured,
        "plan_count": len(plans),
        "plans": plans,
        "limits": [
            "informational reference model only; never grants execution",
            "one-shot exact functional probes, not arbitrary user requests",
            "historical GPU card peaks are observations, not admission budgets",
            "no live host health, memory headroom, or production-readiness qualification",
        ],
    }

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = replay(SOURCE.read_bytes())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as fd:
        json.dump(result, fd, indent=2, sort_keys=True)
        fd.write("\n")
    print(result["verdict"], "plans", result["plan_count"])

if __name__ == "__main__":
    main()
