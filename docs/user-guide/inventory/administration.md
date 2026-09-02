# Inventory Administration

This page covers the setup and management screens under the **Management**, **Catalog**, and
**Procurement** sidebar groups — the modules a manager or tenant admin uses to configure how
Inventory works for everyone else, rather than the daily catalog/warehouse/procurement work
covered in the other three guides.

If you're looking for staff accounts, PINs, roles at the organisation level, branches, or billing,
that's a different, platform-wide screen — see
[Managing Your Organisation](../organisation/managing-your-organisation.md). This page's **Team &
Roles** section (below) is the Inventory-specific piece: which Inventory permissions a role has,
and setting an individual staff member's PIN.

Most of these screens live under **Management** in the sidebar, which is collapsed by default —
click it to expand the list.

## Categories & Brands

> **Direct link:** `https://inventory.codevertexafrica.com/{your-tenant-slug}/categories`
> (demo: `https://inventory.codevertexafrica.com/codevertex-demo/categories`)

![Categories list](assets/administration/01-categories-list.png)

Categories group items for reporting, filtering, and the catalog's category picker. Categories can
be nested — **Add Category** lets you assign a **Parent Category** to create a subcategory.

![Add Category dialog](assets/administration/02-add-category.png)

1. **Name** — required.
2. **Code** — optional, a short internal reference (e.g. "BEV" for Beverages).

The **Brands** tab alongside it manages the separate brand master used by Goods' Brand field.

![Brands list](assets/administration/03-brands-list.png)

## Units of Measure

> **Direct link:** `https://inventory.codevertexafrica.com/{your-tenant-slug}/units`
> (demo: `https://inventory.codevertexafrica.com/codevertex-demo/units`)

![Units list](assets/administration/04-units-list.png)

This is the tenant-wide unit master — every item's base **Unit** field (piece, kg, litre, bottle,
and so on) is picked from this list, and it can also be extended on the spot from the item form
itself. A unit's own "view details" drawer shows which items currently use it.

![Add Unit dialog](assets/administration/05-add-unit.png)

1. **Name** — the full unit name (e.g. "Kilogram").
2. **Abbreviation** — the short form shown throughout the app (e.g. "kg").

