# Database Maintenance Procedures

Centralized database maintenance scripts for all Go microservices. All services share a single PostgreSQL instance in the `infra` namespace (`postgresql-0`).

## Connection pooling: apps go through PgBouncer, admin/DDL work bypasses it

Since the 2026-04-16 migration, every application service connects through a shared **PgBouncer** (`pgbouncer.infra.svc.cluster.local:6432`, transaction-pooling mode), not directly at `postgresql.infra.svc.cluster.local:5432` — this dropped raw Postgres client connections from ~50 to ~19 with 2000-client capacity on the pooler side. Auth is via PgBouncer's `auth_query` against a `pgbouncer.user_lookup` function (dynamic SCRAM validation against `pg_shadow` — no per-user `userlist.txt` entries needed). New services get PgBouncer-pointed secrets automatically via `scripts/infrastructure/create-service-secrets.sh`. Full detail, service list, and rollback procedure: `devops-k8s/docs/pgbouncer-migration-2026-04-16.md`.

**This matters for migrations specifically:** PgBouncer's transaction-pooling mode is incompatible with some DDL (`ERROR: cannot run inside a transaction block` / `prepared statement already exists`) — every service's migrate job needs a separate `POSTGRES_MIGRATE_URL` pointed at the **direct** Postgres host:port (see "Add postgres-migrate-url to K8s Secrets" below), while the app's own `POSTGRES_URL` stays pointed at PgBouncer. The admin scripts in this file all go through `kubectl exec` directly into the `postgresql-0` pod and run `psql` locally inside it — they never touch PgBouncer at all, which is the correct approach for admin/DDL/reset work regardless of what the apps use for their normal traffic.

> **SECURITY NOTE:** This file must never contain real passwords. Fetch the admin password
> from the K8s secret at runtime using the snippet below. If this file is ever exposed in
> git history with a real password, rotate `admin-user-password` immediately.

## Service Database Map

| Service | Namespace | Database | DB User | Deployment |
|---------|-----------|----------|---------|------------|
| auth-api | auth | auth | auth_service_user | auth-api |
| ordering-backend | ordering | ordering | ordering_user | ordering-backend |
| logistics-api | logistics | logistics | logistics_user | logistics-api |
| inventory-api | inventory | inventory | inventory_user | inventory-api |
| notifications-api | notifications | notifications | notifications_user | notifications-api |
| treasury-api | treasury | treasury | treasury_user | treasury-api |
| subscriptions-api | subscriptions | subscriptions | subscriptions_user | subscriptions-api |
| pos-api | pos | pos | pos_user | pos-api |
| projects-api | projects | projects | projects_user | projects-api |
| iot-api | iot | iot | iot_user | iot-api |
| ticketing-api | ticketing | ticketing | ticketing_user | ticketing-api |
| marketflow-api | marketflow | marketflow | marketflow_user | marketflow-api |
| marketflow-ai | marketflow | marketflow | marketflow_user | marketflow-ai (shares the marketflow DB) |
| erp-api | erp | bengo_erp | erp_user | erp-api (DB name is `bengo_erp`, not `erp` — see the ERP-decomposition memory) |
| isp-billing-backend | isp-billing | isp_billing | isp_billing_user | isp-billing-backend (Python/FastAPI + SQLAlchemy, not Go) |
| truload-backend | truload | truload | (Npgsql, .NET) | truload-backend (`ConnectionStrings__DefaultConnection`, not `POSTGRES_URL`) |

**PostgreSQL Pod:** `postgresql-0` (Namespace: `infra`)
**Admin User:** `admin_user`

## Fetch Admin Password (Required Before Running Any Script)

```bash
export PGPASSWORD=$(kubectl get secret postgresql -n infra \
  -o jsonpath='{.data.admin-user-password}' | base64 -d)
```

Run this once in your shell session before any of the scripts below. All scripts use `$PGPASSWORD`.

---

## Quick Reference Scripts

### Fix DB Ownership & Privileges (All Services)

Run this after any DB reset to ensure correct ownership and privileges:

