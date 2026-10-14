# Public GitHub repository support — implementation plan

Updated: 2026-10-14. **Proposed capability; not implemented or security-verified.**

## Outcome

Accept public GitHub repositories without requiring per-repository allowlisting. Preserve Entra authentication, genuine Copilot Dynamic Workflows A/B/C, observable results, one Fix confirmation, private publication and owned-only cleanup. Remain a customer-deployed Azure application, not a multi-tenant SaaS.

“Any public repository” means repository-independent admission and bounded source analysis. It does not guarantee complete analysis, successful builds, tests or fixes for every language, size or dependency environment. Show coverage and explicit unsupported, blocked and partial outcomes. Public visibility does not establish an open-source license; analysis eligibility and redistribution permission are separate checks.

Deliver in stages: **public source analysis → Python and Node.js/TypeScript validation → isolated remediation/publication → additional languages**. Keep unsupported projects eligible for bounded source analysis. No promise of universal build or automatic fix support.

## Confirmed implementation gaps

| Area | Current behavior | Required change |
| --- | --- | --- |
| Admission | [security.py](../backend/app/security.py) checks a URL allowlist; deployment allows only `ij-23/academo-fastapi-fixture` | Public GitHub identity validation plus separate capability policy |
| Source | [operations.py](../workflows/shared/operations.py) requires `app.py`, `test_app.py`, `requirements.txt`, with 100-file and 200 KB/file limits | Bounded general inventory, component detection and safe transport |
| A | [Security extension](../workflows/security-review/extension.mjs) is fixture-oriented; scanners are skipped and helper findings have fixed severity | General review, actual supported scans, justified severity and coverage |
| B | [Build extension](../workflows/build-validation/extension.mjs) assumes fixture pytest and health checks | Versioned language/framework adapters and applicable-check policy |
| C | [Remediation extension](../workflows/remediation/extension.mjs) patches only `app.py` | Bounded multi-file patches and independent project-specific checks |
| Reports | [contracts.py](../backend/app/contracts.py) requires fixture-specific pytest/health gates | Versioned schemas and host-controlled required checks by adapter |
| Credentials | [sandbox.py](../backend/app/sandbox.py) binds the provider connection to A/B/C; C uses the same PAT for publishing | Separate trusted coordinators, credential-free execution and publishing identity |

Existing successful demo evidence in [acceptance.md](./acceptance.md) remains a regression baseline, not proof of these new capabilities. Preserve the original fixture, existing fixed repository, genuine replay and protected Sandbox.

## Proposed execution and credential boundaries

Keep three **logical** A/B/C Dynamic Workflows. Permit additional disposable worker Sandboxes; three physical VMs are not sufficient for the proposed separation of credentials and arbitrary execution.

| Boundary | Responsibility | Must not contain or perform |
| --- | --- | --- |
| React + deterministic FastAPI | Entra authorization, metadata resolution, policy, scheduling, artifact storage and SSE | Repository execution or LLM operations |
| Trusted Copilot coordinator Sandboxes A/B/C | Built-in Copilot disk, trusted extensions, narrow Copilot credential, bounded source/log data as agent input | Target build/tests, hooks, extensions, plugins or publishing credentials |
| Credential-free disposable workers | Source acquisition, static tools, dependency install, build/tests and localhost checks as applicable | Provider connection, Copilot PAT, GitHub write token, app UAMI or general Blob credentials |
| Separate trusted publisher | Authorize exact artifact/destination, create private repo, push and verify remote SHA | Repository execution, hooks/config, arbitrary destinations or general command/API proxying |

FastAPI relays narrowly typed work requests and results between workflow coordinators and workers. Coordinators receive no app UAMI or general Sandbox-management credential. Prototype this delegation using supported SDK/file APIs; existing file polling proves progress retrieval, not native exec streaming or a working delegation protocol.

Source acquisition and static parsing also handle attacker-controlled data: perform them in credential-free workers and pass bounded regular-file text to Copilot as data. Disable target instructions, extensions, MCP configuration and executable Git configuration in coordinators. Prompt-injection controls and narrow agent tool permissions remain necessary for source-only review.

Clearing environment variables, a venv, another directory or another process in the same privileged Sandbox is **not** a credential isolation boundary. Verify workers cannot reach injected provider credentials, instance identities, trusted files or trusted APIs. Inspect telemetry identity exposure too; use host-mediated ingestion if direct worker telemetry exposes reusable authorization. Worker logs/results are untrusted data and cannot create trusted lifecycle events or publication authority.

