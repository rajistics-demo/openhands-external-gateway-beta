# Automations and GitLab resolver workflows

> Update: [isolated live Compose results](BACKGROUND-LIVE-RESULTS.md) now verify native prompt automations and a GitHub issue resolver. The source-test results below remain historical; live GitLab delivery is still unverified.

The beta admits native app-started automation and resolver conversations to the same server-side credential binder as interactive conversations. Personal customer keys stay encrypted in Enterprise; the sandbox gets a scoped OpenHands inference token. This adds no customer LiteLLM administration permissions and no SDK/frontend source changes.

## Which person's key is used?

| Workflow | Identity and budget owner |
|---|---|
| Scheduled native automation | The automation definition's OpenHands user and organization (`automation.user_id` / `org_id`). |
| Manual or event-triggered native automation | The same definition owner. An external event actor does **not** automatically become the inference/budget owner. |
| New GitLab resolver issue/MR conversation | The GitLab actor's existing mapped native OpenHands account, in the organization selected by existing resolver routing. |
| Service-account owner | Refused in this beta; no borrowing another person's credential. |
| Missing, disabled or invalid mapping | Refused; no shared-key fallback. |

Automation ownership follows the existing automation service contract. Its normal internal per-user OpenHands API-key mechanism remains in use; those application API keys are separate from the customer's LiteLLM virtual keys. The integration does not create customer gateway keys or infer a developer from an arbitrary event header.

The policy is organization-scoped. Existing personal-workspace and repository-claim routing behavior is preserved. Configure the intended repository's organization claim and confirm the resolved organization; this feature does not apply one organization's gateway policy to every workspace in an installation.

## Supported beta paths

Use native prompt/plugin automations that start their conversation through the Enterprise app server and attach the runner to it. Automation 1.32.1's `CloudSandboxBackend.start_conversation` supplies the existing run sandbox and `trigger=automation`; Enterprise binds the LLM before the sandbox executes it. GitLab resolver conversations use the same binder with `trigger=resolver`.

The common app-started launch/binding contract is tested; custom plugin loading is not separately qualified. Arbitrary custom/legacy scripts that construct their own LLM or rely on an unseeded standalone `CloudWorkspace.get_llm` remain outside this qualification. ACP, Responses API, warm backends and service-account execution remain gated. Other integration providers sharing a trigger are not newly claimed as qualified.

## Set up a staging check

1. Follow [SETUP.md](SETUP.md) for a fresh evaluation and import a restricted key for each intended human owner/actor. Select a permitted keyless default model.
2. Keep the normal automation service configured. The gateway Compose overlay now inherits the stock `AUTOMATION_EVENT_FORWARDING_ENABLED=true`; it no longer forces event forwarding off. Deploy this configuration only in your authorized staging environment.
3. Create a native prompt automation as a mapped regular member. Use a harmless task such as writing and reading a marker file. Run it manually, then through the intended schedule/event. Confirm which definition owns it.
4. Verify the run/conversation succeeds and the customer gateway ledger attributes inference to that owner. Test another member's separate automation to check isolation.
5. For GitLab, connect each test actor's existing GitLab identity through normal OpenHands administration, configure the repository's organization routing, then exercise an issue and an MR in an authorized test project. Check the native actor/org and gateway attribution. Repository access, webhook authentication and permission to post GitLab results remain normal setup requirements.
6. Test a denied model and an exhausted staging budget. Confirm failure with no alternate credentials. Restore the budget and verify recovery. Check the final automation run status, not just the conversation start response.
7. Rotate an owner's customer key under the same customer user/budget owner, import it against the same native UUID, and verify a new request. Also check a run that lasts beyond token expiry and the intended gateway outage/recovery behavior.

Do not use a production GitLab project or send external test messages without the appropriate authorization. The above is an operator acceptance checklist, not a statement that live external tests were already run for your installation.

## Evidence and its limits

The coordinator independently reran **119 tests with zero failures, errors or skips** against Enterprise 1.92.0, SDK/workspace 1.62.0 and the automation image's exact source revision. The tests cover the real GitLab caller/context, the real automation backend request and successful startup, distinct owner token claims, denial propagation, and the real dispatcher persisting a launch refusal as FAILED. The dispatcher success test reaches command execution. SQLite tests verify terminal status persistence and stale-write protection.

External HTTP, provisioning, application API-key minting and script execution are substituted in these tests. SQLite is a real stand-in database engine; this is not PostgreSQL or a live customer deployment qualification. The actual entrypoint completion-callback HTTP round-trip, live GitLab webhook delivery/posting, scheduler timing, live background provider spend, long-running refresh and customer IdP/network need the staging checks above. Earlier live two-user inference/budget/rotation evidence is the separate baseline in [compose-evidence.json](../compose-evidence.json), not a new live background run.

The production change is limited to admitting two launch triggers through the existing binder; the Compose change restores normal event forwarding. [Validation details](BACKGROUND-VALIDATION.md), [design decisions](DESIGN-DECISIONS.md) and [engineering handoff](ENGINEERING-HANDOFF.md) preserve the review trail.
