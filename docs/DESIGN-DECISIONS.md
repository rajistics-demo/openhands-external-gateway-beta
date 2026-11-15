# Design decisions: personal keys through an external gateway

Recorded November 14, 2026. **Status: implemented staging beta; production adoption requires the gates in [ENGINEERING-HANDOFF.md](ENGINEERING-HANDOFF.md).** This record preserves the reasoning behind the delivered design. It is not a claim that every alternative was fully implemented or tested.

## 1. Problem and intended outcome

An organization already uses its own LiteLLM for individual developer budgets, model permissions and aggregate usage across AI products. OpenHands must send each developer's inference under the correct existing virtual key, without introducing a separate budget authority or exposing that customer credential to agent-controlled execution.

The developer should sign in through normal authentication, choose an administrator-provided model and use OpenHands. The gateway should enforce that person's access and budget. Rotating a credential must preserve the person's native identity and customer budget owner. Optional adoption and a reviewed way back to the existing inference configuration are requirements.

The broader direction is gateway flexibility: an organization may use its own gateway without running the bundled OpenHands LiteLLM. This beta validates LiteLLM first. It does not establish a platform-wide removal of LiteLLM or prove compatibility with every gateway.

## 2. Alternatives and why the direction changed

| Approach | What it offers | Cost or unresolved issue | Disposition |
|---|---|---|---|
| Shared upstream key through bundled LiteLLM | Familiar deployment and central model routing | A shared key does not identify each developer to the customer's existing per-person budget system | Insufficient for this requirement |
| Personal key in LLM settings or sandbox-delivered secrets | A short path to direct inference with an existing key | The credential enters the agent-controlled sandbox; resolving the secret earlier fixes timing but does not fix that trust boundary. Existing organization settings behavior also cannot be assumed to isolate member credentials | Rejected as the delivered design |
| Replace bundled LiteLLM with the customer's instance as an Enterprise-managed backend | Reuses management integration if the external instance matches its expectations | Couples Enterprise to external key/user/budget administration and requires an exact version/permission audit; conflicts with the goal of requiring only inference keys | Considered; not the delivered or qualified mode |
| Keep both LiteLLMs and add a server-side identity/key hook | Preserves the server-side credential boundary while routing to the customer's ledger | Two routing layers, a hook and management coupling to maintain; passing identity in a header alone does not make the identity trustworthy | Earlier prototype direction; superseded for this beta |
| Embedded Enterprise relay to the customer's gateway | Server-side personal keys, one customer budget authority, no bundled LiteLLM required in this mode | Enterprise owns token validation, credential resolution, streaming and routing enforcement; this needs maintenance and security qualification | Selected and exercised end to end |
| Deploy a separate general-purpose gateway application | Potential reuse of a broader gateway's auth/routing features | Adds another deployed service and integration boundary; not necessary to prove this narrow requirement | Not selected for the beta |

The discussion of other gateway patterns informed the separation between workload credentials and upstream credentials. This repository does not include a verified comparative audit of another product. Do not treat an earlier brainstorm or experiment as equivalent to the delivered evidence.

## 3. Selected design and invariants

### 3.1 Existing identity, explicit credential mapping

Use the existing SSO-backed native OpenHands user UUID and organization membership. Do not create a second identity system, infer ownership from a key label, or use the raw key as identity. An operator explicitly maps an existing org+user UUID to an existing restricted gateway key and relay model allowlist.

The customer manages the relationship between that virtual key and their LiteLLM user/budget owner. OpenHands does not automatically synchronize SSO accounts, create gateway users, or administer their budgets. No Keycloak-specific backend dependency is introduced; an external OIDC test fixture was used during validation.

### 3.2 Personal credentials remain server-side

Store encrypted credentials in the Enterprise database using the existing application encryption service. The sandbox receives a short-lived OpenHands token scoped to the intended inference context, not the customer key. The relay validates the token and current membership/policy, resolves the current member credential and attaches it only to the fixed upstream request.

An extra personal secret field or moving resolution before LLM client construction would not by itself meet this boundary. Sandbox execution and file/tool access must not become a path to the customer credential. A raw identity or personal-key header supplied by the sandbox is not an authorization boundary.

The app server, authorized operators, database and encryption-secret access remain trusted. A scoped token can still authorize inference if stolen; it is not harmless metadata. This design reduces exposure of the upstream key, but does not eliminate inference misuse, prompt injection or other sandbox secret sources.

### 3.3 Keep the relay narrow

