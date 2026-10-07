# Q-008 — MODELD-PROMOTION-GATE

State: CLOSED — OBSERVABILITY_PROMOTED / MATERIALIZATION_REJECTED

## Question

Does any residency/materialization authority studied in Q-002 through Q-007
deserve promotion into an engine-neutral modeld/supervisor control surface?

This is a promotion gate, not a new benchmark.

## Candidate surfaces

Q-008 evaluates four distinct surfaces:

1. **GENERIC_MATERIALIZATION** — supervisor commands for engine-internal
   CPU/GPU/page/KV placement.
2. **RESOURCE_ENVELOPE_INTENT** — supervisor states budgets/reserves while the
   engine chooses materialization.
3. **RUNTIME_OBSERVABILITY** — normalized physical residency, queue, readiness,
   reclaim, and health facts with provenance.
4. **ENGINE_PROVIDER_LIFECYCLE** — engine/model selection, load, semantic
   readiness, serve, drain, unload, and reclaim qualification.

They must not be promoted or rejected as one bundle.

## Promotion criteria

A surface may be promoted toward production implementation only when all
applicable criteria are satisfied:

### C1 — Generality

The abstraction represents at least two materially different engine/runtime
mechanisms without engine-specific semantics leaking upward.

### C2 — Causal evidence

If the surface controls placement/residency, the requested change must have a
reproducible causal relationship to the observed resource state.

### C3 — Semantic safety

A successful lifecycle/control operation preserves semantic readiness under
its qualified envelope.

### C4 — Reclaim/fault safety

Unload/failure behavior has bounded reclaim and no unresolved driver-health
regression in the qualified profile.

### C5 — Ownership boundary

The promoted surface does not move engine-internal token scheduling, KV
materialization, kernel selection, or memory-page authority into modeld
without evidence of safe generality.

### C6 — Truthful observability

Operational facts are measured/reported with provenance or UNKNOWN. Synthetic
defaults cannot satisfy the gate.

### C7 — Failure closure

Known negative results and unsupported paths remain representable without
forcing the supervisor to guess or emulate engine internals.

## Possible decisions

- `PROMOTE_CONTRACT` — justified for implementation as an engine-neutral
  contract.
- `PROMOTE_EXPERIMENTAL` — worth implementing behind a non-production gate.
- `DEFER` — useful direction but missing required evidence.
- `REJECT_GENERIC_AUTHORITY` — evidence says the mechanism must remain
  engine-internal.

## Non-goal

Q-008 does not authorize production deployment by itself. It decides which
authority boundaries are justified enough to enter an implementation program.
