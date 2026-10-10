#!/usr/bin/env python3
"""Read-only Q-010/RTX3070 placement evidence: no runtime authority, no GPU mutation."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ANSI = re.compile(r"\x1b\[[0-9;]*m")
LAYER = re.compile(r"Layers (\d+)-(\d+):\s+(cuda\[\d+\]|cpu)")
RESIDENCY = re.compile(
    r"native expert residency mixed-device admission cpu_layers=(\d+) gpu_layers=(\d+) "
    r"excluded_cpu_profile_entries=(\d+)")
AUTOMAP = re.compile(
    r"Using automatic device mapping parameters: text\[max_seq_len:\s*(\d+), max_batch_size:\s*(\d+)\]")
TRIAL_ORDER = ("control", "pressure", "pressure", "control", "control", "pressure")


class EvidenceError(ValueError):
    pass


def demand(ok: bool, why: str) -> None:
    if not ok:
        raise EvidenceError(why)


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as inp:
        for block in iter(lambda: inp.read(4 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def parse_mapping(raw: str) -> dict:
    log = ANSI.sub("", raw)
    sections = [(int(a), int(b), dev) for a, b, dev in LAYER.findall(log)]
    demand(bool(sections), "missing device map")
    cursor = 0
    gpu = cpu = 0
    for start, end, device in sections:
        demand(start == cursor and end >= start, "non-contiguous or inverted layer ranges")
        size = end - start + 1
        cpu += size if device == "cpu" else 0
        gpu += size if device.startswith("cuda[") else 0
        cursor = end + 1
    demand("Model loaded." in log, "no model loaded witness")
    witness = RESIDENCY.search(log)
    demand(witness is not None, "missing mixed-device residency witness")
    demand(int(witness.group(1)) == cpu and int(witness.group(2)) == gpu,
           "reported residency differs from mapping")
    demand(cpu > 0 and gpu > 0 and cursor == cpu + gpu, "invalid layer count")
    params = AUTOMAP.search(log)
    demand(params is not None, "auto map parameters missing")
    demand("disabling PagedAttention" in log, "mixed-device PagedAttention status absent")
    return {
        "segments": [{"first": a, "last": b, "device": d} for a, b, d in sections],
        "gpu_layers": gpu,
        "cpu_layers": cpu,
        "total_layers": cursor,
        "excluded_cpu_profile_entries": int(witness.group(3)),
        "placement_estimate_max_seq_len": int(params.group(1)),
        "placement_estimate_max_batch_size": int(params.group(2)),
        "paged_attention": "DISABLED_MIXED_CPU_GPU",
    }


def verify_receipt(receipt: dict, *, mode: str, repetition: int) -> dict:
    demand(receipt.get("status") == "PASS_SAMPLES", "non-PASS server run")
    demand(receipt.get("engine") == "candidate", "wrong engine")
    demand(receipt.get("repeat") == repetition, "wrong repetition index")
    demand(receipt.get("server_reaped") is True, "model server not reaped")
    demand(receipt.get("ctx_requested") == 1024, "context changed")
    demand(abs(receipt.get("reclaim_delta_mib", 999999)) <= 128, "GPU reclaim threshold violated")
    demand(set(receipt.get("samples", {})) == {"128", "512"}, "missing inference sample")
    gpu = receipt["before"]["gpu"]
    demand(gpu["free_mib"] >= 1536, "insufficient GPU at admission")
    demand(receipt["before"]["ram_available_mib"] >= 16384, "insufficient host RAM at admission")
    demand(receipt["telemetry"].get("samples", 0) >= 5, "missing resource samples")
    demand(receipt["telemetry"]["peak_total_gpu_used_mib"] > 0, "missing GPU peak")
    for limit in ("128", "512"):
        x = receipt["samples"][limit]
        demand(0 < x["tokens"] < int(limit), "generation hit cap or returned zero")
        demand(x["tps_engine"] > 0, "nonpositive throughput")
    return {
        "pre_server_gpu_used_mib": gpu["used_mib"],
        "pre_server_gpu_free_mib": gpu["free_mib"],
        "pre_server_host_ram_available_mib": receipt["before"]["ram_available_mib"],
        "peak_total_gpu_mib": receipt["telemetry"]["peak_total_gpu_used_mib"],
        "peak_owned_rss_mib": receipt["telemetry"]["peak_owned_process_tree_rss_mib"],
        "reclaim_delta_mib": receipt["reclaim_delta_mib"],
        "decode_tps_short": receipt["samples"]["128"]["tps_engine"],
        "decode_tps_checklist": receipt["samples"]["512"]["tps_engine"],
        "generated_tokens_short": receipt["samples"]["128"]["tokens"],
        "generated_tokens_checklist": receipt["samples"]["512"]["tokens"],
        "hot_stream_first_text_ms": receipt["samples"]["128"]["separate_request_stream"].get("first_text_ms"),
        "requested_context_tokens": receipt["ctx_requested"],
        "mode": mode,
    }


def verify_pressure(s: Path, mode: str, repetition: int, item: dict, parent_index: int,
                    parent: dict, controller_text: str, requested_mib: int) -> dict | None:
    if mode != "pressure":
        demand(parent.get("holder_alive_at_end") is None, "unexpected pressure witness in control")
        return None
    demand(parent.get("holder_alive_at_end") is True, "CUDA reservation exited before inference")
    log = (s / "pressure" / f"{repetition:02d}-pressure.log").read_text()
    demand("RESERVATION_READY" in log and f"requested_mib {requested_mib}" in log,
           "CUDA reservation handshake missing")
    pattern = rf"TRIAL_BEGIN {parent_index} 6 pressure {repetition} GPU (\d+)"
    match = re.search(pattern, controller_text)
    demand(match is not None, "no controller-before-reservation witness")
    initial_used = int(match.group(1))
    rise = item["pre_server_gpu_used_mib"] - initial_used
    demand(rise >= requested_mib - 128, "pressure reservation size not observed on GPU")
    demand(item["pre_server_gpu_free_mib"] >= 3200, "pressure left insufficient GPU headroom")
    return {
        "holder_alive_at_model_stop": True,
        "gpu_before_reservation_mib": initial_used,
        "gpu_before_model_mib": item["pre_server_gpu_used_mib"],
        "observed_gpu_delta_mib": rise,
        "requested_reservation_mib": requested_mib,
    }


def collect(session: Path, *, check_model: Path | None = None, check_binary: Path | None = None) -> dict:
    p = json.loads((session / "protocol.json").read_text())
    summary = json.loads((session / "summary.json").read_text())
    earlier = json.loads((session / "audit.json").read_text())
    demand(p["run_order"] == list(TRIAL_ORDER), "trial order not frozen")
    demand(p["pressure_requested_mib"] == 2048, "unexpected GPU pressure specification")
    demand(summary["status"] == "SIX_TRIALS_COMPLETE_UNAUDITED", "benchmark not completed")
    demand(summary["completed_trials"] == 6, "not six engine launches")
    demand(earlier["status"] == "SIX_TRIALS_PASS_RESOURCE_AWARE_STARTUP_PLACEMENT",
           "underlying independent audit does not PASS")
    if check_model is not None:
        demand(digest(check_model) == p["model_sha256"], "source model has changed")
    if check_binary is not None:
        demand(digest(check_binary) == p["candidate_sha256"], "candidate binary has changed")
    controller_text = (session / "controller.log").read_text()
    observed = []
    tracked_paths = ["protocol.json", "summary.json", "audit.json", "controller.log"]
    for index, mode in enumerate(TRIAL_ORDER, start=1):
        repetition = sum(v["mode"] == mode for v in observed) + 1
        parent_file = session / f"trial-{index:02d}-{mode}.json"
        parent = json.loads(parent_file.read_text())
        demand(parent.get("status") == "PASS_SAMPLES", "parent trial is not PASS")
        demand(parent.get("mode") == mode and parent.get("repeat") == repetition, "parent trial wrong identity")
        directory = session / mode
        basename = f"{repetition:02d}-candidate"
        receipt_file = directory / f"{basename}.json"
        receipt = json.loads(receipt_file.read_text())
        obs = verify_receipt(receipt, mode=mode, repetition=repetition)
        obs["placement"] = parse_mapping((directory / f"{basename}.server.log").read_text(errors="replace"))
        demand(obs["placement"]["total_layers"] == 48, "model topology not 48 layers")
        obs["cuda_reservation"] = verify_pressure(
            session, mode, repetition, obs, index, parent, controller_text,
            p["pressure_requested_mib"])
        for limit in ("128", "512"):
            file = directory / f"{basename}-{limit}-response.txt"
            demand(digest(file) == receipt["samples"][limit]["output_sha256"], "response checksum failed")
            content = file.read_text()
            demand(content.startswith("<think>") and content.rstrip().endswith("."),
                   "response did not finish")
            if limit == "512":
                demand(re.findall(r"(?m)^\s*(\d+)\.\s+", content) == list("123456"),
                       "incomplete six-item checklist")
            tracked_paths.append(str(file.relative_to(session)))
        tracked_paths += [
            str(parent_file.relative_to(session)),
            str(receipt_file.relative_to(session)),
            str((directory / f"{basename}.server.log").relative_to(session)),
        ]
        if mode == "pressure":
            tracked_paths.append(str((directory / f"{repetition:02d}-pressure.log").relative_to(session)))
        obs["mode"] = mode
        obs["repetition"] = repetition
        observed.append(obs)
    ctrl = [x for x in observed if x["mode"] == "control"]
    pres = [x for x in observed if x["mode"] == "pressure"]
    gpu_control = [v["placement"]["gpu_layers"] for v in ctrl]
    gpu_pressure = [v["placement"]["gpu_layers"] for v in pres]
    demand(max(gpu_pressure) < min(gpu_control), "no resource-sensitive placement separation")
    import statistics
    med = lambda vals: statistics.median(vals)
    decode = {mode: med([r["decode_tps_checklist"] for r in runs])
              for mode, runs in (("control", ctrl), ("pressure", pres))}
    demand(all(v > 0 for v in decode.values()), "invalid medians")
    demand(abs(decode["control"] - summary["median_tps_512"]["control"]) < 0.001,
           "control median disagrees with original")
    demand(abs(decode["pressure"] - summary["median_tps_512"]["pressure"]) < 0.001,
           "pressure median disagrees with original")
    baseline_gpu = summary["ambient_start"]["used_mib"]
    post_gpu = summary["ambient_end"]["used_mib"]
    demand(abs(post_gpu - baseline_gpu) <= 160, "ambient GPU after session not recovered")
    return {
        "schema": "gnostral.placement-observation.v1",
        "classification": "EVIDENCE_PASS_RESOURCE_AWARE_STARTUP_ONLY",
        "provenance": {
            "session": str(session),
            "model_sha256": p["model_sha256"],
            "binary_sha256": p["candidate_sha256"],
            "underlying_audit_sha256": digest(session / "audit.json"),
        },
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "topology": {"layer_count": 48,
                     "gpu_layers_control": gpu_control, "gpu_layers_under_pressure": gpu_pressure},
        "resource_condition": {"reservation_mib": p["pressure_requested_mib"],
                               "ambient_gpu_used_begin_mib": baseline_gpu,
                               "ambient_gpu_used_end_mib": post_gpu},
        "decode_tps_median": decode,
        "repetitions": observed,
        "trace_sha256": {name: digest(session / name) for name in sorted(set(tracked_paths))},
        "qualified_capabilities": ["resource_aware_initial_placement",
                                   "synthetic_vram_pressure_coexistence",
                                   "release_of_owned_experimental_processes"],
        "not_qualified": ["hot_rebalancing", "KV_PagedAttention_mixed_cpu_gpu",
                          "genuine_GPU_compute_contention", "multi_model_orchestration",
                          "semantic_quality_generalization", "runtime_admission_policy_authority"],
        "evidence_type": "OFFLINE_POST_RUN_OBSERVATION_NOT_RUNTIME_CONTROL",
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--session", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--model", type=Path, default=None, help="Optional fresh SHA256 verification")
    ap.add_argument("--binary", type=Path, default=None, help="Optional fresh SHA256 verification")
    args = ap.parse_args()
    result = collect(args.session, check_model=args.model, check_binary=args.binary)
    if args.output.exists():
        raise SystemExit("refusing overwrite: " + str(args.output))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["classification"], "runs", len(result["repetitions"]),
          "gpu_control", result["topology"]["gpu_layers_control"],
          "gpu_pressure", result["topology"]["gpu_layers_under_pressure"],
          "artifacts", len(result["trace_sha256"]))
    print("EVIDENCE_PATH", args.output)


if __name__ == "__main__":
    main()
