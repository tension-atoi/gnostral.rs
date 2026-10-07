# Elastic memory L1 synthesis

The first elastic-memory slice compared engine-specific residency mechanisms without promoting a generic production authority.

## Proven or observed in bounded local controls

- mistral.rs small dense model can serve as an always-hot control and releases GPU memory quickly after process exit;
- Pulsar can execute a real MoE model larger than local 8 GiB VRAM;
- warm host/VRAM residency materially changes >VRAM performance;
- CUDA VMM provides usable fine-grained mapping/remapping primitives on the RTX 3070;
- Qwen3.5 multimodal execution showed reusable encoder state in mistral.rs;
- desktop pressure measurably changes safe residency margins.

## Important negative evidence

- one Pulsar/Qwen IQ2_XXS path triggered NVIDIA Xid 31;
- a tested Candle CUDA-VMM allocator path failed repeated same-model growth;
- multimodal success was not cross-family general: exact tested Ministral and Gemma combinations hit upstream execution defects.

## Promotion decision

REJECTED for production promotion at L1.

Measured gains and bounded reproducibility exist, but cross-family generality and a defensible engine-neutral materialization contract are not yet proven.
