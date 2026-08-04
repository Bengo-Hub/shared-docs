# Codevertex Africa — Platform Documentation

Codevertex Africa is a suite of business management products — point of sale, inventory, accounting, HR, and more — for African SMEs and growing enterprises, all sharing one account and one login.

This site has two parts:

- **[User Guide](user-guide/index.md)** — for business owners, managers, and staff using the products. High-level, no technical background required.
- **[Technical Guide](architecture/index.md)** — for developers and integrators, covering how the platform is built: architecture, engineering standards, and integration contracts.

## Where to start

**Using the products?** Start with the [Platform Overview](user-guide/platform-overview.md) to see which product fits your business, then [Getting Started](user-guide/getting-started.md) to sign up.

**Building on the platform?** Start with [Microservice Architecture](architecture/microservice-architecture.md) for the big picture, then [Platform Engineering Standards](platform-standards/index.md) for the conventions every service follows (caching, idempotency, rate limiting, secrets, migrations). Working on payments specifically? [Payment Workflow](integrations/payment-workflow.md) is the hub, with gateway-specific detail in the M-Pesa and Paystack reference pages.

## How this site is organized

Built with [mkdocs-material](https://squidfunk.github.io/mkdocs-material/), with an automatic "last updated" date on every page so staleness is visible at a glance.

## Building this site locally

```bash
pip install -r requirements.txt   # mkdocs-material + plugins
mkdocs serve                       # http://127.0.0.1:8000
mkdocs build --strict              # fails on broken links/nav — run before committing
```

**Known, expected `--strict` warnings:** several docs link to files in sibling service repos (e.g. `../finance-service/treasury-api/docs/...`) that live outside this repo entirely — `mkdocs build` can't resolve those and will always warn. That's expected, not a regression; only investigate a new warning if it points to a file that should exist *inside* `shared-docs/docs/`.
