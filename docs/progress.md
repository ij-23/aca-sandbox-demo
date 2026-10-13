# Development progress

## Current status — 2026-10-13

**Latest comparison after the user's 1.0.97 report:** static inspection of the checksum-verified official 1.0.97 package confirms `defineWorkflow`, workflow registration, direct command dispatch and result handling. No CLI upgrade is justified for a sandbox already using that version. The target group currently lists only protected sandbox `5bf17eda-250b-4c90-9cd6-bd44a5610851`, now Running; read-only exec reports **1.0.83** as `root` from `/usr/local/bin/copilot`. Its portal preset label/private disk reference differs from our public-disk create request, but that does not explain the version mismatch conclusively. Asked the user to identify the sandbox/portal URL that showed 1.0.97. No new sandbox, lifecycle change, workflow execution, credential change or Terraform change occurred. See [comparison evidence](./compatibility.md#current-comparison-user-reported-cli-1097--2026-10-13).

**Latest static investigation:** official CLI 1.0.83 has the global experimental switch and project-extension trust opt-in, but its bundled SDK exports `defineFactory` / `factories` instead of the documented `defineWorkflow` / `workflows` registration. The verified release package also lacks the direct workflow command options. This replaces the insufficient help-only inference with concrete package evidence; see [compatibility investigation](./compatibility.md#static-cli-1083-investigation--2026-10-13). No new sandbox, Azure API call, CLI upgrade or agent execution occurred. The saved Terraform plan hash remains unchanged. A compatible image/CLI and a newly approved live test remain necessary; no working Dynamic Workflow run is claimed.

**Milestone 0 remains blocked on genuine Dynamic Workflow execution.** The reusable harness now attaches the existing Ready provider credential connection. One newly approved sandbox confirmed Copilot **1.0.83** and injected `COPILOT_GITHUB_TOKEN`, but `copilot --no-auto-update --experimental workflow run --help` returned general help with no workflow subcommand/`--args`/`--result-file`. The harness stopped at that capability gate, before workflow extension upload/execution. No workflow outputs, steps or live progress were produced. Creation **1.010s**, finally cleanup **6.879s**, total **13.529s**; exact-ID GET **404** verified. The pre-existing sandbox remains Stopped and untouched. No additional sandbox, credential/Terraform change, GitHub write, CLI upgrade or application development occurred.

Implemented the [Terraform foundation](../infrastructure/terraform/), [smoke harness](../scripts/smoke_test_sandbox.py), [real workflow extension](../workflows/smoke/extension.mjs), and [deployment guide](./deployment.md). Application development remains blocked on real Milestone 0 evidence.

**Revised scope:** A/B run genuine concurrent Dynamic Workflows; one **Fix Vulnerability** approval starts C's third genuine Dynamic Workflow for fix, deterministic validation, private `{repo}-fixed` creation/push inside C using the same group PAT, and verified repository URL/SHA. All three workflows must be observable in React. The [plan](../PLAN.md) and checklist reflect this requirement; C implementation and publication verification remain undone. The [README](../README.md) defines the current PAT requirements; successful Copilot authentication does not establish publication readiness. This diagnosis was limited to one disposable runtime sandbox and preserved all Terraform artifacts.

## Skills and project-specific precedence

- Read the complete `terraform-builder` skill at `/Users/ij/.agents/skills/terraform-builder/SKILL.md`. An additional installed copy exists at `/Users/ij/.codex/skills/terraform-builder/SKILL.md`. The selected skill directory contains only its instruction file, with no separate mandatory templates.
- Followed the skill for Terraform implementation: Microsoft Learn grounding, concern-based modules, relative sources, typed/described inputs, parameterization, provider constraints, state handling, validation and Terraform-owned static teardown.
- **Recorded override:** project instructions require `infrastructure/terraform/`, overriding the skill's generic `iac/` directory. No clarification is needed to follow the explicit project requirement.
- **Recorded override:** project runtime sandbox cleanup is performed through the SDK; generic skill static-resource teardown guidance does not replace that runtime requirement. Terraform still owns static Azure-resource teardown.
- Local Terraform state is the skill default. A durable Azure Blob backend is proposed for Actions, but must be explicitly requested before adding backend configuration. No backend has been created.
- Read `/Users/ij/.agents/skills/documentation-keeper/SKILL.md`; apply its factual tracking and audience separation to the project-mandated plan/progress/compatibility files. Do not create a competing `AGENT.md` source of truth or rewrite the canonical deployment README with untested commands.

## Task checklist

### Milestone 0 — discovery and viability

- [x] Read complete project instructions and README before editing.
- [x] Inspect repository contents and Git status.
- [x] Discover/read mandatory Terraform skill; record path and precedence decisions.
- [x] Inventory local Terraform, Azure CLI, Git/GitHub CLI, Node/npm, Python, Copilot and container tooling.
- [x] Review Microsoft Learn via its MCP tools, Microsoft Sandbox portal docs, GitHub docs and official workflow SDK source.
- [x] Confirm documented public `copilot` disk and group-scoped provider-credential procedure.
- [x] Confirm documented programmatic workflow definition/registration and direct invocation; inspect local CLI help without running an agent.
- [x] Record source-confirmed facts separately from untested runtime assumptions.
- [x] Produce architecture, milestones, dependencies, risks and acceptance plan.
- [x] Prepare findings, blockers and proposed sequence for delivery at this planning checkpoint, before implementation.
- [x] Re-read updated AGENTS.md/README.md and align PLAN.md/checklist with all three genuine Dynamic Workflows, one Fix approval, deterministic C publication and React observability (2026-10-13).
- [x] Resolve SDK download problem using pip's configured Microsoft proxy explicitly in uv; install pinned isolated dependencies and verify SDK import.
- [x] Inspect installed SDK signatures/source; verify DefaultAzureCredential access, one create/exec/get/delete lifecycle and completed stdout/stderr/exit codes. File transfer, workflow capture, concurrent polling and timeout-path behavior remain untested.
- [ ] Inspect installed provider runtime schemas, API contracts, authConfig support and group-policy ownership.
- [x] Retrieve intended subscription/tenant and initial User operator via authorized CLI discovery; Sweden Central/prefix academo selected. Approved foundation deployed.
- [x] Verify target quota, role definition and read-only public-image metadata; deployed group lists `copilot` as Ready.
- [x] Prepare genuine workflow with deterministic preparation, `ctx.agent`, actual-result conditional verification, structured per-step outputs and boundary events; update bounded harness for provider binding, file delivery/polling and finally cleanup. Fourteen local unit tests passed; genuine live execution remains blocked by CLI capability gate.
- [ ] Verify official GitHub personal-owner repository creation API/permission requirements, `X-Accepted-GitHub-Permissions`, account restrictions and actual git push requirements; do not assume creation grants push.
- [x] Verify Sandbox Group Copilot credential configuration and runtime injection (2026-10-13): API Ready maps to portal Configured; explicit connection binding injects `COPILOT_GITHUB_TOKEN`. Only set/unset booleans reported, no credential values collected.
- [ ] Verify updated demo publication PAT capability: disposable personal owner/Copilot seat, Copilot Requests, Repository creation: Write, Contents: Read and write, current/future repository access and short expiration. Configuration confirmation alone does not prove these permissions; publication testing is outside current approval.
- [x] Obtain explicit approval for one disposable SDK sandbox in the deployed group, trusted prompt and genuine workflow, strict timeouts and deletion; no repository creation, public ingress, Terraform or app changes (2026-10-13).
- [x] Reverify approved group ARM state, copilot Ready status and authenticated sandbox inventory; leave the pre-existing stopped sandbox untouched.
- [x] Execute exactly one SDK smoke attempt with trusted prompt, no ports and no third-party repository; finally delete and verify exact-ID 404. Automatic Copilot authentication failed; workflow execution was not reached.
- [x] Diagnose automatic credential binding for SDK `disk="copilot"`: omitted `connections` caused the previous failure. Existing Ready connection attached in one newly authorized sandbox; same CLI 1.0.83 prompt succeeded without login or manual token injection; finally cleanup and GET 404 verified.
- [x] Incorporate verified connection-ID binding into reusable smoke harness; require existing Ready connection ID and verify returned attachment. Live workflow-capability attempt confirmed injection (2026-10-13). Application adapter remains future work.
- [x] Check in-sandbox workflow help with `--experimental` in one newly approved sandbox: CLI 1.0.83 returned identical general help, without the documented direct workflow command. Exact-ID cleanup verified (2026-10-13).
- [x] Investigate CLI 1.0.83 statically beyond help: verify official release checksum, actual extension exports/registration, experimental handling, documented extension paths and trust opt-in. Confirm the standard release lacks the required Dynamic Workflow API; distinguish this from an actual in-image import test.
- [x] Inspect official CLI 1.0.97 package and confirm genuine workflow API/registration/direct-command implementation. Compare existing sandbox metadata and read-only executable version without creating or upgrading anything.
- [ ] Identify the user-reported 1.0.97 sandbox/executable and resolve its difference from the target group's root exec environment (1.0.83); preserve the existing sandbox. Adjust the harness's explicit reviewed-version gate before an approved test on a compatible version.
- [ ] Select a compatible built-in image or explicitly approved pinned CLI version and obtain a new sandbox approval before live verification. Do not automatically upgrade, substitute factory/prompt execution, or reuse the consumed one-sandbox approval.
- [ ] Execute real smoke; record credential success, workflow registration/AI step/branch, structured output, actual transport and verified deletion.
- [ ] Implement/exercise a genuine C Dynamic Workflow PoC inside an approved sandbox; prove failing build/tests or targeted recheck branches to a report with repository creation/push skipped and no remote write.
- [ ] Verify the same group-injected PAT is accessible through a supported GitHub API/git authentication path inside C without revealing/copying it to the host; block publication if unavailable, no alternate credential/backend publisher.
- [ ] Obtain separate approval for exact disposable private test-repository owner/name, harmless content, create/push action and sandbox scope; then verify private repository creation, harmless push and remote owner/URL/SHA using that same injected credential.
- [ ] Record real C branch/publication evidence and owned-sandbox cleanup; retain partial test-repository outcomes transparently. Remove a test repository only after further explicit approval.
- [ ] Mark viability gate passed only after all runtime evidence succeeds.

### Milestone 1 — Terraform foundation

- [x] Select local state for this bootstrap and lock AzureRM 4.81.0 / AzAPI 2.13.0 for Darwin ARM64 and Linux AMD64. CI backend remains a later explicit decision.
- [x] Author bootstrap modules, typed inputs, example configuration and required outputs; application URL is empty until the later real-image phase.
- [x] Implement and deploy scoped identities/RBAC, private blob containers/retention and telemetry; resource/grant read-back verified, UAMI runtime integration remains untested.
- [ ] Resolve group limits/egress and Entra auth through verified APIs; any Terraform/infrastructure change needs separate approval.
- [x] Run formatting, inspect installed provider schemas and validate; five offline Terraform tests pass.
- [x] Produce real saved foundation plan with discovered identity, Sweden Central, academo prefix and signed-in User operator: 23 additions, no changes/deletions.
- [x] Present plan; apply exact saved plan after explicit approval; verify all resources and record policy-imposed Storage deviation.
- [ ] Resolve policy-imposed Storage connectivity blocker through a separately reviewed and approved design before app deployment.

### Milestone 2 — application image and CI/CD

- [ ] Create React/FastAPI host and multi-stage Dockerfile.
- [ ] Implement server-side authorization, Blob persistence and health/readiness endpoints.
- [ ] Implement platform-only CI tests and OIDC build/push/Terraform deployment with one image owner.
- [ ] Validate image and approved Azure HTTPS deployment, login and managed identity access.

### Milestone 3 — real A/B execution

- [ ] Implement vetted repository URL validation and immutable SHA resolution.
- [ ] Implement strict event/report schemas for all three workflows, redaction and ownership ledger; C report includes validation, publication outcome, `fixed_repository_url` and verified commit SHA on success.
- [ ] Implement SDK adapter, concurrent A/B orchestration, quotas and timeouts.
- [ ] Implement real security and build Dynamic Workflows with observed branches.
- [ ] Verify real A/B results, cancellation, partial failure, restart reconciliation and cleanup.

### Milestone 4 — observability dashboard

- [ ] Implement lifecycle cards and genuine Dynamic Workflow timelines for A, B and C: concurrent A/B and full C timeline after Fix approval; real logs, timestamps, branch/skip/retry evidence and cleanup states.
- [ ] Implement single Fix Vulnerability confirmation disclosing selected finding, immutable source and private destination creation/push; no separate Publish button.
- [ ] Show C stages `checkout`, `agent.fix`, `validate`, `publication.gate`, `create_repo`, `push`, `verify_remote`, `complete`; validation results/diff, failure or partial-publication status, and clickable verified repository URL/commit SHA.
- [ ] Verify authenticated SSE resume/heartbeat and durable history beyond ring buffer for all three workflows, including C branch/publication events; disclose polling if true streaming is unavailable.
- [ ] Verify genuine replay includes A/B/C timelines and publication outcome while performing no sandbox or GitHub side effects; no synthetic live events.
- [ ] Validate 1080p presentation layout and actual data; enable replay only when genuine recording exists.

### Milestone 5 — approved remediation and publication Dynamic Workflow

- [ ] Bind one Fix Vulnerability approval to user/run/finding/source SHA/destination/attempt; enforce ownership and reject duplicate, stale or concurrent requests. No C before consent and no second publication approval in the product flow.
- [ ] Implement C as a third trusted registered Copilot Dynamic Workflow; only fix selection/patch reasoning goes to Copilot, deterministic code controls validation and publication.
- [ ] Execute pinned checkout, bounded fix, build/tests and targeted security recheck; capture reviewable diff including new files. Failed, missing or timed-out required validation reports failure and skips all remote writes.
- [ ] On success, verify personal destination owner and name availability; collisions fail without overwrite. Create private `{original-name}-fixed` inside C through the verified API with the same group PAT.
- [ ] Commit/push checked sanitized fixed source with fresh history, including new files and license/attribution; exclude old `.git`, credentials, `.env`, runtime artifacts and secret-bearing fixtures; original repo/remote unchanged.
- [ ] Verify remote owner/name/private visibility and pushed SHA before returning successful `remediation.json` with `fixed_repository_url`, commit SHA, diff and validation evidence.
- [ ] Handle API/git permission errors, rate limits, name collisions, ambiguous create/push responses, timeouts and partial publication with observable reasons; reconcile before retries, no overwrite or automatic remote deletion.
- [ ] Persist sanitized diff/report and publication outcome to Blob before deleting C; expose persistence failures and preserve recovery/cleanup tracking. Resolve the Storage connectivity blocker before app-integrated C testing.
- [ ] Exercise real passing and failing C branches, UI timeline/reconnect/result link, stale/duplicate consent rejection and cleanup; verify original repository unchanged and no success reported without remote verification.

### Milestone 6 — customer readiness

- [ ] Finish verified README, deployment/security/architecture guides, examples and OSS licensing.
- [ ] Capture genuine successful JSONL replay covering all three workflows, including C validation branch/private publication/verified URL and cleanup; sanitize it and preserve provenance.
- [ ] Finish and rehearse 15-minute script, screenshots and failure/replay drill.
- [ ] Rehearse clean-customer installation, orphan cleanup and approved static teardown.
- [ ] Reconcile every acceptance criterion in [AGENTS.md](../AGENTS.md).

## Initial discovery verification record (historical)

All checks below are local inspection or public documentation requests, not cloud feature tests.

| Command/check | Result |
| --- | --- |
| `rg --files --hidden -g '!.git'`, `ls -la` | Initial workspace had only AGENTS.md and README.md |
| `cat AGENTS.md README.md`, bounded follow-up reads | Both complete files reviewed; follow-up reads recovered truncated tool output |
| `git status --short` | Exit 128: workspace not initialized as a Git repository |
| `cat /Users/ij/.agents/skills/terraform-builder/SKILL.md` | Full skill read; directory discrepancy recorded above |
| `terraform version` | 1.15.3, Darwin ARM64 |
| `az version` | 2.83.0; containerapp extension version shown as `Unknown` |
| `node --version`, `npm --version` | 24.13.1 and 11.8.0 |
| `git --version`, `gh --version`, `uv --version` | Git 2.54.0; GitHub CLI 2.92.0; uv 0.10.8 |
| `copilot --version`, `copilot --help`, `copilot workflow run --help` | 1.0.91; workflow command and JSON input/result flags present; no agent invocation |
| Python environment tools | Initially system 3.9.6; found and selected `/opt/homebrew/bin/python3.13` at 3.13.16; only pip/wheel reported, no sandbox SDK |
| Container configuration tool; `docker version --format '{{json .}}'` | Docker client 29.2.1; exit 1, server unavailable at desktop socket |
| Node HTTPS GET of PyPI metadata | SDK 0.1.0b4; requires Python >=3.10 |
| Node HTTPS GET of Terraform Registry provider metadata | AzureRM 5.9.0, AzAPI 2.13.0, AzureAD 3.10.0; candidate metadata only |
| Microsoft Learn search/fetch | Reviewed overview, Python quickstart, Sandbox Group ARM template and Entra auth; identified authConfig schema for follow-up |
| Official GitHub docs and raw SDK guides | Confirmed code-based workflow API, extension discovery, direct run, result behavior and eligibility caveats |
| Official pinned Terraform module source | Rich-preview fields use 2026-02-01-preview and disabled schema validation; must reconcile with stable template/runtime |
| Python HTTPS metadata/download attempt | Failed with `URLError: [Errno 9] Bad file descriptor`; no package inspected |
| Node wheel-download attempt | Failed with `TypeError: fetch failed`, `ENOTCONN`; no SDK install/source validation completed |
| Documentation validation | All required plan sections present; all nine relative links resolve; editor diagnostics report no errors in the three new documents |

## Foundation verification record — 2026-10-12

| Command/check | Result |
| --- | --- |
| `git init -b main` | Initialized; no commit or remote publication |
| `terraform init -input=false` | AzureRM 4.81.0 and AzAPI 2.13.0 installed |
| `terraform providers schema -json` | Runtime schemas inspected alongside official ARM contracts and pinned AzureRM source |
| `terraform providers lock -platform=darwin_arm64 -platform=linux_amd64` | Both platform checksums saved |
| `terraform fmt -check -recursive`, `terraform validate` | Passed after documenting the Sandbox Group schema exception |
| `terraform test` | 5 passed, 0 failed; mock providers, no Azure calls |
| `.venv/bin/python -m unittest discover -s scripts/tests -v` | 8 passed; explicit doubles test consent, provenance and owned-only cleanup including failures |
| `node --check workflows/smoke/extension.mjs` | Passed syntax check; no local Copilot execution |
| SDK install via environment tool and uv | Blocked by connection failure to files.pythonhosted.org; package signatures not yet verified |
| `.venv/bin/python scripts/verify_environment.py` | Blocked: required SDK absent; Python, Terraform and Azure CLI present |
| `terraform plan -input=false -no-color` | Exit 1: required subscription_id, tenant_id, region, name_prefix missing; no saved plan |

Only Sandbox Group disables AzAPI embedded schema validation because installed AzAPI 2.13.0 does not contain that resource type. The minimal body follows the published stable ARM contract. This exception is not service validation. Storage and Log Analytics use validated AzAPI ARM schemas to avoid shared-key reads into state; other supported resources use AzureRM. Provider automatic registration is disabled in both providers. See [compatibility](./compatibility.md) for exact APIs.

## Blockers and next action

1. Foundation apply/read-back are complete and saved plan unchanged. The authorized one-sandbox smoke was attempted and its sandbox deleted with exact-ID 404 confirmed; see private [live results](../.local/live-smoke/results-2026-10-13.md). Do not create another sandbox under that consumed approval.
2. SDK installation/signature inspection/basic lifecycle pass. Diagnose missing automatic Copilot authentication for the public-disk path and check experimental workflow support before the next approved runtime attempt. DefaultAzureCredential used the existing CLI account with the intended subscription temporarily selected; the previous default was restored.
3. Sandbox Group stable creation, authenticated operator inventory and one sandbox command lifecycle succeeded. UAMI identity/scoped grants exist; UAMI runtime access and successful Copilot execution remain untested. The deployer has inherited Owner; Contributor alone could not grant RBAC.
4. Resolve group limits/persistent egress against a supported API before repository evaluation. App Entra auth, host UAMI integration, CI OIDC and durable CI state remain later work.
5. Azure Policy `StorageAccount_PublicNetwork_Modify`, assigned through `MCAPSGovDeployPolicies`, disabled Storage public network access. No private endpoint exists. Resolve connectivity for the future app through a separately reviewed design; no policy/network change is authorized by this deployment. This does not block group PAT setup or the trusted nonce smoke, which does not use Blob.
6. Updated publication requirements are unverified: dedicated personal GitHub owner, API/git permissions and same group-injected PAT access must be confirmed inside an approved disposable sandbox. C PoC, failed-validation/no-write evidence and separately authorized private test create/push are now Milestone 0 gates. The existing nonce smoke does not cover them.
7. Align compatibility/deployment guidance with verified publication evidence during the next authorized implementation slice; retain prior deployment evidence as historical. Do not treat the old Copilot-only PAT instructions as sufficient for C.

One real sandbox lifecycle/failed-prompt test and verified cleanup now exist. No successful credential-backed workflow or genuine demo replay exists. Milestone 0 remains incomplete; application development stays paused.

## Azure discovery and saved planning — 2026-10-12 (historical)

- Re-read the complete `terraform-builder` skill at `/Users/ij/.agents/skills/terraform-builder/SKILL.md` and the project instructions/README. Followed Microsoft Learn grounding, locked providers, existing concern-based modules, local state and fmt/validate/plan. The project-specific `infrastructure/terraform/` layout override still applies. Re-read `documentation-keeper` and updated the canonical README plus project-mandated progress/compatibility/deployment ledgers.
- Used existing Azure CLI authentication; no login, context switch, credential changes, provider registration, resource creation or role grant. Verified Enabled/default subscription and tenant twice; Graph returned the signed-in user Object ID, and role assignments corroborated principal type User. Identifiers are retained only in ignored customer-specific inputs/review.
- Effective subscription permission response includes `actions: ["*"]`, no exclusions; inherited Owner is unconditional. Existing SandboxGroup Data Owner at subscription scope was discovered and left untouched. Planned operator assignment is scoped only to the new group.
- All six service namespaces are Registered. Stable 2026-07-01 and preview 2026-02-01-preview Sandbox Group list calls succeeded; two existing Sweden Central groups were read only and excluded from this plan. Regional quota returned SandboxCores 0/20000 and ManagedEnvironmentCount 1/50. Relevant deny assignments were confined to unrelated managed groups; no locks found. Visible policy initiatives concern SQL/relational services.
- Official stable schema has no group limit/timeout/egress fields. Preview controls are documented but persistence/enforcement is untested. Microsoft documents per-sandbox create-time egress; omitted policy permits unrestricted outbound. No static group-wide Terraform policy contract was verified. Repository evaluation remains gated on these controls.
- Added git-ignored local Terraform inputs with `swedencentral`, `academo`, the discovered subscription/tenant and initial operator. Global ACR and Storage name checks returned available; no target resource group collision was found.
- `terraform init -input=false -lockfile=readonly`, `terraform fmt -check -recursive`, `terraform validate`, and saved `terraform plan` succeeded. JSON inspection confirmed every one of 23 resource actions is create; no app/sandbox workload or existing-resource change is included. Saved plan SHA-256 is recorded in the private review.
- No Terraform resource definitions changed. The existing narrow Sandbox Group embedded-schema exception remains. Service write acceptance, installed sandbox SDK verification, real Copilot smoke, credentials, application authentication and runtime controls remain open. No fabricated execution evidence or replay was produced.

## Final pre-apply review — 2026-10-12 (historical)

- Completed the private [final review](../.local/azure-discovery/preapply-review.md), covering all 23 individual additions, exact eight RBAC scopes and live role-definition permissions, public endpoint exposure, monthly baseline estimates, existing-resource protection, smoke prerequisites and saved-plan validity.
- Preserved the original binary plan and its SHA-256. A separately saved fresh plan matches configuration, variables, planned values, resource/output changes, prior state and checks. All 25 embedded Terraform source files and the provider lock file are byte-identical to current files. Validation passed; all resource actions remain create, with no updates, replacements, imports or deletes.
- Rechecked active subscription/tenant, effective resource/RBAC permission, resource-group absence and global ACR/Storage name availability. No identity or name blocker was found. No existing Azure resource or assignment was changed.
- Retrieved Sweden Central USD retail rates: ACR Basic $0.1666/day, Hot LRS Blob $0.0184/GB-month, writes $0.05/10K, reads $0.004/10K, paid Analytics Logs ingestion $2.99/GB. Estimated idle foundation around $5/month; light usage $5–10/month, with explicit assumptions/exclusions in the review. Telemetry caps are not total budget caps.
- The foundation is sufficient for a later trusted smoke attempt, but SDK installation/inspection, manual group PAT setup, built-in image/workflow proof and separately approved sandbox creation remain prerequisites. The smoke currently supplies neither a create-time egress policy nor a service-side TTL; this is disclosed and must not be mistaken for hardened repository evaluation.
- **No apply is authorized or executed. Awaiting the user's final foundation deployment approval.** No Terraform source or input changed during this review.

## Approved foundation deployment — 2026-10-12

- Re-read the complete installed `terraform-builder` skill at `/Users/ij/.agents/skills/terraform-builder/SKILL.md`; retained the project-required layout, locked providers, local state and exact reviewed configuration. Followed `documentation-keeper` using the existing project-mandated ledgers and canonical README.
- After explicit user approval, verified saved plan SHA-256 `386fceff8f67a42d8e51f20d6bf521b59fc4244a5e8e3186d8cbe76178178622` and ran only `terraform -chdir=infrastructure/terraform apply -input=false -no-color academo-swedencentral.tfplan`. Exit 0: **23 added, 0 changed, 0 destroyed**. No replacement plan was generated or applied. The consumed saved plan must not be reapplied.
- Read all 23 Terraform-managed resources individually through ARM/diagnostic-settings APIs. Every read succeeded; all resources exposing provisioning state returned `Succeeded`. Verified four private containers, 30-day lifecycle retention, disabled shared-key/local authentication, diagnostics, ACR Basic and the Consumption environment. Exact names, identities, scopes and evidence are in the private [deployment results](../.local/azure-discovery/deployment-results.md).
- Verified the UAMI tenant/client/principal IDs and all eight RBAC assignments against state: AcrPull at ACR; SandboxGroup Data Owner at the group for UAMI and initial User; Monitoring Metrics Publisher at App Insights; Storage Blob Data Contributor separately at each of four containers. Existing grants were not modified. UAMI runtime authorization remains untested until a host is deployed.
- Sandbox Group stable `2026-07-01` read-back returned `Succeeded` and its Sweden Central management endpoint. `aca` CLI `1.0.0-preview.2` authenticated listing returned zero sandboxes; public disks include built-in `copilot` with state `Ready`. Container App listing returned zero apps. This proves group read availability, not sandbox creation, Copilot credentials or Dynamic Workflow execution.
- **Policy deviation:** Storage live `publicNetworkAccess` is `Disabled`; approved plan/state body requested `Enabled`. Activity Log records successful `Microsoft.Authorization/policies/modify/action` at `2026-10-12T20:36:05.7589109Z`, caused by management-group assignment `MCAPSGovDeployPolicies` and definition `StorageAccount_PublicNetwork_Modify`. No private endpoint exists. This post-deployment finding supersedes the earlier discovery assumption about visible policy scope and the pre-apply public Blob endpoint description. No policy, network setting or existing resource was changed to work around it; configuration is not fully converged with the approved plan.
- Updated deployment/compatibility guidance and PAT handoff. **Stopped after verification:** user must configure the PAT manually and explicitly approve proceeding. No token collected, sandbox created, Container App deployed or Milestone 0 smoke executed.

## Three-workflow plan alignment — 2026-10-13

- Re-read the user's updated AGENTS.md and README.md in full. Updated only PLAN.md and this tracker; retained previous deployment records as historical evidence.
- Defined C as a third genuine registered Dynamic Workflow with observable checkout, Copilot fix, validation, deterministic publication gate, private repository creation, sanitized-source commit/push, remote SHA verification and completion. One Fix Vulnerability confirmation covers the disclosed operation; no second Publish button or backend publisher.
- Added requirements for React visibility across A/B/C, actual branch/skip/failure evidence, C diff/tests and verified destination link, SSE resume, genuine replay and cleanup. Added explicit collision, permission, partial-publication, secret-exclusion and evidence-persistence acceptance checks.
- Expanded Milestone 0 to include C's failing-tests/no-write branch and separately approved private test creation/push with the same injected PAT. All new implementation/runtime checklist items remain unchecked. Credential configuration, SDK access, publication permission/injection and Storage connectivity remain open gates.
- Checked 22 relative documentation links and required C stage/report terms successfully. Verified the saved foundation plan's SHA-256 before and after edits: `386fceff8f67a42d8e51f20d6bf521b59fc4244a5e8e3186d8cbe76178178622`, unchanged. No Terraform command, infrastructure edit, Azure call, credential change, sandbox execution or GitHub write occurred in this update.

## Authorized live smoke preflight — 2026-10-13

- User confirmed manual group PAT configuration and explicitly authorized one disposable sandbox through the official SDK for a minimal prompt and genuine workflow, with strict timeouts and deletion. No GitHub repository creation, third-party clone, public ingress, Terraform change or Container App deployment is permitted by this scope.
- Configured the existing isolated Python 3.13.16 environment. Reviewed the prepared smoke harness/extension and re-fetched the official Microsoft Learn SDK quickstart. Package-install tool failed; fallback `uv pip install --python /Users/ij/Dev/aca-sandbox-demo/.venv/bin/python -r requirements-smoke.txt` failed after three retries at the PyPI wheel-metadata URL. Direct official wheel/source downloads, including IPv4/HTTP1.1, also failed with curl exit 35 / socket not connected. Requests used bounded timeouts. Metadata is reachable; no cached SDK was found. Did not replace the SDK with CLI resource creation or run unverified calls.
- Explicit target ARM read succeeded: group state Succeeded, Sweden Central endpoint. `aca sandboxgroup disk list-public` returned built-in `copilot` Ready. Initial CLI default was a different tenant; `aca sandbox list` returned 403 despite an explicit subscription. Temporarily selecting the previously authenticated target subscription made inventory succeed; an EXIT trap restored the prior default, confirmed by a follow-up account read. No login, role assignment or token export was used.
- Inventory contains one pre-existing Stopped sandbox without this smoke's ownership label. Left it untouched. **Zero create requests and zero test sandboxes**: deletion is not applicable, and no creation/cleanup time can be reported. Did not claim the group is empty or a cleanup test passed.
- No SDK method or in-sandbox Copilot command executed. Automatic auth, minimal prompt, genuine workflow, command/step/result retrieval and streaming remain untested. The prepared harness still needs a distinct minimal-prompt test, SDK credential-context inspection, Ready-state validation and timings before execution; no speculative SDK/code changes made while package inspection is blocked.
- Updated compatibility evidence and checklist; private sanitized [preflight results](../.local/azure-discovery/smoke-preflight-2026-10-13.json) record the target, existing sandbox, download errors and unchanged saved-plan SHA-256. No Terraform-managed infrastructure or GitHub resource was changed. **Stopped with Milestone 0 blocked**; resolve the SDK artifact-host connection before resuming the approved smoke, and await user direction before application development. C publication remains outside this approval.

## SDK installation diagnosis corrected — 2026-10-13

- At the user's request, inspected pip config files and relevant environment settings without exposing credentials. Both global `/Library/Application Support/pip/pip.conf` and user `/Users/ij/.config/pip/pip.conf` configure `https://packagefeedproxy.microsoft.io/pypi/simple/`. The venv has no pip module, and uv does not read pip config; initial uv and curl commands therefore bypassed the intended index.
- Retried `uv pip install --python /Users/ij/Dev/aca-sandbox-demo/.venv/bin/python --index-url https://packagefeedproxy.microsoft.io/pypi/simple/ -r requirements-smoke.txt`. Installation succeeded: 24 packages including SDK 0.1.0b4 and Azure Identity 1.26.0. Verified versions and imported `SandboxGroupClient`/`endpoint_for_region` successfully.
- Corrected current blocker/status documentation; preserved the earlier failed attempt as history. No package-index configuration, Terraform artifact or Azure resource changed. Live SDK method verification, prompt/workflow tests and cleanup timing remain pending; no test sandbox created.

## One authorized live SDK smoke — 2026-10-13

- Inspected official SDK 0.1.0b4 signatures and source before mutation. Verified creation poll parameters, completed ExecResult fields, file-method signatures and immediate-return delete semantics. Found a stale SDK docstring referencing absent `create_sandbox`; used actual `begin_create_sandbox`.
- Used DefaultAzureCredential restricted to the existing CLI identity, with the intended cached subscription selected temporarily. Restored the prior default afterward. Confirmed SDK `copilot` disk Ready and recorded the pre-existing stopped sandbox. No PAT values inspected or printed.
- Executed one create request, automatic retries disabled, 1 vCPU/2 GiB, public disk copilot and empty ports; Running after 1.413s. Version command returned GitHub Copilot CLI 1.0.83. Noninteractive trusted prompt exited 1 after 1.463s with No authentication information found; no /login or token workaround.
- Plain `copilot workflow run --help` returned generic CLI help, missing expected workflow flags. The runner stopped before extension upload, so no genuine workflow or structured events ran. **Verification limitation:** the probe omitted `--experimental`; cannot conclude workflow feature absence. Authentication binding is independently unresolved. No extra sandbox or CLI update attempted.
- CLI stdout/stderr and exit codes were captured programmatically in completed ExecResult objects. SDK source exposes no incremental exec streaming interface; CLI `--stream` does not establish SDK streaming. File polling and the delayed-output transport probe were not reached.
- Finally called delete, polled the exact smoke ID to HTTP 404, and confirmed absence in final listing: cleanup 6.729s, total 19.290s. The pre-existing sandbox still reports Stopped and was never modified. Creation/command/cleanup had independent bounds; no timeout was triggered, so timeout-path cleanup is not claimed as tested.
- Preserved private [results](../.local/live-smoke/results-2026-10-13.md), [sanitized evidence](../.local/live-smoke/9e933970b6fc4327bcca778ff9ee63d9.json), and the executed trusted runner. Updated compatibility/checklist and verified the original Terraform plan SHA-256 unchanged. **Milestone 0 did not pass. Stopped after cleanup/reporting; no further sandbox or application work without user approval.**

## Authentication-only diagnosis — 2026-10-13

- User authorized one new disposable sandbox solely to diagnose Copilot authentication, with no workflows, credential changes, manual PAT injection, `/login`, GitHub writes, Terraform changes, public ingress or app deployment. Re-read project instructions/README and applied documentation-keeper factual tracking to these requested documents.
- Reviewed official [provider credential](https://staging.sandboxes.azure.com/docs/sandboxes/credentials), [built-in image](https://staging.sandboxes.azure.com/docs/sandboxes/disk-images), [Python quickstart](https://learn.microsoft.com/en-us/azure/container-apps/sandboxes-quickstart-python-sdk) and [Copilot authentication](https://docs.github.com/en/copilot/how-tos/copilot-cli/set-up-copilot-cli/authenticate-copilot-cli) documentation. Inspected installed SDK 0.1.0b4 signatures/request construction and ACA CLI 1.0.0-preview.2 help.
- Read-only `aca sandboxgroup credential list` returned existing `github-copilot` connection `4e86451e-7ec1-434e-8b1b-cbfc4088960d` in **Ready** state. Inspected the official portal client mapping of Ready to **Configured**; no token reveal or update. SDK does not manage provider credentials, but its create request accepts `connections: list[str]`. CLI help explicitly pairs `--disk copilot` with `--credential <id>`; portal's Copilot template uses the distinct `GitHubCopilot` preset.
- **Root cause verified:** previous smoke chose the disk without attaching the credential. The authorized diagnosis created one sandbox through `DefaultAzureCredential` and `begin_create_sandbox(disk="copilot", connections=[existing_id], ...)`, 1 vCPU/2 GiB and no ports. Read-back confirmed Running and that exact connection attached. No PAT was supplied by the caller, and no group configuration was changed.
- Trusted in-sandbox Python probe reported only **COPILOT_GITHUB_TOKEN set; GH_TOKEN unset; GITHUB_TOKEN unset**. It launched Copilot in the same inherited process environment without a user change, login shell or environment override. `copilot --version` returned **1.0.83**. Help-verified flags disabled automatic updates, custom instructions and built-in MCPs, with read as the only available tool and explicitly denied. Minimal prompt returned **ACA_AUTH_PONG**, exit **0**, in **4.127s**. Raw CLI text and credential values were not exported; only expected response, diagnostic booleans, exit code and timing were retained.
- Sandbox `d49f0e6c-6868-4030-addc-07a228a1dbb6`: exactly one create request, Running in **1.109s**. Finally cleanup took **6.513s**, verified by direct GET **404** and final listing. Pre-existing sandbox `5bf17eda-250b-4c90-9cd6-bd44a5610851` remained **Stopped** and untouched. Total **18.201s**; original Azure CLI subscription restored and verified. Strict command, transport, work and independent cleanup deadlines applied; no timeout occurred.
- Detailed evidence, exact commands, injection semantics and bounds are in [compatibility](./compatibility.md#authentication-diagnosis--2026-10-13). Private [sanitized evidence](../.local/auth-diagnosis/735e5a1ac26c4f4e83c56c25c80a5736.json), [runner](../.local/auth-diagnosis/run.py) and [probe](../.local/auth-diagnosis/probe.py) retained. Do not rerun the runner under the consumed authorization.
- **Solution:** pass the existing Ready credential connection ID when creating from the Copilot disk. No PAT replacement or platform-side fix is indicated by this successful test. Reusable harness/adapter still needs this binding in a later approved work item. Dynamic Workflow eligibility/execution, C publication permissions and broader Milestone 0 gates remain unverified. No workflows ran, even after authentication succeeded, because this task was diagnosis only.
- Saved Terraform plan SHA-256 remains `386fceff8f67a42d8e51f20d6bf521b59fc4244a5e8e3186d8cbe76178178622`. No Terraform command, resource modification or app development performed. **Stopped after diagnosis and verified cleanup; await approval before further live testing or application development.**


## Experimental Dynamic Workflow attempt — 2026-10-13

- User authorized one fresh disposable sandbox for the final workflow test, with the verified existing credential binding. Reviewed official workflow API/extension documentation and direct invocation requirements; no ordinary prompt fallback.
- Updated [reusable harness](../scripts/smoke_test_sandbox.py) to require `--credential-connection-id`, verify Ready provider metadata, pass `connections=[id]`, confirm no ports and protect all pre-existing IDs. Uses existing Azure CLI identity through `DefaultAzureCredential`, disabled API retries, strict independent work/cleanup deadlines and exact-ID 404 verification. Plan-only mode remains inert.
- Updated [trusted extension](../workflows/smoke/extension.mjs): `ctx.step("prepare-v1")` computes 2 + 3 with a labeled three-second observation window; `ctx.agent` returns structured nonce/pong/sum; `ctx.step("verify-v1")` deterministically chooses verified/rejected from the actual result. Prepared timestamps, run ID, step statuses/results/durations and JSONL events. [Sandbox helper](../scripts/smoke_workflow_runner.py) provides bounded capability probes and a detached workflow runner; redacts CLI logs inside the sandbox before SDK retrieval. No extension requests secret environment variables.
- Prepared live `read_file` polling of status/events with complete-line handling and before/after running checks. Structured result validation checks nonce, run ID, all boundaries and each expected result. These paths remain prepared, **not cloud-verified**, because the capability gate stopped the test.
- Local checks: Python compilation and Node syntax passed; VS Code reported no problems. VS Code test discovery found no tests, so ran `.venv/bin/python -m unittest discover -s scripts/tests -v`: **14 passed**, including provider binding, zero-exit generic-help rejection, result provenance, partial event handling, timeout cleanup and protected IDs. All use explicit doubles and imply no workflow success.
- Live ID `bb472511-ea6a-4caf-b57e-2e92c04bd93a`, one create request, built-in `copilot`, 1 vCPU/2 GiB and existing connection `4e86451e-7ec1-434e-8b1b-cbfc4088960d`; Running in **1.010s**. SDK `write_file` delivered the trusted helper and `exec` executed it. Copilot **1.0.83**; `COPILOT_GITHUB_TOKEN` set, `GH_TOKEN` and `GITHUB_TOKEN` unset. No PAT values exported.
- **Failed capability gate:** `copilot --no-auto-update --experimental workflow run --help` exited 0 but was identical to general help, without `workflow`, `--args` or `--result-file`. `--experimental` itself was advertised. Stopped before genuine workflow extension upload/invocation; no workflow exit code, step result, duration, log or live progress exists. This is not a workflow execution failure and does not establish account ineligibility or absence of all internal APIs.
- Local CLI **1.0.91** recognized the exact help command. Official release metadata dates 1.0.83 to September 4 and 1.0.91 to October 1, supporting a version/image mismatch. Local inspection was help-only; no local workflow or AI prompt executed. Minimum supported version and actual Azure execution on 1.0.91 remain unverified.
- Finally deleted the exact created ID; direct GET **404** and final inventory verified. Cleanup **6.879s**, total **13.529s**. Only pre-existing `5bf17eda-250b-4c90-9cd6-bd44a5610851` remains **Stopped**, untouched. Azure CLI original subscription/tenant restored and verified. No second sandbox, group-credential change, public ingress, GitHub repository, CLI update or Terraform operation.
- [Compatibility record](./compatibility.md#experimental-dynamic-workflow-attempt--2026-10-13) documents exact calls/commands, timeouts, results and next options; [sanitized live evidence](../.local/workflow-smoke-2026-10-13.json) preserves command outputs and inventories. Original saved-plan SHA-256 remains `386fceff8f67a42d8e51f20d6bf521b59fc4244a5e8e3186d8cbe76178178622`.
- **Stopped after the test.** Next live attempt requires new sandbox authorization plus a reviewed compatible built-in image/CLI, potentially an explicitly approved pinned CLI update inside that disposable sandbox. No application development started. Broader Milestone 0/C publication gates remain open and are outside this attempt.
