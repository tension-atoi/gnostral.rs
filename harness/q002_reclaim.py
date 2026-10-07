#!/usr/bin/env python3
"""Measure process exit and return toward an ambient total-VRAM envelope."""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import time
from pathlib import Path


def gpu_used_mib() -> int:
    out = subprocess.check_output(
        [
            "nvidia-smi",
            "--query-gpu=memory.used",
            "--format=csv,noheader,nounits",
        ],
        text=True,
    )
    return int(out.splitlines()[0].strip())


def alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False

    try:
        stat = Path(f"/proc/{pid}/stat").read_text()
        state = stat.split()[2]
        if state == "Z":
            return False
    except (FileNotFoundError, IndexError):
        return False

    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pid", type=int, required=True)
    parser.add_argument("--ambient-mib", type=int, required=True)
    parser.add_argument("--tolerance-mib", type=int, default=96)
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    t_signal = time.perf_counter()
    os.kill(args.pid, signal.SIGTERM)

    deadline = t_signal + args.timeout
    t_exit = None
    while time.perf_counter() < deadline:
        if not alive(args.pid):
            t_exit = time.perf_counter()
            break
        time.sleep(0.025)

    threshold = args.ambient_mib + args.tolerance_mib
    t_reclaim = None
    samples = []
    while time.perf_counter() < deadline:
        used = gpu_used_mib()
        now = time.perf_counter()
        samples.append({"elapsed_ms": (now - t_signal) * 1000, "used_mib": used})
        if used <= threshold:
            t_reclaim = now
            break
        time.sleep(0.05)

    result = {
        "pid": args.pid,
        "ambient_vram_mib": args.ambient_mib,
        "tolerance_mib": args.tolerance_mib,
        "threshold_mib": threshold,
        "sigterm_to_exit_ms": None if t_exit is None else (t_exit - t_signal) * 1000,
        "sigterm_to_ambient_ms": None if t_reclaim is None else (t_reclaim - t_signal) * 1000,
        "exit_to_ambient_ms": (
            None if t_exit is None or t_reclaim is None else (t_reclaim - t_exit) * 1000
        ),
        "samples": samples,
    }

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0 if t_exit is not None and t_reclaim is not None else 3


if __name__ == "__main__":
    raise SystemExit(main())