```bash
# Fetch password first (see above)
export PGPASSWORD=$(kubectl get secret postgresql -n infra -o jsonpath='{.data.admin-user-password}' | base64 -d)

for db in ordering logistics inventory notifications treasury subscriptions pos projects iot ticketing marketflow; do
  echo "=== Fixing $db DB ownership ==="
  kubectl exec postgresql-0 -n infra -- sh -c "PGPASSWORD='$PGPASSWORD' psql -h 127.0.0.1 -U admin_user -d postgres -c \"
    ALTER DATABASE $db OWNER TO ${db}_user;
    GRANT ALL PRIVILEGES ON DATABASE $db TO ${db}_user;
  \""
  kubectl exec postgresql-0 -n infra -- sh -c "PGPASSWORD='$PGPASSWORD' psql -h 127.0.0.1 -U admin_user -d $db -c \"
    GRANT ALL ON SCHEMA public TO ${db}_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ${db}_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ${db}_user;
  \""
done
```

### Full Reset: Drop & Recreate All Service DBs (Except auth)

Use this when migrations are broken or you need a clean slate. Auth-service DB is **never** dropped.

```bash
export PGPASSWORD=$(kubectl get secret postgresql -n infra -o jsonpath='{.data.admin-user-password}' | base64 -d)

# Step 1: Scale down all Go API services
kubectl scale deployment ordering-backend -n ordering --replicas=0
kubectl scale deployment logistics-api -n logistics --replicas=0
kubectl scale deployment inventory-api -n inventory --replicas=0
kubectl scale deployment notifications-api -n notifications --replicas=0
kubectl scale deployment treasury-api -n treasury --replicas=0
kubectl scale deployment subscriptions-api -n subscriptions --replicas=0
kubectl scale deployment pos-api -n pos --replicas=0
kubectl scale deployment projects-api -n projects --replicas=0
kubectl scale deployment iot-api -n iot --replicas=0
kubectl scale deployment ticketing-api -n ticketing --replicas=0
kubectl scale deployment marketflow-api -n marketflow --replicas=0

# Step 2: Terminate sessions, drop, recreate, fix ownership
for db in ordering logistics inventory notifications treasury subscriptions pos projects iot ticketing marketflow; do
  echo "=== Resetting $db ==="
  kubectl exec postgresql-0 -n infra -- sh -c "PGPASSWORD='$PGPASSWORD' psql -h 127.0.0.1 -U admin_user -d postgres -c \"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='$db' AND pid<>pg_backend_pid();\""
  kubectl exec postgresql-0 -n infra -- sh -c "PGPASSWORD='$PGPASSWORD' dropdb -h 127.0.0.1 -U admin_user $db --if-exists && createdb -h 127.0.0.1 -U admin_user $db"
  kubectl exec postgresql-0 -n infra -- sh -c "PGPASSWORD='$PGPASSWORD' psql -h 127.0.0.1 -U admin_user -d postgres -c \"
    ALTER DATABASE $db OWNER TO ${db}_user;
    GRANT ALL PRIVILEGES ON DATABASE $db TO ${db}_user;
  \""
  kubectl exec postgresql-0 -n infra -- sh -c "PGPASSWORD='$PGPASSWORD' psql -h 127.0.0.1 -U admin_user -d $db -c \"
    GRANT ALL ON SCHEMA public TO ${db}_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ${db}_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ${db}_user;
  \""
  echo "=== $db reset complete ==="
done

# Step 3: Scale up all services (auto-migrate + seed on startup)
kubectl scale deployment ordering-backend -n ordering --replicas=1
kubectl scale deployment logistics-api -n logistics --replicas=1
kubectl scale deployment inventory-api -n inventory --replicas=1
kubectl scale deployment notifications-api -n notifications --replicas=1
kubectl scale deployment treasury-api -n treasury --replicas=1
kubectl scale deployment subscriptions-api -n subscriptions --replicas=1
kubectl scale deployment pos-api -n pos --replicas=1
kubectl scale deployment projects-api -n projects --replicas=1
kubectl scale deployment iot-api -n iot --replicas=1
kubectl scale deployment ticketing-api -n ticketing --replicas=1
kubectl scale deployment marketflow-api -n marketflow --replicas=1

# Step 4: Wait for rollout
for svc_ns in "ordering-backend:ordering" "logistics-api:logistics" "inventory-api:inventory" "notifications-api:notifications"; do
  SVC=${svc_ns%%:*}; NS=${svc_ns##*:}
  kubectl rollout status deployment/$SVC -n $NS --timeout=180s
done
```

