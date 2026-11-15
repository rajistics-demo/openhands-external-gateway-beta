# Set up a customer-owned LiteLLM gateway

This guide takes an administrator from a fresh evaluation host to two OpenHands members using separate existing LiteLLM virtual keys. Start with staging, two test members and small budgets. This is an Enterprise beta for native conversations, including the supported app-started background workflows; review [limitations](LIMITATIONS.md) before rollout.

## 1. Prepare the host and access

You need:

- A dedicated Linux amd64 host with Docker Engine, BuildKit, Compose v2, Python 3 and approximately 16 GB RAM.
- Access to the pinned official Enterprise base image and an applicable Enterprise license/configuration.
- A public HTTPS app origin, your own certificate/reverse proxy and normal supported OpenHands authentication. This package provisions no DNS, certificates, identity provider or firewall.
- An existing staging LiteLLM endpoint reachable over HTTPS from Enterprise, with working chat-completions models and tool/stream support.
- Two test people who can sign in to the same OpenHands organization, and an administrator able to inspect their native user UUIDs and organization UUID.

Use a separate project and fresh database volumes. The app and worker use the host Docker socket to create native sandboxes; do not share this daemon with unrelated sensitive workloads. Sandboxes must reach the app's relay and token endpoints. They do not need the customer virtual key.

## 2. Prepare people, models and budgets in LiteLLM

Using your existing LiteLLM administration process:

1. Create or select a distinct LiteLLM user/budget owner for each person.
2. Issue a restricted virtual key for each person. Associate it with that person's LiteLLM user. Store keys in your existing administrator secret manager.
3. Set the allowed upstream model names and a small user budget. For example, give Member A DeepSeek and Sonnet, and deny Opus; Member B can have a different policy.
4. Verify the gateway itself permits the intended models and rejects forbidden models. Confirm model aliases match your LiteLLM configuration exactly.

OpenHands imports these keys; it does not create or administer your LiteLLM users, teams, budgets or keys. **Do not supply a LiteLLM master/admin key to Enterprise.** See [exact API permissions](API-PERMISSIONS.md). Model names below are illustrative aliases, not bundled provider access.

## 3. Configure the fresh Compose stack

From the repository root:

```sh
cp .env.example .env
cp .env.customer-gateway.example .env.customer-gateway
```

Edit `.env` with a unique `COMPOSE_PROJECT_NAME`, your app's `WEB_HOST` and HTTPS `WEB_URL`, and applicable licensing values. The default `APP_IMAGE` matches the build below. Keep filled-in environment files private.

In `.env.customer-gateway`, use **your OpenHands origin**, for example:

```dotenv
CUSTOMER_GATEWAY_RELAY_URL=https://openhands.customer.example/api/customer-gateway/v1
CUSTOMER_GATEWAY_TOKEN_URL=https://openhands.customer.example/api/customer-gateway/token
CUSTOMER_GATEWAY_TOKEN_TTL_SECONDS=900
CUSTOMER_GATEWAY_ALLOW_HTTP_TEST_ONLY=false
```

The customer LiteLLM URL belongs in the gateway profile in step 6, not in these two variables. Configure HTTPS termination to forward to the Compose proxy host port (`9043` by default); restrict staging access to intended operators and users.

```sh
./build/build.sh
./evaluate config
./evaluate up
```

The build verifies the pinned base, overlay hashes and installed SDK version. `config` validates quietly; success does not print resolved secrets. `up` starts services. Initial image pulls and native sandbox startup can take several minutes.

The wrapper creates `.env.generated-secrets` with mode 0600 on first use. Back this file up securely with the database. Its persistent `JWT_SECRET` is needed to decrypt member credentials: **never regenerate it to rotate a personal key**. Start the stack through `./evaluate` so the security and gateway overlays are applied together.

## 4. Prepare operator commands

Use this shell function for the rest of this guide. It uses the same environment files and overlays as `./evaluate`, avoiding accidental selection of a different Compose project:

```sh
dc() {
  docker compose \
    --env-file .env \
    --env-file .env.customer-gateway \
    --env-file .env.generated-secrets \
    -f docker-compose.yml \
    -f docker-compose.customer-gateway.yml \
    -f docker-compose.security.yml "$@"
}
dc ps
```

Wait for services to become healthy. Inspect diagnostics locally if needed; logs and resolved configuration can contain sensitive data and must not be committed or shared raw.

## 5. Sign in and identify the members

Configure normal native authentication or your supported SSO provider through existing OpenHands administration. No Keycloak container or Keycloak-specific integration is required.

Have both people sign in and confirm membership in the intended organization. Record the actual native organization and user UUIDs from your trusted administrative surface. Do not infer identity from an email label, display name, list order or a LiteLLM key name. Importing a key does not provision a person or link an SSO account automatically.

Set these non-secret identifiers locally, replacing the placeholders:

```sh
ORG_ID='REPLACE-WITH-ORGANIZATION-UUID'
MEMBER_A_ID='REPLACE-WITH-FIRST-NATIVE-USER-UUID'
MEMBER_B_ID='REPLACE-WITH-SECOND-NATIVE-USER-UUID'
```

## 6. Configure the fixed gateway and catalog

Create a private working directory (ignored by this repository) and write your gateway profile:

```sh
mkdir -p private
chmod 700 private
cat > private/gateway-profile.json <<'JSON'
{
  "base_url": "https://gateway.customer.example/v1",
  "protocol": "openai_chat_completions",
  "credential_header": "authorization",
  "capabilities": ["stream", "tools"],
  "models": {
    "deepseek": "deepseek",
    "sonnet": "sonnet",
    "opus": "opus"
  }
}
JSON
chmod 600 private/gateway-profile.json
```

