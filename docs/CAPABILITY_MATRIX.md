# Capability matrix · qualified, observed, and unproven

**Snapshot: 2026-10-10 · Reference workstation: RTX 3070 8 GiB VRAM / 32 GiB RAM**

This is the **public truth table**. A `PASS` means only that the precise linked gate completed; it does **not** imply a shipped feature, portable speed, or operational readiness.

| Capability | Status | Mechanism / exact observation | Primary evidence | Not established |
| --- | --- | --- | --- | --- |
| Bonsai PTQ1 inference baseline | **QUALIFIED WITH LIMITS** | Product-control 35.2 tok/s, 28.44 ms/token, FG-02 | [Q-001](../quests/Q-001-FG03-TRUTH-01.md), [Bonsai baseline](../research/bonsai/BASELINE.md) | FG-03 40 tok/s |
| Full runtime control methodology | **QUALIFIED WITH LIMITS** | Cold/HTTP/semantic ready, memory, reclaim, concurrency and two desktop profiles | [Q-002](../quests/Q-002-RUNTIME-BASELINE-01.md) | Uninterrupted production uptime |
| Memory-residency observability ledger | **CONTRACT SUPPORTED** | Cross-mechanism sourced facts vs unsupported/unknown fields | [Q-003](../quests/Q-003-ELASTIC-LEDGER-02.md) | Engine-neutral allocator |
| EngineProvider v0 lifecycle contract | **CONTRACT TESTED** | Typed engine capability, semantic readiness, unload, reclaim | [Contract](../contracts/ENGINE_PROVIDER_V0.md), [tests](../harness/engine-provider-contract) | Dynamic multi-engine deployment |
| Strata MoE borrowed CPU weights | **BOUNDED A/B PASS** | Q2_K/Q3_K copy-free path; 9.51 → 20.18 tok/s six-check medians | [Q-010/Q-011](../research/runtime/GNOSTRAL-Q010-Q011-PUBLIC-HANDOFF-20261010.md), [receipts](../evidence/runs) | Faster than llama.cpp; all architectures |
| Adaptive MoE layer count at load | **OBSERVED** | 22/21/21 → 13/12/13 GPU layers with synthetic VRAM reservation | [Q-011](../research/runtime/GNOSTRAL-Q010-Q011-PUBLIC-HANDOFF-20261010.md) | Migration while live; competing compute fairness |
| Native dense Qwen2.5-Coder 1.5B | **FUNCTIONAL PASS** | Same SHA-pinned Rust/CUDA Q012 engine | [Q-012](../research/runtime/GNOSTRAL-Q012-NATIVE-CAPABILITIES-20261010.md), [receipt](../evidence/runs/gnostral-q012-native-three-families-20261010.json) | Quality at production traffic |
| Native Qwen3-Embedding 0.6B | **FUNCTIONAL PASS** | 3 × 1024 vectors, finite norms and expected cosine ordering | [Q-012 receipt](../evidence/runs/gnostral-q012-native-three-families-20261010.json) | Broad retrieval benchmarks |
| Native quantized Qwen3 MoE 30B-A3B | **FUNCTIONAL PASS** | Q2_K GGUF mixed CPU/GPU after correcting missing Cargo residency feature | [Q-012 report](../research/runtime/GNOSTRAL-Q012-NATIVE-CAPABILITIES-20261010.md) | Concurrent resident models |
| SHA-pinned evidence-bound admission | **CONTRACT-ONLY PASS** | Three exact probe plans, all `execution_authorized=false` | [Q013-A](../quests/Q-013-EVIDENCE-BOUND-ADMISSION.md), [plans](../evidence/runs/gnostral-q013-exact-probe-plans-20261010.json) | Permission to spawn arbitrary programs |
| Bounded subprocess lifecycle | **CPU FIXTURE PASS** | Pinned executable, cgroup v2, timeout/cancel, group kill, CPU reclaim | [Q013-B](../quests/Q-013B-ISOLATED-FIXTURE.md), [receipt](../evidence/runs/gnostral-q013b-fixture-process-20261010.json) | VRAM isolation, adversarial process security |
| Real dense inference supervisor pilot | **SINGLE-SERVER PASS** | One bounded local Qwen2.5 server, exact `GNOSTRAL` oracle, independently audited rehash and GPU ambient return | [Q013-C](../quests/Q-013C-REAL-DENSE-PILOT.md), [receipt](../evidence/runs/gnostral-q013c-real-dense-single-server-20261010.json) | Generic server, authenticated public API |
| Modeld resource-envelope intents | **DESIGN BOUNDARY** | Supervisor may express envelopes and consume facts; kernel/KV/expert policy remains inside engine | [Q-008](../quests/Q-008-MODELD-PROMOTION-GATE.md) | Generic materialization authority |
| Real multi-model hot swap | **NOT QUALIFIED** | A→B→A lifetime not demonstrated under one supervisor | [Next gates](ROADMAP.md) | Zero-downtime switching, co-residency |
| Always-on multitenant service / authentication | **NOT IMPLEMENTED / NOT QUALIFIED** | No ratified deployment/control plane | [Roadmap](ROADMAP.md) | Public API, SLA |
| Burn Remote v5 quantized transfers | **UPSTREAM CONFIRMED, LOCAL NOT TESTED** | Q8/Q4/FP8/FP4 and protocol v5 candidate | [Watch](../research/runtime/RUST-INFERENCE-WATCH-20261010.md) | Q012 model transport or engine integration |
| Ferrum SLO scheduler | **UPSTREAM EXPERIMENT, LOCAL NOT TESTED** | Optional TTFT/TPOT/ITL-aware policy | [Watch](../research/runtime/RUST-INFERENCE-WATCH-20261010.md) | Throughput improvement or SLO guarantee |
| WakeKV reversible KV | **PAPER LEAD / NO LOCAL RUN** | Cooling-head CPU reservoir and potential wake-back | [Paper intake](../research/runtime/WAKEKV-LEAD-20261009.md) | Q012 attention compatibility, local performance |
| CubeCL NCCL/transfer stream ordering | **UPSTREAM CONFIRMED; MULTI-GPU NOT TESTED** | Separate communication resources and collective order | [Watch](../research/runtime/RUST-INFERENCE-WATCH-20261010.md) | Multi-GPU result on one RTX 3070 |

## Operational interpretation

**Three distinct layers must not be merged in product language:**

1. **Mechanism:** upstream source or experimental patch exists.
2. **Qualification:** a narrowly scoped experiment passed, with evidence and negative gates.
3. **Delivery:** reproducible, packaged, supported software usable outside the lab.

`gnostral.rs` currently includes parts of (1) and (2). It does not yet fulfill (3) for a general multi-model serving system.

## Audit navigation

- **What failed?** The original Q010 reclaim run failed (+196 MiB vs ±128 MiB gate); the first Q012 three-family run omitted a compile-time residency feature, and MoE timed out. Both remained recorded.
- **What was repaired?** A fresh Q010 run satisfied the same reclaim threshold; Q012 recompiled with explicit `gnostral-expert-residency` and all three families passed independently.
- **How is the desktop protected?** The external local `gnu6-lab-run` wrapper places cooperating tasks inside a memory/swap-limited systemd slice. This is **not** itself a portable GNOSTRAL feature or a GPU VRAM cap.

Read [the methodology](EVIDENCE_MODEL.md) before reusing a result in a public claim, portfolio, pitch or API documentation.
