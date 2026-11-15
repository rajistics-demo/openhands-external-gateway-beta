# Reviewer code map

This is a portable evaluation overlay for Enterprise **1.92.0**, base commit `7647eab7b963a5ed0a564215c082dd66331b79a6`, with SDK **1.62.0**. It is not a complete Enterprise checkout. There are no SDK or frontend source changes.

Read the gateway profile, relay, token/service and encrypted-store code first. Then inspect the conversation launch, profile switch, sandbox/session and settings hooks. The hooks bind the same identity and scoped-token mechanism across supported native inference paths. Unsupported launch paths fail closed.

`build/patches/enterprise-1.92.0-customer-gateway.patch` contains the original change and regression tests against the pinned Enterprise source. The main patch retains the original migration section; the separate migration docstring correction is applied next by the source build. Both are required to match the reviewed overlay hash. `build/manifest/overlay-manifest.json` records the expected base and final hashes of all 23 product files. Build-time guards refuse a mismatched base.

| Packaged file | Original Enterprise path |
|---|---|
| `build/overlay/f000.py` | `migrations/versions/216_add_customer_gateway_tables.py` |
| `build/overlay/f001.py` | `openhands/app_server/app_conversation/app_conversation_router.py` |
| `build/overlay/f002.py` | `openhands/app_server/app_conversation/live_status_app_conversation_service.py` |
| `build/overlay/f003.py` | `openhands/app_server/sandbox/docker_sandbox_service.py` |
| `build/overlay/f004.py` | `openhands/app_server/sandbox/managed_sandbox_service.py` |
| `build/overlay/f005.py` | `openhands/app_server/sandbox/remote_sandbox_service.py` |
| `build/overlay/f006.py` | `openhands/app_server/services/jwt_service.py` |
| `build/overlay/f007.py` | `openhands/app_server/user/user_router.py` |
| `build/overlay/f008.py` | `openhands/app_server/utils/customer_gateway_hooks.py` |
| `build/overlay/f009.py` | `saas_server.py` |
| `build/overlay/f010.py` | `server/customer_gateway/__init__.py` |
| `build/overlay/f011.py` | `server/customer_gateway/cli.py` |
| `build/overlay/f012.py` | `server/customer_gateway/config.py` |
| `build/overlay/f013.py` | `server/customer_gateway/profile.py` |
| `build/overlay/f014.py` | `server/customer_gateway/relay.py` |
| `build/overlay/f015.py` | `server/customer_gateway/routes.py` |
| `build/overlay/f016.py` | `server/customer_gateway/service.py` |
| `build/overlay/f017.py` | `server/customer_gateway/tokens.py` |
| `build/overlay/f018.py` | `server/routes/api_keys.py` |
| `build/overlay/f019.py` | `server/routes/users_v1.py` |
| `build/overlay/f020.py` | `storage/customer_gateway.py` |
| `build/overlay/f021.py` | `storage/customer_gateway_store.py` |
| `build/overlay/f022.py` | `storage/saas_settings_store.py` |

`cli/bootstrap_default_profile.py` is operator tooling, not another product interceptor. It sets both the keyless picker profile and the native org launch default through the pinned admin-settings validator, in a single locked transaction. It leaves member overrides intact and resets org-level LLM tuning to the selected fresh profile.

`evaluate` and the additive Compose files provide the dedicated-host evaluation deployment. They generate/preserve service secrets, set the app origin and Docker network, disable the bundled proxy and keep customer administration outside the application. The optional fixture is not the customer integration itself.

The background revision changes `server/customer_gateway/service.py` (`f016.py`) to admit automation/resolver triggers; 21 runtime overlays remain at the baseline; the migration overlay changes its docstring only, matching the separate source-build correction. Its upgrade/downgrade code is unchanged. The Compose overlay restores stock event forwarding. New tests and build hashes record this revision separately from the earlier live pilot. Refer to `compose-evidence.json` for observed behavior and `EVIDENCE.json` for the separate prior GKE regression run.
