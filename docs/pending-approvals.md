# External actions awaiting approval

## M0-CLI97: one disposable workflow test

Prepared 2026-10-13. **Explicitly approved and successfully executed 2026-10-14; authorization consumed.** This authorization covers exactly the operation below. Previous one-sandbox approvals remain consumed.

- Subscription `be9948d2-4149-4be2-a040-ef1a6dc1c866`, tenant `6cdedf3f-fe2c-48bd-894d-1c8e5554c0be`, Sweden Central.
- Existing group `rg-academo-a3dcd3b3/sbg-academo-a3dcd3b3`.
- Create **one** 1-vCPU / 2-GiB disposable sandbox from public built-in `copilot`, attach existing provider connection `4e86451e-7ec1-434e-8b1b-cbfc4088960d`, expose no ports.
- Download official standalone Copilot **1.0.97** into that sandbox's unique `/tmp/aca-smoke-<nonce>/cli/` directory. Do not overwrite the built-in executable or change any other sandbox/image. Disable automatic updates. The official Linux x64 archive was downloaded locally for checksum/layout inspection only; SHA-256 `07f3f63cb361e911268e8a4b010e06eeced8d4f2d898d13a8180273e34aeff3f`, sole archive member `copilot`.
- Upload the reviewed [smoke extension](../workflows/smoke/extension.mjs) and run `copilot --experimental workflow run aca-viability-smoke` with a nonce, deterministic addition, real `ctx.agent` call, actual-result branch and JSONL file polling. No external repository clone, creation or push. No interactive login or credential change.
- Bound all calls: 60s artifact download, 210s workflow timeout/5s kill grace, 400s work budget, separate 100s cleanup budget. Delete in `finally`, verify exact-ID GET 404. Protect all pre-existing IDs, including `5bf17eda-250b-4c90-9cd6-bd44a5610851`.
- Preserve Terraform configuration, state and saved plan. Estimated scope: one short-lived sandbox plus Copilot usage; no always-running infrastructure.

After approval, select the verified cached Azure CLI subscription temporarily and restore it in `finally`, then invoke:

```sh
.venv/bin/python scripts/smoke_test_sandbox.py \
  --subscription-id be9948d2-4149-4be2-a040-ef1a6dc1c866 \
  --tenant-id 6cdedf3f-fe2c-48bd-894d-1c8e5554c0be \
  --resource-group rg-academo-a3dcd3b3 \
  --sandbox-group sbg-academo-a3dcd3b3 --region swedencentral \
  --credential-connection-id 4e86451e-7ec1-434e-8b1b-cbfc4088960d \
  --expected-cli-version 1.0.97 --pinned-cli \
  --confirm-group /subscriptions/be9948d2-4149-4be2-a040-ef1a6dc1c866/resourceGroups/rg-academo-a3dcd3b3/providers/Microsoft.App/sandboxGroups/sbg-academo-a3dcd3b3 \
  --output .local/m0-cli97-evidence.json --execute
```

This approval does not authorize GitHub writes, other sandboxes or infrastructure changes. A failed capability/authentication run remains a failed gate, with no prompt substitution.

## Later actions not yet ready for approval

- C publication test: requires the dedicated personal GitHub owner and exact private test repository name/content, then separate create/push approval. Deletion requires further approval.
- Azure application deployment: requires a reviewed saved plan, policy-compliant Blob connectivity, Entra application registration/authorized users, real app image digest and CI/CD state/OIDC decisions. No apply is authorized here.

## M0-C-FAIL — prepared, NOT executed

Exactly one disposable built-in `copilot` Sandbox in the same Sweden Central group,
1 vCPU/2 GiB, no ports, existing connection `4e86451e-7ec1-434e-8b1b-cbfc4088960d`.
Use the same checksum-pinned official CLI 1.0.97 in a temporary directory. Upload
only this project's trusted fixture and C extension. Create a local fixture commit
inside the Sandbox, append one deliberately failing pytest case, and execute the
genuine remediation Dynamic Workflow. Confirm Copilot patch, actual pytest exit 1,
conditional publication skip, structured evidence and finally exact-ID deletion.
No repository cloning, GitHub repository API requests, remote creation/push, PAT changes,
pre-existing Sandbox changes or static Azure mutations. Work budget 850 seconds,
CLI bound 720 seconds, independent cleanup 100 seconds; no create retry.

```sh
.venv/bin/python scripts/smoke_test_remediation.py \
  --subscription-id be9948d2-4149-4be2-a040-ef1a6dc1c866 \
  --tenant-id 6cdedf3f-fe2c-48bd-894d-1c8e5554c0be \
  --resource-group rg-academo-a3dcd3b3 \
  --sandbox-group sbg-academo-a3dcd3b3 --region swedencentral \
  --credential-connection-id 4e86451e-7ec1-434e-8b1b-cbfc4088960d \
  --expected-cli-version 1.0.97 --pinned-cli \
  --confirm-group /subscriptions/be9948d2-4149-4be2-a040-ef1a6dc1c866/resourceGroups/rg-academo-a3dcd3b3/providers/Microsoft.App/sandboxGroups/sbg-academo-a3dcd3b3 \
  --output .local/m0-c-fail-evidence.json --execute
```

This proves only the failed-validation branch. Passing publication, extension
credential permission, real public pinned clones and A/B concurrency still require
separate tests and exact approved GitHub destination. Sandbox costs/Copilot usage
are limited to this attempt; no always-running resources are provisioned.


## Customer inputs pending for deployment preparation

| Input | Proposed path / reason needed |
| --- | --- |
| Dedicated personal GitHub owner | Binds C publication authorization and verifies the injected PAT owner; never provide the token |
| Vetted public fixture URL | Pins the real A/B/C source; alternatively approve publication of the bundled fixture under an exact destination |
| Project GitHub repository and branch | Binds Actions checkout and OIDC trust subjects |
| Entra API/SPA registrations | Prepare new single-tenant registrations authorizing the current signed-in user, or provide existing client IDs; registration changes need a concrete reviewed plan |
| Terraform state | Explicitly choose Azure Blob backend preparation/migration for Actions, or retain the current local-state/manual path; no migration has occurred |

These inputs prepare reviewable operations; they do not authorize apply, role grants,
repository writes or extra Sandboxes. The already-approved M0-CLI97 allocation is
consumed. Per [AGENTS.md section 10](../AGENTS.md#10-working-style-and-environment),
“Before terraform apply, role grants, provisioning paid resources, changing existing
credentials or publishing repositories, present the exact plan and obtain approval.”