### Reset a Single Service DB

```bash
export PGPASSWORD=$(kubectl get secret postgresql -n infra -o jsonpath='{.data.admin-user-password}' | base64 -d)

SERVICE=ordering          # Change to: logistics, inventory, notifications, treasury, etc.
NAMESPACE=$SERVICE
DEPLOYMENT="${SERVICE}-api"  # Adjust: ordering uses "ordering-backend"

kubectl scale deployment $DEPLOYMENT -n $NAMESPACE --replicas=0
kubectl exec postgresql-0 -n infra -- sh -c "PGPASSWORD='$PGPASSWORD' psql -h 127.0.0.1 -U admin_user -d postgres -c \"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='$SERVICE' AND pid<>pg_backend_pid();\""
kubectl exec postgresql-0 -n infra -- sh -c "PGPASSWORD='$PGPASSWORD' dropdb -h 127.0.0.1 -U admin_user $SERVICE --if-exists && createdb -h 127.0.0.1 -U admin_user $SERVICE"
kubectl exec postgresql-0 -n infra -- sh -c "PGPASSWORD='$PGPASSWORD' psql -h 127.0.0.1 -U admin_user -d postgres -c \"ALTER DATABASE $SERVICE OWNER TO ${SERVICE}_user; GRANT ALL PRIVILEGES ON DATABASE $SERVICE TO ${SERVICE}_user;\""
kubectl exec postgresql-0 -n infra -- sh -c "PGPASSWORD='$PGPASSWORD' psql -h 127.0.0.1 -U admin_user -d $SERVICE -c \"GRANT ALL ON SCHEMA public TO ${SERVICE}_user; ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ${SERVICE}_user; ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ${SERVICE}_user;\""
kubectl scale deployment $DEPLOYMENT -n $NAMESPACE --replicas=1
kubectl rollout status deployment/$DEPLOYMENT -n $NAMESPACE --timeout=180s
```

---

## Streaming Replica (postgresql-replica-0) — Monitoring & Manual Promotion

Added 2026-08-06 as part of the fleet's DB-HA remediation pass (`shared-docs/internal/platform-standards/gap-analysis-and-remediation-plan.md` item 3). `postgresql-replica-0` (StatefulSet `postgresql-replica`, namespace `infra`, manifest `devops-k8s/manifests/databases/postgresql-replica-statefulset.yaml`) is a hot standby, primed via `pg_basebackup -R` and streaming continuously from `postgresql-0`.

**What this is, and isn't:** this is a single-node cluster — both pods share the same physical disk/node, so this protects against a **primary pod crash, OOM, or bad migration**, not against node or disk failure. There is no automatic failover — promotion is always a deliberate, manual, human decision. Nothing reads from the replica today: PgBouncer and every app service still point only at the primary.

### Check Replication Health

```bash
kubectl exec -n infra postgresql-0 -c postgresql -- psql -U admin_user -d postgres -tAc \
  "SELECT client_addr, state, sync_state, replay_lag, write_lag FROM pg_stat_replication;"
```
One row, `state=streaming`, should always be present. No row = the replica has disconnected (check `kubectl logs -n infra postgresql-replica-0 -c postgresql` and confirm the pod is `Running`/`1/1`). `replay_lag` should stay in the low milliseconds under normal load.

```bash
# From the replica itself — confirms it's still in recovery/standby mode
kubectl exec -n infra postgresql-replica-0 -c postgresql -- psql -U admin_user -d postgres -tAc "SELECT pg_is_in_recovery();"
```
Must return `t`. If it ever returns `f` without a deliberate promotion having been run, treat it as an incident — something wrote to what should be a read-only standby.

### Manual Promotion (Incident Recovery Only)

