# M0 Foundation — Acceptance Criteria

M0 is complete only when all applicable checks have evidence.

- [ ] Repository purpose, scope, and non-goals are documented.
- [ ] Architecture decision records local-first boundaries and Recapv1 separation.
- [ ] Secrets, model weights, and user media are excluded from version control.
- [ ] Python tooling and CI run deterministic, GPU-free checks.
- [ ] Provider configuration validates local endpoint URLs and reports connection errors without leaking secrets.
- [ ] No external model download, paid API requirement, or destructive local setup step is introduced.
- [ ] Windows compatibility assumptions and target hardware constraints are documented.
- [ ] Dependency and third-party license review is recorded before adoption.
- [ ] CI status is green before merge.

M0 does not claim image/video generation, FFmpeg integration, packaging, or end-to-end production readiness.
