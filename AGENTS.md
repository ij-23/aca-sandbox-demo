# AGENTS.md — From Untrusted Code to Trusted Decisions

> Binding implementation instructions for the VS Code coding agent. Read **this entire file** and `README.md` before editing. Implement a reproducible, customer-deployable, **fully Azure-hosted** open-source demo. Track progress in `docs/progress.md`.

## 0. Outcome / non-negotiable scope

Build a polished **15-minute live demo** where an authenticated user submits a public GitHub repository URL; a deterministic FastAPI orchestrator creates **two ACA Sandboxes in parallel** using the **built-in GitHub Copilot disk/image** and executes **two genuine GitHub Copilot Dynamic Workflows** concurrently within those isolated MicroVMs. Results are streamed to a React observability dashboard. Upon a single explicit **Fix Vulnerability** approval, **Sandbox C executes a third genuine GitHub Copilot Dynamic Workflow** that patches the code, validates it, creates a new **private** GitHub repository named `{original-repo}-fixed`, commits/pushes the corrected source with the Sandbox Group Copilot PAT, and returns the new repository URL plus diff/tests. The original repository remains unchanged. There is no separate Publish button or backend GitHub publisher. Clean up all demo-created sandboxes. Provide a clearly marked replay mode recorded from a genuine successful run.

- **A / Security & Code Review Dynamic Workflow:** pinned clone, non-executing source inspection, optional actual SAST/secrets scans, Copilot review, conditional evidence verification, structured `review.json`.
- **B / Build & Validation Dynamic Workflow:** same pinned clone, Python/FastAPI discovery, bounded dependency installation and build, pytest, conditional localhost app launch/health and non-destructive runtime validation, structured `build.json`.
- **C / Remediation & GitHub Publication Dynamic Workflow:** after a single Fix Vulnerability confirmation, pinned clone, Copilot patch, tests, diff, new private `{repo}-fixed` repository created and pushed **inside C** using the existing Sandbox Group PAT; return `fixed_repository_url` in `remediation.json`. No additional Publish approval.

This is **not** a SaaS/multi-tenant platform; each customer deploys their own instance into their own subscription. No Foundry, Azure OpenAI, AKS, custom sandbox images, or arbitrary-language build support. The **application** may and should have its own container image in ACR; that is distinct from the **built-in Copilot sandbox image**, which MUST NOT be rebuilt.

## 1. Mandatory Terraform skill: `terraform-builder`

**All provisioning, modifying, importing or destroying Azure infrastructure with Terraform MUST be performed following the agent skill named exactly `terraform-builder`.** Before writing any `*.tf` files or applying infrastructure:

1. Discover the installed `terraform-builder` skill in the coding-agent environment (workspace/user/global skill locations supported by that agent).
2. Read its **complete `SKILL.md`** and follow any referenced mandatory templates, validation procedures and examples.
3. State in `docs/progress.md` where the skill was located and how its rules are being followed.
4. If the skill is unavailable, **stop Terraform authoring/provisioning** and ask the user to install or provide it. **Do not invent** its contents or substitute an unrelated skill without permission. Other application development can continue if it does not require infrastructure changes.
5. For Terraform itself, use verified provider schemas and versions; prefer `azurerm` for supported resources and `azapi` for preview sandbox-group resources when necessary. Verify Sandbox Group API details from official docs and provider runtime; no guessed fields, API versions or roles. All resources must be IaC-managed except documented intentional manual credentials setup.

## 2. Target architecture: everything on Azure

```text
Authenticated browser (Microsoft Entra ID)
     | HTTPS, REST, SSE
     v
Azure Container App (one public app, single replica for MVP)
     |-- built React/Vite static assets served by FastAPI
     |-- Python/FastAPI deterministic orchestrator (NO LLM in backend)
     |-- typed events, sanitized logs, results, replay mode
     |-- user-assigned managed identity (Azure access)
     |-- Azure Blob Storage: durable reports, event logs, diffs/replay
     |-- Application Insights / Log Analytics telemetry
     |
     | ACA Sandbox data-plane SDK (managed identity)
     v
ACA Sandbox Group (group-scope GitHub Copilot provider credential, configured MANUALLY)
     |-- A: built-in Copilot preset -> REAL security Dynamic Workflow
     |-- B: built-in Copilot preset -> REAL build Dynamic Workflow
     `-- C: built-in Copilot preset -> REAL remediation/publish Dynamic Workflow (after one Fix approval)

