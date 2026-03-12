# Payment Workflow (Invoice-First, Shared Pay Page)

**Last Updated**: March 2026  
**Applies to**: All services that collect payments (ordering, subscription, cafe-website, treasury-ui). Treasury-api is the single source for payment intents and gateway orchestration.

---

## Overview

Payments follow an **invoice-first** flow:

1. A **service** (ordering-backend, subscription-api, cafe-website backend, etc.) creates a **payment intent** (invoice) via treasury-api with payment details and `payment_method: "pending"`.
2. Treasury-api returns **intent_id** and invoice details (amount, currency, reference_id, reference_type).
3. The service’s **frontend** redirects the user to the **shared treasury-ui pay page** with these details (and optional `intent_id`, `invoice_number`, `initiate_url`, etc.) in the URL.
4. The **pay page** shows an invoice summary at the top, then lists **active payment gateways** (Paystack, M-Pesa, COD). The user picks one; the corresponding **payment modal** opens with the same payment context.
5. When the user completes the flow (redirect to Paystack, STK push, or COD/manual confirmation), the intent is updated via webhooks or API; the user is sent to the **callback page** or redirect_url with a configurable button.

---

## 1. Create Invoice (Payment Intent) — Treasury API

**Endpoint**: `POST /api/v1/{tenant}/payments/intents`  
**Auth**: Required (service backend calls with valid JWT).

**Request** (invoice-only; user will choose method on pay page):

```json
{
  "reference_id": "order-123",
  "reference_type": "order",
  "payment_method": "pending",
  "currency": "KES",
  "amount": 1500,
  "source_service": "ordering",
  "description": "Order #123"
}
```

- Use `payment_method: "pending"` (or omit) to create the intent **without** initiating any gateway. No redirect or STK is sent yet.
- **Response**: `intent_id`, `status`, `amount`, `currency`, `reference_id`, `reference_type`. The service stores or passes these to the frontend.

**Optional**: If the service already knows the method (e.g. “paystack” or “mpesa”), it can send that and treasury-api will initiate the gateway immediately (existing behavior). For the shared pay page flow, use `"pending"`.

---

## 2. Initiate Payment for an Existing Intent — Treasury API

After the user selects a gateway on the pay page, the **calling service’s backend** (or a proxy) calls:

**Endpoint**: `POST /api/v1/{tenant}/payments/intents/{intentID}/initiate`  
**Auth**: Required.

**Request**:

```json
{
  "payment_method": "paystack",
  "customer_email": "user@example.com"
}
```

- For M-Pesa: `payment_method: "mpesa"`, `phone_number: "254712345678"`.
- For COD: `payment_method: "cash"` — intent is marked succeeded without gateway.
- For **manual / paid at till**: `payment_method: "manual"` or `"till"` — intent is marked succeeded without calling the gateway (user confirmed they paid at agent/till).

**Response**: Same shape as create intent — e.g. `authorization_url` (Paystack), `checkout_request_id` (M-Pesa), or `status: "succeeded"` for cash/manual.

---

## 3. Confirm Manual Payment (Paid at Till) — Treasury API

When the user clicks “I paid at till / agent” in the UI, the service backend can either:

- Call **initiate** with `payment_method: "manual"` (see above), or  
- Call **confirm-manual** for the intent:

**Endpoint**: `POST /api/v1/{tenant}/payments/intents/{intentID}/confirm-manual`  
**Auth**: Required.  
**Body**: Empty.  
**Effect**: Intent status set to `succeeded`; payment_method can be updated to `"manual"`.

---

## 4. Shared Pay Page (Treasury UI)

**URL**: Public; e.g. `https://books.codevertexitsolutions.com/pay`  
**Route**: `/(public)/pay` (no auth).

**Query parameters** (passed by the service frontend when redirecting):

| Parameter        | Required | Description                                      |
|-----------------|----------|--------------------------------------------------|
| `amount`        | Yes*     | Amount to pay (*or `intent_id` if amount from server) |
| `tenant`        | Yes      | Tenant ID (UUID)                                  |
| `intent_id`     | No       | Treasury payment intent ID (invoice-first flow)   |
| `invoice_number`| No       | Display only (e.g. INV-xxx or reference_id)       |
| `reference_id`  | No       | External reference (order id, subscription id)     |
| `reference_type`| No       | e.g. order, subscription                          |
| `currency`      | No       | Default KES                                       |
| `description`   | No       | Shown in summary                                  |
| `redirect_url`  | No       | Where to send user after payment (path or URL)    |
| `button_text`   | No       | Label for post-payment button (e.g. “View my order”) |
| `initiate_url`  | No       | Service backend URL to POST to initiate/confirm   |
| `gateways`      | No       | Comma-separated: paystack, mpesa, cod (default: all) |

**Page behavior**:

- Renders **invoice summary** at top (invoice number, amount, description).
- Renders **gateway cards** with official logos (Paystack, M-Pesa, COD) for the chosen `gateways`.
- On gateway click, opens the **respective payment modal** (Paystack, M-Pesa, or COD) with the same payment details.

**initiate_url** (recommended): The pay page and modals POST to this URL with body e.g. `{ intent_id, payment_method, customer_email?, phone_number? }`. The service backend then calls treasury-api `POST .../intents/{id}/initiate` (or confirm-manual) and returns `authorization_url`, `checkout_request_id`, or `redirect_url` so the UI can redirect or show “Check your phone”.

---

## 5. Payment Modals (Flexible, QR & Manual)

All payment dialogs in treasury-ui support:

- **Standard flow**: Paystack → redirect to `authorization_url`; M-Pesa → STK push, then optional “Check your phone” / redirect; COD → confirm and mark succeeded.
- **QR code**: When an `authorization_url` is returned (e.g. Paystack), the Paystack modal can show a **QR code** for that URL so the user can scan and pay on another device.
- **Manual / till**: An **“I paid at till / agent”** (or similar) button that POSTs `payment_method: "manual"` to `initiate_url`; the backend calls treasury-api initiate with `"manual"` or confirm-manual, then the UI redirects to `redirect_url`.

This applies in **all services** that use the shared pay page and in **treasury-ui** itself when it hosts payment flows.

---

## 6. Callback Page (After Payment)

After Paystack (or other redirect-based gateways) complete, the user lands on a **callback page** with `?reference=...` (and optionally `redirect_url`, `button_text`). See [paystack-callback-page.md](paystack-callback-page.md). The callback page is public; it may call a verify endpoint and then show a single button (custom text and URL) to continue.

---

## 7. Webhooks & Auto-Generated URLs

- **Webhook and callback URLs** for Paystack and M-Pesa are **auto-generated** in treasury-api from `HTTP_PUBLIC_BASE_URL` and fixed paths (see treasury-api docs and [paystack-and-platform-admin.md](../finance-service/treasury-api/docs/paystack-and-platform-admin.md)).
- Production base URL is set in `devops-k8s/apps/treasury-api/values.yaml` as `TREASURY_HTTP_PUBLIC_BASE_URL`.

---

## References

- [Paystack callback page](paystack-callback-page.md)
- [Treasury API Paystack & platform admin](../finance-service/treasury-api/docs/paystack-and-platform-admin.md)
- [Treasury API integrations](../finance-service/treasury-api/docs/integrations.md)
- Treasury-ui pay page: `finance-service/treasury-ui/src/app/(public)/pay/page.tsx`
- Payment modals: `finance-service/treasury-ui/src/components/payments/`
