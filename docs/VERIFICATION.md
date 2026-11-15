# Verify before wider use

Use staging and existing approved test members first. Keep raw diagnostics private.

1. Build with `./build/build.sh`; base/overlay hashes and the installed SDK version must pass.
2. Run `./evaluate config`. Verify the selected public HTTPS origin and project name; do not use another stack’s volumes.
3. Configure normal login and native organization membership. Confirm each signed-in user’s native UUID and organization before importing keys.
4. Configure the org gateway/catalog; import separate restricted keys through stdin. Create and activate keyless profiles with the bootstrap CLI.
5. Launch a conversation as each user. Have the agent write and read a harmless marker file; verify the file independently.
6. Select another permitted model through the UI. Confirm the label persists, inference succeeds, and the customer ledger attributes the request to the correct user/key.
7. Try a disallowed model. Confirm denial and no fallback. Check both the relay allowlist and the customer key ACL; a relay denial does not prove the request reached the customer gateway.
8. Set a staging user budget below accumulated spend. Confirm a subsequent native request is denied by LiteLLM, then restore the original budget and verify recovery.
9. Rotate one member key under the same customer user/budget owner, import it against the same native UUID, and revoke the old key. Confirm the existing conversation succeeds without an app/sandbox restart and the replacement key has positive attributed spend.
10. Inspect the OpenHands conversation Usage panel and the customer’s user/key/request-log views. Aggregate gateway totals can include calls outside the conversation’s own metrics.
11. Verify encrypted storage and that sandbox environment/settings exports contain no customer/provider/master key. Check failure behavior during a staging gateway outage.
12. Rehearse rollback using protected backups; never regenerate JWT_SECRET to rotate a personal key.

`compose-evidence.json` records the completed AWS checks. `EVIDENCE.json` records the separate previous GKE/Helm checks; unsupported or untested scenarios remain explicit.

The AWS demonstration was restricted to operator/node access after unrelated invalid-key traffic filled the unfiltered log window. Filtering by the test user showed the actual request rows. No real key values or deployment identifiers are included here.