Azure Container Registry -- application image ONLY -> Azure Container App
GitHub Actions (Azure OIDC) -> build/push image, deploy revisions
Terraform (using terraform-builder skill) -> static resources and RBAC
```

**Never run user repository code in the Container App/backend, runner, local developer computer, or pipeline.** Only within purpose-created disposable sandboxes. Sandbox Group is a separate ARM resource and does not require an ACA Managed Environment; the **host application Container App does**.

### Static Azure resources (Terraform)

- Resource Group (can optionally support existing group via documented input).
- Azure Container Registry (ACR) for **application** image only.
- Log Analytics Workspace and an Azure Container Apps Managed Environment.
- **One** Azure Container App: public HTTPS ingress, React+FastAPI together, secrets-free configuration, probes, min replicas **1**, max replicas **1** for MVP; no scale-to-zero while executing in-process jobs. Azure platform restart can still interrupt jobs; document limits.
- **User Assigned Managed Identity** for app; `AcrPull` on ACR and `Container Apps SandboxGroup Data Owner` scoped to the Sandbox Group (verify real role and scope, avoid subscription-wide grants).
- Azure Storage Account + private blob container(s) for reports, logs/events, diffs and real-run replay; RBAC (e.g. Storage Blob Data Contributor) for app managed identity, no account keys in config. Use secure transport, minimum TLS, no public blob container.
- ACA Sandbox Group, supported region, quotas/limits, appropriate restricted egress policy **after verifying** GitHub Copilot/clone/dependency endpoints. Do not break auth by blindly deny-all. Group-level Copilot credentials MUST be configured **manually after Terraform creates group**.
- Microsoft Entra ID user authentication: support customer-owned tenant, authorized users only, Entra App Registration and authentication settings where deployment automation is supported/appropriate. App registration/consent might require a documented admin action; verify actual Terraform/API support. Block unauthenticated evaluate/remediate/cleanup requests in the backend and enforce identities/authorization server-side, not just UI. Prefer Azure Container Apps built-in auth where compatible and enforce identity in API; avoid unprotected public cost-incurring endpoints.
- Application Insights (recommended for published OSS sample; if included, verify and implement connection to LAW) with redacted request telemetry, correlation by run ID.
- Optionally GitHub Actions OIDC federated identity credentials and scoped deploy role assignments, when customer's tenant setup permits; document one-time trust/bootstrap. No long-lived Azure service principal secret.

No required VNet, Azure Firewall, Front Door, SQL, Cosmos, Event Hubs, Service Bus or Key Vault for MVP. Avoid implying that public HTTPS ingress alone constitutes sufficient access control.

**Terraform outputs:** `application_url`, `sandbox_group_name`, `resource_group_name`, `region`, `acr_login_server`, `managed_identity_client_id`, `storage_account_name`, and any required manual setup URLs/instructions. Do not output tokens.

## 3. Deployment model / customer reproducibility

Create `infrastructure/terraform/` with reusable modules or simple explicit resources, pinned providers, examples and inputs for region, names, tags, tenant/subscription, authorized users, image tag, sandbox group limits, retention and application auth.

Handle the **container image bootstrap cycle** correctly:
1. **Bootstrap Terraform:** establish RG, ACR, identities, storage, logging, Sandbox Group, required scopes. Do not require a yet-nonexistent final application image during bootstrap; choose a verified valid two-stage approach (separate app phase or documented bootstrap image).
2. **Build and push the app image** to ACR from GitHub Actions (or documented one-off bootstrap build) using workload-identity federation/OIDC.
3. **Finalize Terraform/application deployment** with the actual image digest/tag and Container App auth, environment/config, storage access, managed identity. Avoid Terraform and `az containerapp update` concurrently fighting over image state; choose a single documented owner for image revision updates.
4. **Manual GitHub Copilot PAT configuration** at Sandbox Group level through https://sandboxes.azure.com (details in `README.md`), after Sandbox Group creation. Never put it in `.tfvars`, Terraform state, GitHub secrets for the sandbox credential, Docker build arguments, Container App env or repository.
5. Verify login protection, backend identity/data-plane access, Copilot auth and real minimal Dynamic Workflow in a disposable sandbox; then test **all three authentic Dynamic Workflows** including C (with explicit authorization before any GitHub write).

The resulting public repository must document both a GitHub Actions CI/CD path and a manual Terraform/bootstrap path with precise, verified commands. The deployed application requires **no local app host** and serves its UI/API from Azure. Do not claim completely unattended install: Copilot credential setup (and potentially Entra consent) are manual checkpoints.

## 4. Essential technical validation: Milestone 0, blocking gate

ACA Sandbox APIs, built-in disk IDs and Copilot Dynamic Workflows evolve. Consult current official docs and installed tool versions first:

- https://learn.microsoft.com/en-us/azure/container-apps/sandboxes-quickstart-python-sdk
- https://learn.microsoft.com/en-us/azure/container-apps/sandboxes-overview
- https://learn.microsoft.com/en-us/azure/templates/microsoft.app/2026-07-01/sandboxgroups
- https://sandboxes.azure.com/docs/sandboxes/quickstart/setup-terraform
- https://staging.sandboxes.azure.com/docs/sandboxes/credentials
- https://github.blog/changelog/2026-10-01-dynamic-workflows-in-copilot-cli-and-the-copilot-app/
- Current GitHub Copilot CLI extension/Dynamic Workflow and authentication docs.

Write `docs/compatibility.md`: actual built-in Copilot disk identifier; concrete SDK calls; actual Workflow extension loading and noninteractive invocation; Copilot CLI version and possible experimental flags; real output capture/streaming limitations; required auth and egress; Terraform resource/provider schemas.

`smoke_test_sandbox.py` MUST create disposable sandbox with **built-in Copilot preset**, validate provider credentials without `/login`, invoke a **real minimal programmatic Dynamic Workflow** (not a prompt pretending to be one), collect result and delete in `finally`. Never invent CLI commands. If any gate fails, report exact blocker and STOP corresponding cloud feature development rather than silently substituting custom image or fake workflow.

## 5. Repo layout

```text
AGENTS.md
README.md
Dockerfile                 # multi-stage frontend build + Python app image
.github/workflows/ci.yml
.github/workflows/deploy.yml
infrastructure/terraform/  # ALL Terraform authored/applied per terraform-builder skill
frontend/                   # React + TypeScript + Vite
backend/app/                # FastAPI, orchestrator, SDK adapter, auth, event store, reports
backend/tests/
workflows/security-review/ # real instrumented Copilot Dynamic Workflow extension
workflows/build-validation/
workflows/remediation/     # REAL instrumented Copilot Dynamic Workflow extension
workflows/schemas/          # JSON report schemas
demo-repo/                  # reviewed FastAPI fixture (or linked public hosted fixture)
scripts/smoke_test_sandbox.py
scripts/verify_environment.py
scripts/cleanup_orphans.py
fixtures/replay-events.jsonl
 docs/architecture.md       # actual path should be docs/architecture.md
 docs/compatibility.md
 docs/deployment.md
 docs/security.md
 docs/demo-script.md
 docs/progress.md
