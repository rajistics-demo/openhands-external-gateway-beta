# Engineering handoff: external-gateway beta

> Live update: [background results](BACKGROUND-LIVE-RESULTS.md) verify two native automation owners, completion callbacks, a GitHub resolver, exact LiteLLM key attribution and model denial. Historical results below retain their original scope. GitLab live delivery and the recorded webhook reliability concern remain open.

Recorded November 14, 2026; background revision November 15, 2026. This document is the resume point for an engineer who has not read the original conversation. **The repository contains a working staging evaluation, not an approved production release.** No live deployment access details are included.

## 1. Start here

Read, in order:

1. [Design decisions](DESIGN-DECISIONS.md): customer requirement, alternatives, accepted trade-offs and security invariants.
2. [Architecture](ARCHITECTURE.md) and [credential topology](TOPOLOGY.md): trusted server boundary and identity/key flow.
3. [Code map](CODE-MAP.md), [API permissions](API-PERMISSIONS.md) and [limitations](LIMITATIONS.md): actual change surfaces and current guards.
4. [Setup](SETUP.md), [verification](VERIFICATION.md) and [rollback](ROLLBACK.md): reproduce with fresh staging resources.
5. [Compose evidence](../compose-evidence.json), [review](../REVIEW.md) and separate [GKE evidence](../EVIDENCE.json): distinguish observed outcomes from plans.

The complete source overlays are included for reproducible builds; their total line count is not the feature's change size. Review the patch against its pinned Enterprise base for the actual changes. This repository is an evaluation overlay, not a full Enterprise development checkout.

For the background revision, read [BACKGROUND-WORKFLOWS.md](BACKGROUND-WORKFLOWS.md) and [BACKGROUND-VALIDATION.md](BACKGROUND-VALIDATION.md). The original live evidence below describes the earlier interactive baseline; the new coordinator run passed 119 tests, with external services substituted.

## 2. Reproducible baseline

| Component | Tested baseline |
|---|---|
| Enterprise | 1.92.0; base commit `7647eab7b963a5ed0a564215c082dd66331b79a6` |
| SDK | 1.62.0; no SDK source changes |
| Automation | 1.32.1; source revision `1b571fd2b93c4c6ea4a58eb237fc718a8f158e4e`; workspace 1.62.0 |
| Customer-like LiteLLM | 1.103.6 |
| Compose environment | Dedicated Linux amd64 host, approximately 16 GB RAM; PostgreSQL 16; Canvas 1.40.0 |
| Product overlays | 23 Python files; mapped in `build/manifest/overlay-manifest.json` |
| Original runtime patch SHA-256 | `ee331d298bd68282419ad58105a96d8e85c812639978b2ba16d2222130b64eba` |
| Frontend | No frontend source changes |

`HASHES.json` covers the delivered files. `FROZEN-INPUT-SHA256.json` records historical input provenance; it is not the current documentation manifest. The pinned-base build verifies expected base and final source hashes and the actually installed SDK. Do not change base versions or bypass hash guards to make a build pass.

The preferred tested packaging path is `build/build.sh` with the official digest-pinned base plus overlays. The optional full-source build path is not the live Compose build used for the recorded acceptance. No prebuilt beta registry image is claimed published.

## 3. Implementation map

