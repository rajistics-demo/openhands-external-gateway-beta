# Current scope and next validation steps

## Working evaluation

Two regular SSO members in one organization completed native conversations through their own server-side customer keys. Real Haiku/Sonnet inference, tool execution, positive key/user spend attribution, budget denial/recovery, model denial, key rotation and UI usage were observed. The Docker Compose build and launcher were exercised on a dedicated Linux amd64 host. The initial setup uses an operator CLI, not a key-management UI.

## Human-owned background workflows

Automations and GitLab resolver launches remain gated in this snapshot. This is the current preview's scope restriction. Where those workflows already identify a human OpenHands user, the intended next step is to reuse that established identity and resolve that member's key through the same relay. This does not require inventing another identity system. An actor without an OpenHands account does not gain an account or credential through this integration.

Before lifting each guard, validate the actual launch path, correct owner/trigger identity, organization membership, model/budget enforcement, auxiliary calls, token refresh, rotation and negative/no-fallback cases. Preserve the existing failure behavior for unmapped actors. Do not infer success from the interactive-conversation tests.

## Service accounts

A service account needs an explicit assigned gateway credential and budget owner. Decide that policy and test it separately; do not silently charge a triggering developer or fall back to a shared key. The current credential store/guards refuse this path.

## Production and other gateways

Production qualification still needs the customer's IdP and network, HA/load/soak, backup/restore with the persistent encryption secret, and older-binary rollback. The package adds no sandbox egress firewall or distributed budget reservation system.

Bifrost and Portkey are future compatibility targets. The gateway profile isolates protocol/header/model mapping, but neither product is claimed supported until real end-to-end tests pass. Only the OpenAI chat-completions protocol is implemented in this snapshot.

For the rationale and reviewable production acceptance stages, see [Design decisions](DESIGN-DECISIONS.md) and [Engineering handoff](ENGINEERING-HANDOFF.md).