```

No unnecessary microservices or always-running worker in MVP. One container app/replica; in-process orchestration with bounded concurrency. **Blob persistence is for durability of reports/events, not durable job execution**. On restart, mark interrupted jobs and perform tracked/orphan cleanup; do not claim automatic workflow recovery.

## 6. Backend, state, observability and API

- FastAPI orchestrator launches A+B concurrently with `asyncio`; use `asyncio.to_thread` for blocking SDK calls. C runs later only after explicit approval. One active run at a time by default; enforce global quota and per-step/run timeouts. Idempotent cleanup in success/failure/cancel/restart paths; delete only sandboxes recorded as owned by this app/run.
- Validate only public `https://github.com/{owner}/{repo}` URLs; safe SHA resolution and pinned checkout of **same immutable SHA**; SSRF guards, no command injection or unsafe URLs/protocols. Support Python/FastAPI fixture only in MVP.
- `POST /api/runs`, `GET /api/runs/{id}`, `GET /api/runs/{id}/events` (SSE, ID/Last-Event-ID, heartbeat, resume), `POST /api/runs/{id}/remediate` (finding ID and explicit user approval), `POST /api/runs/{id}/cleanup`, `GET /api/healthz`, `GET /api/readyz` (non-secret). All sensitive endpoints require authenticated authorized user; ownership checks on run IDs.
- Structured event schema: `event_id`, `run_id`, `timestamp`, `sandbox_role` (`security|build|remediation|system`), `sandbox_id`, `type`, `step_id`, `payload`; instrument **real** workflow boundaries; no fake AI reasoning, metrics or step transitions. Append sanitized replayable JSONL/events to Blob Storage, and retain recent in-memory ring buffer for live SSE. Poll SDK output if true streaming unsupported; disclose actual behavior.
- Validate strictly `review.json`, `build.json`, `remediation.json`; aggregate real results and evidence with accurate states `pending|running|passed|failed|skipped|timed_out`; report errors and checked/skipped limitations.
- Structured telemetry in Azure Monitor/Log Analytics/Application Insights with correlation IDs; redact before telemetry and SSE; avoid saving secrets or full potentially sensitive code in Blob.

