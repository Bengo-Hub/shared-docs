# Observability

## Status: logging and basic tracing exist; metrics/dashboards/alerting do not — this is the platform's single biggest infrastructure gap

## What exists today

- **Structured logging:** `shared/httpware` provides `Logging(log *zap.Logger)` middleware (method, path, status, duration, request_id, tenant_id, tenant_slug, outlet_id as structured fields) and `Recover(log *zap.Logger)` for panic recovery with a structured stack trace. `shared/cache` and `shared/service-client` also use `zap` consistently. If you're adding logging to a new service, use `zap` via `shared/httpware` — don't introduce a different logging library.
- **Basic distributed tracing:** `shared/service-client` creates an OpenTelemetry span around every outbound S2S call (method, URL, service name, status/error), and `X-Request-ID` propagation via `shared/httpware` gives basic request correlation across services even without full span propagation everywhere. See [Resilience — Circuit Breakers & Retries](resilience-and-retries.md).
- **A `ServiceMonitor` Helm template** (`devops-k8s/charts/app/templates/servicemonitor.yaml`) that would let Prometheus Operator scrape a `/metrics` endpoint every 30s per app — this exists in the chart and is wired via Helm values, but as of this writing **nothing consumes it**, because:

## What doesn't exist: the metrics/dashboards/alerting stack itself

A live cluster inspection (2026-08, `kubectl get pods -A`) found **zero** Prometheus, Grafana, Loki, Jaeger, Tempo, or OpenTelemetry Collector pods anywhere in the cluster. There is no metrics dashboard, no log aggregation, no distributed-tracing backend, and no alerting. Several documented production incidents (in the project's `.claude/memory/` incident write-ups) were diagnosed via raw `kubectl logs`/`kubectl exec psql` rather than a dashboard, purely because no dashboard exists to check first.

Individual services do implement their own `promhttp`/metrics endpoints independently (e.g. treasury-api) — this is the same "duplicated per service instead of a shared package" pattern seen in [Rate Limiting](rate-limiting.md); there's no `shared/metrics` helper.

## Recommended remediation (not yet started — proposed, needs sign-off)

Deploy `kube-prometheus-stack` (Prometheus + Grafana + Alertmanager) wired to the already-existing `ServiceMonitor` template, plus Loki for log aggregation. This is flagged as the platform's top "must-have" gap in the best-practices audit. Like [Secrets Management](secrets-management.md), this is a real infra change with real blast radius (new cluster-wide workloads, resource consumption on an already-provisioned node) and should land as an explicit, reviewed rollout — not something to stand up quietly as a side effect of unrelated work.

## In the meantime

Until the stack above exists, rely on: `kubectl logs`/`kubectl get events`/`kubectl top pods` for live diagnosis, and the structured `zap` fields already emitted by every service (tenant_id, request_id) to correlate a specific request across services by grepping logs, since there's no tracing backend to click through yet.