For publication, prefer a separate GitHub App installation identity with short-lived destination-scoped access **if official API and installation behavior supports private repository creation and access to the new repository for the selected owner**. Do not assume it can use the current PAT's `POST /user/repos` endpoint. If unsupported, select a dedicated publisher-only credential and secure secret store before implementation. Credential setup/changes remain manual; never reuse the broad demo PAT for arbitrary repository execution or put secrets in Terraform state, build inputs or source.

### Required instruction changes when implementation starts

The new design conflicts with current fixture-only scope, same-PAT publication inside C, the prohibition on a separate publisher, and the single-service architecture. Explicitly update [AGENTS.md](../AGENTS.md), [README.md](../README.md), [architecture.md](./architecture.md) and [security.md](./security.md) when adopting the design. C remains a genuine Dynamic Workflow controlling validation and the publisher request; the publisher owns GitHub credentials and writes. Preserve one Fix confirmation and no second Publish button.

This planning document does not silently supersede current execution rules or enable public execution.

## P0 — Verify isolation and API feasibility

**Dependency:** blocks enabling unknown repository execution and publication.

- Verify current official ACA SDK/API and Copilot extension contracts for credential-free workers, narrow coordinator credentials, transfer, cancellation, network isolation and workflow-to-worker delegation.
- Prove genuine A/B/C workflows can request bounded work in separate workers and expose real step/branch results. Record concrete supported APIs rather than inventing commands.
- Use project-authored adversarial fixtures and synthetic canaries to test environment/process/filesystem/identity exposure, repository config auto-loading, cross-Sandbox access and controlled egress. Never inspect or print real secret contents.
- Verify worker output cannot forge host event IDs, ownership, authorization, trusted execution envelopes or publisher requests. Capture command exit status through trusted SDK calls; validate and bound report data.
- Verify publisher identity/owner permissions, future repository access and secret-storage design against official GitHub documentation and a harmless scoped live create/push test.
- Record observed APIs, versions, identity exposure, role scopes and limits in [compatibility.md](./compatibility.md).

**Exit gate:** live positive and negative evidence establishes the selected isolation/delegation contracts. If built-in ACA Sandboxes cannot meet a necessary boundary, keep the affected feature disabled and document the required architectural change. Do not remove the existing fixture safeguard to bypass this gate.

## P1 — Public intake and capability discovery

- Add explicit policy modes: current `trusted_fixture`, then `public_analysis`, and later `public_execution`. An empty allowlist must never implicitly authorize unrestricted execution.
- Canonicalize GitHub HTTPS owner/repository URLs, verify public identity and repository ID, and pin one immutable SHA. Reject embedded credentials, unsafe hosts/protocols/redirects. Handle renamed, deleted, private and empty repos, rate limits and outages explicitly.
- Acquire source without hooks/filters. Disable submodules and LFS initially and report omissions. Reject unsafe archive paths, special files and escaping symlinks; bound download size, expansion, files, logs and processing time.
- Detect languages, manifests, lockfiles, runtime versions, component roots and licenses without executing repository configuration. Separate public-but-unlicensed code from open-source licensing; publishing requires an explicit supported license/attribution policy.
- Persist a versioned capability report with supported checks, tool versions, components and omissions. Proposed initial source limits: 100 MiB expanded, 10,000 files, 1 MiB/text file; tune from measurements and disclose truncation. These are application proposals, not claimed Azure limits.

**Exit gate:** diverse public repositories pass admission/discovery without individual allowlisting; unsupported/oversized cases receive truthful bounded results. No repository execution occurs on the host, developer machine or CI.

## P2 — Generalize Dynamic Workflow A; release public analysis

- Genuine sequence: `acquire → inventory → supported static scans → agent.review → verify evidence → review.json` with actual branches and step instrumentation.
- Run pinned scanners in credential-free workers; never load submitted scanner plugins or executable configuration in a coordinator.
- Chunk source within explicit AI budgets and report inspected files/components, scanner coverage and skipped checks. Do not imply full-repository review when only part was inspected.
- Replace fixed severity with evidence-supported severity/confidence. Distinguish exact-source correspondence from proven exploitability. Retain paths, line ranges, finding IDs and verification limitations.
- Enable public source analysis only after relevant P0 gates pass; keep unsupported execution/remediation controls visibly disabled.

**Exit gate:** actual Copilot review and supported scans on multiple unrelated repositories/languages, source-grounded findings, honest coverage and passing malicious-config/prompt-injection tests.