### Dashboard (presentation-grade, 1080p, dark/high contrast)

Single-page UI hosted at the Azure Container App HTTPS FQDN with Entra sign-in:
- Header: GitHub URL, commit SHA, run ID, timer, Start, Clean Up, connection state, **Live / Replay (prerecorded)** toggle.
- Side-by-side **Sandbox A & B** cards with full lifecycle `Provisioning → Running → Completed → Deleting → Deleted`, IDs, elapsed time, GitHub Copilot label and separate dynamic workflow timelines showing deterministic vs AI stages, branches/retries/skips and evidence-based decision summaries.
- Expandable timestamped **real sanitized terminal/agent logs** for each sandbox, filterable chronological event console, auto-follow/pause and reconnect-aware SSE.
- Evaluation report: security evidence, severity, recommendations, build exit codes, actual pytest counts, health and runtime checks. Never call repository definitively 'safe' or 'approved'.
- Human-in-the-loop remediation confirmation: create C only on consent, show live steps, tests and clear git diff; create/push private `{repo}-fixed` in C after successful verification; no PR or writes to original repo.
- Cleanup visualization and show Sandbox lifecycles. Replay uses captured actual events **clearly marked prerecorded**, never passed off as live.

## 7. Workflow details

**A Dynamic Workflow (real Copilot extension):** checkout pinned SHA; inspect but **do not execute** repository code; run pinned approved static tools like Gitleaks/Semgrep if available (otherwise mark skipped); Copilot interprets findings; branch to additional bounded static verification for important findings; generate evidence-backed `review.json` (`id/severity/category/file/line/evidence/explanation/recommendation/confidence/verification_status`). Never expose secret values.

**B Dynamic Workflow (real Copilot extension):** pinned checkout; recognize known Python/FastAPI project; install bounded dependencies in sandbox venv; build/import check and pytest with exit codes/timeouts; if build fails, AI failure analysis and skip runtime; else launch app only bound to localhost, health check, constrained non-destructive tests; stop processes; generate `build.json` (commands/exit codes/test counts/health/checks/limitations). No public sandbox ingress by default.

**C Remediation & GitHub Publication — REAL Copilot Dynamic Workflow (demo-only):** one user approval of `Fix Vulnerability` for selected finding starts C. Checkout original immutable SHA, apply bounded fix, run build/tests and targeted security recheck, generate reviewable diff. If validation fails, do **not** create a repository. The **workflow must implement deterministic, observable conditional branches**: `fix -> build/tests + targeted recheck -> [failed: report without publishing | passed: verify destination name availability -> create private repository -> commit/push -> verify remote SHA -> report]`. Only the fix selection/patch reasoning is delegated to Copilot; do not leave the publish gate to a free-form prompt. On success, within C use the same group-injected GitHub fine-grained PAT to call the verified GitHub REST repository-creation endpoint for the PAT personal owner, create a **private** `{original-name}-fixed` repository, initialize/commit and push only checked/sanitized fixed source to it (including new files; no `.git` history, credentials, fixtures with secrets, or copied tokens), and return its URL and commit SHA in `remediation.json`. No backend publisher/Key Vault, no second Publish button, no changes/PR to original. Handle name collisions as explicit failure (never overwrite), API permissions, rate limits, repository ownership, partial publication, cleanup, and errors transparently; keep a captured diff/report in Blob before deleting C. Mark live stages `checkout`, `agent.fix`, `validate`, `publication.gate`, `create_repo`, `push`, `verify_remote`, `complete`; record failure/skip/branch decisions and reason grounded in exit codes/results; never report success without verifying the destination and pushed SHA. Users see the link on the dashboard.

