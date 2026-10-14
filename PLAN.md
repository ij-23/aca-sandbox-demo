# Implementation plan — From Untrusted Code to Trusted Decisions

> **Current execution authorization (2026-10-14):** Project-scoped Sandbox tests/cleanup, Terraform apply, Azure deployment and GitHub publishing are authorized autonomously under [AGENTS.md](./AGENTS.md#project-execution-authorization--2026-10-14). Recurring approval checkpoints below are superseded. Technical validation, product Fix confirmation, protection of unrelated resources and the prohibition on destructive operations remain.

Updated: 2026-10-14. Status: **M0 and full live A/B/C publishing passed; genuine replay captured; OIDC image release/deployment passed; remaining failure/rehearsal gates in progress. Existing LOCAL state required.**

[AGENTS.md](./AGENTS.md) is authoritative. [README.md](./README.md) remains the customer-facing deployment guide. Track execution in [docs/progress.md](./docs/progress.md); source evidence and unresolved compatibility questions are in [docs/compatibility.md](./docs/compatibility.md).

The approved foundation deployment created 23 resources on 2026-10-12; resource read-back and eight RBAC assignments were verified. Subsequent separately approved disposable Sandboxes proved SDK creation/exec/upload/deletion and Copilot prompt authentication through explicit provider-connection binding. Every test Sandbox was deleted. The explicitly approved one-Sandbox M0-CLI97 test passed with a genuine registered workflow, real AI/conditional branch and live file polling. Its Sandbox was deleted with exact-ID 404 verification. The Azure Container App and Entra registrations are now deployed. The vetted fixture is public. Same-PAT private creation and push now pass after the user corrected permissions; full C publication is verified.

The current autonomous implementation has added the local React/FastAPI platform, strict report schemas, Entra JWT validation, managed-identity Blob adapter, SSE resume, bounded orchestration/cleanup, CI and a buildable application image. A/B live execution is enabled and verified. Publication is enabled after a same-PAT harmless push passed; C then published a verified private fixed repository. Preserve existing foundation resource definitions, state, inputs and consumed saved plan. An optional application module is now prepared and locally validated, defaulting to no application; do not regenerate or reapply the consumed foundation plan. Further project-scoped infrastructure changes use standing authorization; inspect saved plans and reject destructive or unrelated changes.

## 1. Architecture and boundaries

The presentation message is: **Give every AI agent its own isolated computer.** Each customer deploys one instance into their own Azure subscription.

| Component | Responsibility and boundary |
| --- | --- |
| Authenticated browser | React/TypeScript/Vite dashboard; Entra sign-in; REST and reconnectable SSE over the application's HTTPS origin |
| One Azure Container App | FastAPI serves built frontend assets, enforces user authorization, and deterministically orchestrates work; one process and min/max replicas of one |
| App user-assigned managed identity | Azure access only: group-scoped SandboxGroup Data Owner, scoped blob access, and ACR image pull |
| Sandbox Group | Separate ARM resource; manually configured Copilot provider credential; verified limits and egress controls |
| Sandbox A | Built-in `copilot` disk; real security Dynamic Workflow; source inspection and approved static tools only; no execution of submitted repository code |
| Sandbox B | Separate built-in `copilot` sandbox running a genuine build Dynamic Workflow concurrently with A; same immutable SHA; bounded Python/FastAPI install, build, pytest, and conditional localhost runtime checks |
| Sandbox C | One Fix Vulnerability approval starts a third genuine Dynamic Workflow: pinned checkout, bounded fix, deterministic validation/publication branch, private `{repo}-fixed` creation and commit/push inside C using the same group PAT, verified destination URL/SHA and diff/tests; source repository unchanged |
| Private Azure Blob Storage | Sanitized events, reports, ownership records, diffs, and genuine-run replay; persistence does not provide durable execution |
| Log Analytics and Application Insights | Redacted telemetry correlated by application run ID |
| ACR | Application image only; never rebuild or publish the sandbox image |
| GitHub Actions with Azure OIDC | Test the platform and build/push its image; existing local state holder applies its reviewed digest |

No Foundry, Azure OpenAI, AKS, custom sandbox images, extra worker service, database, backend GitHub publisher, or separate publishing credential. The host app needs a Container Apps Managed Environment; the Sandbox Group does not require that linkage. The baseline has no VNet. User-resolved Storage networking was verified read-only: publicNetworkAccess Enabled, defaultAction Allow, endpoint reachable. Operator Blob read lacks data permissions; existing app UAMI runtime access is verified. No network change is needed.

The three identities remain distinct: Entra user, app Azure identity, and group-level Copilot PAT. Never attach the app's Azure identity to untrusted execution sandboxes. Repository code runs only in disposable B/C sandboxes. Local and CI tests exercise platform code and explicit unit-test doubles, never execute a submitted repository or the demo fixture's build/tests.

### Run and observability design

1. Authorize the user and target repository against a configured allowlist of vetted public Python/FastAPI fixtures. Accept only canonical HTTPS GitHub owner/repository URLs. Resolve one public commit SHA using a bounded, host-restricted API call.
2. Acquire a single active-run slot atomically and persist the run owner and intent. Create A/B concurrently; record identifiers and ownership immediately. Reconcile ambiguous creation outcomes before retrying so timeouts do not create untracked duplicates.
3. Upload trusted extension code into a separate control directory in each sandbox. Keep the target checkout separate. Do not discover or trust extensions, hooks, MCP configuration, or instructions supplied by the target repository.
4. Invoke the registered Dynamic Workflows, validate their actual outputs, and persist sanitized events before delivery through SSE. Blocking SDK calls use `asyncio.to_thread`; cancellation must also stop remote work, since cancelling a thread await does not kill the remote command.
5. Delete A/B on success, failure, timeout, or cancellation. Publish real reports with limitations. A report never certifies a repository as safe.
6. Bind the single **Fix Vulnerability** approval to owner, run, SHA, finding ID, destination personal account/private `{repo}-fixed` name, and a unique attempt. The confirmation discloses repository creation and push. Reject duplicates, stale approvals and concurrent remediation attempts. C executes the registered remediation/publication Dynamic Workflow below; there is no second Publish button. Persist its sanitized diff/report and publication outcome to Blob before deleting C.
7. On restart, mark in-flight runs interrupted and reconcile only app-owned sandboxes. Never claim automatic workflow resumption. Retain cleanup failures visibly until deletion is confirmed.

Events use the exact required fields: `event_id`, `run_id`, `timestamp`, `sandbox_role`, `sandbox_id`, `type`, `step_id`, `payload`. The dashboard separates sandbox lifecycle from workflow outcome. Use actual workflow phase/step instrumentation and bounded sanitized logs, with no inferred agent reasoning. If the SDK only permits capture/polling, display that transport honestly. Persist monotonic event IDs, handle `Last-Event-ID`, heartbeat and reconnect, and bound both payload sizes and the in-memory ring buffer.

The React dashboard must expose **all three genuine Dynamic Workflows**: concurrent side-by-side A/B timelines and a full C timeline after Fix approval, with the same lifecycle, timestamps, logs, deterministic/AI stage distinctions, branch reasons, retries/skips, result and cleanup visibility. C shows validation exit codes/test counts, the publication gate, diff, destination privacy/owner, and a clickable verified `fixed_repository_url` plus commit SHA. Failed or partial publication remains visibly distinct from success. SSE reconnect and labeled genuine replay must preserve C's branch and publication events as well as A/B events; replay never performs GitHub writes.

### Sandbox C: genuine remediation and publication Dynamic Workflow

Implement a trusted registered Copilot extension, using verified workflow definition/registration/invocation APIs just as for A/B. Only fix selection and patch reasoning are delegated to Copilot. Trusted workflow code owns validation, conditional branches and GitHub side effects; a prompt asking an agent to publish is insufficient.

| Observable stage | Deterministic contract |
| --- | --- |
| `checkout` | Fresh checkout of the original immutable SHA in C; trusted workflow control directory separate from fixture configuration |
| `agent.fix` | Bounded Copilot patch for the approved finding, instrumented as an actual workflow agent step |
| `validate` | Build/tests and targeted security recheck; capture exit codes, test results and reviewable diff, including new files |
| `publication.gate` | Fail closed on failed, skipped-required, missing or timed-out validation; report with create/push skipped and **no repository creation**. On success verify the authorized personal owner and destination name availability; collisions fail, never overwrite |
| `create_repo` | Inside C, use the same group-injected PAT and verified `POST /user/repos` contract to create private `{original-name}-fixed`; validate returned owner/name/privacy and capture repository identity |
| `push` | Initialize a fresh Git history and commit/push only checked, sanitized fixed source including new files; preserve license/attribution. Exclude original `.git` history, credentials, `.env`, generated runtime artifacts, secret-bearing fixtures and copied tokens; never change the original remote |
| `verify_remote` | Verify exact destination identity, private visibility and pushed commit SHA; do not report successful publication from a local commit or HTTP creation response alone |
| `complete` | Return strict `remediation.json` with validation evidence, diff reference, publication status, `fixed_repository_url` and verified commit SHA on success; persist sanitized report/diff to Blob before C cleanup |

Every failure emits the actual stage, branch decision and evidence; unexecuted stages are skipped. Handle permissions, rate limits, timeouts, ownership mismatches, name collisions and partial publication explicitly. Persist creation intent and returned repository identity; reconcile ambiguous creation/push responses before retrying, never overwrite an existing destination or silently create a second repository. If creation succeeds but push/verification fails, report the partial destination without marking it successful or automatically deleting it. Repository deletion requires further explicit approval. If evidence persistence fails, expose that failure and retain a bounded recovery path without claiming durable capture or losing owned-sandbox cleanup tracking.

### Shared PAT compatibility gate

Follow the updated [README credential procedure](./README.md#mandatory-configure-github-copilot-pat-manually-after-terraform-creates-the-sandbox-group): dedicated disposable **personal** account with eligible Copilot seat, short-lived fine-grained PAT, Copilot Requests, Repository creation: Write, Contents: Read and write, and All repositories access covering current/future repositories. These are the required demo settings, **not yet verified runtime capabilities**. Verify official endpoint permissions, `X-Accepted-GitHub-Permissions`, account policy and actual push behavior; do not infer push rights from successful creation or add unrelated privileges by default.

The token stays only in the manually configured Sandbox Group credential and inside the sandbox's supported injection boundary. Prove the same credential is usable by GitHub API/git operations inside a disposable sandbox without printing or copying it to the host. Copilot login success alone does not prove that access. If the boundary or permissions prevent publication, block that feature and record the exact evidence; no substitute credential or backend publisher unless the user revises the design. B/C code may access this broadly privileged PAT: restrict the demo to vetted harmless fixtures on the disposable account. Production adoption requires separate identities and publication authorization.

## 2. Milestones, deliverables, and exit gates

Milestones are sequential gates. Local code passing tests is not a substitute for the required Azure validation. A gate failure stops the affected cloud feature; report it without replacing real execution with simulation.

| Milestone | Deliverables | Required verification before completion |
| --- | --- | --- |
| **0 — Discovery and PoC** | Compatibility ledger; dependency pins; environment verifier; existing minimal smoke plus C remediation/publication workflow PoC | Installed SDK and in-sandbox CLI verified; group PAT works without login; real registered workflow proof; C failing-tests branch performs no remote write; project-scoped private test-repository creation and harmless push inside a disposable sandbox using the same injected PAT, verified owner/privacy/URL/SHA; capture and sandbox cleanup evidence. Test-repository deletion needs further approval |
| **1 — Terraform foundation** | Concern-based modules, validated inputs/outputs, two-phase deployment, auth/identity/Blob/logging, limits/egress, examples | `fmt -check`, `init`, provider schema inspection, `validate`, reviewed saved plan; inspected project-scoped apply; post-apply resource and scoped-RBAC verification |
| **2 — Application host and CI/CD** | Multi-stage app Dockerfile; FastAPI/static host; Entra authorization; Blob store; CI and OIDC deploy | Platform tests and image checks; project-scoped Azure deployment; HTTPS login works, unauthenticated/unauthorized API calls fail, app MI reaches Blob/sandboxes, reports survive restart |
| **3 — Actual A/B workflows** | URL/SHA validation; SDK adapter; strict report schemas; bounded concurrent orchestrator; real security/build extensions | Real A/B overlap at one SHA; observed branch/skip behavior; actual tool exit codes, tests and health checks; cleanup across failure and cancellation; no fixture code executed outside sandboxes |
| **4 — Dashboard** | 1080p dark dashboard; independent timelines for **all three** workflows; terminal logs; branch/gate evidence, diff and verified repository link; explicit replay state | UI/type/build checks; Azure browser exercise of A/B and C; SSE reconnect preserves publication/branch events; real logs and accurate cleanup; no synthetic live telemetry. Finish C UI integration with Milestone 5 |
| **5 — Remediation C + publication** | One Fix Vulnerability confirmation; third genuine Dynamic Workflow, deterministic validation/publication gate, private `{repo}-fixed` creation/push inside C, verified URL/SHA and durable diff/report | No C before consent; cross-owner/repeated/stale approvals rejected; failed validation causes no remote write; successful branch verifies private owner/destination/remote SHA; collisions/partial publication visible; original unchanged; evidence persisted and C deleted |
| **6 — Customer/demo readiness** | Canonical deployment README; deployment/security/architecture guides; 15-minute script; genuine replay; orphan cleanup; screenshots; OSS license/contribution guidance | Clean customer-install rehearsal, failure drill, all acceptance checks, live demo rehearsal within budget, replay provenance, owned-only cleanup and approved teardown rehearsal |

### Milestone 0 original execution sequence (historical; completed)

1. Maintain the configured Python 3.13 environment and locked dependencies. SDK 0.1.0b4 and Identity 1.26.0 are installed; signatures and basic live lifecycle were verified. The configured Microsoft package proxy resolved the earlier download issue.
2. Inspect actual provider schemas and Sandbox Group contracts. Resolve stable versus preview field support, egress IaC ownership, managed identity authentication, and secret-free web authentication before authoring production integration.
3. Use the previously verified customer subscription/tenant, Sweden Central, `academo` prefix and deployed group recorded in the private [deployment results](./.local/azure-discovery/deployment-results.md). Recheck the exact context before any later approved cloud operation; do not repeat foundation provisioning.
4. Preserve all existing Terraform artifacts, including the already-applied saved plan. Foundation resource creation/read-back is complete, while app UAMI runtime authorization and group limits/egress remain open. Project-scoped infrastructure changes use the standing authorization.
5. Preserve the manually configured PAT. Copilot authentication with the explicit existing provider-connection binding is verified; publication permissions remain unverified. Never request the PAT value or place it in IaC/state, Actions, app configuration or logs. If permissions change, the user updates the group token manually and verification uses fresh Sandboxes.
6. Prepare a smoke test that creates one labeled disposable `copilot` sandbox; verifies the installed CLI and credential usability; uploads a trusted minimal `.mjs` extension; runs a real agent-backed Dynamic Workflow; checks the run envelope, branch evidence, and fresh structured result; deletes in `finally` and verifies absence. Record cleanup failure separately without losing the original error.
7. Inspect the exact smoke action, group, limits, and owned create/delete scope. Run under standing authorization. Test capture behavior and failure cleanup. Record actual versions, timings, calls, exit codes, and sanitized evidence in the compatibility ledger.
8. Implement and exercise the **third genuine Dynamic Workflow PoC**, including a controlled failing-tests branch that emits validation/publication-gate evidence and makes no GitHub write. Keep this inside a tracked disposable sandbox; local tests may use explicit doubles only.
9. Verify official repository creation permissions and the injected credential boundary. Verify the exact personal owner, disposable private test-repository name, harmless content, sandbox limits and create/push side effects. Under standing authorization test private creation and harmless push from inside the sandbox with the same group PAT; verify destination and remote SHA. Retain sanitized evidence and clean up the sandbox under its approved scope. Do not delete the test repository without further explicit approval.
10. Proceed only when the expanded runtime proof succeeds. If the built-in disk lacks workflow capability or the same credential cannot publish, stop the affected feature; do not switch to a custom disk, prompt imitation, different credential or backend publisher. The C PoC belongs to Milestone 0; complete app-integrated C and dashboard acceptance in Milestone 5.

The nonce smoke harness has run against Azure, but stopped at the CLI capability gate before executing its genuine extension. The harness now accepts an explicitly reviewed CLI version and an opt-in, checksum-pinned disposable-local 1.0.97 installation. The approved M0-CLI97 run passed and its authorization is consumed. It does not cover the C publication gates.

## 3. Infrastructure and deployment ownership

Use the installed `terraform-builder` skill at `/Users/ij/.agents/skills/terraform-builder/SKILL.md` (an additional copy exists under `/Users/ij/.codex/skills/terraform-builder/`). Its complete instructions were read; it has no additional template files in the selected directory.

The project explicitly requires `infrastructure/terraform/`; that user instruction overrides the skill's `iac/` location rule. Preserve its other applicable rules: small relative-source modules, typed/described/validated inputs, parameterized names/regions/SKUs/tags, managed identities, Microsoft Learn grounding, provider constraints and lockfile, formatting/validation, and Terraform-owned static-resource teardown. Do not add Key Vault just because the generic skill mentions it. Runtime sandbox deletion remains an SDK responsibility as explicitly required by this project.

Proposed module concerns: resource group, registry/identities, storage, monitoring/environment, sandbox group/policy, application/auth, optional deployment federation. Prefer AzureRM for supported resources, AzAPI only where verified support requires it, and AzureAD for customer-approved directory resources. Verify schemas rather than assuming the newest provider supports every preview resource.

Use one Terraform root with an explicit application phase input, subject to validation:

1. **Foundation phase:** create infrastructure and access scopes without a Container App referencing a nonexistent image. Return ACR and Sandbox Group outputs.
2. **Image phase:** build the application and push a unique version; resolve its digest. OIDC trust must already have been bootstrapped through an approved action. A documented authorized local identity may perform the one-off manual path.
3. **Application phase:** supply the real digest and create the app/auth configuration. Terraform is the sole owner of image revision changes thereafter; Actions builds/pushes; the existing local state holder plans/applies its digest. Actions never updates the app or handles state.
4. **Manual credential checkpoint and validation:** configure group PAT, verify login and managed identity, then run the approved smoke and integration tests.

App authentication must fail closed even while deployment dependencies converge. Avoid a momentarily anonymous operational endpoint during app/auth provisioning.

**Existing LOCAL Terraform state is explicitly required (2026-10-14).** Preserve it and its lineage; no remote backend, migration, reset or recreation. Hosted Actions must never run Terraform against empty ephemeral state or upload state/plans as artifacts. Use OIDC for image publication and the existing local state holder for inspected Terraform deployment. A fully automated Terraform Actions job would require a customer-provided persistent trusted runner with access to this exact state; do not install one silently.

Required outputs: `application_url`, `sandbox_group_name`, `resource_group_name`, `region`, `acr_login_server`, `managed_identity_client_id`, `storage_account_name`, and non-secret manual setup links/instructions. Explain phase-dependent outputs, retention, budget expectations, and the manual credential/consent checkpoints.

Project-scoped apply, scoped grants, bounded Sandboxes, deployment and GitHub publication use the standing authorization in AGENTS.md. Inspect saved plans and targets and reject destructive/unrelated actions. Preserve the app's single Fix Vulnerability confirmation. Repository deletion and credential changes remain outside scope.

## 4. Verified dependencies and remaining prerequisites

| Dependency | Current state |
| --- | --- |
| Source | Public project ij-23/aca-sandbox-demo; reviewed fixture ij-23/academo-fastapi-fixture; original immutable SHA preserved |
| Terraform | 1.15.3; AzureRM 4.81.0, AzAPI 2.13.0 and AzureAD locked; local state and lineage retained |
| Runtime | Python platform 3.13.16; official Sandbox SDK 0.1.0b4; Azure Identity 1.26.0 |
| Workflows | Official CLI1.0.97 in disposable control directories; built-in copilot disk unchanged; three genuine workflows verified |
| Identity | Secretless Entra PKCE/API validation; app UAMI for Blob/Sandboxes; separate DCR ingestion identity; build-only AcrPush/OIDC identity |
| PAT | Manually configured group credential; same-PAT private creation/push passed after user correction; no interactive login or credential substitution |
| Azure | Existing academo deployment in Sweden Central is healthy; UAMI data access and all-role telemetry verified |
| Release | GitHub OIDC image build/push and existing-local-state Terraform digest deployment passed |
| External validation | Browser availability for final transport/presentation drills; separate empty subscription/tenant for an actual clean-customer install |

## 5. Technical risks and resolution criteria

| Risk | Impact | Resolution / evidence required |
| --- | --- | --- |
| Preview API/schema drift | Invalid resource fields or misleading successful validation | Stable 2026-07-01 template currently exposes `environmentId`; official rich-preview module uses 2026-02-01-preview and disables schema validation. Verify target resource-provider contract and read-back behavior; do not copy mixed schemas |
| Built-in image changes | Documented CLI features may be missing on the actual disk | Discover `copilot`, record disk metadata and in-sandbox CLI version; real workflow test; stop if incompatible |
| Copilot entitlement/billing | Valid PAT and ordinary Copilot access may still reject workflows | Check eligible plan and run actual workflow; retain sanitized `dynamic_workflows_unavailable` error if returned |
| Extension trust and prompt injection | Target repository can load executable configuration or redirect agents | Trusted control directory, explicit tool permissions, disabled target instructions/config auto-loading; malicious-config negative tests |
| Credential exposure inside B/C | Repository code may read/exfiltrate a PAT with create/write rights to the demo owner's current/future repositories | Vetted harmless fixture allowlist, disposable personal account, short expiry, scoped tested egress and post-demo revocation; MicroVM isolation does not protect the token from code in the same VM. Production requires credential separation |
| PAT injection and publication permissions | Copilot authenticates but GitHub API/git cannot create or push | Verify the same injected token's supported access boundary, personal ownership, endpoint permission headers and actual private test push after approval; stop publication if unsupported, no credential substitution |
| Validation/publication gate | Invalid fix could publish or an AI prompt could bypass checks | Trusted workflow code requires successful build/tests and targeted recheck; failed/missing/timed-out checks skip all writes; observe real failing-tests and passing branches |
| Destination collision / partial write | Retry overwrites an existing repo or reports false success | Check owner/name/privacy, reconcile ambiguous responses, track created repository identity, verify remote SHA; collisions fail, partial publication is explicit, no automatic remote deletion |
| Source sanitization | New repo contains old history, secrets or unwanted artifacts | Fresh Git history; checked source manifest including new files, preserved license/attribution, secret/artifact exclusions and post-push verification; do not grant unrelated Workflows permissions to bypass a rejected push |
| Storage authorization | Durable reports require app UAMI data access | Current network configuration is reachable. UAMI grants exist at all four containers; verify actual access from deployed host. No network changes authorized or needed |
| Egress controls | Deny rules break Copilot, clone, package installation, repository creation or push | Build allowlist from official Copilot/GitHub API/git endpoints and locked dependencies; validate TLS/inspection and denied destinations; determine IaC support for persistent policies |
| SDK output/cancellation limits | Dashboard may lag and timed-out remote work may continue | Observe exec/file semantics; prove polling or supported streaming; explicit deadlines and process termination; delete owned sandbox as final containment |
| Process restart / creation race | Orphans, lost events or duplicated work | Durable ownership intent, labels and reconciliation; idempotent cleanup; interrupted status; no automatic recovery claim |
| Authentication and SSE | Unauthorized costs, spoofed principal headers, cross-owner reads | Validate Entra issuer/audience/principals server-side; establish proxy trust, CSRF/same-origin policy, session expiry and SSE resume rules through Azure tests |
| Secret-free authentication | Default portal setup creates a client secret | Evaluate documented existing-registration secret-free option and its token-flow tradeoffs; validate before adopting; do not introduce secrets into state to make login work |
| CI/CD state and bootstrap | Lost state, missing image or competing image owners | Preserve existing local state, serialize inspected deployments, and use Terraform as image owner |
| Fifteen-minute timing | Provisioning, dependency and AI latency vary | Small vetted fixture, bounded stages, measure real runs, rehearse, keep honestly labeled genuine replay |
| Local prerequisites | Packages, SDK and Docker now available | Preserve hash-locked dependencies, public-registry lockfiles and proxy overrides; local checks do not establish Azure runtime compatibility |

## 6. Verification and acceptance criteria

Tests must verify observable behavior and security boundaries. Use explicit doubles only in unit tests. Cloud tests run only with approved create/delete scope. Record exact versions, commands, outcomes and unresolved limitations after each slice.

| Layer | Planned checks |
| --- | --- |
| Source/CI | Python lint/type/unit checks, strict schema validation, TypeScript checks/build, dependency and secret checks; no target repository execution |
| Authorization | Missing/invalid/expired/wrong-tenant identities; principal allowlist; owner-only reports/SSE/remediation/cleanup; spoofed headers; CSRF; no unauthenticated side effects |
| Inputs/reports | Reject URL tricks/redirects/private targets, unsupported projects and malformed SHA; cap payloads; reject extra fields and invalid evidence/test counts; treat missing AI results as failures |
| Orchestration | Prove A/B concurrency and same SHA; single-run admission; retry/cancel/timeout; ambiguous create; duplicate approval; partial failures and deletion retries |
| C workflow/publication | Genuine registered workflow with actual fix step and deterministic pass/fail gate; failed validation makes zero remote writes; approved private test create/push with same injected PAT; verify owner/privacy/URL/SHA; name collision, rate-limit, permission, ambiguous/partial push and sanitization tests; source unchanged |
| Persistence/SSE | Redaction before every sink; ordering, duplicate handling, heartbeat, resume beyond ring buffer, interrupted run recovery, retention and purge authorization |
| Dashboard A/B/C | Three genuine workflow timelines with real stage/branch/skip evidence; C validation/gate/create/push/remote verification and clickable verified URL/SHA; reconnect/replay preserves outcomes, failed/partial publication never looks successful; cleanup visible |
| Terraform | `terraform fmt -check -recursive`, `terraform init`, `terraform providers schema -json`, `terraform validate`, saved `terraform plan`; approved apply plus resource read-back; never represent validate alone as runtime support |
| Azure integration | Real Copilot-backed A/B/C, least-privileged managed identity, functioning Entra login, private Blob persistence, constrained egress, actual cleanup |
| Demo/customer | HTTPS-only deployed host, usable 1080p dashboard, genuine replay, practiced 15-minute script, precise clean-subscription deployment steps and owned-resource teardown |

Final acceptance checklist:

- [ ] All static resources are skill-compliant Terraform-managed, with working clean-customer deployment and validated providers.
- [x] The application runs on Azure HTTPS with Entra sign-in and server-side authorization; no local host dependency.
- [x] ACR contains only the application image; A/B/C use the service-provided Copilot disk.
- [x] Same manually configured personal-owner group PAT supports Copilot and C publication with verified permissions/injection; never present in source/state/build/app/browser/event artifacts, and no interactive login is required.
- [x] A/B are separate and concurrent at one SHA; two real registered Dynamic Workflows expose observed branches and evidence.
- [ ] Private Blob persists sanitized reports/events/diffs; authorized SSE reconnect recovers missed events.
- [x] One explicit Fix Vulnerability confirmation authorizes C's third genuine Dynamic Workflow and disclosed private destination; deterministic failed validation prevents repository creation/push, successful validation leads to sanitized-source creation/push and verified `fixed_repository_url`/commit SHA. No backend publisher or second Publish button; origin unchanged.
- [x] All three Dynamic Workflows are observable in React with actual steps/logs/branch reasons, validation results and lifecycle/cleanup. C includes diff, publication stages and a verified repository link; no fabricated success or replay side effects.
- [x] C persists sanitized report/diff/publication outcome to Blob before sandbox deletion; collisions and partial remote publication are visible and never silently overwritten/deleted.
- [ ] Failure, timeout, cancellation, restart and orphan scenarios have accurate status and owned-only cleanup.
- [x] OIDC CI/CD and the manual bootstrap path have one image owner and a durable state strategy.
- [ ] A genuine successful run is recorded, the demo is rehearsed, and security/cost/timing limitations are documented.

## 7. Current execution checkpoint

M0-CLI97 and M0-C-FAIL passed. Telemetry infrastructure, Entra and the Azure host are deployed; anonymous operational calls return 401 and browser sign-in succeeds. Workflow-correlated LAW ingestion, same-PAT C publishing, concurrent A/B and authenticated A/B/C dashboard/replay passed. Complete live operational drills and presentation/customer-install acceptance. The public vetted fixture is published. The user explicitly requires existing LOCAL state; no migration. Continue without routine milestone approvals.

## Foundation and revised-scope checkpoint — 2026-10-13 (historical)

The user previously approved foundation implementation, then explicitly approved applying the exact saved plan. Deployment completed on 2026-10-12: 23 created, 0 changed, 0 destroyed; see [progress](./docs/progress.md) and private [deployment results](./.local/azure-discovery/deployment-results.md). Preserve [academo-swedencentral.tfplan](./infrastructure/terraform/academo-swedencentral.tfplan), SHA-256 `386fceff8f67a42d8e51f20d6bf521b59fc4244a5e8e3186d8cbe76178178622`, as the already-applied artifact; do not reuse or regenerate it. The user now requests plan/checklist alignment to the revised [AGENTS.md](./AGENTS.md) and [README.md](./README.md). C implementation, publication capability and all runtime tests remain incomplete. Prior approval covers no new infrastructure or GitHub action.
