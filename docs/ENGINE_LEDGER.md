# Engine ledger

This ledger distinguishes local evidence from upstream claims.

| Engine | Current local role | Local evidence state | Primary unresolved question |
|---|---|---|---|
| mistral.rs + Candle patches | Bonsai/Rust CUDA reference | extensive bounded proof | lifecycle + multi-model runtime qualification |
| Candle primitives | kernel/correctness substrate | extensive bounded proof | broader serving abstraction |
| candle-vLLM | serving challenger/donor | loader/format work only for Bonsai | semantic Bonsai execution |
| Pulsar | elastic-memory/MoE reference | >VRAM execution proven in bounded controls | generality + safety under more workloads |
| xInfer | challenger | not yet locally evaluated | KV compression + batching on 8 GiB |
| zLLM | challenger | not yet locally evaluated | adaptive placement under desktop pressure |
| UniLLM | donor/challenger | not yet locally evaluated | abstraction quality and lifecycle semantics |

No engine is designated the universal production runtime.