Copilot and user repository code run **inside sandbox** only; no separate LLM agent in backend. Deliver workflow files dynamically via verified upload/exec APIs, not by changing built-in image.

### Demo-only GitHub PAT and publication requirements (mandatory)

One **personal-account-owned fine-grained PAT** configured **manually** at **Sandbox Group → Security → Credentials → GitHub Copilot → Set Token** after Terraform. It serves **both Copilot CLI and publication inside C**. Never put the PAT into Terraform, tfstate, image, backend config, git or logs. In GitHub's token settings use:

- **Resource owner: personal GitHub account with an active Copilot seat**, not an organization (required for Copilot Requests); use a dedicated disposable demo account.
- **Account permissions → Copilot Requests** (the access level exposed by GitHub, typically read) for Copilot CLI.
- **Repository permissions → Repository creation: Write** for `POST /user/repos` and **Contents: Read and write** for commits and push to the newly created repo. GitHub can require additional permissions for specific API methods: verify `X-Accepted-GitHub-Permissions` and actual Git push. Do not assume API repository creation permission alone authorizes push.
- **Repository access: All repositories** for the demo owner's current **and future** repositories, so the token can access the newly created `{repo}-fixed` repo. `Only select repositories` is unsuitable for automatically writing to repos created later without updating token scope. This is deliberately broad: never use on a real personal or corporate account. GitHub's access/ownership and policy constraints may vary; verify with a disposable private test repo first.
- Short expiration, account-level quota/rate limit awareness; store token only as Sandbox Group provider credential. If token permissions change, update the group token manually and use **fresh** Sandboxes to verify the new capability. Do not print a token or ask the user to paste it.

For **Milestone 0**, in addition to Copilot and workflow auth, verify **the third real Dynamic Workflow** including its failing-tests branch (no remote write), and separately repository creation and a harmless test push with that *same injected credential from a disposable sandbox* only after user approval to create a private test repository; remove the test repo only with further explicit approval. If token is not actually available to GitHub CLI/git operations in C, document the exact boundary and block the publish feature: Copilot authentication does not imply arbitrary Git API access. Never bypass with a different credential unless the user revises the demo design.

**Security tradeoff:** This is a **trusted-fixture demo only**. The same PAT is reachable by processes inside C and has GitHub write/create permissions. The MicroVM protects outside infrastructure, **not the token from untrusted repository code executed inside**. Hardening for customer/production use requires a separate publishing identity or broker, narrowly scoped permissions, explicit destination authorization, and independent review. A successful scan is not proof of safety.

## 8. Security/identity requirements

- **Three distinct identities:** (1) Entra-authenticated app user, (2) App UAMI for Azure data-plane/control-plane calls, (3) Copilot fine-grained PAT configured **manually as Sandbox Group provider credential** after provisioning. Never conflate them. Authenticate/authorize users server-side.
- Untrusted repo code in Sandbox B/C may read/exfiltrate credentials in the same sandbox; MicroVM isolation between sandboxes **does not secure the credential from code running within one**. Limit demo to vetted, benign repository; dedicated short-lived least-privileged PAT and account, scoped network egress, no access to unrelated organization repositories, revoke/rotate after presentations. This demo deliberately grants repository creation and contents write; malicious code in C may access the same token. Production implementations MUST separate Copilot identity and GitHub publishing permissions. Public customers must assess risk before evaluating arbitrary hostile repos.
- Repository instructions/README and output are untrusted prompt-injection sources. Restrict Copilot tool permissions; do not use `--allow-all-tools` casually. No unrestricted shell execution on hosting app. No external exploit traffic. No secrets in Docker image, ACR, `.env`, application settings, replay events, SSE, logs, storage or Terraform state.
- Secure storage with managed identity and RBAC; private containers, retention/lifecycle policy. Bound resource concurrency/costs. Guard against authenticated users exhausting quotas; use allowlists or approval for demo target URLs if necessary.
- Cleanup only sandboxes created by this app, never group, unrelated resources or customer-owned infrastructure. Retain reports for documented period; allow purge. Prevent orphaned sandboxes on error/timeout.

## 9. Implementation milestones and quality gates

