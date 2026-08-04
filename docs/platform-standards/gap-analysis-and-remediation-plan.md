# Best-Practices Gap Analysis & Remediation Plan

Compiled 2026-08 from a live prod cluster inspection (`ssh mss-prod` / `kubectl`) plus a targeted scan of `shared/` and `devops-k8s/`, checked against a general best-practices reference spanning codebase, deployment, scalability, security, and performance. This page is the single compiled list — the individual [Platform Engineering Standards](index.md) pages link back here for the specific gaps they call out. **Nothing on the "confirmed gaps" list below has been implemented as part of this audit** — this is a gap analysis and proposed task list for sign-off, not a changelog. Prod-infrastructure changes carry real blast radius and should be reviewed and approved individually before work starts, per the [risk-confirmation norm](../index.md) this documentation set follows.

## Confirmed working well (no action needed — documented for completeness)

| Practice | Evidence |
|---|---|
| Connection pooling | PgBouncer, fleet-migrated — [detail](connection-pooling-pgbouncer.md) |
| Circuit breakers & retries | `shared/service-client` (`gobreaker` + `cenkalti/backoff`) — [detail](resilience-and-retries.md) |
| Idempotency & outbox | `shared/events` — [detail](idempotency-and-outbox.md) |
| Caching | `shared/cache` cache-aside pattern — [detail](caching.md) |
| Autoscaling & health probes | HPA + VPA + KEDA + PodDisruptionBudgets, mature Helm chart, fleet-wide (min 2 replicas is the platform HA standard) |
| Ingress-level rate limiting | Per-service `limit-rps`/`limit-connections` nginx annotations |
| Structured logging | `zap` via `shared/httpware`, consistent fleet-wide |
| DB migrations | Ent + Atlas versioned-migration convention — [detail](../architecture/go-backend-ent-atlas-migrations.md) |
| N+1 mitigation | Ent's `.IDIn()` batch-loading idiom at hot paths — [detail](n-plus-one-queries.md) |
| TLS | cert-manager with `letsencrypt-prod`/`staging` issuers |
| Webhooks for payments | treasury-api's `/api/v1/webhooks` group — [detail](webhooks-vs-polling.md) |

## Confirmed gaps — prioritized remediation task list (proposed, needs sign-off per item)

### Must-have

1. **No observability stack.** Zero Prometheus/Grafana/Loki/tracing-backend pods anywhere in the cluster, despite an unused `ServiceMonitor` Helm template already wired up. **Proposed:** deploy `kube-prometheus-stack` + Loki. See [Observability](observability.md) for full detail. *Highest-priority gap — several past incidents were diagnosed blind, via raw `kubectl logs`, purely because no dashboard exists.*
2. **Secrets are plain Kubernetes Secrets, not GitOps-tracked.** No SealedSecrets/ExternalSecrets CRDs installed; secret existence depends on someone having run a provisioning script against the live cluster, with no encrypted-in-git record. **Proposed:** adopt External Secrets Operator or Sealed Secrets (ArgoCD is already in use, either integrates cleanly). See [Secrets Management](secrets-management.md).
3. **No HA on Postgres, Redis, or PgBouncer.** All three run as a single replica in prod. Multiple prior production incidents (documented in the project's own memory) already trace back to this layer. **Proposed:** at minimum, formally document the accepted risk; ideally plan Postgres streaming replication. Not started.
4. **Rate-limiting logic duplicated per-service instead of centralized.** Two independently-built implementations (treasury-api, notifications-api) doing overlapping work. **Proposed:** extract a `shared/ratelimit` package. See [Rate Limiting](rate-limiting.md).

### Good-to-have

5. **No `shared/metrics` package** — each service that does implement `/metrics` does so independently, the same "solved twice" pattern as rate limiting. Depends on item 1 landing first (no point centralizing instrumentation for a stack nothing scrapes yet).
6. **No formal API-versioning/deprecation strategy** beyond the fixed `/api/v1/` convention — fine today, but there's no tooling or process for introducing a breaking `/v2` when the platform eventually needs one.
7. **CDN does TLS/IP-preservation only, no asset caching.** Cloudflare sits in front of `*.codevertexafrica.com` for latency (Kenya↔origin RTT) and IP preservation, but no `Cache-Control` headers or CDN-level asset caching were found in any ingress config. Lower urgency — the POS-load-speed work already shipped gzip + client-side cache-first fixes that addressed the original symptom this would have targeted.

### Explicitly out of scope for this pass — flagged for a future, separate audit

WAF/DDoS protection, blue-green/canary rollout policy (ArgoCD's sync policy specifically wasn't audited), chaos engineering, multi-region/DR beyond the existing tenant-scoped backup CronJobs, feature flags as a formal system, SLO/SLI/error-budget practice, cost optimization. These came from the reference best-practices checklist this audit was run against, but weren't part of this pass's targeted scan — don't assume they're fine just because they're not listed as a confirmed gap above.

## How to action this list

Each numbered item above is independent and should be scoped, reviewed, and approved on its own — this list is deliberately a menu, not a bundled project. If you're picking one up, start by re-verifying the gap still exists (this audit is a point-in-time snapshot) before scoping the fix.
