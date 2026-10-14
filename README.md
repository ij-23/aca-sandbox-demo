# From Untrusted Code to Trusted Decisions

> **Current execution authorization (2026-10-14):** Project-scoped Sandbox tests/cleanup, Terraform apply, Azure deployment and GitHub publishing are authorized autonomously under [AGENTS.md](./AGENTS.md#project-execution-authorization--2026-10-14). Recurring approval checkpoints below are superseded. Technical validation, product Fix confirmation, protection of unrelated resources and the prohibition on destructive operations remain.

**Azure-hosted Open Source Evaluation Demo** — Azure Container Apps Sandboxes + GitHub Copilot Dynamic Workflows.

[MIT license](./LICENSE) · [Contributing](./CONTRIBUTING.md)

> **Live A/B/C publishing verified.** The Azure host, Entra sign-in, concurrent genuine Copilot workflows, source-verified finding, successful C fix/validation/private publication, telemetry and 95-event private persistence/replay are verified. The original fixture is unchanged and all disposable Sandboxes are deleted. OIDC image release/deployment and runtime cancellation/recovery passed; remaining checks are tracked in [acceptance](./docs/acceptance.md). The project is not yet declared fully complete.

The project source is [ij-23/aca-sandbox-demo](https://github.com/ij-23/aca-sandbox-demo). Follow the [manual application deployment](./docs/deployment.md#manual-application-deployment-used-in-this-project) with the [application input example](./infrastructure/terraform/application.auto.tfvars.example).

## Developer quick start

Requires Python 3.13, Node 24, uv and Docker. These commands test the platform and preview its empty dashboard; they do not execute fixture code, create Sandboxes or contact Azure:

```sh
uv venv --python 3.13 .venv
uv pip sync --python .venv/bin/python --require-hashes requirements-dev.txt
npm ci --prefix frontend --ignore-scripts
.venv/bin/python -m pytest backend/tests scripts/tests -q
.venv/bin/python scripts/export_schemas.py --check
npm --prefix frontend test
npm --prefix frontend run build
LIVE_EXECUTION_ENABLED=false .venv/bin/python -m uvicorn app.main:app \
  --app-dir backend --host 127.0.0.1 --port 8000 --no-access-log
```

Open `http://127.0.0.1:8000` for development inspection. This is not the required final Azure deployment. Sign-in requires customer Entra registrations; operational APIs reject anonymous requests. Without Azure storage configuration, health returns 200 and readiness returns 503. There is no production memory-store fallback or fabricated replay.

Build the **application** image with `docker build --platform linux/amd64 -t aca-sandbox-demo:local .`. [Deployment guidance](./docs/deployment.md#local-preparation-and-validation) includes the optional package proxy configuration used in this environment. Never pass credentials as build arguments. CI in [.github/workflows/ci.yml](./.github/workflows/ci.yml) runs platform checks and an image build only; OIDC image publication is configured; deployment uses the existing local Terraform state as described below.

The approved M0-CLI97 test passed on 2026-10-14, including real Copilot AI, branching, live file polling and exact-ID cleanup. M0-C-FAIL also passed: actual AI patching and failing pytest caused the deterministic gate to skip all GitHub writes. The already-applied foundation plan must not be reapplied.

## Intended live experience

**Sandbox retention:** new application runs default to `RETAIN_SANDBOXES=true`. A/B/C are stopped and retained after execution for inspection, including unsuccessful runs. Their IDs and workflow files remain available in the Sandbox portal; use the dashboard's **Clean up** button to explicitly delete that run's Sandboxes. Restart reconciliation preserves the run's recorded retention policy. Retained resources consume quota and can incur storage charges; clean them up when inspection is finished. Previously deleted Sandboxes cannot be recovered by enabling this setting. Dedicated smoke/recovery probes still explicitly test deletion.

**Current repository support:** the deployed demo accepts only the configured trusted fixture, `https://github.com/ij-23/academo-fastapi-fixture`. See the [public-repository capability plan](./docs/public-repository-plan.md) for the proposed expansion. It separates general source analysis from verified language-specific builds/remediation and requires credential isolation before arbitrary repository code execution. This capability is not yet enabled.

An authenticated user enters a **public GitHub repository URL** into a React dashboard. A Python/FastAPI orchestrator (hosted together with React in one Azure Container App) creates **two isolated ACA Sandboxes simultaneously** from the built-in GitHub Copilot image. Both execute **genuine Copilot Dynamic Workflows**:

1. **Security Review (A):** static/source review, optional SAST and secrets scan, evidence-based findings and risk assessment.
2. **Build & Validation (B):** framework discovery, install/build, pytest, conditional app launch, localhost health and bounded runtime tests.

The web dashboard streams sandbox provisioning, agent activity, workflows and sanitized logs through **SSE**. After the report is ready, an authorized user may approve **Remediation (C)**; a third sandbox runs a **third genuine GitHub Copilot Dynamic Workflow** that patches the code, validates it, then **creates and pushes a new private GitHub repository named `{original-name}-fixed` using the same group-scoped PAT**. It returns the new repository link and the git diff. The original repository is never modified. There is no second Publish button. Sandboxes are then stopped and retained for inspection until you select Clean up. A labeled **Replay (prerecorded)** mode backs up the 15-minute presentation.

## High-level architecture

```text
Authenticated user (Microsoft Entra ID) -> HTTPS
   Azure Container App (React assets + FastAPI + SSE; 1 replica MVP)
      |-- User Assigned Managed Identity -> Azure Blob Storage (reports/events/diffs)
      |-- ACA Sandboxes SDK -> ACA Sandbox Group (Copilot PAT credential configured at group level)
                                |-- Sandbox A: Copilot Dynamic Workflow / security
                                |-- Sandbox B: Copilot Dynamic Workflow / build, test, runtime
                                `-- Sandbox C: on Fix approval, Copilot Dynamic Workflow / fix, validate, create/push {repo}-fixed
   ACR -> serves host application's Docker image only
   GitHub Actions OIDC -> build/push app image and release digest
   Local-state Terraform -> static Azure infrastructure and app image deployment
```

The Sandbox Group is separate from the **Container Apps Managed Environment** hosting our app. **No custom sandbox disk/image or ACR copy of Copilot is required.**

## Terraform-managed Azure resources

| Resource | Purpose |
|---|---|
| Resource Group | Owns resources for a customer deployment |
| Azure Container Registry | Stores React/FastAPI **application image** |
| Log Analytics Workspace + DCE/DCR + ingestion UAMI | Host diagnostics and fixed Sandbox workflow metadata via official telemetryConfig |
| Azure Container Apps Managed Environment | Hosting environment |
| Azure Container App | One HTTPS host for React, API, SSE and orchestration |
| User Assigned Managed Identity | App access to sandboxes and blob data without secrets |
| ACA Sandbox Group | Group for temporary Copilot agent sandboxes; limits/egress |
| Azure Storage Account + private Blob containers | Persist reports, event history, diffs, replay recordings |
| RBAC assignments | `AcrPull`, `Container Apps SandboxGroup Data Owner`, Blob data access |
| App Insights (recommended) | App traces, metrics and failures |
| Microsoft Entra app/user auth settings | Restrict web UI/API to approved users |
| OIDC/Federated credentials (where supported) | Secretless GitHub Actions image publication; local-state Terraform deploys the digest |

The three individual **Sandboxes are dynamic**, created/deleted at runtime by FastAPI—not tracked by Terraform.

## Requirements before deploying

- Azure subscription with permission to create resources, assign roles and (if needed) Entra application registrations.
- Region supporting **ACA Sandboxes** and host Azure Container Apps; appropriate Sandbox Group quotas.
- dedicated personal GitHub account with active Copilot entitlement, supporting a **fine-grained PAT** with Copilot Requests, repository creation and repository content write permissions. This is intentionally more privileged for the demo; do not use a corporate account.
- A customer-owned Microsoft Entra tenant and designated authorized demo users.
- Terraform toolchain and providers pinned by implementation; GitHub Actions OIDC trust configured for deployment (or an alternative documented authorized bootstrap path).
- The coding agent must have the **`terraform-builder` skill** installed and must read its `SKILL.md` before creating/updating Terraform.
- A reviewed **public Python/FastAPI demo repository**, ideally containing a benign intentional issue and fast pytest tests. Don't start with unknown hostile repositories.

## Deployment: bootstrap and application phases

Use the verified commands in the [deployment guide](./docs/deployment.md). These steps summarize the bootstrap sequence; a separate clean-subscription installation remains an [open acceptance check](./docs/acceptance.md#remaining-work-and-external-dependencies).

1. **Configure inputs:** subscription, tenant, Azure region, Resource Group prefix, ACR and Sandbox Group names, authorized Entra users/groups, repository/branch and retention. Never add the Copilot PAT to Terraform inputs.
2. **Bootstrap static infrastructure with Terraform:** using `terraform-builder`, create RG, ACR, workspace, identities, Blob, Sandbox Group and required RBAC. Validate plan; the final app image does not yet exist.
3. **Build/push application image:** GitHub Actions builds the multi-stage Dockerfile (React frontend + FastAPI host) and publishes to ACR using federated Azure OIDC authentication. Confirm the pushed image digest/tag.
4. **Finish app deployment via Terraform:** create/update Container Apps Managed Environment and the single Container App with that valid image, user-assigned managed identity, ingress, TLS, app settings, managed auth, Storage access, min/max replicas=1. Keep one clearly documented owner of future app image revision deployments to avoid Terraform drift.
5. **MANDATORY MANUAL STEP: configure the GitHub Copilot PAT on the newly created Sandbox Group** (instructions immediately below). Terraform should not store the PAT or its value in state.
6. **Preflight:** sign in to the published HTTPS app with Entra; verify `/api/readyz`, ACA Data Owner permissions, group credential status, Copilot noninteractive prompt, actual Dynamic Workflow extension, event persistence, and owned-only cleanup.
7. **Live exercise:** analyze the reviewed public repository; confirm two concurrent sandboxes and same commit SHA; click Fix Vulnerability once; verify patch/tests, a **new private `{repo}-fixed` repository created and pushed by Sandbox C**, the returned URL, and sandbox cleanup.

### Mandatory: configure GitHub Copilot PAT manually **after Terraform creates the Sandbox Group**

**This step is intentionally NOT automated by Terraform.** The PAT is a provider credential of the Sandbox Group, not a secret of the application Container App. Each customer must configure their own token in their own group. Do not paste PATs into GitHub Actions variables, `terraform.tfvars`, Dockerfile, `.env`, README issues, PRs or logs.

1. Use a **dedicated personal GitHub account with an active Copilot subscription**, preferably a disposable demo account. Open <https://github.com/settings/personal-access-tokens/new>. Select **Fine-grained PAT**, short expiration, and **Resource owner = personal account (NOT organization)**. Tokens start with `github_pat_`; classic `ghp_` tokens are not supported by Copilot CLI.
2. Choose **Repository access = All repositories** for this dedicated account. This includes **future** repositories and allows pushing into the new `{repo}-fixed` repository after it is created. **Only select repositories** does not automatically grant access to future newly created repositories; choosing All is an intentional *demo-only security compromise*.
3. Under **Account permissions**, add **Copilot Requests** with the access level offered by GitHub (typically Read).
4. Under **Repository permissions**, add **Repository creation: Write** and **Contents: Read and write**. GitHub may require more for some creation/commit/push methods; confirm the chosen account's policies and test the exact `POST /user/repos` plus `git push` operations. Creation alone does not prove push authorization. Do **not** select unrelated permissions such as Actions/Workflows or broad administration by default.
5. Generate the PAT and copy it securely. **Do not** add it to Terraform, GitHub Actions, app settings, ACR, `.env` or any logs.
6. After Terraform finishes creating the Sandbox Group, sign in to **ACA Sandboxes Portal** at <https://sandboxes.azure.com> using the Azure tenant/subscription that hosts the group.
7. Open **Sandbox Groups** and select the Sandbox Group created by Terraform. Ensure you have the **Container Apps SandboxGroup Data Owner** role at an appropriate scope.
8. In the group navigation, open **Security → Credentials** (portal labels may change).
9. Find **GitHub Copilot**, select **Set Token** (or the equivalent Configure action), paste the fine-grained PAT into **Token**, and select **Save**.
10. Confirm the GitHub Copilot row displays **Configured**. The portal intentionally does not reveal the token after saving.
11. **Verify real use**, not just the badge: create a temporary sandbox using the **built-in GitHub Copilot preset**, execute a minimal noninteractive Copilot prompt and, separately, a minimal **real Dynamic Workflow**; no `/login` should be needed. Additionally, within the authorized demo scope, create a disposable private test repo and, verify **that exact group PAT** can create a repo and push a harmless file from inside a test Sandbox; confirm repo URL, then clean up as separately approved. Do not assume the credential is accessible to arbitrary git operations just because Copilot CLI authenticates. Delete the test sandbox. A Configured status alone is not proof of entitlement, compatibility or successful execution.
12. For rotation: open the same **Security → Credentials → GitHub Copilot → Set Token**, enter the new PAT, Save, and **recreate or restart existing sandboxes** as needed to ensure they pick up the new credential. Expire/revoke demo tokens after presentations.

**Official references:** [Provider credentials](https://staging.sandboxes.azure.com/docs/sandboxes/credentials), [Sandbox portal quickstart](https://learn.microsoft.com/en-us/azure/container-apps/sandboxes-quickstart-portal). As of the referenced provider-credential documentation, this token-management function is not available in the `azure-containerapps-sandbox` Python SDK; therefore the manual portal step is required in this project.


## Fix Vulnerability → new GitHub repository (demo-only)

There is **one approval/action** in the UI: **Fix Vulnerability**. The Python orchestrator creates Sandbox C; **C itself** (not a backend GitHub publisher) runs a **real Dynamic Workflow**, checks out the original pinned commit, uses Copilot to patch the issue, runs build/pytest and focused rechecks, and generates a git diff. The Dynamic Workflow enforces a deterministic branch: if build, tests or targeted rechecks fail, report failure and **skip remote creation/push**. If validation passes, C uses the **same Sandbox Group GitHub Copilot PAT** to create a **private** repo in the PAT's personal owner account named `{original-repository}-fixed`, commits and pushes the corrected source, and returns its verified URL and SHA. The dashboard shows the third Workflow timeline with fix, tests, branch/gate, create-repo, push and remote verification progress, diff/results, and a clickable link. Backend stores sanitized evidence and stops C for retention; Clean up explicitly deletes it. The source repository is not changed. A name collision should fail clearly rather than overwrite an existing repository; partial remote creations are reported, not silently deleted.

**No separate Publish button, publishing credential or Azure Key Vault is required for this demo.** GitHub repository creation is a real external side effect; the Fix confirmation must state that it creates a new private repository. Preserve the original project license/attribution and exclude credentials, runtime artifacts, `.env`, and hidden test secrets before push. The demo is restricted to a pre-reviewed harmless fixture repository. Production adopters **MUST redesign credentials and publication authorization**: never run arbitrary untrusted code with a PAT capable of creating/writing repositories.

Official GitHub references: [Copilot CLI authentication](https://docs.github.com/en/copilot/how-tos/copilot-cli/set-up-copilot-cli/authenticate-copilot-cli), [fine-grained PAT repository access and owner](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens), [fine-grained PAT endpoint permissions](https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens).

## Access and security boundaries

- **Web end user:** Microsoft Entra sign-in; FastAPI must verify identity and authorize all run/remediate/cleanup endpoints, not just rely on React UI.
- **Backend to Azure:** User Assigned Managed Identity with Sandbox Group data-plane role and least-privileged Storage blob access.
- **Copilot agents:** group-level manually set GitHub fine-grained PAT; agent runs **inside** each sandbox.
- **Major caveat:** Build/tests execute repository code inside Sandbox B/C where Copilot is authenticated. MicroVM isolation protects the rest of the application, **but does not guarantee protection of the Copilot credential from malicious code within that same sandbox**. Use vetted fixture code for the live demo, narrow outbound access, dedicated short-lived token and no access to unrelated organization GitHub repositories. For this demo, the PAT intentionally has repository creation and contents-write privileges; **code executing inside Sandbox C can potentially abuse those privileges**. Never use this design for untrusted customer repositories without credential separation. This tool is an evaluation aid, **not a certification that a repository is safe for enterprise use**.
- Publicly hosted does **not** mean anonymously usable. Entra auth, quotas/timeouts, URL allowlisting and rate limiting protect against unauthorized or costly runs. Store sanitized results/events in private Blob containers; no secrets in browser, SSE, telemetry or replays.
- Orchestration is single-process/single-replica MVP. Blob gives event/report persistence, **not automatic recovery of in-flight work after an app restart**. Proper multi-replica customer production would need durable job/worker coordination and further hardening.

## Repository structure

```text
backend/app/               FastAPI, auth, orchestrator, Sandbox SDK, SSE and Blob
backend/tests/             platform unit tests; no fixture execution
frontend/                  React + TypeScript + Vite dashboard and tests
workflows/                 security-review, build-validation and remediation extensions
  shared/                  trusted workflow operations, runner and event instrumentation
  copilot-host/            official SDK host, locked dependencies and credential probes
  smoke/                   minimal genuine Dynamic Workflow compatibility check
  schemas/                 generated report contracts, checked against backend models
scripts/                   operator probes, smoke/cleanup tools and platform checks
  tests/                   tests for operator tools and trusted workflow operations
demo-repo/                 vetted vulnerable FastAPI source; execute only in Sandboxes
fixtures/                  genuine prerecorded events and provenance
infrastructure/terraform/  Terraform root, modules, tests and customer input examples
.github/workflows/         platform CI and OIDC image release (no Terraform apply)
.vscode/                   build, test and local preview tasks
docs/                      architecture, deployment, security, compatibility and acceptance
requirements*.in           platform runtime/development dependency inputs
requirements*.txt          hash-locked runtime/development dependencies
pyproject.toml             platform-only pytest discovery and Ruff configuration
Dockerfile                 multi-stage application container
.env.example               non-secret application configuration example
AGENTS.md                  implementation requirements and project authorization
README.md                  customer onboarding and deployment overview
CONTRIBUTING.md             contributor checks and repository maintenance
LICENSE                    project MIT license
```

The host, dashboard, smoke workflow, report schemas, CI, foundation and [trusted source fixture](./demo-repo/README.md) exist. The [vetted fixture](https://github.com/ij-23/academo-fastapi-fixture) is published; its tests run only inside disposable Sandboxes. All three workflow extensions and the SDK adapter have passed real Azure execution. Publication defaults off for new installations until their credential gates pass; it is enabled in this verified demo. A genuine full-run replay is available. The current [configuration example](./.env.example) contains non-secret names only; the host never reads a Copilot PAT.

### Documentation map

| Document | Purpose |
| --- | --- |
| [Deployment](./docs/deployment.md) | Bootstrap, manual deployment, OIDC releases, operator checks and costs |
| [Architecture](./docs/architecture.md) | Implemented components, execution boundaries and state ownership |
| [Security](./docs/security.md) | Identity, shared-PAT risks and trusted-fixture restrictions |
| [Compatibility](./docs/compatibility.md) | Verified SDK/CLI/API behavior and dated technical evidence |
| [Acceptance](./docs/acceptance.md) | Current verification status and remaining work |
| [Progress](./docs/progress.md) | Dated implementation and maintenance history |
| [Demo script](./docs/demo-script.md) | Fifteen-minute presenter walkthrough |
| [Replay provenance](./fixtures/README.md) | Origin and checksum of the genuine recording |

Use [locked development dependencies](./requirements-dev.txt) for platform tests and operator tools. Local caches, installed dependencies and generated dashboard assets are ignored. Private deployment evidence, Terraform state, backups, inputs and saved plans must be retained separately from disposable caches; see [repository maintenance](./CONTRIBUTING.md#repository-maintenance).

## API / live UX

`POST /api/runs`, `GET /api/runs/{id}`, `GET /api/runs/{id}/events` (SSE with reconnect), `POST /api/runs/{id}/remediate`, `POST /api/runs/{id}/cleanup`, and health/readiness endpoints. All operational API paths require user authorization. The display shows Sandboxes A/B independently progressing, exact branch outcomes, real sanitized command logs, an evidence-backed report, then C with a diff, automated new private `{repo}-fixed` publication, and clickable verified GitHub repository URL. Replay is clearly tagged **prerecorded**.

## 15-minute presenter plan

| Minute | Story |
|---|---|
| 0–2 | Why evaluate untrusted OSS in isolation? |
| 2–4 | Azure architecture, group credentials and built-in Copilot sandbox image |
| 4–5 | Enter GitHub URL; two sandboxes provision |
| 5–9 | Two real parallel Copilot Dynamic Workflows; live logs and branching |
| 9–11 | Security/build/runtime report and evidence |
| 11–13 | User clicks Fix; C runs a third Dynamic Workflow to patch/test and create/push private `{repo}-fixed` (time is variable) |
| 13–14 | Sandbox cleanup/lifecycle |
| 14–15 | Key takeaways, risks and customer deployment |

Copilot and cloud timings are nondeterministic. Record one actual successful run for fallback; show **Replay (prerecorded)** label prominently if used.

## Troubleshooting / checks

| Symptom | Check |
|---|---|
| GitHub Copilot asks for `/login` | Group credential status and entitlement; SDK creation must attach the existing connection with `connections=[connection_id]` alongside `disk="copilot"`; never inject a token or use interactive login |
| Group not found / sandbox creation denied | Correct tenant, subscription, region; app UAMI `Container Apps SandboxGroup Data Owner` scoped to group |
| Copilot works but Dynamic Workflow (A/B/C) doesn't | Copilot CLI version, experimental setting if needed, actual extension registration/invocation; check `docs/compatibility.md` |
| App fails image pull | Image/tag/digest exists in ACR, Container App registry identity and `AcrPull` RBAC |
| UI loads but calls return 401/403 | Entra authentication registration, audience/issuer, user allowlist and API authorization |
| SSE is interrupted | Container App revision/restart, SSE ID replay from saved event history, app replica setting |
| Missing reports after restart | Blob connectivity/RBAC, retention, run recovery limitation |
| Slow build or timeout | Repo fixture size, dependency constraints, sandbox limits, bounded task timeouts |
| Unexpected cloud costs | One active run, sandbox max count, per-run deadlines, clean orphans, monitor ACA/ACR/Blob/Logs |

## Teardown

1. From the app, finish/cancel runs and perform owned-only sandbox cleanup.
2. Validate that no demo-created sandboxes remain in the Sandbox Group; use verified orphan cleanup script if needed.
3. Archive/export needed sanitized reports; remove the manually configured Copilot credential or revoke its PAT as appropriate.
4. Only after confirming the scope of changes, execute skill-compliant `terraform destroy` to remove **this deployment's** static resources. Never destroy an unrelated or shared Sandbox Group/resource group.

## Official technical starting points

- [ACA Sandboxes Python quickstart](https://learn.microsoft.com/en-us/azure/container-apps/sandboxes-quickstart-python-sdk)
- [Sandbox Groups Terraform / AzAPI resource](https://learn.microsoft.com/en-us/azure/templates/microsoft.app/2026-07-01/sandboxgroups)
- [Sandboxes Terraform quickstart](https://sandboxes.azure.com/docs/sandboxes/quickstart/setup-terraform)
- [Copilot provider credentials](https://staging.sandboxes.azure.com/docs/sandboxes/credentials)
- [GitHub Copilot Dynamic Workflows announcement](https://github.blog/changelog/2026-10-01-dynamic-workflows-in-copilot-cli-and-the-copilot-app/)

**Main message:** Give every AI agent its own isolated computer — with three observable, real Copilot Dynamic Workflows, user-controlled remediation and a fully Azure-hosted, customer-deployable platform.

## Local Terraform state and OIDC image releases

This deployment explicitly retains **local Terraform state**. Do not migrate it to Blob, reset it, or run Terraform against an empty hosted runner. Keep private backups of state/inputs; never commit or upload state or saved plans as Actions artifacts. Terraform remains the sole owner of application revisions.

Set optional `github_build_repository = "owner/project-repository"` in private Terraform inputs. Inspect `gh api repos/OWNER/REPO/actions/oidc/customization/sub`; if immutable subjects are enabled, set `github_build_subject` to the returned `sub_claim_prefix` plus `:ref:refs/heads/main`. Inspect/apply the exact plan, then configure these non-secret repository variables: `AZURE_CLIENT_ID` from `github_build_client_id`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, `ACR_NAME`, `ACR_LOGIN_SERVER`. The build identity has **AcrPush on this registry only**, and exact main-branch GitHub federation. It cannot deploy infrastructure or read report blobs.

Run the [release workflow](./.github/workflows/deploy.yml) from main. Download its `application-release` artifact containing only image digest and source SHA. On the existing state-holding machine, set `application.image` in private deployment inputs to that digest, preserve all other inputs, plan/inspect/apply using [manual deployment](./docs/deployment.md#manual-application-deployment-used-in-this-project). Drain active app runs first. The workflow does not itself update the Container App. Full automatic Terraform deployment is not claimed without a persistent trusted runner.
