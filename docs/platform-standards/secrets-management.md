# Secrets Management

## Platform-level secrets

Every service's runtime secrets (database credentials, signing keys, the shared service-to-service
key) are Kubernetes Secrets produced from SealedSecrets kept in the devops-k8s repository. A
SealedSecret is encrypted with the cluster's public key and can only be decrypted inside the
cluster, under its own name and namespace, so the encrypted file is safe to keep in git. Git is the
single source of truth: the cluster's Secrets are always rebuilt from it, and nothing edits a live
Secret directly.

`devops-k8s/scripts/infrastructure/create-service-secrets.sh` provisions a service's Secret on every
deploy. It is generate-or-preserve: required keys are created when absent and never overwritten once
set, so re-running it is safe. When it has something new to store, it seals the whole Secret and
commits the encrypted file; when nothing changed it does nothing. For a new service it points
`POSTGRES_URL` at PgBouncer, adds `POSTGRES_MIGRATE_URL` on the direct PostgreSQL connection for
migrations, and derives `DB_NAME` and `DB_USER` from the service name. See
[Connection Pooling & PgBouncer](connection-pooling-pgbouncer.md).

Shared values (the service-to-service key, the platform database and Redis password, object storage
credentials) have one source each and are sealed into every namespace that needs them by one
script, so a rotation is a single commit followed by restarting the listed workloads.

The keys that decrypt SealedSecrets are backed up daily, encrypted, to offsite storage, and a
recovery drill proves the backup opens the newest files.

**New service checklist:** let `create-service-secrets.sh` create the Secret on the first deploy;
add any extra key with `scripts/sealing/seal-keys.sh`; never commit a plain `Secret` manifest or add
a key with `kubectl patch`.

## Tenant-level secrets

Tenant-scoped credentials — payment gateway API keys, backup destination credentials — are handled differently from platform secrets: they're encrypted at rest in each service's own database, using a platform-owner-configurable encryption key. Key resolution is DB-first with an environment-variable fallback, and decryption supports multiple keys at once so rotating the active key never orphans data encrypted under a previous one. Keys themselves are never returned in API responses or logged — only a fingerprint (a hash of the key) is ever exposed, to confirm which key is active without revealing it.

This is a separate mechanism from platform-level Kubernetes Secrets above — don't conflate the two. Platform secrets are how a service authenticates to its own infrastructure (its database, its S2S peers); tenant secrets are how a service stores a *customer's* third-party credentials safely.
