# Evaluation limits

This preview was exercised on a dedicated 16 GB AWS Docker host with two regular SSO members and customer-like LiteLLM 1.103.6. Real Haiku 4.5 and Sonnet 4.5 queries succeeded. Opus was a denial target; successful real Opus or DeepSeek inference was not qualified in this Compose run.

Not qualified: the customer’s production IdP/network/model set; HA, load/soak and disaster recovery; older-binary rollback; Bifrost/Portkey; organization-wide OpenHands billing dashboards. The prior GKE regression evidence is recorded separately.

While this mode is enabled, service-account launches, warm backends, unseeded standalone `CloudWorkspace.get_llm` and Responses API calls remain unsupported/refused. Native app-started human automations and GitLab resolver launches are now admitted; see [BACKGROUND-WORKFLOWS.md](BACKGROUND-WORKFLOWS.md) for their test scope and live staging checks. Startup app-side LLM title generation uses a first-message fallback. Other supported native auxiliary inference is charged through the member gateway key.

Personal key import/rotation is an operator CLI action. There is no new key-management UI and no automatic synchronization between SSO accounts and customer LiteLLM users. Map the native OpenHands UUID to an existing customer key explicitly.

The shared catalog and relay member allowlist are separate from the customer key’s own model ACL. This evaluation kept Susan restricted in both layers; native relay denial and a separate direct customer-key denial were verified. Relaxing the relay guard to demonstrate customer-only enforcement was not performed. Do not treat that exact native scenario as tested.

The gateway owns budget semantics, including concurrent/in-flight behavior. This relay adds no new budget ledger or distributed reservation system. Model-denial and outage errors stop inference; they do not themselves destroy a sandbox.

The application and worker retain the native Docker backend’s host socket access and must be trusted. Test sandbox containers had no Docker socket and no provider/master/personal gateway keys in their environment. This package introduces no sandbox egress firewall; operators remain responsible for network isolation and all other secret sources.

App operators with the application encryption key and database access can decrypt stored member credentials. Back up and protect the persistent JWT_SECRET and database together; personal-key rotation does not require changing that secret.

The background revision has 119 independently passing tests, with external services substituted and SQLite persistence checks. Live scheduler/webhook/provider execution and the entrypoint completion-callback HTTP round-trip were not exercised in these new tests. Automations use the definition owner rather than an arbitrary external event actor. Service accounts still need a separately approved credential and budget-owner policy. See [the background scope](BACKGROUND-WORKFLOWS.md).
