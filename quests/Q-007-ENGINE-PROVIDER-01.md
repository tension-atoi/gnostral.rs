# Q-007 — ENGINE-PROVIDER-01

State: CLOSED — CONTRACT_V0_QUALIFIED

## Question

What is the smallest engine-neutral provider contract justified by Q-002
through Q-006?

The contract must let a supervisor select and lifecycle-manage inference
engines while preserving engine ownership of placement, KV materialization,
batch construction, and kernel/runtime policy.

## Evidence constraints

The contract inherits the following proven boundaries:

- Q-002: process/socket/HTTP readiness is weaker than semantic readiness.
- Q-002: declared context/concurrency limits are not qualified capacity.
- Q-002/Q-003: physical reclaim and driver health are lifecycle facts.
- Q-003: residency observations can be normalized across heterogeneous
  mechanisms.
- Q-003: materialization mechanisms cannot yet be normalized safely.
- Q-004: a compile/load success is not equivalent to a usable runtime.
- Q-005: resource availability may influence engine placement, but the engine
  owns the placement mechanism.
- Q-006: registry, request state, lifecycle and health shapes are useful
  donors; device/KV/token scheduling stays engine-internal.
- Q-006: unknown operational facts must remain UNKNOWN.

## Supervisor authority

The provider contract MAY allow the supervisor to specify:

- engine identity;
- exact model artifact identity;
- requested modality and semantic operation;
- requested context/concurrency envelope;
- resource budget or reserve requirement;
- request priority/deadline;
- load / serve / drain / unload lifecycle intent.

The contract MUST NOT expose generic supervisor commands for:

- moving a layer to CPU/GPU;
- choosing a GPU layer count;
- mapping/unmapping device pages;
- allocating/evicting KV blocks;
- selecting radix/paged cache nodes;
- constructing token-level batches;
- selecting engine-internal kernels.

## Exit gate

Q-007 closes only when:

1. an explicit provider state machine is published;
2. declared capabilities are separated from qualified capabilities;
3. semantic readiness is first-class;
4. runtime facts carry provenance or UNKNOWN;
5. unload and physical reclaim are distinct but composable receipts;
6. forbidden engine-internal authority is explicit;
7. the contract can represent Q-002 mistral.rs, Q-003 Pulsar, Q-005 zLLM,
   and a one-shot/CLI engine without engine-specific fields leaking upward.

## Post-closure review — 2026-10-09

**Disposition: CLOSED / CONTRACT_V0_QUALIFIED, NO PRODUCTION ADAPTER CLAIM.** The dependency-free Rust reference contract and its 7/7 local tests are not concrete production adapters. Q-009 may emit engine-origin expert-residency observations; future WakeKV experiments may emit KV-specific observations. The provider must not prescribe expert/KV slots or movement. Preserve declared versus qualified capability, provenance/UNKNOWN, semantic readiness, and unload-versus-physical-reclaim separation. No v0 public API or control authority is changed by this note.
