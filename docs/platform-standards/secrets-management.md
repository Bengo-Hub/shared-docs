# Secrets Management

## Status: plain Kubernetes Secrets — a real gap vs. best practice, not yet remediated

Every service's secrets are plain, imperatively-created Kubernetes `Secret` objects — `devops-k8s/scripts/infrastructure/create-service-secrets.sh` runs `kubectl create secret generic ...` directly, and the Helm chart has a corresponding `charts/app/templates/secrets.yaml`. A live cluster check (2026-08) found **zero** SealedSecrets or ExternalSecrets CRDs installed anywhere in the cluster.

**What this means in practice:** secret *values* are not tracked in git (correctly — never put a real secret in a tracked file, see the project's own `feedback_no_secrets_in_code` rule), but they're also not reconstructable purely from GitOps state — a secret exists only because someone ran the creation script against the live cluster, and there's no encrypted-in-git record of what should exist. If a namespace or secret is accidentally deleted, recovery depends on someone re-running the provisioning script with the right values, not `kubectl apply` from git.

## Current per-service pattern (works, but is the thing being flagged as a gap)

`create-service-secrets.sh` is "generate-or-preserve": it creates required keys if absent, never overwrites an existing value, and defaults new services to `pgbouncer.infra.svc.cluster.local:6432` for `POSTGRES_URL` and derives `DB_NAME`/`DB_USER` from the service name automatically (see [Connection Pooling & PgBouncer](connection-pooling-pgbouncer.md)) — this part works well and needs no change.

## Tenant-level secrets (a different, already-solved problem)

Tenant-scoped credentials (payment gateway API keys, backup destination credentials) are **not** stored as Kubernetes Secrets — they're encrypted at rest in each service's database via a platform-owner-configurable encryption key, resolved DB-first then env-fallback, with multi-key backward-compatible decryption so key rotation never orphans existing data. This pattern is solid and is a separate concern from the platform-level Kubernetes Secrets gap described above — don't conflate the two when reasoning about "secrets management" on this platform.

## Recommended remediation (not yet started — proposed, needs sign-off)

Adopt either [External Secrets Operator](https://external-secrets.io/) or [Sealed Secrets](https://github.com/bitnami-labs/sealed-secrets) — ArgoCD is already the GitOps engine in use, so either integrates cleanly. This is flagged as a "must-have" gap in the platform best-practices audit; it has not been implemented and should not be treated as done until it lands as an explicit, signed-off infra change (this is a genuine blast-radius change to how every service gets its credentials — not something to roll out casually).
