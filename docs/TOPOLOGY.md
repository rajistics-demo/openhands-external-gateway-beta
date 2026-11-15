# Endpoints and credential ownership

| Value | Owner / destination | Authentication |
|---|---|---|
| `CUSTOMER_GATEWAY_RELAY_URL` | OpenHands app `/api/customer-gateway/v1` | Short-lived scoped inference token |
| `CUSTOMER_GATEWAY_TOKEN_URL` | OpenHands app `/api/customer-gateway/token` | Sandbox session authentication |
| Gateway profile `base_url` | Customer LiteLLM, usually ending `/v1` | Member personal virtual key, added server-side |

The relay accepts chat-completion requests and local catalog discovery, chooses a fixed configured upstream, and supplies the stored member key. It does not forward arbitrary client authentication headers or call customer key/user/team/budget administration endpoints.

Member keys are encrypted in `customer_gateway_member_credential` in the Enterprise database using the application’s existing encryption service. SSO maps to the native user UUID; the org+user mapping selects the credential. Replacing that credential leaves identity unchanged. The sandbox never receives the personal key.

The app’s shared model catalog, its additional member allowlist and the customer key’s model ACL are independent layers. Customer LiteLLM owns the budget and aggregate spend. This package creates no new budget engine and no network firewall.
