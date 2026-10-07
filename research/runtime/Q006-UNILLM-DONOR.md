# Q-006 — UniLLM Donor Analysis

**State:** CLOSED — DONOR_ANALYSIS_COMPLETE
**Date:** 2026-10-07

Q-006 evaluated UniLLM as an architecture donor, not as a performance
challenger.

Pinned upstream:

- repository: `cognisoc/unillm`
- revision: `9e20eaf8d8b25191534f531746faa4c025a50453`
- license: MIT

The source is structured into separate `runtime`, `kv`, `scheduler`,
`inference`, and CLI crates. Local unit validation completed:

- `unillm-kv`: **15/15 PASS**
- `unillm-scheduler`: **7/7 PASS**

These are source/unit-level donor checks, not GPU runtime qualification.

## Strong donor concepts

### ModelRunner — ADAPT_CONCEPT

The streaming runner surface is intentionally small: token input, generation
configuration, streaming callback, EOS, architecture, and context size.

This is a better donor for a future provider boundary than UniLLM's broader
`Model` trait, because the latter also owns tensor-level forward execution
and `to_device`.

gnostral.rs should adapt the runner shape toward semantic request execution,
not import tensor/model implementation details into the supervisor.

### ModelFactory / ModelRegistry — ADOPT_CONCEPT

Explicit registration, architecture discovery, and support queries are useful
provider concepts. A supervisor needs to know what an engine claims it can
load before attempting a lifecycle transition.

Capability discovery remains a claim until semantic readiness proves a loaded
instance.

### Request priority / timeout / state — ADAPT_CONCEPT

Typed request IDs, priorities, deadlines, queue state, and failure state are
useful at the engine-provider boundary.

They must remain distinct from token-level engine scheduling. The outer
supervisor may specify a deadline or priority; it should not assemble inference
batches itself.

## Engine-internal concepts

### Model::to_device — ENGINE_INTERNAL

Q-003 already showed why this must not become generic supervisor authority.
Different engines own fundamentally different residency mechanisms.

A future EngineProvider may expose placement/residency observations and
capabilities. It must not expose a generic “move this layer/page to GPU”
control simply because one donor trait has `to_device`.

### KV cache — ENGINE_INTERNAL

UniLLM exposes a useful paged allocator, radix cache, and hybrid-cache shape,
but the current source also contains:

- placeholder L3 compressed storage;
- placeholder/approximate GPU integration fields;
- placeholder defragmentation;
- approximate cache-memory accounting;
- incomplete copy/synchronize paths.

The basic KV/scheduler unit tests pass, but this is not evidence for a generic
cross-engine cache-control API.

The provider boundary should report KV facts such as resident bytes, context
capacity, cache mode, and reclaimability where the engine can prove them.
Allocation, radix mutation, paging, promotion, compression, and eviction stay
inside the engine.

### Continuous batching — ENGINE_INTERNAL

The simple scheduler has real request and batch state, but token-level
continuous batching is an inference-runtime responsibility.

A provider may expose:
- supported concurrency;
- current queue depth;
- capacity;
- preemption/cancellation capability;
- semantic outcome.

It should not export batch construction as modeld authority.

## Surfaces rejected as operational facts

UniLLM's current high-level inference layer contains several values that look
like telemetry but are explicitly mock/simplified:

- health GPU memory usage is hard-coded;
- TTFT/cache hit/memory usage fields are hard-coded in the generation result;
- response GPU utilization/peak memory/cache-hit values are hard-coded;
- the background batch worker currently contains an “in real implementation”
  placeholder instead of actual batch processing;
- several cache-aware scheduler heuristics use placeholder total memory and
  synthetic efficiency values.

These shapes may inspire schemas. Their current values must not be treated as
runtime evidence.

gnostral.rs therefore requires an important invariant:

> **Unknown operational facts remain UNKNOWN. They are never replaced by
> plausible defaults.**

## Missing lifecycle semantics

UniLLM has `start`, `stop`, `is_running`, health, and shutdown surfaces.
That is a useful starting shape, but Q-002/Q-003 require stronger semantics:

- process/socket ready;
- model registered;
- **semantic ready**;
- draining;
- stopped/faulted;
- physical reclaim completion.

A boolean `running` does not prove the model is usable, and `stop()` does
not by itself prove VRAM returned to the host envelope.

The future provider therefore needs explicit readiness and reclaim receipts.

## Decision table

| Surface | Decision |
|---|---|
| ModelRunner | ADAPT_CONCEPT |
| ModelFactory / registry | ADOPT_CONCEPT |
| model memory requirements | ADAPT_CONCEPT as estimate |
| Model::to_device | ENGINE_INTERNAL |
| paged/radix/hybrid KV mutation | ENGINE_INTERNAL |
| token-level continuous batching | ENGINE_INTERNAL |
| request priority/deadline/state | ADAPT_CONCEPT |
| lifecycle start/stop | ADAPT_CONCEPT |
| EngineHealth schema | ADAPT_CONCEPT |
| current mock health/resource values | REJECT |
| scheduler memory-pressure command | REJECT as generic authority |
| semantic-ready | REQUIRED FROM GNOSTRAL EVIDENCE |
| unload + physical reclaim receipt | REQUIRED FROM GNOSTRAL EVIDENCE |

## Architectural result

Q-006 strengthens the same line established by Q-003:

```text
provider registry / capability discovery   YES
semantic request interface                 YES
typed lifecycle + health                   YES, strengthened
runtime observation                        YES, provenance required

device placement commands                  ENGINE INTERNAL
KV/page/radix mutation                     ENGINE INTERNAL
token-level batching                       ENGINE INTERNAL
synthetic/default telemetry                REJECT
```

Q-006 is complete. The evidence is sufficient to unblock Q-007 and define the
first gnostral.rs `EngineProvider` contract without importing engine-internal
materialization authority.

Machine-readable decisions:
`evidence/q006/unillm-donor-decisions.json`.
