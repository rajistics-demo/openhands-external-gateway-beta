# Gateway operations and setup permissions

## OpenHands calls to the customer gateway

The current product relay makes one outbound inference operation:

| Method and path | Purpose | Credential |
|---|---|---|
| `POST <gateway-profile.base_url>/chat/completions` | Streaming or non-streaming OpenAI-compatible inference | The mapped member virtual key, normally `Authorization: Bearer <key>` |

If the configured gateway base ends in `/v1`, this is `POST /v1/chat/completions`. The profile can specify a different credential-header name; the default LiteLLM configuration uses bearer authentication.

OpenHands does **not** call the customer gateway for model discovery, key generation/update/deletion, user/team management, budget updates, spend queries, global configuration or UI administration. It requires no customer LiteLLM master/admin key. Restrict imported keys to the necessary inference routes/models using the controls supported by the customer's gateway version.

## Endpoints served inside Enterprise

| Endpoint on the OpenHands app | Behavior |
|---|---|
| `POST /api/customer-gateway/v1/chat/completions` | Validates scoped inference token and current membership/policy, resolves the encrypted member key, forwards to the fixed upstream |
| `GET /api/customer-gateway/v1/models` | Returns the configured catalog filtered by the relay member allowlist; no upstream discovery request |
| `GET /api/customer-gateway/token` | Authenticates the sandbox session and refreshes its scoped inference token; never returns a customer key |

No public HTTP endpoint in this integration writes or exports personal gateway keys. The operator CLI performs local encrypted database updates from stdin.

## Operator and fixture work is separate

The customer creates/manages keys, users, teams, budgets and reporting in their existing gateway. An OpenHands operator imports an existing key and associates it with the native org/user UUID. To rotate, update that mapping and revoke the old key in the customer gateway. Keep the same LiteLLM user/budget owner for spend continuity.

Optional demo tools use administrative operations such as `/user/new` and `/key/generate` to prepare synthetic fixtures. Demo budget/rotation tests also used customer administration. Those are operator/test activities, not application permissions. The optional demo LiteLLM service owns its own master key; app, worker and sandbox do not receive it.

Source: `server/customer_gateway/profile.py` and `relay.py`, represented by `build/overlay/f013.py` and `f014.py`; see the overlay manifest for the complete source map.

## Native automation authentication

Automation 1.32.1 uses its existing OpenHands service authentication to obtain an internal application API key for `automation.user_id` and `automation.org_id`. This is separate from the customer gateway virtual key: the integration still imports customer keys and sends only inference upstream. External event actors are not automatically substituted for the definition owner. See [the ownership matrix](BACKGROUND-WORKFLOWS.md).
