# Database Maintenance Procedures

Centralized database maintenance scripts for all Go microservices. All services share a PostgreSQL instance in the `infra` namespace (`postgresql-0`).

## Service Database Map

| Service | Namespace | Database | DB User | Deployment |
|---------|-----------|----------|---------|------------|
| auth-api | auth | auth_service | auth_service_user | auth-api |
| ordering-backend | ordering | ordering | ordering_user | ordering-backend |
| logistics-api | logistics | logistics | logistics_user | logistics-api |
| inventory-api | inventory | inventory | inventory_user | inventory-api |
| notifications-api | notifications | notifications | notifications_user | notifications-api |
| treasury-api | treasury | treasury | treasury_user | treasury-api |

**PostgreSQL Pod:** `postgresql-0` (Namespace: `infra`)
**Admin User:** `admin_user`

---

## Quick Reference Scripts

### Fix DB Ownership & Privileges (All Services)

Run this after any DB reset to ensure correct ownership and privileges:

```bash
for db in ordering logistics inventory notifications treasury; do
  echo "=== Fixing $db DB ownership ==="
  kubectl exec postgresql-0 -n infra -- sh -c "export PGPASSWORD='Vertex2020!'; psql -h 127.0.0.1 -U admin_user -d postgres -c \"
    ALTER DATABASE $db OWNER TO ${db}_user;
    GRANT ALL PRIVILEGES ON DATABASE $db TO ${db}_user;
  \""
  kubectl exec postgresql-0 -n infra -- sh -c "export PGPASSWORD='Vertex2020!'; psql -h 127.0.0.1 -U admin_user -d $db -c \"
    GRANT ALL ON SCHEMA public TO ${db}_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ${db}_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ${db}_user;
  \""
done
```

### Full Reset: Drop & Recreate All Service DBs (Except auth)

Use this when migrations are broken or you need a clean slate. Auth-service DB is never dropped.

```bash
# Step 1: Scale down all Go API services
kubectl scale deployment ordering-backend -n ordering --replicas=0
kubectl scale deployment logistics-api -n logistics --replicas=0
kubectl scale deployment inventory-api -n inventory --replicas=0
kubectl scale deployment notifications-api -n notifications --replicas=0

# Step 2: Terminate sessions, drop, recreate, fix ownership
for db in ordering logistics inventory notifications; do
  echo "=== Resetting $db ==="
  kubectl exec postgresql-0 -n infra -- sh -c "export PGPASSWORD='Vertex2020!'; psql -h 127.0.0.1 -U admin_user -d postgres -c \"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='$db' AND pid<>pg_backend_pid();\""
  kubectl exec postgresql-0 -n infra -- sh -c "export PGPASSWORD='Vertex2020!'; dropdb -h 127.0.0.1 -U admin_user $db --if-exists; createdb -h 127.0.0.1 -U admin_user $db"
  kubectl exec postgresql-0 -n infra -- sh -c "export PGPASSWORD='Vertex2020!'; psql -h 127.0.0.1 -U admin_user -d postgres -c \"
    ALTER DATABASE $db OWNER TO ${db}_user;
    GRANT ALL PRIVILEGES ON DATABASE $db TO ${db}_user;
  \""
  kubectl exec postgresql-0 -n infra -- sh -c "export PGPASSWORD='Vertex2020!'; psql -h 127.0.0.1 -U admin_user -d $db -c \"
    GRANT ALL ON SCHEMA public TO ${db}_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ${db}_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ${db}_user;
  \""
  echo "=== $db reset complete ==="
done

# Step 3: Scale up all services (auto-migrate on startup)
kubectl scale deployment ordering-backend -n ordering --replicas=1
kubectl scale deployment logistics-api -n logistics --replicas=1
kubectl scale deployment inventory-api -n inventory --replicas=1
kubectl scale deployment notifications-api -n notifications --replicas=1

# Step 4: Wait for rollout
kubectl rollout status deployment/ordering-backend -n ordering --timeout=180s
kubectl rollout status deployment/logistics-api -n logistics --timeout=180s
kubectl rollout status deployment/inventory-api -n inventory --timeout=180s
kubectl rollout status deployment/notifications-api -n notifications --timeout=180s
```

### Reset a Single Service DB

```bash
SERVICE=ordering          # Change to: logistics, inventory, notifications, treasury
NAMESPACE=$SERVICE
DEPLOYMENT="${SERVICE}-backend"  # Adjust if different (e.g., logistics-api, inventory-api)

kubectl scale deployment $DEPLOYMENT -n $NAMESPACE --replicas=0
kubectl exec postgresql-0 -n infra -- sh -c "export PGPASSWORD='Vertex2020!'; psql -h 127.0.0.1 -U admin_user -d postgres -c \"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='$SERVICE' AND pid<>pg_backend_pid();\""
kubectl exec postgresql-0 -n infra -- sh -c "export PGPASSWORD='Vertex2020!'; dropdb -h 127.0.0.1 -U admin_user $SERVICE --if-exists; createdb -h 127.0.0.1 -U admin_user $SERVICE"
kubectl exec postgresql-0 -n infra -- sh -c "export PGPASSWORD='Vertex2020!'; psql -h 127.0.0.1 -U admin_user -d postgres -c \"ALTER DATABASE $SERVICE OWNER TO ${SERVICE}_user; GRANT ALL PRIVILEGES ON DATABASE $SERVICE TO ${SERVICE}_user;\""
kubectl exec postgresql-0 -n infra -- sh -c "export PGPASSWORD='Vertex2020!'; psql -h 127.0.0.1 -U admin_user -d $SERVICE -c \"GRANT ALL ON SCHEMA public TO ${SERVICE}_user; ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ${SERVICE}_user; ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ${SERVICE}_user;\""
kubectl scale deployment $DEPLOYMENT -n $NAMESPACE --replicas=1
kubectl rollout status deployment/$DEPLOYMENT -n $NAMESPACE --timeout=180s
```

---

## Verification

### Check All Service Pods

```bash
for ns in ordering logistics inventory notifications; do
  echo "=== $ns ==="
  kubectl get pods -n $ns -l "app in (ordering-backend,logistics-api,inventory-api,notifications-api)"
done
```

### Check DB Connectivity From Pod

```bash
kubectl exec postgresql-0 -n infra -- sh -c "export PGPASSWORD='Vertex2020!'; psql -h 127.0.0.1 -U admin_user -d postgres -c \"SELECT datname, pg_database_size(datname) as size FROM pg_database WHERE datname IN ('ordering','logistics','inventory','notifications','auth_service');\""
```

### Check Table Counts After Migration

```bash
for db in ordering logistics inventory notifications; do
  echo "=== $db tables ==="
  kubectl exec postgresql-0 -n infra -- sh -c "export PGPASSWORD='Vertex2020!'; psql -h 127.0.0.1 -U admin_user -d $db -c \"SELECT schemaname, count(*) FROM pg_tables WHERE schemaname='public' GROUP BY schemaname;\""
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
- The service auto-migrates on startup with Ent/Atlas.

### Image Pull Failures (DNS Timeout)
- Transient DNS issue on the node (`127.0.0.53` systemd-resolved timeout)
- Fix: delete the stuck pod to force a fresh pull: `kubectl delete pod <name> -n <namespace>`
- If persistent, check node DNS: `kubectl run dns-test --image=busybox:1.36 --restart=Never --overrides='{"spec":{"hostNetwork":true}}' -- sh -c "nslookup registry-1.docker.io"`
