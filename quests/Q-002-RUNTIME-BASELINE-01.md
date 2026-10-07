# Q-002 — RUNTIME-BASELINE-01

State: ACTIVE

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
