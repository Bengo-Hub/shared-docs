# Platform Overview

Codevertex Africa is a suite of business management products built for African SMEs and growing enterprises — point of sale, inventory, accounting, HR, and more — sharing one account, one login, and one subscription across whichever products a business needs.

## One account, many products

You sign up once and get a single organisation account, managed centrally at the SSO portal — see
[Account & Organisation](organisation/index.md) for signing in and everything a tenant admin
manages there (branding, branches, staff and roles, billing, support). From there, you can add
whichever products your business needs — a retail shop might start with just POS and Inventory, a
hospitality business might add hospitality-specific POS features and recipe costing, and a larger
operation might bring in Treasury for accounting and ERP for HR and payroll. Every product shares
the same login, the same staff and roles, and the same subscription billing, so adding a new
product doesn't mean setting up a separate account or re-onboarding your team.

## The core commerce suite

**Point of Sale (POS)** handles day-to-day sales — retail checkout, pharmacy, restaurants and cafés, and quick-service counters each get a version of the terminal suited to how that business actually operates: table service and kitchen tickets for a restaurant, prescription and batch tracking for a pharmacy, fast checkout for retail.

**[Inventory](inventory/index.md)** manages stock, purchase orders, suppliers, and — for
hospitality businesses — recipes and ingredient costing. It's the single source of truth for what
a business has on hand, and POS reads from it in real time so a sale never oversells stock that
isn't there. Has its own [Service Guide](inventory/index.md), covering both day-to-day staff
workflows and administration.

**[Treasury](treasury/index.md)** (branded "Books" in the product) is the accounting side —
invoicing, bills, accounts receivable and payable, the general ledger, and Kenyan tax compliance
(VAT, eTIMS fiscal receipting). Sales made in POS and orders taken in Ordering post through to
Treasury automatically, so the books stay current without manual re-entry. Has its own
[Service Guide](treasury/index.md).

**ERP** covers HR, payroll, procurement, and asset management for businesses that need it — approval workflows, staff records, and the payroll runs that Treasury's accounting then reflects.

**Ordering** is the online-ordering and delivery side — a storefront customers can order from, connected to Logistics for delivery.

**Logistics** manages delivery riders, routes, and live tracking, for any business that delivers to customers.

**MarketFlow CRM** manages leads, customer relationships, and marketing campaigns for businesses that need more than a till receipt to keep track of who they sell to.

**Projects** covers project and task management for businesses running work that doesn't fit neatly into a single sale — internal projects, client engagements, and the teams working on them.

**[Notifications](notifications/index.md)** is the shared messaging layer every other product sends through — SMS, WhatsApp, and email, with per-channel provider configuration, message templates, and delivery monitoring. Has its own [Service Guide](notifications/index.md).

**Subscriptions** is how the platform itself is billed — the plans, trials, and feature entitlements described in [Subscriptions & Billing](subscriptions-and-billing.md).

## Beyond the core suite

Codevertex also runs a small number of purpose-built products for specific industries or needs:

- **Codevertex Afya** — hospital and clinic management (newly launched, with more clinical features on the way).
- **Library Management System** — for libraries.
- **ISP Billing** — for internet service providers.
- **Webmail** — hosted email mailboxes for your organisation's own domain.
- **Ticketing** — event ticketing and box-office sales.
- **TruLoad** — a separate weighbridge and axle-load compliance platform for the logistics/transport sector (TruLoad has its own dedicated documentation site).

## Multi-outlet and multi-tenant by default

Every product is built to handle more than one location out of the box — a retail chain with several branches, a restaurant group with multiple outlets, or a single shop just starting out all use the same underlying account model. Staff, stock, and settings can be scoped to a specific outlet or managed centrally, depending on how a business is structured — see [Managing Your Organisation](organisation/managing-your-organisation.md#branches) for how branches are set up.

## Finding a guide for a specific product

The **[Service Guides](inventory/index.md)** section of this User Guide has step-by-step,
screenshot-led guides for using each product day to day — Inventory, Notifications, and Treasury
today, with more added the same way as they're written. Anything about the shared account layer
itself — signing in, managing your organisation, billing — lives in
[Account & Organisation](organisation/index.md) instead of being repeated in every product's own
guide.
