# Application architecture and current implementation

The target is one Azure Container App serving React static assets and a deterministic FastAPI API. The SDK creates disposable Copilot MicroVMs; all repository execution stays there. This document distinguishes implemented local contracts from unverified cloud behavior.

| Layer | Implemented locally | Remaining live gate |
| --- | --- | --- |
| React dashboard | A/B/C lifecycle and event views, reports, diff, single remediation/publication confirmation, MSAL PKCE, bearer SSE reconnect; built assets and local empty-state browser checks pass | Azure sign-in; 1080p live-data exercise; genuine run/replay |
| FastAPI | Entra access-token validation, owner checks, request limits, repository allowlist, public SHA resolution, strict reports | Customer app registrations/consent, allowed identities/fixtures |
| Orchestrator | One-run admission, A/B concurrency, bounded execution, C approval binding, persisted run state, interruption handling | SDK adapter implemented; real concurrent A/B and C remain untested |
| Blob | Managed-identity adapter, private artifacts, append JSONL before event delivery, cursor-based replay | Networking reachable; deployed-host UAMI data access still untested |
| Sandbox runtime | M0-CLI97 genuine workflow, binding, upload/read/polling and exact-ID cleanup passed | Prepared A/B/C workflow extensions require real integration tests |
| Terraform | Deployed 23-resource foundation and verified RBAC | Optional app module validates; Entra, group limits/egress, state/OIDC and approved deployment remain |

The app never creates a fake successful run. By default `LIVE_EXECUTION_ENABLED=false`; a configured and verified executor is also required. Unit-test executors and in-memory stores exist only in test files. Replay must consume recorded genuine events and remain labeled prerecorded; no fixture currently claims a successful real run.

The [trusted source fixture](../demo-repo/README.md) is authored but not executed or published. Its intentional document-path issue uses harmless temporary canaries in the regression tests. Platform tests/CI and the Docker build exclude fixture execution and packaging. A fixture test failure is an observed result only after a real Sandbox run, not because a local expectation predicts it.

Event delivery uses a bounded recent window (256 events per run, eight cached runs) and Blob history for older cursors. Each log has count and 15 MiB byte budgets, below the reader's 16 MiB cap. Restart reconciliation marks work interrupted and attempts cleanup of every relevant run even after an earlier failure. Individual unresolved cleanup records block new work; retries clear only the resolved record. These behaviors have local double-based coverage, not yet live managed-identity/storage verification.

## Storage/network decision

The user resolved the previous networking issue. On 2026-10-14 read-only checks returned publicNetworkAccess Enabled, defaultAction Allow, no private endpoints, public blobs/shared keys disabled and TLS1.2/HTTPS required. An anonymous request reached the Blob service and returned 409 (public access forbidden); operator OAuth listing was denied by data authorization. The app UAMI’s existing per-container grants were verified. Runtime data access still needs the deployed host. No networking, policy or RBAC change was made or is proposed to fix this again.

## Deployment ownership

Terraform remains the owner of static resources and image revisions. The original consumed foundation plan stays unchanged. Image build/push, Entra/OIDC setup, state migration and app deployment require concrete external approvals. GitHub Actions must not apply with ephemeral untracked local state; a durable backend needs an explicit customer decision. No pipeline should independently run `az containerapp update` against Terraform's image field.
