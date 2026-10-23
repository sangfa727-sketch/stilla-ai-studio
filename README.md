# STILLA AI Studio

A local-first AI video creation studio designed to turn an idea into a planned, generated, edited, and exported video while preserving user control over models, assets, and rendering.

## Project status

**Foundation stage — not production-ready.** The repository is being initialized with an architecture and safety-first development plan before generation engines are integrated.

## Design goals

- Keep the existing `Recapv1` repository unchanged; reuse only explicitly reviewed modules through documented interfaces.
- Connect to the existing Bionic OpenAI-compatible local API for Qwen text planning without moving, deleting, or reinstalling the model.
- Treat text planning, image generation, video generation, speech/audio, editing, and rendering as separate providers/workers.
- Make optional cloud providers opt-in; never require cloud credentials for local planning.
- Keep long-running jobs cancellable, resumable where safe, observable, and isolated from the UI process.
- Never commit secrets, model weights, user media, or generated outputs.
- Validate hardware capability before launching GPU-heavy work; target the current development PC (Windows, 16 GB RAM, RTX 3050 6 GB VRAM) without promising that every video model will fit.

## Planned workflow

1. Project brief and creative intent
2. Script and storyboard planning
3. Scene/shot list and asset requirements
4. Explicit provider/model selection and readiness checks
5. Image/video/voice generation as separate jobs
6. Timeline assembly, subtitles, audio mix, and rendering
7. Preview, quality checks, and export

## Initial architecture direction

- `apps/desktop/`: user interface and job orchestration entry point (final framework to be selected after a short architecture spike).
- `stilla/ai/`: provider contracts and local OpenAI-compatible client.
- `stilla/planning/`: project brief, script, storyboard, and shot-plan schemas.
- `stilla/jobs/`: job lifecycle, cancellation, progress, and persistence contracts.
- `stilla/media/`: media metadata, paths, and workspace boundaries.
- `stilla/render/`: FFmpeg integration boundary; no unreviewed direct coupling to Recapv1 internals.
- `tests/`: unit and contract tests, with fake providers for CI.
- `docs/`: architecture decisions, hardware constraints, security, and integration audit.

The exact runtime layout may be adjusted by the first architecture PR after checking Windows compatibility and dependency constraints.

## Local Qwen endpoint

Default base URL: `http://127.0.0.1:1234/v1`

The application should discover compatible models through `GET /models` and use the selected model returned by the local server rather than hard-coding one model identifier. Requests must fail with a clear diagnostic if Bionic is not running. Do not log prompts or credentials by default.

## Development principles

- One focused PR at a time; verify CI before merge.
- No generated model downloads or GPU-heavy inference in CI.
- Mock external providers in automated tests.
- Pin and review dependencies; document licenses before adopting third-party code.
- Never claim a generation provider works until a real local smoke test passes.

## Roadmap

- [ ] M0: Repository foundation, architecture decision, security boundaries, CI checks.
- [ ] M1: Local Qwen provider adapter and contract tests.
- [ ] M2: Project brief, script, storyboard, and shot-plan data models.
- [ ] M3: Job lifecycle and local project workspace.
- [ ] M4: Generation-provider interface and capability diagnostics.
- [ ] M5: First supported image-generation workflow.
- [ ] M6: Video-generation engine evaluation and hardware-bounded prototype.
- [ ] M7: Timeline composition, FFmpeg render, and export.
- [ ] M8: End-to-end Windows smoke tests and packaging.

## License

No license has been selected yet. Do not assume this repository or any future third-party integration is licensed for redistribution until a license review is completed.
