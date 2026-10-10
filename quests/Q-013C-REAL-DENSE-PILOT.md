# Q-013C — real-engine dense pilot on the reference desktop

**Verdict: `Q013C_REAL_DENSE_SINGLE_SERVER_PASS` — bounded real CUDA dense pilot only.**

This work extends [Q013-A](Q-013-EVIDENCE-BOUND-ADMISSION.md)
and [Q013-B](Q-013B-ISOLATED-FIXTURE.md). It does not replace either
qualification. The real engine is not yet integrated into the Rust Q013B
adapter; this is a separate, narrow Python experimental supervisor.

## Exact run (2026-10-10, RTX 3070 8 GB)

- Dense model: **Qwen2.5-Coder-1.5B-Instruct**.
- Engine executable (same as Q012, checked SHA-256 before copying):
  `64eec222ccefff4cd4c0067bd83348f1d22eebda27d0d857e352ee090cf19723`
- Dense model weights (rehash in preflight and by independent auditor):
  `c1b9b30e907950516ba3c646bdf570d8084c25a6410a0cdca80cf04b11bc13a8`
- Frozen source public Q012 qualification receipt:
  `48241e35df171941e5d80a8f3832a55642de43d96abad04c0a000208e1cd3164`
- GPU used before/after: **681 → 689 MiB** (+8 MiB); server reaped.
- End-to-end (including preflight weight hash + binary snapshot + startup +
  HTTP completion + stop): **16.829 s**.
- Semantic output: **`GNOSTRAL`**, 4 completion tokens.
- Server bound to **127.0.0.1:18949**. The port was unoccupied before launch
  and unbound after cleanup. No external inference API used.
- `gnu6-lab-run --exclusive` enforced shared cgroup high 18 GiB/max 22 GiB/
  swap 2 GiB, with child max 21 GiB, OOM-group kill and a heavy-job lock.
  Preflight required ≥18,000 MiB host MemAvailable and ≥5,200 MiB available
  NVIDIA VRAM, a live Hyprland graphical unit and no existing mistralrs process.
- Hyprland remained **active** after both supervisor and independent auditor.
  No leftover engine process was detected in postflight checks.

## Mechanism and evidence

1. `harness/experiments/q013c_real_dense.py` uses **hard-coded SHA identities**
   for the engine and model weights, a fixed dense model family, local port and
   bounded API request. Paths may be relocated using `GNOSTRAL_Q013C_ENGINE`
   and `GNOSTRAL_Q013C_DENSE_MODEL`; their bytes must still match the exact
   pinned SHA values. No arbitrary executable identity, URL or model CLI.
2. Real operating-system checks preflight the `gnu6-lab.slice` parent and child
   cgroup values and the live GPU/host headroom; unwrapped execution is denied.
   Engine copied into a new mode 0700 private directory, fsynced, chmod 0500,
   SHA checked again, then started as an owned process session.
3. Fresh `/v1/models` readiness precedes the bounded
   `/v1/chat/completions` request. Raw HTTP response and engine logs remain
   in a private, owner-only session folder; output is not claimed to be
   intrinsically trustworthy just because the server returned 200.
4. The supervisor terminates its owned process group, waits, removes the
   snapshot and records GPU memory after shutdown. It never installs a
   persistent systemd service.
5. `harness/experiments/q013c_independent_audit.py` independently rehashes
   the engine and weights, verifies the public Q012 receipt, validates session
   provenance and sequence, checks response file SHA and **requires the exact
   semantic content `GNOSTRAL`**, then verifies return to baseline GPU card
   memory within ±128 MiB. It produced
   `Q013C_REAL_DENSE_SINGLE_SERVER_PASS`.
6. 11/11 portable auditor tests pass: wrong word, altered response, wrong
   engine/model digest, missing stop, missing scope, reclaim failure, wrong
   lifecycle, invalid token budget and false preflight status are rejected.
   These synthetic tests do *not* themselves prove a real model ran.

The public machine-readable receipt is
`evidence/runs/gnostral-q013c-real-dense-single-server-20261010.json`.
It contains the SHA-256 digest of the independently retained private audit.
Full private session retained in the lab evidence store; never commit raw
engine log, live process IDs, host-local paths or private responses.

## Qualification boundary

**PASS:** One local Rust/CUDA dense model, single process, bounded localhost
endpoint, explicit cleanup, exact-model independent output oracle and a
GPU-card ambient recovery observation.

**NOT PROMOTED:** Production inference hosting; signed external auditor,
cryptographically authenticated semantic witness, persistent service,
concurrent sessions, hot swap, MoE/embedding adapter integration, automatic
multi-family routing, race-proof model-file immutability, GPU VRAM isolation,
full host failure/reboot recovery, driver-fault handling or a Linux security
boundary against other processes owned by the same user.

In particular, the 8 MiB GPU-card delta is an *ambient* observation, not
a direct per-process CUDA allocation trace or proof of long-term stability.

## Reproduction contract

From a checkout with the same Q012 **local** model and executable:

```bash
export PATH="$HOME/.local/bin:$PATH"
gnu6-lab-run --check
# Optional for non-default local paths, with mandatory SHA verification:
# export GNOSTRAL_Q013C_ENGINE=/local/path/to/mistralrs
# export GNOSTRAL_Q013C_DENSE_MODEL=/local/path/to/qwen25coder-snapshot
# Read and run the exact pinned pilot; creates a NEW private evidence folder.
gnu6-lab-run --exclusive -- python3 harness/experiments/q013c_real_dense.py \
    /path/to/new/private/q013c-run
# Separately rehash weights/binary and independently verify exact oracle.
gnu6-lab-run --exclusive -- python3 harness/experiments/q013c_independent_audit.py \
    --session /path/to/new/private/q013c-run \
    --output /path/to/new/private/q013c-run/independent-audit.json
# Lightweight portable negative controls (no models).
gnu6-lab-run -- python3 -m unittest discover -s harness/experiments -p 'test_q013c*.py'
```

The script **fails closed** when weights/binary/path or available headroom
differ. This is not a generic model adapter; future versions must externalize
these identities under a separately signed/validated protocol.

## Forward gate: Q-013D (pending)

A production-grade real-model adapter needs authenticated process identity
of the bound localhost listener, a real external semantic oracle, fresh
VRAM/driver-health checks during execution, robust kernel/driver failure
handling, and a controlled integration into the Rust EngineProvider runtime
state machine. Generalization to embeddings and MoE requires separate runs
and resource budgets; their Q012 historical PASS does not certify Q013-C.
