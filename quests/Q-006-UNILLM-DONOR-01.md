# Q-006 — UNILLM-DONOR-01

State: ACTIVE

## Question

Which UniLLM abstractions are useful donors for gnostral.rs / future
ENGINE-PROVIDER-01 without importing engine-internal residency policy into the
supervisor?

Q-006 is an architecture donor analysis. It is not a throughput bakeoff.

## Pinned upstream

- repository: `https://github.com/cognisoc/unillm`
- revision: `9e20eaf8d8b25191534f531746faa4c025a50453`
- license: MIT

## Donor dimensions

Q-006 inspects five boundaries:

1. **Model contract** — what semantic execution facts the model abstraction
   owns.
2. **Backend contract** — how CPU/CUDA/Metal device execution is separated.
3. **KV/cache contract** — ownership of paged/radix cache state and mutation.
4. **Scheduler contract** — admission, batching, preemption, and request state.
5. **Lifecycle/observability** — whether load, unload, resident bytes, health,
   reclaim, and model capabilities are explicit enough for a supervisor.

## Prior constraints from gnostral.rs

Q-002 and Q-003 already constrain the donor result:

- HTTP/socket readiness is weaker than semantic readiness;
- physical residency facts can be normalized across engines;
- materialization mechanisms remain engine-specific;
- reclaim and driver health are supervisor-relevant observations;
- concurrency claims require semantic validity, not request acceptance alone.

Any donor concept that conflicts with those observations is rejected.

## Exit gate

Q-006 closes with a table of:

- `ADOPT_CONCEPT`
- `ADAPT_CONCEPT`
- `ENGINE_INTERNAL`
- `REJECT`
- `UNKNOWN`

for the relevant UniLLM interfaces.

No code is vendored and no runtime is promoted by this quest.
