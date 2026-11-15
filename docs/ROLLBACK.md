# Rollback and recovery

Before rollout, protect a consistent database backup, `.env.generated-secrets`, deployment configuration and prior org model profiles. The persistent JWT_SECRET is needed to decrypt stored credentials. Backups contain sensitive data and belong outside source control.

For a new evaluation, `./evaluate down` stops the application services without deleting volumes. If you used the optional fixture, use `--demo` consistently. Avoid `--volumes` unless intentionally deleting disposable data.

For an existing installation, restore the previous application image/configuration and previous model profiles as one reviewed rollback. Set `CUSTOMER_GATEWAY_ENABLED=false` or omit the opt-in overlay. This does not automatically configure an alternative inference provider; relay-bound profiles/tokens will stop working while the relay is disabled.

Migration 216 is additive. Its tested downgrade preserves the gateway tables and encrypted keys rather than deleting them, and re-upgrade is idempotent. Older-binary rollback was not live-rehearsed. Verify it on staging for your exact release before production use.

To rotate a member’s LiteLLM key, use the operator `set-key` command with the same org/user UUID and appropriate model policy. Keep the key attached to the same customer LiteLLM user for budget continuity. **Do not change JWT_SECRET, recreate users or reinitialize the database for personal-key rotation.**
