# Inventory & Integrated Services — Audit Findings & TODOs

_Audit date: 2026-06-25. Covers inventory-api/ui, pos-api/ui, ordering-backend/frontend, shared-ui-lib._

## ✅ Shipped in this pass (committed + pushed to default branches)

| Area | Change | Repo(s) |
|------|--------|---------|
| Real toast errors (root cause) | `useDocumentPreview` swallowed every failure as "Failed to load document". Added dependency-free `extractErrorMessage` that decodes axios **Blob**/string/object error bodies and surfaces the real message. Released **v0.1.23**. | shared-ui-lib (+ consumer bumps in inventory-ui, pos-ui, ordering-frontend, treasury-ui) |
| Real toast errors (inventory-ui) | `apiErrorMessage` helper (Blob-aware) + axios interceptor attaches `normalizedMessage`. Label-print dialog now fetches the blob up-front and shows `EMPTY_SELECTION` / `NO_LABELS` verbatim. | inventory-ui |
| Empty categories in label form | Label-print category dropdown now only lists categories that have items (`useCategories(slug,{hasItems:true})`). | inventory-ui |
| Source `has_items` filter | `GET /inventory/categories?has_items=true` → only categories with ≥1 active item (GROUP BY on `(tenant_id, category_id)`). | inventory-api |
| Proxy: never sync empty categories + use-case gating | ordering-backend `ListCategories` requests `has_items=true` and applies `categoryAllowedForUseCase` (ported from proven pos-api heuristic). Handlers accept `?use_case=`. | ordering-backend |

**Note:** pos-api **already** does both (item-linkage via `GetCatalogCategories` `withItems` map + `categoryAllowedForUseCase` + `useCaseItemTypes`). Left unchanged to avoid regressing production behavior.

---

## ✅ P1 (done) — Toast sweep across all three UIs

`apiErrorMessage` helper (Blob/string/object-aware) + axios-interceptor `normalizedMessage` added to inventory-ui, pos-ui, ordering-frontend. Call sites swept:
- inventory-ui: ~50+ earlier batch converted (catch/onError → `apiErrorMessage`).
- pos-ui: 57 files converted (0 remaining `onError: () =>`; 59 files import the helper).
- ordering-frontend: ~30 sites across ~17 files (rest already used `parseApiError`).
All tsc-clean, committed & pushed. Validation/business toasts intentionally left as-is.

**Remaining (optional):** an ESLint guard to flag `toast.error('literal')` inside `catch`/`onError` to prevent regressions; a few low-traffic stragglers may remain.

## ✅ P1 (done) — Outlet use-case gating reaches the storefront UI

ordering-frontend now passes the browsed outlet's use_case to `GET /catalog/categories?use_case=` (`fetchCategories`/`useCategories` + `useOrderingConfig`). Backend gating is active end-to-end.

## 🟠 P2 — ordering-frontend use-case modularity (FOUNDATION SHIPPED)

**Shipped:** `src/lib/use-case-config.ts` (`OrderingProfile` + `orderingConfigFor` behavioural flags) + `useOrderingConfig()` (effective use_case: browsed outlet › selected outlet › tenant; the storefront analogue of pos-ui's `useTerminal().cfg`). `catalog-discovery` + `CatalogHero` are now cfg-driven (CTA label, search copy, dietary filters food-only, make/model surface, grid density, hero/headings). Catalog page slimmed to a thin shell.

**Also shipped:** product detail page now cfg-driven (CTA label + make/model gating via `useOrderingConfig`). It already handled SERVICE appointments, variants, and modifiers.

**Remaining (per-view divergence — see memory `pos-terminal-modular-architecture`):**
1. Checkout: generalize the existing `isTicketOnly` branch to also skip fulfillment for a services-only cart (appointment confirmation) and a pharmacy Rx note. NOTE: checkout is content-driven (cart contents), which is safer than use_case for mixed-vertical tenants — keep that; do not regress the payment flow.
2. Cart item display per profile (tickets show QR, no qty spinner; retail show variant/stock).
3. Decompose the 567-line `catalog-discovery.tsx` / 380-line `checkout/page.tsx` into shared building blocks (behavior-preserving — lose no workflow).
4. Optional per-profile view files (`components/catalog/views/*`) once divergence justifies it; today MenuDiscovery + product detail self-adapt via cfg (faithful to pos-ui's thin-view-over-shared-shell pattern).

## 🟠 P2 — Inventory schema: largely robust, targeted e-commerce gaps

**Already present (good for retail/online):** `manufacturer`, `model`, `brand_id`/ItemBrand, `sku`, `barcode`+`barcode_type`, `weight_kg`, `dimensions_cm`, **ItemVariant** (attributes/sku/price/barcode/image), **VariantAttribute**, **ItemAsset** gallery (primary + order + video/3D), **CustomFieldDefinition** (per-category specs), **Warranty**, **ModifierGroup**, **Bundle**, multi-tier **ItemPricing**, lot/serial/balance tracking. → "make/model and related e-commerce features" **are** covered.

**✅ Shipped (inventory-api):** additive Item fields `gtin`, `mpn`, `condition` (NEW/REFURBISHED/USED/OPEN_BOX), `slug`, `short_description`, `meta_title`, `meta_description`, `country_of_origin`, `hs_code`, `is_returnable`, `return_window_days`, `allow_backorder`, `is_discontinued` — wired through ItemDTO (read+create; update sets strings/condition conditionally, never clobbers the new bools). Columns are nullable/defaulted so the startup online auto-migrate applies them (no manual migration).

**Remaining for these fields:**
- inventory-ui: surface the new fields in the item create/edit form + detail view (and an explicit returnable/backorder toggle so the update path can set the bools).
- ordering-frontend: show condition badge / specs / brand on product cards & detail for retail.
- Still NOT added (lower priority): structured product specifications surface beyond `CustomFieldDefinition` for faceted search; `show_stock_level` flag.

## 🟡 P3 — Hardening / smaller items
- pos-api & ordering use a **name-substring heuristic** for use-case gating. Long-term: drive off `Item.use_case` enum at source once item data is reliably tagged (currently defaults to RETAIL → risky to switch now).
- inventory-api `has_items` is uncached (cheap GROUP BY). If categories endpoint gets hot, cache the linkage set per tenant (5-min TTL) alongside the category list.
- Label-print `NO_LABELS` still possible when lot/serial mode is on but no active lots/serials exist — now shown verbatim; consider disabling the lot/serial checkboxes when the selection has none.
