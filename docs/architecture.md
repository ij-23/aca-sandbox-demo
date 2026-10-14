# Application architecture and current implementation

> **Current execution authorization (2026-10-14):** Project-scoped Sandbox tests/cleanup, Terraform apply, Azure deployment and GitHub publishing are authorized autonomously under [AGENTS.md](../AGENTS.md#project-execution-authorization--2026-10-14). Recurring approval checkpoints below are superseded. Technical validation, product Fix confirmation, protection of unrelated resources and the prohibition on destructive operations remain.

The deployed host is one Azure Container App serving React static assets and a deterministic FastAPI API. The SDK creates disposable Copilot MicroVMs; all repository execution stays there. The remaining gates are same-PAT git push, full C dashboard publication, final persistence/telemetry checks, OIDC and complete replay/rehearsal.

| Layer | Implemented locally | Remaining live gate |
| --- | --- | --- |
| React dashboard | A/B/C lifecycle and event views, reports, diff, single remediation/publication confirmation, MSAL PKCE, bearer SSE reconnect; built assets and local empty-state browser checks pass | Entra sign-in and real A/B timelines pass; C publication and complete replay pending |
| FastAPI | Entra access-token validation, owner checks, request limits, repository allowlist, public SHA resolution, strict reports | Deployed secretless registrations and authorized fixture/user verified |
| Orchestrator | One-run admission, A/B concurrency, bounded execution, C approval binding, persisted run state, interruption handling | Real concurrent A/B and C failed-validation pass; successful publication pending |
| Blob | Managed-identity adapter, private artifacts, append JSONL before event delivery, cursor-based replay | UAMI access passes; append-history revalidation follows conditional-create correction |
| Sandbox runtime | M0-CLI97 genuine workflow, binding, upload/read/polling and exact-ID cleanup passed | A/B and C failed-validation executed genuinely; same-PAT git push403 |
| Terraform | Deployed 23-resource foundation and verified RBAC | App/Entra/telemetry deployed; per-create egress used; remote state/OIDC open |

The app never creates a fake successful run. By default `LIVE_EXECUTION_ENABLED=false`; a configured and verified executor is also required. Unit-test executors and in-memory stores exist only in test files. Replay must consume recorded genuine events and remain labeled prerecorded; no fixture currently claims a successful real run.

The [trusted source fixture](../demo-repo/README.md) is published at https://github.com/ij-23/academo-fastapi-fixture and executed only inside disposable Sandboxes. Its intentional document-path issue uses harmless temporary canaries in the regression tests. Platform tests/CI and the Docker build exclude fixture execution and packaging. A fixture test failure is an observed result only after a real Sandbox run, not because a local expectation predicts it.

Event delivery uses a bounded recent window (256 events per run, eight cached runs) and Blob history for older cursors. Each log has count and 15 MiB byte budgets, below the reader's 16 MiB cap. Restart reconciliation marks work interrupted and attempts cleanup of every relevant run even after an earlier failure. Individual unresolved cleanup records block new work; retries clear only the resolved record. These behaviors have local double-based coverage, not yet live managed-identity/storage verification.

## Storage/network decision

The user resolved the previous networking issue. On 2026-10-14 read-only checks returned publicNetworkAccess Enabled, defaultAction Allow, no private endpoints, public blobs/shared keys disabled and TLS1.2/HTTPS required. An anonymous request reached the Blob service and returned 409 (public access forbidden); operator OAuth listing was denied by data authorization. The app UAMI’s existing per-container grants were verified. Deployed-host UAMI data access passes. No networking, policy or RBAC change was made or is proposed to fix this again.

## Deployment ownership

Terraform remains the owner of static resources and image revisions. The original consumed foundation plan stays unchanged. Project image build/push, Entra/OIDC setup and app deployment use standing authorization. The user explicitly requires existing LOCAL Terraform state. GitHub Actions uses OIDC only for app image publication; the state-holding deployment machine applies inspected Terraform plans. No remote migration or ephemeral hosted-runner Terraform apply. No pipeline should independently run `az containerapp update` against Terraform's image field.