0. **Discovery/PoC (GATE):** Find/read `terraform-builder` skill; verify providers and sandbox SDK, built-in Copilot preset, group-scoped auth, real CLI Dynamic Workflows, actual streaming. Document compatibility and smoke test. Stop if impossible.
1. **Terraform cloud foundation:** use skill to provision all static resources and identity/auth/Blob/ACA/ACR; implement bootstrap deployment and outputs; validate `terraform fmt/validate/plan`, provider schema, RBAC. No live `apply` or costly resource changes without user authorization.
2. **App container + CI/CD:** multi-stage Dockerfile to serve React static assets via FastAPI, GitHub Actions OIDC push/deploy, one HTTPS endpoint, Entra auth and Blob integration. Validate from Azure URL.
3. **Orchestrator + actual A/B workflows:** immutable SHA, two concurrently running real Copilot Dynamic Workflows, typed schemas, timeouts, reliable cleanup, real integration run.
4. **Live observability dashboard:** all lifecycle/step events, logs, SSE reconnect, report, Replay mode, event Blob persistence, no simulated live telemetry.
5. **Remediation C + publish Dynamic Workflow:** one Fix confirmation, third genuine Copilot Dynamic Workflow, isolated real fix, post-fix checks/diff, new private `{repo}-fixed` creation and push from within C using existing group PAT, verified URL in UI, audit events and cleanup.
6. **Presentation and customer readiness:** README, `.tfvars.example`, deployment guide, security/cost limitations, `docs/demo-script.md` minute-by-minute for 15 minutes, successful real JSONL replay, smoke/CI tests, cleanup/orphans, screenshots, customer self-deployment steps.

### Acceptance criteria

- [ ] ALL static Azure resources provisioned with Terraform following verified `terraform-builder` skill; `terraform validate` and deployment documentation work from a clean customer subscription.
- [ ] Customer application accessible on Azure HTTPS URL; **no localhost-only hosting**, no unauthenticated operational APIs; Entra sign-in functional.
- [ ] ACR hosts only the **app image**; Sandbox A/B/C use built-in GitHub Copilot preset with no custom sandbox images.
- [ ] GitHub PAT set manually post-provisioning at Sandbox Group portal; it is absent from source, tfstate, build env and app settings; no interactive `/login` in live sandboxes.
- [ ] Actual A+B separate and concurrent, at same immutable SHA, **two authentic Copilot Dynamic Workflows** with observed branching; real outputs and no fabricated agent activity.
- [ ] Run/report events and diffs stored privately in Azure Blob with server-side access controls; SSE real-time output reconnects/replays missed events.
- [ ] C created only after user authorization/confirmation; **executes a third genuine Copilot Dynamic Workflow** (not a prompt-only imitation) with instrumented fix, validation, deterministic pass/fail publication gate, remote repo creation/push and verification steps. No repo creation on failed validation. Returns verified URL/commit, never changes the source repository.
- [ ] Timeouts, auth failures, errors, cancellations and restarts handled with explicit statuses, owned-only cleanup and manual orphan remediation.
- [ ] Deploy workflow uses short-lived OIDC credentials, documented image lifecycle; nothing depends on locally running server after deployment.
- [ ] Verified and practiced 15-minute demo, honest recorded replay backup, tests and customer-installable docs.

## 10. Working style and environment

- Work in incremental independently testable slices. For each milestone: document design assumptions, exact commands, test results, unresolved risks; maintain `docs/progress.md`.
- Do not infer nonexistent Terraform skill semantics, Copilot CLI flags, sandbox disk names or preview API capabilities. Verify from installed tooling/docs before authoring production integration. No silent fallback to mock cloud runs; explicit local test doubles allowed **only in unit tests** and clearly labeled UI replay permitted.
- Ask only for truly missing user-specific values: subscription, region, tenant, authorized Entra principals, existing/reused Sandbox Group, customer GitHub repo and OIDC principal. **Never ask the user to paste PAT into chat or code.**
- Before `terraform apply`, role grants, provisioning paid resources, changing existing credentials or publishing repositories, present the exact plan and obtain approval.
- `README.md` must be the canonical customer-facing deployment guide, including **manual portal PAT steps** and customer limitations.

**Presentation message:** “Give every AI agent its own isolated computer.” The value is real execution isolation + observable GitHub Copilot Dynamic Workflows, not fake agent animation or automatic enterprise security approval.
