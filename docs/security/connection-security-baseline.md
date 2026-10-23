# Connection and Security Baseline

- Status: implementation baseline for M1; must be extended before exposing remote providers or importing third-party engines.
- Scope: STILLA desktop process and the local OpenAI-compatible endpoint used by Bionic.
- Security posture: local-only provider transport; deny by default when host or response behavior is unexpected.

## Trust boundaries

1. **UI → application core:** UI input is untrusted. Validate project paths, media metadata, prompt sizes, and export destinations in the core, not only in UI controls.
2. **Application core → local provider:** The current transport only accepts loopback hosts, applies request/response size limits, uses a finite timeout, rejects redirects, and avoids printing raw exception strings or response bodies.
3. **Application core → media tools / model runtimes:** Future subprocesses must use argument arrays (never shell interpolation), fixed executable allowlists, controlled working directories, timeouts, cancellation, and bounded logs.
4. **Project files and imported media:** Treat project JSON, subtitle files, metadata, prompts, and downloaded assets as untrusted input. Avoid arbitrary path resolution, archive traversal, and automatic execution of embedded workflows.
5. **Optional remote services:** Not implemented by the local client. Remote services require a separate provider, explicit user opt-in, visible Local/Remote state, TLS, secret storage, data disclosure, and tests for redirect/credential handling.

## M1 transport safeguards implemented

- Local transport only permits loopback hostnames/IPs, even if the configuration parser can represent an HTTPS URL.
- No redirect following; redirect responses are an explicit error.
- Finite request timeout inherited from validated configuration.
- Request body limited to 256 KiB; response body limited to 1 MiB.
- JSON object responses only; invalid JSON and unexpected shapes fail closed.
- Errors do not include raw URLs, provider response bodies, or raw transport exception messages.
- No API key or credential is added by default. Never log prompts or model output by default.

## Required before production

- Add property-based/fuzz tests for URL parsing, project schemas, subtitle import, and path handling.
- Implement safe project storage: atomic writes, versioned schema/migrations, recovery snapshots, and path traversal protections.
- Define a permission/capability model before adding plugins, arbitrary workflows, remote execution, or shell tools.
- Use OS credential storage if/when remote API keys are supported; never store keys in project files, source control, or plain-text logs.
- Pin and audit dependencies; generate an SBOM and scan licenses/vulnerabilities before bundling.
- Test on Windows with Bionic running/stopped, timeout, malformed response, large output, cancellation, and crash recovery.
- Add integration tests against a fake local HTTP server and a manual smoke test against the user's existing Bionic endpoint. Do not run or alter Bionic automatically.
- Require CI, security review, and explicit merge gating for each PR; never start the next PR until the current PR is merged.

## Out of scope

This baseline does not claim end-to-end production security, image/video generation, a safe plugin sandbox, or secure remote-provider support. The app is not production-ready until the required controls have evidence.
