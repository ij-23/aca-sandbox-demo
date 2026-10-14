# Public repository expansion: credential setup and current gate

Status: implementation in progress on `feature/public-repository-support`. The
deployed application still runs only its trusted fixture. The new metadata UI/API
and policy/source helpers are on this branch, not deployed public execution.

## Prepared Azure groups

Both new groups are in `rg-academo-a3dcd3b3`, Sweden Central, in the existing
subscription. Terraform owns them and their group-scoped Data Owner assignments
for the application identity and existing presenter. Local state is preserved.

| Group | Purpose | Credential policy |
| --- | --- | --- |
| `sbg-academo-a3dcd3b3` | Existing trusted-fixture A/B/C | Existing demo credential remains unchanged |
| `sbg-academo-a3dcd3b3-workers` | Source acquisition and future unknown-code workers | No identities, provider credentials, connections or direct telemetry identity |
| `sbg-academo-a3dcd3b3-analysis` | Future trusted Copilot coordinators | Copilot-only provider credential; ingestion-only telemetry identity; no target code execution |

The new groups do **not** enable public execution automatically. Never configure
the Copilot or publisher token in the worker group. Do not disable Terraform
foundation flags as a feature rollback: that would propose deletion. Feature
activation belongs to the application, after live gates pass.

## Manual Copilot-only credential

The [adopted instructions](../AGENTS.md#public-repository-expansion-approved--2026-10-14)
leave credential setup manual. A new credential is needed so the existing demo's
GitHub write privileges do not follow source-analysis coordinators.

1. In the dedicated personal GitHub account with a Copilot seat, open
   [fine-grained token settings](https://github.com/settings/personal-access-tokens/new).
2. Use that personal account as resource owner, a short expiration, and
   **Account permissions → Copilot Requests** at the access level shown by GitHub.
   Do not grant repository creation, Contents write, Administration write or
   other publishing permissions. This credential serves Copilot inference only.
3. Open [ACA Sandboxes](https://sandboxes.azure.com), choose
   **Sandbox Groups → sbg-academo-a3dcd3b3-analysis → Security → Credentials →
   GitHub Copilot → Set Token**, enter the new token securely, and save.
4. Confirm the credential is configured. Report completion only; do not paste
   its value, prefix, length, hash, screenshot or any token material into chat.
5. The implementation can then discover the non-secret connection ID and verify
   actual authentication in a fresh owned coordinator. A Configured badge alone
   does not pass that gate.

Leave the original group's credential unchanged. Neither Terraform nor the app
will copy, create, rotate or expose a PAT.

## Separate publisher identity: customer value required

The intended destination owner remains `ij-23`. The publisher must use a separate
identity, keep its credentials outside all analysis/execution Sandboxes, and
accept only the exact user-approved destination and host-verified artifact.

If a GitHub App is already installed for that owner, provide **only its App ID and
installation ID**. Otherwise, confirm that a new dedicated App is needed before
choosing its installation and secure private-key storage. No private key or token
belongs in chat, Terraform state, the app image, a workflow input or source control.

The [official create-repository endpoint](https://docs.github.com/en/rest/repos/repos#create-a-repository-for-the-authenticated-user)
currently lists GitHub App user tokens, installation tokens and fine-grained PATs.
Its documented creation permission alternatives are Administration (write) or
Repository creation (write); Contents (write) is also needed for publication.
This is not proof that a particular installation can create a private repository
under this owner and access the newly created destination. Verify both with a
harmless creation/push test before enabling publishing. Installation selection,
future-repository coverage and the exact permission set remain live gates.

Do not reuse the current broad demo PAT as a shortcut. GitHub repository deletion,
overwriting destinations and modifications to original repositories remain excluded.

## Remaining implementation after credentials

- Validate the narrow coordinator credential and trusted tool/extension boundary.
- Integrate general A/B/C workflows with durable group-aware worker ownership,
  retention, cancellation/restart handling and dashboard child-worker events.
- Verify Python/Node adapters and required checks; static manifest detection does
  not establish build support. Add additional ecosystems independently.
- Implement the separate publisher against the selected identity/store; bind
  validation to the exact artifact and the single Fix consent. Preserve the
  editable private destination and `main` branch.
- Verify host-mediated worker telemetry, real Azure E2E, broader corpus,
  hostile-input cases, new replay, rehearsal and customer installation.

Progress and live evidence: [progress](./progress.md),
[compatibility](./compatibility.md), [implementation plan](./public-repository-plan.md).
