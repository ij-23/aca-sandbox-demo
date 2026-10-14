# Application architecture and current implementation

## Public-repository branch (in progress)

The [adopted expansion](./public-repository-plan.md) separates credential-bearing
Copilot coordinators from workers and a future independent publisher. Optional
Terraform groups now exist: `sbg-academo-a3dcd3b3-workers` has no identity/provider
credential; `sbg-academo-a3dcd3b3-analysis` has the telemetry identity and awaits a
manual Copilot-only credential. Existing fixture groups/runs remain unchanged.
Live probes verified denied worker identity requests versus successful responses
in the old identity-bearing group, genuine file-mediated workflow delegation,
and bounded static inventory of two public projects. These are limited proofs,
not full arbitrary-code or publishing acceptance.

The feature branch adds authenticated metadata-only lookup at
`POST /api/repositories/inspect`, with bounded GitHub responses, fixed URLs/no
redirects, immutable SHA/repository ID and a global ten-second lookup cooldown.
It performs no source execution or Sandbox creation. New run policy names are
explicit; public analysis/execution requests remain blocked before the old
credential-bearing executor. Source acquisition/parsing lives only in the
worker helper. Delegation/publication contracts are preparation, not a deployed
publisher. [Credential setup and remaining work](./public-repository-setup.md).

## Deployed trusted-fixture architecture

> **Current execution authorization (2026-10-14):** Project-scoped Sandbox tests/cleanup, Terraform apply, Azure deployment and GitHub publishing are authorized autonomously under [AGENTS.md](../AGENTS.md#project-execution-authorization--2026-10-14). Recurring approval checkpoints below are superseded. Technical validation, product Fix confirmation, protection of unrelated resources and the prohibition on destructive operations remain.

The deployed host is one Azure Container App serving React static assets and a deterministic FastAPI API. The SDK creates disposable Copilot MicroVMs; all repository execution stays there. Successful C publication, all-role telemetry and private replay are verified. Remaining gates are authenticated transport drills and customer-install/rehearsal verification.

| Layer | Verified implementation | Remaining live gate |
| --- | --- | --- |
| Browser/auth | Entra PKCE, authenticated A/B/C, private URL/diff, complete labelled replay | Explicit SSE transport drill, final viewport/rehearsal |
| Orchestrator | Concurrent A/B, single Fix consent, C validation/private push, runtime cancellation/reconciliation | Runtime timestamp fix verified; HTTP-process failure/browser transport drill |
| Blob | UAMI read-back of 95 contiguous events, three reports/diff, actual replay, deleted ownership | Customer-install verification |
| Sandbox runtime | Built-in disk, genuine CLI1.0.97 workflows, bounded polling, all-role LAW ingestion, exact404 cleanup | No remaining core workflow capability blocker |
| Terraform/release | Foundation/app/Entra/telemetry and least-scope OIDC image release; local-state image apply | Separate clean-customer install |

The app never creates a fake successful run. By default `LIVE_EXECUTION_ENABLED=false`; a configured and verified executor is also required. Unit-test executors and in-memory stores exist only in test files. Replay must consume recorded genuine events and remain labeled prerecorded; the captured fixture contains a verified successful A/B/C run.

The [trusted source fixture](../demo-repo/README.md) is published at https://github.com/ij-23/academo-fastapi-fixture and executed only inside disposable Sandboxes. Its intentional document-path issue uses harmless temporary canaries in the regression tests. Platform tests/CI and the Docker build exclude fixture execution and packaging. A fixture test failure is an observed result only after a real Sandbox run, not because a local expectation predicts it.

Event delivery uses a bounded recent window (256 events per run, eight cached runs) and Blob history for older cursors. Each log has count and 15 MiB byte budgets, below the reader's 16 MiB cap. Restart reconciliation marks work interrupted and attempts cleanup of every relevant run even after an earlier failure. Individual unresolved cleanup records block new work; retries clear only the resolved record. Unit tests cover these edge cases; deployed UAMI persistence and actual A/B cancellation/interruption recovery also passed. An explicit authenticated SSE cursor transport drill remains open in [acceptance](./acceptance.md).

## Storage/network decision

The user resolved the previous networking issue. On 2026-10-14 read-only checks returned publicNetworkAccess Enabled, defaultAction Allow, no private endpoints, public blobs/shared keys disabled and TLS1.2/HTTPS required. An anonymous request reached the Blob service and returned 409 (public access forbidden); operator OAuth listing was denied by data authorization. The app UAMI’s existing per-container grants were verified. Deployed-host UAMI data access passes. No networking, policy or RBAC change was made or is proposed to fix this again.

## Deployment ownership

Terraform remains the owner of static resources and image revisions. The original consumed foundation plan stays unchanged. Project image build/push, Entra/OIDC setup and app deployment use standing authorization. The user explicitly requires existing LOCAL Terraform state. GitHub Actions uses OIDC only for app image publication; the state-holding deployment machine applies inspected Terraform plans. No remote migration or ephemeral hosted-runner Terraform apply. No pipeline should independently run `az containerapp update` against Terraform's image field.
