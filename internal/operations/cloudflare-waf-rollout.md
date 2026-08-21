# Cloudflare Managed WAF Rollout

## Why this exists

The 2026-08 platform gap analysis flagged WAF/DDoS protection as zero-config beyond ingress-nginx's existing rate-limit annotations and Cloudflare's orange-cloud DNS proxying (TLS + IP preservation only, no request-filtering ruleset). Decided 2026-08-21: close this via **Cloudflare's built-in managed WAF ruleset** — a dashboard-level toggle per zone, not a self-hosted ModSecurity/ingress-nginx WAF. This is a real change to a control that inspects/can block 100% of production traffic for the affected hosts, so it's run as a manual, reviewed dashboard action rather than a scripted API call, and rolled out in **Log mode before Block mode** to catch false positives before they affect real customers.

## Which zone / hosts

`codevertexafrica.com` (zone ID confirmed via `.claude/memory/reference_cloudflare_zone_id_mixup.md` — **not** the ID recorded for `codevertexitsolutions.com`, they were previously mixed up). This covers every proxied subdomain, including the 5 critical services' public hostnames — see `reference_production_service_hosts.md` (`sso`, `posapi`, `inventoryapi`, `booksapi`, `pricingapi`).

## Rollout steps (dashboard, manual — do this yourself, not scripted)

1. Cloudflare dashboard → the `codevertexafrica.com` zone → **Security → WAF → Managed rules**.
2. Enable the **Cloudflare Managed Ruleset** and the **Cloudflare OWASP Core Ruleset**, both with the **action set to Log**, not Block, for the first observation period.
3. Leave it in Log mode for at least a few days of real traffic. Check **Security → Events** for any rule that fires on legitimate Codevertex traffic (a false positive most likely to hit: POS/inventory API requests with large JSON payloads, or webhook callbacks from Paystack/M-Pesa/KRA that might resemble injection patterns to a generic ruleset).
4. For any rule that clearly false-positives on real traffic, either add a targeted exception (scoped to the specific host/path) or leave that individual rule in Log-only via a custom override — don't disable the whole ruleset over one noisy rule.
5. Once a rule has run clean (or been scoped) for the observation period, flip it from Log to **Block**. Do this per-ruleset/per-rule, not as one big-bang switch for everything at once.
6. Sensitivity level: start at the ruleset's default sensitivity; only loosen it if a specific rule proves to be a recurring false positive after step 4's targeted exception still isn't enough.

## What this does not cover

This protects the public edge (Cloudflare-proxied hostnames) only — internal ClusterIP S2S traffic never passes through Cloudflare and is unaffected (and shouldn't be routed through it — see [S2S Conventions](../../docs/platform-standards/s2s-conventions.md) on why internal DNS, not public hostnames, is used for S2S). A self-hosted WAF layer inside the cluster's own ingress path remains a bigger, not-yet-justified investment — revisit only if the managed ruleset proves insufficient for a specific real attack pattern.

## Status

Not yet actioned as of 2026-08-21 — this is the runbook, the actual dashboard toggle is a manual step for the account owner.
