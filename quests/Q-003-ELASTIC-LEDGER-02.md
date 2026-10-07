# Q-003 — ELASTIC-LEDGER-02

State: CLOSED — OBSERVABILITY_CONTRACT_SUPPORTED

## Question

Which residency facts can be observed consistently across a dense model
runtime, an oversubscribed MoE runtime, and raw CUDA virtual-memory primitives
without pretending their mechanisms are interchangeable?

Q-003 does not seek a universal allocator. It builds a comparable evidence
ledger for residency, warmth, reclaim, and desktop safety.

## Pinned local tracks

- mistral.rs v0.9.3: `24dbf5c256f232176ee5949485ba264049407fbe`;
- Pulsar main snapshot: `18f990094e1091ee2ef3078f20be418f8c162f03`;
- candle_cuda_vmm: `e8e3d106d375a88acaccdd9906b5302c35915828`.

These are Q-003 intake pins, not claims about latest upstream state.
## Workload classes

### DENSE_RESIDENT

mistral.rs with the existing small dense Qwen control. Purpose: load, steady
resident state, request behavior, and physical reclaim.

### MOE_OVERSUBSCRIBED

Pulsar with a previously safe >VRAM MoE control. Purpose: distinguish cold,
host-warm, and engine/VRAM-warm execution without using the known IQ2_XXS/Xid
combination.

### VMM_PRIMITIVE

CUDA VMM synthetic probe. Purpose: map/unmap/remap cost and physical commitment
without claiming model-level semantics.

No cross-class tok/s ranking is allowed.
## Common observation contract

Each track records, where meaningful:

1. exact upstream/binary/artifact identity;
2. desktop profile and ambient GPU memory;
3. process start and readiness boundary;
4. semantic readiness for serving engines;
5. process RSS and physical VRAM;
6. cold vs warm state classification;
7. request/prefill/decode timing when applicable;
8. physical reclaim to the ambient envelope;
9. NVIDIA Xid/MMU-fault window;
10. bounded desktop-health observation.

A field may be `NOT_APPLICABLE`; it may not be silently invented.

## State vocabulary

- `PROCESS_COLD` — new process; OS page cache not necessarily cold;
- `HOST_WARM` — useful host/file cache retained;
- `ENGINE_WARM` — engine-specific reusable state retained;
- `RECLAIMED` — physical GPU use returned to the declared ambient envelope.

`RESIDENT` and `WARM` remain distinct observations.
## Guardrails

- CONTROL and DESKTOP-PRESSURE remain separate lanes from Q-002.
- The Pulsar IQ2_XXS combination that previously produced Xid 31 is excluded.
- A driver fault fails the stability gate immediately.
- Existing L1 results are prior evidence, not automatically promoted into
  Q-003 proof.
- Mechanism ownership stays inside the runtime unless evidence proves a safe
  higher-level contract.
- No new modeld authority is implied.

## Exit gate

Q-003 closes when one machine-readable ledger contains at least one bounded,
reproducible observation for every track and makes explicit which fields are
comparable, incomparable, unknown, and unsafe.

The result must be sufficient to decide whether Q-007 can define only an
observability contract or something stronger.

## Closure

Closed on 2026-10-07 as **OBSERVABILITY_CONTRACT_SUPPORTED**.

Published evidence:
- `evidence/q003/residency-ledger.json`
- `research/runtime/Q003-ELASTIC-LEDGER.md`

Q-003 supports mandatory runtime observability but does not authorize a
generic materialization API or new residency authority.
