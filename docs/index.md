# Codevertex Africa — Platform Documentation

This is the ecosystem-wide documentation for Codevertex Africa's microservices platform: a multi-tenant SaaS suite (POS, Inventory, Treasury, ERP, Ordering, Logistics, Subscriptions, Notifications, Hospital, Library, TruLoad, ISP Billing, MarketFlow, and more) sharing a common auth/RBAC model, event bus, and set of Go/TypeScript libraries.

This site covers the **cross-service** concerns — architecture, integration contracts, and engineering standards that apply across the platform. Each service's own repo carries its own service-specific docs (`docs/` folder, `README.md`) for things scoped only to that service.

## Where to start

- **New to the platform architecture?** Start with [Microservice Architecture](architecture/microservice-architecture.md), then [Trinity Authorization Pattern](architecture/trinity-authorization-pattern.md) (how auth, subscriptions, and RBAC compose).
- **Integrating a new service with the platform?** See [Platform Engineering Standards](platform-standards/index.md) for the conventions every service is expected to follow (S2S auth, caching, idempotency, rate limiting, secrets, migrations), and [Cross-Service Data Ownership](architecture/cross-service-data-ownership.md) to find out which service owns the data you need.
- **Working on payments?** [Payment Workflow](integrations/payment-workflow.md) is the hub; gateway-specific detail lives in the M-Pesa and Paystack reference pages.
- **Running database or infra maintenance?** See [Operations & Runbooks](operations/index.md).
- **Looking for a past sprint audit or decision record?** See [History](history/index.md) — these are kept for context but are not actively maintained.

## How this site is organized

Mirrors the pattern already proven out in `TruLoad/truload-docs`: [mkdocs-material](https://squidfunk.github.io/mkdocs-material/) with automatic "last updated" dates per page (via `git-revision-date-localized`) so staleness is visible at a glance, organized by audience — architecture for engineers designing new services, platform standards for anyone integrating with the shared libraries, integrations for anyone touching payments/notifications, operations for on-call/ops work, and business/governance for the non-engineering policy docs that still need a durable home.

## Building this site locally

```bash
pip install -r requirements.txt   # mkdocs-material + plugins
mkdocs serve                       # http://127.0.0.1:8000
mkdocs build --strict              # fails on broken links/nav — run before committing
```

**Known, expected `--strict` warnings:** several docs link to files in sibling service repos (e.g. `../finance-service/treasury-api/docs/...`) that live outside this repo entirely — `mkdocs build` can't resolve those and will always warn. That's expected, not a regression; only investigate a new warning if it points to a file that should exist *inside* `shared-docs/docs/`.
