# Observability

## Structured logging

Every service uses `zap` via `shared/httpware`, which provides a `Logging(log *zap.Logger)` middleware (method, path, status, duration, and structured fields for `request_id`, `tenant_id`, `tenant_slug`, `outlet_id`) and a `Recover(log *zap.Logger)` panic-recovery middleware that logs a structured stack trace instead of crashing the process. `shared/cache` and `shared/service-client` also log through `zap`. If you're adding logging to a new service, use `zap` via `shared/httpware` rather than introducing a different logging library — consistency here is what makes cross-service log correlation possible.

## Request correlation

`shared/httpware` propagates an `X-Request-ID` header across service calls, and `shared/service-client` wraps every outbound S2S call in an OpenTelemetry span (method, URL, service name, status/error) — see [Resilience — Circuit Breakers & Retries](resilience-and-retries.md). Together, these let you trace a single request's path across multiple services by grepping the structured log fields for its `request_id` or `tenant_id`, even without a full tracing UI to click through.

## Metrics

Services that expose `/metrics` (e.g. treasury-api, via `promhttp`) do so independently today — there's no shared instrumentation helper yet, so if you're adding metrics to a new service, expect to wire up `promhttp` yourself following an existing example rather than importing a shared package. The Helm chart (`devops-k8s/charts/app/templates/servicemonitor.yaml`) includes a `ServiceMonitor` template so a service's metrics endpoint can be scraped once a metrics-collection stack is pointed at it.

## Debugging without a dashboard

Day to day, `kubectl logs`, `kubectl get events`, and `kubectl top pods` remain the fastest way to check what's happening in a specific pod, combined with grepping the structured `zap` fields (`tenant_id`, `request_id`) to correlate a request across services.
