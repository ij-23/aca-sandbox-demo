# External dependencies and standing authorization

Updated 2026-10-14. Project operations remain authorized under [AGENTS.md](../AGENTS.md).

- PAT permissions corrected by the user: same-PAT push and successful C private publication now pass. No token change is needed.
- Terraform state decision resolved: existing LOCAL state only; no migration/reset/recreation. Hosted Actions publishes OIDC-authenticated image releases. Local Terraform applies the inspected digest. Fully automated Actions apply would require a trusted persistent runner; no runner is installed.
- Edge automation restored. Authenticated A/B/C and genuine replay are being verified.
- A clean-customer subscription installation still needs a separate customer-provided subscription/scope. Do not simulate this by recreating the current deployment.

Protect unrelated resources, existing source repositories and the pre-existing stopped Sandbox. No static destruction, repository deletion/overwrite, or credential rotation. The single product Fix confirmation remains mandatory; the agent may exercise it.
