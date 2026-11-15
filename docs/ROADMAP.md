# Current scope and next validation steps

## Working evaluation

Two regular SSO members in one organization completed native conversations through their own server-side customer keys. Real Haiku/Sonnet inference, tool execution, positive key/user spend attribution, budget denial/recovery, model denial, key rotation and UI usage were observed. The Docker Compose build and launcher were exercised on a dedicated Linux amd64 host. The initial setup uses an operator CLI, not a key-management UI.

## Human-owned background workflows

Native app-started automation and GitLab resolver launches are admitted through the existing binder. A coordinator rerun passed 119 gateway/automation/GitLab tests against exact source pins. The automation backend returns a ready conversation, owner tokens stay distinct, and the actual dispatcher persists a launch refusal as FAILED in SQLite.

Automations use the definition's native user/org; new GitLab resolver conversations use the existing mapped actor and resolved org. There is no automatic external-event-actor identity synchronization. Service accounts remain separate.

The next acceptance step is the customer's authorized live staging workflow: scheduler/webhook delivery, repository permissions, provider spend attribution, model/budget denials after startup, long-running refresh, rotation, outage/recovery and the entrypoint completion-callback HTTP leg. These were not live-run by the new source tests. See [ownership and setup](BACKGROUND-WORKFLOWS.md).

## Service accounts

A service account needs an explicit assigned gateway credential and budget owner. Decide that policy and test it separately; do not silently charge a triggering developer or fall back to a shared key. The current credential store/guards refuse this path.

## Production and other gateways

Production qualification still needs the customer's IdP and network, HA/load/soak, backup/restore with the persistent encryption secret, and older-binary rollback. The package adds no sandbox egress firewall or distributed budget reservation system.

Bifrost and Portkey are future compatibility targets. The gateway profile isolates protocol/header/model mapping, but neither product is claimed supported until real end-to-end tests pass. Only the OpenAI chat-completions protocol is implemented in this snapshot.

For the rationale and reviewable production acceptance stages, see [Design decisions](DESIGN-DECISIONS.md) and [Engineering handoff](ENGINEERING-HANDOFF.md).
