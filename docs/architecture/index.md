# Architecture & Engineering Standards

The durable, cross-service architecture documents — how services talk to each other, how authorization composes, how events flow, and the platform-wide conventions every new service is expected to follow.

| Doc | Covers |
|---|---|
| [Microservice Architecture](microservice-architecture.md) | The master architecture reference — communication patterns, service discovery, resilience, observability, shared libraries. Start here. |
| [Trinity Authorization Pattern](trinity-authorization-pattern.md) | The three-layer authorization model: RBAC (auth-service) + Licensing (subscriptions-service) + Resources (domain services). |
| [Event Architecture](event-architecture.md) | NATS JetStream event catalog, the outbox pattern, envelope formats. |
| [SSO Integration Guide](sso-integration-guide.md) | The OIDC/PKCE login flow, JWT claim shape, JIT provisioning. |
| [Login Flow Contract](login-flow-contract.md) | Frontend-specific API signatures/route contracts for the login flow, per service. |
| [Subscription Gating Guide](subscription-gating-guide.md) | The mutations-only subscription enforcement pattern — full implementation guide (code samples). |
| [Cross-Service Data Ownership](cross-service-data-ownership.md) | The canonical data-ownership matrix — which service owns which entity, and the integration pattern for reading it from elsewhere. |
| [Go Backend — Ent + Atlas Migrations](go-backend-ent-atlas-migrations.md) | The Ent codegen + Atlas versioned-migration convention every Go service follows. |
| [DevOps-K8s Ingress & CORS](devops-k8s-ingress-cors.md) | The canonical CORS origin allowlist and NGINX ingress annotation conventions per service. |
