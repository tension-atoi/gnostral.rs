# Q-002 CONTROL qualification

**State:** CLOSED — QUALIFIED_WITH_LIMITS
**Date:** 2026-10-07

## Qualified target

- mistral.rs 0.9.3 experimental Bonsai path;
- engine revision `0bed3b4ce4f490131696ea268e133f952425bcc0`;
- binary SHA-256 `c29c9c822696f0c6b5460d5ee98884cafe5c1989cc884967595259cf09860189`;
- Ternary Bonsai 2 27B PTQ1 SHA-256 `53107f530aa52eb00912263ab1ee29bd199261c87cd7b4ad4ca1318c1fe33ee3`;
- NVIDIA RTX 3070 8 GiB, driver 615.71.09, CUDA UMD 13.4;
- 64/64 CUDA layers;
- `--max-model-len 4096`;
- paged attention off;
- prefix cache off;
- recurrent pool slots = 2;
- live graphical desktop retained; tty7 explicitly allowed as desktop infrastructure.

The CONTROL lane was run after closing opportunistic browser GPU clients.
## Lifecycle

A process-cold start reached HTTP-ready in **3835.8 ms**. The OS page cache
was not flushed, so this is not a cold-storage measurement.

The process RSS at HTTP-ready was **6826.5 MiB**. Total GPU use at HTTP-ready
was **7396 MiB**, against an ambient CONTROL level of **1169 MiB**.

Graceful SIGTERM produced:
- SIGTERM → process exit: **25.4 ms**;
- SIGTERM → ambient VRAM envelope: **253.7 ms**;
- process exit → ambient VRAM envelope: **228.3 ms**.

Three successive starts passed the `2+3=5` semantic probe. A deliberate
SIGKILL returned GPU use to the ambient envelope in **238.1 ms**, and the
following restart again passed semantic readiness.

No NVIDIA Xid or MMU fault was observed in the qualification windows.

## Streaming latency

A deterministic 64-token streaming completion measured:
- client TTFT: **154.97 ms**;
- total streaming wall time: **1748.11 ms**;
- client-inferred TPOT: **25.29 ms/token**.

A paired non-stream request confirmed exactly 64 completion tokens and
reported native mistral.rs metrics:
- decode: **40.97 tok/s**;
- native TPOT: **24.41 ms/token**;
- prefill: **49.18 tok/s** for the 12-token prompt.

The client and native TPOT measurements are therefore consistent.

## Concurrency

The frozen one-token semantic oracle gave:
- **C1: PASS**;
- **C4: PASS**, 4/4 valid semantic responses;
- **C8: FAIL**, 4/8 valid responses in the primary run.

A boundary diagnostic repeated C5, C6, C7 and C8 twice each. Every lane
produced exactly **3 successful responses**, while a sequential recovery probe
immediately after every lane passed.

The failing requests changed between repeats and were not tied to a specific
prompt. The server's configured `--max-seqs` default is 32, so the observed
boundary is not explained by the declared scheduler sequence limit.

Root cause remains **UNKNOWN**. Concurrency above C4 is not qualified.

## Context growth

Token counts were measured with mistral.rs `/v1/messages/count_tokens`, so the
reported sizes include chat-template formatting rather than character-count
estimates.

Fresh/control runs established:
- 64: PASS
- 128: PASS
- 192: PASS
- 256: PASS
- 320: PASS
- 336: PASS
- 352: PASS
- 368: PASS
- **384: PASS**
- **512: CUDA OOM**
- 1024 / 2048 / 3072 / 4000: FAIL in fresh-process probes.

Therefore `--max-model-len 4096` is a declared configuration value, **not a
qualified usable context size** for this full-GPU topology on the reference
8 GiB card.

The measured context result is bounded by ambient desktop VRAM and this exact
binary/model configuration.

## Desktop-pressure contrast

With approximately **1446 MiB** ambient GPU use, the same server reached HTTP
readiness but left only 186 MiB free. Its first semantic request failed with
`CUDA_ERROR_OUT_OF_MEMORY`, followed by another OOM while resetting model
cache.

This proved that HTTP-ready is weaker than semantic-ready and caused Q-002 to
make semantic readiness mandatory before performance/concurrency measurement.

## Verdict

Q-002 is **QUALIFIED_WITH_LIMITS** and CLOSED.

Qualified:
- semantic-ready local serving in CONTROL;
- C1 and C4 semantic concurrency;
- bounded TTFT/TPOT;
- graceful VRAM reclaim;
- abrupt-process reclaim and restart;
- isolated 384-token input under the measured CONTROL envelope.

Not qualified:
- concurrency above C4;
- 4096-token practical context;
- production readiness;
- cross-GPU generality;
- the root cause of the C>4 partial-failure boundary.

Machine-readable packet: `evidence/q002/control-qualification.json`.