## P3 — Generalize Dynamic Workflow B; Python and Node execution

- Define a trusted adapter contract: detection, toolchain version, dependency resolution, install/build/test commands, result parsing, optional localhost checks, timeouts and required checks.
- First adapters: common Python requirements/pyproject projects and Node.js/TypeScript lockfile-based projects. Libraries and CLI tools do not require HTTP health checks. Missing private dependencies/services/toolchains are explicit blockers, not fabricated test failures.
- Verify toolchains in disposable workers, using pinned official artifacts when installation is required. Do not execute repository Dockerfiles or silently fall back to privileged nested containers. Do not rebuild the built-in coordinator image.
- B coordinates `discover → worker provision → install → build → tests → conditional runtime checks → AI result analysis → build.json`. A/B use the same SHA and run concurrently within global Sandbox/CPU/time budgets.
- Run all repository scripts, including dependency install hooks, only in credential-free workers. Enforce registry/network policies, private/metadata address denial, process/memory/disk/output limits and cancellation. Verify enforcement rather than assuming host allowlists cover every network path.

**Exit gate:** real successful/failing Python and Node builds, correct counts/exit codes/skips, progress while running, no credential exposure, and exact-ID cleanup for timeout/cancel/restart paths.

## P4 — Generalize Dynamic Workflow C and isolate publishing

- Bind the single Fix confirmation to user, SHA, finding/component, required-check policy, destination and attempt. Reject stale, duplicate and cross-owner requests.
- Copilot proposes a bounded multi-file patch as data. Validate paths, sizes and allowed changes; apply only in credential-free workers. Preserve baseline tests, record new regression tests separately, and reject weakened checks or unexpected dependency/policy changes.
- Run baseline and patched code using the same adapter plus a trusted targeted regression check where available. If meaningful independent validation is unavailable, return a proposed diff marked unvalidated and block automatic publication.
- Bind trusted validation receipts to exact source SHA, patched artifact digest, policy/tool versions and attempt. A repository or AI output cannot select required checks. Test exit codes do not prove code is nonmalicious.
- Genuine sequence: `agent.fix → apply.patch → isolated validation → publication.gate → publisher request → verify_remote → remediation.json`. Failed, missing, skipped-required or timed-out checks cause zero remote writes.
- Publisher accepts only host-authorized receipts/artifacts, checks digest and safely materializes regular files. It performs no repository execution, uses trusted Git config with hooks/filters disabled, excludes secrets/runtime artifacts, preserves license/attribution and creates fresh history. Disable copied automation such as GitHub Actions by explicit policy and disclose exclusions.
- Keep private `{repo}-fixed` naming initially; collisions fail without overwrite/deletion. Journal create/push intent and reconcile ambiguous responses before retrying. Verify repository ID, owner, privacy and remote SHA; report partial publication truthfully.

**Exit gate:** real multi-file Python and Node remediation/private publication succeeds; original repositories are unchanged. Failed validation, forged receipts, changed artifact digests, missing license clearance, expired consent, collisions and publication failures cannot cause unauthorized writes or false success.

## P5 — Dashboard, durability and deployment integration

- Version schemas with component coverage and explicit unsupported/blocked/partial/not-applicable outcomes. Do not turn skipped checks into passes. Keep old genuine replay readable through schema-version handling.
- Replace fixture-only UI with public input and support/limit information. Show A/B/C plus child-worker lifecycles, actual AI/deterministic steps, decisions, validation, diff, publication status and verified URL/SHA.
- Preserve owner-authorized private Blob reports/events, ordered IDs, SSE heartbeat/resume and genuine prerecorded replay. Distinguish trusted control events from escaped untrusted terminal text.
- Correlate telemetry across coordinator/worker/run/step. Verify ingestion under the new identity boundaries; report untrusted log origin accurately.
- Keep one active run initially, enforce per-user request/run budgets, persist resource ownership intents and reconcile on timeout/cancel/restart. Blob persistence does not provide resumed job execution.
- Scope any publisher service/identity/secret-store additions only after P0. Infrastructure work uses `terraform-builder`, inspected saved plans, existing LOCAL state/lineage and Terraform-owned image revisions. No remote-state migration or speculative provisioning.

**Exit gate:** authenticated Azure dashboard demonstrates new paths, reconnect retrieves missed events, private persistence and real telemetry work, all owned disposable resources are confirmed deleted.

## P6 — Broader ecosystems and release validation

