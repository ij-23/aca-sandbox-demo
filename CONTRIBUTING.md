# Contributing

Read [AGENTS.md](./AGENTS.md), [README.md](./README.md) and the current
[compatibility ledger](./docs/compatibility.md) before changing integrations.
Use the README developer commands for platform tests, frontend build and the
network-isolated application container check. Keep generated JSON schemas in sync
with the Pydantic models using `scripts/export_schemas.py`.

The [fixture](./demo-repo/README.md) is deliberately vulnerable teaching code.
Do not import it, execute its tests, build it or launch it on a developer machine,
the hosting application or a CI runner. Platform pytest discovery is limited to
`backend/tests` and `scripts/tests`. Run fixture code only in a separately approved
disposable Sandbox. Static reading and dependency-lock generation are permitted.

Unit-test doubles must stay in test files. Never label their output as an Azure,
Copilot or Dynamic Workflow result. Real replay recordings must come from a
verified A/B/C run and remain explicitly labeled prerecorded.

All Terraform work must follow the installed `terraform-builder` skill. Preserve
the already-applied foundation plan; prepare a new reviewed plan for any future
infrastructure change. Obtain approval before paid resource creation, apply, RBAC
changes, credential changes or GitHub publication. Never include PATs, Azure
tokens, state, private evidence, `.env` files or credential-bearing logs in a patch.

Report the scope, local checks, real integration evidence and outstanding gates
in each change. Update [progress](./docs/progress.md) with facts and limitations.
The project's own source is distributed under the [MIT license](./LICENSE);
third-party dependencies keep their own licenses and notices.
