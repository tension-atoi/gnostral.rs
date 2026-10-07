# Bonsai Rust CUDA public baseline

## Bounded claim

PROVEN under the retained local FG-02 qualification protocol:
- target GPU: NVIDIA RTX 3070 8 GiB;
- model: Ternary Bonsai 2 27B PTQ1;
- topology: full-GPU 64/64 for the qualified path;
- qualified decode baseline: 35.2 tok/s;
- qualified TPOT: 28.44 ms/token.

Earlier stages established native Rust/Candle execution of experimental PTQ1/PQ2 formats, semantic micro-oracles, full-GPU PTQ1 residency after recurrent-pool tuning, Q8_1/dp4a MMVQ acceleration, PTQ1 MMQ prefill work, a BF16 GDN batch-broadcast concurrency defect and bounded fix, and PQ2 MMVQ qualification.

## Not claimed

- 40 tok/s FG-03 closure;
- arbitrary concurrency;
- production serving readiness;
- broad numerical parity for every workload;
- cross-GPU generality.
