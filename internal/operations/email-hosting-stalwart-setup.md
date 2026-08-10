# Email Hosting — Stalwart Mail Server Setup Runbook

Codevertex's self-hosted, Zoho-Mail-style email hosting platform runs on [Stalwart](https://stalw.art/) (`stalwartlabs/stalwart` on Docker Hub — **not** `stalwartlabs/mail-server`, which is the project's old, abandoned repo capped at v0.11.8). Deployed in the `email` namespace on the production cluster. Full architecture/business plan: `.claude/plans/codevertex-email-hosting-service-plan.md` in the main Codevertex workspace (not part of this public-facing docs tree).

> **SECURITY NOTE:** This file must never contain real credentials. Every value below that is
> a live secret is shown as a placeholder — fetch the real value at runtime via the `kubectl`
> commands given, or from the relevant K8s Secret directly. If this file is ever found with a
> real credential in it, rotate that credential immediately.

## Setup wizard — the exact choices made, step by step

Stalwart v0.16.x (unlike the older v0.11.x line) bootstraps via an interactive web wizard at `https://mail-admin.codevertexafrica.com` rather than a purely declarative config file. These are the choices made for the production instance, for anyone re-running or auditing the setup:

### Step 1 — Server Identity

| Field | Value | Why |
|---|---|---|
| Server Hostname | `mx1.codevertexafrica.com` | **Not** the pod hostname — used in SMTP HELO/EHLO, TLS cert CN, and must match the PTR record |
| Default Email Domain | `codevertexafrica.com` | |
| Automatically Obtain TLS Certificate | **OFF** | Stalwart's own ACME would collide with ingress-nginx's hostNetwork ownership of ports 80/443 on the same node. TLS for the mail-protocol ports (25/465/587/993/995) needs a separate solution — see "Open items" below |
| Generate Email Signing Keys (DKIM) | left at default (ON) | |

### Step 2 — Storage

