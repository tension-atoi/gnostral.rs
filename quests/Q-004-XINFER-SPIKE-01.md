# Q-004 — XINFER-SPIKE-01

State: CLOSED — NOT_QUALIFIED / RUNTIME_BLOCKED

## Question

Does xInfer add a measurable runtime capability on the reference RTX 3070
that the current gnostral.rs control arm does not already qualify?

The target capability is **KV-cache compression under a fixed local model and
fixed semantic workload**, with continuous-batching/prefix-cache behavior
recorded secondarily.

## Pinned upstream

- repository: `https://github.com/guoqingbao/xinfer`
- branch observed: `main`
- revision: `b88c15334fb607ff52cdc3fd875c3da796dcc020`
- license: MIT

This pin is an intake identity, not a claim about future upstream state.

## Reference workload

Local model:
`Qwen3.5-9B-Q4_K_M.gguf`

The first comparison uses the same model artifact and the same process/build
for both lanes:

1. baseline KV cache;
2. `turbo4` KV cache.

## Frozen measurements

Each lane records:

- exact xInfer revision/binary/model identity;
- CONTROL preflight and ambient VRAM;
- process start → HTTP-ready;
- semantic-ready result;
- short deterministic decode;
- total VRAM at ready and peak during request;
- maximum usable input context under the same model/runtime envelope;
- process reclaim;
- Xid/MMU-fault window.

If baseline and turbo4 both qualify, the primary Q-004 comparison is:

```text
context headroom gained per MiB of physical VRAM
```

Raw tok/s is secondary and must not substitute for context/residency evidence.

## Scheduler probes

Only after both KV lanes are semantically qualified:

- C1 / C4 / C8;
- prefix-cache repeated-prefix probe;
- scheduler recovery after a failed/oversized request.

These probes are observational. They do not authorize xInfer adoption.

## Guardrails

- no Python runtime is introduced into the execution path;
- no model download is required for the first spike;
- no Web UI is started;
- no MCP/tool execution is enabled;
- no network access is needed after source/build dependencies are resolved;
- any Xid/MMU fault fails the lane immediately;
- build failure on SM86 is retained as evidence rather than patched blindly;
- upstream benchmark claims remain VENDOR_CLAIM until reproduced locally.

## Promotion gate

Q-004 closes as useful only if xInfer demonstrates at least one of:

1. materially greater qualified context at comparable physical VRAM;
2. lower physical VRAM at the same qualified context;
3. concurrency/prefix-cache behavior that survives the frozen semantic gates
   and is not already represented by the Q-002 control.

Otherwise xInfer remains a watched upstream, not a donor or product candidate.

## Post-closure review — 2026-10-09

**Disposition: CLOSED / NOT_QUALIFIED / RUNTIME_BLOCKED.** WakeKV is a separate reported FlexiCache/vLLM research mechanism; it does not retroactively establish xInfer TurboQuant, continuous batching or KV correctness on SM86. Reassessment requires a new pinned, compatible upstream build, a runnable matching local model and a new frozen same-runtime KV A/B; no such rerun is recorded by this audit. Keep build failures and OOMs as negative evidence.
