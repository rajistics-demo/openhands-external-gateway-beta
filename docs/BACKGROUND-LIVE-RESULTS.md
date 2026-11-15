# Live background workflow results

The isolated Compose evaluation used Enterprise 1.92.0, SDK/workspace 1.62.0, automation 1.32.1 and customer LiteLLM 1.103.6. It used two synthetic regular members in the same organization, native external OIDC, encrypted server-side virtual keys and no bundled OpenHands LiteLLM. This is beta evidence, not production certification.

| Check | Observed result |
|---|---|
| Native prompt automations | Both definition owners completed real tool tasks through the native runner and completion callback. The coordinator independently read both proof files from the retained terminal containers. Definitions remain disabled. |
| Personal attribution | All action-associated model response IDs joined to LiteLLM request IDs under each owner's actual key: three responses for one automation, two for the other. |
| GitHub resolver | A real GitHub issue-label webhook, native OAuth connection and existing actor/org routing started a conversation. It read the repository and posted the requested result. All nine action-associated model responses joined to the actor's key in LiteLLM. No repository change or PR was made. |
| Disallowed model | A native automation requesting a prohibited model failed with HTTP 403, `relay_denied/model_not_permitted`. The entrypoint propagated failure to the native run record. No shared-key fallback occurred. |
| Credential isolation | Checked sandbox environments contain no personal upstream key, provider/master key or GitHub App credentials. Personal keys stayed in encrypted server storage; operator setup reused them in memory. |
| Existing walkthrough | Original running container identities/images were preserved. Nothing was torn down. |

## Configuration learned from the test

The Compose gateway overlay sets the existing Enterprise GitHub and GitLab service classes on both app and worker. Without these settings, the generic GitHub service did not retrieve the actor's saved native OAuth token and attempted an empty Bearer header. This correction uses existing Enterprise code; it adds no SDK or product authentication implementation.

These class settings do not create an OAuth provider, Git App, connection or repository claim. Configure those using the installation's normal native integration setup. For a fresh install, supply the appropriate GitHub App configuration before the first migration so the existing native provider seed runs. Keep App secrets server-side. Do not add a Keycloak-specific dependency or use an administrative bootstrap helper to replace normal OAuth.

## Review limits

A GitHub label delivery returned HTTP 500 even though the native conversation finished and posted its results. That HTTP response is a real unresolved reliability concern: investigate acknowledgement handling, redelivery and deduplication before production. Do not retry an uncertain delivery blindly.

GitLab's actual caller/context is source-tested, but live GitLab issue/MR webhook delivery and posting are still unverified. Manual dispatch proves native automation owner routing and callbacks, not cron timing or a new event-actor policy. Live background budget exhaustion/recovery, long-running refresh, rotation, outages, HA/load and other gateways still need qualification. The picker can display a model that inference subsequently refuses.

An initial negative test hit an unrelated sandbox-polling `ReadError`; it was not counted as a policy denial. Its retry produced the explicit 403 above. Old expected customer-account labels in a private fixture were also stale; final attribution used LiteLLM's current key-owner records plus exact response-ID joins, not those labels.

## Supplemental developer test

The independently rerun combined suite now has 122 passing tests with no failures, errors or skips. The additional three GitHub caller cases are in `tests/test_github_resolver_gateway_integration.py`. Copy that file into `tests/unit/integrations/github/` in the patched Enterprise checkout, preserving that location because its template fixture resolves the Enterprise repository root from the test path. Add the copied file to the pinned source-test command in [BACKGROUND-VALIDATION.md](BACKGROUND-VALIDATION.md). It imports Enterprise modules and is not a standalone package test.

[Machine-readable live results](../background-live-validation.json) · [Source validation](BACKGROUND-VALIDATION.md) · [Workflow policy](BACKGROUND-WORKFLOWS.md)
