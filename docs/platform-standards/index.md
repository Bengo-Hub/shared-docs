# Platform Engineering Standards

The conventions every Codevertex service is expected to follow, and the shared Go libraries (`github.com/Bengo-Hub/shared-*` — `shared-events`, `shared-auth-client`, `shared-service-client`, `shared-ratelimit`, `httpware`, `cache`) that implement them. Each page below documents what's actually implemented and where — not aspirational advice — so you can go straight to the real code.

| Standard | Where it lives |
|---|---|
| [Webhooks vs Polling](webhooks-vs-polling.md) | `treasury-api/internal/http/router` webhook group |
| [Connection Pooling & PgBouncer](connection-pooling-pgbouncer.md) | `devops-k8s/manifests/databases/pgbouncer.yaml` |
| [Caching](caching.md) | `shared/cache` |
| [Idempotency & the Outbox Pattern](idempotency-and-outbox.md) | `shared/events` |
| [Resilience — Circuit Breakers & Retries](resilience-and-retries.md) | `shared/service-client` |
| [Rate Limiting](rate-limiting.md) | ingress annotations + per-service middleware |
| [Service-to-Service (S2S) Conventions](s2s-conventions.md) | `shared/auth-client` |
| [Secrets Management](secrets-management.md) | `devops-k8s/scripts/infrastructure/create-service-secrets.sh` |
| [Observability](observability.md) | `shared/httpware` (logging), `shared/service-client` (tracing) |
| [AI Integrations & pgvector](ai-and-pgvector.md) | `shared/infrastructure/{pgvector,ollama,onnx}` |
| [N+1 Queries & Preloading](n-plus-one-queries.md) | Ent's generated `.IDIn()`/eager-load |

Each page below describes the pattern as it exists today, grounded in the actual code and infrastructure rather than aspirational design docs.
