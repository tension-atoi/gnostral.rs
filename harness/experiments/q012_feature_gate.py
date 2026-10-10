#!/usr/bin/env python3
"""Fail-closed native CUDA + MoE residency build gate; no model is loaded."""
from __future__ import annotations
import argparse
import hashlib
import json
import mmap
from pathlib import Path

FEATURES = frozenset({"cuda", "gnostral-expert-residency"})
RESIDENCY_MARKER = b"native expert residency mixed-device admission"
COUNTERS_MARKER = "native expert residency engine counters initialized"
CACHELESS_GUARD = "!pipeline_metadata.no_kv_cache && pipeline.cache().is_hybrid(),"

def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def qualify(binary: Path, expected: str, fingerprint: Path, engine: Path,
            runtime_log: Path | None = None) -> dict:
    if len(expected) != 64 or any(c not in "0123456789abcdef" for c in expected):
        raise ValueError("expected SHA-256 must be 64 lowercase hexadecimal characters")
    data = json.loads(fingerprint.read_text())
    declared = data.get("features", [])
    # Cargo encodes the features list as a JSON string inside its fingerprint JSON.
    if isinstance(declared, str):
        declared = json.loads(declared)
    if not isinstance(declared, list) or not all(isinstance(v, str) for v in declared):
        raise ValueError("invalid Cargo fingerprint features payload")
    if not FEATURES.issubset(set(declared)):
        raise ValueError(f"missing required compiled feature: {sorted(FEATURES - set(declared))}")
    if engine.read_text().count(CACHELESS_GUARD) != 2:
        raise ValueError("two guarded no-KV hybrid-cache probes not found in source")
    with binary.open("rb") as fd:
        if not fd.seek(0, 2):
            raise ValueError("binary is empty")
        fd.seek(0)
        with mmap.mmap(fd.fileno(), 0, access=mmap.ACCESS_READ) as mapped:
            if mapped.find(RESIDENCY_MARKER) < 0:
                raise ValueError("native residency marker missing from executable")
    measured = digest(binary)
    if measured != expected:
        raise ValueError(f"binary digest mismatch: expected={expected} actual={measured}")
    if runtime_log is not None:
        log = runtime_log.read_text(errors="replace")
        if RESIDENCY_MARKER.decode() not in log or COUNTERS_MARKER not in log:
            raise ValueError("native residency admission and counters not observed at runtime")
    return {"schema": "gnostral.q012.feature-gate.v1",
            "verdict": "RUNTIME_RESIDENCY_WITNESS_PASS" if runtime_log else "BUILD_FEATURE_PRECHECK_PASS",
            "binary_sha256": measured, "compiled_features": sorted(declared),
            "runtime_witness": runtime_log is not None,
            "limits": ["source guards are not proof of binary source provenance",
                       "no inference or model-quality claim"]}

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--sha256", required=True, help="Previously recorded expected binary digest")
    parser.add_argument("--fingerprint", type=Path, required=True)
    parser.add_argument("--engine-source", type=Path, required=True)
    parser.add_argument("--runtime-log", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = qualify(args.binary, args.sha256, args.fingerprint,
                         args.engine_source, args.runtime_log)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        parser.exit(2, f"Q012_FEATURE_GATE_FAIL: {exc}\n")
    if args.output:
        if args.output.exists():
            parser.exit(2, "Q012_FEATURE_GATE_FAIL: refuse evidence overwrite\n")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x") as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write("\n")
    print(result["verdict"], result["binary_sha256"])

if __name__ == "__main__":
    main()
