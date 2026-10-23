# ADR 0001: Modular, local-first architecture

- Status: Proposed for M0 review
- Date: 2026-10-24

## Context

STILLA is intended to support planning, media generation, editing, and export. These tasks have different runtime, licensing, hardware, and failure characteristics. The existing Recapv1 project is a separate codebase and must not be destabilized during initial STILLA development. The developer PC has 16 GB RAM and an RTX 3050 with 6 GB VRAM, so large video models may be infeasible without low-memory modes or external execution.

## Decision

1. Keep STILLA in its own repository.
2. Define provider contracts before adding concrete generation engines.
3. Use the existing Bionic OpenAI-compatible local endpoint for Qwen planning; do not install or copy model weights.
4. Separate planning from image, video, speech, and rendering providers.
5. Keep GPU jobs out of the UI process and make their status/cancellation explicit.
6. Reuse Recapv1 functionality only after reviewing exact files, dependencies, tests, and license. Prefer stable interfaces over copying broad code.
7. Keep cloud providers optional and clearly label local versus remote processing.

## Consequences

- More initial interface work, but lower coupling and easier provider replacement.
- CI can test schemas and provider contracts with fake servers, without GPU access or credentials.
- Real generation capability remains unproven until a local smoke test passes on target hardware.
- Packaging and UI framework are not locked until a small Windows-compatible architecture spike is reviewed.

## Rejected alternatives

- Putting all new work directly inside Recapv1: increases regression risk and mixes product goals.
- Bundling large models or GPU runtimes in the first milestone: excessive disk/runtime risk and poor CI reproducibility.
- Claiming universal local video generation on 6 GB VRAM: not supported without model-specific measurement.
