# Secrets Management

## Platform-level secrets

Every service's runtime secrets (database credentials, API keys, signing keys) are provisioned as Kubernetes Secrets via `devops-k8s/scripts/infrastructure/create-service-secrets.sh`. The script is "generate-or-preserve": it creates required keys if they're absent and never overwrites an existing value, so re-running it is always safe. For a new service, it defaults `POSTGRES_URL` to point at PgBouncer (`pgbouncer.infra.svc.cluster.local:6432`) and derives `DB_NAME`/`DB_USER` from the service name automatically — see [Connection Pooling & PgBouncer](connection-pooling-pgbouncer.md).

**New service checklist:** run `create-service-secrets.sh <service-name>` (or use the standard ArgoCD template, which references it) rather than hand-crafting a Secret manifest. This keeps every service's secret provisioning consistent and means the defaults above are applied automatically.

## Tenant-level secrets

Tenant-scoped credentials — payment gateway API keys, backup destination credentials — are handled differently from platform secrets: they're encrypted at rest in each service's own database, using a platform-owner-configurable encryption key. Key resolution is DB-first with an environment-variable fallback, and decryption supports multiple keys at once so rotating the active key never orphans data encrypted under a previous one. Keys themselves are never returned in API responses or logged — only a fingerprint (a hash of the key) is ever exposed, to confirm which key is active without revealing it.

This is a separate mechanism from platform-level Kubernetes Secrets above — don't conflate the two. Platform secrets are how a service authenticates to its own infrastructure (its database, its S2S peers); tenant secrets are how a service stores a *customer's* third-party credentials safely.
