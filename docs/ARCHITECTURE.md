# Architecture direction

gnostral.rs studies a layered architecture rather than a single monolithic inference engine.

workload
→ engine-neutral supervisor
→ one or more qualified runtimes
→ runtime evidence

Candidate runtimes currently include mistral.rs/Candle-derived paths, Pulsar, xInfer, zLLM, UniLLM, candle-vLLM, and future qualified engines.

The supervisor contract is intentionally not yet ratified. It is blocked on runtime and challenger quests in QUESTLOG.md.

## Authority boundary

Engines may expose capability and health information. They do not receive implicit authority over privileged host actions, network policy, secret access, or tool execution.
