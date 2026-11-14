# M7g — Durable Character Revisions and Concurrency-Safe Local Persistence

## Scope
- Add a project-scoped cross-process lock, backed by OS file locking (POSIX flock and Windows msvcrt), plus a process-local thread lock.
- Add content-hash compare-and-swap (CAS) for versioned project documents while preserving the existing unversioned bridge methods for older clients.
- Add an append-only, project-local character revision ledger containing validated profile snapshots, full-profile checksums, and visual identity fingerprints.
- Migrate existing .character.json profiles to revision 1 on first desktop load without changing the profile schema or .stilla-character.json bundle format.
- Treat the ledger as authoritative and recover the current .character.json compatibility mirror when it is missing or matches an older ledger revision.
- Preserve revision history with a deletion tombstone; deleted character IDs cannot be reused.
- Connect the desktop Character Creator and Storyboard UI to durable revision tokens and document CAS.
- Keep browser-only mode on its existing project-scoped localStorage behavior.

## Integrity and safety
- All character and document mutations are serialized by the selected project's lock.
- CAS rejects stale desktop saves rather than silently overwriting newer edits.
- Revision snapshots are immutable and bounded to 100 revisions / 20 MiB per character ledger; limits fail closed without pruning history.
- Corrupt ledgers and unrecognized profile divergence are not overwritten. Existing data is preserved for recovery.
- Writes use same-directory temporary files, fsync and atomic replacement; parent-directory sync is attempted where supported.
- The legacy current-profile JSON remains a mirror for compatibility; the revision ledger is the authoritative history.
- No browser-supplied filesystem paths, shell access, external media transfer, cloud API, model download, or runtime reconfiguration is added.

## Known limitations
- The ledger and current-profile mirror are separate files. Ledger-first ordering plus recovery prevents silent history loss, but this is not a general multi-file transaction journal.
- Native reference import and profile revision save are still separate user actions. A stale-save conflict after importing an image can leave an orphaned image; safe asset garbage collection / transactional reference attachment remains follow-up work.
- Revision conflict feedback currently tells the user to reload; there is no automatic three-way merge.
- A dedicated Windows GitHub Actions job exercises msvcrt locking and project persistence. The user's own Windows laptop still requires acceptance because hosted CI does not verify the installed PyWebView runtime, native dialogs, filesystem policy, or local GPU environment.
- No ComfyUI reference conditioning, image preview pipeline, Windows installer, or native phone app is included.

## Acceptance gates
- Unit tests cover immutable revisions, legacy migration, stale-write rejection, ledger corruption, interrupted mirror recovery, tombstones, project isolation, document CAS, and concurrent writers.
- A multiprocessing test verifies that independent processes cannot enter the same project critical section simultaneously.
- Python tests, Ruff, JavaScript syntax checks, browser-state regression tests, GitHub Actions CI, and Vercel Preview must pass.
- Manual Windows acceptance must verify two-project isolation, two-window conflict handling, restart recovery, image import, Burmese UI rendering, and no external media transfer.
