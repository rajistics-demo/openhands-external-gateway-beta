# Working in this evaluation repository

- This is an Enterprise 1.92.0 / SDK 1.62.0 staging preview. Keep the original license and preview status clear.
- Personal customer keys stay encrypted server-side. Never export them through normal sandbox secrets. The app must not acquire a customer master/admin key.
- Preserve the original source/base/overlay guards. A product change requires a corresponding patch, manifest, regression coverage and fresh real-path evidence. Do not carry earlier acceptance forward across behavior changes.
- Keep human-owned background workflow validation separate from service-account policy. Current gates must not be removed without appropriate identity/key/budget tests.
- Keep credentials, real env files, raw logs, API responses, infrastructure identifiers and recordings in an ignored private location outside tracked evidence. Publish sanitized necessary evidence only; inspect exact outgoing history and metadata before pushes.
- Repository editing does not authorize changes to running demos, customer systems, global model defaults, account permissions or invitations. Preserve the running walkthrough demo.
- This repository was explicitly authorized for initial private publication. Further external messages, public visibility changes, customer invitations and broader publication require the applicable user authorization. Do not auto-send messages or invoke review bots.
