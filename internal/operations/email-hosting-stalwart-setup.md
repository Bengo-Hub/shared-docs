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

# Individual mailbox passwords (7 platform role mailboxes, created 2026-08-11 via the
# JMAP admin API — see "Creating mailboxes" below, not the old v0.11.x REST API)
kubectl get secret stalwart-postmaster-mailbox -n email -o jsonpath='{.data.password}' | base64 -d
kubectl get secret stalwart-abuse-mailbox -n email -o jsonpath='{.data.password}' | base64 -d
kubectl get secret stalwart-dmarc-mailbox -n email -o jsonpath='{.data.password}' | base64 -d
kubectl get secret stalwart-tlsrpt-mailbox -n email -o jsonpath='{.data.password}' | base64 -d
kubectl get secret stalwart-fbl-mailbox -n email -o jsonpath='{.data.password}' | base64 -d
kubectl get secret stalwart-no-reply-mailbox -n email -o jsonpath='{.data.password}' | base64 -d
kubectl get secret stalwart-info-mailbox -n email -o jsonpath='{.data.password}' | base64 -d
```

## Login — the real flow, and why `GET /api/principal` doesn't work on v0.16.x

Stalwart v0.16.x dropped the old REST self-service API (`GET/POST /api/principal`, which worked on v0.11.x) in favor of JMAP methods under a vendor-specific `urn:stalwart:jmap` capability, prefixed `x:` (e.g. `x:Account/set`, `x:Domain/get`). Anyone reaching for the old REST endpoints will get a plain `404`, which looks identical to an auth failure — it isn't one.

The webui's own login form (`GET /login`) is a static page that POSTs JSON to `POST /api/auth` (**not** a REST-style Basic-Auth check) — body shape: `{"type":"authCode","accountName":"<user>","accountSecret":"<pass>","clientId":"stalwart-webui","redirectUri":"...","scope":"...","state":"...","codeChallenge":"...","codeChallengeMethod":"S256"}`. A `200 {"type":"authenticated","client_code":"..."}` means the credential is genuinely correct; `{"type":"failure"}` means it's genuinely wrong — this is real server-side validation, not a client-side bug, so a login failure here always means the password itself doesn't match what's currently live (which is exactly what happened 2026-08-11: a credential rotated earlier in that session had never been communicated, and the browser was still using the stale one — see the plan's saga log for the full trace). Basic Auth (`Authorization: Basic base64(email:password)`) works fine directly against `/jmap/session` and all `/jmap/` API calls, and is the fastest way to test a credential server-side without the OAuth/PKCE dance: `curl -H "Authorization: Basic $(printf 'user@domain:pass' | base64)" https://mx1.codevertexafrica.com/jmap/session` — `200` with real account data means it's valid, `401` means it isn't.

## Creating mailboxes — the real JMAP API (discovered 2026-08-11, not documented clearly upstream)

There's no simple REST "create mailbox" call on v0.16.x. The full live schema is self-documented at `GET /api/schema` (redirects to a content-hashed, gzip-compressed URL — fetch with `curl -L --compressed`), which is far more reliable than any blog/doc summary. Ground truth confirmed live against the schema + trial-and-error:

- The object is `x:Account`, a tagged union with variants `User` (`x:UserAccount`) and `Group`. Method calls use the `x:` prefix: `x:Account/set`, `x:Account/get`, `x:Domain/get`, `x:Domain/set`, `x:Domain/get` etc. — **not** bare `Account/set` or `Principal/set` (those either 404 as `unknownMethod`, or belong to the separate, much thinner, standard `Principal` object used for calendar/contact sharing, which cannot create accounts at all).
- Required capabilities in the JMAP request's `"using"` array: `["urn:ietf:params:jmap:core","urn:stalwart:jmap"]`.
- `credentials` is a **map keyed by numeric-string index** (`"0"`, `"1"`, ...), not a JSON array and not named keys — `{"credentials":{"0":{"@type":"Password","secret":"..."}}}`. Any other key shape (`"c1"`, `"cred1"`) fails with `invalidPatch` / `"Invalid key for object property"`; a plain array fails with `"Invalid value for object property"`.
- Minimum viable create payload for one mailbox:
  ```json
  {"using":["urn:ietf:params:jmap:core","urn:stalwart:jmap"],
   "methodCalls":[["x:Account/set",{"create":{
     "info":{"@type":"User","name":"info","domainId":"<domain-id>",
       "credentials":{"0":{"@type":"Password","secret":"<password>"}},
       "roles":{"@type":"User"},"permissions":{"@type":"Inherit"}}
   }},"c1"]]}
  ```
