# Fifteen-minute demo rehearsal plan

**Not rehearsed or timed yet.** Do not present this as a successful deployment. Complete M0, Azure auth/storage/egress, A/B/C and publication validation first. Use only a vetted fixture and a dedicated short-lived PAT/account.

| Time | Presenter action | Evidence to show |
| --- | --- | --- |
| 0–2 | “Give every AI agent its own isolated computer.” Explain host versus disposable MicroVMs and token tradeoff. | Architecture and explicit trusted-fixture limitation |
| 2–4 | Sign in using Entra on the Azure HTTPS app. Select the approved public fixture. | Authenticated identity; exact source URL |
| 4–5 | Start evaluation once. | Pinned SHA; different A/B sandbox IDs; real provisioning |
| 5–9 | Expand both workflow timelines and command output. | A static review, B build/tests/health, real conditional branches and captured exit codes |
| 9–11 | Read findings and validation report. | Verified versus unverified findings; skipped checks and limitations; no blanket safety claim |
| 11–13 | Select a verified finding and approve Fix Vulnerability once. | C timeline through fix, validate, publication gate, create, push, remote verification; private destination URL/SHA |
| 13–14 | Open the new private repository and inspect diff/commit. | Original unchanged; verified destination; all owned sandbox deletions |
| 14–15 | Explain customer deployment/manual credential checkpoints and production redesign. | Real timings, retained reports, short-lived PAT/account, cleanup |

Keep an actual successful A/B/C recording as fallback. The dashboard replay path requires stored sandbox-backed workflow evidence and labels playback **REPLAY · PRERECORDED**. It performs no sandbox or GitHub write. There is no fabricated replay fixture in this repository.

If authentication, validation, publication or cleanup fails, show that state and the actual evidence. Never imply that replay is live, that a partial repository publication succeeded, or that an unconfirmed delete completed.
