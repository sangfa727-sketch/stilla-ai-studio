# M7l — ComfyUI Character Identity Conditioning

## Goal

Connect the existing, explicitly local ComfyUI runtime to the saved Character DNA and storyboard bindings so generated shots can use the approved character reference images as conditioning inputs. Character IDs, identity fingerprints, reference asset IDs, source files, and immutable character revisions remain authoritative.

## Existing baseline (verified on main at M7k)

- `CharacterProfile` stores validated visual identity, project-relative reference metadata, and an optional canonical seed.
- `build_generation_plan()` compiles positive/negative prompts, reference paths, identity fingerprint, consistency key, and seed.
- `ComfyUIConfig` restricts the server to loopback HTTP.
- `ComfyUIClient` validates and submits caller-supplied workflows, then reads history.
- `ComfyUIAssetStore` retrieves generated images into a project without overwriting existing assets.
- `diagnose_comfyui()` can inspect `/system_stats` and `/object_info`.
- The desktop UI currently performs ComfyUI health checks only; it does not yet bind character plans to a workflow or submit generation jobs.

## Delivery gates

### M7l-a — Capability and workflow contract

- Parse the live `/object_info` response into a bounded capability snapshot.
- Distinguish basic text-to-image nodes from optional reference-conditioning nodes; do not assume IP-Adapter, PuLID, InstantID, or custom nodes are installed.
- Define a strict, versioned workflow binding contract identifying positive prompt, negative prompt, seed, image loader/reference inputs, and output nodes.
- Reject missing, ambiguous, unsupported, or type-incompatible bindings before submission.
- Keep workflow templates user-selected/imported and project-local; do not silently install custom nodes or download checkpoints.

### M7l-b — Safe local reference handoff

- Resolve reference assets only from the selected project's validated character profile and canonical project-relative asset paths.
- Verify ownership, SHA-256, image format, dimensions, and full decode before use.
- Transfer approved references only to the configured loopback ComfyUI server using its documented local upload endpoint; never upload to cloud services.
- Use collision-safe names and reject path traversal, symlinks, oversized payloads, redirects, and overwrite attempts.
- Preserve source references unchanged. Any ComfyUI-side copy is a derived working input, not a replacement for the canonical reference.

### M7l-c — Identity-bound workflow execution

- Build each shot request from the exact immutable character revision bound to that storyboard shot.
- Inject the compiled positive/negative prompts, supported seed, and approved reference inputs through explicit workflow bindings.
- Record identity fingerprint, character revision, consistency key, workflow-template version, selected model/checkpoint metadata when available, and actual provider settings with the job result.
- Fail closed if the workflow cannot apply all required identity controls; never label prompt-only generation as reference-conditioned.
- Keep job cancellation, bounded polling, error sanitization, and project-local output persistence.

### M7l-d — UI, quality review, and acceptance

- Show capability readiness and the exact conditioning method before the user submits a job.
- Preview the bound character/reference and shot context; require explicit confirmation before generation.
- Preserve the existing Character Creator and Storyboard data formats and old bridge methods.
- Provide output review against the canonical reference and a regenerate-only-failed-shot path.
- Add EN/MY strings and desktop-only runtime status; browser preview must remain honest that it cannot access loopback services.

## Security and compatibility invariants

- Loopback-only ComfyUI; bypass proxies and reject redirects.
- No cloud provider, remote endpoint, API key, model download, custom-node installation, or automatic runtime reconfiguration.
- No changes to Bionic, Qwen2.5 model files, ComfyUI installation, checkpoints, or existing endpoint settings.
- Never mutate canonical character profiles or reference files during generation.
- Preserve project isolation and use the selected project's workspace APIs only.
- Bound JSON, image bytes, dimensions, node counts, workflow size, timeouts, and polling duration.
- Treat workflow JSON as untrusted input; validate node IDs, class types, input references, and all binding targets before POST.
- No claim of perfect identity consistency; reference conditioning improves repeatability but must be evaluated against actual local outputs.

## Acceptance evidence

- Unit tests for capability parsing, unsupported-node behavior, binding ambiguity, prompt/negative/seed injection, reference ownership and integrity, path traversal, symlink rejection, size limits, collisions, timeout, redirects, malformed ComfyUI responses, and failure recovery.
- Contract tests use fake local HTTP servers; CI must not launch GPU inference or download models.
- Existing Python, Ruff, JavaScript, Node, Windows project-lock, and packaging checks remain green.
- Manual acceptance on the user's Windows laptop must verify the installed ComfyUI node set, chosen checkpoint, actual reference upload, workflow submission, output retrieval, identity drift, and restart recovery. CI success alone is not local runtime acceptance.
