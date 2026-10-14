# Security boundaries and verification

This is a **trusted-fixture demonstration**, not a service for arbitrary hostile repositories. A scan is not proof of safety.

## Identity and authentication

The browser uses MSAL authorization-code flow with PKCE. The API independently verifies Entra RS256 signatures against the configured tenant's JWKS, issuer, API audience, expiry/not-before, tenant, `access_as_user` delegated scope and explicit user object-ID allowlist. It ignores `X-MS-CLIENT-PRINCIPAL` headers. Run reads, event streams, cleanup and remediation enforce ownership. Public endpoints expose only health and non-secret application configuration. An authenticated browser's token is never sent to a sandbox.

Entra setup requires customer-owned SPA/API registrations, `requestedAccessTokenVersion=2` for the API, the delegated scope, exact HTTPS SPA redirect URI, and consent where tenant policy requires it. No client secret is needed for PKCE. These registrations and Azure sign-in are **not deployed or verified yet**. API token checks have local tests using explicit test signing keys. Token verification is not proof of immediate account revocation: signed access tokens can remain valid until expiry. SSE connections end after at most one minute so each reconnect revalidates the access token.

References: [Microsoft auth-code/PKCE flow](https://learn.microsoft.com/entra/identity-platform/v2-oauth2-auth-code-flow), [token versions](https://learn.microsoft.com/entra/identity-platform/access-tokens#token-formats).

## Execution and credentials

- The app's UAMI accesses Azure Blob and Sandbox Group APIs only. Never attach it to execution sandboxes.
- Copilot authentication uses the manually configured Sandbox Group connection. The host holds its connection ID, never its PAT.
- The MicroVM isolates the execution environment from the host. It **does not protect a PAT from other code in the same sandbox**. The demo publication credential has broad current/future repository write access; use a dedicated disposable account and short expiry.
- Evaluate only explicitly allowlisted public GitHub fixture URLs. Resolve one immutable SHA for A/B/C; reject URL credentials, query/fragment, extra path segments and alternate hosts. Never execute fixture code locally, in CI, or in the app container.
- Trust only the project's control extension. Disable submitted instructions, extensions and MCP configuration; restrict agent tool permissions. An ordinary Copilot prompt is not a Dynamic Workflow.
- The M0 CLI compatibility test is separately approval-gated. A successful ordinary Copilot prompt is not proof of workflow eligibility or GitHub publication permission.

## Reports and events

Strict report contracts reject extra fields. Published results require passed validation and a GitHub destination URL/commit SHA. Redact credentials inside the sandbox before transfer and again before storage/streaming. The implemented host strips secret-bearing keys and known token formats; this is defense in depth, not proof that arbitrary source text has no secrets. Do not use real secret fixtures. Event contents are escaped by React; no raw HTML rendering exists.

The Blob adapter uses managed identity and private containers with no shared keys. It persists events before they are delivered, does not retry ambiguous appends, and invalidates cached history on append failure. The inherited Storage policy currently blocks actual connectivity; no durable-write success is claimed. Loss of persistence must fail the run, not fall back to local storage.

## Approval and publication

One Fix Vulnerability confirmation binds the source SHA, finding, configured personal owner and `{repo}-fixed` destination. C must implement deterministic validation, name-collision rejection, private creation, sanitized fresh-history push and remote-SHA verification. No source repository writes, no backend publisher and no second Publish button. The live C workflow and same-token publication boundary remain gated by M0. Partial destinations must be reported, never silently overwritten or deleted. Test repository creation/push needs separate approval; deletion needs further approval.

## Availability and outstanding controls

One app process/replica admits one run. Blob durability is not durable execution. Startup marks interrupted work and invokes owned-only cleanup through the executor contract; the live adapter is pending the verified workflow gate. Ambiguous creation and deletion need exact ownership/ID reconciliation. Never delete unrelated sandboxes.

Customer-policy-compatible Blob networking, Entra deployment, persistent group limits/egress, live transport, UAMI access and sandbox timeout/restart behavior remain unverified. No public sandbox ingress is planned. The app's public ingress must serve authenticated operations only. Production adoption requires credential separation, stronger code/egress controls, destination authorization and independent review.
