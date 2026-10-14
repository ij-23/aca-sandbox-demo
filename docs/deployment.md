# Foundation deployment and Milestone 0

> **Current execution authorization (2026-10-14):** Project-scoped Sandbox tests/cleanup, Terraform apply, Azure deployment and GitHub publishing are authorized autonomously under [AGENTS.md](../AGENTS.md#project-execution-authorization--2026-10-14). Recurring approval checkpoints below are superseded. Technical validation, product Fix confirmation, protection of unrelated resources and the prohibition on destructive operations remain.

This guide covers the Terraform foundation and deployed Azure React/FastAPI host. The initial 23-resource foundation was extended with DCE/DCR/ingestion identity, Entra registrations and the Container App. Browser Entra sign-in, managed-identity Blob readiness and real run/event persistence pass. Genuine CLI1.0.97 and M0-C-FAIL tests passed. Full A/B/C validation is ongoing; same-PAT private repository creation succeeds but push currently returns403. See the current compatibility ledger before enabling publication.

The [README](../README.md) is the canonical customer guide. See the [compatibility ledger](./compatibility.md) for verified schemas and current blockers, and [progress](./progress.md) for test results.

## What this slice creates

The [Terraform root](../infrastructure/terraform/) creates a dedicated resource group, application ACR, host UAMI, Consumption-profile Container Apps Environment, workspace-based Application Insights, Log Analytics workspace, StorageV2 account, four private artifact containers, lifecycle retention, diagnostics, Sandbox Group, and scoped RBAC. With application and entra_public_origin inputs it also provisions the application and secretless SPA/API registrations. Sandbox telemetry adds DCE/DCR/custom table and an ingestion-only UAMI. Image build/push is a separate step; temporary Sandboxes remain runtime-managed. GitHub OIDC trust is not configured yet.

Terraform modules are grouped by resource group, registry, identity, monitoring, storage, sandbox group, and access. AzureRM 4.81.0 and AzAPI 2.13.0 are locked. Local state is the current default; no remote backend is provisioned. Keep state and saved plans private, backed up and excluded from Git. Resolve a durable locked backend before implementing GitHub Actions deployment.

Storage public blob access and shared-key authentication are disabled. The approved configuration requested a public HTTPS endpoint with Entra authorization. The user resolved the earlier inherited-policy networking issue. Read-only verification on 2026-10-14 shows publicNetworkAccess Enabled and a reachable Blob HTTPS endpoint. Anonymous access is denied, and the operator lacks Blob data permissions. No networking fix was attempted. App UAMI grants were read back; deployed-host readiness and real event writes verified UAMI Blob access. Blob roles are assigned at each container. Log Analytics/Storage use ARM resources to avoid fetching shared keys into Terraform state. The environment sends logs through Azure Monitor diagnostics, avoiding a workspace-key connection. Application Insights disables local authentication; its exported connection string/instrumentation identifier does not grant ingestion access. The future host needs its UAMI and Monitoring Metrics Publisher role to send telemetry.

## Required values and permissions

| Item | Requirement |
| --- | --- |
| Subscription/tenant | Explicit UUIDs for the intended customer deployment; never infer them from the CLI default |
| Region | Public-cloud region supporting both Sandboxes and Container Apps; verify provider metadata and quota |
| Naming | A new 3–12 character lowercase alphanumeric prefix; globally unique storage/ACR names derive from it and the subscription |
| Sandbox operators | Entra **object IDs** and principal types for credential setup and smoke execution; no automatic deployer data access |
| Read-only planning | Sign-in to intended tenant/subscription; permission to read resource/provider metadata, role definitions and existing state resources |
| Foundation apply | Permission to create the dedicated RG and listed resource types; permission for `Microsoft.Authorization/roleAssignments/write` at intended resource scopes. Contributor alone cannot grant RBAC; an appropriately scoped RBAC administrator or equivalent is needed |
| Provider registration | Microsoft.App, Microsoft.ContainerRegistry, Microsoft.ManagedIdentity, Microsoft.Storage, Microsoft.OperationalInsights and Microsoft.Insights must already be registered, or their registration needs a separately approved admin action |
| Smoke/PAT setup | Container Apps SandboxGroup Data Owner on the exact group; supported Copilot account/billing and fine-grained PAT with Copilot Requests |

The app UAMI gets AcrPull at ACR, SandboxGroup Data Owner at the group, Storage Blob Data Contributor on each of four containers, and Monitoring Metrics Publisher at Application Insights. Sandbox operators receive only the group data role. This does not grant web-user access; Entra web authorization is a later gate.

Provider auto-registration is explicitly disabled in both providers so a plan cannot silently register resource providers. This may expose missing registrations instead of automatically fixing them.

## Local preparation and validation

Run from the repository root. Use Python 3.13, Node 24 and an isolated virtual environment. Terraform 1.11+ is required for foundation work under the mandatory skill. Platform checks never execute fixture repository code:

```bash
uv venv --python 3.13 .venv
uv pip sync --python .venv/bin/python --require-hashes requirements-dev.txt
npm ci --prefix frontend --ignore-scripts
.venv/bin/ruff check backend scripts
.venv/bin/ruff format --check backend scripts
.venv/bin/python -m pytest backend/tests scripts/tests -q
.venv/bin/python scripts/export_schemas.py --check
npm --prefix frontend test
npm --prefix frontend run build
terraform -chdir=infrastructure/terraform init -input=false
terraform -chdir=infrastructure/terraform fmt -check -recursive
terraform -chdir=infrastructure/terraform validate
terraform -chdir=infrastructure/terraform test
.venv/bin/python -m unittest discover -s scripts/tests -v
node --check workflows/smoke/extension.mjs
.venv/bin/python scripts/verify_environment.py
```

The Terraform tests use mock providers and the Python unit tests use explicit doubles. They do not authenticate to Azure or run Copilot. SDK installation and actual method inspection have passed. In this environment, uv must explicitly use the configured public Microsoft proxy because it does not read pip configuration:

```sh
uv pip sync --python .venv/bin/python --require-hashes \
  --index-url https://packagefeedproxy.microsoft.io/pypi/simple/ requirements-dev.txt
docker build --platform linux/amd64 -t aca-sandbox-demo:local \
  --build-arg PIP_INDEX_URL=https://packagefeedproxy.microsoft.io/pypi/simple/ \
  --build-arg NPM_REGISTRY=https://packagefeedproxy.microsoft.io/npm/ .
```

The Dockerfile defaults to public PyPI/npm registries; both overrides are non-secret URLs. Never use authenticated URLs or credentials in build arguments. The SHA256-locked Python requirements and npm integrity hashes still apply. The build context excludes local environments, dependencies, Terraform artifacts and credentials. The final image contains only the Python host and built React assets, runs as UID 10001, and keeps live execution disabled. No Copilot binary or custom Sandbox image is built.

The [CI workflow](../.github/workflows/ci.yml) runs these platform checks and builds an image without Azure access or publishing. The [configuration example](../.env.example) lists required non-secret application settings. The current host implements MSAL SPA PKCE plus Entra v2 delegated access-token validation in FastAPI; it requires customer SPA/API registrations, `access_as_user` consent, API v2 tokens and authorized user object IDs. Browser Entra login, authorized run creation and anonymous401 checks passed in the deployed instance. See [architecture](./architecture.md) for the network and deployment-state decisions still needed.

## Prepare the real deployment plan

1. Copy [terraform.tfvars.example](../infrastructure/terraform/terraform.tfvars.example) to a private `terraform.tfvars` beside it, replace every placeholder and review the operator object IDs. Do not put a PAT or any credential in this file.
2. Authenticate the Azure CLI to the intended tenant if needed. Sign-in and selecting context are user prerequisites; this implementation never changes the active subscription automatically.
3. Run the read-only preflight with explicit identifiers:

```bash
.venv/bin/python scripts/verify_environment.py --azure \
  --subscription-id '<subscription-uuid>' \
  --tenant-id '<tenant-uuid>' --region '<region>'
```

This checks registration, relevant API versions/locations, role-definition presence, and local SDK signatures. It does not prove effective role-assignment permission, quota availability or live Copilot access.

4. Produce and review a saved plan:

```bash
terraform -chdir=infrastructure/terraform plan -input=false -out=foundation.tfplan
terraform -chdir=infrastructure/terraform show -no-color foundation.tfplan
```

**Current result (2026-10-12):** after explicit approval, the exact reviewed [academo foundation plan](../infrastructure/terraform/academo-swedencentral.tfplan) was applied using the existing Azure CLI authentication for Sweden Central, prefix `academo`, and signed-in User as initial operator: **23 added, 0 changed, 0 destroyed**. The private [deployment results](../.local/azure-discovery/deployment-results.md) record exact targets, verification, plan hash and the Storage policy deviation. This plan is already consumed; do not reapply it. The preparation/apply sequence here is for new deployments. These local artifacts are not distributed with the repository; new customers must supply their own values. Do not plan/apply the all-zero example subscription.

5. Inspect that exact saved plan, subscription, region, names, role assignments, and expected costs. Under standing project authorization, apply it only when it contains no destructive or unrelated changes. Re-plan and inspect again if inputs/configuration change.

After plan inspection:

```bash
terraform -chdir=infrastructure/terraform apply foundation.tfplan
terraform -chdir=infrastructure/terraform output
```

## Important Sandbox Group schema limitation

The official stable ARM resource is `Microsoft.App/sandboxGroups@2026-07-01`, with a minimal empty properties object for an independent group. AzAPI 2.13.0 has **no embedded Sandbox Group schema**. Initial validation failed with `resource type Microsoft.App/sandboxGroups can't be found`.

Only this resource sets `schema_validation_enabled = false`, following the official module's need to handle the absent schema. Its body is constrained in source to the published stable contract; the other AzAPI resources retain schema validation. The approved deployment now proves Azure accepted this minimal stable body in the selected subscription: group read-back is `Succeeded`, authenticated data-plane listing works and built-in `copilot` is Ready. This does not validate rich-preview fields or runtime execution. New customers must still verify target API registration.

The foundation does **not** invent `maxSandboxCount`, `defaultTimeoutSeconds`, or egress properties in that stable contract. The official rich-preview example uses `2026-02-01-preview`. Both API versions are advertised in the selected subscription and succeeded for read-only group listing in Sweden Central. Those reads do not prove limit-field persistence or enforcement on create. Microsoft documents egress at sandbox creation and runtime; an omitted policy permits unrestricted outbound access. No persistent group-wide Terraform policy contract was verified. The application instead supplies explicit default-Deny/Full inspection per Sandbox, enforces one active run and bounded deadlines, and restricts inputs to the reviewed fixture. Genuine A/B clone, Copilot and dependency traffic succeeded with this policy. This is application-enforced isolation, not a claim of a persistent group-wide policy or hard service lifetime limit.

## Manual Copilot credential checkpoint

Follow the exact [README portal procedure](../README.md#mandatory-configure-github-copilot-pat-manually-after-terraform-creates-the-sandbox-group). Select the Terraform output group, configure GitHub Copilot with a dedicated fine-grained PAT carrying **Copilot Requests**, and confirm Configured. Never paste its value into chat, `.tfvars`, state, GitHub Actions, app settings, shell commands, or evidence. Existing sandboxes do not automatically reload a rotated token; recreate them.

No provider-credential management API is called by Terraform or the smoke harness. The manual configuration itself occurs only after the user approves cloud setup. A portal badge is not Milestone 0 proof.

## Prepare and execute the bounded smoke operation

First inspect the local plan-only output (zero Azure calls):

```bash
.venv/bin/python scripts/smoke_test_sandbox.py \
  --subscription-id '<subscription-uuid>' --tenant-id '<tenant-uuid>' \
  --resource-group '<terraform-resource-group>' \
  --sandbox-group '<terraform-sandbox-group>' --region '<region>' \
  --credential-connection-id '<existing-ready-connection-uuid>' \
  --expected-cli-version 1.0.97
```

Under project authorization, create, run and clean up one bounded temporary Copilot sandbox in that group per test attempt. Its requested size is 1 vCPU / 2 GiB; the work deadline is 400 seconds, the workflow process timeout is 210 seconds with 5-second kill grace, and cleanup gets an independent 100-second deadline. A compatible built-in CLI can be used directly. The opt-in `--pinned-cli` path downloads checksum-verified official 1.0.97 into the disposable control directory only; review the checksum and target before execution. The workflow allows one concurrent agent, up to two total attempts, and a soft limit of two AI credits. Usage limits are not a hard billing cap.

For an authorized execution, add:

```text
--execute --confirm-group /subscriptions/<subscription-uuid>/resourceGroups/<rg>/providers/Microsoft.App/sandboxGroups/<group>
--output .local/smoke-<unique-attempt>.json
```

The harness uses DefaultAzureCredential restricted to the existing Azure CLI identity, after checking that the cached active subscription/tenant match the approved target. It refuses a mismatched context. Temporarily select the approved subscription only when needed and restore the previous context in a `finally`/EXIT handler. SDK creation attaches `connections=[existing_connection_id]`; disk selection alone does not inject the credential. The deployed UAMI has created/cleaned separate A/B Sandboxes and written private Blob events.

The smoke harness:

1. Discovers `copilot` in the group's public disks and refuses a run if previous smoke-owned sandboxes exist.
2. Persists a unique ownership label before creation and records the returned sandbox ID.
3. Uploads the trusted [extension](../workflows/smoke/extension.mjs) into a new control repository within the sandbox. No target repository is cloned.
4. Invokes the registered `aca-viability-smoke` workflow. An actual `ctx.agent` call must return the generated nonce and `pong`; deterministic code verifies it and records real phase boundaries. No login or token injection by the host is performed.
5. Polls workflow files, retrieves the fresh result, CLI version, exit code and instrumented events. It rejects wrong nonce, missing events and inconsistent workflow IDs. Only logs sanitized inside the Sandbox are retrieved; raw logs remain there.
6. Deletes only the returned sandbox and exact app/nonce-label matches in `finally`, then checks their absence. Cleanup failure makes the entire smoke fail.

The SDK docs disagree on some filtered-list argument names; the harness avoids those filters and compares exact labels after an unfiltered list. Installed 0.1.0b4 signatures were inspected. A lost create response is reported as ambiguous even after matched orphans are removed; an empty list cannot establish that a delayed create will never appear.

Hard termination (`SIGKILL`), machine loss, and service delays can still leave an orphan. The private evidence records group, nonce and labels. [cleanup_orphans.py](../scripts/cleanup_orphans.py) is inert by default: supply `--evidence <record.json>` to inspect its local scope, then `--inspect --tenant-id <id> --region <region>` for a read-only inventory. After reviewing exact ownership under the standing owned-cleanup authorization, add `--delete-id <exact-id> --confirm-group <exact-arm-id>` to delete that ID and verify GET 404. The script rechecks live labels and refuses pre-existing IDs from the evidence inventory. It handles smoke records only; application-ledger recovery runs at host startup and only deletes exact matching ownership labels. Never delete the group or unrelated Sandboxes. This slice does not claim a service-enforced lifetime limit.

## Gate and next phase

Pass Milestone 0 only with a real registered Dynamic Workflow, correct result/branch evidence, confirmed cleanup, C's failed-validation/no-write branch, and separately authorized publication proof. Record actual versions and behavior in the compatibility ledger. SDK exec returns completed output; the harness prepares detached execution with file polling, but live progress through that route is not yet proven.

The real adapter and A/B/C workflow source are prepared. After their remaining gates pass, approve/push the tested app image to ACR and plan the optional Container App module using its real digest. Terraform remains the image revision owner. Entra registrations/users, GitHub OIDC trust and a durable CI state backend require reviewed configuration. Current Storage networking is verified; do not change it again. No local application host is required by the final design.

## Prepared application phase and CI/CD safeguards

The optional root `application` input defaults to null, preserving bootstrap behavior.
[Application module](../infrastructure/terraform/modules/application/) uses the existing
UAMI and registry, HTTPS ingress, min/max replicas 1, single revision and probes.
Supply the actual pushed image **digest**, real API/SPA registration IDs, authorized
user IDs, vetted repository allowlist, existing provider connection ID, personal
publication owner and exact HTTPS origin. Live execution/publication default false.
Do not enable publication before real extension credential and create/push validation.

The prepared [deployment workflow](../.github/workflows/deploy.yml) uses OIDC and
uses customer-owned `azure-plan` and `azure-apply` GitHub environments. Required reviewers are optional customer policy. The first builds and saves the plan; the second applies the inspected artifact. It applies only that artifact after checking its SHA256,
never replans during apply and never calls `az containerapp update`.
The plan artifact contains infrastructure configuration/state-derived values;
restrict repository/environment access and retain it for one day. Never add the
Copilot credential to any Terraform input/state or pipeline variable.

This workflow intentionally refuses to run without an approved **azurerm remote
backend** and migration. No backend file/state account is created by the workflow.
The existing foundation uses protected local state. Customer backend/OIDC choices,
actual repository/branch, federated identity and least-privileged build/deploy grants
remain unconfigured. A workflow file is not a verified CI/CD deployment.
Environment variables are `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`,
`AZURE_SUBSCRIPTION_ID`, `ACR_LOGIN_SERVER`, `ACR_NAME`,
`TERRAFORM_INPUTS_JSON` (non-secret root inputs) and `TERRAFORM_BACKEND_JSON`
(non-secret backend account/container/key settings). All are GitHub environment
**variables**, not credentials; no long-lived Azure client secret is used.

Drain all active runs and confirm owned-sandbox cleanup before a revision update.
Single revision/min-max 1 does not prevent old/new revision overlap during rollout;
in-process work is not durable. Do not deploy over an active demonstration.
Azure HTTPS login and UAMI Blob/Sandbox access pass. Full A/B/C publication, durable replay and clean-customer installation remain acceptance gates.

## Manual application deployment used in this project

Keep foundation inputs in private terraform.tfvars. Never remove existing Entra/application inputs on a later plan: that would propose destruction. Reject destructive plans. With the foundation deployed, discover the prospective application origin using the existing environment:

```sh
ENVIRONMENT_ID=$(terraform -chdir=infrastructure/terraform output -raw container_app_environment_id)
ENVIRONMENT_NAME=${ENVIRONMENT_ID##*/}
APP_NAME=ca-${ENVIRONMENT_NAME#cae-}
APP_DOMAIN=$(az resource show --ids "$ENVIRONMENT_ID" --query properties.defaultDomain -o tsv)
APP_ORIGIN=https://${APP_NAME}.${APP_DOMAIN}
```

Set `entra_public_origin` to that HTTPS origin in private inputs; keep application null for this step. Plan, inspect and apply the exact saved plan to create secretless registrations. Read `terraform output -json entra_client_ids`. Copy [application.auto.tfvars.example](../infrastructure/terraform/application.auto.tfvars.example) to private `deployment.auto.tfvars.json` only after converting the example HCL to JSON, or use `deployment.auto.tfvars` for its HCL form. Supply real registration IDs, operator object ID, reviewed source URL, existing connection ID and matching origin. Do not put a token in these files.

Build/push under the existing authorized Azure CLI identity (manual bootstrap alternative to OIDC):

```sh
ACR_SERVER=$(terraform -chdir=infrastructure/terraform output -raw acr_login_server)
ACR_NAME=${ACR_SERVER%%.*}
IMAGE_TAG=$(git rev-parse --short=12 HEAD)
az acr login --name "$ACR_NAME"
docker build --platform linux/amd64 -t "$ACR_SERVER/academo-app:$IMAGE_TAG" .
docker push "$ACR_SERVER/academo-app:$IMAGE_TAG"
az acr repository show --name "$ACR_NAME" --image "academo-app:$IMAGE_TAG" --query digest -o tsv
```

Set application.image to the returned `registry/academo-app@sha256:...` digest. Keep publication disabled until a same-PAT harmless push is live-verified. Plan, inspect the exact changes, apply that saved plan, then check readiness and anonymous rejection at the resulting application_url. Sign in through the browser to test authorized operations. The current instance uses one replica, trusted-fixture A/B and no local host.

For Sandbox telemetry, export the non-secret configuration for command-line smoke tests:

```sh
mkdir -p .local
terraform -chdir=infrastructure/terraform output -json sandbox_telemetry_config > .local/sandbox-telemetry.json
```

All smoke commands require `--telemetry-config .local/sandbox-telemetry.json`. The application receives the same output through Terraform. Query `AcademoSandboxLogs_CL` by exact run_id/sandbox_id; API creation success alone is not an ingestion check.

## Monthly baseline and operational limits

Budget approximately **USD20/month idle** or **USD47/month with the host continuously active**, before free allowances, discounts, tax and Sandbox/Copilot use. This is a30-day estimate for one0.5-vCPU/1-GiB Consumption replica, ACR Basic,1GB of artifacts and1GB of paid Analytics ingestion. Azure Retail Prices queried2026-10-14 in Sweden Central give vCPU idle0.000003/s, active0.000024/s, memory0.000003/GiB-s: host idle11.664 or active38.88/month. Previously verified foundation light-use estimate is8.06/month (ACR5, artifacts/operations0.07, logs2.99). Actual host utilization can change idle eligibility.

DCE/DCR/managed identity have no dedicated VM compute in this design; log ingestion/storage is usage-based. Do not infer Sandbox prices from the unrelated legacy Dynamic Sessions meter. Sandboxes, image builds, network transfer and Copilot subscriptions/AI credits are additional and must be checked against current account billing. A1GB/day LAW cap is not a hard spending ceiling or a reason to ingest that much data. No cost-alert resource has been added.

Measured genuine A/B runs finished in26–27 seconds; these are observations, not latency guarantees. One active run, bounded Sandbox CPU/memory, process deadlines, explicit outbound allowlists and exact-ID cleanup constrain use. Container restarts can interrupt work; Blob preserves artifacts, not live execution. Never call the demo a production security boundary for the shared GitHub PAT.
