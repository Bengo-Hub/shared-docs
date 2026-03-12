# Paystack API Integration Reference

> **Source**: [Paystack Developer Documentation](https://paystack.com/docs/api/)  
> **Base URL**: `https://api.paystack.co`  
> **Auth**: `Authorization: Bearer sk_live_<secret_key>` (all requests)  
> **Updated**: March 2026

---

## Treasury payment workflow (high level)

Services create a payment intent (invoice) via treasury-api with `payment_method: "pending"`, then redirect users to the **shared pay page** (treasury-ui `/pay`). User selects Paystack (or M-Pesa, COD); the UI calls the service’s `initiate_url`, which calls treasury-api `POST .../intents/{id}/initiate` with `payment_method: "paystack"`. Treasury returns `authorization_url`; user is redirected to Paystack. After payment, user lands on the app’s **callback page**; webhooks update the intent. Payment modals support **QR code** (scan to pay) and **“I paid at till”** (manual confirmation). See [payment-workflow.md](payment-workflow.md).

---

## Platform Configuration

The Paystack account belongs to **Codevertex** (platform owner). All tenant payments are collected into the platform Paystack account. Funds are redistributed to tenant accounts via Paystack Transfers.

| Config Level | Who Sets It | Fields |
|---|---|---|
| **Platform** | Codevertex superadmin | `PAYSTACK_SECRET_KEY`, `PAYSTACK_PUBLIC_KEY`, `PAYSTACK_WEBHOOK_SECRET` |
| **Tenant** | Tenant admin | Payout account details (recipient_code created via Paystack Transfer Recipients API) |

---

## 1. Transactions — Initiate Payment

**Purpose**: Start a hosted checkout payment (card, bank, USSD, mobile money, QR).  
**Endpoint**: `POST /transaction/initialize`

```json
{
  "amount": 10000,
  "email": "customer@example.com",
  "currency": "KES",
  "reference": "ORDER-123-uuid",
  "callback_url": "https://app.bengobox.com/payments/verify?ref=ORDER-123",
  "metadata": {
    "order_id": "uuid",
    "tenant_id": "uuid",
    "source_service": "ordering"
  },
  "channels": ["card", "bank_transfer", "mobile_money", "ussd"]
}
```

**Amount**: In lowest currency unit (KES cents = kobo equivalent, but KES uses 100 kobos per shilling). For KES 100 → `amount: 10000`.

**Response**: Returns `authorization_url` (redirect customer here) and `access_code`.

**Channels** supported for Kenya: `card`, `bank_transfer`, `mobile_money` (M-Pesa via Paystack), `ussd`.

### Kenya Mobile Money Channel (Paystack-proxied M-Pesa)
```json
{
  "amount": 10000,
  "email": "customer@example.com",
  "currency": "KES",
  "channels": ["mobile_money"],
  "mobile_money": {
    "phone": "0712345678",
    "provider": "mpesa"
  }
}
```

---

## 2. Transactions — Verify Payment

**Purpose**: Verify a transaction after customer returns from checkout (or on webhook receipt).  
**Endpoint**: `GET /transaction/verify/:reference`

```json
{
  "status": true,
  "data": {
    "reference": "ORDER-123-uuid",
    "status": "success",
    "amount": 10000,
    "currency": "KES",
    "paid_at": "2026-03-09T12:00:00.000Z",
    "gateway_response": "Successful",
    "channel": "card",
    "fees": 150,
    "customer": {"email": "customer@example.com"},
    "metadata": {"order_id": "uuid", "tenant_id": "uuid"}
  }
}
```

**Statuses**: `success`, `failed`, `abandoned`, `ongoing`, `pending`.

---

## 3. Transactions — List

**Endpoint**: `GET /transaction?perPage=50&page=1&status=success&from=2026-01-01&to=2026-03-31&customer=<email>`

---

## 4. Webhooks

Configure webhook URL in Paystack Dashboard → Settings → API Keys & Webhooks.

**Endpoint receives**: `POST /webhooks/paystack`  
**Verify**: `x-paystack-signature: HMAC-SHA512(request_body, secret_key)` — already implemented in `treasury-api`.

**Events**:
| Event | Trigger |
|---|---|
| `charge.success` | Payment completed successfully |
| `charge.dispute.create` | Customer raised chargeback |
| `charge.dispute.resolve` | Chargeback resolved |
| `transfer.success` | B2C transfer (payout) succeeded |
| `transfer.failed` | Transfer failed |
| `transfer.reversed` | Transfer reversed after failure |
| `invoice.create` | Subscription invoice generated |
| `invoice.update` | Invoice updated |
| `invoice.payment_failed` | Subscription payment failed |
| `subscription.create` | New subscription activated |
| `subscription.disable` | Subscription paused |
| `subscription.expiring_cards` | Customer card expiring |
| `paymentrequest.success` | Payment link paid (Paystack Invoice) |
| `refund.processed` | Refund completed |

---

## 5. Refunds

**Endpoint**: `POST /refund`

```json
{
  "transaction": "transaction_reference_or_id",
  "amount": 5000,
  "currency": "KES",
  "customer_note": "Order cancelled by customer",
  "merchant_note": "Refund for order #123"
}
```

Full refund: omit `amount`. Partial refund: specify `amount` in lowest denomination.

---

## 6. Transfer Recipients — Create

**Purpose**: Register a tenant's bank account or mobile money wallet to receive payouts.  
**Endpoint**: `POST /transferrecipient`

### Bank Account (Kenya)
```json
{
  "type": "nuban",
  "name": "Urban Loft Cafe",
  "account_number": "0001234567",
  "bank_code": "068",
  "currency": "KES"
}
```

### M-Pesa (Mobile Money)
```json
{
  "type": "mobile_money",
  "name": "Urban Loft Cafe",
  "account_number": "0712345678",
  "bank_code": "MPESA_KE",
  "currency": "KES"
}
```

**Response**: Returns `recipient_code` (e.g., `RCP_12abc`). Store as `payout_config.recipient_code`.

---

## 7. Transfer Recipients — List Banks

**Purpose**: Get list of banks and mobile money providers for a country.  
**Endpoint**: `GET /bank?country=kenya&pay_with_bank_transfer=true&type=mobile_money`

Returns array of banks with `code` and `name`. Used to populate payout account form dropdowns.

---

## 8. Transfers — Initiate Single Transfer (Payout)

**Purpose**: Send collected funds to a tenant's registered account.  
**Endpoint**: `POST /transfer`

```json
{
  "source": "balance",
  "amount": 500000,
  "recipient": "RCP_abc12",
  "reason": "Weekly payout - Week 2026-W10",
  "currency": "KES",
  "reference": "PAYOUT-tenant-uuid-2026-W10"
}
```

**Note**: Transfers in Kenya require OTP approval (unless OTP is disabled in Dashboard). For production automation, enable "Disable OTP" in Paystack Settings.

**Response**:
```json
{
  "transfer_code": "TRF_1234",
  "reference": "PAYOUT-tenant-uuid-2026-W10",
  "status": "pending"
}
```

---

## 9. Transfers — Initiate Bulk Transfer (Equity Payouts)

**Purpose**: Send payouts to multiple equity holders in one API call.  
**Endpoint**: `POST /transfer/bulk`

```json
{
  "currency": "KES",
  "source": "balance",
  "transfers": [
    {
      "amount": 150000,
      "recipient": "RCP_holder1",
      "reason": "Q1 2026 royalty — ordering service",
      "reference": "EQUITY-holder1-Q12026"
    },
    {
      "amount": 80000,
      "recipient": "RCP_holder2",
      "reason": "Q1 2026 shareholder dividend",
      "reference": "EQUITY-holder2-Q12026"
    }
  ]
}
```

---

## 10. Transfers — Verify Transfer

**Endpoint**: `GET /transfer/verify/:reference`

Returns current status: `success`, `failed`, `pending`, `reversed`.

---

## 11. Settlements — List (Paystack → Platform Bank Account)

**Purpose**: View Paystack auto-settlement payouts to the platform's bank account.  
**Endpoint**: `GET /settlement?perPage=50&page=1&from=2026-01-01&to=2026-03-31`

**Note**: Paystack automatically settles collected funds to the platform's nominated bank account on a T+1 or T+2 basis depending on account type.

---

## 12. Balance — Check Platform Balance

**Endpoint**: `GET /balance`

```json
{
  "currency": "KES",
  "balance": 1250000
}
```

Used before initiating transfers to ensure sufficient balance.

---

## 13. Subscriptions API (Recurring Billing for SaaS Plans)

**Purpose**: Charge tenants recurring subscription fees via card-on-file or direct debit.

### Create Plan
`POST /plan`
```json
{
  "name": "GROWTH Plan",
  "interval": "monthly",
  "amount": 499900,
  "currency": "KES"
}
```

### Create Subscription
`POST /subscription`
```json
{
  "customer": "customer_code",
  "plan": "PLN_abc",
  "authorization": "AUTH_xyz"
}
```

### Disable/Enable Subscription
`POST /subscription/disable` | `POST /subscription/enable`

**Integration note**: `subscriptions-api` manages the subscription lifecycle. When a tenant pays via Paystack, the authorization token is stored and used for future recurring charges.

---

## 14. Payment Pages / Payment Links

**Purpose**: Generate shareable payment links (e.g., for invoices, subscription upgrade prompts).  
**Endpoint**: `POST /page`

```json
{
  "name": "Upgrade to GROWTH Plan",
  "description": "Monthly subscription payment",
  "amount": 499900,
  "currency": "KES",
  "metadata": {"tenant_id": "uuid", "plan": "GROWTH"}
}
```

Returns `link` (e.g., `https://paystack.com/pay/bengobox-growth`).

---

## 15. QR Code Payments (South Africa only)

> [!IMPORTANT]
> Paystack QR code payments (Visa QR) are **not available in Kenya** as of 2025. For QR payments in Kenya, use **M-Pesa QR Code** (see `mpesa-integration-reference.md`).

---

## 16. Dedicated Virtual Accounts (DVA)

**Purpose**: Generate a dedicated bank account number per customer for seamless bank transfer payments.  
**Availability**: Nigeria currently; available in Ghana (June 2025). **Not available in Kenya yet.**

---

## Transaction Fee Calculation

Paystack Kenya fee matrix (charged to platform, passed to tenants as line item on payouts):

| Payment Method | Fee |
|---|---|
| Card (Visa/Mastercard) | 1.5% + KES 20 (capped at KES 2,500) |
| Bank Transfer | KES 50 flat |
| Mobile Money | 0.5% (no cap) |
| USSD | KES 30 flat |

**Formula for fee estimate UI**:
```ts
function estimatePaystackFee(amount: number, method: string): number {
  switch (method) {
    case 'card': return Math.min(amount * 0.015 + 20, 2500)
    case 'bank_transfer': return 50
    case 'mobile_money': return amount * 0.005
    case 'ussd': return 30
    default: return 0
  }
}
```

---

## Environment Variables

```bash
# Treasury API (.env / K8s secrets)
PAYSTACK_SECRET_KEY=sk_live_...
PAYSTACK_PUBLIC_KEY=pk_live_...
PAYSTACK_WEBHOOK_SECRET=<your webhook secret>
# Webhook and callback URLs are auto-generated from HTTP_PUBLIC_BASE_URL (TruLoad pattern):
# Webhook: {HTTP_PUBLIC_BASE_URL}/api/v1/webhooks/paystack
# Callback (user redirect): {HTTP_PUBLIC_BASE_URL}/api/v1/payments/callback
HTTP_PUBLIC_BASE_URL=https://booksapi.codevertexitsolutions.com
# Optional overrides (if not set, auto-generated URLs are used):
# PAYSTACK_CALLBACK_URL=...
# PAYSTACK_WEBHOOK_URL=...
```

---

## References

- [Paystack API Docs](https://paystack.com/docs/api/)
- [Paystack Dashboard](https://dashboard.paystack.com)
- Existing Paystack implementation: `finance-service/treasury-api/internal/modules/gateways/paystack.go`
- Existing Paystack webhook handler: `finance-service/treasury-api/internal/http/handlers/payments.go#PaystackWebhook`
