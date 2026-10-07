# Third-party material

gnostral.rs does not claim ownership of upstream projects studied by the lab.

| Project | Role in research | Local status |
|---|---|---|
| mistral.rs | Rust inference/runtime reference and Bonsai integration target | upstream plus experimental local patches |
| Candle | tensor/kernel substrate used by local experiments | upstream plus experimental local patches |
| candle-vLLM | Rust serving/runtime candidate | upstream probe / donor analysis |
| Pulsar | oversubscribed MoE and residency reference | upstream experimental track |
| xInfer | scheduler/KV compression challenger | planned evaluation |
| zLLM | placement/runtime challenger | planned evaluation |
| UniLLM | unified runtime/model abstraction donor | planned evaluation |

Actual vendored code must carry its upstream license in-tree and be registered in manifests/upstreams.toml.

The root MIT license applies only to original gnostral.rs material unless a file or subtree states otherwise.
