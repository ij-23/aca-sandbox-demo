# External actions awaiting approval

## M0-CLI97: one disposable workflow test

Prepared 2026-10-13. **Not executed.** This is a new authorization request; previous one-sandbox approvals are consumed.

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
