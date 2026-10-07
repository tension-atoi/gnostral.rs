#!/usr/bin/env python3
"""Semantic-readiness and bounded concurrency probe for Q-002."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

CASES = [
    ("2plus3", "2+3=", "5"),
    ("7minus4", "7-4=", "3"),
    ("6minus2", "6-2=", "4"),
    ("3times2", "3*2=", "6"),
]


def request_one(base_url: str, case: tuple[str, str, str], timeout: float) -> dict:
    name, prompt, expected = case
    body = json.dumps({
        "model": "default",
        "prompt": prompt,
        "max_tokens": 1,
        "temperature": 0,
    }).encode()
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/v1/completions",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read()
            status = response.status
        payload = json.loads(raw)
        text = payload.get("choices", [{}])[0].get("text", "").strip()
        return {
            "name": name,
            "status": status,
            "text": text,
            "expected": expected,
            "pass": status == 200 and text == expected,
            "latency_ms": (time.perf_counter() - t0) * 1000,
        }
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        return {
            "name": name,
            "status": exc.code,
            "text": "",
            "expected": expected,
            "pass": False,
            "latency_ms": (time.perf_counter() - t0) * 1000,
            "error": raw[:1000],
        }
    except Exception as exc:
        return {
            "name": name,
            "status": 0,
            "text": "",
            "expected": expected,
            "pass": False,
            "latency_ms": (time.perf_counter() - t0) * 1000,
            "error": repr(exc),
        }


def concurrent_lane(base_url: str, n: int, timeout: float) -> dict:
    barrier = threading.Barrier(n)
    selected = [CASES[i % len(CASES)] for i in range(n)]

    def gated(case: tuple[str, str, str]) -> dict:
        barrier.wait()
        return request_one(base_url, case, timeout)

    t0 = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=n) as pool:
        results = list(pool.map(gated, selected))
    return {
        "concurrency": n,
        "wall_ms": (time.perf_counter() - t0) * 1000,
        "pass": all(item["pass"] for item in results),
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:12549")
    parser.add_argument("--output", required=True)
    parser.add_argument("--timeout", type=float, default=180.0)
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    semantic = [request_one(args.base_url, case, args.timeout) for case in CASES]
    semantic_ready = all(item["pass"] for item in semantic)
    result = {
        "semantic_ready": semantic_ready,
        "semantic_probe": semantic,
        "concurrency_valid": semantic_ready,
        "concurrency": {},
    }

    if semantic_ready:
        for n in (1, 4, 8):
            result["concurrency"][f"C{n}"] = concurrent_lane(
                args.base_url, n, args.timeout
            )
    else:
        result["concurrency_skip_reason"] = (
            "semantic readiness failed; concurrency would not be causal"
        )

    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0 if semantic_ready else 2


if __name__ == "__main__":
    raise SystemExit(main())