Only do this when the primary is genuinely down/unrecoverable and you've decided to fail over. This is a **one-way, high-blast-radius** action — get explicit sign-off before running it, never automate it.

```bash
# 1. Confirm the primary really is unreachable — do not promote a healthy primary's replica.
kubectl exec -n infra postgresql-0 -c postgresql -- pg_isready -U admin_user -d postgres || echo "primary unreachable, proceeding"

# 2. Promote the replica — this ends recovery mode and makes it a standalone read/write primary.
kubectl exec -n infra postgresql-replica-0 -c postgresql -- psql -U admin_user -d postgres -tAc "SELECT pg_promote();"

# 3. Confirm promotion succeeded (should now return false)
kubectl exec -n infra postgresql-replica-0 -c postgresql -- psql -U admin_user -d postgres -tAc "SELECT pg_is_in_recovery();"

# 4. Repoint every service's POSTGRES_URL / POSTGRES_MIGRATE_URL and PgBouncer's
#    pgbouncer.ini "host=" entries from postgresql.infra.svc.cluster.local to
#    postgresql-replica.infra.svc.cluster.local (or swap Service selectors instead
#    of touching every secret, if time-pressured — either way, PgBouncer pods need
#    a rolling restart afterward to pick up the change).
```

**After a real promotion**, the old primary (if it comes back) is now diverged and must NOT be allowed to resume as if nothing happened — it needs to be re-initialized as a fresh replica of the newly-promoted node (repeat the `pg_basebackup` priming this replica used, in reverse) before it can rejoin. Do not just restart it.

### If the Replica Falls Behind or Needs Re-Priming

The replica has no data of its own worth preserving — if it ever gets into a bad state (disk full, corrupt WAL, too far behind to catch up), the safe fix is to delete and let it re-prime from scratch, exactly like a fresh first start:

```bash
kubectl delete pod postgresql-replica-0 -n infra          # StatefulSet recreates it
# If PGDATA itself needs wiping (rare — only if PG_VERSION is present but corrupt):
kubectl delete pvc data-postgresql-replica-0 -n infra     # then delete + let StatefulSet recreate the pod
```
This never touches the primary — safe to run any time.

---

## Migration Status Audit

### Check Applied Migrations (atlas_schema_revisions)

```bash
export PGPASSWORD=$(kubectl get secret postgresql -n infra -o jsonpath='{.data.admin-user-password}' | base64 -d)

for DB in auth ordering logistics inventory treasury notifications subscriptions pos projects iot ticketing marketflow; do
  echo -n "=== $DB: "
  kubectl exec -n infra postgresql-0 -- sh -c \
    "PGPASSWORD='$PGPASSWORD' psql -U admin_user -d $DB -Atc \
    'SELECT version FROM atlas_schema_revisions ORDER BY applied_at DESC LIMIT 1;' 2>/dev/null \
    || echo 'atlas_schema_revisions not found (fresh DB or pre-Atlas)'"
done
```

### Add postgres-migrate-url to K8s Secrets

Run once per service to add the direct-PostgreSQL URL (bypasses PgBouncer for migrations):

```bash
# Template — substitute SECRET_NAME and NAMESPACE per service.
# Reads POSTGRES_URL from the existing secret, substitutes PgBouncer host:port with
# the direct PostgreSQL host:port, then writes POSTGRES_MIGRATE_URL to the same secret.
patch_migrate_secret() {
  SECRET_NAME=$1
  NAMESPACE=$2
  EXISTING=$(kubectl get secret "$SECRET_NAME" -n "$NAMESPACE" \
    -o jsonpath='{.data.POSTGRES_URL}' | base64 -d)
  if [ -z "$EXISTING" ]; then
    echo "ERROR: POSTGRES_URL not found in $SECRET_NAME / $NAMESPACE — skipping"
    return 1
  fi
  MIGRATE_URL=$(echo "$EXISTING" | \
    sed 's|pgbouncer\.infra\.svc\.cluster\.local:6432|postgresql.infra.svc.cluster.local:5432|')
  kubectl patch secret "$SECRET_NAME" -n "$NAMESPACE" --type=merge \
    -p "{\"data\":{\"POSTGRES_MIGRATE_URL\":\"$(echo -n "$MIGRATE_URL" | base64)\"}}"
  echo "Patched $SECRET_NAME in $NAMESPACE → POSTGRES_MIGRATE_URL added"
}

patch_migrate_secret auth-api-secrets          auth
patch_migrate_secret ordering-backend-secrets  ordering
patch_migrate_secret logistics-api-secrets     logistics
patch_migrate_secret inventory-api-secrets     inventory
patch_migrate_secret treasury-api-secrets      treasury
patch_migrate_secret notifications-api-env     notifications
patch_migrate_secret subscription-api-secrets  subscriptions
patch_migrate_secret pos-api-secrets           pos
patch_migrate_secret projects-api-secrets      projects
patch_migrate_secret iot-api-secrets           iot
patch_migrate_secret ticketing-api-secrets     ticketing
patch_migrate_secret marketflow-api-secrets    marketflow
```

