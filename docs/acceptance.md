# Live acceptance evidence

Updated 2026-10-14. **Not all acceptance criteria are complete.** Unit tests are not cloud evidence.

| Requirement | Actual evidence | State |
| --- | --- | --- |
| Terraform-managed static resources | Existing local state; inspected in-place publication enablement; scoped OIDC build identity; validate and6 offline tests | Deployed; separate clean-subscription install untested |
| Azure HTTPS + Entra | Browser sign-in and authenticated Start/Fix; anonymous operational requests401 | Passed |
| Built-in Copilot A/B/C | Official SDK0.1.0b4, `disk=copilot`, explicit existing connection, pinned official CLI1.0.97 in disposable control directory | Passed |
| Genuine concurrent A/B | Run ffe4af9f-f911-491b-b00c-327b3d84605f; different IDs, same c1c3d2b source, real AI and conditional checks | Passed |
| Genuine C publishing | Single Fix consent;4 tests,2 targeted regressions and localhost health passed; private repository1418760503, remote d84155b39cd758e6e22b8db51036d72eda5c9f3d | Passed |
| Failed C validation gate | Previous M0-C-FAIL actual failing pytest skips every remote write | Passed |
| Private durability |95 contiguous events,3 reports and exact diff read through deployed UAMI; private replay Blob readback | Passed |
| Workflow telemetry | Same successful run: A11, B10, C14 records in AcademoSandboxLogs_CL | Passed |
| UI observation/replay | A/B/C steps, running AI, results, diff/link and all95 prerecorded events observed | Passed; revision0000007 browser recheck pending |
| SSE recovery | History reloaded after revision change;95 events restored, automatic connection active | Partial; explicit Last-Event-ID transport drill pending |
| Sandbox cleanup | Exact A/B/C/probe GET404; only pre-existing protected Stopped Sandbox remains | Passed |
| Operational failure paths | Real command timeout124 and egress allow200/deny403; local cancellation/recovery regressions | Passed at actual A/B step boundaries: cancellation21.58s, interruption23.784s, timestamps and exact404; browser cancellation/HTTP-process crash not exercised |
| OIDC release + local deployment | Build-only UAMI/AcrPush and exact immutable subject; no remote state or state artifacts | Passed: OIDC run38556062751, image-only local-state apply, Healthy revision0000007; final plan No changes |
| Customer/demo readiness | Canonical docs, genuine replay/provenance and technical walkthrough | Separate clean install and final15-minute rehearsal pending |

The original source repository and protected Sandbox remain unchanged. Existing fixed destination must never be overwritten. No credential value is captured in these records.

## Remaining work and external dependencies

This is the current checklist, consolidated from the retired implementation plan and
approval notes. Historical results remain in [progress](./progress.md) and
[compatibility](./compatibility.md); requirements remain in [AGENTS.md](../AGENTS.md).

- [ ] Exercise authenticated SSE with an explicit Last-Event-ID cursor and browser cancellation on the deployed revision; runtime cancellation/recovery has already passed.
- [ ] Complete the final 1080p dashboard review, screenshots and timed 15-minute rehearsal with the [demo script](./demo-script.md) and genuine replay fallback. These browser checks need an available dashboard window.
- [ ] Verify customer bootstrap and deployment in a separate customer-provided empty subscription/tenant. Do not recreate the existing deployment as a substitute.

PAT permissions and Terraform state decisions are resolved: same-PAT private publication
passed, and the existing LOCAL state/lineage must be retained. The OIDC workflow publishes
an image and digest; the state-holding machine applies the inspected Terraform plan.
Fully automated Actions apply would require a separately configured trusted persistent runner.

Project-scoped operations use the [standing authorization](../AGENTS.md#project-execution-authorization--2026-10-14).
The product's single Fix confirmation remains required. Credential rotation, repository
deletion/overwrite, static infrastructure destruction and unrelated changes are outside that scope.
