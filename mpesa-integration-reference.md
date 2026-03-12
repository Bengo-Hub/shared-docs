# M-Pesa Daraja API Integration Reference

> **Sources**: Safaricom APIs Postman collection (`shared-docs/mpesa apis/Safaricom APIs.postman_collection.json`), Safaricom Daraja Developer Portal.
> **Updated**: March 2026

---

## Treasury payment workflow (high level)

Services create a payment intent via treasury-api with `payment_method: "pending"`, then redirect to the **shared pay page** (treasury-ui `/pay`). User selects M-Pesa; the modal sends phone number to the service’s `initiate_url`, which calls treasury-api `POST .../intents/{id}/initiate` with `payment_method: "mpesa"`. Treasury triggers STK Push; user completes on phone. Modals support **“I paid at till / agent”** for manual confirmation. See [payment-workflow.md](payment-workflow.md).

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
  "CallBackURL": "https://booksapi.codevertexitsolutions.com/api/v1/webhooks/mpesa/callback",
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
  "ConfirmationURL": "https://booksapi.codevertexitsolutions.com/webhooks/mpesa/confirmation",
  "ValidationURL": "https://booksapi.codevertexitsolutions.com/webhooks/mpesa/validation"
}
```

Must be registered once per production shortcode. Sandbox uses simulate.

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
  "InitiatorName": "bengobox_initiator",
  "SecurityCredential": "<RSA encrypted initiator password>",
  "CommandID": "BusinessPayment",
  "Amount": "5000",
  "PartyA": "600000",
  "PartyB": "254708374149",
  "Remarks": "Rider payout week 2026-W10",
  "QueueTimeOutURL": "https://booksapi.codevertexitsolutions.com/webhooks/mpesa/b2c-timeout",
  "ResultURL": "https://booksapi.codevertexitsolutions.com/webhooks/mpesa/b2c-result",
  "Occasion": "WeeklyPayout"
}
```

**CommandID options**: 
- `BusinessPayment` — (no tax) general business payment
- `SalaryPayment` — salary disbursement
- `PromotionPayment` — for cashback/promotions

**SecurityCredential**: RSA-encrypt initiator password using M-Pesa public key certificate.

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
  "Initiator": "bengobox_initiator",
  "SecurityCredential": "<RSA encrypted>",
  "CommandID": "BusinessPayBill",
  "SenderIdentifierType": "4",
  "RecieverIdentifierType": "4",
  "Amount": "10000",
  "PartyA": "600000",
  "PartyB": "600001",
  "AccountReference": "Invoice001",
  "Remarks": "Supplier payment",
  "QueueTimeOutURL": "https://booksapi.codevertexitsolutions.com/webhooks/mpesa/b2b-timeout",
  "ResultURL": "https://booksapi.codevertexitsolutions.com/webhooks/mpesa/b2b-result"
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
  "Initiator": "bengobox_initiator",
  "SecurityCredential": "<RSA encrypted>",
  "CommandID": "TransactionStatusQuery",
  "TransactionID": "LHG31AA5TX",
  "PartyA": "600000",
  "IdentifierType": "4",
  "ResultURL": "https://booksapi.codevertexitsolutions.com/webhooks/mpesa/txn-status-result",
  "QueueTimeOutURL": "https://booksapi.codevertexitsolutions.com/webhooks/mpesa/txn-timeout",
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
  "Initiator": "bengobox_initiator",
  "SecurityCredential": "<RSA encrypted>",
  "CommandID": "TransactionReversal",
  "TransactionID": "OEI2AK4Q16",
  "Amount": "100",
  "ReceiverParty": "600000",
  "RecieverIdentifierType": "4",
  "ResultURL": "https://booksapi.codevertexitsolutions.com/webhooks/mpesa/reversal-result",
  "QueueTimeOutURL": "https://booksapi.codevertexitsolutions.com/webhooks/mpesa/timeout",
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
  "Initiator": "bengobox_initiator",
  "SecurityCredential": "<RSA encrypted>",
  "CommandID": "AccountBalance",
  "PartyA": "600000",
  "IdentifierType": "4",
  "Remarks": "Balance check",
  "QueueTimeOutURL": "https://booksapi.codevertexitsolutions.com/webhooks/mpesa/timeout",
  "ResultURL": "https://booksapi.codevertexitsolutions.com/webhooks/mpesa/balance-result"
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
  "CallBackURL": "https://booksapi.codevertexitsolutions.com/webhooks/mpesa/ratiba",
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
  "MerchantName": "Urban Loft Cafe",
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

| M-Pesa Event | Internal Route |
|---|---|
| STK Push callback | `POST /webhooks/mpesa/callback` |
| C2B Validation | `POST /webhooks/mpesa/validation` |
| C2B Confirmation | `POST /webhooks/mpesa/confirmation` |
| B2C Result | `POST /webhooks/mpesa/b2c-result` |
| B2C Timeout | `POST /webhooks/mpesa/b2c-timeout` |
| B2B Result | `POST /webhooks/mpesa/b2b-result` |
| Transaction Status Result | `POST /webhooks/mpesa/txn-status-result` |
| Transaction Reversal Result | `POST /webhooks/mpesa/reversal-result` |
| Account Balance Result | `POST /webhooks/mpesa/balance-result` |
| M-Pesa Ratiba | `POST /webhooks/mpesa/ratiba` |

---

## RSA Security Credential Generation

Required for B2C, B2B, Transaction Status, Reversal, Account Balance:
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

Certificates: [sandbox](https://developer.safaricom.co.ke/sites/default/files/cert/cert_sandbox/cert.cer) | [production](https://developer.safaricom.co.ke/sites/default/files/cert/cert_prod/cert.cer).

---

## References

- [Daraja Portal](https://developer.safaricom.co.ke)
- Postman Collection: `shared-docs/mpesa apis/Safaricom APIs.postman_collection.json`
- Existing M-Pesa implementation: `finance-service/treasury-api/internal/modules/gateways/mpesa.go`