- Get the domain's id first via `x:Domain/get` with `{"ids":null}` — the response's `dnsZoneFile` field is also the single most reliable source for exactly what DNS records (DKIM selectors, SPF, DMARC, MTA-STS, autoconfig/autodiscover) Stalwart currently expects; diff it against Cloudflare after any domain/DKIM regeneration.
- POST to `/jmap/` (not `/api/...`) with the same Basic Auth used for `/jmap/session`.
- All 7 platform mailboxes (`postmaster`, `abuse`, `dmarc`, `tlsrpt`, `fbl`, `no-reply`, `info`) were created this way 2026-08-11 after confirming the earlier ones did **not** survive the DB wipes during the setup saga (see "Open items" below, now resolved).

## TLS for the mail-protocol ports — resolved 2026-08-11

`mx1.codevertexafrica.com`'s mail-protocol listeners (25/465/587/993/995) served an ephemeral, auto-generated self-signed cert (`CN=rcgen self signed cert`) until fixed. Since `mx1` deliberately isn't an Ingress host (must stay DNS-only, plan Part 5), it can't reuse the existing ingress-shim-generated `stalwart-mail-tls` cert (webmail/mail-admin/mta-sts only) — needed its own standalone `cert-manager` `Certificate` (`devops-k8s/manifests/email/stalwart-mx1-tls.yaml`), issued via the same `letsencrypt-prod` `ClusterIssuer` already used everywhere else. That issuer's ACME solver list has a `dns01.cloudflare` solver scoped to `dnsZones: [codevertexafrica.com]`, which takes priority over the generic `http01/nginx` fallback — so this resolves via a temporary `_acme-challenge.mx1` TXT record (self-cleaning), no HTTP reachability needed for `mx1` at all.

Loading the issued cert into Stalwart itself is **not** a mounted-file config — it's a JMAP `x:Certificate/set` call:
```json
{"using":["urn:ietf:params:jmap:core","urn:stalwart:jmap"],
 "methodCalls":[["x:Certificate/set",{"create":{"new1":
   {"certificate":{"@type":"Text","value":"<full PEM chain>"},
    "privateKey":{"@type":"Text","secret":"<PEM private key>"}}
 }},"c1"]]}
```
Stalwart parses the PEM and auto-populates `subjectAlternativeNames` (server-set, read-only) — confirmed it correctly extracted `mx1.codevertexafrica.com`. **However, creating the object alone did not take effect live** — a real SMTP TLS handshake immediately after creation still presented the old ephemeral self-signed cert. **A full pod restart was required** before the new certificate was actually served (confirmed via `openssl`-equivalent `curl` TLS handshake showing `issuer: C=US; O=Let's Encrypt; CN=YR1` post-restart). Whatever selects the active TLS certificate for the mail-protocol listeners appears to be loaded once at process start, not hot-reloaded like most other JMAP settings — plan for a restart after adding/changing a certificate this way. Renewal (cert-manager auto-renews ~30 days before expiry) will need the same re-create-object-then-restart cycle repeated, or a small periodic job — not yet automated.

## Fixing "address not found" bounces to a Stalwart-hosted mailbox (e.g. `info@`)

**Symptom**: an external sender (e.g. Gmail) gets a bounce like `550 5.1.1 The email account that you tried to reach does not exist` when sending to a Stalwart-hosted platform mailbox (`info@`, `no-reply@`, etc.), even though that mailbox is real and working inside Stalwart.

**Root cause**: `codevertexafrica.com`'s MX record points at Google Workspace (`smtp.google.com`), not at Stalwart — confirm with `nslookup -type=MX codevertexafrica.com`. Google Workspace is the domain's real, authoritative inbound mail receiver (it hosts the real staff mailboxes); Stalwart's IP is only authorized to *send* as this domain (it's in the SPF record), not to *receive* for it. A mailbox that exists only inside Stalwart (`info@`, `no-reply@`, etc.) is invisible to Google Workspace, which rejects mail for it before Stalwart ever sees it.

