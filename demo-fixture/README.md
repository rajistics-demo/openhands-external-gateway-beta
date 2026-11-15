# Demo fixture — optional, demo DB only

Everything in this directory exists only to make the evaluation runnable **without**
any customer infrastructure. None of it is part of the product.

- `litellm-customer.yaml` / `provider_stub.py` / `Dockerfile.provider-stub` — a
  deterministic, customer-shaped LiteLLM config and a fake OpenAI-compatible provider
  behind it. Used only by `docker-compose.demo-litellm.yml`.
- `fixture_seed_key.py` — talks to the demo LiteLLM's admin API with its master key to
  create a demo customer user + budget and mint a demo personal key. Run this against
  the demo LiteLLM only; the Enterprise app never sees the master key.
- `seed_fixture.py` — **operator restore tool**. It inserts two approved synthetic
  identities (SSO provider/org/user rows) into a **fresh, empty** application database
  so this package is reviewable without real customer SSO wired up yet. It refuses to
  run if any of the target users already exist.

  **Do not run `seed_fixture.py` against a production or customer-provisioned
  database.** It is for demonstration/evaluation databases only.

  **v4 fix:** a fresh org created by this script now gets `contact_name`/
  `contact_email` set (defaults: `"Gateway Evaluation Operator"` /
  `"operator@example.com"`, or pass your own in `doc['org']`). `OrgResponse`
  (`server/routes/org_models.py`) declares both as required, non-nullable `str`
  fields with no default, even though the DB column itself is nullable
  (`storage/org.py`) — an org fixture-created without them serializes fine until
  something returns it through `OrgResponse`, which then 500s on Pydantic
  validation. This was diagnosed as the exact cause of a "Could not load your
  workspaces" UI failure seen against a v3-seeded org; it is a gap in this
  fixture script, not a gateway/product bug, so no UI/product code is changed.

## Typical demo sequence

```sh
# 1. Bring up the base stack + customer-gateway overlay + demo LiteLLM overlay
docker compose -f docker-compose.yml -f docker-compose.customer-gateway.yml \
  -f docker-compose.demo-litellm.yml up -d

# 2. Seed two demo identities into the fresh app DB (operator action, private JSON on stdin)
cat private-demo-identities.json | docker compose exec -T app \
  python demo-fixture/seed_fixture.py

# 3. Create demo users/budgets and mint demo personal keys against the demo LiteLLM
LITELLM_URL=http://localhost:${DEMO_LITELLM_HOST_PORT:-4000} \
LITELLM_MASTER_KEY=$DEMO_LITELLM_MASTER_KEY \
  python demo-fixture/fixture_seed_key.py user --user cust-susan-demo \
    --models deepseek-chat,claude-sonnet --budget 1.0

LITELLM_URL=http://localhost:${DEMO_LITELLM_HOST_PORT:-4000} \
LITELLM_MASTER_KEY=$DEMO_LITELLM_MASTER_KEY \
  python demo-fixture/fixture_seed_key.py key --user cust-susan-demo \
    --models deepseek-chat,claude-sonnet --alias oh-susan-demo \
  | docker compose exec -T app python -m server.customer_gateway.cli set-key \
      --org <demo-org-uuid> --user <susan-native-uuid> --models deepseek-chat,claude-sonnet

# 4. Use the real CLI (cli/README.md) to point the org at the demo gateway profile,
#    then log in as the seeded user through normal native SSO and start a conversation.
```

`private-demo-identities.json` is **not included**; the deploying operator supplies the
existing approved fixture identity/client privately, as stated in the task.
