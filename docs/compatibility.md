# Compatibility ledger

## Verified M0-CLI97 — 2026-10-14

**Passed genuine Dynamic Workflow execution inside ACA.** The [approved test](./pending-approvals.md) created one built-in `copilot` Sandbox with the existing provider connection, downloaded only the approved checksum-pinned official 1.0.97 into its disposable directory, and deleted that Sandbox with exact-ID HTTP 404 verification. Detailed timings and IDs are in [progress](./progress.md#approved-m0-cli97-result--2026-10-14); private [sanitized evidence](../.local/m0-cli97-evidence.json) contains actual commands/results. Older sections below are historical and superseded where stated.

Verified calls: `begin_create_sandbox(...).result(timeout=90)`, `get`, `exec`, `write_file`, `read_file`, `delete`, `list_sandboxes`, and exact-ID `get`. Verified invocation: `GITHUB_COPILOT_PROMPT_MODE_EXTENSIONS=true copilot --experimental --no-auto-update --no-custom-instructions --disable-builtin-mcps --available-tools=read --deny-tool=read workflow run aca-viability-smoke --args @input.json --result-file result.json --output-format json`. The CLI warns `read` is unknown in 1.0.97 (actual tool is `view`); the observed subagent used zero tools. No silent prompt substitution or login occurred.

`defineWorkflow`, `joinSession({workflows})`, `ctx.step`, `ctx.agent`, `ctx.phase`, `ctx.log`, `ctx.runId` and `ctx.signal` worked. Returned deterministic sum 5, genuine AI pong and verified actual-result branch, three timed results and six boundary events. Native JSON output includes `session.extensions_loaded`, `workflow.run_started`, `workflow.run_updated`, `subagent.started/completed`, `workflow.run_settled`, `workflow.result`, and message deltas. SDK `exec` returns completed results; detached execution plus SDK `read_file` polling **did** retrieve progress while running. This proves polling, not native SDK exec streaming.

Current Storage: Enabled public network, Allow default rule, HTTPS/TLS1.2, no public blobs/shared keys. Endpoint reachable; operator OAuth read denied by authorization. No networking fix attempted. App UAMI runtime access remains untested. CLI extension secret access and same-PAT GitHub publication remain separate gates; the smoke requested no secret environment access.

## Prepared compatible-CLI test and local platform — 2026-10-13

The [M0-CLI97 request](./pending-approvals.md) is awaiting approval. No additional Sandbox has been created. The [harness](../scripts/smoke_test_sandbox.py) preserves the verified `disk="copilot", connections=[existing_id]` binding and accepts `--expected-cli-version 1.0.97 --pinned-cli`. The opt-in helper downloads the official Linux x64 standalone archive to a fresh disposable control directory, verifies SHA256 `07f3f63cb361e911268e8a4b010e06eeced8d4f2d898d13a8180273e34aeff3f`, and invokes that binary without changing the image/system installation. Source: [official release](https://github.com/github/copilot-cli/releases/tag/v1.0.97). Automatic updates stay disabled. No downloaded CLI or AI operation has been executed locally.

Static source confirms `defineWorkflow`, `joinSession({workflows})` and direct workflow dispatch in 1.0.97. It does **not** establish entitlement, successful registration inside ACA, agent results, extension environment permissions or concurrent file polling. The smoke requests no secret environment access. C's ability to perform GitHub writes with the same injected PAT remains a separate explicit gate; do not bypass extension environment restrictions.

Independent application checks now pass: 49 Python tests, one frontend test, TypeScript/Vite build, Ruff, JSON-schema consistency, npm audit (zero advisories), AMD64 application image build and an isolated local container check. The container ran with network disabled, no Azure identity, UID 10001 and read-only filesystem: dashboard/assets/health 200, unconfigured readiness 503, anonymous operations 401. The owned container was removed. Browser inspection found and fixed the backend static-asset directory mismatch. These are platform results, not Azure Dynamic Workflow evidence.

SDK exec remains a completed-result interface. The prepared detached runner polls JSONL/status files; genuine progress visibility is still unverified. The platform SSE layer persists before delivery, keeps an eight-run/256-event-per-run memory window, and reads older events from Blob for resume. Stored event logs have a 15 MiB write budget below the 16 MiB read cap. Ambiguous append recovery, ring-buffer eviction/resume, cleanup retry/restart, stale consent and wrong destination rejection are covered by unit-test doubles. Blob network/RBAC access, Entra login and actual A/B/C telemetry remain unverified in Azure.

## Current comparison: user-reported CLI 1.0.97 — 2026-10-13

**Do not generalize the 1.0.83 finding to every current ACA Copilot sandbox.** The user reports CLI **1.0.97** in a manually created GitHub Copilot sandbox. The official 1.0.97 package supports the required API; the exact sandbox/executable behind that observation still needs identification.

Read-only inspection of subscription `be9948d2-4149-4be2-a040-ef1a6dc1c866`, group `sbg-academo-a3dcd3b3` in `rg-academo-a3dcd3b3`, Sweden Central, returned only sandbox `5bf17eda-250b-4c90-9cd6-bd44a5610851`. It is now **Running** (previously Stopped; this investigation did not start it). Its metadata contains `preset=copilot`, `workload=ai-coding`, CPU `4`, memory `8Gi`, no ports, and `sourcesRef.diskImage={id:"11346a0c-e721-415b-a078-bbdba5ddabe2",isPublic:false}`. The referenced disk GET returned 404, so its provenance could not be resolved. The public `copilot` listing remains Ready with metadata updated `2026-10-08T22:08:04.4028225+00:00`; that timestamp is not a verified CLI version.

| Comparison | Previous disposable SDK smoke | Existing sandbox inspected now |
| --- | --- | --- |
| Creation selection | `disk="copilot"`, explicit existing credential connection, 1 CPU / 2 GiB | Portal preset label `copilot`; private disk reference, 4 CPU / 8 GiB |
| Version | 1.0.83 | **1.0.83 in the exec environment**, not the user-reported 1.0.97 |
| Executable context | SDK shell command | Read-only `aca sandbox exec`: user `root`, executable `/usr/local/bin/copilot` |
| Workflow help | General help despite experimental flag | General help; no direct workflow usage, `--args` or `--result-file` |

Existing-sandbox checks used `timeout --kill-after=2s 15s env COPILOT_AUTO_UPDATE=false copilot --no-auto-update --version` and the same prefix with `--experimental workflow run --help`. Identity/path inspection used `id -un`, `command -v copilot`, and `readlink -f`. No agent, extension or workflow was executed; no files were delivered or edited, and no sandbox was created, started, stopped or deleted. Each CLI call had a local timeout, and the original Azure CLI subscription was restored and verified after every inspection block. `aca sandbox exec -o json` returns plain command stdout here, so output was parsed as text rather than assuming an SDK `ExecResult` JSON envelope.

### Official 1.0.97 capability evidence

The [official Linux x64 1.0.97 artifact](https://github.com/github/copilot-cli/releases/download/v1.0.97/github-copilot-1.0.97-linux-x64.tgz) was downloaded and read statically, without installing or executing it. SHA-256 matches the [release API](https://api.github.com/repos/github/copilot-cli/releases/tags/v1.0.97): `7348b753e9f8cbd032cecd36c78010ee7c9b874452714c035af29e4ab7302e7b`. Package version `1.0.97`, build commit `0ce88c54`.

- `copilot-sdk/extension.js` actually exports `defineWorkflow`; its declaration exposes `workflows?: WorkflowHandle[]`.
- `joinSession()` extracts `workflows` and passes `{workflows}` to `resumeSessionForExtension`.
- Bundled SDK sends `session.workflow.run` requests. CLI `cli-main.js` dispatches `case "workflow run"` to `runWorkflowRunCommand`, calls `sessionClient.workflow.run`, and implements result-file handling and `workflow.result` output.
- Project extension trust checks recognize `GITHUB_COPILOT_PROMPT_MODE_EXTENSIONS=true`. Use it only for this project's reviewed extension.

**Result:** 1.0.97 has the required Dynamic Workflow API and command implementation. Authentication, extension loading and an actual workflow run with that version remain unverified. The known creation-path difference and possible interactive executable/automatic-update differences are hypotheses, not a proven explanation for 1.0.83 versus 1.0.97. The user was asked for the sandbox ID/portal URL that showed 1.0.97. Do not upgrade or create another sandbox until the correct target is identified and the required approval is obtained. The reusable harness now requires an explicitly reviewed expected version (default 1.0.97) and optionally uses a checksum-pinned 1.0.97 binary in its disposable control directory. This is a prepared path, not a live test result; see the pending approval below.

## Historical 1.0.83 conclusion

Checked 2026-10-13. **The official CLI 1.0.83 package lacks the documented Dynamic Workflow API.** Static inspection now establishes more than the previous help-only probe: its bundled extension SDK exports `defineFactory`, not `defineWorkflow`, and `joinSession` registers `factories`, not `workflows`. Its CLI source contains the experimental flag and extension trust opt-in, but no documented direct workflow command or result-file option. See the static investigation below. No additional sandbox, CLI upgrade, agent execution or Azure change occurred during this investigation. Genuine workflow execution and live progress remain unverified.

## Static CLI 1.0.83 investigation — 2026-10-13

The previous `workflow run --help` check, even with `--experimental`, was insufficient by itself to prove runtime incompatibility. The current conclusion instead uses the official release's actual SDK exports, registration implementation and CLI source, compared with the two requested GitHub documentation pages.

### Documented invocation and extension trust

The [Dynamic Workflow guide](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-dynamic-workflows) requires experimental features. The [programmatic reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-programmatic-reference) documents direct execution, JSON arguments, output and trust. Their combined invocation is:

```sh
# Documented syntax for a compatible CLI; NOT a successful 1.0.83 invocation.
# Run only from our isolated trusted control project containing our extension.
GITHUB_COPILOT_PROMPT_MODE_EXTENSIONS=true \
  copilot --experimental workflow run aca-viability-smoke \
  --args @workflow-input.json --output-format json \
  --result-file workflow-result.json
```

- Discovery paths: `.github/extensions/<name>/extension.mjs` for a project, and `~/.copilot/extensions/<name>/extension.mjs` for the default personal configuration. The entry point must be an ES module named `extension.mjs` inside its own extension directory.
- Copilot automatically resolves the bundled `@github/copilot-sdk/extension`; installing an unrelated newer SDK does not prove compatibility with the CLI runtime.
- Project extensions require a trusted folder or explicit per-invocation `GITHUB_COPILOT_PROMPT_MODE_EXTENSIONS=true`. Limit this opt-in to our reviewed control extension; never enable discovery of submitted repository extensions. It permits extension code loading and does **not** grant tool permissions.
- Direct execution does not prompt for tool approvals. Preconfigure only the required narrow permissions; prompt/session flags such as `-p`, `--agent`, `--fleet`, `--autopilot`, `--resume` and `--continue` are unsupported with this command. No ordinary prompt is a substitute.
- JSON output can contain progress records and a final `workflow.result` envelope. `--silent` suppresses progress; omit it when investigating observability. A result file is written only after completion with a returned value; use a fresh path.
- The [pinned official SDK workflow guide](https://github.com/github/copilot-sdk/blob/6259d096a5970ab9c3b124b9c269bfc8b47985b5/nodejs/docs/workflows.md) defines `defineWorkflow({meta, run})` and `joinSession({workflows: [handle]})`. This current documentation does not promise these APIs in 1.0.83.

### Version-specific package evidence

Inspected the [official Linux x64 1.0.83 release asset](https://github.com/github/copilot-cli/releases/download/v1.0.83/github-copilot-1.0.83-linux-x64.tgz), downloaded for static reading only. Its SHA-256 matches the digest in the [GitHub release API](https://api.github.com/repos/github/copilot-cli/releases/tags/v1.0.83): `888f8fbb4575c335afba4a8863c647ef04f81e5124c7c794bdcaee90c5fa4503`. Release date: 2026-09-04. Package metadata: version `1.0.83`, build commit `e6a98f1`. No package installation or execution was performed.

| Check | Actual package evidence |
| --- | --- |
| Global experimental switch | `app.js` defines `.option("--experimental","Enable experimental features")` and passes the parsed setting into feature-flag resolution as `isExperimental`. The prior sandbox probe already supplied it. |
| Project-extension opt-in | `app.js` explicitly tests `process.env.GITHUB_COPILOT_PROMPT_MODE_EXTENSIONS === "true"` and adds `project` to the prompt-mode extension sources. The switch exists in 1.0.83. |
| Extension discovery/loading | Bundled `copilot-sdk/docs/extensions.md` documents project/user extension discovery, `.mjs` entry points, a child process with automatic SDK resolution, and `joinSession()` attachment. |
| Required named export | The complete runtime export list of `copilot-sdk/extension.js` is `Canvas`, `CanvasError`, `FactoryResumeError`, `createCanvas`, `defineFactory`, `isFactoryRunTerminal`, `joinSession`. **No `defineWorkflow` export exists.** The declaration file agrees. |
| Required registration | `JoinSessionConfig` declares `factories?: FactoryHandle[]`. Runtime `joinSession()` extracts `factories` and passes it to `resumeSessionForExtension`; no workflow registration implementation exists in this bundle. |
| Session API | Bundled code exposes `session.factory` / `session.factory.run` and factory events. It contains no `workflow.run` / `workflow.register` API. These older factory APIs are not proof of support for the documented Dynamic Workflow contract and were not substituted. |
| Direct invocation | CLI `app.js` contains no `workflow run`, `--result-file` or `--args <...>` handler/option strings. This supports the previous general-help observation; the missing SDK export is the decisive additional blocker. |

An extension importing the documented `defineWorkflow` named export cannot link against this bundled SDK. This is a static ESM export/registration incompatibility, **not an observed live extension error**, a missing PAT, or an omitted experimental/trust switch. Sensitive environment access is a separate extension boundary: the bundled guide says sensitive variables are stripped unless explicitly requested and approved. Our smoke extension does not request token access; CLI agent authentication uses the existing connection binding.

**Conclusion and limits:** standard official CLI 1.0.83 cannot execute our extension through the documented Dynamic Workflow interface. The ACA image previously reported 1.0.83; its binary/package checksum was not captured, so this inspection does not independently rule out an Azure-specific patched build. A current compatible built-in image or an explicitly approved, pinned CLI update inside a disposable sandbox is the next path to test. No minimum supported version is claimed from release dates alone. No new live Azure test is needed to establish the official package mismatch; any verification of the exact ACA build or a newer CLI requires new user approval before sandbox creation. Nothing was upgraded.

## Evidence matrix

| Area | Observed evidence | Unverified gate |
| --- | --- | --- |
| Sandbox service | Target group operational; one SDK `begin_create_sandbox(disk="copilot")` reached Running, no ports, and was deleted with exact GET 404 confirmed | UAMI runtime access, broader concurrency/capacity and failure-path cleanup behavior |
| Python API | Installed SDK signatures/source inspected; creation, exec, get/list/delete exercised. `exec` returns completed `ExecResult(exit_code, stdout, stderr)`; delete is asynchronous | File transfer and workflow result capture, cancellation/failure-path tests. Source docstring references `create_sandbox`, but this class has no such public method; use verified `begin_create_sandbox` |
| SDK package | SDK 0.1.0b4 / Azure Identity 1.26.0 installed through configured Microsoft proxy on Python 3.13.16; import, relevant method signatures and one live sandbox lifecycle verified | Untested features must still be validated individually |
| Built-in Copilot disk | SDK `list_public_disk_images()` returned `copilot` Ready; created using public disk name plus explicit credential connection; CLI **1.0.83** authenticated | Compatible workflow CLI/image needed: official 1.0.83 lacks the documented API even though experimental flags exist |
| Group credentials | API connection state Ready / portal Configured verified; explicit `connections=[existing_credential_id]` injected `COPILOT_GITHUB_TOKEN`; prompt succeeded without login | Reusable harness now requires and passes the verified connection ID. PAT publication permissions and workflow eligibility remain unverified |
| Data-plane RBAC | Eight approved grants read back with matching principals/scopes; group Data Owner role `c24cf47c-5077-412d-a19c-45202126392c` granted to UAMI and operator [S2]; signed-in User listing works, with pre-existing broader grants unchanged | UAMI runtime access; user listing does not isolate which inherited/new grant authorized it |
| File transfer | `write_file` uploaded the trusted capability helper, and SDK `exec` executed it successfully. `read_file` is source-inspected and documented [S6] | Workflow extension transfer/round-trip, result retrieval and live file polling were not reached |
| Exec/streaming | Installed `exec` performs a synchronous POST to `executeShellCommand`, parses a completed JSON response; actual CLI stdout/stderr and exit codes retrieved | No public exec streaming interface found in 0.1.0b4. CLI `--stream` exists but does not turn this SDK call into streaming; concurrent file polling/alternative transport remains untested |
| Workflow feature | Public-preview code-defined Dynamic Workflows confirmed by GitHub [S8, S9] | Combined built-in image, CLI, extension ABI and account eligibility |
| Workflow registration | Official SDK guide uses `defineWorkflow({meta, run})` and `joinSession({workflows: [...]})` [S11]; official 1.0.83 bundle lacks both and exposes factory APIs | Minimal real extension must load and execute with a compatible CLI inside the sandbox |
| Workflow invocation | Fresh sandbox CLI 1.0.83 returned identical general help even with `--experimental`; static official package inspection confirms missing documented API/command options. Local CLI 1.0.91 recognizes the exact command | No genuine run verified; exact ACA package bytes, account eligibility and compatible runtime execution still require an approved live test |
| Terraform ARM contract | 2026-07-01 template has `properties.environmentId` [S13] | Preview group defaults, limits and policy management cannot be assumed in this contract |
| Terraform preview example | Official module at pinned commit uses 2026-02-01-preview; rich-preview fields, `schema_validation_enabled = false` [S14, S15] | Installed provider schemas and target API registration/field persistence |
| App auth | Entra existing-registration setup documents optional client secret; default automatic registration creates one [S16] | Verify secret-free login choice, trust boundary, session/CSRF behavior, authConfig/provider support |

## Workflow integration details

Trusted workflow code will be JavaScript `extension.mjs` under a trusted control repository's `.github/extensions/<name>/` directory. The extension SDK is supplied by Copilot's loader; do not assume a separately installed SDK matches the built-in CLI. Keep the submitted checkout outside this discovery root. [S12]

The documented noninteractive mechanism is direct invocation of the registered workflow, with JSON arguments and a fresh result path. GitHub documents `--experimental` for enabling the feature and `GITHUB_COPILOT_PROMPT_MODE_EXTENSIONS=true` for loading an untrusted-directory project extension in noninteractive mode. That opt-in must apply only to our trusted control directory, never to submitted repository configuration. Grant narrow required tools explicitly. [S8, S10]

Source-confirmed API identifiers include `ctx.agent`, `ctx.step`, `ctx.phase`, `ctx.log`, `ctx.signal`, and the workflow run envelope. Agent calls can resolve to `null`; output schema enforcement is only structural, so the backend needs independent strict validation. Progress observation includes `getRunProgress` and `workflow.run_updated` inside the owning session; these do not establish a backend streaming transport. [S11]

The result file is written only for successful completion with a returned result; an old file can survive a failed invocation. Use a fresh run directory and validate the run envelope and report provenance before consuming any result. [S10]

GitHub's current concepts page excludes certain legacy annual Pro/Pro+ billing plans. The SDK guide says ineligible execution can fail with JSON-RPC `-32601` and `data.code = dynamic_workflows_unavailable`. A configured PAT badge or successful ordinary prompt is insufficient proof. [S9, S11]

Observed local CLI: **1.0.91**. Live sandbox CLI: **1.0.83**. The initial trusted noninteractive prompt failed before authentication; the subsequent authorized authentication-only diagnosis succeeded after attaching the existing credential connection. No genuine workflow has executed, no repository was cloned, and no repository code was executed locally or in the sandbox.

## Auth, egress, and resource schema decisions

Use a manually configured group PAT with Copilot Requests permission, a dedicated account, and a short expiry. The token must not traverse the host application. Runtime credential behavior must be checked without printing environment variables or credential files. Credential rotation requires fresh/restarted sandboxes. [S5, S17]

The user selected `swedencentral`. Target subscription metadata advertises Sandbox Groups and the host Managed Environment there; stable and preview Sandbox Group list GETs succeeded. The regional usage endpoint reports SandboxCores 0/20000 and ManagedEnvironmentCount 1/50. This is observed quota, not reserved runtime capacity. The general Microsoft quota page says 2,000 Sandbox/Express cores, so retain the distinction between general guidance and the target response. [S18, S22]

GitHub's allowlist guidance uses its public metadata API and includes the apex `github.com` separately from wildcard domains. Derive Copilot domains from current official guidance and account routing, then include verified clone and locked Python-package download hosts. No complete egress policy has been validated. CLI tool URL permissions do not replace sandbox network enforcement. [S19]

The sandbox egress guide documents `set_egress_policy(EgressPolicy(...))` and create-time policy controls. Persistent group policy provisioning must have a verified Terraform owner; applying a per-sandbox SDK policy does not prove that the required static group configuration is IaC-managed. TLS inspection and Copilot traffic must be tested together. [S20]

The ARM template and rich-preview module describe different contracts. The latter includes `defaultCpu`, `defaultMemory`, `defaultDisk`, `maxSandboxCount`, and `defaultTimeoutSeconds`, with schema validation disabled. Do not copy these fields into the stable resource body or assume enforcement. The scoped embedded-schema exception below is required by the missing provider schema and does not establish service acceptance. Confirm target API versions and inspect returned settings. `environmentId` is optional and an established link cannot be changed or removed; leave the Sandbox Group independent as required. [S13, S15]

Registry metadata returned AzureRM **5.9.0**, AzAPI **2.13.0**, and AzureAD **3.10.0**. The portal quickstart instead constrains AzureRM to **4.x** and also uses a prerelease `Azure/aca` provider for individual sandbox resources. This project creates individual sandboxes at runtime; it does not need to adopt that provider for lifecycle management. Persistent policy support still needs inspection. The implementation now locks AzureRM 4.81.0 and AzAPI 2.13.0; their installed runtime schemas were inspected. AzureAD is not used in this bootstrap. [S14, S21]

## Implemented foundation contracts

AzureRM **4.81.0** and AzAPI **2.13.0** are installed and locked; Terraform **1.15.3** completed validation and five offline mock-provider tests. Constraints permit only patch updates within the chosen minor versions; the lock selects exact versions. These checks do not validate cloud acceptance.

| Resource | Implementation and verified API |
| --- | --- |
| Resource group | AzureRM; [2023-07-01](https://learn.microsoft.com/en-us/azure/templates/microsoft.resources/2023-07-01/resourcegroups) |
| UAMI | AzureRM; [2024-11-30](https://learn.microsoft.com/en-us/azure/templates/microsoft.managedidentity/2024-11-30/userassignedidentities) |
| ACR | AzureRM; [2025-11-01](https://learn.microsoft.com/en-us/azure/templates/microsoft.containerregistry/2025-11-01/registries) |
| ACA Environment | AzureRM; [2025-07-01](https://learn.microsoft.com/en-us/azure/templates/microsoft.app/2025-07-01/managedenvironments) |
| App Insights | AzureRM; [2020-02-02](https://learn.microsoft.com/en-us/azure/templates/microsoft.insights/2020-02-02/components) |
| RBAC assignments | AzureRM; [2022-04-01](https://learn.microsoft.com/en-us/azure/templates/microsoft.authorization/2022-04-01/roleassignments) |
| Log Analytics | AzAPI; [2025-07-01](https://learn.microsoft.com/en-us/azure/templates/microsoft.operationalinsights/2025-07-01/workspaces), local auth disabled |
| Storage account | AzAPI; [2025-06-01](https://learn.microsoft.com/en-us/azure/templates/microsoft.storage/2025-06-01/storageaccounts), HTTPS/TLS 1.2, shared keys/public blobs disabled |
| Blob containers / retention | AzAPI; [containers](https://learn.microsoft.com/en-us/azure/templates/microsoft.storage/2025-06-01/storageaccounts/blobservices/containers) and [management policies](https://learn.microsoft.com/en-us/azure/templates/microsoft.storage/2025-06-01/storageaccounts/managementpolicies), 2025-06-01 |
| Sandbox Group | AzAPI; stable 2026-07-01 [S13], empty `properties`, independent from ACA Environment |

AzureRM API choices were cross-checked against resource implementation imports in [provider v4.81.0](https://github.com/hashicorp/terraform-provider-azurerm/tree/v4.81.0/internal/services). Storage/LAW intentionally use AzAPI because AzureRM exports shared keys into state. ACA uses [Azure Monitor diagnostics](https://learn.microsoft.com/en-us/azure/container-apps/log-options), avoiding a LAW shared-key connection. The host UAMI receives [Monitoring Metrics Publisher](https://learn.microsoft.com/en-us/azure/azure-monitor/app/azure-ad-authentication) for authenticated App Insights ingestion. Blob diagnostics use the [documented categories](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/supported-logs/microsoft-storage-storageaccounts-blobservices-logs).

**Scoped validation exception:** AzAPI 2.13.0 rejected Sandbox Group with `resource type Microsoft.App/sandboxGroups can't be found`. Only that resource disables embedded schema validation, consistent with the official module [S15]. Other AzAPI resources keep validation enabled. The body contains none of the rich-preview limits/egress fields. Approved real apply/read-back now confirms this minimal stable body is accepted in the target subscription; group limits/persistent egress remain unresolved gates.

## Prepared smoke contract

The [harness](../scripts/smoke_test_sandbox.py), [sandbox helper](../scripts/smoke_workflow_runner.py) and [extension](../workflows/smoke/extension.mjs) implement the documented `copilot` disk, explicit existing credential connection and direct workflow path. Default execution prints a plan with zero Azure calls. Live mode requires an explicit exact group confirmation and connection ID. The prepared extension journals deterministic preparation (sum of 2 + 3), includes an explicit three-second file-observation window, calls real `ctx.agent`, and branches on the actual structured response before journaling verification. It emits timestamped boundary events and returns per-step results and durations. These workflow operations are prepared, not live-verified. The [workflow API source snapshot](https://github.com/github/copilot-sdk/blob/6259d096a5970ab9c3b124b9c269bfc8b47985b5/nodejs/docs/workflows.md) records the reviewed contract; built-in image compatibility remains untested.

The harness now starts a bounded workflow process in the sandbox and polls its status and complete JSONL event records via SDK `read_file`, then retrieves the result and a CLI log redacted inside the sandbox. This file-polling path is **not yet live-verified** because the CLI capability gate stopped execution first. `exec` itself still returns completed output. The harness validates fresh results/event provenance and deletes only owned sandboxes in `finally` with a separate deadline, protecting all pre-existing IDs. A returned sandbox must be absent on direct lookup, not merely missing from a list. Lost create responses remain explicitly ambiguous even if label reconciliation finds nothing. Fourteen tests use doubles only; no cloud/workflow success is implied.

**Current blocker before reuse:** provider binding is implemented and live-verified. The targeted CLI 1.0.83 does not expose the documented direct workflow command in the tested help probe. A new sandbox authorization and a reviewed compatible built-in image/CLI version are needed before another live attempt. No automatic CLI upgrade was performed.

The [list documentation](https://staging.sandboxes.azure.com/docs/sandboxes/sandboxes) and [labels documentation](https://staging.sandboxes.azure.com/docs/sandboxes/sandbox/labels) disagree about filtered-list keywords. The implementation avoids those keywords, lists and matches exact ownership labels locally. Created client `sandbox_id` versus listed record `id` follows the [lifecycle documentation](https://staging.sandboxes.azure.com/docs/sandboxes/sandbox/lifecycle). Installed SDK inspection is still mandatory before execution.

## Exact unresolved blockers / limitations

1. The foundation remains deployed and unchanged. The earlier smoke, authentication-diagnosis and latest workflow-capability sandboxes were each separately authorized and deleted, with exact-ID 404 verification. All three one-sandbox approvals are consumed. Another live attempt needs newly approved sandbox scope; GitHub repository creation, Terraform changes, app deployment and public ingress remain excluded.
2. SDK download and automatic Copilot authentication blockers are **resolved**. SDK 0.1.0b4 requires an explicit existing credential connection for the verified disk-based creation path. The reusable harness now passes that binding. The latest `--experimental` capability probe did not expose the documented direct workflow command; genuine workflow execution remains blocked.
3. Docker daemon is unavailable at the configured desktop socket. This blocks local image validation, not documentation review or a future approved CI image build.
4. Target-service reads, registration, regional quota, deployer permissions, stable group creation and one sandbox lifecycle/exec capture are verified. Group limits/egress ownership, secret-free app auth, remote cancellation, file polling and Copilot workflow ABI remain open. Local Terraform validation used the narrow Sandbox Group schema exception.
5. Real sandbox lifecycle, failed and successful prompt, credential injection and cleanup evidence exists; no successful Dynamic Workflow, remediation or genuine demo replay exists. Never imply these gates passed.
6. Inherited `MCAPSGovDeployPolicies` / `StorageAccount_PublicNetwork_Modify` forced Storage public network access to Disabled, despite the saved plan/state body requesting Enabled. Activity Log confirms the policy modification; no private endpoint exists. Future app Blob connectivity requires a separately reviewed solution. This does not block group PAT setup or the trusted nonce smoke, which does not use Blob. No corrective Azure mutation or new plan was performed.

## Experimental Dynamic Workflow attempt — 2026-10-13

**Outcome: failed capability gate; no genuine workflow execution.** This is a compatibility result, not an authentication regression. Private [sanitized live evidence](../.local/workflow-smoke-2026-10-13.json) includes exact command arrays, captured CLI help/stdout/stderr, ownership, and before/after inventories. No token value was exported.

| Check | Observed result |
| --- | --- |
| Existing credential | Read-only CLI metadata guard confirmed the selected `github-copilot` connection Ready; `DefaultAzureCredential` used the existing Azure CLI identity |
| Create | Exactly one request; built-in `copilot`, `connections=["4e86451e-7ec1-434e-8b1b-cbfc4088960d"]`, 1 vCPU/2 GiB, no ports; returned connection read back |
| CLI and credential | Version **1.0.83**; `COPILOT_GITHUB_TOKEN` set; `GH_TOKEN` and `GITHUB_TOKEN` unset. No regular prompt was used |
| Experimental flag | Present in top-level help; flag accepted by the help invocation |
| Direct workflow command | **Failed gate:** experimental workflow help equals general help; no `workflow` subcommand, `--args` or `--result-file` |
| SDK file upload | Trusted helper uploaded using `write_file` and executed using `exec`; passed |
| Genuine extension delivery/run | Not reached: stopped before extension upload and direct execution |
| Workflow exit code, step results, output, duration | Not available: no workflow process started. Help probes exited 0 with empty stderr; those are not workflow exit codes |
| Workflow progress/streaming | Not reached. Prepared SDK file polling remains unverified; no observed step events or workflow logs exist |
| Cleanup | `delete()` in `finally`, exact-ID GET **404**, final listing excludes the created sandbox |

The live commands were bounded invocations of:

```sh
copilot --version
copilot --no-auto-update --experimental --help
copilot --no-auto-update --experimental workflow run --help
```

All three exited **0**. Both help outputs began `Usage: copilot [options] [command]` and were identical, rather than showing `Usage: copilot workflow run [OPTIONS] <name>`. The command list lacked `workflow`. The prior smoke's missing-`--experimental` uncertainty is therefore resolved for **this exact direct-command help probe**. Do not generalize this to proof that every internal extension API is absent, or that the account is ineligible: neither was invoked.

For comparison, the same local **1.0.91** help-only command shows `Usage: copilot workflow run [OPTIONS] <name>`, `--args`, `--result-file`, `--silent` and `--output-format`. No local workflow/agent execution occurred. Official releases date [1.0.83 to September 4](https://github.com/github/copilot-cli/releases/tag/v1.0.83) and [1.0.91 to October 1](https://github.com/github/copilot-cli/releases/tag/v1.0.91); the [Dynamic Workflows announcement](https://github.blog/changelog/2026-10-01-dynamic-workflows-in-copilot-cli-and-the-copilot-app/) is October 1. This supports a built-in image/CLI compatibility mismatch; these observations do not establish the minimum supported release or guarantee 1.0.91 workflow success in Azure.

Actual Azure methods: `SandboxGroupClient`, `endpoint_for_region`, `list_public_disk_images`, `list_sandboxes`, `begin_create_sandbox(...).result(timeout=90)`, `SandboxClient.get`, `exec`, `write_file`, `delete`, and `get_sandbox_client` for owned-only cleanup. `read_file` and its planned progress-polling path were inspected but not executed in this attempt. Creation used 80s polling timeout/2s interval, no retries; calls had 10s connect/90s read limits. Each version/help subprocess had a 20s timeout inside a 70s exec timeout with 5s kill grace. The complete work budget was 400s, cleanup separately 100s. No timeout occurred. If reached, the prepared workflow has a 180s internal limit, 210s command timeout with 5s kill grace, 220s process watchdog and 235s observation budget.

Created ID **`bb472511-ea6a-4caf-b57e-2e92c04bd93a`**; creation **1.010s**, cleanup **6.879s**, total **13.529s**. The final inventory contained only **`5bf17eda-250b-4c90-9cd6-bd44a5610851`**, still **Stopped**. The original Azure CLI default subscription was restored and verified. No second sandbox, CLI update, group-credential change, Terraform operation, GitHub repository, public ingress or application deployment occurred.

**Next step requires approval:** obtain a refreshed built-in Copilot disk with a compatible CLI, or explicitly approve a pinned official CLI update *inside a future disposable sandbox* while retaining the built-in disk and existing credential binding. Recheck the command/extension ABI before running. Do not rebuild the image or substitute a prompt for a Dynamic Workflow. If the platform is expected to ship the newer feature already, share the sanitized version/help evidence, region and deleted sandbox ID with Azure support. No support request was sent. Milestone 0 remains incomplete; application development has not started.

## Authentication diagnosis — 2026-10-13

**Root cause:** the initial SDK request selected the built-in Copilot disk but omitted its provider credential connection. A configured group credential is available for attachment; plain `disk="copilot"` did not automatically attach it. The same CLI version and disk authenticated after explicitly passing the existing connection ID. No evidence from this test requires PAT replacement or a platform incident.

### Credential status and documented mechanism

- Read-only `aca sandboxgroup credential list --subscription <target> --resource-group rg-academo-a3dcd3b3 --group sbg-academo-a3dcd3b3 --region swedencentral -o json` returned `name/type = github-copilot`, ID `4e86451e-7ec1-434e-8b1b-cbfc4088960d`, state `Ready`. Output was restricted to these metadata fields.
- The [official portal client](https://sandboxes.azure.com/assets/index-D0CpZwJV.js), retrieved on this date, maps `isConfigured` to `connection.state === "Ready"` and renders **Configured**. This verifies the badge semantics from the portal's implementation and live API state; it is not a claim of having inspected an authenticated browser screenshot.
- [Provider credential documentation](https://staging.sandboxes.azure.com/docs/sandboxes/credentials) says credentials are stored as group connections and the platform injects tokens at startup. Running instances are not automatically restarted on rotation. Its general wording omits the explicit attachment needed by this disk-based SDK path.
- Installed ACA CLI **1.0.0-preview.2** documents `aca sandbox create --disk copilot --credential <id>`. SDK **0.1.0b4** exposes `connections: list[str] | None`; inspected source sends those IDs as the request's `connections` field, separately from disk selection. It does not discover/attach group credentials itself. Credential management is not exposed in this SDK. No token value belongs in `environment` or the caller.
- The portal Copilot template submits `presetSandboxType: "GitHubCopilot"`; the SDK has a separate `preset` argument. That preset path was inspected but **not live-tested**. The verified solution below keeps the requested `copilot` disk and attaches the connection explicitly. Provider `connections` are distinct from external API/MCP `gatewayConnections`.
- [Built-in image documentation](https://staging.sandboxes.azure.com/docs/sandboxes/disk-images) describes `copilot` as backing the GitHub Copilot preset, using systemd as PID 1, with Copilot CLI/GitHub CLI/Node.js/Python and a boot-time Git-authentication unit. The page does not specify an environment variable or credential-file path. The variable mechanism below is **live evidence**, supported by [GitHub's CLI authentication documentation](https://docs.github.com/en/copilot/how-tos/copilot-cli/set-up-copilot-cli/authenticate-copilot-cli), which gives `COPILOT_GITHUB_TOKEN` first priority. No credential files or values were printed.

### Verified SDK creation and execution

Using the existing Azure CLI identity through `DefaultAzureCredential` and the target subscription/tenant, the diagnosis invoked:

```python
# Existing, non-secret group connection ID; no PAT is supplied by the caller.
sandbox = client.begin_create_sandbox(
    disk="copilot",
    connections=["4e86451e-7ec1-434e-8b1b-cbfc4088960d"],
    cpu="1000m", memory="2048Mi", ports=[],
    labels=unique_ownership_labels,
    auto_suspend_seconds=300,
    polling_timeout=80, polling_interval=2,
).result(timeout=90)
```

The returned sandbox was Running, had no ports, and its `connections` contained that exact ID. A trusted Python probe invoked through `SandboxClient.exec` checked only whether each variable was set and then launched Copilot as a direct subprocess with its environment inherited unchanged. It used no `sudo`, user switch, login shell, `/login`, environment replacement or manual PAT injection.

| Variable | Present in SDK command / inherited Copilot environment |
| --- | --- |
| `COPILOT_GITHUB_TOKEN` | Set |
| `GH_TOKEN` | Unset |
| `GITHUB_TOKEN` | Unset |

`copilot --version` returned **1.0.83**. `copilot --help` confirmed the safety flags before the following prompt, in an empty temporary directory:

```sh
timeout --kill-after=5s 90s copilot \
  --no-auto-update --no-custom-instructions --disable-builtin-mcps \
  --available-tools=read --deny-tool=read \
  -p 'Reply with exactly ACA_AUTH_PONG. Do not use tools or inspect any files.'
```

Result: **exit 0**, expected response **`ACA_AUTH_PONG`**, **4.127s**. Only the expected response marker, exit code, timings and fixed diagnostic booleans were retained; arbitrary CLI stdout/stderr was not exported. No token values, lengths, prefixes, hashes or fragments were emitted. Automatic authentication works in the SDK exec environment with explicit binding. Success establishes Copilot access at test time, not GitHub repository-creation/push permissions or Dynamic Workflow eligibility.

### Cleanup, bounds and conclusion

- Exactly one create request, retries disabled (`retry_total=0`); sandbox `d49f0e6c-6868-4030-addc-07a228a1dbb6`. Creation **1.109s**, cleanup **6.513s**, total including preflight/restoration **18.201s**.
- Independent bounds: 10s transport connect / 145s read, 80s creation polling / 90s poller result, 15s CLI version/help each, 90s prompt with 5s kill grace, 140s outer probe with 5s grace, 280s local work deadline and 100s separate cleanup deadline. No timeout occurred; timeout-path cleanup is not claimed as exercised.
- `delete()` executed in `finally`; direct GET of the diagnostic ID returned **404**, and final group listing contained only pre-existing `5bf17eda-250b-4c90-9cd6-bd44a5610851`, still **Stopped**. No operation modified that sandbox. Original Azure CLI subscription context was restored and verified.
- Private [sanitized evidence](../.local/auth-diagnosis/735e5a1ac26c4f4e83c56c25c80a5736.json), [executed runner](../.local/auth-diagnosis/run.py) and [trusted probe](../.local/auth-diagnosis/probe.py) preserve reproducibility. **Do not rerun the runner without a new sandbox authorization.**
- Solution: resolve an existing Ready `github-copilot` connection and attach its ID when creating from the disk. Update the reusable harness/adapter during the next approved work item. No credential changes or Terraform changes are needed for this demonstrated authentication fix. If a future correctly bound fresh sandbox lacks the variable, collect sanitized connection state, sandbox ID, region, versions and timestamps for Azure support; this run does not show such a platform failure.
- Stopped after authentication diagnosis. No Dynamic Workflow, repository clone/create/push, public ingress or app deployment occurred. All Terraform artifacts remain unchanged; saved-plan SHA-256 still matches the previously reviewed value.

## Executed one-sandbox smoke — 2026-10-13 (historical, before authentication fix)

Private [results and exact commands](../.local/live-smoke/results-2026-10-13.md) and [sanitized execution evidence](../.local/live-smoke/9e933970b6fc4327bcca778ff9ee63d9.json) record this attempt. Only trusted locally authored control code was used; no third-party clone, GitHub write, credential change, Terraform edit or app deployment occurred. The original saved-plan SHA-256 remains unchanged.

| Check | Result |
| --- | --- |
| Installed SDK/source/signatures | Passed: SDK 0.1.0b4, Azure Identity 1.26.0, Python 3.13.16 |
| Authentication to Azure | Passed: `DefaultAzureCredential` restricted to cached Azure CLI credential; correct subscription selected temporarily and original default restored |
| Disk, create and ingress | Passed: SDK discovered `copilot` Ready; one `disk="copilot"` sandbox, 1 vCPU/2 GiB, no ports; Running in **1.413s** |
| `copilot --version` | Passed: **GitHub Copilot CLI 1.0.83**, retrieved via `ExecResult.stdout` |
| Minimal noninteractive prompt | Failed in **1.463s**, exit 1, empty stdout; stderr: **No authentication information found**. No `/login`, token read or injection workaround |
| Workflow capability probe | `copilot workflow run --help` exited 0 but returned general help without `--args` or `--result-file`; runner stopped before extension upload. Missing `--experimental` in this probe limits the conclusion |
| Genuine workflow / structured events | Not executed; no workflow result or step events generated/retrieved |
| CLI output capture | Passed: synchronous `exec` returned stdout/stderr/exit code for actual commands; sanitized outputs saved |
| Streaming | Source inspection confirms completed-response `exec`; no public incremental exec interface. CLI help advertises `--stream`, which does not establish SDK streaming. File polling and delayed-output probe were not reached |
| Cleanup | Passed: `delete()` in finally, exact-ID `get()` returns 404, final list excludes test sandbox. **6.729s**; pre-existing sandbox still Stopped and untouched |
| Total duration | **19.290s** from preflight through cleanup |

Actual methods: `endpoint_for_region`, `SandboxGroupClient`, `list_public_disk_images`, `list_sandboxes`, `begin_create_sandbox(...).result(timeout=100)`, `SandboxClient.get`, `exec`, `get_sandbox_client`, `delete`, and exact-ID `get` polling. `write_file(path, content, *, create_dirs=True, mode=None, container_name=None, **kwargs)` and `read_file(path, *, container_name=None, **kwargs) -> bytes` were inspected but never exercised. `exec(command, *, working_directory=None, **kwargs) -> ExecResult` sends a synchronous POST to `executeShellCommand`; arbitrary timeout kwargs are not forwarded by this implementation. Use the transport-level and shell deadlines instead. `delete(**kwargs)` returns immediately and requires separate disappearance polling.

Creation used `begin_create_sandbox(disk="copilot", cpu="1000m", memory="2048Mi", ports=[], labels=<unique ownership>, auto_suspend_seconds=300, polling_timeout=90, polling_interval=2).result(timeout=100)`. One request only, `retry_total=0`; transport connection/read limits 10/240s. Overall local deadline 540s and independent cleanup deadline 100s. Commands used `timeout --kill-after=5s`: version/help/setup 15s, prompt 90s; planned workflow bound 210s was not exercised. No actual timeout occurred; this run does not prove timeout cleanup paths. Auto-suspend is not an auto-delete guarantee.

The prompt was `copilot --no-auto-update --no-custom-instructions --disable-builtin-mcps --available-tools=read --allow-tool=read -p 'Reply with exactly ACA_SMOKE_PONG. Do not use tools or inspect any files.'`, in a fresh trusted control directory. The SDK returned the CLI's authentication error, rather than a model response. The [official credentials guide](https://staging.sandboxes.azure.com/docs/sandboxes/credentials), fetched again, describes group credentials as connections and automatic injection on startup. The tested public-disk request supplied no explicit connections. Investigate that binding and disk-versus-preset behavior without assuming the PAT is invalid or silently changing the requested disk path. A later authorized attempt should also check the workflow command with documented experimental flags before judging the built-in CLI's capabilities. No second sandbox or CLI/image update was attempted.

## Live smoke attempt — 2026-10-13 (historical preflight, blocked before creation)

| Test | Observed result |
| --- | --- |
| Approved target identity/region | Passed: explicit target subscription resolves the original customer tenant/User; ARM group read returned Sweden Central, Succeeded and `https://management.swedencentral.azuredevcompute.io` |
| Built-in disk | Passed: `aca sandboxgroup disk list-public` returned `copilot` with `status.state = Ready` |
| Group data-plane inventory | Passed after selecting the correct cached CLI subscription temporarily; one pre-existing Stopped sandbox, no smoke ownership label; untouched |
| Official SDK installation/inspection | Blocked by PyPI artifact-host connection failure; isolated Python 3.13.16 configured, pinned SDK not installed |
| SDK sandbox creation | Not attempted; zero create requests, zero smoke sandbox IDs |
| In-sandbox Copilot CLI/version and automatic authentication | Not run; PAT configured per user, runtime injection and entitlement unknown; no `/login` |
| Minimal prompt/output | Not run; no prompt result captured |
| Genuine Dynamic Workflow/step and result retrieval | Not run; prepared extension remains unverified against the built-in image |
| Output streaming | Unverified; prepared harness uses exec completion plus file retrieval, not proven live streaming |
| Deletion and timings | Not applicable: no test sandbox was created or deleted, so creation/cleanup durations are unmeasured. Do not report a cleanup pass. Pre-existing sandbox remains untouched |

Actual read-only commands used: `az account show --subscription <approved-subscription>`, `az resource show --subscription <approved-subscription> --ids <group-arm-id> --api-version 2026-07-01`, `aca sandboxgroup disk list-public`, and `aca sandbox list`, with explicit target subscription/resource-group/group/region. The local CLI default belonged to a different tenant. Explicit subscription fixed the ARM read, but `aca sandbox list` still returned 403 until the cached Azure CLI default was temporarily selected with `az account set`; a shell EXIT trap restored the prior default and a follow-up read confirmed restoration. No new login, role grant or credential export occurred. This demonstrates an identity-context pitfall, not failure of the configured Copilot PAT.

**Actual SDK methods/Copilot commands executed: none.** The current official [Python quickstart](https://learn.microsoft.com/en-us/azure/container-apps/sandboxes-quickstart-python-sdk), fetched again during this attempt, documents `SandboxGroupClient`, `endpoint_for_region`, `begin_create_sandbox(...).result()`, `sandbox.exec(...)` returning `stdout`, and `sandbox.delete()`. The prepared harness also expects `list_public_disk_images`, `list_sandboxes`, `write_file`, `read_file`, `get_sandbox_client` and `get`. These remain documented/planned methods, not runtime-verified usage. Likewise `copilot --version` and `copilot ... workflow run aca-viability-smoke ...` in the harness were not executed. The harness still needs a separate minimal-prompt check, exact subscription-bound SDK authentication inspection, Ready-state validation, creation/cleanup timing, and programmatic output/transport observations before its first approved live execution.

Downloads were bounded by 10-second connection and 20–30-second total curl timeouts; uv stopped after its retries. No sandbox runtime timeout was exercised. Restore access to the exact PyPI artifact host or provide the official SDK wheel and dependencies with verified hashes before retrying. Do not substitute CLI sandbox creation for the requested official SDK. C publication and its test repository remain separate unverified gates and are explicitly outside this smoke approval. See private [smoke preflight results](../.local/azure-discovery/smoke-preflight-2026-10-13.json).

### Correction: configured package proxy resolved installation

The user's pip settings in `/Library/Application Support/pip/pip.conf` and `/Users/ij/.config/pip/pip.conf` both select Microsoft's `https://packagefeedproxy.microsoft.io/pypi/simple/` index. The venv has no pip module; initial `uv pip install` did not inherit these settings. Direct curl retries also bypassed the configured proxy. The earlier recommendation to restore public PyPI connectivity was premature.

Successful command: `uv pip install --python /Users/ij/Dev/aca-sandbox-demo/.venv/bin/python --index-url https://packagefeedproxy.microsoft.io/pypi/simple/ -r requirements-smoke.txt`. Installed 24 packages including `azure-containerapps-sandbox==0.1.0b4` and `azure-identity==1.26.0`. Import of `SandboxGroupClient` and `endpoint_for_region` passed. No pip/uv configuration, Terraform artifact or cloud resource was modified; no sandbox was created. Runtime verification remains pending.

## Deployment verification — 2026-10-12

The private [deployment results](../.local/azure-discovery/deployment-results.md) link all 23 ARM read-backs, eight scoped grants, outputs, empty sandbox/app inventories and policy evidence. `aca` CLI `1.0.0-preview.2 (8d2c5ff 2026-08-31, build 20260901.1)` read the deployed group successfully using existing Azure authentication. Built-in disk Ready status establishes availability only; credential injection, actual sandbox CLI and Dynamic Workflow execution still require the later approved smoke. UAMI identity/role existence is verified, not runtime access from a deployed host.

## Sources reviewed

### Azure discovery update — 2026-10-12

The private [deployment review](../.local/azure-discovery/deployment-review.md) records exact identities, scopes, all 23 additions and plan SHA-256. Existing Azure resources and assignments were read only. All required providers are registered; no relevant deny assignment or lock was observed. Effective subscription permissions include unconditional `actions: ["*"]`, supported by inherited Owner. Entra application-registration/consent rights are a separate later check.

The current [Bicep quickstart](https://learn.microsoft.com/en-us/azure/container-apps/sandboxes-quickstart-bicep) and pinned Terraform module confirm that group defaults/count/timeout belong to the rich-preview profile. Stable and preview reads returned existing groups but no limit fields. The Terraform quickstart describes defaults as applying when clients do not override them. Read success cannot establish a hard count or timeout cap; no mutation was used to test persistence.

[Microsoft Learn's egress guide](https://learn.microsoft.com/en-us/azure/container-apps/sandboxes-egress-policies) specifies create-time and runtime sandbox policies, with Full inspection blocking non-HTTP traffic. The portal SDK guide explicitly warns that no policy means unrestricted outbound traffic. Default Deny plus Full inspection and narrow HTTPS rules is the intended runtime policy; no verified static group-wide Terraform policy is included. This resolves where documented controls belong but leaves the project requirement for persistent group-wide enforcement open.

GitHub's public `/meta` returned Copilot domains `*.github.com`, `*.githubusercontent.com`, `default.exp-tas.com`, `*.githubcopilot.com`; its official guidance adds apex `github.com`. Clone/API and Python dependency candidates include `github.com`, `api.github.com`, `codeload.github.com`, `pypi.org`, and `files.pythonhosted.org`. Narrow these to the selected account and vetted fixture and test them with Copilot/TLS inspection inside the approved sandbox; this is not a validated allowlist.

### Reference list

- **S1:** [Microsoft Learn — Sandboxes overview](https://learn.microsoft.com/en-us/azure/container-apps/sandboxes-overview).
- **S2:** [Microsoft Learn — Python SDK quickstart](https://learn.microsoft.com/en-us/azure/container-apps/sandboxes-quickstart-python-sdk).
- **S3:** [PyPI SDK metadata](https://pypi.org/pypi/azure-containerapps-sandbox/json).
- **S4:** [Microsoft Sandbox portal — built-in disk images](https://staging.sandboxes.azure.com/docs/sandboxes/disk-images).
- **S5:** [Microsoft Sandbox portal — provider credentials](https://staging.sandboxes.azure.com/docs/sandboxes/credentials).
- **S6:** [Microsoft Sandbox portal — file transfer](https://staging.sandboxes.azure.com/docs/sandboxes/sandbox/files).
- **S7:** [Microsoft Sandbox portal — shell versus exec](https://staging.sandboxes.azure.com/docs/sandboxes/sandbox/interactive-shell).
- **S8:** [GitHub announcement — October 1, 2026](https://github.blog/changelog/2026-10-01-dynamic-workflows-in-copilot-cli-and-the-copilot-app/).
- **S9:** [GitHub — Dynamic Workflow concepts and eligibility](https://docs.github.com/en/copilot/concepts/agents/dynamic-workflows).
- **S10:** [GitHub — using Dynamic Workflows](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-dynamic-workflows).
- **S11:** [GitHub SDK — workflow API guide](https://github.com/github/copilot-sdk/blob/main/nodejs/docs/workflows.md), read directly from the official repository. The `main` branch is mutable; pin the compatible source during implementation.
- **S12:** [GitHub SDK — extensions](https://github.com/github/copilot-sdk/blob/main/nodejs/docs/extensions.md) and [authoring guide](https://github.com/github/copilot-sdk/blob/main/nodejs/docs/agent-author.md).
- **S13:** [Microsoft ARM/AzAPI — Sandbox Groups 2026-07-01](https://learn.microsoft.com/en-us/azure/templates/microsoft.app/2026-07-01/sandboxgroups).
- **S14:** [Microsoft Sandbox portal — Terraform quickstart](https://sandboxes.azure.com/docs/sandboxes/quickstart/setup-terraform).
- **S15:** [Official pinned Sandbox Group module](https://github.com/Azure/terraform-provider-aca/blob/debaefd1c08d8156a3291c48432dd4ca63e0fbed/modules/sandbox_groups/main.tf) and [inputs](https://github.com/Azure/terraform-provider-aca/blob/debaefd1c08d8156a3291c48432dd4ca63e0fbed/modules/sandbox_groups/variables.tf).
- **S16:** [Microsoft Learn — Container Apps Entra authentication](https://learn.microsoft.com/en-us/azure/container-apps/authentication-entra); [authConfig schema search result](https://learn.microsoft.com/en-us/azure/templates/microsoft.app/2026-07-01/containerapps/authconfigs) identified, full schema/provider inspection still pending.
- **S17:** [GitHub — CLI command reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference).
- **S18:** [Microsoft Sandbox portal — regions](https://staging.sandboxes.azure.com/docs/sandboxes/regions).
- **S19:** [GitHub — network allowlist](https://docs.github.com/en/copilot/reference/copilot-allowlist-reference).
- **S20:** [Microsoft Sandbox portal — egress policy](https://staging.sandboxes.azure.com/docs/sandboxes/sandbox/egress).
- **S21:** Terraform Registry metadata: [AzureRM](https://registry.terraform.io/v1/providers/hashicorp/azurerm), [AzAPI](https://registry.terraform.io/v1/providers/Azure/azapi), [AzureAD](https://registry.terraform.io/v1/providers/hashicorp/azuread).
- **S22:** [Microsoft Learn — Container Apps quotas](https://learn.microsoft.com/en-us/azure/container-apps/quotas); target regional `Microsoft.App/locations/swedencentral/usages?api-version=2026-07-01` read-only response.

Staging portal documentation is explicitly identified above. Treat it as published guidance requiring production-runtime confirmation, not proof of deployed behavior.

## Post-smoke runtime/deployment implementation — 2026-10-14

The real adapter now uses the verified creation/binding, upload/read/exec and
exact-ID deletion APIs. It installs the same pinned 1.0.97 only in owned Sandbox
control directories. A/B/C extensions use the verified definition/registration,
step/agent and JSON result APIs. Production transport polls a trusted JSONL journal;
terminal command output is captured on command completion, while real workflow
boundaries are observable during execution. Native CLI logs are sanitized inside
the Sandbox; only a bounded tail is delivered. This adapter and the full workflows
remain **locally tested but not exercised in Azure**.

The inspected official 1.0.97 extension declaration documents
`requestedEnvironmentVariables: ["COPILOT_GITHUB_TOKEN"]`: sensitive variables are
stripped at extension startup, and the CLI requests explicit permission before
returning granted variables. Denial prevents loading. The exact noninteractive
approval mechanism remains unverified. C requests this only when publication is
authorized/enabled, never scrapes another process or copies a PAT into a file.
Therefore Copilot authentication success still does not establish C publishing
capability. No GitHub repository API or push has been tested with the group PAT.
The prepared M0-C-FAIL test does not request credential access for publication.
It uses Copilot service traffic but makes no repository API/clone/push calls.

Official [repository REST documentation](https://docs.github.com/en/rest/repos/repos#create-a-repository-for-the-authenticated-user)
confirms POST /user/repos, private=true and auto_init=false. Prepared publishing
checks the personal /user identity, destination availability and response identity,
creates a fresh sanitized-source commit, pushes with a credential helper reading
only the granted environment variable, then verifies private identity and remote
refs/heads/main SHA. X-Accepted-GitHub-Permissions is captured without token values.
Fine-grained endpoint permissions and actual push still need the approved live test.

SDK 0.1.0b4 exports EgressPolicy, EgressRule, EgressRuleMatch and EgressRuleAction
from azure.containerapps.sandbox (not a models submodule). Their installed
constructors support default_action, traffic_inspection and host-match rules.
The adapter prepares default Deny/Full inspection with the documented GitHub,
Copilot and PyPI host candidates. No policy is changed in the existing group;
this is a future create-time policy and is not yet live-proven. Microsoft Learn
[documents create-time/runtime scopes](https://learn.microsoft.com/en-us/azure/container-apps/sandboxes-egress-policies),
not a persistent group-wide Terraform policy contract. That original requirement
remains unresolved, rather than being silently claimed as satisfied.

Application Terraform uses locked AzureRM 4.81.0's inspected container_app schema:
UAMI image pull, digest image, HTTPS ingress, single revision, one replica and
explicit probes. Default null application input keeps foundation-only behavior.
Validation and six offline tests pass; no application plan/apply or auth registration
is claimed. PKCE + delegated JWT verification is prepared; Microsoft Learn confirms
secret-free EasyAuth login uses implicit flow, which this app does not adopt.


### Extension permission boundary: additional static evidence

Read-only inspection of the official 1.0.97 release confirms that the CLI classifies
requested filtered variables, submits an `extension-env-access` permission request,
and rejects extension loading unless its result is `approved`. Only then does it
resolve the granted variables and register workflows. The SDK writes granted
values into the requesting extension's environment before `joinSession` resolves.
This agrees with the official [extension documentation](https://github.com/github/copilot-sdk/blob/main/nodejs/docs/extensions.md).
Project-extension trust alone is insufficient evidence of this grant. The prepared
noninteractive runner's grant remains unverified; no blanket permission flag,
credential scraping, token file or alternate identity has been introduced.
