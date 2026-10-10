# Q-013B — isolated local process adapter (fixture qualification)

**Verdict: `Q013B_FIXTURE_PROCESS_CONTAINMENT_PASS` — no real inference adapter qualification.**

## Intent and scope

Q013-B implements the first *operational*, Linux-local subprocess boundary
under the existing [EngineProvider v0](../contracts/ENGINE_PROVIDER_V0.md) and
[Q-013-A evidence contract](Q-013-EVIDENCE-BOUND-ADMISSION.md).

The candidate deliberately executes **only one pinned, disposable Rust fixture**.
It is not allowed to launch arbitrary external programs, user prompts, model
weights, CUDA inference or tools. Q013-A probe plans are used as the three
operation-specific test shapes; the fixture is not the Q-012 inference engine.

## Implemented mechanism

- `harness/q013b-local-adapter`: native Rust subprocess harness. It checks
  the *actual* cgroups v2 path and kernel controls before spawning:
  `gnu6-lab.slice`, own `memory.max` ≤21 GiB, own `memory.swap.max` ≤2 GiB,
  own `memory.oom.group=1`, parent high ≤18 GiB / max ≤22 GiB / swap ≤2 GiB.
  It checks Linux `MemAvailable` and `SwapFree` ≥1 GiB. This is a CPU-only
  fixture preflight; larger loads require `gnu6-lab-run --exclusive` and
  additional GPU reserve/driver checks.
- Executable allowlist: the fixed name `q013b-fixture` **and** its pinned
  SHA-256, not a hash chosen by the caller. Copy its bytes into a new private
  0700 directory, fsync, change the snapshot to 0500, verify the snapshot's
  SHA and only then spawn it.
- Fixed operation arguments; no shell, arbitrary argv, file chooser,
  network connection or model runtime. Detached process group via
  `CommandExt::process_group(0)`; timeout/cancellation kill only its
  process group. Cleanup fallback also attempts parent kill and waits.
- Input/output bounded: 30 ms–3 s window, no stdin, `RLIMIT_FSIZE` 64 KiB,
  no core dump. Captured stdout checked against an exact *fixture* predicate.
- CPU memory/swap and OOM counters sampled from the cgroup before/after;
  positive runs return within a 32 MiB envelope. This is a bounded
  **scope-level observation**, not proof of the memory footprint of each
  subprocess individually, and it is emphatically **not VRAM reclaim**.
- The `q013b-boundary` binary exits 73 outside the required protected scope.
  A separate negative control ran it outside the wrapper and confirmed denial.

## Evidence and gates — 2026-10-10

- 11/11 Rust integration tests on a live bounded systemd user scope,
  including three independent fixture probes, incorrect semantic output,
  nonzero exit 23, timeout, cancellation, nested child/group kill, forged
  fixture executable SHA, invalid budget and pre-cancel refusal.
- 6/6 independent Python log-auditor tests; tampering with group kill, OOM,
  memory return, GPU reclaim claims, binary SHA or outside-scope refusal
  is rejected.
- Dedicated isolation fixture binary:
  `60dee3e056d442ac779edb6f799f2d2926c6916e636752de4183b2bf12955c40`.
  The SHA is intentionally toolchain-specific: a different build must be
  re-pinned and re-qualified, **not silently accepted**.
- The original Q-012 public receipt SHA remains pinned:
  `48241e35df171941e5d80a8f3832a55642de43d96abad04c0a000208e1cd3164`.
- Public sanitized receipt:
  `evidence/runs/gnostral-q013b-fixture-process-20261010.json`.
  Local raw logs:
  a private, user-controlled lab evidence directory supplied via `--session`.
- Hyprland remained active; no model loading, GPU workload, resident server,
  driver reset, production service or native inference process was used.

## Local reproduction (no deployment)

From repository root on a host with the qualified `gnu6-lab-run` launcher:

```bash
gnu6-lab-run --check
gnu6-lab-run -- cargo test --offline --locked \
  --manifest-path harness/q013b-local-adapter/Cargo.toml \
  --test isolated_process -- --test-threads=1
gnu6-lab-run -- cargo clippy --offline --locked \
  --manifest-path harness/q013b-local-adapter/Cargo.toml \
  --all-targets -- -D warnings
```

The fixture binary must be built in the same pinned host/toolchain
environment or the SHA gate intentionally fails. The audit Python tests
also work on clean checkouts via synthetic test logs generated from the
public receipt; those portable parser tests **do not replace** the local
11-case process qualification.

## Q013-B remaining gate — NOT EXECUTED

Before connecting a real mistral.rs/other provider adapter:

1. Authenticate a semantic witness rather than trusting strings asserting
   independent origin; bind the real output digest to exact model and binary.
2. Implement non-fixture process identity and transport allowlisting, a
   fresh GPU reserve/driver-health preflight and restart/cancellation policy.
3. Test real semantic failures, driver faults, process crashes, reclaim and
   termination under `gnu6-lab-run --exclusive` with strict memory headroom.
4. Qualify provenance, permissions and input limits. Do not equate this
   fixture's static literal outputs with model responses.

**Q013B-FIXTURE is closed; Q013B-REAL-ENGINE is pending.**
