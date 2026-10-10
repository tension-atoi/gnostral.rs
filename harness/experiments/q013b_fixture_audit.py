#!/usr/bin/env python3
"""Q013-B fixture qualification from independent retained subprocess/test logs.

Read-only inputs; fail-closed outputs; no weights, model runtime or network required.
"""
from __future__ import annotations
import argparse
import datetime
import hashlib
import json
import re
from pathlib import Path

EXPECTED = {
    "Q013B_DENSE=GNOSTRAL": "ProbePass",
    "Q013B_EMBEDDING=3x1024_FINITE": "ProbePass",
    "Q013B_MOE=CPU_EXPERTS": "ProbePass",
    "timeout": "TimedOut",
    "cancel": "Cancelled",
    "timeout_descendant": "TimedOut",
    "process_exit_23": "ProcessFailed",
    "invalid_output": "SemanticReject",
}
KILLED = {"timeout", "cancel", "timeout_descendant"}
PINNED_FIXTURE = "60dee3e056d442ac779edb6f799f2d2926c6916e636752de4183b2bf12955c40"
PINNED_Q012_RECEIPT = "48241e35df171941e5d80a8f3832a55642de43d96abad04c0a000208e1cd3164"

def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for buf in iter(lambda: stream.read(65536), b""):
            h.update(buf)
    return h.hexdigest()

def parse(test_log: str, inside: str, outside: str, exit_code: str, fixture_sha: str, q012_sha: str) -> dict:
    if fixture_sha != PINNED_FIXTURE or q012_sha != PINNED_Q012_RECEIPT:
        raise ValueError("Q013B fixture binary or Q012 evidence identity drift")
    if not re.search(r"test result: ok\. 11 passed; 0 failed; 0 ignored;", test_log):
        raise ValueError("isolated process suite not fully passed")
    if len(re.findall(r"^test [a-zA-Z0-9_]+ \.\.\.", test_log, flags=re.MULTILINE)) != 11:
        raise ValueError("insufficient case-level witnesses")
    rows = {}
    for line in test_log.splitlines():
        if "Q013B_SAMPLE " not in line:
            continue
        items = {}
        for token in line.partition("Q013B_SAMPLE ")[2].split():
            if "=" not in token:
                raise ValueError("unexpected sample token")
            key, val = token.split("=", 1)
            items[key] = val
        label = items.get("name")
        if label not in EXPECTED or label in rows:
            raise ValueError("unexpected or duplicate subprocess receipt")
        if items.get("outcome") != EXPECTED[label]:
            raise ValueError("semantic or lifecycle outcome changed")
        for field in ("oom_unchanged", "returned"):
            if items.get(field) != "true":
                raise ValueError("missing bounded CPU cgroup reclaim or OOM gate")
        if items.get("gpu_reclaim") != "false":
            raise ValueError("CPU-only proof falsely promoted GPU reclaim")
        if (items.get("group_killed") == "true") != (label in KILLED):
            raise ValueError("kill-on-timeout/cancel invariant broken")
        ms = int(items["ms"])
        if not 1 <= ms <= 3000:
            raise ValueError("unbounded fixture duration")
        before = int(items["before_mem"])
        after = int(items["after_mem"])
        if before < 0 or after < 0 or after > before + 32 * 1024 * 1024:
            raise ValueError("cgroup memory return threshold exceeded")
        if int(items["after_swap"]) > int(items["before_swap"]) + 32 * 1024 * 1024:
            raise ValueError("cgroup swap return threshold exceeded")
        rows[label] = {
            "outcome": items["outcome"], "duration_ms": ms,
            "cpu_cgroup_memory_before_bytes": before, "cpu_cgroup_memory_after_bytes": after,
            "cpu_cgroup_swap_before_bytes": int(items["before_swap"]),
            "cpu_cgroup_swap_after_bytes": int(items["after_swap"]),
            "group_killed": label in KILLED, "oom_events_unchanged": True,
            "bounded_cpu_reclaim": True,
        }
    if set(rows) != set(EXPECTED):
        raise ValueError(f"missing or extra subprocess samples: {set(EXPECTED) - set(rows)}")
    if "Q013B_BOUNDARY_PASS " not in inside or "/gnu6-lab.slice/" not in inside:
        raise ValueError("bounded session admission not demonstrated")
    if "Q013B_BOUNDARY_DENIED Unisolated" not in outside or exit_code.strip() != "73":
        raise ValueError("unwrapped execution was not rejected")
    return {"schema": "gnostral.q013b.fixture-process-qualification.v1",
            "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "verdict": "Q013B_FIXTURE_PROCESS_CONTAINMENT_PASS",
            "fixture_binary_sha256": fixture_sha,
            "source_q012_public_receipt_sha256": q012_sha,
            "test_cases": 11, "observed_process_runs": len(rows),
            "runs": rows,
            "boundary": {"bounded_scope_accepted": True, "unwrapped_scope_refused_code": 73},
            "qualified": ["CPU-only fixture subprocess","SHA-pinned isolated executable snapshot",
                          "bounded timeout/cancellation with process-group kill",
                          "exact marker oracle rejection", "observed CPU cgroup reclaim"],
            "not_qualified": ["real Q-012 model adapter", "GPU VRAM reclaim", "production inference",
                              "multi-model residency", "arbitrary process execution permission",
                              "integrity against a malicious process with the same user ID",
                              "signed semantic attestation independent of this fixture"]}

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--session", type=Path, required=True)
    ap.add_argument("--fixture", type=Path, required=True)
    ap.add_argument("--q012", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    d = args.session
    inputs = {
        name: d.joinpath(name).read_text() for name in
        ("isolation-e2e-test-qualified.log", "boundary-inside.log",
         "boundary-outside.log", "boundary-outside-exit-code.txt")
    }
    result = parse(inputs["isolation-e2e-test-qualified.log"], inputs["boundary-inside.log"],
                   inputs["boundary-outside.log"], inputs["boundary-outside-exit-code.txt"],
                   sha(args.fixture), sha(args.q012))
    result["private_source_logs_sha256"] = {
        name: sha(d / name) for name in inputs
    }
    if args.output.exists():
        ap.error("refusing to overwrite existing evidence receipt")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as f:
        json.dump(result, f, indent=2, sort_keys=True)
        f.write("\n")
    print(result["verdict"], result["test_cases"], "tests", result["observed_process_runs"], "run receipts")

if __name__ == "__main__":
    main()
