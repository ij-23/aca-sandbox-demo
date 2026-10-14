# Development progress

## Autonomous completion authorization — 2026-10-14

The user authorized project-scoped Sandbox creation/cleanup, Terraform apply, Azure deployment and GitHub publishing without recurring approval. M0-C-FAIL and later bounded integration attempts no longer await approval. Existing technical gates remain. Do not destroy static resources, delete/overwrite repositories, change credentials or modify unrelated resources. The pre-existing stopped Sandbox stays protected. Read terraform-builder at `/Users/ij/.agents/skills/terraform-builder/SKILL.md`; retain the required `infrastructure/terraform/` layout. Official telemetryConfig and DCR/DCE are deployed; a trusted container-stdout probe ingested 15 records. Actual LAW ingestion is verified for A (11), B (10), and C (18) workflow records with exact run/Sandbox correlation.

## Current status — 2026-10-14

User confirmed corrected PAT permissions and explicitly selected **existing LOCAL Terraform state**. No remote backend, state migration/reset, or infrastructure recreation is permitted. Fresh same-PAT probe passed: private test repository remote SHA `1f9fe8d42bb5f364d352d5d2b784492b9a6b53e1`, no second repository created. Sandbox `e0602a8b-62bf-4aa3-aad8-526eec75e4ab` created in 0.987s, deleted in 2.232s, exact404 verified. New authenticated A/B run `ffe4af9f` produced a source-verified finding and expected 2 passed/2 failed fixture tests. Preparing publication enablement; successful C remains to be verified.

Earlier checkpoint (superseded where noted):

**M0-CLI97 and M0-C-FAIL PASSED; full project remains incomplete.** Standing project authorization covers continued bounded tests, Terraform and publishing. The latest C smoke executed genuine Copilot patching, successful dependency/build checks and an actual deliberate pytest failure, then skipped all publication stages and deleted its exact Sandbox. Telemetry infrastructure, Entra registrations and the Azure host are deployed. Entra browser sign-in and UAMI Blob access pass. Same-PAT GitHub creation passes, but push returns 403. Genuine concurrent A/B and full 48-event Blob persistence pass; successful C publication/replay and CI/CD remain incomplete.

Storage networking was verified read-only: publicNetworkAccess Enabled, defaultAction Allow, no private endpoints, HTTPS/TLS1.2, public blob/shared-key access disabled. HTTPS reached the Blob service (anonymous 409 public access forbidden); operator OAuth listing failed authorization. This is not the old networking blocker. Do not change networking. Deployed-host readiness verified UAMI access to all four containers; the first live run persisted state/events and cleanup records.

- Implemented local FastAPI platform contracts, Entra RS256 issuer/audience/tenant/delegated-scope/user-allowlist verification, owner checks, repository allowlisting/SHA resolution, redaction, managed-identity Blob storage, durable-before-delivery events, SSE cursors and deterministic A/B admission/orchestration. The real executor is now implemented but disabled by default pending broader live verification; no in-memory production fallback exists.
- Implemented React/TypeScript dashboard source with A/B/C lifecycle/timelines, real-event console, reports/diffs, one explicit fix/private-publication confirmation, Entra MSAL sign-in and bearer-authenticated reconnecting SSE. Empty states contain no invented execution. TypeScript/Vite build passed; the empty dashboard was inspected in the local browser. Replay is gated on complete Sandbox-backed A/B/C evidence; no recording is fabricated. The 1080p live-data exercise remains pending.
- Local verification: **68 Python tests passed**, including signed-token rejection cases, spoofed principal headers, owner boundaries, URL attacks, event ordering/durability, parallel A/B test doubles and smoke finally cleanup. Ruff checks pass. Vitest 5.0.3 passes, npm audit reports zero advisories, schema export matches, and the application image builds and passes a network-isolated container smoke. One Starlette/httpx test-client deprecation warning remains. Test doubles exist only in tests and are not cloud evidence.
- The existing protected sandbox had no alternative Copilot executable under the bounded inspected paths (`/root/.local`, `/home`, `/opt`); its default remains 1.0.83. This does not identify the user's separate 1.0.97 observation.

### Earlier investigation checkpoints

Historical snapshots below describe their dates, not the current gate. The 2026-10-14 M0-CLI97 result above supersedes earlier workflow-capability blockers.

**Latest comparison after the user's 1.0.97 report:** static inspection of the checksum-verified official 1.0.97 package confirms `defineWorkflow`, workflow registration, direct command dispatch and result handling. No CLI upgrade is justified for a sandbox already using that version. The target group currently lists only protected sandbox `5bf17eda-250b-4c90-9cd6-bd44a5610851`, now Running; read-only exec reports **1.0.83** as `root` from `/usr/local/bin/copilot`. Its portal preset label/private disk reference differs from our public-disk create request, but that does not explain the version mismatch conclusively. Asked the user to identify the sandbox/portal URL that showed 1.0.97. No new sandbox, lifecycle change, workflow execution, credential change or Terraform change occurred. See [comparison evidence](./compatibility.md#current-comparison-user-reported-cli-1097--2026-10-13).

