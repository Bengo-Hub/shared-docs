# Best-Practices Gap Analysis & Remediation Plan

> **INTERNAL ONLY — do not publish.** This file lives under `shared-docs/internal/` specifically because it is not built into the public docs site (see `mkdocs.yml`'s `docs_dir`). It's the fleet-wide, centralized record of known infrastructure/architecture gaps — effectively a map of the platform's current weak points — which is exactly the kind of thing that shouldn't be handed to the public alongside the developer-facing guide content. The published [Platform Engineering Standards](../../docs/platform-standards/index.md) pages describe how each piece of infrastructure works and are safe to publish; they deliberately do NOT restate the gap analysis below. Cross-referenced from the project's own memory system — see `d:\Projects\Codevertex\.claude\memory\deferred-and-open-items.md`.

Compiled 2026-08 from a live prod cluster inspection (`ssh mss-prod` / `kubectl`) plus a targeted scan of `shared/` and `devops-k8s/`, checked against a general best-practices reference spanning codebase, deployment, scalability, security, and performance. This page is the single compiled list — the individual [Platform Engineering Standards](../../docs/platform-standards/index.md) pages used to link back here for the specific gaps they called out; that cross-linking was removed when the public pages were rewritten to be gap-free, so this file is now the only place this analysis lives. **Nothing on the "confirmed gaps" list below has been implemented as part of this audit** — this is a gap analysis and proposed task list for sign-off, not a changelog. Prod-infrastructure changes carry real blast radius and should be reviewed and approved individually before work starts.

## Confirmed working well (no action needed — documented for completeness)

| Practice | Evidence |
|---|---|
| Connection pooling | PgBouncer, fleet-migrated — [detail](../../docs/platform-standards/connection-pooling-pgbouncer.md) |
| Circuit breakers & retries | `shared/service-client` (`gobreaker` + `cenkalti/backoff`) — [detail](../../docs/platform-standards/resilience-and-retries.md) |
| Idempotency & outbox | `shared/events` — [detail](../../docs/platform-standards/idempotency-and-outbox.md) |
| Caching | `shared/cache` cache-aside pattern — [detail](../../docs/platform-standards/caching.md) |
| Autoscaling & health probes | HPA + VPA + KEDA + PodDisruptionBudgets, mature Helm chart, fleet-wide (min 2 replicas is the platform HA standard) |
| Ingress-level rate limiting | Per-service `limit-rps`/`limit-connections` nginx annotations |
| Structured logging | `zap` via `shared/httpware`, consistent fleet-wide |
| DB migrations | Ent + Atlas versioned-migration convention — [detail](../architecture/go-backend-ent-atlas-migrations.md) |
| N+1 mitigation | Ent's `.IDIn()` batch-loading idiom at hot paths — [detail](../../docs/platform-standards/n-plus-one-queries.md) |
| TLS | cert-manager with `letsencrypt-prod`/`staging` issuers |
| Webhooks for payments | treasury-api's `/api/v1/webhooks` group — [detail](../../docs/platform-standards/webhooks-vs-polling.md) |

## Confirmed gaps — prioritized remediation task list (proposed, needs sign-off per item)

### Must-have

1. ~~**No observability stack.** Zero Prometheus/Grafana/Loki/tracing-backend pods anywhere in the cluster... Proposed: deploy kube-prometheus-stack + Loki.~~ **NOT A GAP — corrected 2026-08-06.** This framing was stale against a later, deliberate decision: `devops-k8s` commits `aa18b5ca`/`402faacc` (2026-07-13) decommissioned the self-hosted kube-prometheus-stack on purpose, its own message stating "Replaced by lightweight admin-panel scripts on auth-service reading kubectl top / metrics-server directly." That is the current, intended architecture, not a resource-driven pause awaiting a re-deploy. A session that treated this line item at face value nearly re-deployed the full stack (caught before anything went live; see `deferred-and-open-items.md`'s Resolved log). **Do not propose re-deploying Prometheus/Grafana/Loki again without the user explicitly revisiting this decision first** — if a future need (e.g. monitoring a DB HA rollout) makes the lightweight approach insufficient, that's a fresh conversation with the user, not an autonomous action against this old audit line.
2. **Secrets are plain Kubernetes Secrets, not GitOps-tracked.** No SealedSecrets/ExternalSecrets CRDs installed; secret existence depends on someone having run a provisioning script against the live cluster, with no encrypted-in-git record. **Proposed:** adopt External Secrets Operator or Sealed Secrets (ArgoCD is already in use, either integrates cleanly). See [Secrets Management](../../docs/platform-standards/secrets-management.md).
3. **No HA on Postgres, Redis, or PgBouncer.** All three run as a single replica in prod. Multiple prior production incidents (documented in the project's own memory) already trace back to this layer. **Proposed:** at minimum, formally document the accepted risk; ideally plan Postgres streaming replication. Not started. **Note (2026-08-06):** if this is picked up, its "HA rollout should be monitored" premise can no longer lean on item 1 (cancelled) — check with the user whether the lightweight kubectl-top/metrics-server approach is sufficient for that, rather than assuming Prometheus is coming back to cover it.
4. ~~**Rate-limiting logic duplicated per-service instead of centralized.**~~ **DONE 2026-08-06:** extracted to `github.com/Bengo-Hub/shared-ratelimit` (`Limiter` for treasury-api's sliding-window abuse throttling, `Quota` for notifications-api's daily plan-quota metering); both services migrated. See [Rate Limiting](../../docs/platform-standards/rate-limiting.md) (updated).

### Good-to-have

5. **No `shared/metrics` package** — each service that does implement `/metrics` does so independently, the same "solved twice" pattern rate-limiting was. Previously framed as depending on item 1 (no point centralizing instrumentation for a stack nothing scrapes yet) — since item 1 is now cancelled rather than merely pending, this dependency is moot until/unless the user revisits observability; don't treat it as blocked-and-waiting.
6. **No formal API-versioning/deprecation strategy** beyond the fixed `/api/v1/` convention — fine today, but there's no tooling or process for introducing a breaking `/v2` when the platform eventually needs one.
7. **CDN does TLS/IP-preservation only, no asset caching.** Cloudflare sits in front of `*.codevertexafrica.com` for latency (Kenya↔origin RTT) and IP preservation, but no `Cache-Control` headers or CDN-level asset caching were found in any ingress config. Lower urgency — the POS-load-speed work already shipped gzip + client-side cache-first fixes that addressed the original symptom this would have targeted.

### Explicitly out of scope for this pass — flagged for a future, separate audit

WAF/DDoS protection, blue-green/canary rollout policy (ArgoCD's sync policy specifically wasn't audited), chaos engineering, multi-region/DR beyond the existing tenant-scoped backup CronJobs, feature flags as a formal system, SLO/SLI/error-budget practice, cost optimization. These came from the reference best-practices checklist this audit was run against, but weren't part of this pass's targeted scan — don't assume they're fine just because they're not listed as a confirmed gap above.

## How to action this list

Each numbered item above is independent and should be scoped, reviewed, and approved on its own — this list is deliberately a menu, not a bundled project. If you're picking one up, start by re-verifying the gap still exists (this audit is a point-in-time snapshot) before scoping the fix.
