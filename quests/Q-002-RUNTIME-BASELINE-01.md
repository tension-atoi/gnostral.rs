# Q-002 — RUNTIME-BASELINE-01

State: CLOSED — QUALIFIED_WITH_LIMITS

## Question

What is the reproducible runtime baseline of the current local
mistral.rs + Ternary Bonsai 2 27B PTQ1 stack on the reference RTX 3070
desktop, beyond a single throughput number?

This quest freezes lifecycle, concurrency, memory, reclaim, and failure
measurements before any challenger engine enters the comparison.

## Frozen target

- engine: current locally qualified mistral.rs + Candle Bonsai path;
- model: Ternary Bonsai 2 27B PTQ1;
- GPU topology: 64/64 CUDA layers where the qualified runtime permits it;
- paged attention: off;
- prefix cache: disabled for baseline unless a subtest explicitly says otherwise;
- recurrent pool slots: 2;
- live graphical desktop retained.

## Required measurements

1. GPU/host preflight and exact binary/model identities.
2. Cold process start → HTTP readiness.
3. Warm request TTFT and TPOT.
4. C1, C4, and C8 request concurrency.
5. VRAM and RSS at ready, request peak, and steady warm state.
6. Context-growth probes through the declared max model length.
7. Graceful stop → physical VRAM reclaim latency.
8. Restart after graceful stop.
9. Controlled server failure/restart behavior without driver fault.
10. NVIDIA Xid/MMU scan and bounded desktop-health proxy.

## Hard guardrails

- unexpected compute client => run is contaminated, not silently accepted;
- any NVIDIA Xid/MMU fault => stability gate FAIL;
- OOM is retained as evidence, never rewritten as a lower-performance success;
- sampled nvidia-smi values are telemetry, not allocator truth;
- concurrency success requires valid semantic responses, not HTTP 200 alone;
- no runtime/kernel tuning is allowed inside the qualification run.

## Exit gate

Q-002 closes only when one machine-readable qualification packet records:

- frozen identities and commands;
- every subtest result;
- raw evidence references;
- contamination/stability classification;
- qualified lifecycle numbers;
- explicit non-claims.

The packet must be sufficient for the next engine to run under the same
external contract.

## Non-goals

Q-002 does not optimize kernels, enable PagedAttention, change placement
policy, introduce multi-model orchestration, or prove production readiness.
It establishes the control arm for later runtime comparisons.

## Runtime profiles

### CONTROL

A comparable engine-control lane.

- graphical session remains active;
- known desktop infrastructure may be explicitly allow-listed;
- opportunistic GPU compute clients such as browsers are not allowed;
- preflight must be CLEAN before measurement.

### DESKTOP-PRESSURE

A real-workstation lane.

- graphical session remains active;
- browser/desktop GPU clients may remain active;
- every observed compute client and baseline VRAM value is recorded;
- the run is classified by its measured ambient pressure, not called CLEAN;
- comparisons are valid only against other runs inside a compatible pressure envelope.

CONTROL provides the cross-engine reference. DESKTOP-PRESSURE tests robustness
under ordinary workstation contention. Neither lane may silently substitute for
the other.

## Protocol refinement after DESKTOP-PRESSURE-01

The first pressure run demonstrated that HTTP control-plane availability can
precede usable model state. Q-002 therefore records two readiness milestones:

- HTTP-ready: `/v1/models` responds successfully;
- semantic-ready: the frozen one-token correctness probe succeeds.

Concurrency, context, and throughput qualification begin only after
semantic-ready. This refinement tightens the gate; it does not reinterpret a
failed measurement as success.

See `research/runtime/Q002-DESKTOP-PRESSURE-01.md`.

## Closure

Closed on 2026-10-07 as **QUALIFIED_WITH_LIMITS**.

See:
- `research/runtime/Q002-CONTROL-QUALIFICATION.md`
- `evidence/q002/control-qualification.json`

The control arm is now frozen for Q-003 and later challenger comparisons.

## Post-closure review — 2026-10-09

**Disposition: CLOSED / CONTROL CONTRACT RETAINED.** Q-009 Strata and prospective WakeKV experiments must preserve exact binary/model/quantization identities, CONTROL versus DESKTOP-PRESSURE, HTTP-ready versus semantic-ready, request-level timing, concurrency and context boundaries, physical reclaim and Xid/MMU observations. The Q-002 numbers are not transferable to a different model, MoE geometry, or KV policy. This is a reusable qualification discipline, not approval of either new mechanism.
