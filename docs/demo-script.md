# Fifteen-minute demo rehearsal plan

**Technical walkthrough verified on 2026-10-14; final timed presenter rehearsal remains open.** The authenticated Azure A/B/C path ran successfully: A/B27s, C35.5s, complete recorded wall time4m33s including the gap before Fix. The labelled95-event replay completed at1x. Use only a vetted fixture and a dedicated short-lived PAT/account.

| Time | Presenter action | Evidence to show |
| --- | --- | --- |
| 0–2 | “Give every AI agent its own isolated computer.” Explain host versus disposable MicroVMs and token tradeoff. | Architecture and explicit trusted-fixture limitation |
| 2–4 | Sign in using Entra on the Azure HTTPS app. Select the approved public fixture. | Authenticated identity; exact source URL |
| 4–5 | Start evaluation once. | Pinned SHA; different A/B sandbox IDs; real provisioning |
| 5–9 | Expand both workflow timelines and command output. | A static review, B build/tests/health, real conditional branches and captured exit codes |
| 9–11 | Read findings and validation report. | Verified versus unverified findings; skipped checks and limitations; no blanket safety claim |
| 11–13 | Select a verified finding and approve Fix Vulnerability once. | C timeline through fix, validate, publication gate, create, push, remote verification; private destination URL/SHA |
| 13–14 | Open the new private repository and inspect diff/commit. | Original unchanged; verified destination; stopped/retained Sandbox IDs; optional explicit Clean up |
| 14–15 | Explain customer deployment/manual credential checkpoints and production redesign. | Real timings, retained reports, short-lived PAT/account, cleanup |

Keep an actual successful A/B/C recording as fallback. The dashboard replay path requires stored sandbox-backed workflow evidence and labels playback **REPLAY · PRERECORDED**. It performs no sandbox or GitHub write. The [real event fixture](../fixtures/README.md) records the successful run.

If authentication, validation, publication or cleanup fails, show that state and the actual evidence. Never imply that replay is live, that a partial repository publication succeeded, or that an unconfirmed delete completed.

## Before repeating a live publication

The successful destination `ij-23/academo-fastapi-fixture-fixed` now exists and must be preserved. Re-running C on that source must report a name collision, never overwrite or delete it. For a fresh live publication, prepare a newly named public copy of the vetted fixture and explicitly allowlist it in the application; its corresponding `{repo}-fixed` must be absent. This requires a scoped configuration update, not a new credential. Otherwise use the clearly labelled genuine replay and inspect the existing verified destination.

## Evidence from the walkthrough

- Real Entra-authenticated Start; concurrent A/B same source SHA. A source verification passed; B showed the expected2 failing regressions.
- One visible Fix/private-publication confirmation; C AI step observed running, then validation/gate/create/push/verify/deleted.4 tests and2 targeted tests passed.
- Dashboard diff and verified private link inspected. Original SHA unchanged.95 private Blob events/three reports/diff verified.
- Replay played all95 events without new Sandboxes; all owned IDs independently404.
- Exact1080p viewport, final browser reconnect/cancellation checks and uninterrupted15-minute presenter rehearsal are not yet claimed. Deployed-runtime cancellation/interruption recovery at genuine A/B step boundaries passed separately; see the [acceptance matrix](./acceptance.md).