| Setting | Value | Why |
|---|---|---|
| Main Data Storage | **PostgreSQL** (not the wizard's own suggested default, RocksDB) | Matches this platform's "one Postgres to operate, reuse the existing shared instance" convention rather than a second local storage engine |
| Hostname | `postgresql.infra.svc.cluster.local` | |
| Port | `5432` | |
| Database | `stalwart_mail` | |
| Username | `stalwart` | |
| Password | *(placeholder — see "Fetching credentials" below)* | Stored in the `stalwart-mail` K8s Secret, key `postgres-password` |
| Enable TLS | **OFF** | Matches every other service's connection to this same in-cluster instance — the cluster network is the trust boundary here, not TLS at the DB layer |
| Recycling Method | Fast recycling method | Default; fine for a same-datacenter, low-latency, reliable connection — the extra safety of Verified/Clean isn't worth the overhead here |
| Attachment & File Storage | "Use data store" | No S3 needed at current scale |
| Full-Text Search Index | "Use data store" | Revisit only if search gets slow with real mailbox volume |
| Caching | **Redis/Valkey**, URL `redis://:<redis-password>@redis-master.infra.svc.cluster.local:6379/0` | Reuses the platform's existing shared Redis instance — **do not rotate this password**, it's used by every other service too. Password is in the `redis` Secret (namespace `infra`), key `redis-password` |

### Step 3 — Account Directory

| Field | Value | Why |
|---|---|---|
| Directory Type | "Use the internal directory" | Native Stalwart accounts for the MVP. The "OpenID Connect" option here is worth revisiting later — it could be a simpler path to platform SSO than a custom webmail frontend |

### Step 4 — Logging

| Field | Value | Why |
|---|---|---|
| Log Destination | Log file | |
| Path | `/var/lib/stalwart/logs/` (**not** the default `/var/log/stalwart/`) | Only paths under `/var/lib/stalwart` are on the persistent volume; the default path would lose all logs on every pod restart |
| Rotate frequency | Daily | |
| Tracer (ACME-specific event checkboxes) | left unchecked / any one checked as a formality | Moot — ACME auto-cert is off, so these events never fire |

### Step 5 — DNS Provider

| Field | Value | Why |
|---|---|---|
| DNS Server Type | **"Manual DNS server management"** (not Stalwart's built-in Cloudflare integration) | Keeps `devops-k8s/scripts/cloudflare/populate-zone.py` (run via the `cloudflare-sync-dns.yml` GitHub Action) as the single source of truth for DNS. Letting Stalwart also write directly to Cloudflare would give two systems the ability to fight over the same records |

## Kubernetes-level configuration — bugs found and fixed getting here

All fixes live in `devops-k8s/manifests/email/stalwart-statefulset.yaml`. Recorded here since they were non-obvious and easy to reintroduce if this manifest is ever rewritten from scratch:

1. **Wrong Docker Hub repo.** `stalwartlabs/mail-server` is stale since 2025-04-30, capped at v0.11.8. The project renamed to `stalwartlabs/stalwart`, with active releases well beyond that. Use the new repo.
2. **Wrong container user.** The `stalwartlabs/stalwart` image defines its own `stalwart` user at **uid/gid 2000** (check via `id` inside the container) — not 1000, which is this fleet's usual convention for other services' images but doesn't apply here. Running as 1000 meant the container couldn't write to `/etc/stalwart` at all, surfacing as a "Local registry write error... Permission denied" on every attempt to finish the setup wizard. Set `runAsUser`/`runAsGroup`/`fsGroup` to `2000`.
3. **No default config path.** Without an explicit `-c/--config <PATH>` argument (confirmed via `stalwart --help` run directly in the container — there is no `--help`-documented default), the entrypoint uses some undocumented, non-persistent location. This meant the setup wizard would report "Setup complete" and then lose everything on the next restart, with **both** `/var/lib/stalwart/etc/config.toml` and `/etc/stalwart/` completely empty afterward. Fixed by adding `args: ["--config", "/var/lib/stalwart/etc/config.toml"]` to the container spec, forcing every boot (wizard or otherwise) to agree on one explicit, PVC-backed path.
4. **Don't mount a ConfigMap over the config path.** An earlier version of this manifest mounted a declarative `config.toml` via a ConfigMap `subPath` at that same path (left over from the v0.11.x design, which *did* read a declarative TOML file directly). v0.16.x ignores it entirely, and the subPath mount caused kubelet to auto-create the parent `etc/` directory as `root:root 755` — unwritable by the non-root container user, which was actually the *first* permission error hit (separate from #2 above). Don't reintroduce a ConfigMap mount at this path for this Stalwart version.
5. **Pinned recovery login**, independent of whatever the wizard itself generates on "Setup complete": `STALWART_RECOVERY_ADMIN=admin@codevertexafrica.com:<password>` env var, sourced from the `stalwart-mail` Secret's `recovery-admin` key (format `user:password`). This is the mechanism Stalwart's own bootstrap-mode banner documents for pinning a known credential instead of relying on its randomly-generated temporary one (which regenerates on every restart while still in bootstrap mode).

## Fetching credentials at runtime

```bash
# Stalwart admin/webui password
kubectl get secret stalwart-mail -n email -o jsonpath='{.data.admin-password}' | base64 -d

# Postgres role password (for the 'stalwart' Postgres user)
kubectl get secret stalwart-mail -n email -o jsonpath='{.data.postgres-password}' | base64 -d

# Recovery-admin login string (user:password)
kubectl get secret stalwart-mail -n email -o jsonpath='{.data.recovery-admin}' | base64 -d

# Shared platform Redis password (used by many services, not just Stalwart — never rotate
# without checking who else depends on it)
kubectl get secret redis -n infra -o jsonpath='{.data.redis-password}' | base64 -d

# Individual mailbox passwords (no-reply@, info@ — created outside the wizard, via the
# admin REST API)
kubectl get secret stalwart-no-reply-mailbox -n email -o jsonpath='{.data.password}' | base64 -d
kubectl get secret stalwart-info-mailbox -n email -o jsonpath='{.data.password}' | base64 -d
```

## Open items (as of this writing)

- **TLS for the mail-protocol ports (25/465/587/993/995).** Auto-ACME is off (see Step 1). Needs either (a) cert-manager issuing a cert for `mx1.codevertexafrica.com` too, mounted into Stalwart's TLS config, or (b) revisiting Stalwart's own Cloudflare DNS-01 ACME integration, scoped carefully. Not yet resolved.
- **Whether the domain principal + mailboxes created under the old v0.11.8 instance survived the version/storage-backend transition.** They were written into the same `stalwart_mail` Postgres database the v0.16.x wizard now also points at, but a jump across that many minor versions can mean an incompatible internal schema. Verify via the admin UI or `GET /api/principal` once setup is fully confirmed stable; recreate the mailboxes if needed (cheap — they're role addresses with no real mail in them yet).