**Latest static investigation:** official CLI 1.0.83 has the global experimental switch and project-extension trust opt-in, but its bundled SDK exports `defineFactory` / `factories` instead of the documented `defineWorkflow` / `workflows` registration. The verified release package also lacks the direct workflow command options. This replaces the insufficient help-only inference with concrete package evidence; see [compatibility investigation](./compatibility.md#static-cli-1083-investigation--2026-10-13). No new sandbox, Azure API call, CLI upgrade or agent execution occurred. The saved Terraform plan hash remains unchanged. A compatible image/CLI and a newly approved live test remain necessary; no working Dynamic Workflow run is claimed.

**Milestone 0 remains blocked on genuine Dynamic Workflow execution.** The reusable harness now attaches the existing Ready provider credential connection. One newly approved sandbox confirmed Copilot **1.0.83** and injected `COPILOT_GITHUB_TOKEN`, but `copilot --no-auto-update --experimental workflow run --help` returned general help with no workflow subcommand/`--args`/`--result-file`. The harness stopped at that capability gate, before workflow extension upload/execution. No workflow outputs, steps or live progress were produced. Creation **1.010s**, finally cleanup **6.879s**, total **13.529s**; exact-ID GET **404** verified. The pre-existing sandbox remains Stopped and untouched. No additional sandbox, credential/Terraform change, GitHub write, CLI upgrade or application development occurred.

Implemented the [Terraform foundation](../infrastructure/terraform/), [smoke harness](../scripts/smoke_test_sandbox.py), [real workflow extension](../workflows/smoke/extension.mjs), and [deployment guide](./deployment.md). The corresponding live SDK/workflow integrations remain blocked on real Milestone 0 evidence; independent platform work is authorized by the latest request.

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
- [x] Inspect installed SDK signatures/source; verify DefaultAzureCredential access, one create/exec/get/delete lifecycle and completed stdout/stderr/exit codes. File transfer, genuine workflow capture and concurrent polling passed in M0-CLI97; live timeout-path behavior remains untested.
- [ ] Inspect installed provider runtime schemas, API contracts, authConfig support and group-policy ownership.
- [x] Retrieve intended subscription/tenant and initial User operator via authorized CLI discovery; Sweden Central/prefix academo selected. Approved foundation deployed.
- [x] Verify target quota, role definition and read-only public-image metadata; deployed group lists `copilot` as Ready.
- [x] Prepare genuine workflow with deterministic preparation, `ctx.agent`, actual-result conditional verification, structured per-step outputs and boundary events; update bounded harness for provider binding, file delivery/polling and finally cleanup. Initial fourteen unit tests passed; genuine live execution subsequently passed in M0-CLI97.
- [ ] Verify official GitHub personal-owner repository creation API/permission requirements, `X-Accepted-GitHub-Permissions`, account restrictions and actual git push requirements; do not assume creation grants push.
- [x] Verify Sandbox Group Copilot credential configuration and runtime injection (2026-10-13): API Ready maps to portal Configured; explicit connection binding injects `COPILOT_GITHUB_TOKEN`. Only set/unset booleans reported, no credential values collected.
- [ ] Verify updated demo publication PAT capability: disposable personal owner/Copilot seat, Copilot Requests, Repository creation: Write, Contents: Read and write, current/future repository access and short expiration. Configuration confirmation alone does not prove these permissions; publication testing is authorized; current git push fails403.
- [x] Obtain explicit approval for one disposable SDK sandbox in the deployed group, trusted prompt and genuine workflow, strict timeouts and deletion; no repository creation, public ingress, Terraform or app changes (2026-10-13).
- [x] Reverify approved group ARM state, copilot Ready status and authenticated sandbox inventory; leave the pre-existing stopped sandbox untouched.
- [x] Execute exactly one SDK smoke attempt with trusted prompt, no ports and no third-party repository; finally delete and verify exact-ID 404. Automatic Copilot authentication failed; workflow execution was not reached.
- [x] Diagnose automatic credential binding for SDK `disk="copilot"`: omitted `connections` caused the previous failure. Existing Ready connection attached in one newly authorized sandbox; same CLI 1.0.83 prompt succeeded without login or manual token injection; finally cleanup and GET 404 verified.
- [x] Incorporate verified connection-ID binding into reusable smoke harness; require existing Ready connection ID and verify returned attachment. Live workflow-capability attempt confirmed injection (2026-10-13). Application adapter is implemented; its full Azure integration remains unverified.
- [x] Check in-sandbox workflow help with `--experimental` in one newly approved sandbox: CLI 1.0.83 returned identical general help, without the documented direct workflow command. Exact-ID cleanup verified (2026-10-13).
- [x] Investigate CLI 1.0.83 statically beyond help: verify official release checksum, actual extension exports/registration, experimental handling, documented extension paths and trust opt-in. Confirm the standard release lacks the required Dynamic Workflow API; distinguish this from an actual in-image import test.
- [x] Inspect official CLI 1.0.97 package and confirm genuine workflow API/registration/direct-command implementation. Compare existing sandbox metadata and read-only executable version without creating or upgrading anything.
- [ ] Identify the user-reported 1.0.97 sandbox/executable and resolve its difference from the target group's root exec environment (1.0.83); preserve the existing sandbox. Adjust the harness's explicit reviewed-version gate before an approved test on a compatible version.
- [x] Explicit M0-CLI97 approval consumed 2026-10-14: pinned official CLI in one disposable Sandbox; genuine workflow passed; exact-ID deletion confirmed.
- [x] Execute real smoke; credential auth without login, genuine registration/AI/conditional branch, result and six boundary events, live file polling and exact-ID cleanup verified (2026-10-14).
- [x] Implement/exercise a genuine C Dynamic Workflow PoC inside an approved sandbox; prove failing build/tests or targeted recheck branches to a report with repository creation/push skipped and no remote write.
- [x] Verify supported same-PAT extension access: official SDK permission handler grants only the trusted extension’s COPILOT_GITHUB_TOKEN request; GitHub /user returns ij-23. No host credential export. Git push permission remains a separate failed gate.
- [ ] Complete same-PAT harmless push and verify remote SHA. Personal owner and exact private test-repository creation passed; current push403 is an external permission blocker.
- [ ] Record real C branch/publication evidence and owned-sandbox cleanup; retain partial test-repository outcomes transparently. Remove a test repository only after further explicit approval.
- [ ] Mark viability gate passed only after all runtime evidence succeeds.

### Milestone 1 — Terraform foundation

- [x] Select local state for this bootstrap and lock AzureRM 4.81.0 / AzAPI 2.13.0 for Darwin ARM64 and Linux AMD64. CI backend remains a later explicit decision.
- [x] Author bootstrap modules, typed inputs, example configuration and required outputs; application URL is empty until the later real-image phase.
- [x] Implement and deploy scoped identities/RBAC, private blob containers/retention and telemetry; resource/grant read-back verified, UAMI runtime Blob/Sandbox access passes.
- [x] Deploy secretless Entra auth and test per-create default-Deny/Full egress. Document unsupported persistent group-wide controls and use app admission/deadlines; no hard service-lifetime guarantee.
- [x] Run formatting, inspect installed provider schemas and validate; six offline Terraform tests pass.
- [x] Produce real saved foundation plan with discovered identity, Sweden Central, academo prefix and signed-in User operator: 23 additions, no changes/deletions.
- [x] Present plan; apply exact saved plan after explicit approval; verify all resources and record policy-imposed Storage deviation.
- [x] Verify user-resolved Storage networking read-only (2026-10-14). Endpoint reachable; no network change made. App UAMI Blob authorization passes.

### Milestone 2 — application image and CI/CD

- [x] Create React/FastAPI host and multi-stage Dockerfile; local AMD64 image build and isolated HTTP/static/non-root checks passed. Azure application image deployed and readiness verified.
- [x] Implement server-side authorization, Blob persistence adapter and health/readiness endpoints; local security tests pass. Entra sign-in and Blob managed-identity access pass.
- [x] Implement platform-only CI lint/tests/schema/frontend/image checks with no Azure credentials or fixture execution.
- [ ] Implement approved OIDC build/push/Terraform deployment with one image owner and durable state.
- [x] Validate Azure HTTPS image deployment, browser Entra login, anonymous401, UAMI Blob/Sandbox access and ACR application-only contents.

### Milestone 3 — real A/B execution

- [x] Implement vetted repository URL validation and bounded public immutable-SHA resolution; input rejection covered locally.
- [x] Implement strict event/report schemas and generated JSON contracts for all three workflows, redaction and run-owner state; C report validates publication evidence and approved destination.
- [x] Connect durable per-attempt ownership intent to the real SDK executor; local cleanup/cancellation tests and real A/B owned cleanup pass.
- [x] Implement deterministic concurrent A/B orchestration, single-run admission, timeouts and per-run cleanup-failure recovery; verified with explicit unit-test doubles.
- [ ] Verify the implemented real SDK adapter through approved Azure A/B/C runs.
- [x] Verify genuine security/build Dynamic Workflows concurrently at one immutable SHA; real AI, source verification,2 passed/2 failed pytest and conditional runtime skip observed.
- [ ] Verify real A/B results, cancellation, partial failure, restart reconciliation and cleanup.

### Milestone 4 — observability dashboard

- [x] Provision official telemetryConfig/DCR/DCE/UAMI and verify LAW ingestion for actual A/B/C run and Sandbox IDs.
- [x] Verify all48 real A/B events persist contiguously in private Blob after conditional append-blob creation fix.
- [x] Verify real command timeout124, outbound allow200/deny403 and exact-ID cleanup.

- [x] Implement lifecycle cards and genuine A/B/C timelines. Real A/B steps/logs/results/cleanup observed in React; C UI execution remains blocked by publication credentials.
- [x] Implement single Fix Vulnerability confirmation disclosing finding, source SHA and private destination; no separate Publish button. End-to-end live behavior remains unverified.
- [ ] Show C stages `checkout`, `agent.fix`, `validate`, `publication.gate`, `create_repo`, `push`, `verify_remote`, `complete`; validation results/diff, failure or partial-publication status, and clickable verified repository URL/commit SHA.
- [ ] Verify authenticated SSE resume/heartbeat and durable history beyond ring buffer for all three workflows, including C branch/publication events; disclose polling if true streaming is unavailable.
- [ ] Verify genuine replay includes A/B/C timelines and publication outcome while performing no sandbox or GitHub side effects; no synthetic live events.
- [ ] Validate 1080p presentation layout and actual data; enable replay only when genuine recording exists.

### Milestone 5 — approved remediation and publication Dynamic Workflow

- [x] Bind one Fix Vulnerability approval to user/run/finding/source SHA/destination/attempt; local tests reject stale and repeated approvals and wrong report destinations. No live C executor is enabled; cloud acceptance remains open.
- [x] Implement C as a third genuine registered extension with deterministic validation/publication code. Genuine C failed-validation branch passes; successful publication remains blocked.
- [x] Exercise genuine C fix/build/tests/diff and deterministic failed-validation gate with an uploaded immutable trusted fixture; all publication stages skipped. Repository-cloned successful publication remains a separate gate.
- [ ] On success, verify personal destination owner and name availability; collisions fail without overwrite. Create private `{original-name}-fixed` inside C through the verified API with the same group PAT.
- [ ] Commit/push checked sanitized fixed source with fresh history, including new files and license/attribution; exclude old `.git`, credentials, `.env`, runtime artifacts and secret-bearing fixtures; original repo/remote unchanged.
- [ ] Verify remote owner/name/private visibility and pushed SHA before returning successful `remediation.json` with `fixed_repository_url`, commit SHA, diff and validation evidence.
- [ ] Handle API/git permission errors, rate limits, name collisions, ambiguous create/push responses, timeouts and partial publication with observable reasons; reconcile before retries, no overwrite or automatic remote deletion.
- [ ] Persist sanitized diff/report and publication outcome to Blob before deleting C; expose persistence failures and preserve recovery/cleanup tracking. Verify deployed-UAMI data access before app-integrated C testing; Storage networking is resolved.
- [ ] Exercise real passing and failing C branches, UI timeline/reconnect/result link, stale/duplicate consent rejection and cleanup; verify original repository unchanged and no success reported without remote verification.

### Milestone 6 — customer readiness

- [ ] Finish verified README, deployment/security/architecture guides, examples and OSS licensing.
- [ ] Capture genuine successful JSONL replay covering all three workflows, including C validation branch/private publication/verified URL and cleanup; sanitize it and preserve provenance.
- [ ] Finish and rehearse 15-minute script, screenshots and failure/replay drill.
- [ ] Rehearse clean-customer installation, orphan cleanup and approved static teardown.
- [ ] Reconcile every acceptance criterion in [AGENTS.md](../AGENTS.md).

## Autonomous platform hardening — 2026-10-13

- Synchronized the Python environment to the SHA256-locked development requirements; SDK 0.1.0b4 and Identity 1.26.0 remain pinned. Fixed Docker dependency downloads using the existing public Microsoft proxy as an optional non-secret build argument. Normal defaults and npm lockfile URLs use public registries; TLS and integrity checks stay enabled.
- Fixed FastAPI's packaged static-asset path after an actual browser failure. Built React with separate identity bundle, and inspected the gated empty dashboard. No synthesized findings, workflow progress or replay recording was used. Fixed duplicate MSAL initialization under React StrictMode.
- Replaced unbounded event caches with bounded windows and Blob-backed cursor recovery. Added byte budgeting, contiguous-ID validation and ambiguous-append recovery. Cleanup now continues across interrupted runs, even when event persistence fails; each unresolved failure separately blocks new admission until its retry succeeds. Report persistence does not masquerade as a Sandbox workflow-completion event.
- Confirmed deletion is persisted in run state before its event is emitted, so an exhausted event budget cannot permanently strand the cleanup slot. Event-delivery failure is recorded separately, surfaced by dashboard state polling, and disqualifies a run from replay. Concurrent report-state writes are serialized to prevent out-of-order Blob overwrites.
- Added local tests for history eviction/resume, append acknowledgement loss, restart cleanup failure/retry, stale and duplicate C approval, wrong publication destination, invalid SSE cursors and unavailable replay. Fixed the smoke `finally` path so a local evidence-write error cannot skip deletion. Added the inert-by-default [smoke orphan tool](../scripts/cleanup_orphans.py), with exact scope/nonce/live-label checks and protected IDs; it has not performed a live deletion.
- Added generated [report schemas](../workflows/schemas/) and a CI consistency check. Added a small [trusted FastAPI fixture](../demo-repo/README.md) with deliberate path traversal and harmless canary regression tests. The fixture was authored/read only; its code/tests were **not executed**, and no public fixture repository was created. Its expected failures and post-fix success remain Sandbox-only validation work.
- Local results: **49 Python tests passed**, **1 Vitest test passed**, Ruff lint/format and TypeScript/Vite build passed, npm audit **0 advisories** after upgrading Vitest to 5.0.3. One Starlette warning notes future test-client migration from httpx. No test used cloud execution as a hidden fallback.
- Built `aca-sandbox-demo:local` for Linux AMD64. [Container verification](../scripts/verify_container.py) passed using no network, no credentials, read-only filesystem, dropped capabilities and UID 10001: health/dashboard/assets 200, readiness 503 with unconfigured storage, anonymous read/create/remediate/cleanup APIs 401. Live execution remained disabled; the exact local test container was removed.
- Updated README, plan, deployment, compatibility and architecture status. The original Terraform root/state/consumed plan remain untouched. M0 approval, GitHub owner/fixture/project-repository details, and networking/state choices are pending. No application image was pushed, no Container App deployed, and no GitHub resource created.
- Added MIT license and contributor boundaries. Final editor diagnostics and `git diff --check` pass; nine documentation files have no missing local link targets. Rebuilt and rechecked the final container after the recovery fixes; removed its verification container and stopped the temporary loopback-only preview host. Saved foundation plan SHA256 remains `386fceff8f67a42d8e51f20d6bf521b59fc4244a5e8e3186d8cbe76178178622`.

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

## Approved M0-CLI97 result — 2026-10-14

- Exact Sandbox `f53a4414-c37e-497d-a3a6-0ab6e8cc29d7`; one create request, SDK 0.1.0b4, `disk="copilot"`, existing connection `4e86451e-7ec1-434e-8b1b-cbfc4088960d`, 1 vCPU/2 GiB, no ports. Protected pre-existing ID remained Stopped before/after.
- Official standalone CLI 1.0.97 checksum matched; installed only in disposable control directory. No existing image/executable or group credentials modified.
- Registered `aca-viability-smoke`, actual workflow ID `4e40b2c4-9c13-4281-aad9-01a85ce160aa`; result `answer=pong`, `sum=5`, `branch=verified`. Six real boundary events and native workflow/subagent/result events captured. Auth succeeded automatically without `/login`.
- Creation 1.681s, workflow command 8.732s, cleanup 1.375s, total 19.033s. Eight file polls; progress seen while runner still running at 4.618s, 7.233s and 8.540s. No runtime timeout occurred; timeout paths are not live-proven.
- CLI warned that `read` is an unknown tool name in 1.0.97; available tools were disabled and actual subagent reported zero tool calls. Future invocations will use verified `view` with an explicit deny, retaining zero-tool AI where source is supplied directly.
- Private sanitized evidence: [M0-CLI97](../.local/m0-cli97-evidence.json). Azure CLI was already on the approved subscription/tenant; no context switch needed. No other Sandbox creation, GitHub operation or static Azure mutation occurred.
- Expanded M0 still requires real C failed-validation and approved publication tests. The successful minimal workflow unlocks corresponding implementation, not unapproved cloud execution.

## Continued implementation after genuine workflow proof — 2026-10-14

- Implemented [official SDK adapter](../backend/app/sandbox.py): managed identity, explicit existing credential binding, durable per-attempt ownership intent before create, cancellation drains in-flight SDK calls, trusted workflow upload, pinned disposable CLI, detached file polling, strict provenance and exact-ID owned-only cleanup. Orchestrator persists C report/diff before successful cleanup. Publication and live execution default off. Adapter runtime is **not yet Azure-tested**.
- Added real [A](../workflows/security-review/extension.mjs), [B](../workflows/build-validation/extension.mjs), and [C](../workflows/remediation/extension.mjs) `defineWorkflow`/`joinSession` extensions. Deterministic helper performs pinned checkout, bounded fixture source review, hash-locked installation/build/pytest, conditional localhost health, fixed-source integrity and targeted recheck. C receives structured Copilot patch content limited to app.py; tests/dependencies cannot be modified. No fixture code was executed locally.
- Implemented C's private publication path inside its Sandbox helper: explicit consent/validation gate, same granted provider token only, personal-owner check, collision refusal, clean source export/fresh commit, POST /user/repos, credential-helper push without token in URLs/files, private destination and remote SHA verification. Definite rejection and ambiguous/partial writes remain distinct; no overwrite, retry creation or deletion. **No GitHub write or real publication test occurred.** Extension `requestedEnvironmentVariables` is supported in the inspected SDK, but noninteractive permission granting is still unverified. No parent-environment scraping or alternate credentials.
- Prepared [M0-C-FAIL harness](../scripts/smoke_test_remediation.py) and [exact scope](./pending-approvals.md#m0-c-fail--prepared-not-executed). It uploads the trusted fixture and adds a deliberate failing pytest case inside one future Sandbox, then proves the real C AI step and no-publication branch. Plan-only invocation made zero Azure calls. New approval requested and pending; not executed.
- SDK egress schema and Microsoft Learn reviewed. Adapter supplies create-time default Deny/Full inspection with explicit GitHub/Copilot/PyPI hosts. This policy is **prepared, not live-validated**; the approved M0-CLI97 nonce test had no new egress policy. Persistent group-wide IaC enforcement remains unsupported/unverified and is not claimed.
- Read-only Storage verification: Enabled public network, Allow default, HTTPS/TLS1.2, no public blobs/shared keys. HTTPS reaches Blob; signed-in operator OAuth read lacks data permissions. UAMI `97766d42-5dbe-4fe1-b99a-41366f515c34` has existing Data Contributor at reports/events/diffs/replay; group Data Owner, AcrPull and Monitoring Metrics Publisher also read back. No networking, policy or RBAC fixes attempted.
- Applied installed terraform-builder and documentation-keeper guidance. Added optional [application module](../infrastructure/terraform/modules/application/) under the project-required path: existing UAMI/ACR, digest-only image, single revision, min/max 1, HTTPS, health/readiness/startup probes, non-secret settings. Null application preserves foundation-only mode. Microsoft Learn and AzureRM 4.81.0 runtime schema grounded fields. `init -lockfile=readonly`, `validate`, fmt and **6 offline Terraform tests passed**. No apply, real replacement plan, provider-lock change or existing static resource mutation.
- Entra design uses MSAL authorization code + PKCE and strict backend v2 delegated JWT authorization. Existing-registration EasyAuth without a secret uses implicit flow per Microsoft Learn, so no implicit flow or secret is added. Actual customer registration/consent choice is pending, as are owner/fixture/project GitHub details and remote-state choice; requested asynchronously. New registrations have not been created.
- Local verification: **61 Python tests passed**, including SDK cancellation drain, exact ownership mismatch, ambiguous create, event-store failure cleanup, failed publication validation, collision and remote-SHA mismatch. No test invokes real cloud/git publication. Ruff and syntax checks pass. Updated CI to check workflow code. Application image rebuild found excluded workflow files, fixed Docker allowlist; direct package downloads hit the known environment TLS issue and rebuild uses the documented non-secret Microsoft package proxies. Final image verification is in progress.


## Final local verification and approval handoff — 2026-10-14

- **64 Python tests pass** (one existing Starlette/httpx deprecation warning). Added a regression proving one Sandbox ownership/deletion failure cannot prevent peer cleanup. Cleanup runs independently for each durable ownership record, preserves failed records, requires exact-ID absence, and refuses mismatched ownership. These failure cases use explicit unit doubles, not live Azure resources.
- Latest application image rebuilt successfully after all runtime edits. Local image manifest list: `sha256:bc2371938875b462b56023d99cd9452520c333354ee49df8aa38644f13ba1d4c`. Network-isolated, read-only container check passed: UID 10001, dashboard/three assets/health HTTP 200, unconfigured readiness 503, anonymous operational routes 401, live execution disabled. Exact local verification container removed. Image has not been pushed to ACR.
- Structured lifecycle telemetry now emits an allowlisted JSON record to stdout for ACA/Log Analytics diagnostics, excluding headers, prompts, report bodies and credentials. Tests verify exclusion. Direct Application Insights SDK ingestion and Azure telemetry delivery remain unverified.
- Dashboard now retains real stage payloads, separates step events from logs, shows test counts/health, and marks partial publication. Fix remains disabled until publication is configured. Frontend build/test passed earlier in this slice; no real Azure dashboard session or synthetic replay is claimed.
- Prepared GitHub Actions OIDC build/plan/apply workflow enforces environment review gates, requires an approved Azure remote backend, binds the app image digest, saves the exact plan/hash, and applies that artifact without replanning. Actionlint passed. GitHub repository, environments, OIDC trust/grants and backend are not configured, and no Actions run occurred.
- Rechecked the original consumed foundation plan SHA256: `386fceff8f67a42d8e51f20d6bf521b59fc4244a5e8e3186d8cbe76178178622` (unchanged). No additional Sandbox, Azure apply, RBAC/network/credential change or GitHub write occurred after M0-CLI97.
- **External gates:** [M0-C-FAIL approval](./pending-approvals.md#m0-c-fail--prepared-not-executed); dedicated GitHub owner/vetted public fixture/project repository; Entra registration and remote-state choices; then exact deployment/publication plans and approvals. Full A/B/C, managed-identity data access, authenticated Azure dashboard/SSE/replay and demo rehearsal remain open. Project is **not complete**.

## Sandbox telemetry implementation — 2026-10-14

- Official [telemetryConfig documentation](https://sandboxes.azure.com/docs/sandboxes/telemetry) verified: per-create LogAnalytics endpoint, DCE, DCR stream and group-assigned managed identity. SDK 0.1.0b4 silently ignores unknown creation kwargs; a pinned, exact-create-path subclass now inserts telemetryConfig before the official SDK transport serializes it. Tests assert one request, preserved built-in disk and credential connection, and reject inline secrets/unrelated endpoints.
- Added an ingestion-only UAMI (distinct from host identity), DCE, DCR, custom workspace table, DCR-scoped Monitoring Metrics Publisher and group identity PATCH under terraform-builder. Scoped saved plan contains five new Azure resources plus one identity PATCH, zero deletions/replacements or unrelated changes. Apply is in progress. Preserved external Storage SecurityControl tag; no network fix attempted.
- A/B/C runtime now emits only fixed workflow-boundary metadata to container stdout, with run/Sandbox/role correlation; DCR filters project records and drops non-contract fields. No prompts, PATs, source or command output enters this stream. Live ingestion remains to be verified.
- 67 Python tests and six offline Terraform tests passed. Standing project authorization replaces recurring approval gates; app Fix confirmation and destructive-operation limits remain.

## Continued live validation — 2026-10-14

- Telemetry apply completed: six Terraform additions (including group identity PATCH), no deletions/replacements. Added DCR LogErrors diagnostics after verifying the actual category. Exact-create SDK compatibility adapter preserves disk and provider connection. GET omits telemetryConfig; ingestion must prove delivery. DCR metrics and LAW table have no records yet.
- Entra apply completed: five additions, zero changes/deletions. API `9f0d4700-e68d-4153-b366-124ec470b6be`, SPA `3a06f8f3-8e74-4ea9-a59d-a21003d3507b`; secretless PKCE. Persisted origin in private inputs to prevent an accidental future destroy plan. Login unverified.
- Captured sanitized extension startup diagnostics: `TypeError: meta.phases is not iterable`. Fixed required metadata in A/B/C. C subsequently loaded and ran a real AI patch. Built-in Python lacks ensurepip; validation now uses venv --without-pip and official pip 26.2 wheel pinned to SHA256 `931c303696af6fa3417112103b1cad26890e5a07eccb5b99783700e33f2b8aad` inside the Sandbox.
- M0-C-FAIL passed: Sandbox `5fc61a0e-6a13-4c47-b50f-34064630b151`, run `962729cd-14da-4756-86b6-29be211ea93f`. Create 5.767s, workflow 21.679s, cleanup 2.308s, total 36.491s. venv/dependencies/build passed; actual pytest exit 1; publication skipped; exact-ID GET404. Prior attempts also confirmed deleted. Evidence `.local/m0-c-fail-telemetry-06.json`.
- Published reviewed source fixture and license to https://github.com/ij-23/academo-fastapi-fixture, SHA `c1c3d2b` (full immutable SHA is verified before each run). No fixture code executed locally; GitHub publication here is the input fixture, not C's required same-PAT result.
- Remote-state choice requested because terraform-builder explicitly requires it; independent manual deployment continues.

## Azure host and same-PAT publication evidence — 2026-10-14

- Azure HTTPS application deployed with digest ownership in Terraform. Browser Entra PKCE login passes; anonymous operational API returns 401; readiness confirms managed identity access to all four private containers. Live A/B enabled; publication remains disabled pending PAT write access.
- Official Node SDK 1.0.21 grants only the trusted extension's `extension-env-access` request for COPILOT_GITHUB_TOKEN. Genuine credential workflow GET /user verified ij-23/User. No credential was copied to the backend.
- Same group PAT created private `ij-23/academo-pat-check-20261014` (repository ID 1418649119, HTTP201), but harmless git push failed HTTP403, “Write access to repository not granted.” Exact-empty-repository retry reproduced it; no overwrite or second repository creation. Evidence `.local/publication-pat-02.json`; retry Sandbox 67c2a860-5a5c-4922-bea3-80074e9eca67 created in 1.259s, deleted in 1.820s, exact-ID404 verified. User must verify All repositories/future access and Contents read/write, then manually update group credential if needed.
- First deployed A/B run `d09f309c-0122-45f8-a2a2-0e85c844516a` pinned c1c3d2bcd0f33eddfd77d29249c3a04c0130da1e. Separate A dc236e32-2354-4aa6-9e07-9b14ec2e15c4 and B 551d3f52-bee5-47fd-ab96-98172036e675 overlapped, then failed on workflow event payload `kind` colliding with a Python parameter. Both deleted/exact404; durable events visible in dashboard. Renamed event-type parameters and added regression coverage. Retry pending deployment.
- ARM readback of environment/blob diagnostics returns null logAnalyticsDestinationType after repeated Dedicated applies. Configuration now accepts documented default routing; explicit Consumption app profile matches service readback. Diagnostic categories and LAW destination retained.

## Real A/B result and telemetry/persistence corrections — 2026-10-14

- Run e4af7981-6b40-4cbe-85f9-348c1b9afdbf completed in 26s at source c1c3d2bcd0f33eddfd77d29249c3a04c0130da1e. A 9979aad4-6d27-4dec-a360-137d1eaeb926 and B 99020fa1-b38b-4c17-a90d-60e03fc6e5d2 ran concurrently. A genuine Copilot review returned source-verified path traversal; B venv/dependencies/build passed, pytest had 2 passed/2 failed, runtime skipped, genuine AI analysis completed. Dashboard showed both timelines and 48 real events. Both ownership records are deleted and exact404 checks completed.
- Persistence inspection from the deployed host found only the final event in Blob: Azure create_append_blob overwrites existing content by default. Fixed conditional creation with MatchConditions.IfMissing; regression models real destructive initialization. Earlier run timelines are NOT durable complete replay evidence. Revalidation of new runs is required.
- C telemetry run c1285860-9b2e-4973-88ec-3f0516a831e1, Sandbox586a8350-32f0-49f0-a88d-3327ed5fbde0: the container entrypoint tails a fixed metadata journal to stdout; LAW ingested18 correlated records. This succeeds where detached-exec /proc/1/fd/1 writes did not. Genuine C failed-validation branch passed, create0.809s, cleanup2.307s, total30.771s, deleted/exact404. Same forwarding path is now in the application adapter; A/B revalidation pending.
- Terraform image-only update applied0 additions/1 change/0 destroy. Recurring diagnostic and Consumption-profile drift resolved in configuration. Original consumed foundation plan preserved.

## Durable Azure A/B and all-role telemetry verified — 2026-10-14

- Latest run4fbb0295-6786-4e3d-b697-8f18ec4575c2 completed in27s. Exact A23fb901f-4ff7-4096-bca9-243217072a83 and Bd4ff1f55-2ae7-4c58-b77f-020fbc4617f3 deleted. Reading Blob through the deployed host UAMI returned48 contiguous events1–48, both reports and deleted ownership records. Prior truncated histories remain identified as invalid replay evidence.
- LAW returned11 security and10 build records for this exact run, plus18 remediation records from the C failed-validation run. Official telemetryConfig ingestion now passes for every role. The entrypoint journal-to-stdout route is the verified implementation.
- AI returned an incorrect source line in the last review; verification correctly marked that finding unverified. Security prompt now supplies numbered source lines; exact source verification remains strict. Do not convert an unverified finding into a verified one merely to enable Fix.
-68 platform Python tests,6 offline Terraform tests, frontend build/test, actionlint and isolated application-container checks pass. These are distinct from live Azure evidence.
- Created public project destination https://github.com/ij-23/aca-sandbox-demo under standing authorization. Project source publication/CI is independent of the blocked same-PAT C publishing path.

## Operational controls and CI — 2026-10-14

- Trusted controls probe Sandbox0cfa210f-02ec-4770-8697-5a7aef37d8e2: timeout1s terminated sleep10 with exit124; allowed github.com returned200; default-denied example.com returned403. Creation0.996s, cleanup8.907s, exact404 verified. Protected Sandbox remained Stopped; no fixture execution, PAT exposure or ingress. This validates shell timeout and outbound rule behavior, not a full host-crash recovery drill.
- Public project push f4eb686 succeeded. First hosted CI failed only because the last smoke CLI help-text edit needed Ruff formatting; fixed and retrying. No Azure deployment was triggered by that platform-only CI.

## Hosted CI and final verification checkpoint — 2026-10-14

- GitHub Actions [Platform checks run38543168107](https://github.com/ij-23/aca-sandbox-demo/actions/runs/38543168107) passed on84fe8b8: locked dependency install, lint/format,68 Python tests, schema export, workflow syntax, frontend tests/build and isolated application image check. No fixture code executed on the runner.
- Fresh Terraform plan returned **No changes** after drift corrections. ACR contains only academo-app. Original source fixture SHA remains c1c3d2bcd0f33eddfd77d29249c3a04c0130da1e. Anonymous GET/POST runs, remediation and cleanup all returned401.
- Remaining external dependencies: user confirmation of corrected group PAT repository write/future-repository access; explicit remote-state choice required by terraform-builder for an actual OIDC deployment pipeline. Edge window became unavailable (cgWindowNotFound), so additional browser reconnect/cancellation checks cannot currently proceed. Earlier real Azure Entra login and A/B UI observations remain valid; do not claim unperformed C/replay/rehearsal checks.

- Source-alignment Terraform apply completed: image-only update,0 added/1 changed/0 destroyed. Deployed app digest742939758418493cf0116983b46870855dcd2f56d174de2bc4c018ec21c49d5f includes the numbered-source prompt change; that final prompt refinement still awaits another live review after browser access resumes.
- Final official SDK inventory contains only protected5bf17eda-250b-4c90-9cd6-bd44a5610851, Stopped. All latest A/B/C/control/publication-probe IDs independently returned404. Original consumed foundation plan SHA256 remains386fceff8f67a42d8e51f20d6bf521b59fc4244a5e8e3186d8cbe76178178622.
- Project remains **INCOMPLETE**: no successful fixed repository, no complete A/B/C replay, no OIDC Azure deployment run, no full15-minute rehearsal or clean-subscription install proof. Do not confuse genuine C failed-validation success with the successful publishing branch. Resume from the external dependencies; do not repeat foundation apply or create another test repository.

## Successful C publication and local-state decision — 2026-10-14

- Fresh group-PAT harmless push passed to the exact existing private test repository; verified SHA `1f9fe8d42bb5f364d352d5d2b784492b9a6b53e1`. Probe Sandbox exact404 after finally cleanup. No token printed or substituted.
- Publication enablement plan/apply changed only PUBLICATION_ENABLED on the existing app: 0 additions, 1 in-place update, 0 deletions. Existing local state and original consumed foundation plan retained.
- Authenticated Azure dashboard run `ffe4af9f-f911-491b-b00c-327b3d84605f`: A/B concurrent at original `c1c3d2bcd0f33eddfd77d29249c3a04c0130da1e`; A source-verified path traversal; B expected 2 passed/2 failed. Single Fix confirmation launched C `8d9da772-0066-450a-a118-42702df758f2` and all real stages were visible, including AI running, validation, repository creation, push, remote verification and deletion.
- C succeeded: 4 pytest passed, 2 targeted regressions passed, build/localhost health/source integrity passed. Private `ij-23/academo-fastapi-fixture-fixed` ID1418760503, remote SHA `d84155b39cd758e6e22b8db51036d72eda5c9f3d` independently read from GitHub. Original SHA unchanged. C provisioning1.182s, cleanup1.183s, approval-through-cleanup35.5s from persisted events.
- Deployed UAMI read-back proves all95 contiguous events, A/B/C reports, exact matching private diff and three deleted ownership records. Captured genuine replay in private replay Blob and [event fixture](../fixtures/replay-events.jsonl); UI replay validation ongoing. Evidence `.local/full-abc-verified.json`.
- Explicit user decision: LOCAL Terraform state only. Removed the hosted-runner remote-backend requirement from the release workflow. Preparing build-only OIDC (new dedicated UAMI + main-branch federation + AcrPush on this ACR); no app/Blob/Sandbox/directory grants. Hosted Actions publishes a digest manifest; the existing local state holder plans/applies it. Fully automated Terraform-on-Actions would need a trusted persistent runner; none installed.
