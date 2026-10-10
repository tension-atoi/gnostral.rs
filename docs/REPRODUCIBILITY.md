# Reproducibility, trust boundaries, and safe first run

**Two different goals:** (1) inspect the open-source proofs without a GPU, or (2) reproduce a bounded inference qualification on a specific local workstation. Only the first is a conventional clone-and-run workflow.

## A. Read-only public evidence (any platform)

Start with [the capability matrix](CAPABILITY_MATRIX.md) and [QUESTLOG](../QUESTLOG.md). Machine-readable, sanitized receipts are in `evidence/runs/`. Each detailed report states its model, host, executable, workload, evidence sources and nonclaims.

```bash
git clone https://github.com/tension-atoi/gnostral.rs.git
cd gnostral.rs
git rev-parse HEAD
cat docs/CAPABILITY_MATRIX.md
cat evidence/runs/gnostral-q012-native-three-families-20261010.json
cat evidence/runs/gnostral-q013c-real-dense-single-server-20261010.json
```

Receiving a precomputed receipt is **not** an independent re-execution of the original run.

## B. Portable and CPU-only tests

```bash
# Typed provider and Q013-A admission state machine, no weights.
cargo test --locked --manifest-path harness/engine-provider-contract/Cargo.toml

# Q013-C portable negative controls and public receipt consistency:
python3 -m unittest discover -s harness/experiments -p 'test_q013c*.py' -v

# Q013-B evidence-auditor parsers: use sanitized portable fixtures
# in a clean checkout; no process-isolation run is claimed.
GNOSTRAL_Q013B_TEST_EVIDENCE_DIR=/path/that/does/not/exist \
python3 -m unittest discover -s harness/experiments -p 'test_q013b*.py' -v

# Public artifact safety and tracked-file checks:
bash scripts/check-public.sh
git diff --check
```

**Offline caveat:** `--offline` can be added to Cargo only after the necessary crates are in the local cache. Downloading dependencies or running tests on your workstation is not evidence that another machine has reproduced the original GPU qualification. Some test modules legitimately skip when their intentionally unbundled vendor trees are absent.

## C. GPU experiments — only on a protected compatible local host

Preconditions: Linux with systemd cgroups v2, a working graphical session protected from resource pressure, the explicitly pinned local engine binary and model weights, and a user-controlled `gnu6-lab-run` deployment. The experimental launcher is **not distributed as an installed system service** by this repo. Do not download or run hidden binaries based only on a README.

```bash
export PATH="$HOME/.local/bin:$PATH"
gnu6-lab-run --check

# If local model/runtime paths differ, the two SHA-256 identities still
# have to match the pinned Q013-C values or the run fails closed.
# export GNOSTRAL_Q013C_ENGINE=/your/local/path/to/mistralrs
# export GNOSTRAL_Q013C_DENSE_MODEL=/your/local/path/to/model-snapshot

# WARNING: starts one real CUDA dense server, under exclusive bounded scope.
# Run ONLY with adequate fresh RAM/VRAM headroom.
gnu6-lab-run --exclusive -- python3 harness/experiments/q013c_real_dense.py \
    /new/private/evidence/session-unique-01

# Independent second pass: rehash exact engine and model, check semantic
# output, memory return and immutable-by-policy retained session.
gnu6-lab-run --exclusive -- python3 harness/experiments/q013c_independent_audit.py \
    --session /new/private/evidence/session-unique-01 \
    --output /new/private/evidence/session-unique-01/independent-audit.json
```

Do **not** weaken executable/model SHA checks to make a different host pass. Instead freeze a new baseline and establish a separate qualification.

## D. What can make a run FAIL?

- Cgroup limits absent or modified, no safe memory reserve or graphical session down.
- Unexpected existing GPU/engine activity, occupied port or unknown bound process.
- Binary/model SHA mismatch, unsupported model, missing required Cargo features.
- HTTP control endpoint responds but semantic oracle fails or times out.
- Model exception, CUDA Xid, stale driver/VRAM telemetry or incomplete process cleanup.
- Persistent GPU ambient memory above the frozen reclaim tolerance.
- Source status looks PASS but the independent audit says NOT_QUALIFIED.

A controlled failure is a **successful safety test**, but not an inference performance PASS. Preserve original raw receipts, do not edit away negative runs.

## E. What the evidence does **not** guarantee

- Reproducibility on arbitrary GPUs, drivers, operating systems, compiler versions or weights.
- Per-process VRAM isolation from systemd memory cgroups.
- Independent cryptographic authentication of the localhost model listener.
- Safe multitenant operation, high availability, concurrent model hosting or automatic hot-swap.
- Any new upstream feature (Burn/Ferrum/CubeCL/WakeKV) has been integrated.

For a contribution, attach pinned source commit, model digest, exact command/env, host/driver stats, independent oracle result, negative gates, and a statement of known limitations. Follow [CONTRIBUTING](../CONTRIBUTING.md) and [vendor provenance](../THIRD_PARTY.md).
