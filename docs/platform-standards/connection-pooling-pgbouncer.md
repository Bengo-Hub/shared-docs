# Connection Pooling & PgBouncer

## Status: implemented fleet-wide

Every application service connects through a shared **PgBouncer** instance (`pgbouncer.infra.svc.cluster.local:6432`, transaction-pooling mode) in the `infra` namespace, not directly at Postgres (`postgresql.infra.svc.cluster.local:5432`). This was migrated 2026-04-16 and dropped raw Postgres client connections from ~50 to ~19, with 2000-client capacity on the pooler side.

Full detail, the exact service list, and the rollback procedure: `devops-k8s/docs/pgbouncer-migration-2026-04-16.md`. Per-service DB/user map and admin scripts live in the team's internal ops runbook (not published here, since it includes prod-access commands).

## How auth works

PgBouncer uses `auth_query` against a `pgbouncer.user_lookup` Postgres function that dynamically validates each service's SCRAM password hash from `pg_shadow` — there's no static `userlist.txt` to maintain per user.

## The one thing every service must get right: migrations bypass the pool

PgBouncer's transaction-pooling mode is **incompatible with some DDL** — you'll see `ERROR: cannot run inside a transaction block` or `prepared statement already exists`. Every service's migrate path needs a **separate** `POSTGRES_MIGRATE_URL` pointed at the direct Postgres host:port (`postgresql.infra.svc.cluster.local:5432`), while the app's normal traffic (`POSTGRES_URL`) stays pointed at PgBouncer (`pgbouncer.infra.svc.cluster.local:6432`). `devops-k8s/scripts/infrastructure/create-service-secrets.sh` sets both correctly for new services by default — don't hand-roll this.

## New service checklist

1. Add the service via `create-service-secrets.sh <service-name>` (or the normal ArgoCD template) — it points `POSTGRES_URL` at PgBouncer and `POSTGRES_MIGRATE_URL` at direct Postgres automatically. Don't invent a third connection string convention.
2. If your service isn't Go (the fleet also has a Python/FastAPI+SQLAlchemy service and a .NET/Npgsql one), the *host:port* convention is identical, just the env var name may differ per stack (`ConnectionStrings__DefaultConnection` for .NET, for example) — check `pgbouncer-migration-2026-04-16.md`'s service table for your stack's exact key name before inventing a new one.
3. Client-side connection-pool tuning (`SetMaxOpenConns`, etc.) is **not** currently used anywhere in the fleet — pooling is handled entirely by PgBouncer. Don't add client-side pool limits without checking this stays true; two pooling layers fighting each other can cause more problems than one.