- Add .NET, Java, Go and Rust individually, verifying actual runtimes and registry egress. Add bounded monorepo component selection/per-component results. Unknown toolchains retain analysis-only support.
- Use a SHA-pinned real corpus: at least two unrelated public projects per initial ecosystem (Python and Node), plus library, web app, monorepo, unsupported language, missing tests, dependency failure and large/binary cases. Use appropriately licensed projects for publication tests.
- Run project-authored hostile/config-injection fixtures only in credential-free workers: path/symlink escapes, metadata access, output/process floods, result forgery and attempted publisher access. No need to fetch known malware.
- Execute Azure E2E successes/failures: A/B concurrency; C pass/private push and fail/no writes; collision, rate limit, auth expiry, SSE disconnect/resume, cancellation and process interruption. Record actual tool versions, timings, Sandbox counts, cleanup, telemetry and costs.
- Finish existing transport/demo/customer-install acceptance gates; document support and limitations, capture genuine new replay and rehearse 15 minutes. Large projects may exceed presentation timing within disclosed run limits.

**Exit gate:** every enabled capability has live evidence and security review; unsupported paths remain explicit. Do not mark universal build/remediation support complete.

## Implementation map and sequence

| Workstream | Existing areas | Planned additions |
| --- | --- | --- |
| Intake/capabilities | [security.py](../backend/app/security.py), [config.py](../backend/app/config.py), [contracts.py](../backend/app/contracts.py) | Inventory and adapter registry |
| Isolation | [sandbox.py](../backend/app/sandbox.py), [orchestrator.py](../backend/app/orchestrator.py), [telemetry adapter](../backend/app/sandbox_telemetry.py) | Coordinator/worker policy, delegated-work protocol, artifact receipts |
| Workflows | [workflows](../workflows/), [shared operations](../workflows/shared/operations.py) | General scanners/build adapters and multi-file patch validation |
| Publishing | [C extension](../workflows/remediation/extension.mjs), [contracts](../backend/app/contracts.py) | Separate publisher and narrowly scoped identity |
| UX/storage | [frontend](../frontend/), [store.py](../backend/app/store.py), [schemas](../workflows/schemas/) | Capabilities, child-worker events, schema migration |
| Verification | [tests](../backend/tests/), [scripts](../scripts/), [deployment](./deployment.md) | Real repository corpus, isolation tests, release evidence |

Dependency order: **P0 → P1 → P2 → P3 → P4 → P6**. P5 schema/UI work progresses alongside P1–P4. Intake validation, adapter contracts, capability UI and unit tests can proceed while P0 is unresolved; public execution/publication cannot.

Resolve in P0: supported worker isolation and telemetry identity exposure; actual Copilot delegation contract; publisher owner type/identity setup; license policy; and measured quotas/network enforcement. Do not invent service guarantees or firm delivery estimates before the proof. Additional workers/publisher increase cost: measure CPU/memory seconds, AI usage, logs/storage and publisher baseline before setting budgets.

Roll out behind explicit capability flags: existing demo → public analysis → Python/Node execution → isolated publication → additional adapters. Roll back by disabling the new mode, draining work and cleaning owned workers/coordinators; retain reports and existing repositories. Preserve local state and the consumed foundation plan throughout.

## Acceptance checklist

- [ ] Public admission works without individual repository allowlisting in the new mode; authentication, ownership and quotas remain enforced.
- [ ] Coverage, unsupported projects, size limits and skipped checks are explicit.
- [ ] Repository code never executes with Copilot/publishing credentials or app identity, or on host/local/CI machines.
- [ ] Three genuine Dynamic Workflows and delegated worker steps/branches are observable.
- [ ] Python and Node validation/remediation pass the live corpus; extra adapters claim only verified support.
- [ ] Separate publishing identity, exact-artifact validation and single bound Fix consent work; failed validation makes zero writes.
- [ ] Private destination URL/SHA are verified; licenses preserved, originals unchanged and collisions never overwritten.
- [ ] Real SSE reconnect, private persistence, genuine replay and correlated telemetry pass without secret disclosure.
- [ ] Timeout/cancel/restart paths clean all owned coordinators/workers and preserve protected resources.
- [ ] Customer deployment, costs and security limitations are documented; LOCAL Terraform state is preserved.
- [ ] Genuine release replay, timed demo and clean-customer deployment are verified; existing open acceptance work remains visible.

This is documentation-only planning. No deployed access policy, application code, credential, cloud resource or Terraform state changes are part of this task.
