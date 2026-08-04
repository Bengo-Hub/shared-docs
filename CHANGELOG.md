# Changelog

All notable changes to the Codevertex Africa platform documentation are recorded here. Format loosely follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions are published via [mike](https://github.com/jimporter/mike) and selectable from the version dropdown on the published site.

## [1.0.0] — 2026-08-04

Initial versioned release. Rebuilt the site as an mkdocs-material site (previously a flat folder of markdown files with no site, no nav, no freshness signal) and published it to GitHub Pages.

### Added
- Full mkdocs-material site structure under `docs/`, organized by audience: `architecture/`, `platform-standards/`, `integrations/`, `operations/`, `business/`, `client-deliverables/`, `history/`.
- 11 new **Platform Engineering Standards** pages, grounded in a live prod cluster audit and a `shared/` library scan: webhooks vs polling, connection pooling & PgBouncer, caching, idempotency & the outbox pattern, resilience (circuit breakers & retries), rate limiting, S2S conventions, secrets management, observability, AI integrations & pgvector, N+1 queries.
- A compiled best-practices **gap analysis and remediation plan** (what's confirmed working well vs. genuine gaps — no observability stack, plain K8s Secrets, no DB/cache HA, duplicated rate-limiting logic — each with a proposed, sign-off-gated remediation).
- `git-revision-date-localized` plugin, so every page shows an automatic "last updated" date instead of relying on a manually-maintained header.
- Versioning via `mike`, published to GitHub Pages.

### Changed
- Merged the 3-file architecture-doc cluster (`ARCHITECTURE-RECOMMENDATIONS.md`, `Microservice-Architecture-for-POS-Inventory-Orders.md`, `microservice-architecture.md`) into one canonical `architecture/microservice-architecture.md` — genuinely unique content from the two retired docs was folded in (entity ownership matrices, token/API-key security parameters, the combined-authorization worked example, the NATS published-event catalog, offline-first resilience patterns); stale/superseded content (old auth ordering, old pricing tiers, time-bound audit action items) was left out.
- Cross-linked the auth/SSO/subscription-gating docs (`trinity-authorization-pattern.md`, `sso-integration-guide.md`, `subscription-gating-guide.md`) instead of each restating the same "mutations-only subscription enforcement" rule independently.
- Deduplicated the boilerplate payment-flow paragraph repeated in both gateway reference docs (M-Pesa, Paystack) down to a single hub page (`integrations/payment-workflow.md`).
- Refreshed `operations/database-maintenance.md`'s stale pre-PgBouncer connection topology and added the 4 services missing from its DB map (erp-api, isp-billing-backend, marketflow-ai, truload-backend).

### Archived
- Moved 3 dated sprint-snapshot/decision-log documents into `docs/history/` (not actively maintained going forward): the 2026-06-25 inventory/ordering audit, the 2026-07-06 POS QA remediation sprint, and the 2026-06 WhatsApp provider evaluation.

---

## How to cut a new version

```bash
pip install -r requirements.txt
mike deploy --push --update-aliases <new-version> latest
mike set-default --push latest
```

Add an entry to this file for every version deployed via `mike` — the version dropdown on the published site tells a reader *that* something changed; this file is where they find out *what*.
