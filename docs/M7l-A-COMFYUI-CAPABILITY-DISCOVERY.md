# M7l-A — Installed ComfyUI Conditioning Capability Discovery

## Scope

This slice adds a read-only capability inspector for the already-configured loopback ComfyUI instance. It does not change ComfyUI, install custom nodes, download models, submit workflows, or invoke GPU inference.

## Detection contract

- Reads only `/system_stats` and `/object_info` through the existing validated loopback configuration and bounded HTTP reader.
- Uses exact known node class names and checks each node's required input schema. A familiar class name alone is not evidence of a usable conditioning graph.
- Reports IPAdapter and InstantID independently as `available`, `partial`, or `unsupported`.
- Renamed or unknown custom nodes are not guessed or fuzzy-matched; they remain unsupported until an explicit schema adapter is reviewed and added.
- The report always sets `generation_ready=false`. Capability discovery is not workflow validation or generation approval.
- Version information is informational and bounded; missing version metadata is represented as null.

## Safety

- No arbitrary URL, redirect, prompt submission, workflow submission, model path inspection, node installation, cloud call, or media transfer.
- Catalog class count and input-name count are bounded.
- Malformed catalog entries and missing required sockets fail closed.
- Errors returned to the UI are sanitized and do not include local endpoint details.

## Automated acceptance

Run `python -m pytest tests/test_comfyui_capabilities.py tests/test_comfyui_diagnostics.py -q`.

Fixtures cover absent nodes, partial packs, schema mismatch, renamed custom nodes, malformed and oversized catalogs, version metadata, local-only read paths, and unavailable ComfyUI. These are contract tests with fake data; they do not prove the user's installed node pack is compatible.

## Remaining acceptance

The user's Windows laptop must run this inspector against the existing local ComfyUI instance. Record the exact discovered class names and required sockets before implementing M7l-B workflow compilation. Do not install or update any custom node as part of this step.
