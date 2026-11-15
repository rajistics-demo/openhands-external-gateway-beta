# Real-provider smoke configuration

The native real-provider test used Anthropic Haiku 4.5 behind the customer LiteLLM, with an existing provider credential held **only by that gateway**. This is an additional customer-gateway configuration, not an Enterprise or SDK code change. The bundled staging chart replays the deterministic policy fixture; the real-model extension was supplied privately.

Example customer LiteLLM configuration (merge with the customer's own configuration):

```yaml
model_list:
  - model_name: real-haiku
    litellm_params:
      model: anthropic/claude-haiku-4-5-20251001
      api_key: os.environ/ANTHROPIC_API_KEY
litellm_settings:
  drop_params: true
```

Use a normal gateway-side secret reference for the provider credential. Do not add it to the OpenHands sandbox environment, generic personal secrets or keyless LLM profile.

`drop_params: true` was necessary on the tested LiteLLM 1.103.6: strict mode rejected the SDK's OpenAI `prompt_cache_key` extension on the Anthropic route before provider inference. With filtering enabled, the unchanged Enterprise relay and SDK completed two actual tool actions. Endpoint compatibility alone does not establish support for every provider parameter; test the customer's exact models and gateway configuration.

Allow the alias on the customer's user/key policy, include it in the Enterprise gateway catalog and import the existing personal virtual key against the existing native user UUID. The keyless shared OpenHands model profile used `openai/real-haiku`, with a 2,048-token output cap for this smoke test. The customer user's budget remained configured.

The actual native task wrote and read a benign marker file using `file_editor` and `terminal`. A separate authenticated runtime read verified exact contents. Three positive-spend customer ledger rows matched the expected personal key and existing customer user. The provider credential and personal keys were absent from the live sandbox user export and event trace; credential environment-variable presence checks were false.

This qualifies that one real model through the native path. It does not qualify real Sonnet/DeepSeek/Opus, Bifrost, Portkey or native Docker Compose.

## Adding a real Sonnet route and an Opus permission-contrast

Same mechanism, not new code: add one more `model_list` entry to the customer's
LiteLLM config for Sonnet (e.g. `anthropic/claude-sonnet-4-5-...`), add its alias to
the Enterprise gateway catalog JSON passed to `cli set-org`, and allow it on the
relevant customer user/key policy; deny the Opus alias on the same policy (or omit it
from that user's key) to get the ACL contrast Dave/Sue previously exercised with the
deterministic fixture. The deploying operator will supply the exact provider IDs/credentials privately,
per the task's instruction — this package does not hardcode or guess them. Until this
is actually run against a live gateway, treat Sonnet/Opus-contrast-with-real-providers
as configuration guidance, not a verified result.
