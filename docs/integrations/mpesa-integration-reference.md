# M-Pesa Daraja API Integration Reference

> **Sources**: Safaricom APIs Postman collection (`shared-docs/mpesa apis/Safaricom APIs.postman_collection.json` — refreshed 2026-08-22 from a 2026-06 Daraja Developer Portal export; single canonical copy, was previously duplicated 19x under `finance-service/resources/m-pesa-apis/`), Safaricom Daraja Developer Portal.
> **Updated**: August 2026

---

## Treasury payment workflow

See [payment-workflow.md](payment-workflow.md) for the full end-to-end flow (intent creation, shared pay page, `initiate_url`, gateway redirect). This page covers only the M-Pesa/Daraja API specifics: STK Push triggering, manual "I paid at till/agent" confirmation, and the credential model below.

---

## Two-Tier Configuration Model

| Tier | Owner | Scope | Fields |
|------|-------|-------|--------|
| **Platform (Tier 1)** | Codevertex superadmin | Shared across all tenants | `consumer_key`, `consumer_secret`, `passkey`, `environment` (sandbox/production) |
| **Tenant (Tier 2)** | Tenant admin | Unique per tenant | `shortcode` (Paybill or Till), `initiator_name`, `initiator_password`, `account_reference` |

**Storage**: Tier 1 credentials stored in encrypted `credentials` JSON blob in `GatewayConfig` table (encrypted at rest). Tier 2 fields stored as plain columns (`mpesa_shortcode`, `mpesa_initiator_name`, `mpesa_initiator_password` encrypted, `mpesa_account_ref`) on the tenant-level `GatewayConfig` row.

---

## Authentication

All M-Pesa Daraja APIs require an OAuth 2.0 Bearer token obtained from:

```
GET https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials
Authorization: Basic base64(consumer_key:consumer_secret)
```

**Sandbox**: `https://sandbox.safaricom.co.ke`  
**Production**: `https://api.safaricom.co.ke`

Token expires in 3600 seconds. Cache and refresh before expiry.

---

## 1. STK Push (Lipa Na M-Pesa Online / Express)

**Purpose**: Initiate customer-to-business (C2B) payment via a push prompt to the customer's phone.  
**Use case**: Online orders, checkout payments.

**Endpoint**: `POST /mpesa/stkpush/v1/processrequest`

### Request
```json
{
  "BusinessShortCode": "174379",
  "Password": "<base64(shortcode + passkey + timestamp)>",
  "Timestamp": "20250925124519",
  "TransactionType": "CustomerPayBillOnline",
  "Amount": "100",
  "PartyA": "254708374149",
  "PartyB": "174379",
  "PhoneNumber": "254708374149",
  "CallBackURL": "https://booksapi.codevertexafrica.com/api/v1/webhooks/mpesa/callback",
  "AccountReference": "OrderRef123",
  "TransactionDesc": "Payment for Order #123"
}
```

**Password generation**:
```go
timestamp := time.Now().Format("20060102150405")
password := base64.StdEncoding.EncodeToString([]byte(shortcode + passkey + timestamp))
```

**TransactionType**: `CustomerPayBillOnline` (Paybill) | `CustomerBuyGoodsOnline` (Till)

### Response
```json
{
  "MerchantRequestID": "29115-34620561-1",
  "CheckoutRequestID": "ws_CO_191220191020363925",
  "ResponseCode": "0",
  "ResponseDescription": "Success. Request accepted for processing",
  "CustomerMessage": "Success. Request accepted for processing"
}
```

**Callback** (async, received at `CallBackURL`):
```json
{
  "Body": {
    "stkCallback": {
      "MerchantRequestID": "29115-34620561-1",
      "CheckoutRequestID": "ws_CO_191220191020363925",
      "ResultCode": 0,
      "ResultDesc": "The service request is processed successfully.",
      "CallbackMetadata": {
        "Item": [
          {"Name": "Amount", "Value": 1.00},
          {"Name": "MpesaReceiptNumber", "Value": "NLJ7RT61SV"},
          {"Name": "TransactionDate", "Value": 20191219102115},
          {"Name": "PhoneNumber", "Value": 254708374149}
        ]
      }
    }
  }
}
```

