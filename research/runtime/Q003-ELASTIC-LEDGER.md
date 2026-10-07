# Q-003 — Elastic Residency Ledger

**State:** CLOSED — OBSERVABILITY_CONTRACT_SUPPORTED
**Date:** 2026-10-07

Q-003 asked a narrower question than “which engine is fastest?”:

> Which residency facts can be observed consistently across a dense runtime,
> an oversubscribed MoE runtime, and raw CUDA virtual-memory primitives without
> pretending their mechanisms are interchangeable?

The answer is **yes for observability, no for generic materialization**.

## DENSE_RESIDENT — mistral.rs / LFM2.5

Pinned engine:
`24dbf5c256f232176ee5949485ba264049407fbe`

Binary SHA-256:
`d6e107722cf026c40991fd748e7e5f67550e0b2193106ecb4da3bff606c55667`

Model:
LFM2.5-2.6B Q4_K_M GGUF
SHA-256:
`02a8b7e17487d326e46d68ce0ba24211e1b80a14c4cd0597fa73c1cd697f52ed`

The semantic probe was reproduced in independent fresh processes. In the
qualified CONTROL run:
- HTTP-ready: **21.70 s**;
- semantic request: **PASS**, 878 ms wall;
- native decode: **168.20 tok/s** for this small bounded request;
- ambient total VRAM: **1173 MiB**;
- peak total VRAM: **3153 MiB**;
- process RSS at ready: **3337 MiB**;
- return to ambient VRAM after SIGTERM: **191.8 ms**;
- Xid/MMU fault: **none observed**.

The model file had just been hashed, so host-page-cache state is deliberately
classified as **uncontrolled / likely warm**. The 21.70 s start must not be
reported as storage-cold load time.
## MOE_OVERSUBSCRIBED — Pulsar / Qwen3-30B-A3B Q2_K

Pinned Pulsar revision:
`18f990094e1091ee2ef3078f20be418f8c162f03`

Binary SHA-256:
`e68ebbb2c44f83d0d9c96634de4e34ca32acb7845fb7ada01e9e50aeb519230e`

Model SHA-256:
`db3ce897ccc9e7d9dbf17fe083cae7880a2092aa473b45eba8b77715aa9ca170`

The Q2_K artifact is approximately 11 GiB, larger than the RTX 3070's 8 GiB
VRAM. Two fresh-process / host-warm runs both generated the expected Paris
completion.

Run 1:
- load: **6.9 s**;
- decode: **43.79 tok/s**;
- VRAM-cache hit rate: **94%**;
- host-cache: **100% of the remainder**;
- disk fallback: **0.0 s**;
- peak total VRAM: **7171 MiB**;
- process exit → ambient VRAM: **15.1 ms**.

Run 2:
- load: **5.6 s**;
- decode: **39.42 tok/s**;
- VRAM-cache hit rate: **94%**;
- host-cache: **100% of the remainder**;
- disk fallback: **0.0 s**;
- peak total VRAM: **7143 MiB**;
- process exit → ambient VRAM: **13.5 ms**.

No NVIDIA Xid/MMU fault was observed.

This proves bounded >VRAM execution with warm host + VRAM residency. It does
not prove storage-cold performance or generic MoE behavior. The previously
unsafe IQ2_XXS configuration was explicitly excluded.
## VMM_PRIMITIVE — CUDA virtual memory

The local cudarc 0.18.2 probe was rebuilt and run under the same CONTROL
desktop profile.

Whole-allocation control:
- mapped allocation: **256 MiB**;
- CUDA allocation granularity: **2 MiB**;
- iterations: **5**;
- median map+access: **65 µs**;
- median unmap: **85 µs**;
- median release: **92 µs**;
- stable virtual address across remaps: **PASS**;
- data round-trip after each remap: **PASS**.

Pagewise control:
- allocation: **512 MiB**;
- pages: **256 × 2 MiB**;
- iterations: **3**;
- median map: **26.67 µs/page**;
- median unmap: **12.74 µs/page**;
- median release: **8.64 µs/page**;
- stable virtual address: **PASS**;
- data round-trip: **PASS**.

No Xid/MMU fault was observed.

These timings describe a synthetic primitive. They do not establish a
production allocator or a model-level residency policy.
## What is actually comparable

Across all three tracks, gnostral.rs can require:

- exact engine/binary/model identity;
- CONTROL vs DESKTOP-PRESSURE profile;
- ambient physical VRAM;
- peak physical VRAM;
- explicit warmth/residency state;
- reclaim or release observation;
- Xid/MMU-fault observation;
- bounded semantic readiness where an inference engine exists.

The following are **not** valid cross-track comparisons:

- tok/s between dense, MoE and VMM workloads;
- expert-cache state versus dense model residency;
- CUDA VA mapping versus semantic model state;
- engine-specific cache representations.

## Architectural result

Q-003 supports a future **observability contract** more strongly than a
generic residency command surface.

A supervisor may reasonably require engines to report facts such as residency,
warmth, physical usage, reclaim completion and health. Q-003 does **not**
justify telling different engines *how* to materialize those states.

Therefore:

```text
common observability contract     SUPPORTED
generic materialization contract  NOT PROVEN
new modeld residency authority    NOT AUTHORIZED
```

Machine-readable ledger:
`evidence/q003/residency-ledger.json`.
