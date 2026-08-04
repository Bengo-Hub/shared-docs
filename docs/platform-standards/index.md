# Platform Engineering Standards

The conventions every Codevertex service is expected to follow, and the shared Go libraries (`d:\Projects\Codevertex\shared\`) that implement them. Each page below documents what's actually implemented and where — not aspirational advice — so you can go straight to the real code.

| Standard | Status | Shared library |
|---|---|---|
| [Webhooks vs Polling](webhooks-vs-polling.md) | Implemented for payments; audit recommended elsewhere | `treasury-api/internal/http/router` webhook group |
| [Connection Pooling & PgBouncer](connection-pooling-pgbouncer.md) | Implemented fleet-wide | `devops-k8s/manifests/databases/pgbouncer.yaml` |
| [Caching](caching.md) | Implemented, reusable | `shared/cache` |
| [Idempotency & the Outbox Pattern](idempotency-and-outbox.md) | Implemented, reusable — but has a sharp edge | `shared/events` |
| [Resilience — Circuit Breakers & Retries](resilience-and-retries.md) | Implemented, reusable | `shared/service-client` |
| [Rate Limiting](rate-limiting.md) | Implemented per-service (duplicated) + ingress-level | no shared package yet — a real gap |
| [Service-to-Service (S2S) Conventions](s2s-conventions.md) | Implemented, but has a recurring footgun | `shared/auth-client` |
| [Secrets Management](secrets-management.md) | Plain Kubernetes Secrets — a real gap vs. GitOps best practice | `devops-k8s/scripts/infrastructure/create-service-secrets.sh` |
| [Observability](observability.md) | Structured logging + tracing exist; metrics/dashboards/alerting do not — the platform's biggest gap | `shared/httpware` (logging), `shared/service-client` (tracing) |
| [AI Integrations & pgvector](ai-and-pgvector.md) | Infrastructure scaffolded, one production consumer (marketflow-ai) | `shared/infrastructure/{pgvector,ollama,onnx}` |
| [N+1 Queries & Preloading](n-plus-one-queries.md) | Handled via Ent idioms at hot paths, no shared abstraction needed | Ent's generated `.IDIn()`/eager-load |

This section came out of a 2026-08 cross-service best-practices audit (live prod cluster inspection + shared library scan). Where something is a genuine gap rather than "not yet documented," the page says so explicitly and links to the [Gap Analysis & Remediation Plan](gap-analysis-and-remediation-plan.md) rather than pretending the gap doesn't exist.
