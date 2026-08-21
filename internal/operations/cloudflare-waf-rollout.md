# Cloudflare Managed WAF Rollout

## Why this exists

The 2026-08 platform gap analysis flagged WAF/DDoS protection as zero-config beyond ingress-nginx's existing rate-limit annotations and Cloudflare's orange-cloud DNS proxying (TLS + IP preservation only, no request-filtering ruleset). Decided 2026-08-21: close this via **Cloudflare's built-in managed WAF ruleset**, rolled out in **Log mode before Block mode** to catch false positives before they affect real customers. Originally planned as a manual dashboard toggle; upgraded same-day to a scripted, auditable rollout (`devops-k8s/scripts/cloudflare/manage-waf.py` + `.github/workflows/cloudflare-manage-waf.yml`) once a dedicated, narrowly-scoped `CF_WAF_API_TOKEN` was created — this is a real change to a control that inspects/can block 100% of production traffic for the affected hosts, so a scripted, idempotent, re-runnable path is safer than a one-off manual click, not less safe: it's re-verifiable and git-tracked.

## Which zone / hosts

`codevertexafrica.com` (zone ID `dbbf1a40cb82ffd43dbc1405d3d8a4b1`, confirmed via `.claude/memory/reference_cloudflare_zone_id_mixup.md` — **not** the ID recorded for `codevertexitsolutions.com`, they were previously mixed up). This covers every proxied subdomain, including the 5 critical services' public hostnames — see `reference_production_service_hosts.md` (`sso`, `posapi`, `inventoryapi`, `booksapi`, `pricingapi`).

## Important: the zone is on Cloudflare's Free plan

Discovered live 2026-08-21 (`GET /zones/{zone}/rulesets` only returns `Cloudflare Normalization Ruleset`, `Cloudflare Managed Free Ruleset`, and `DDoS L7 ruleset`) — the paid-tier **Cloudflare Managed Ruleset** (full) and **Cloudflare OWASP Core Ruleset** referenced in the original version of this runbook don't exist on this plan and can't be deployed without upgrading. What's actually live is the **Cloudflare Managed Free Ruleset** — a smaller, curated rule set, not the full managed/OWASP coverage. If broader coverage is ever needed, that's a Cloudflare plan upgrade decision for the account owner, not something `manage-waf.py` can work around.

## Rollout steps (scripted — `workflow_dispatch` or run locally)

1. **Log mode (done 2026-08-21):** `CF_API_TOKEN=<CF_WAF_API_TOKEN value> python3 scripts/cloudflare/manage-waf.py dbbf1a40cb82ffd43dbc1405d3d8a4b1 --mode log` — or trigger the `Manage Cloudflare WAF` GitHub Action (`workflow_dispatch`, `mode: log`). Deploys `Cloudflare Managed Free Ruleset` with every rule forced to log-only via an `overrides.action` — **nothing is blocked**, it only produces entries under Security > Events. Live-verified: deployed cleanly, and a second run correctly no-oped (idempotency check confirmed working).
2. Leave it in Log mode for at least a few days of real traffic. Check **Security → Events** in the dashboard for any rule that fires on legitimate Codevertex traffic (a false positive most likely to hit: POS/inventory API requests with large JSON payloads, or webhook callbacks from Paystack/M-Pesa/KRA that might resemble injection patterns to a generic ruleset).
3. For any rule that clearly false-positives on real traffic, add a targeted exception in the dashboard (scoped to the specific host/path) before flipping to block — the script deploys the whole ruleset as one unit and doesn't (yet) support per-rule exceptions.
4. Once the observation period passes clean: `python3 scripts/cloudflare/manage-waf.py dbbf1a40cb82ffd43dbc1405d3d8a4b1 --mode block` (or the same workflow with `mode: block`) — removes the log override so the ruleset's rules enforce their own default actions (typically block/managed_challenge, rule-by-rule).
5. Rollback is instant either direction: re-run with `--mode log`, or delete the entry point ruleset via the dashboard.

## What this does not cover

This protects the public edge (Cloudflare-proxied hostnames) only — internal ClusterIP S2S traffic never passes through Cloudflare and is unaffected (and shouldn't be routed through it — see [S2S Conventions](../../docs/platform-standards/s2s-conventions.md) on why internal DNS, not public hostnames, is used for S2S). A self-hosted WAF layer inside the cluster's own ingress path, or upgrading the Cloudflare plan for the fuller Managed/OWASP rulesets, both remain bigger, not-yet-justified investments — revisit only if the Free-tier ruleset proves insufficient for a specific real attack pattern.

## Status

**Log mode LIVE as of 2026-08-21.** Deployed via `manage-waf.py`, live-verified (clean deploy + idempotent re-run). Block mode is the next step, pending the observation period in step 2 above.
