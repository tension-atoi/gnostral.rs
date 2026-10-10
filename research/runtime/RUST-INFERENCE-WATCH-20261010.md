# GNU6 Rust Inference Watch — 2026-10-10

Status: **UPSTREAM VERIFIED / LOCAL INTEGRATION NOT QUALIFIED**. This is an engineering intake, not a capability promotion. Reviewed the four exact commits through the connected GitHub commit/diff API, not merely the release announcements.

## Priority P1 — Burn Remote v5 and Flex quantization

Upstream:
- [Burn #6010](https://github.com/tracel-ai/burn/commit/839136c02b9221ae069383bf80881802165ec578), `839136c02b9221ae069383bf80881802165ec578`.
- [Burn #6004](https://github.com/tracel-ai/burn/commit/58664ff6f3ded952226533b94d7260c048624997), `58664ff6f3ded952226533b94d7260c048624997`.

Verified: Burn Remote adds quantize/dequantize, quantized and mixed matmul, layout ops and quantized transfer/read routes, including byte-preserving tests for supported layouts, transposes and inter-server transfers. The application protocol changes from v4 to **v5** with incompatible-peer refusal. Flex adds symmetric integer and floating-point quantization schemes, including E4M3, E5M2 and E2M1, with careful scheme/packing-axis/scale handling.

**Relevance:** a candidate for a *separate quantized-tensor transport oracle* and a useful anti-corruption boundary between source weights, packed representation and remote execution. This is NOT evidence that Burn can currently load the exact Q012 GGUF MoE into its system, that its quantization matches Bonsai ternary PTQ1, or that CPU/RAM↔VRAM model-expert residency is managed automatically.

**Next bounded experiment BURN-REMOTE-01 (PROPOSED, NOT EXECUTED):**
1. Freeze repository commits, Cargo lockfiles, compiler and supported device/mode matrix. Use a loopback-only pair of local peers under `gnu6-lab-run` and explicitly bounded memory.
2. Negotiate protocol v5; negative control v4 must be refused. No broad egress, remote host credentials or background service required.
3. Round-trip Q8S, Q4S and supported FP8/FP4 Flex schemes and verify **dtype + scheme + shape + quantized values/scales raw bytes** across same-peer, cross-peer and transposed/packed-axis layouts. Reject unsupported schemes and missing metadata.
4. Establish an independent reference oracle and controls for mismatched endianness, scale layout and partial transfer. Measure transfer time, bytes moved and memory peak without attributing improvements to inference quality or residency.
5. Only then consider a CPU↔GPU transfer as a distinct optional test, with fresh GPU headroom and independent allocation/reclaim checks; it is not authorized by a remote CPU transport PASS.
6. **Do not** add Burn as a model executor, donor dependency or scheduler to the qualified `mistralrs` binary on this evidence alone.

## Priority P2 — Ferrum SLO-aware scheduling

Upstream [Ferrum #402](https://github.com/sizzlecar/ferrum-infer-rs/commit/0680840becae342e481df4ac0705c43fc08633a7), `0680840becae342e481df4ac0705c43fc08633a7`.

Verified: optional `--scheduler-slo ttft:200,tpot:15,itl:50` or file settings, disabled by default. Prefill wave estimation primarily uses inter-token latency (ITL) with a TTFT fallback. TPOT is a benchmark/request-level target, not itself the direct per-wave cap. `/health` surfaces adaptation and infeasibility; no throughput gain established on the published ShareGPT workload. Estimates do not guarantee client-visible P99.

**Next experiment FERRUM-SLO-01 (PROPOSED, NOT EXECUTED):** start with replayable request traces, independent client-observed TTFT, TPOT and visible ITL; freeze tokenizer, prompts, concurrency, token counts and warmup. Compare static versus opt-in scheduler across repeated runs on *same* hardware and selected model. Track goodput under P99 constraints, tails, OOM, cancellation, and any excessive reduction of throughput. Reject a claimed performance win without confidence bounds and controls. No scheduler modification to Q013's one-shot launcher yet.

## Conditional P3 — CubeCL CUDA transfer/collective ordering

Upstream [CubeCL #1782](https://github.com/tracel-ai/cubecl/commit/29990822e4ec04896e0ab99e28060955a0ca22c0), `29990822e4ec04896e0ab99e28060955a0ca22c0`.

Verified: the CUDA communication path splits collective and device-to-device transfer streams/communicators, coordinates first-use/connect and ordering, and adds tests for transfers alongside `all_reduce`, pipeline/tensor-parallel patterns and deadlock prevention.

**NEXT: monitor, do not run multi-GPU claims on the reference machine.** Physical RTX 3070 count is one. A later hardware gate requires at least two supported GPUs, pinned NCCL/CUDA/CubeCL versions, bounded collective timeouts, failure cleanup, driver/Xid checks and reproducibility of concurrent transfer plus all-reduce. No `Q013C` promotion follows from a CubeCL upstream fix.

## Promotion matrix

| Candidate | Upstream status | Local status | Allowed next action |
| --- | --- | --- | --- |
| Burn Remote v5 / Flex quantized | Verified change | NOT_TESTED | isolated loopback byte-oracle prototype |
| Ferrum adaptive SLO | Verified opt-in capability; no measured throughput win | NOT_TESTED | offline trace and A/B benchmark design |
| CubeCL CUDA collective order | Verified upstream fix | NOT_TESTED; physical 2nd GPU missing | watch + prepare multi-GPU gates |
| Q012 mistral.rs dense / embedding / MoE | Separate local functional evidence | PASS (sequential functional) | preserve existing oracle |
| Q013C dense supervisor | Separate local live/pinned evidence | PASS (single dense server) | constrained adapter hardening |

**Boundary:** The four verified upstream commits introduce candidate design primitives. They do not establish a new local qualified runtime, hot-swap, distributed serving or automatic model residency. Do not blend research inputs with Q012/Q013 executable evidence.
