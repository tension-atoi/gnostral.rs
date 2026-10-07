# Q-002 DESKTOP-PRESSURE-01

Date: 2026-10-07
Classification: OBSERVED / bounded negative runtime result

## Target

- mistral.rs 0.9.3 experimental Bonsai path;
- engine revision: `0bed3b4ce4f490131696ea268e133f952425bcc0`;
- binary SHA-256: `c29c9c822696f0c6b5460d5ee98884cafe5c1989cc884967595259cf09860189`;
- Ternary Bonsai 2 27B PTQ1 SHA-256: `53107f530aa52eb00912263ab1ee29bd199261c87cd7b4ad4ca1318c1fe33ee3`;
- 64/64 CUDA layers, max model length 4096;
- paged attention off, prefix cache off, recurrent pool slots 2.

## Ambient pressure

Total GPU memory in use before engine start was 1446 MiB.

Observed background GPU clients included two browser GPU processes and the
live desktop application surface. This run intentionally retains them and is
therefore DESKTOP-PRESSURE evidence, not CONTROL evidence.

## Result

The process reached HTTP `/v1/models` readiness in **14,094.5 ms**.

At that point total GPU usage was **7686 MiB**, leaving **186 MiB free**.
The sampler later observed **7718 MiB used / 154 MiB free**.

Before the first external semantic request, the engine log already recorded a
CUDA out-of-memory error in a prompt step followed by another OOM while
resetting model cache.

The first `2+3=` semantic request then returned HTTP 500 with the same
prompt-step CUDA OOM. Later requests returned HTTP 500 immediately.

Therefore C1/C4/C8 measurements from this process are **INVALID AS CONCURRENCY
MEASUREMENTS**: semantic readiness had already failed.

No NVIDIA Xid or MMU fault was observed during the run window.
After process exit, total GPU use returned to the ambient desktop range.
Exact reclaim latency is UNKNOWN because the first harness revision failed
while aggregating the reclaim timestamp after the engine had already exited.

## Finding

HTTP endpoint readiness is not a sufficient runtime readiness contract for
this workload.

gnostral.rs therefore distinguishes:

1. **HTTP-ready** — control endpoint responds;
2. **semantic-ready** — a declared correctness probe succeeds.

Only semantic-ready engines may enter concurrency and throughput qualification.

## Non-claims

This does not prove that 64/64 serving is generally unstable.
It proves that this exact full-GPU / 4096-context configuration did not remain
semantically runnable under the measured ~1.45 GiB ambient desktop pressure.