Replace the origin and the **right-hand** model names with your LiteLLM deployment's exact names. The left-hand aliases are the catalog names OpenHands uses. The relay appends `/chat/completions` to `base_url`; a typical LiteLLM deployment uses `/v1` here. This catalog is configured locally; Enterprise does not discover it through your gateway's `/models` API.

```sh
dc cp private/gateway-profile.json app:/tmp/customer-gateway-profile.json
dc exec app python -m server.customer_gateway.cli set-org \
  --org "$ORG_ID" --gateway-id customer \
  --profile-file /tmp/customer-gateway-profile.json
dc exec app rm -f /tmp/customer-gateway-profile.json
```

## 7. Import each person's key securely

Read the real virtual key from your secret manager into stdin. This example uses `pass`; substitute your own secret-manager command. Never paste the key into a command argument, committed JSON, model profile or conversation prompt.

```sh
pass show staging/gateway/member-a | dc exec -T app \
  python -m server.customer_gateway.cli set-key \
  --org "$ORG_ID" --user "$MEMBER_A_ID" --models deepseek,sonnet

pass show staging/gateway/member-b | dc exec -T app \
  python -m server.customer_gateway.cli set-key \
  --org "$ORG_ID" --user "$MEMBER_B_ID" --models sonnet,opus

dc exec app python -m server.customer_gateway.cli status --org "$ORG_ID"
```

The model lists are OpenHands catalog aliases. Both the relay allowlist and LiteLLM's own key ACL apply. Key import stores an encrypted org+user credential record in the Enterprise database. The sandbox gets a short-lived scoped token; the customer key stays server-side. Status is masked, not a key-read command.

## 8. Create keyless model profiles and a default

```sh
dc cp cli/bootstrap_default_profile.py app:/tmp/bootstrap_default_profile.py
dc exec -e PYTHONPATH=/app app python /tmp/bootstrap_default_profile.py \
  --org "$ORG_ID" --alias deepseek --profile-name DeepSeek
dc exec -e PYTHONPATH=/app app python /tmp/bootstrap_default_profile.py \
  --org "$ORG_ID" --alias opus --profile-name Opus
dc exec -e PYTHONPATH=/app app python /tmp/bootstrap_default_profile.py \
  --org "$ORG_ID" --alias sonnet --profile-name Sonnet
```

Each invocation adds/updates a shared picker profile and makes it the default. Running Sonnet last selects a default both sample members can use. Choose an actual permitted model for your members. The script updates both the picker and native API launch defaults; profiles contain no customer key.

On an existing organization, back up custom LLM tuning first: this bootstrap replaces organization-level LLM tuning with profile/SDK defaults. Other agent settings and member overrides remain under the normal settings validator. Existing member LLM overrides may need to be updated through normal settings.

## 9. Verify the complete path

Sign in as each regular member and start a fresh interactive conversation. Select a permitted model and request a harmless file write/read so the test includes tools. Open conversation Usage, then find the corresponding request in LiteLLM's own user/key ledger.

| Check | Expected result |
|---|---|
| Two people, same organization | Each person's calls use their imported virtual key and correct LiteLLM budget owner. |
| Member A selects DeepSeek or Sonnet | Inference succeeds if the model is configured and permitted upstream. |
| Member A selects Opus | Denied with no shared-key fallback. A relay denial alone does not prove upstream ACL enforcement; test the gateway ACL separately. |
| Staging budget below accumulated user spend | The next request is denied by LiteLLM; restoring the budget permits recovery. |
| OpenHands model picker and Usage | Keyless profiles appear; conversation tokens/cost are visible when returned by the model. |
| Gateway totals | User/key ledger shows aggregate spend. Auxiliary calls mean it need not equal one conversation's displayed cost. |
| Sandbox configuration/export | No customer virtual key, provider key or gateway master key is present. |
| Temporary staging gateway outage | Requests fail without alternate shared credentials; confirm resume/retry behavior for your environment. |

Run [the complete verification checklist](VERIFICATION.md) and retain sanitized outcomes before wider access. The included [evidence](../compose-evidence.json) records the tested Haiku/Sonnet demonstration; it does not certify your chosen DeepSeek/Opus deployment or production SSO configuration.

The shared picker can show a model the current person cannot use. This beta enforces policy on inference, rather than tailoring the picker per person. Native app-started human automations and GitLab resolver launches are enabled in this beta; follow [the background workflow setup and acceptance checks](BACKGROUND-WORKFLOWS.md). Automations use their definition owner, while GitLab resolver conversations use the mapped actor. Service accounts remain refused.

## 10. Rehearse rotation and recovery

Create a replacement restricted key under the **same LiteLLM user/budget owner**, then rerun `set-key` for the same OpenHands org/user UUID. Revoke the old key through your LiteLLM administration process. Verify the existing conversation resumes and new spend appears under the replacement key and same customer user. No new SSO identity, app restart or sandbox restart is required by the tested path. In-flight requests are not force-cancelled by import.

For a lost/compromised key, revoke it promptly at LiteLLM and use the local `disable --org ... --user ...` command to block that member mapping while investigating. Import a replacement and verify its policy; do not rotate the application's `JWT_SECRET` as a substitute.

Back up the database and application encryption secret securely and rehearse [recovery/rollback](ROLLBACK.md). `./evaluate down` stops this evaluation and keeps volumes; `--volumes` deletes data. Disabling the optional relay requires restoring a valid alternative inference configuration, not just removing a flag.

## Optional: an entirely synthetic local gateway

For an isolated fixture rather than your real gateway, see [demo-fixture/README.md](../demo-fixture/README.md). `./evaluate up --demo` adds a separate LiteLLM, database and deterministic provider stub. It does not automatically create SSO users, budgets or mappings. Do not use fixture restore scripts against an existing database.
