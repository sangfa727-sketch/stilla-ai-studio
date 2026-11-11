# M7 — Character Creator and Consistency Engine

## Product intent

Create original reusable cartoon characters once, preserve their visual identity across storyboards and clips, and let the user select characters instead of manually writing character-lock prompts.

## Character DNA

A versioned profile records:
- silhouette and body proportions;
- face shape, eyes, nose, mouth, head/hair shape and surface details;
- canonical color palette, outfit, accessories and distinguishing marks;
- original art direction;
- personality traits, comic flaw, humor mechanics, speech pattern, reaction style,
  relationship dynamics and recurring gag;
- canonical reference images with project-relative paths and optional SHA-256 checksums;
- voice description and language.

The profile is the source of truth. Pose, expression and scene action are variable shot-level controls; visual anchors remain locked unless the user explicitly approves a costume/design variation.

## Consistency recipe

For every shot, the application compiles the saved profile into positive and negative conditioning automatically. It carries the same reference images, identity fingerprint and generation metadata into each compatible provider request. The identity fingerprint is deterministic over canonical visual identity and reference metadata. A separate per-shot consistency key identifies the exact scene plan.

A fixed seed is advisory only: seeds do not guarantee identical appearance across different models, samplers, versions, resolutions or scene compositions. Stronger consistency requires reference-conditioned generation (e.g. supported image-to-image, character-reference/IP-Adapter or equivalent controls), plus a selected model/provider that exposes those capabilities. Video workflows must also preserve the approved character reference at shot and clip boundaries. The engine must report unsupported conditioning rather than silently pretending the character is locked.

No diffusion workflow can promise mathematically perfect identity in every frame. Acceptance must be measured against approved reference sheets and real local runtime tests.

## Original comedy system

Comedy is authored from reusable behavior mechanics (misunderstanding, overconfidence, deadpan timing, harmless slapstick, delayed reaction, playful rivalry, visual callbacks and running gags), combined with a character's own strengths, flaws, speech pattern and relationships. Do not copy Minions' visual design, names, signature language, costume or recognizable behavior. Build a distinct original cast.

## Delivery sequence

1. **M7a — Character DNA core:** validated profile, safe persistence, deterministic identity fingerprint, automatic prompt compiler and unit tests.
2. **M7b — Character Creator UI:** character library, guided creation form, reference image import, character sheet review, edit/version history and one-click reuse.
3. **M7c — Story integration:** select characters in brief/storyboard; auto-bind profiles to every shot; show missing references or unsupported provider controls.
4. **M7d — Image/video provider integration:** provider capability negotiation, reference conditioning, seed/settings provenance and local GPU acceptance tests.
5. **M7e — Quality gate:** reference-sheet comparison, face/body/palette/costume drift review, per-shot approval and regenerate-only-failed-shot workflow.

## Safety and compatibility boundaries

- No model downloads, provider installation or GPU inference in CI.
- Do not change the existing Bionic/Qwen endpoint, model files or runtime configuration.
- Do not transmit reference images or prompts to cloud providers unless the user explicitly selects and approves that provider.
- Keep reference paths project-relative; reject traversal and symlink targets.
- Preserve previous character profile files if a write fails.
- Keep visual identity immutable by default; variations require an explicit user action.
- Do not claim production character consistency until the real provider's reference-conditioning path passes local end-to-end tests.
