# From two gateways to an Enterprise relay

This comparison describes the earlier proposed two-gateway integration and the delivered beta. It does not claim that every stock OpenHands deployment has the same routing configuration.

```mermaid
flowchart LR
  subgraph Before[Earlier two-gateway proposal]
    direction TB
    S1[Sandbox: OpenHands token] --> L1[Bundled OpenHands LiteLLM + identity hook]
    K1[(Encrypted member credential)] --> L1
    L1 --> C1[Customer LiteLLM: budget and model ACL]
    C1 --> P1[Provider]
  end
  subgraph After[Delivered optional relay]
    direction TB
    S2[Sandbox: scoped OpenHands token] --> R2[Relay inside Enterprise]
    K2[(Encrypted member credential)] --> R2
    R2 --> C2[Customer LiteLLM: budget and model ACL]
    C2 --> P2[Provider]
  end
```

Both designs keep the customer virtual key server-side. The beta replaces the bundled gateway/hook with an embedded relay and disables bundled LiteLLM. Customer model access, budgets and spend stay in the customer's gateway. There are no SDK or frontend source changes.

## Identity and rotation

```mermaid
sequenceDiagram
  participant O as Operator
  participant D as Enterprise encrypted database
  participant S as Sandbox
  participant R as Enterprise relay
  participant G as Customer LiteLLM
  O->>D: Import existing key for native org + user UUID
  S->>R: Inference with scoped OpenHands token
  R->>D: Verify current membership/policy and resolve credential
  D-->>R: Member credential (server-side decryption)
  R->>G: Chat completion with member virtual key
  G-->>R: Response or model/budget denial
  R-->>S: Response or bounded error
  O->>D: Replace key for same org + user UUID
  Note over D,G: Replacement stays with the same LiteLLM user/budget owner
```

The stable identity is the existing native SSO-backed account, not the key string. The database stores keys using the application's encryption service. Authorized server/database/encryption-secret administrators remain trusted; encryption does not protect against compromise of the application server. The sandbox can use its scoped inference token, so a stolen token is still a limited inference credential until expiry/revocation checks apply. This feature does not add an egress firewall or eliminate prompt-injection risks.

[Exact endpoints and permissions](API-PERMISSIONS.md) · [Code map](CODE-MAP.md) · [Setup](SETUP.md) · [Limitations](LIMITATIONS.md)
