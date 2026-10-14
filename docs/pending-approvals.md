# External dependencies and standing authorization

Updated 2026-10-14. [AGENTS.md](../AGENTS.md#project-execution-authorization--2026-10-14) authorizes autonomous project-scoped Sandbox tests and cleanup, Terraform apply, Azure deployment and GitHub publication. Routine operations do not require another chat approval. Inspect exact targets/plans, preserve unrelated resources and reject destructive changes.

## Remaining customer choice

The installed [terraform-builder skill](/Users/ij/.agents/skills/terraform-builder/SKILL.md) says: “Add backend.tf and remote state configuration (Azure Storage backend) only when the user explicitly requests remote state.” A choice between remote state for Actions and the local-state/manual deployment path is pending. Current local state is preserved; no ephemeral Actions apply is permitted.

The Sandbox Group PAT personal owner is verified as ij-23 through a genuine credential workflow. Private test repository creation passed, but git push returned403; the user must verify Contents write and access to future repositories, then manually update the group token if needed. Never paste the PAT into chat. The signed-in GitHub CLI account is `ij-23`; its OAuth credential publishes only the project/input fixture. C must use the existing group PAT.

## Verified and ongoing work

- M0-CLI97: passed genuine workflow/auth/polling and exact-ID cleanup.
- M0-C-FAIL: passed genuine AI fix, actual pytest failure and skipped publication, exact-ID cleanup.
- Public vetted input: https://github.com/ij-23/academo-fastapi-fixture at immutable SHA `c1c3d2bcd0f33eddfd77d29249c3a04c0130da1e`.
- Entra registrations, telemetry DCE/DCR/UAMI/table and Azure application are Terraform-deployed. Live A/B execution is enabled; publication remains disabled.
- A real container stdout probe arrived in the existing LAW through telemetryConfig; A/B/C correlated ingestion remains to be verified.
- C same-PAT extension access and private creation pass; git push, full deployed A/B/C, replay and rehearsal remain open.

## Boundaries that remain

No static-resource destruction/replacement, credential change, repository deletion/overwrite, unrelated resource change or source-repository mutation. The pre-existing stopped Sandbox is protected. Owned disposable Sandbox cleanup is authorized and mandatory, including after failure. Each app remediation still requires the single Fix Vulnerability confirmation; the agent may exercise it during E2E. There is no second Publish confirmation.

## Current completion blockers

1. Same-PAT GitHub push403. Verify Contents read/write and All repositories/future repositories on the personal-account fine-grained token. Update group credential manually only if needed; do not provide its value. Retry only the exact owned empty test repository, then complete C.
2. Azure Blob remote-state choice is pending. Platform CI passes, but OIDC Terraform deployment must not run with ephemeral/local runner state. Current manually deployed state stays protected.
3. Existing Edge window is unavailable to automation (cgWindowNotFound). Resume remaining authenticated dashboard reconnect, C and full replay/rehearsal checks when the window is accessible. No browser credential extraction is used.

Proposed remote-state scope for the customer choice: a private state container in the existing project Storage Account, Entra/OIDC authentication with container-scoped state access, and migration of the protected local state under Terraform’s state lock. No shared keys, public state or Actions state artifacts. The GitHub deploy identity and its project resource/directory scopes must then be inspected before grants; the workflow must first produce a no-destructive-change plan. This remains prepared, not configured.