| Responsibility | Files in the pinned Enterprise source | Resume/review concern |
|---|---|---|
| Protocol and forwarding | `server/customer_gateway/profile.py`, `relay.py`, `routes.py`, `config.py` | Fixed upstream, model mapping, bounded/redacted errors, streaming, no arbitrary credential forwarding or redirects |
| Identity binding and tokens | `server/customer_gateway/service.py`, `tokens.py`; `openhands/app_server/utils/customer_gateway_hooks.py`; JWT/session integration | Native user/org/sandbox binding, expiry, current policy and membership checks, authenticated refresh |
| Encrypted persistence and import | `storage/customer_gateway.py`, `customer_gateway_store.py`; migration 216; `server/customer_gateway/cli.py` | Org+member isolation, encryption-secret continuity, rotation/disable semantics, no key export |
| Conversation/sandbox/settings hooks | Router, live status, Docker/managed/remote sandbox and settings files listed in the code map | All supported entry points bind the right credential context; unsupported paths fail closed |
| Operator profile bootstrap | `cli/bootstrap_default_profile.py` in this repository | Shared picker plus native default launch settings; catalog validation, transaction, member overrides, custom LLM tuning |
| Deployment package | `evaluate`, `docker-compose.customer-gateway.yml`, `docker-compose.security.yml`, `build/` | Opt-in mode, persistent generated secrets, image and URL correctness, supported rollback |

The app serves its own relay/catalog/token endpoints. The only upstream gateway operation is chat completions with the mapped member inference key. An operator imports existing keys through stdin; the application does not receive the customer's gateway master key. No separate relay service is deployed.

## 4. What has been demonstrated

| Capability | Recorded outcome and boundary |
|---|---|
| Identity isolation | Two regular SSO members in one organization mapped to distinct correct customer users/keys |
| Real inference and tools | Haiku and Sonnet success; harmless file/tool markers independently checked |
| Fresh launch defaults | Both members completed fresh native API conversations without an explicit `llm_profile` |
| Spend ownership | 13 positive customer spend rows: 8 for one member, 5 for the other; replacement key had 3 positive rows |
| Model enforcement | Native Opus attempt denied by relay; separately, direct customer-key Opus request denied by LiteLLM. Customer-only denial through a relaxed native relay was not tested |
| Budget enforcement | Staging user budget lowered below accumulated spend, native `ExceededBudget`, budget restored and inference recovered |
| Rotation | Same native identity and customer budget owner; old key revoked; existing conversation worked with replacement key without app/sandbox restart |
| Credential boundary | Encrypted records verified; checked sandbox environments had no personal/customer-master/provider key and no Docker socket |
| UI | Keyless model selection, persistent selection label and conversation Usage observed; customer budget/spend/log views checked |
| Review | Primary source/live-path review plus hosted Opus review for the controlled pilot; not a production security certification |

Use the evidence files for exact details. The separate prior GKE run recorded 1,165 selected passing regressions and one skip; that is not a full Compose regression claim. Prior test results do not certify a later code revision. Raw logs, credentials, account identifiers and deployment access information are intentionally excluded.

## 5. Remaining work, in reviewable stages

These are acceptance gates, not delivery estimates or promises. Identify an owner for each before production adoption.

### Stage A — upstream integration and optional-mode regression

Port the narrowly scoped patch into an authorized checkout of the intended Enterprise release. Reconcile upstream changes instead of copying old full files over newer code. Keep credential/token/profile contracts gateway-neutral and use existing application services where possible.

Acceptance: source review of the actual diff; applicable lint/type/regression checks; fresh two-member real inference; UI and API default/profile-switch coverage; a mode-disabled baseline that preserves existing managed inference/settings; no SDK/frontend changes assumed necessary without evidence. Refresh the patch, overlay manifest and image provenance together if retaining this evaluation package.

### Stage B — routing and credential security review

Review all supported launch, resume, model-switch and auxiliary inference paths. Validate invalid/expired tokens, wrong organization/user/sandbox context, removed membership, disabled mappings, missing keys, policy changes and token refresh. Verify there is no fallback to shared credentials or an arbitrary upstream/header. Inspect settings/export/log/error surfaces for customer keys.

Acceptance: meaningful automated negative cases plus live-path evidence; bounded malformed/error handling; refresh/rotation/disable behavior; streaming/tools compatibility; current SSRF/redirect/egress and network assumptions explicitly reviewed. Exercise customer-only native model denial separately from relay denial. Document residual risk from a usable sandbox token, trusted server administrators and external egress.

### Stage C — deployment and operational qualification

