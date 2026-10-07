# Q-008 — modeld Promotion Gate

**State:** CLOSED — OBSERVABILITY_PROMOTED / MATERIALIZATION_REJECTED
**Date:** 2026-10-07

Q-008 evaluated which authority boundaries from Q-002 through Q-007 are
justified strongly enough to enter an implementation program.

The answer is deliberately split by surface.

## 1. Generic materialization authority — REJECT_GENERIC_AUTHORITY

gnostral.rs does **not** promote a generic supervisor API for layer placement,
expert movement, KV block mutation, virtual-page mapping, or token-batch
construction.

The evidence is heterogeneous:

- mistral.rs/Bonsai exposes a full-GPU path with tight context/concurrency
  limits under 8 GiB;
- Pulsar uses engine-specific VRAM + host cache behavior for a >VRAM MoE;
- CUDA VMM proves useful mapping primitives but not model-level policy;
- xInfer never reached a qualified local KV A/B experiment;
- zLLM declares Qwen3.6/3.8 adaptive CPU+CUDA placement, but the causal
  placement rail remains blocked by model inventory.

A generic placement/materialization API would therefore encode assumptions
that have not been shown to survive across engines.

## 2. Resource-envelope intent — PROMOTE_EXPERIMENTAL

A supervisor may safely express constraints such as:

- maximum GPU bytes;
- minimum GPU reserve;
- maximum host bytes;
- requested context/concurrency envelope.

The engine must remain free to choose how to satisfy that envelope or return
an explicit unsatisfied result.

This boundary is suitable for experimental implementation, not production
policy. Q-005 did not complete the causal changing-VRAM placement experiment,
so automatic response to resource pressure is not yet generally qualified.

## 3. Runtime observability — PROMOTE_CONTRACT

Q-003 demonstrated a useful common fact plane across three materially
different mechanism classes:

- exact identity;
- desktop/control profile;
- ambient and peak physical VRAM;
- explicit warmth/residency state;
- reclaim or release behavior;
- driver-health observation.

Q-006/Q-007 add the critical truth rule: unavailable facts are UNKNOWN and
carry provenance rather than receiving plausible defaults.

This observability contract is justified for implementation.

## 4. EngineProvider lifecycle — PROMOTE_EXPERIMENTAL

Q-007's reference contract passed 7/7 local tests and represents:

- mistral.rs/Bonsai;
- Pulsar;
- zLLM;
- a one-shot CLI engine.

It also preserves semantic readiness, declared-vs-qualified capabilities,
resource envelopes, and unload-vs-reclaim.

Concrete adapters do not yet exist in gnostral.rs, so the contract is promoted
to a non-production implementation program rather than declared production
ready.

## Ratified modeld boundary

modeld / the outer supervisor **may own**:

- engine registry and selection;
- exact model artifact identity;
- declared versus qualified capability ledger;
- semantic readiness gating;
- request priority/deadline at the provider boundary;
- resource-envelope intent;
- load / serve / drain / unload lifecycle intent;
- runtime observation with provenance;
- physical reclaim qualification;
- fault and driver-health adjudication.

modeld **must not own**:

- CPU/GPU layer placement;
- expert placement;
- KV block allocation/eviction/compression;
- radix/paged cache mutation;
- CUDA virtual-page mapping;
- token-level batch construction;
- kernel selection.

## Final decision

```text
runtime observability          PROMOTE_CONTRACT
resource-envelope intent       PROMOTE_EXPERIMENTAL
EngineProvider lifecycle       PROMOTE_EXPERIMENTAL
generic materialization        REJECT_GENERIC_AUTHORITY
```

This closes the original Q-001→Q-008 research sequence.

The next justified program is not another engine bakeoff. It is an adapter
implementation slice: bind EngineProvider v0 to already-qualified runtimes
behind a non-production gate, then prove that the contract retains the same
truth and authority boundaries in executable integration.

Machine-readable decision:
`evidence/q008/modeld-promotion-gate.json`.