`ResultCode: 0` = success. Any other code = failure.

---

## 2. STK Push Query

**Purpose**: Poll the status of an STK Push transaction (use when callback wasn't received).  
**Endpoint**: `POST /mpesa/stkpushquery/v1/query`

```json
{
  "BusinessShortCode": "174379",
  "Password": "<same as STK push>",
  "Timestamp": "20250925124519",
  "CheckoutRequestID": "ws_CO_191220191020363925"
}
```

**Response**: `ResultCode: 0` = paid; `1032` = user cancelled; `1037` = timeout.

---

## 3. C2B — Register URLs

**Purpose**: Register confirmation/validation URLs for over-the-counter C2B payments (paybill, till).  
**Endpoint**: `POST /mpesa/c2b/v1/registerurl`

```json
{
  "ShortCode": "600000",
  "ResponseType": "Completed",
  "ConfirmationURL": "https://booksapi.codevertexafrica.com/api/v1/webhooks/c2b/confirmation",
  "ValidationURL": "https://booksapi.codevertexafrica.com/api/v1/webhooks/c2b/validation"
}
```

Must be registered once per production shortcode. Sandbox uses simulate.

**Two gotchas confirmed live against the sandbox (2026-08-22), both now fixed in code
(`urls.MpesaConfirmationURL`/`MpesaValidationURL`) but worth knowing if you're hand-building these
URLs elsewhere:**
- The URL must include the API's real path prefix (`/api/v1/webhooks/...` here) — a URL missing it
  404s on our own server the moment Daraja tries to deliver a confirmation, even though registration
  itself appears to succeed.
- Daraja's RegisterURL rejects any Confirmation/ValidationURL containing the substring **"mpesa"**
  outright, with `400.003.02 "Bad Request - Invalid ValidationURL - URL has the word MPESA"` — hence
  `/webhooks/c2b/...`, not `/webhooks/mpesa/...`, for these two specific URLs. Every other `mpesa/*`
  webhook (STK callback, B2C/B2B results, txn-status, reversal, balance) is unaffected — those are
  passed to different Daraja APIs (as `ResultURL`/`QueueTimeOutURL`) that were not observed to apply
  the same filter.

---

## 4. C2B — Simulate (Sandbox Only)

**Endpoint**: `POST /mpesa/c2b/v1/simulate`

```json
{
  "ShortCode": "600000",
  "CommandID": "CustomerPayBillOnline",
  "Amount": 100,
  "Msisdn": "254708374149",
  "BillRefNumber": "account123"
}
```

---

## 5. B2C — Business to Customer (Payouts to Users)

**Purpose**: Send money from business shortcode to customer M-Pesa account.  
**Use cases**: Rider earnings payouts, refunds, cashback, loyalty redemption.  
**Endpoint**: `POST /mpesa/b2c/v1/paymentrequest`

```json
{
  "InitiatorName": "YOUR_INITIATOR_NAME",
  "SecurityCredential": "<RSA encrypted initiator password>",
  "CommandID": "BusinessPayment",
  "Amount": "5000",
  "PartyA": "600000",
  "PartyB": "254708374149",
  "Remarks": "Rider payout week 2026-W10",
  "QueueTimeOutURL": "https://booksapi.codevertexafrica.com/webhooks/mpesa/b2c-timeout",
  "ResultURL": "https://booksapi.codevertexafrica.com/webhooks/mpesa/b2c-result",
  "Occasion": "WeeklyPayout"
}
```

**CommandID options**: 
- `BusinessPayment` — (no tax) general business payment
- `SalaryPayment` — salary disbursement
- `PromotionPayment` — for cashback/promotions

**SecurityCredential**: RSA-encrypt initiator password using M-Pesa public key certificate. See
"Initiator SecurityCredential" below for where this cert actually comes from in this codebase and its
current admin UI.

**Result callback**:
```json
{
  "Result": {
    "ResultCode": 0,
    "TransactionID": "LGR019G3J2",
    "ResultParameters": {
      "ResultParameter": [
        {"Key": "TransactionAmount", "Value": 5000},
        {"Key": "TransactionReceipt", "Value": "LGR019G3J2"},
        {"Key": "ReceiverPartyPublicName", "Value": "254708374149 - John Doe"}
      ]
    }
  }
}
```

---

## 6. B2B — Business to Business

**Purpose**: Shortcode-to-shortcode payments (e.g., pay supplier's paybill).  
**Endpoint**: `POST /mpesa/b2b/v1/paymentrequest`

```json
{
  "Initiator": "YOUR_INITIATOR_NAME",
  "SecurityCredential": "<RSA encrypted>",
  "CommandID": "BusinessPayBill",
  "SenderIdentifierType": "4",
  "RecieverIdentifierType": "4",
  "Amount": "10000",
  "PartyA": "600000",
  "PartyB": "600001",
  "AccountReference": "Invoice001",
  "Remarks": "Supplier payment",
  "QueueTimeOutURL": "https://booksapi.codevertexafrica.com/webhooks/mpesa/b2b-timeout",
  "ResultURL": "https://booksapi.codevertexafrica.com/webhooks/mpesa/b2b-result"
}
```

**CommandID**: `BusinessPayBill` | `MerchantToMerchantTransfer` | `MerchantTransferFromMerchantToWorking`

---

## 7. B2Pochi — Business to Pochi (Individual Till)

**Endpoint**: Same as B2C (`/mpesa/b2c/v1/paymentrequest`)  
**CommandID**: `BusinessPayment` with PartyB as the Pochi till number.

---

## 8. Transaction Status Query

**Purpose**: Query the status of any M-Pesa transaction.  
**Endpoint**: `POST /mpesa/transactionstatus/v1/query`

```json
{
  "Initiator": "YOUR_INITIATOR_NAME",
  "SecurityCredential": "<RSA encrypted>",
  "CommandID": "TransactionStatusQuery",
  "TransactionID": "LHG31AA5TX",
  "PartyA": "600000",
  "IdentifierType": "4",
  "ResultURL": "https://booksapi.codevertexafrica.com/webhooks/mpesa/txn-status-result",
  "QueueTimeOutURL": "https://booksapi.codevertexafrica.com/webhooks/mpesa/txn-timeout",
  "Remarks": "Status check",
  "Occasion": ""
}
```

---

## 9. Transaction Reversal

**Purpose**: Reverse a completed M-Pesa transaction (within 24 hours).  
**Endpoint**: `POST /mpesa/reversal/v1/request`

```json
{
  "Initiator": "YOUR_INITIATOR_NAME",
  "SecurityCredential": "<RSA encrypted>",
  "CommandID": "TransactionReversal",
  "TransactionID": "OEI2AK4Q16",
  "Amount": "100",
  "ReceiverParty": "600000",
  "RecieverIdentifierType": "4",
  "ResultURL": "https://booksapi.codevertexafrica.com/webhooks/mpesa/reversal-result",
  "QueueTimeOutURL": "https://booksapi.codevertexafrica.com/webhooks/mpesa/timeout",
  "Remarks": "Duplicate payment reversal",
  "Occasion": ""
}
```

---

## 10. Account Balance Query

**Purpose**: Query current M-Pesa shortcode balance.  
**Endpoint**: `POST /mpesa/accountbalance/v1/query`

```json
{
  "Initiator": "YOUR_INITIATOR_NAME",
  "SecurityCredential": "<RSA encrypted>",
  "CommandID": "AccountBalance",
  "PartyA": "600000",
  "IdentifierType": "4",
  "Remarks": "Balance check",
  "QueueTimeOutURL": "https://booksapi.codevertexafrica.com/webhooks/mpesa/timeout",
  "ResultURL": "https://booksapi.codevertexafrica.com/webhooks/mpesa/balance-result"
}
```

---

## 11. M-Pesa Ratiba / Standing Orders

**Purpose**: Schedule recurring customer-to-business payments.  
**Endpoint**: `POST /standingorder/v1/createStandingOrderExternal`

```json
{
  "StandingOrderName": "Monthly Subscription",
  "BusinessShortCode": "174379",
  "TransactionType": "Standing Order Customer Pay Bill",
  "Amount": "500",
  "PartyA": "254708374149",
  "ReceiverPartyIdentifierType": "4",
  "CallBackURL": "https://booksapi.codevertexafrica.com/webhooks/mpesa/ratiba",
  "AccountReference": "SubRef123",
  "TransactionDesc": "Monthly subscription",
  "Frequency": "3",
  "StartDate": "20260310",
  "EndDate": "20271231"
}
```

**Frequency**: `1`=daily, `2`=weekly, `3`=monthly, `4`=quarterly, `5`=half-yearly, `6`=yearly.  
**TransactionType**: `"Standing Order Customer Pay Bill"` (Paybill) | `"Standing Order Customer Pay Merchant"` (Till/Buy Goods).

**Use case**: Subscription billing — when a tenant enables M-Pesa, create a standing order to auto-collect monthly subscription fees.

---

## 12. QR Code Generation

**Purpose**: Generate a static QR code for the tenant's shortcode (customers scan with M-Pesa app).  
**Endpoint**: `POST /mpesa/qrcode/v1/generate`

```json
{
  "MerchantName": "Acme Retail",
  "RefNo": "cafe-checkout-01",
  "Amount": "500",
  "TrxCode": "PB",
  "CPI": "174379",
  "Size": "300"
}
```

**TrxCode**: `PB` = Paybill | `BG` = Buy Goods | `WA` = Wallet-to-Account | `SB` = Subscriber-to-Bank.

Returns a base64-encoded PNG of the QR code.

---

## Webhook Endpoints in treasury-api

All paths below are relative to `PublicBaseURL` and require the `/api/v1` prefix (e.g.
`https://booksapi.codevertexafrica.com/api/v1/webhooks/mpesa/callback`) — every URL builder now goes
through `internal/pkg/urls`'s `MpesaXxxURL` helpers (single source of truth, confirmed live
2026-08-22 after finding several of these were previously missing this prefix entirely and being
submitted to Daraja as bare relative paths).

| M-Pesa Event | Internal Route | Built via |
|---|---|---|
| STK Push callback | `POST /api/v1/webhooks/mpesa/callback` | `urls.MpesaCallbackURL` |
| C2B Validation | `POST /api/v1/webhooks/c2b/validation` | `urls.MpesaValidationURL` |
| C2B Confirmation | `POST /api/v1/webhooks/c2b/confirmation` | `urls.MpesaConfirmationURL` |
| B2C Result | `POST /api/v1/webhooks/mpesa/b2c-result` | `urls.MpesaB2CResultURL` |
| B2C Timeout | `POST /api/v1/webhooks/mpesa/b2c-timeout` | `urls.MpesaB2CTimeoutURL` |
| B2B Result | `POST /api/v1/webhooks/mpesa/b2b-result` | `urls.MpesaB2BResultURL` |
| B2B Timeout | `POST /api/v1/webhooks/mpesa/b2b-timeout` | `urls.MpesaB2BTimeoutURL` |
| Transaction Status Result | `POST /api/v1/webhooks/mpesa/txn-status-result` | `urls.MpesaTxnStatusURL` |
| Transaction Reversal Result | `POST /api/v1/webhooks/mpesa/reversal-result` | `urls.MpesaReversalURL` |
| Account Balance Result | `POST /api/v1/webhooks/mpesa/balance-result` | `urls.MpesaBalanceURL` |
| M-Pesa Ratiba | `POST /api/v1/webhooks/mpesa/ratiba` | `urls.MpesaRatibaURL` |
| Shared QueueTimeOutURL | `POST /api/v1/webhooks/mpesa/timeout` | `urls.MpesaTimeoutURL` |

**Note on C2B's `/webhooks/c2b/...` paths** (not `/webhooks/mpesa/...` like everything else): Daraja's
RegisterURL API rejects any Confirmation/ValidationURL containing the substring "mpesa" outright, with
a hard `400.003.02 "URL has the word MPESA"` — confirmed live 2026-08-22. Every other path above is
fine to contain "mpesa" since it's passed as `ResultURL`/`QueueTimeOutURL` to a *different* Daraja API
(B2C/B2B/balance/etc.) that was not observed to apply the same filter.

---

## Initiator SecurityCredential (RSA-encrypted initiator password)

Required for B2C, B2B, Transaction Status, Reversal, Account Balance — every Daraja command that
authenticates as an "Initiator" rather than just the OAuth app. `MpesaGateway.generateSecurityCredential`
(mpesa.go) does this at runtime:
```go
// Encrypt initiator password with M-Pesa public key certificate
func generateSecurityCredential(initiatorPassword, certPath string) (string, error) {
    certPEM, _ := os.ReadFile(certPath)
    block, _ := pem.Decode(certPEM)
    cert, _ := x509.ParseCertificate(block.Bytes)
    rsaKey := cert.PublicKey.(*rsa.PublicKey)
    encrypted, _ := rsa.EncryptPKCS1v15(rand.Reader, rsaKey, []byte(initiatorPassword))
    return base64.StdEncoding.EncodeToString(encrypted), nil
}
```

**Where the certificate actually comes from** (checked live 2026-08-22): `cert_pem` credential
(inline PEM, preferred — no file mount needed) → `cert_path` credential (filesystem path) →
`MPESA_SANDBOX_CERT_PATH`/`MPESA_PROD_CERT_PATH` env vars → **if none of those are set, silently
falls back to sending the initiator password UNENCRYPTED (base64 only)**. Confirmed none are
currently configured in the treasury-api deployment (no matching env vars, no volume mounts) — every
initiator-authenticated call has been running on the unencrypted fallback, which sandbox tolerates
but production would reject.

**This is environment-scoped (sandbox vs production), not per-tenant or per-app** — it's Safaricom's
own infrastructure public key, identical for every developer/tenant in that environment, so it's set
once at the **platform level** (Settings → Platform → Gateways → M-Pesa Paybill/Till → "cert pem"
field) and every tenant inherits it via the existing `ResolveConfig`/`MergeCredentials` chain — no
tenant-level field exists or is needed for this specific credential.

**Certificates** (current working URLs, found in a saved 2026-06 Daraja portal capture — the URLs
previously documented here, `developer.safaricom.co.ke/sites/default/files/cert/cert_{sandbox,prod}/cert.cer`,
now 404): [sandbox](https://developer.safaricom.co.ke/certificates/SandboxCertificate.cer) |
[production](https://developer.safaricom.co.ke/certificates/ProductionCertificate.cer). Both are
saved (verified working 2026-08-22) as `shared-docs/mpesa apis/{Sandbox,Production}Certificate.cer` —
the same tracked location as the Postman collection, unlike `finance-service/resources/m-pesa-apis/`
which is NOT a git repo at all (nothing saved there persists past the local machine). Both certs are
technically X.509-expired (2016 and 2018 respectively) but still valid for this use: Daraja's
SecurityCredential flow only extracts the RSA public key for encryption, it doesn't check certificate
expiry, and Safaricom continues to publish and expect these exact certs.

---

## References

- [Daraja Portal](https://developer.safaricom.co.ke)
- Postman Collection: `shared-docs/mpesa apis/Safaricom APIs.postman_collection.json`
- Existing M-Pesa implementation: `finance-service/treasury-api/internal/modules/gateways/mpesa.go`
