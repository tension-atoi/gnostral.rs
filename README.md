# gnostral.rs

Rust-first local inference research lab.

gnostral.rs is a public, reproducible research repository for local AI inference and serving on constrained hardware. It studies Rust-native and Rust-first runtimes, quantization, multimodal workloads, memory residency, KV-cache behavior, concurrency, model lifecycle, and engine-neutral orchestration.

This repository does not claim to own, replace, or author the upstream inference engines studied here. Upstream projects retain their own copyright, licenses, names, and provenance.

## Reference host

The initial public research baseline comes from an NVIDIA RTX 3070 with 8 GiB VRAM and 32 GiB system RAM. Results are evidence for that bounded environment unless a report explicitly establishes broader generality.

## Research principles

- Real artifacts before synthetic claims.
- Negative results are retained.
- Vendor claims are never silently promoted to reproduced facts.
- Engine-specific mechanisms remain engine-specific until generality is shown.
- A commit message is not evidence.
- Performance claims require a retained protocol and measurement artifact.
- Upstream support and local patched support are always distinguished.
- Tool execution authority is outside the inference engine.

See QUESTLOG.md and docs/EVIDENCE_MODEL.md.

## Initial tracks

1. Bonsai / Rust CUDA — ternary and ultra-low-bit execution on mistral.rs plus Candle-derived kernels.
2. Elastic memory — RAM↔VRAM behavior, oversubscribed models, CUDA VMM, residency, reclaim, and desktop pressure.
3. Runtime challengers — xInfer, zLLM, UniLLM, Pulsar, candle-vLLM and other credible Rust-first runtimes.
4. Engine-neutral orchestration — lifecycle and capability contracts above individual runtimes.

## Public baseline

The current qualified Bonsai product baseline is 35.2 tok/s, 28.44 ms/token, on the bounded FG-02 protocol.

A historical local commit title stated that a 40 tok/s FG-03 product gate had been achieved. The retained FG-03 evidence does not support publishing that number: the required final qualification artifact is absent and the implementation-authority document says the relevant follow-on seams had not been implemented. Public gnostral.rs therefore does not claim 40 tok/s.

See quests/Q-001-FG03-TRUTH-01.md.

## License

Original gnostral.rs material is MIT licensed. Vendored, adapted, or derived third-party material is not relicensed by this repository. Its original license and provenance must be preserved.

See THIRD_PARTY.md and docs/VENDORING_POLICY.md.

## Contributing

Reproductions, negative results, engine intakes, donor analyses, and bounded implementation experiments are welcome. Contributions require provenance and a DCO-style Signed-off-by trailer.

See CONTRIBUTING.md.