**Fix — requires Google Workspace Admin Console access (admin.google.com), not fixable via kubectl/Stalwart/DNS**:

1. Sign in to `https://admin.google.com` with a Google Workspace super-admin account for this domain.
2. Go to **Apps → Google Workspace → Gmail → Hosts** (sometimes listed as "Routing" → "Configure Gmail routing"). Add a new host entry pointing at Stalwart's public mail hostname (`mx1.codevertexafrica.com`), port 25, with TLS as required/opportunistic.
3. Go to **Apps → Google Workspace → Gmail → Routing** (sometimes "Compliance" in older Admin Console layouts) and add a new **routing rule** ("dual delivery" / "split delivery" is Google's own name for this pattern):
   - **Messages to affect**: Inbound
   - **Envelope filter**: recipient matches the specific Stalwart-hosted addresses — `info@codevertexafrica.com`, `no-reply@codevertexafrica.com`, `postmaster@codevertexafrica.com`, `abuse@codevertexafrica.com`, `dmarc@codevertexafrica.com`, `tlsrpt@codevertexafrica.com`, `fbl@codevertexafrica.com` (the 7 platform role mailboxes — see "Creating mailboxes" above for the full list)
   - **Modify message → Route → Change route**: select the host added in step 2
   - Leave real staff-user addresses unaffected — this rule must only ever match the Stalwart-hosted role mailboxes, never a real Google Workspace staff mailbox
4. Save, then re-test from a real external mail account (e.g. Gmail) — a message to `info@codevertexafrica.com` should now be routed to Stalwart instead of bouncing. Verify actual delivery by checking that mailbox in the webmail app (`https://webmail.codevertexafrica.com/admin`), not just the absence of a bounce.

**Not yet done as of this writing** — flagged live 2026-08-18 after a real user-reported bounce, not yet actioned (needs a human with Google Workspace super-admin access to actually click through the above).

## Port-scan self-ban — a real, recurring false-positive (2026-08-11, 2026-08-18)

Stalwart has a built-in auto-ban feature (distinct from a separate fail2ban install) that watches for port-scan-shaped behavior — connections to ports it isn't listening on, or HTTP requests for exploit-style paths — and auto-bans the source IP. **In this cluster, that source IP is often the node's own public IP** (`77.237.232.66`), because `ingress-nginx` runs `hostNetwork: true` and kubelet's own health-check probes also originate from the host — so a burst of legitimate traffic patterns can look like a scan from Stalwart's point of view, and it bans the node's own IP. When this happens, **every** external path into Stalwart (webmail, mail-admin, IMAP/SMTP) 502s or resets, looking like a broad outage rather than a targeted block.

**How to check** (do this FIRST in any "everything suddenly stopped working" investigation on this service, before chasing network/MTU/conntrack theories):
```bash
kubectl exec -n email stalwart-mail-0 -- sh -c '
ADMIN_PASS=$(printenv STALWART_ADMIN_PASSWORD)
AUTH=$(printf "admin@codevertexafrica.com:%s" "$ADMIN_PASS" | base64 -w0)
curl -s -X POST http://localhost:8080/jmap/ -H "Authorization: Basic $AUTH" -H "Content-Type: application/json" \
  -d "{\"using\":[\"urn:ietf:params:jmap:core\",\"urn:stalwart:jmap\"],\"methodCalls\":[[\"x:BlockedIp/query\",{},\"b1\"],[\"x:BlockedIp/get\",{\"#ids\":{\"resultOf\":\"b1\",\"name\":\"x:BlockedIp/query\",\"path\":\"/ids\"}},\"b2\"]]}"
'
```
A non-empty `list` with `"reason":"portScanning"` and the node's own public IP confirms this. Also viewable/manageable in the WebUI: `mail-admin.codevertexafrica.com` → Settings → Security → Blocked IPs.

**How to fix (temporary — clears the current ban)**:
```bash
# destroy=["<id-from-the-query-above>"]
kubectl exec -n email stalwart-mail-0 -- sh -c '
ADMIN_PASS=$(printenv STALWART_ADMIN_PASSWORD)
AUTH=$(printf "admin@codevertexafrica.com:%s" "$ADMIN_PASS" | base64 -w0)
curl -s -X POST http://localhost:8080/jmap/ -H "Authorization: Basic $AUTH" -H "Content-Type: application/json" \
  -d "{\"using\":[\"urn:ietf:params:jmap:core\",\"urn:stalwart:jmap\"],\"methodCalls\":[[\"x:BlockedIp/set\",{\"destroy\":[\"<id>\"]},\"s1\"]]}"
'
# Deleting the record alone does NOT take effect live on this version — a restart is required:
kubectl rollout restart statefulset/stalwart-mail -n email
```

**No permanent fix has been found yet.** Confirmed via Stalwart's own published docs (`stalw.art/docs/server/auto-ban/`) that **there is no allowlist/exemption mechanism** for this feature at all — it applies its rate thresholds uniformly to every source IP, with no way to mark the node's own IP as trusted. The real config keys are `scanBanRate` (default: 30 attempts/day), `scanBanPeriod` (ban duration), `scanBanPaths` (glob patterns for instant-ban HTTP paths) — raising `scanBanRate` is the only real lever (widens the margin, doesn't eliminate the risk). These keys were **not found reachable via the JMAP API** (every `x:` vendor object name tried — `x:Settings`, `x:AntiAbuse`, `x:SecuritySettings`, `x:FailBan`, `x:Config` — returned `unknownMethod`, and plain REST guesses like `/api/settings` 404'd). They're most likely only reachable via the WebUI's own session-cookie-authenticated settings page (`mail-admin.codevertexafrica.com` → Settings → Security, after a real interactive login — the WebUI login is NOT the same auth mechanism as the JMAP Basic-Auth calls used everywhere else in this doc, see "Login" above) — **not yet pursued**. Whoever picks this up next: log into the WebUI directly, find the Security settings page, and raise `scanBanRate` there.

## Open items (as of this writing)

- ~~TLS for the mail-protocol ports (25/465/587/993/995)~~ — **Resolved 2026-08-11**, see the section above. **New open item it left behind: cert renewal isn't automated.** cert-manager auto-renews the underlying Secret ~30 days before expiry, but Stalwart doesn't watch that Secret — the `x:Certificate/set` + restart cycle above needs repeating manually (or via a small CronJob) each renewal, or the mail-protocol ports will silently fall back to serving an expired cert.
- **Port 587 (STARTTLS submission) isn't listening at all** — confirmed 2026-08-11 (`Connection refused`); only 25/465/993/995/4190/8080/443 are up. Not urgent: port 465 (implicit TLS) already works end-to-end and is what this plan's own SRV records point clients at.
- ~~Whether the domain principal + mailboxes created under the old v0.11.8 instance survived~~ — **Resolved 2026-08-11: no.** The DB wipes during the setup saga (see plan) cleared everything. Domain (`codevertexafrica.com`) and all 7 role mailboxes were recreated fresh via the JMAP API above. DKIM keys were regenerated in the process (new selectors dated 2026-08-11) — **Cloudflare's published DKIM TXT records must be re-synced against the new `dnsZoneFile` output before DKIM will validate anywhere.**
- **Stalwart Enterprise paywall.** Dashboard, tenant list, mailbox/inbox view, and delivery-trace all require a paid Enterprise license (confirmed live 2026-08-11, and against `stalw.art/compare`/`stalw.art/pricing`). Decision: skip it, stay Community-tier — see plan Part 8 for the full reasoning (tenant isolation was never designed to depend on Stalwart's own multi-tenancy feature). Build homegrown observability (queue-depth checks, our own delivery logging) instead, as and when actually needed.
- **File-based logging never actually wrote anything.** The wizard's Step 4 "Log file" destination (`/var/lib/stalwart/logs/`) hit the same missing-directory bug as `etc/config.toml` earlier — fixed in the StatefulSet's init container 2026-08-11, but not yet re-verified that logs are actually landing there post-fix.
