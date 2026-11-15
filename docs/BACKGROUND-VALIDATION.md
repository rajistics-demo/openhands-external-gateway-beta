# Background workflow validation

## Source and scope

The November 15, 2026 revision enables native automation and resolver triggers through the existing Enterprise binder. It restores stock Compose event forwarding. It does not change the SDK, frontend, customer key storage, relay protocol or customer gateway permissions. A stale migration docstring was also corrected so the preferred overlay build and two-step source build agree; the migration's executable code is unchanged.

| Source | Pin |
|---|---|
| Enterprise | 1.92.0, `7647eab7b963a5ed0a564215c082dd66331b79a6` plus the packaged patch |
| SDK / workspace | 1.62.0 / 1.62.0 |
| Automation | 1.32.1, `1b571fd2b93c4c6ea4a58eb237fc718a8f158e4e` |
| Tested gateway service SHA-256 | `304eeb1d83e4224ae59856f0d5e75deb55ce9da17059514089709354b25ceb47` |

The automation revision was read from the deployed image's official source labels. Imported backend code was checked against the captured deployed source; the final rerun used the complete exact-release checkout. The earlier partial reference tree was diagnostic scaffolding, not the final source pin.

## Independently observed results

The coordinator reran the combined gateway, automation and GitLab caller suite: **119 tests, zero failures, zero errors, zero skips**. The source hash was checked before and after the run. SDK/workspace versions and automation Git revision were asserted by the runner.

| Claim | Evidence |
|---|---|
| GitLab issue/MR launches use the mapped actor context | Real resolver context, conversation service and binder; posted scoped-token claims checked for the test actors |
| Native automation startup succeeds | Real `CloudSandboxBackend.start_conversation`, HTTP serialization into the real Enterprise service/binder, valid sandbox-response fixture; backend returns `StartedConversation` |
| Different owners stay distinct | Two owners in the same synthetic organization get distinct owner-scoped tokens through successful backend launches |
| Missing/disabled/service-account mapping is not a shared-key fallback | Store-denial propagation through the actual launch path; no sandbox LLM post on refusal |
| A launch refusal fails the automation | Actual dispatcher `_execute_run` handles a `ConversationStartError`; SQLite row is FAILED, status detail retained, no entrypoint command executed |
| Successful startup reaches execution | Actual dispatcher reaches the substituted command executor and does not mark the run failed |
| Terminal state writes persist | Real ORM/status utilities with SQLite; failed/completed writes and stale-terminal-write protection checked |

The customer-key store's account-type classification is separate baseline coverage. Mocking a store denial in a caller test proves propagation, not that a real database account was classified. The source's explicit human-account check remains unchanged.

[Machine-readable results](../background-validation.json) · [Automation source pins](automation-source-pins.json)

## What was substituted

HTTP transport, sandbox provisioning/agent-server responses, internal application API-key minting, uploads and entrypoint execution are test fixtures. SQLite is an actual in-memory database using the real ORM/status functions; it is not PostgreSQL qualification. These tests do not contact a model provider or a live GitLab service.

The successful dispatcher test reaches script execution; the real entrypoint completion-callback HTTP round-trip is not exercised. Live scheduler timing, webhook authentication/delivery/posting, customer SSO/repository access, background provider spend, budget/model denials after startup, long-running refresh and gateway outage/recovery still require [the staging checklist](BACKGROUND-WORKFLOWS.md).

Earlier live two-SSO-user provider, spend, budget and rotation evidence remains in [compose-evidence.json](../compose-evidence.json). Its runtime patch and background restrictions describe that earlier baseline. [EVIDENCE.json](../EVIDENCE.json) is separate historical GKE evidence. Neither is relabeled as a fresh live background test.

## Reproduce the developer tests

Use authorized source checkouts. Follow the pinned Enterprise repository's normal development setup and guidance. Do not run this against production data.

1. Check out the Enterprise base commit above in an isolated worktree.
2. Apply `build/patches/enterprise-1.92.0-customer-gateway.patch`, then `build/patches/migration-docstring-correction.patch` from this beta repository. This preserves the original migration contents and correction order used by the guarded source build.
3. Check out automation at the exact revision above in a separate directory.
4. Use the Enterprise test environment with SDK 1.62.0, pytest/pytest-asyncio and aiosqlite. The cross-repository tests also require workspace 1.62.0, matching the deployed automation image. If absent, install that exact package without replacing the pinned SDK:

```sh
uv pip install --python .venv/bin/python --no-deps openhands-workspace==1.62.0
```

From the patched Enterprise checkout:

```sh
AUTOMATION_SOURCE_DIR=/absolute/path/to/automation-checkout \
  .venv/bin/python -m pytest --noconftest \
  tests/unit/server/customer_gateway/ \
  tests/unit/integrations/gitlab/test_gitlab_resolver_gateway_integration.py -q
```

The source-provenance guard must match the pinned automation backend. This focused command avoids the unrelated global PostgreSQL fixture; it does not claim to run the entire Enterprise suite. Run the repository-required broader checks when integrating into a different release. Keep raw results, credentials and diagnostic exports private.

## Package consistency

The coordinator applied the complete 42-section patch and the separate migration documentation correction to pristine pinned Enterprise source. Base and final guards passed for all 23 runtime paths, and all changed Python files compiled. The executable migration code is unchanged.

The preferred pinned-base candidate image was also built on the isolated evaluation host. The installed SDK is 1.62.0 and all 23 built-image source hashes match the final manifest. The merged Compose configuration enables the gateway and event forwarding, disables user LLM configuration, and contains no bundled LiteLLM service. The candidate image was not substituted into the existing walkthrough deployment.
