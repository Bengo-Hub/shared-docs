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

## 🔴 P1 — Remaining toast sweep (explicitly requested: "apply across all toast logic")

The **mechanism** now exists; the **call sites** still hardcode generic strings and ignore the error object. Counts:

- inventory-ui: ~201 `toast.error(...)` across 53 files
- pos-ui: ~177 across 63 files (has unused `error-handler.ts`)
- ordering-frontend: ~80 across 20 files (already has `parseApiError` — best off)

**TODO:**
1. pos-ui & ordering-frontend: add the same axios-interceptor `normalizedMessage` + `apiErrorMessage` helper as inventory-ui (port `error-message.ts`).
2. Sweep `onError`/`catch` sites to `toast.error(await apiErrorMessage(e, '<fallback>'))`. Mechanical but large — prioritize: submit/save/delete mutations, PDF/preview surfaces, payment/checkout flows.
3. Lint guard (optional): flag `toast.error('literal')` inside a `catch`/`onError` to prevent regressions.

## ✅ P1 (done) — Outlet use-case gating reaches the storefront UI

ordering-frontend now passes the browsed outlet's use_case to `GET /catalog/categories?use_case=` (`fetchCategories`/`useCategories` + `useOrderingConfig`). Backend gating is active end-to-end.

## 🟠 P2 — ordering-frontend use-case modularity (FOUNDATION SHIPPED)

**Shipped:** `src/lib/use-case-config.ts` (`OrderingProfile` + `orderingConfigFor` behavioural flags) + `useOrderingConfig()` (effective use_case: browsed outlet › selected outlet › tenant; the storefront analogue of pos-ui's `useTerminal().cfg`). `catalog-discovery` + `CatalogHero` are now cfg-driven (CTA label, search copy, dietary filters food-only, make/model surface, grid density, hero/headings). Catalog page slimmed to a thin shell.

**Remaining (per-view divergence — see memory `pos-terminal-modular-architecture`):**
1. Product detail page: per-profile (retail specs/variants, hospitality modifiers/courses, services time-slot picker, ticketing tier/seat selection).
2. Checkout: generalize the `isTicketOnly` branch into a `bookingMode`-driven flow (ticketing skips address/fulfillment; services → appointment confirmation; pharmacy → Rx note).
3. Cart item display per profile (tickets show QR, no qty spinner; retail show variant/stock).
4. Decompose the 567-line `catalog-discovery.tsx` / 380-line `checkout/page.tsx` into shared building blocks (behavior-preserving — lose no workflow).
5. Optional per-profile view files (`components/catalog/views/*`) once divergence justifies it; today MenuDiscovery self-adapts via cfg (faithful to pos-ui's thin-view-over-shared-shell pattern).

## 🟠 P2 — Inventory schema: largely robust, targeted e-commerce gaps

**Already present (good for retail/online):** `manufacturer`, `model`, `brand_id`/ItemBrand, `sku`, `barcode`+`barcode_type`, `weight_kg`, `dimensions_cm`, **ItemVariant** (attributes/sku/price/barcode/image), **VariantAttribute**, **ItemAsset** gallery (primary + order + video/3D), **CustomFieldDefinition** (per-category specs), **Warranty**, **ModifierGroup**, **Bundle**, multi-tier **ItemPricing**, lot/serial/balance tracking. → "make/model and related e-commerce features" **are** covered.

**Gaps to add (additive — mind pos-api online auto-migrate gotcha; see memory `pos-migrations-additive-auto-migrate`):**
- `gtin` / `mpn` (marketplace feeds), `condition` enum (NEW/REFURBISHED/USED/OPEN_BOX)
- Item-level SEO: `slug`, `meta_title`, `meta_description`, `short_description`
- `country_of_origin`, `hs_code` (customs / international)
- Structured product specifications surface (beyond CustomFieldDefinition) for faceted search
- Inventory policy flags: `allow_backorder`, `is_discontinued`, `show_stock_level`
- Return policy: `is_returnable`, `return_window_days`

## 🟡 P3 — Hardening / smaller items
- pos-api & ordering use a **name-substring heuristic** for use-case gating. Long-term: drive off `Item.use_case` enum at source once item data is reliably tagged (currently defaults to RETAIL → risky to switch now).
- inventory-api `has_items` is uncached (cheap GROUP BY). If categories endpoint gets hot, cache the linkage set per tenant (5-min TTL) alongside the category list.
- Label-print `NO_LABELS` still possible when lot/serial mode is on but no active lots/serials exist — now shown verbatim; consider disabling the lot/serial checkboxes when the selection has none.