Two of the "Content per unit" style fields on item forms — the ones that convert between a stock
unit and a recipe-line unit — are limited to a fixed **ml / L / g / kg** list regardless of what's
in this master; see
[Configuring quantity-per-unit for ingredients](adding-products.md#configuring-quantity-per-unit-for-ingredients-content-per-unit)
in the Adding Products guide.

## Suppliers

> **Direct link:** `https://inventory.codevertexafrica.com/{your-tenant-slug}/suppliers`
> (demo: `https://inventory.codevertexafrica.com/codevertex-demo/suppliers`)

![Suppliers list](assets/administration/06-suppliers-list.png)

The supplier master used throughout Purchasing & Receiving (see
[Purchasing & Receiving](procurement.md)) — name, contact details, and a payment method (M-Pesa,
bank, cash, or cheque) with the matching account details captured per method.

![Add Supplier dialog](assets/administration/07-add-supplier.png)

Only **Name** is required; everything else — contact info, payment details, preferred currency —
can be filled in later by editing the supplier.

## Team & Roles

> **Direct link:** `https://inventory.codevertexafrica.com/{your-tenant-slug}/team`
> (demo: `https://inventory.codevertexafrica.com/codevertex-demo/team`)

![Team & Roles — Accounts tab](assets/administration/08-team-accounts.png)

The **Accounts** tab lists everyone with access to Inventory in this organisation, searchable by
email. Expanding a row shows their role(s) and which outlets they can access, and this is also
where a manager sets or resets an individual staff member's **PIN** — the same PIN used to log
into the app on a shared till or warehouse tablet throughout the rest of this guide (see
[Signing In](../organisation/signing-in.md) for the login flow itself).

The **Roles & Permissions** tab is where a role's actual Inventory permissions are defined — pick a
role on the left, and its permission matrix (Approvals, Assets, Procurement, Stock, and so on, each
with add/view/change/delete-style toggles) opens on the right.

![Roles & Permissions — permission matrix](assets/administration/09-roles-permissions.png)

A **Permission Catalog** tab alongside it lists every permission that exists in the system, for
reference, independent of any one role.

New staff accounts themselves — inviting someone new to the organisation, and assigning which
tenant-level role they start with — are managed centrally, not here; see
[Managing Your Organisation](../organisation/managing-your-organisation.md#team).

## Settings — Stock & Thresholds

> **Direct link:** `https://inventory.codevertexafrica.com/{your-tenant-slug}/settings`
> (demo: `https://inventory.codevertexafrica.com/codevertex-demo/settings`)

The Settings page has several tabs (Modules, Tax & Compliance, Documents, Printing, Integrations,
and more); the one worth understanding in depth is **Stock & Thresholds**, since it changes how
every item in the catalog behaves.

![Settings — Stock & Thresholds](assets/administration/10-settings-stock-thresholds.png)

- **Inventory Costing Method** — FIFO, LIFO, FEFO, or weighted average. FIFO/LIFO/FEFO require lot
  tracking (FEFO additionally needs expiry tracking); weighted average uses a simple item-level
  cost with no lot ordering.
- **Critical Stock (%)** — below this percentage of an item's reorder level, it's flagged as
  critically low rather than just low.
- **Default Reorder Level (fallback)**, and a **per-unit-type reorder defaults** table further down
  — used when an item has no explicit reorder level of its own set on its item form.
- **Purchase Order Approval Required** — turning this on is what feeds the **Approvals** module
  below: POs above a configured threshold then need sign-off before they can be sent to a supplier.
- **Recipe Items Don't Deplete Stock (Manual Counting)** — when on, selling a menu/recipe item does
  not deduct its ingredients' stock, and it's never auto-marked sold out; goods, bottles, and tots
  keep depleting as normal regardless. This is a tenant-wide default — an individual recipe item
  can still override it via its own **Stock Tracking** field (see
  [Adding Products & Menu Items](adding-products.md#recipe-menu-items-the-new-menu-item-wizard)).
  For businesses that count recipe stock manually rather than trusting automatic deduction.
- **Record Theoretical Usage for Non-Depleting Sales** — with the setting above on, this keeps
  logging what a sale *would* have consumed, so food-cost and actual-vs-theoretical variance
  reports still mean something even though stock isn't actually moving.

## Approvals

> **Direct link:** `https://inventory.codevertexafrica.com/{your-tenant-slug}/approvals`
> (demo: `https://inventory.codevertexafrica.com/codevertex-demo/approvals`)

![Approvals inbox](assets/administration/11-approvals-inbox.png)

Once Purchase Order Approval Required (or a similar gate elsewhere — manufacturing, asset
disposal, large stock adjustments) is switched on, matching requests land here instead of going
through immediately. Three tabs: **My Inbox** (assigned to you), **All Pending**, and **All**
(full history). Opening a request shows its approval-step trail and an Approve/Reject action.

**Approval Rules** (linked from the top of this page) is where those gates are actually configured
— one rule per module + amount band, with an ordered list of approval steps and which role signs
off at each step.

## Pricing Profiles

> **Direct link:** `https://inventory.codevertexafrica.com/{your-tenant-slug}/pricing-profiles`
> (demo: `https://inventory.codevertexafrica.com/codevertex-demo/pricing-profiles`)

![Pricing Profiles list](assets/administration/14-pricing-profiles-list.png)

Pricing Profiles let you define price tiers beyond the plain Selling Price — Retail, Wholesale, a
staff-discount tier, and so on. Each item can then carry a different price per profile, set from
the item's own page, and a **Generate prices** dialog can bulk-derive an entire profile's prices
from the base Selling Price using a percentage rule instead of pricing every item by hand.

![Add Profile dialog](assets/administration/15-add-pricing-profile.png)

**Name** is required; **Code** is an optional short reference (e.g. "WHOLESALE").

## Backups and Audit Log

Two lighter-weight admin screens round out this group:

- **Backups** — on-demand and scheduled backups of your Inventory data.
- **Audit Log** — a read-only, filterable log of who changed what and when, across the modules
  above.

## Common Issues

**A category, unit, or supplier I just added doesn't show up in the item form's dropdown yet.**
These pickers cache the list briefly — reopening the New Item form (or refreshing the page) picks
up anything added in Categories, Units, or Suppliers immediately after.

**"Purchase Order Approval Required" is on, but POs aren't landing in anyone's Approvals inbox.**
Check that an **Approval Rule** actually exists for the Procurement module covering the PO's
amount band — the toggle in Settings only turns the *gate* on; without a matching rule, there's no
one configured to approve against, and the workflow that actually enforces the gate depends on a
rule being in place.

**A manager can see Inventory in the sidebar, but a screen they should have access to 403s or is
missing.** Check their role's permission matrix under **Team & Roles → Roles & Permissions** — a
role only sees and can act on the modules its permissions explicitly grant, module by module (Stock,
Procurement, Assets, and so on each have their own toggles).

**Recipe items keep showing as sold out even though "Recipe Items Don't Deplete Stock" is on.**
That tenant-wide setting only applies to items left on the **default** Stock Tracking mode. If a
specific recipe item's own Stock Tracking field is set to "Always deplete stock," it overrides the
tenant policy for that one item — open the item and check its Stock Tracking field.

**A pricing profile's "Generate prices" produced numbers that don't look right.** It always
calculates from the item's base Selling Price, not from another profile's price — if you've been
editing this item's Wholesale price by hand for a while and then run Generate prices on a
different profile, it recalculates from Selling Price, not from Wholesale.