---

## Verification

### Check All Service Pods

```bash
for ns in auth ordering logistics inventory notifications treasury subscriptions pos projects iot ticketing marketflow; do
  echo "=== $ns ===" && kubectl get pods -n $ns 2>/dev/null | grep -v "^NAME"
done
```

### Check DB Sizes

```bash
export PGPASSWORD=$(kubectl get secret postgresql -n infra -o jsonpath='{.data.admin-user-password}' | base64 -d)

kubectl exec postgresql-0 -n infra -- sh -c "PGPASSWORD='$PGPASSWORD' psql -h 127.0.0.1 -U admin_user -d postgres -c \"
  SELECT datname,
         pg_size_pretty(pg_database_size(datname)) AS size
  FROM pg_database
  WHERE datname NOT IN ('template0','template1','postgres')
  ORDER BY pg_database_size(datname) DESC;
\""
```

### Check Table Counts After Migration

```bash
export PGPASSWORD=$(kubectl get secret postgresql -n infra -o jsonpath='{.data.admin-user-password}' | base64 -d)

for db in ordering logistics inventory notifications treasury subscriptions pos projects iot ticketing marketflow; do
  echo -n "=== $db: "
  kubectl exec postgresql-0 -n infra -- sh -c "PGPASSWORD='$PGPASSWORD' psql -h 127.0.0.1 -U admin_user -d $db -Atc \"SELECT count(*) FROM pg_tables WHERE schemaname='public';\" 2>/dev/null || echo 'DB not found'"
done
```

---

## Troubleshooting

### Pod CrashLoopBackOff After DB Reset
- Check logs: `kubectl logs <pod> -n <namespace> --tail=50`
- Common causes: JWKS fetch timeout (transient DNS), missing DB user, wrong password
- Fix: restart the pod: `kubectl rollout restart deployment/<name> -n <namespace>`

### "column X does not exist" Errors
- Indicates stale schema vs new code. Run a full DB reset (drop + recreate).
- Services auto-migrate on startup via the `{svc}-migrate` binary (entrypoint).

### Atlas Migration Hash Mismatch
- If `atlas_schema_revisions` is present but has wrong hashes, the migration history is corrupt.
- For non-critical DBs: full reset (Phase 2.3 in the migration plan).
- For auth DB: **never reset** — escalate and apply migrations manually via direct pod exec.

### Image Pull Failures (DNS Timeout)
- Transient DNS issue on the node (`127.0.0.53` systemd-resolved timeout)
- Fix: delete the stuck pod to force a fresh pull: `kubectl delete pod <name> -n <namespace>`
- If persistent: `kubectl run dns-test --image=busybox:1.36 --restart=Never --overrides='{"spec":{"hostNetwork":true}}' -- sh -c "nslookup registry-1.docker.io"`

### Migration Failing Through PgBouncer
- Symptom: `ERROR: cannot run inside a transaction block` or `prepared statement already exists`
- Cause: PgBouncer transaction mode is incompatible with Atlas DDL
- Fix: ensure `POSTGRES_MIGRATE_URL` points to `postgresql.infra.svc.cluster.local:5432` (direct)
  and `POSTGRES_URL` points to `pgbouncer.infra.svc.cluster.local:6432` (app only)
