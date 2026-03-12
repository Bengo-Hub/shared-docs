# Paystack frontend callback page (flexible, reusable)

All services that integrate with treasury and use Paystack (ordering, subscriptions, treasury-ui, cafe, etc.) should use a **flexible, public** payment callback page so that after Paystack redirects the user back, they see a consistent experience with a **single primary button** whose label and destination are configurable per service.

**Payment flow context**: Payments use an **invoice-first** flow: the service creates a payment intent (invoice) via treasury-api, then redirects the user to the **shared treasury-ui pay page** (`/pay`) with invoice details; the user selects a gateway and completes payment. After Paystack, the user is sent to this callback page. See [payment-workflow.md](payment-workflow.md) for the full flow.

## Contract (same for every app)

- **Route**: Public, no auth. Example: `/(public)/payment/callback` or `/payment/callback`.
- **Query params** (Paystack sends `reference`; your app can append the rest when building the callback URL):
  - `reference` (required) – from Paystack redirect (`reference` or `trxref`).
  - `redirect_url` (optional) – where to send the user after payment (path or full URL). Default: `/` or app home.
  - `button_text` (optional) – label for the primary button. Default: e.g. "Continue" or "Back to dashboard".
  - `payment_type` (optional) – used by the page to choose copy or verify API (e.g. `order`, `subscription`, `billing`).
  - `tenant` or `org` (optional) – tenant slug for tenant-scoped verify APIs.

## Building the callback URL when creating the intent

When your frontend (or backend) creates a Paystack payment intent, set the redirect (callback) URL to your **own** frontend callback page and pass the desired post-payment destination and button text:

```text
{origin}/payment/callback?redirect_url={encodeURIComponent('/orders')}&button_text={encodeURIComponent('View my orders')}
```

Example by service:

- **Ordering**: `redirect_url=/orders` or `/{orgSlug}/orders`, `button_text=View my orders`
- **Subscriptions**: `redirect_url=/billing`, `button_text=Back to billing`
- **Treasury / general**: `redirect_url=/`, `button_text=Go to dashboard`

Paystack will append `&reference=...` when redirecting. The callback page reads `reference`, `redirect_url`, and `button_text` and shows a primary button with that label linking to that URL.

## Page behavior

1. **Public** – no authentication; anyone can land here from Paystack redirect.
2. **Loading** – show a short “Verifying payment…” state.
3. **Verify (optional)** – if the app configures a verify URL (e.g. from env `NEXT_PUBLIC_PAYMENT_VERIFY_URL` or a per–payment_type verify endpoint), call it with `reference` and use the result to show success / failed / pending.
4. **Result** – show success, failed, or pending and a **single primary button**: custom `button_text` → `redirect_url` (or “Try again” / “Back” on failure).
5. **Support** – optional footer with support contact (e.g. mailto, phone).

## Reuse across apps

- **Same pattern everywhere**: Each app (ordering-frontend, subscription-ui, treasury-ui, cafe-website, etc.) implements one public callback page that respects the query params above.
- **Reference implementation**: See `finance-service/treasury-ui/src/app/(public)/payment/callback/page.tsx` for a minimal implementation that uses `redirect_url` and `button_text` and optional verify.
- **ISP Billing**: The same idea is used in `ISPBilling/isp-billing-frontend` at `(public)/payment/callback` with `payment_type` and `org` to vary copy and buttons per product (hotspot, PPPoE, SMS, etc.). Services that use treasury can use the simpler contract above (redirect_url + button_text) or extend with payment_type for custom copy.

## Middleware

Ensure the callback route is **public** (no auth redirect). For example in Next.js middleware, exclude `/payment/callback` from auth checks (see isp-billing-frontend `middleware.ts`).

## Production base URLs

- **Treasury API** base URL (for auto-generated webhook/callback URLs in the backend) is set in **devops-k8s** only: `devops-k8s/apps/treasury-api/values.yaml` as `TREASURY_HTTP_PUBLIC_BASE_URL` (same host as ingress, e.g. `https://booksapi.codevertexitsolutions.com`). In production, do not duplicate this; the chart injects it from values. Local dev can use `HTTP_PUBLIC_BASE_URL` or `TREASURY_HTTP_PUBLIC_BASE_URL` in `.env`.
