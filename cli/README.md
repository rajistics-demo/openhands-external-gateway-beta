# Operator CLI (import existing keys; no new write API)

All commands run **inside the already-running `app` container** of this Compose stack.
There is no public HTTP endpoint for writing customer keys; this keeps key import an
explicit, auditable operator action instead of an API surface.

Keys are **imported**, never generated, by this tool. The native user UUID must already
exist from the customer's normal SSO; this CLI only maps that UUID to a personal
customer-gateway key and policy.

## 0. Getting files into the running container

`server/customer_gateway/cli.py` itself is baked into the app image (one of the 23
reviewed overlay files), so `python -m server.customer_gateway.cli ...` already works
with no mount. But the **profile JSON you author**, and this package's own
`cli/bootstrap_default_profile.py` convenience script, live only on the host and are
not baked into the image or mounted by any compose file here — `docker compose exec`
cannot see a host path directly. Copy them in first:

```sh
docker compose cp cli/example-profile.json app:/tmp/profile.json   # then edit in place, or
docker compose cp /path/to/your/real-profile.json app:/tmp/profile.json
docker compose cp cli/bootstrap_default_profile.py app:/tmp/bootstrap_default_profile.py
```

`/tmp` inside the `app` container is container-local and not shared with `worker`; copy
again if you need to run a command from `worker` instead.

## 1. Configure the organization's gateway profile

Start from `cli/example-profile.json` — it has the exact schema `parse_profile`
validates (`base_url` https origin, `protocol`, `credential_header`, `capabilities`,
and the `models` catalog-alias → upstream-model map). Replace every placeholder value
before use; it is not usable as shipped.

```sh
docker compose exec app \
  python -m server.customer_gateway.cli set-org \
    --org <org-uuid> \
    --gateway-id customer \
    --profile-file /tmp/profile.json
```

Your edited profile file is a private file; it is never committed to this package, and
`/tmp/profile.json` inside the container should be removed after use
(`docker compose exec app rm -f /tmp/profile.json`).

## 2. Import or rotate a member's personal key

```sh
docker compose exec -T app \
  python -m server.customer_gateway.cli set-key \
    --org <org-uuid> \
    --user <native-user-uuid> \
    --models <catalog-aliases>
```

Pipe the actual secret key into **stdin**, never argv:

```sh
pass show customer/litellm/susan-personal-key | \
  docker compose exec -T app \
    python -m server.customer_gateway.cli set-key \
      --org <org-uuid> --user <native-user-uuid> --models deepseek-chat,claude-sonnet
```

(`pass` above is only an example of a secret-manager read; use whatever the customer's
own secret manager is.)

Replacing a key updates that stored record; it does **not** create a new identity and
does **not** force-revoke an in-flight inference stream. Revocation is observed on the
next request.

## 3. Verify before wider rollout

- Start a fresh native conversation as that user.
- Confirm the customer LiteLLM ledger shows the call attributed to the correct personal
  key/user, not a shared or master key.
- Confirm a disallowed model is denied with the customer gateway's own error, not routed
  around it.
- Confirm the sandbox's own authenticated settings/export surfaces never show the
  personal key or the customer gateway master key.

See `../docs/VERIFICATION.md` for the full checklist.

## Bootstrap script test

`cli/bootstrap_default_profile.py`'s `bound_profile_fields()` helper has a focused,
plain-assert test in `cli/test_bootstrap_default_profile.py`. It needs the same
in-container Python environment the bootstrap script itself does:

```sh
docker compose cp cli/test_bootstrap_default_profile.py app:/tmp/test_bootstrap_default_profile.py
docker compose cp cli/bootstrap_default_profile.py app:/tmp/bootstrap_default_profile.py
docker compose exec -w /tmp app python3 test_bootstrap_default_profile.py
```

## Default native launch

After configuring the catalog and importing keys, copy `cli/bootstrap_default_profile.py` into the app container and run it with `--org`, `--alias` and `--profile-name`. It sets both the shared picker profile and the organization’s default `agent_settings.llm`, so native API launches that omit `llm_profile` work as well. It preserves other agent configuration and leaves member overrides unchanged. Members with an existing LLM override must select a permitted profile or update that override through normal settings. Choose a default available to the intended members.

Activating a bootstrap default replaces the organization-level LLM configuration with the selected keyless profile and SDK defaults; back up any custom LLM tuning before using it on an existing organization. Other explicit agent configuration and member overrides are preserved through the normal SDK settings validator, which can normalize default metadata on first use.
