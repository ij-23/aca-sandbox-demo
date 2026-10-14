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
| UI observation/replay | A/B/C steps, running AI, results, diff/link and all95 prerecorded events observed | Passed; final release recheck pending |
| SSE recovery | History reloaded after revision change;95 events restored, automatic connection active | Partial; explicit Last-Event-ID transport drill pending |
| Sandbox cleanup | Exact A/B/C/probe GET404; only pre-existing protected Stopped Sandbox remains | Passed |
| Operational failure paths | Real command timeout124 and egress allow200/deny403; local cancellation/recovery regressions | Real deployed-runtime cancellation/interruption recovery passed; HTTP-process crash/browser cancellation not exercised |
| OIDC release + local deployment | Build-only UAMI/AcrPush and exact immutable subject; no remote state or state artifacts | Passed: OIDC run38553776354, image-only local-state apply, Healthy revision0000006 and readiness |
| Customer/demo readiness | Canonical docs, genuine replay/provenance and technical walkthrough | Separate clean install and final15-minute rehearsal pending |

The original source repository and protected Sandbox remain unchanged. Existing fixed destination must never be overwritten. No credential value is captured in these records.
