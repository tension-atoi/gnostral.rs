# EngineProvider v0

Status: **Q-007 draft contract**

This contract is the smallest engine-neutral surface currently justified by
gnostral.rs evidence.

It separates four things that are easy to accidentally collapse:

1. what an engine **declares** it supports;
2. what gnostral.rs has **qualified** under retained evidence;
3. what a runtime instance is doing **now**;
4. how the engine internally materializes weights, KV state, batches, or
   device placement.

Only the first three cross the provider boundary.

## Core invariant

> The supervisor controls intent, lifecycle, and resource envelopes.
> The engine controls materialization.

A resource envelope such as “leave 1 GiB GPU reserve” is a valid supervisor
constraint. “Put 42 layers on GPU” is not.

## Identity

Every provider exposes immutable engine identity:

- engine/project name;
- exact revision/version where available;
- binary/artifact digest where available;
- implementation transport: in-process, local server, local CLI, or remote;
- upstream/source provenance.

Every loaded model instance has exact artifact identity. Human model names are
not sufficient when a digest is available.

## Capabilities: declared versus qualified

`DeclaredCapability` records what the engine/source claims.

`QualifiedCapability` records what retained evidence has actually proven,
including the qualification profile and evidence reference.

The two sets are never merged.

Example:

```text
declared context = 4096
qualified context = 384
```

is a valid state, not a contradiction to hide.

## Lifecycle state machine

A persistent instance may transition:

```text
OFFLINE
  -> LOADING
  -> READY(CONTROL)       optional
  -> READY(REGISTERED)    optional
  -> READY(SEMANTIC)      required before production routing
  -> SERVING
  -> DRAINING
  -> UNLOADING
  -> STOPPED

any state -> FAULTED
```

Readiness levels may be skipped when they are not applicable. For example, a
one-shot CLI engine may have no control endpoint or model registry and may
move from LOADING directly to READY(SEMANTIC).

Socket/HTTP availability is never equivalent to semantic readiness.

## Load intent

A supervisor may provide:

- exact model artifact;
- requested modality/operation;
- requested context envelope;
- requested concurrency envelope;
- maximum GPU/host resource budgets;
- minimum GPU reserve;
- priority/deadline;
- persistent versus one-shot serving mode.

It may not provide generic layer/page/KV placement commands.

## Runtime facts and provenance

Every operational fact is represented as one of:

- `UNKNOWN(reason)`
- `DECLARED(value, source)`
- `ENGINE_REPORTED(value, source, timestamp)`
- `HOST_OBSERVED(value, source, timestamp)`
- `DERIVED(value, method, timestamp)`

A missing observation must never be replaced with a plausible default.

Examples of facts:

- physical GPU bytes;
- process RSS / host bytes;
- KV bytes;
- queue depth;
- active requests;
- selected placement summary;
- driver health;
- context currently admitted;
- concurrency currently admitted.

Estimates and physical observations are separate facts.

## Semantic readiness

A semantic readiness receipt contains:

- model handle;
- probe identity;
- input digest or bounded probe description;
- expected predicate;
- observed result;
- pass/fail;
- timestamp;
- engine identity;
- model artifact identity.

A model cannot enter `READY(SEMANTIC)` without a passing receipt.

## Unload versus reclaim

Engine unload and physical reclaim are two events.

`UnloadReceipt` proves the engine accepted/completed its lifecycle operation.

`ReclaimReceipt` proves, through host or trustworthy engine telemetry, that
physical resources returned toward a declared ambient envelope.

They are composable but not interchangeable.

This distinction preserves the Q-002/Q-003 observation that a process can
exit before sampled physical GPU memory has returned to ambient.

## Health

Health includes lifecycle state plus provenance-bearing facts. It may expose:

- queue depth;
- active requests;
- last engine error;
- driver fault state;
- observed GPU/host residency;
- semantic readiness receipt age;
- reclaim status.

A boolean “running” is insufficient.

## Engine-internal authority

The following are deliberately absent from EngineProvider v0:

- `move_layer_to_gpu()`
- `set_gpu_layer_count()`
- `map_device_page()`
- `evict_kv_block()`
- `promote_radix_node()`
- `construct_token_batch()`
- `select_kernel()`

Engines may report what they selected. They retain authority over how they
selected it.

## Scheduling boundary

The outer supervisor may choose:

- which engine receives a model/request;
- priority/deadline;
- resource envelope;
- whether to load, drain, or unload.

The inference runtime chooses:

- token-level batching;
- KV allocation/eviction/compression;
- page management;
- kernel selection;
- CPU/GPU layer/expert/page placement.

## Qualification requirement

A provider implementation is not qualified merely because it implements this
interface.

Qualification remains evidence-driven. A provider adapter must separately
prove:

- load/registration behavior;
- semantic readiness;
- supported concurrency/context;
- unload/reclaim;
- fault recovery;
- driver health under the target profile.
