# M7l — ComfyUI Character Identity Conditioning

## Objective

Connect the existing, version-pinned STILLA character identity and storyboard shot bindings to the user's already-installed local ComfyUI instance. The same approved character reference must be reused across shots without modifying the original reference asset or silently changing the saved character profile.

This milestone is an integration boundary, not a promise of pixel-identical output. Diffusion identity consistency is probabilistic and depends on the installed checkpoint, VAE, sampler, custom nodes, reference quality, and workflow parameters.

## Baseline verified in the repository

- Character profiles have deterministic visual identity fingerprints and project-relative reference records.
- Storyboard shots pin exact character profile revisions and fingerprints.
- The consistency compiler separates immutable visual anchors from scene pose/expression.
- ComfyUI configuration is restricted to plain HTTP loopback.
- The local ComfyUI client validates bounded workflow JSON, submits only caller-supplied workflows, and reads history.
- Generated image retrieval validates the returned file reference, media type, byte limit, project boundary, and refuses overwrite.
- Read-only ComfyUI diagnostics already query `/system_stats` and `/object_info`; they do not submit a workflow.

## Delivery gates

### M7l-A — Installed-node capability discovery (first implementation slice)

1. Extend read-only `/object_info` inspection to identify candidate reference-conditioning nodes by exact installed class names and their input schemas.
2. Treat node discovery as evidence only. Do not report conditioning as ready based only on a familiar class name.
3. Return a bounded, sanitized capability report with:
   - detected ComfyUI version when available;
   - candidate node class names and required input names;
   - missing capability groups;
   - explicit status: `available`, `partial`, or `unsupported`.
4. Never query arbitrary hosts, follow redirects, submit prompts, or download/install nodes or models.
5. Add tests for absent nodes, renamed/custom nodes, malformed schemas, oversized catalogs, and unavailable ComfyUI.

### M7l-B — Identity-safe workflow compiler

1. Compile a selected storyboard shot only from its pinned character revision and matching identity fingerprint.
2. Resolve each reference through the project's validated asset registry; verify the file remains within the project, is not a symlink, decodes as a supported image, and matches its stored SHA-256 when present.
3. Preserve the source reference byte-for-byte. Any resized/cropped conditioning derivative must be a new generated asset with provenance; never overwrite the canonical reference.
4. Separate locked identity anchors from shot-variable pose, expression, camera, and scene instructions.
5. Use only installed, explicitly supported conditioning node contracts. Do not guess node IDs, socket names, model paths, or custom-node versions.
6. Refuse compilation when the bound revision is stale, references are missing/corrupt, required nodes are absent, or required model inputs cannot be verified.

### M7l-C — Explicit local generation lifecycle

1. Show the exact character revision, reference assets, detected conditioning method, checkpoint/model identifiers, resolution, seed, and workflow summary before submission.
2. Require a direct user action to submit a workflow. No automatic generation on project open, character save, or health-check.
3. Use the existing loopback-only ComfyUI client and bounded job/history lifecycle.
4. Persist prompt ID, workflow fingerprint, character identity fingerprint, revision, input reference hashes, and output asset provenance.
5. Save generated images as new project assets. Never replace character references or prior generated outputs.
6. Cancellation, timeout, server restart, and partial history must produce an honest recoverable job state; never mark a job complete without a validated output image.

### M7l-D — Quality review and physical acceptance

1. Present generated output beside the canonical reference sheet for human review.
2. Keep per-shot approval separate from generation success.
3. Permit regenerate-only-this-shot without changing approved shots or character identity.
4. Validate the real installed ComfyUI node pack, checkpoint, reference conditioning, and output on the user's Windows laptop.
5. Record hardware use and failure behavior on the RTX 3050 6 GB / 16 GB RAM target; do not promise that every workflow fits in VRAM.
6. CI uses fake local HTTP servers and fixtures only. No GPU inference, model download, or cloud media upload in CI.

## Security and compatibility invariants

- Keep the existing Bionic/Qwen endpoint, model ID, model files, and runtime settings unchanged.
- Keep ComfyUI local at the user's existing loopback endpoint; do not install, update, or reconfigure ComfyUI or custom nodes.
- Do not introduce cloud providers or remote image transfer.
- Keep prompts, local file paths, and reference images out of logs and telemetry.
- Bound workflow JSON, catalog size, image bytes, request timeouts, and output count.
- Reject path traversal, symlinks, unsafe image references, untrusted workflow structures, redirects, and non-loopback endpoints.
- Do not silently fall back to text-only prompting when identity conditioning is unavailable. Report the exact missing capability and stop.
- Preserve existing character profiles, immutable revision history, storyboard bindings, and legacy bridge behavior.

## Acceptance criteria

M7l is not complete until:
- automated tests prove revision/fingerprint pinning and fail-closed behavior;
- fake-server contract tests prove no request escapes loopback and no submission occurs during diagnostics;
- generated assets are new, verified, and never overwrite canonical references;
- the user explicitly approves each real generation submission;
- a real Windows laptop run demonstrates that the installed ComfyUI workflow uses the same canonical reference across at least two distinct scenes and outputs are reviewable beside the reference;
- known limitations and hardware measurements are documented.

CI Green is necessary but does not replace the physical laptop acceptance above.
