# M6 Video Engine Evaluation — RTX 3050 6 GB

**Status:** Evaluation decision record; no video engine is integrated or runtime-verified yet.

## Target machine

- NVIDIA GeForce RTX 3050 Laptop GPU, 6 GB VRAM
- 16 GB system RAM
- Windows
- Existing local Bionic/Qwen text-planning service must remain unchanged

## Decision

Evaluate **FramePack first** as the primary local video-generation candidate.

The official FramePack repository states that it supports Windows and NVIDIA RTX 30/40/50-series GPUs with FP16/BF16 support and lists 6 GB GPU memory as its minimum. It also describes memory-managed long-video generation. This is the closest published hardware match for the target laptop, but the stated minimum is not a guarantee of acceptable speed, stability, or quality on this specific RTX 3050 Laptop GPU.

Official source: https://github.com/lllyasviel/FramePack

Keep **LTX-Video 2B out of the first implementation path**. Current ComfyUI workflow-template documentation lists 12 GB minimum VRAM for 2B and 8–10 GB for 2B distilled FP8. That exceeds the target GPU's 6 GB VRAM.

Sources:
- https://github.com/Comfy-Org/workflow_templates/blob/main/site/knowledge/models/ltx-video.md
- https://github.com/Lightricks/LTX-Video

## Scope boundary

This PR records the hardware evaluation only. It does not:
- install FramePack or ComfyUI;
- download model weights or custom nodes;
- change Python dependencies or CUDA/PyTorch installations;
- alter, move, delete, or reconfigure Bionic/Qwen files or endpoints;
- add a cloud fallback or transmit prompts/media externally;
- claim that generation works on the target PC.

## Required local preflight before integration

1. Confirm exact GPU name, dedicated VRAM, driver version, and CUDA capability using local diagnostics.
2. Confirm available system RAM and free disk space.
3. Confirm the target Python version and whether the FramePack installation instructions support the selected Windows/Python/CUDA combination.
4. Review repository code license and each model-weight license separately before redistribution or commercial use.
5. Check required model downloads and disk footprint before any download; require explicit user confirmation.
6. Ensure existing Bionic/Qwen continues to work unchanged.

## Runtime acceptance gate

Do not mark FramePack supported until a real test on the target laptop demonstrates all of the following:

- installation in an isolated environment, without modifying the existing Bionic runtime;
- successful model load without CUDA out-of-memory;
- one short image-to-video generation completes and produces a valid playable video file;
- output file size, duration, dimensions, frame rate, generation time, peak VRAM, and peak system RAM are recorded;
- cancellation, failed generation, and retry do not corrupt project assets;
- no network access beyond explicitly approved model/runtime downloads;
- generated output is imported into a STILLA project and remains readable after app restart.

## Fallback policy

If FramePack fails the 6 GB laptop test, do not silently switch to a cloud provider or a heavier model. Record the failure evidence and evaluate lower-memory alternatives or an explicitly optional remote provider as a separate decision.

## Next implementation step

After this decision record is reviewed, implement a read-only local hardware/runtime preflight and a bounded FramePack adapter behind an explicit provider selection. Keep all heavy inference outside the UI process and preserve the existing local-only default.