Validate the intended customer's supported IdP and the actual Helm and Compose deployment paths on the target release. Prior Helm work does not make this repository a complete supported Helm distribution. Add reviewed chart/values integration if needed; do not assume the Compose overlay can simply be copied into Helm.

Acceptance: exact-release install/upgrade, opt-in/off regression, migration re-entry, protected backup/restore with the persistent encryption secret, older-binary rollback rehearsal, gateway outage/recovery, slow stream/timeouts, cancellation and disconnect handling. For production scale, include replica behavior, connection/resource limits, load/soak, safe observability and failure recovery. Define supported budget concurrency expectations with the gateway owner; the relay has no distributed reservation engine.

### Stage D — human background workflows, then service accounts

The beta now admits native app-started automation and GitLab resolver triggers, with source-level ownership/binding and dispatcher-refusal tests. Production acceptance still needs the live staging checks in BACKGROUND-WORKFLOWS.md. Keep guards on other unsupported launch paths until their actual owner/trigger identity is established. Where an existing human OpenHands identity is already resolved, reuse it. The current automation contract uses the definition owner, including manual/event-triggered runs. A different owner-versus-trigger policy would be a separate product change.

Acceptance per launch path: correct member key and customer spend owner, membership checks, model/budget denial, refresh, rotation and unmapped-actor failure. Service accounts are a separate policy and test milestone with an explicit credential/budget owner; no silent fallback to a human or organization shared key.

### Stage E — additional gateways and operator experience

Qualify one additional gateway through the existing profile abstraction before adding vendor-specific logic. Bifrost and Portkey are candidates, not supported products today. Responses API and ACP require separate work; the delivered protocol is chat completions.

Acceptance: real native streaming/tools, per-user attribution, model and budget denial, rotation, outage handling and safe errors for each named version. Consider a key-import UI/API only after authorization, audit, encryption, redaction and no-readback requirements are agreed. Improve per-user picker filtering separately from enforcing model access.

## 6. Handling team-requested changes

For each request, record the problem, affected contract, target release, exact source files and acceptance evidence. First determine whether it changes identity ownership, credential exposure, allowed routing, gateway permissions or budget semantics. Those require revisiting the corresponding design decision, not just updating a configuration example.

Implement one reviewable scope at a time. Keep the SDK unchanged unless a specific missing capability is demonstrated. When changing bootstrap/profile code, retest both the UI picker and native default API launches; test member overrides and preserve or explicitly migrate custom tuning. When changing routing, test auxiliary calls and errors as well as successful chat output.

Update tests, source patch, final overlay hashes, build manifest, `HASHES.json`, docs and evidence consistently. Inspect exact outgoing commits and sanitized evidence before publishing. Do not label prior evidence as fresh validation of modified code. Do not remove a gate merely because the intended architecture should support that path.

## 7. Private operator record and live-demo preservation

The owner maintains live deployment origins, cloud/resource references, access procedures, credential locations, protected backups and raw diagnostic receipts in a separate private operator record. Request that record through an authorized private channel when live operations are needed. None of those values belong in this repository, even while it is private.

The existing walkthrough demo was requested to remain running with test data intact. This document is not authorization to tear it down, restart services, change identities/keys, probe unrelated installations or reuse production volumes. Verify current state and permissions before live work; repository evidence is a dated snapshot, not a live health check.

For a new engineer without live access, the supported resume path is to build from this repository and follow [SETUP.md](SETUP.md) on separately authorized staging resources. No customer invitation, public visibility change or external communication is implied by this handoff. Preserve the Enterprise license and applicable evaluation terms.

## 8. Release decision

Before calling this production-ready, obtain the responsible Enterprise/security/deployment owners' review of the actual integrated revision and complete the relevant stages above. Record supported versions, deployment modes, identity/credential ownership, negative-path results, operational recovery and accepted remaining limits. A successful two-user demo establishes feasibility; it does not replace production acceptance.
