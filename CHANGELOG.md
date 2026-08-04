# Changelog

All notable changes to the Codevertex Africa platform documentation are recorded here. Format loosely follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions are published via [mike](https://github.com/jimporter/mike) and selectable from the version dropdown on the published site.

## [1.2.0] — 2026-08-04

Stops the site from publishing the platform's own list of infrastructure weaknesses, and finishes the tone pass started in 1.1.0.

### Removed from the public site
- The **Gap Analysis & Remediation Plan** page — a compiled list of confirmed infrastructure gaps (no observability stack, plain Kubernetes Secrets, no database/cache HA, duplicated rate-limiting logic) is exactly the kind of thing that shouldn't be handed to a public audience alongside the developer guide. Relocated to `shared-docs/internal/platform-standards/` (unpublished) as the single centralized, fleet-wide gaps tracker, and cross-referenced from the project's own memory system so it stays discoverable internally.
- Rewrote five Platform Engineering Standards pages (Secrets Management, Observability, Rate Limiting, Connection Pooling & PgBouncer, Caching) to describe how each system works today — genuinely useful for anyone integrating with the platform — without the "here's exactly what's weak about it" framing that belongs in the internal tracker instead. Removed every "known gap" / "tracked gap" pointer from `microservice-architecture.md` and `trinity-authorization-pattern.md`, replacing them with neutral, factual descriptions.

### Changed — tone
- Full editorial pass on `microservice-architecture.md` (2144 → 1784 lines, ~17% shorter): removed decorative ✅/❌ checkmarks from lists where every item was true by definition, cut a duplicated per-service "Current Stack" block that just repeated an existing table, and fixed a real contradiction — a leftover merge artifact had two consecutive sections claiming Circuit Breaker was both "❌ Not implemented" and "✅ IMPLEMENTED." Checkmarks were kept where they're a genuine mixed pass/fail signal (status tables), not stripped everywhere indiscriminately.

## [1.1.0] — 2026-08-04

A content-quality and scope pass on the site published as 1.0.0, prompted by publishing it to a public audience for the first time: this version narrows the site to genuinely public-appropriate content, corrects a real cluster of outdated technical claims, and rewrites the parts that read like unedited AI output.

### Removed from the public site
- **Business & Governance** (pricing model, equity/revenue-sharing directives), **Operations & Runbooks** (the database-maintenance guide, which includes prod-access commands), and **History** (dated internal sprint audits) are no longer published — none of it is user-guide or technical-guide content, and some of it is either commercially sensitive or an operational-security risk to publish. The files still exist in the repo, under an unpublished `internal/` folder, for the team's own reference.
- The **Client Deliverables** section (pointers to client quotations and signoff PDFs) — those documents already lived outside the published `docs/` tree; this just removed the index page that surfaced them.

### Added
- A genuine **User Guide** section for business users — platform overview, getting started, and how subscriptions/billing work — written at a non-technical level, as a counterpart to the existing developer-facing Technical Guide.
- The nav is now split at the top level into **User Guide** and **Technical Guide**, so the two audiences don't have to wade through each other's content.
- GitHub Pages publishing via a `mike`-versioned GitHub Actions workflow (see the 1.0.0 entry's infrastructure, which this version's content sits on top of).

### Fixed — technical accuracy
- Removed a fleet-wide claim that the ERP service still runs on Django with RabbitMQ/Celery. It was rebuilt on Go years ago and uses NATS JetStream like every other service; RabbitMQ itself was decommissioned platform-wide in 2026-04. This was wrong in roughly 15 places across `microservice-architecture.md` alone (service tables, the architecture diagram, a "why RabbitMQ" rationale section that no longer applies) and in a couple of smaller spots elsewhere.
- Removed several claims that Prometheus, Grafana, and an OpenTelemetry Collector are running and actively monitoring the cluster. They aren't — no metrics/tracing stack is deployed today. Replaced with an honest note pointing at the gap analysis.
- Replaced a hand-drawn ASCII architecture diagram (which had baked in both the RabbitMQ and the fake-observability claims) with a Mermaid diagram that reflects the current, all-Go, NATS-everywhere architecture.
- Fixed a real code-example bug (`login-flow-contract.md` used smart quotes in a JS import statement, which would fail if copy-pasted), a duplicated "Core Principles" section and a duplicated event-subscription table in `cross-service-data-ownership.md`, a systematically mangled `§` section-sign character (rendered as `?`) in `devops-k8s-ingress-cors.md`, and a handful of smaller copy-paste artifacts.

### Fixed — information disclosure
- A real customer's business name and domain had been used as the default "example" tenant throughout the SSO, CORS, and payment-gateway docs (in code samples, CORS allowlists, and API examples) — replaced fleet-wide with a fictional example tenant.
- Removed two references to real internal admin-tool hostnames (Grafana, ArgoCD) under an internal domain that isn't meant to be public.
- Fixed one internal service-DNS hostname that didn't match the platform's actual namespace-naming convention.

### Changed — tone
- Rewrote the densest, most AI-generated-sounding passages (heavy ✅-checkmark bullet lists, "comprehensive/robust/seamless"-style filler, walls of bolded text) into plain professional prose across the SSO guide, event-architecture doc, and the Trinity authorization doc. Trimmed several code blocks and a redundant "Examples" section that repeated content already covered elsewhere, cutting `cross-service-data-ownership.md` by about 13%.

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
