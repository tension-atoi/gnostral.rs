#!/usr/bin/env python3
"""Independent offline auditor for the single-model Q013-C pilot.

No model server is started. Rehashes real engine and dense weights; does not
trust a provider's own assertion of semantic correctness.
"""
from __future__ import annotations
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import sys

from q013c_real_dense import BINARY_SHA, ENGINE, MODEL_SHA, Q012, Q012_SHA, WEIGHT, sha

def audit(session: Path, *, rehash: bool=True) -> dict:
    run=json.loads((session/"session.json").read_text())
    if run.get("schema")!="gnostral.q013c.real-dense-pilot.v1" or run.get("status")!="RUN_COMPLETED_PENDING_INDEPENDENT_AUDIT":
        raise ValueError("NOT_QUALIFIED: no completed Q013C real-dense pilot")
    pre=json.loads((session/"preflight.json").read_text())
    if run.get("preflight")!=pre:
        raise ValueError("NOT_QUALIFIED: preflight receipt mismatch")
    if pre.get("binary_sha256")!=BINARY_SHA or pre.get("model_weight_sha256")!=MODEL_SHA or pre.get("q012_evidence_sha256")!=Q012_SHA:
        raise ValueError("NOT_QUALIFIED: binary/weight/Q012 source identity drift")
    if sha(Q012)!=Q012_SHA:
        raise ValueError("NOT_QUALIFIED: Q012 source bytes changed")
    if rehash and (sha(ENGINE)!=BINARY_SHA or sha(WEIGHT)!=MODEL_SHA):
        raise ValueError("NOT_QUALIFIED: independent executable/weight rehash failed")
    if run.get("snapshot_sha256")!=BINARY_SHA or not run.get("process_reaped"):
        raise ValueError("NOT_QUALIFIED: executable snapshot or reaping")
    if not run.get("reclaim_within_128_mib") or not isinstance(run.get("gpu_ambient_delta_mib"),int) or abs(run["gpu_ambient_delta_mib"])>128:
        raise ValueError("NOT_QUALIFIED: GPU ambient recovery failed")
    if not isinstance(run.get("elapsed_s"),(int,float)) or not 0<run["elapsed_s"]<125:
        raise ValueError("NOT_QUALIFIED: runtime exceeded bound")
    if run.get("lifecycle")!=["PREFLIGHT","SNAPSHOT_VERIFIED","STARTED","HTTP_READY","SEMANTIC_RESPONSE_RETAINED"]:
        raise ValueError("NOT_QUALIFIED: lifecycle incomplete")
    response_path=session/"response-private.json"
    if sha(response_path)!=run.get("response_file_sha256"):
        raise ValueError("NOT_QUALIFIED: response bytes modified")
    raw=json.loads(response_path.read_text())
    choices=raw.get("choices")
    if not isinstance(choices,list) or len(choices)!=1:
        raise ValueError("NOT_QUALIFIED: invalid OpenAI-compatible completion envelope")
    message=choices[0].get("message",{})
    answer=message.get("content")
    if not isinstance(answer,str) or answer.strip()!="GNOSTRAL":
        raise ValueError("NOT_QUALIFIED: independent exact semantic oracle failed")
    if hashlib.sha256(answer.encode()).hexdigest()!=run.get("raw_output_sha256"):
        raise ValueError("NOT_QUALIFIED: semantic output digest mismatch")
    usage=raw.get("usage",{})
    if not isinstance(usage.get("completion_tokens"),int) or usage["completion_tokens"]<=0 or usage["completion_tokens"]>35:
        raise ValueError("NOT_QUALIFIED: incorrect completion token envelope")
    if pre["gpu_before"]["free_mib"]<5200 or pre["ram_available_mib"]<18000:
        raise ValueError("NOT_QUALIFIED: unsafe resource admission")
    cg=pre["boundary"]
    if not cg["cgroup"].endswith(".scope") or "/gnu6-lab.slice/" not in cg["cgroup"] or cg["memory.oom.group"]!=1:
        raise ValueError("NOT_QUALIFIED: scope identity")
    return {
        "schema":"gnostral.q013c.independent-real-dense-audit.v1",
        "audited_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "verdict":"Q013C_REAL_DENSE_SINGLE_SERVER_PASS",
        "exact_engine_sha256":BINARY_SHA,
        "exact_weight_sha256":MODEL_SHA,
        "q012_public_source_sha256":Q012_SHA,
        "real_server":True,
        "model_family":"dense",
        "completion_tokens":usage["completion_tokens"],
        "semantic_oracle":"exact uppercase GNOSTRAL",
        "response_file_sha256":run["response_file_sha256"],
        "session_sha256":sha(session/"session.json"),
        "gpu_card_before_mib":pre["gpu_before"]["used_mib"],
        "gpu_card_after_mib":run["gpu_after"]["used_mib"],
        "gpu_ambient_delta_mib":run["gpu_ambient_delta_mib"],
        "runtime_wall_s":run["elapsed_s"],
        "bounded_scope":True,"process_reaped":True,
        "model_weight_rehashed_independently":rehash,
        "nonclaims":["generalized semantic quality","MoE or embedding runtime integration",
                     "persistent/multi-model service","production supervisor","authenticated external semantic authority",
                     "NVIDIA VRAM pinning/isolation","hardware or OS security boundary"],
    }

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--session",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    try:
        result=audit(args.session)
        with args.output.open("x") as f:
            json.dump(result,f,indent=2,sort_keys=True);f.write("\n")
    except (OSError,KeyError,ValueError,TypeError) as exc:
        print(f"Q013C_INDEPENDENT_AUDIT_FAIL {exc}",file=sys.stderr)
        return 2
    print(result["verdict"],result["runtime_wall_s"],"seconds",flush=True)
    return 0

if __name__=="__main__":raise SystemExit(main())