The relay is embedded in Enterprise, not a separately deployed gateway application. The delivered protocol is OpenAI-compatible chat completions, including supported streaming/tools. The gateway profile contains the fixed upstream base URL, credential header and alias-to-model mapping. See [API-PERMISSIONS.md](API-PERMISSIONS.md) for exact operations.

Only inference is sent upstream. No customer master/admin key, discovery API, key creation/deletion, user/team administration, budget update or spend-query permission is required. Optional fixture scripts perform setup administration separately and must not be confused with product permissions.

Enterprise remains responsible for secure forwarding, response/error handling and identity binding. Gateway neutrality does not remove those responsibilities or guarantee compatibility with another vendor's protocol.

### 3.4 Administrator-controlled models are an accepted trade-off

In gateway mode, administrators choose the shared model catalog and member mappings; user-entered provider URLs and keys are disabled by the opt-in configuration. One or multiple approved models are supported. This reduced flexibility is intentional for organizations relying on a central gateway policy.

The relay allowlist and customer's key ACL are independent checks. A shared model picker can currently show a model the person cannot use; enforcement happens when inference is attempted. A denial must not trigger a shared-key or alternate-provider fallback.

Disabling user configuration is not a sandbox egress firewall. Production review must examine all supported inference launch paths and bypass opportunities, rather than assuming the picker alone enforces routing.

### 3.5 The customer gateway owns budgets and aggregate reporting

Do not build another budget ledger or distributed quota system in this integration. Customer LiteLLM enforces its configured user/key budgets, including its own concurrency and in-flight semantics. No guarantee of zero overshoot under concurrency is established by this beta.

OpenHands conversation Usage remains useful feedback. Customer totals can include auxiliary calls and are not expected to equal one conversation's metrics. Organization-wide OpenHands billing dashboards were not qualified; administrators should use the customer's gateway as their aggregate source of truth.

### 3.6 Rotation changes credentials, not people

Import a replacement key for the same org+native-user mapping. Keep it attached to the same customer LiteLLM user/budget owner, then revoke the old key using customer administration. Subsequent requests resolve the replacement credential; tested existing conversations continued without app or sandbox restarts. Import does not force-cancel an in-flight stream.

The persistent application encryption/signing secret (`JWT_SECRET`) is separate. Regenerating it is not personal-key rotation and can make stored credentials unreadable. Protect it with the database backup.

### 3.7 Opt-in adoption with explicit rollback

The beta uses additive migration 216, guarded product overlays and optional deployment settings. Stock deployments should not be switched automatically. There are no SDK or frontend source changes in this snapshot; Enterprise conversation/sandbox/settings integration still changes and needs regression coverage.

Disabling the relay requires restoring a valid prior inference configuration and model profiles. It is not a complete rollback by itself. The migration preserves credential tables on downgrade; older-binary rollback has not been live-rehearsed. See [ROLLBACK.md](ROLLBACK.md).

## 4. Evidence and limits of the decision

The [Compose evidence](../compose-evidence.json) records two regular SSO members in one organization, real Haiku/Sonnet inference, tool execution, separate key/user spend attribution, budget denial/recovery, native relay model denial and personal-key rotation. A separate direct key test verified the customer's model denial. A native call with relay restrictions relaxed to isolate customer-only enforcement was not tested.

The [prior GKE evidence](../EVIDENCE.json) is a separate qualification, not a claim that the entire selected regression suite ran under Compose. Successful DeepSeek/Opus inference, Bifrost/Portkey, production identity providers, load/HA/recovery and production release acceptance remain unqualified.

Human-owned automations and GitLab resolvers should be able to reuse their established native identity, but the delivered code gates these paths until actual launch-path tests pass. Service accounts need an explicit credential and budget owner; they must not silently borrow a person's identity. These are distinct problems.

## 5. When to revisit these decisions

Revisit the relay boundary if upstream Enterprise/SDK authentication changes, a required protocol cannot be forwarded safely, or a supported built-in mechanism can provide the same server-side credential isolation with less maintenance. Revisit deployment packaging when moving from version-pinned overlays into maintained Enterprise source and supported Helm/Compose configuration.

Treat a new gateway, background launch path, key-management UI, distributed cache, or service-account policy as a separately reviewable capability with its own evidence. Do not expand the beta by removing guards and carrying forward the old acceptance results.

[Architecture diagrams](ARCHITECTURE.md) · [Engineering handoff](ENGINEERING-HANDOFF.md) · [Code map](CODE-MAP.md)
