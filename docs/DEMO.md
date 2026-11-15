# Walkthrough plan

The hosted evaluation and its test data are being kept intact for the requested walkthrough. Connection details and credentials belong only in the private operator handoff; they are not in this package.

1. Sign in as the regular Susan fixture and open the completed packaged-default conversation. Show the exact `PACKAGED_COMPOSE_OK` reply, selected Haiku profile and Usage panel.
2. Open the original multi-step conversation. Show Haiku tool execution, the Sonnet reply, profile switching and conversation token/cost totals.
3. In customer LiteLLM, open the virtual-key and internal-user views. Show separate Susan/David spend, Susan’s $1 user budget and allowed models. The budget is attached to the user, so rotating a key does not reset it.
4. Filter request logs by Susan. Show real model/cost/key-alias attribution and the recorded budget denial. Susan’s replacement-key rows prove rotation; the old key was revoked.
5. If repeating denial live, use only this synthetic staging user, temporarily lower its budget below accumulated spend, run a native query, then restore the original budget and verify recovery. Keep production keys and budgets out of the walkthrough.
6. Demonstrate the shared catalog’s Opus entry and explain call-time restrictions. Both relay denial and a separate direct LiteLLM denial were verified; do not claim the untested customer-only native denial path.
7. Review setup, rollback, licensing/distribution status and production gaps before deciding the customer trial scope.

Leave the demo running afterward. Standard idle sandboxes may pause and resume when opened; their persistent state is retained. Do not delete volumes, rotate JWT_SECRET, revoke the active demo key or remove the temporary IdP client as cleanup before the walkthrough.
