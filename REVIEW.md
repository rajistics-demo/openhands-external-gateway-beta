# Background revision review

The November 15 background revision was independently rerun by the coordinator: 119 gateway/automation/GitLab tests passed with zero failures, errors or skips against the reviewed source and exact automation image revision. Successful backend startup, distinct owner tokens and actual dispatcher failure persistence are covered. External services are substituted and SQLite is used for status persistence; no live scheduler/webhook/provider or completion-callback round-trip is claimed. See [the validation record](docs/BACKGROUND-VALIDATION.md).

The Opus review below applies to the earlier interactive pilot baseline. It is not a new review or production approval of the background changes.

# Review and acceptance

The primary review included the pinned source, exact image/file hashes, actual PostgreSQL storage, two native SSO users, real provider inference and browser inspection. A hosted Opus 5.5 review in the same EKS task sandbox examined the current operator script, launcher/configuration and original runtime overlay against the pinned `OrgStore` source.

Opus found no release-blocking issue for one controlled staging-customer evaluation, contingent on a fresh native API launch without a profile override. Both users subsequently passed that acceptance step with exact assistant markers and no errors. The original 23 product-file hashes, current bootstrap, wrapper and Compose settings match the reviewed artifacts; see `compose-evidence.json`.

The bootstrap uses the existing three-argument admin settings validator in one locked transaction, sets both picker and native launch defaults, refuses ACP, validates the catalog alias and leaves member overrides intact. A repeated live run preserved other effective settings and member overrides. The SDK can normalize initially implicit default context metadata on first use. Activating this default resets org-level LLM tuning to the fresh selected profile; preserve custom tuning before applying it to an existing org.

This review is not a production security certification. Production SSO, HA/load, backup/restore, older-binary rollback and other gateways remain unqualified. Unsupported execution paths and the untested customer-only native denial scenario are explicit in `docs/LIMITATIONS.md`. This private handoff is owner-authorized; applicable licensing and scope are described in `DISTRIBUTION.md`.
