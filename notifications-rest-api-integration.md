# Notifications REST API Integration Guide

**Last Updated:** March 2026

## Overview

Non-Go services (TruLoad/.NET, ERP/Python) that don't use NATS can send notifications via the notifications-api REST endpoint. Go services should prefer the NATS event-driven pattern documented in [event-architecture.md](./event-architecture.md).

---

## Endpoint

```
POST https://notifications-api.bengobox.svc.cluster.local:4000/{tenantId}/notifications/messages
```

**Production (via ingress):**
```
POST https://notificationsapi.codevertexitsolutions.com/{tenantId}/notifications/messages
```

### Authentication

Either:
- `Authorization: Bearer <JWT>` — user JWT from auth-api
- `X-API-Key: <key>` — service API key

### Request Body

```json
{
  "channel": "email",
  "template": "truload/weight_ticket",
  "to": ["recipient@example.com"],
  "data": {
    "name": "John Doe",
    "ticket_number": "WT-2026-001",
    "vehicle_reg": "KDA 123A"
  },
  "metadata": {
    "subject": "Your Weight Ticket is Ready"
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `channel` | string | Yes | `email`, `sms`, `push`, `whatsapp` |
| `template` | string | Yes | Template path (e.g. `truload/weight_ticket`) — without channel prefix |
| `to` | string[] | Yes | Recipients (emails, phone numbers, or device tokens) |
| `data` | object | Yes | Template variables |
| `metadata` | object | No | `subject` for emails, `provider` override, `push_title` for push |

### Response

```json
{
  "status": "accepted",
  "requestId": "uuid-string"
}
```

**Status code:** `202 Accepted`

### Idempotency

- Pass `Idempotency-Key` header (optional) — 24-hour deduplication window
- If omitted, a key is derived from payload hash

### Rate Limiting

- Per-channel rate limits (configurable per tenant)
- Email: limited by `max_emails_per_day` from JWT subscription limits
- Returns `429 Too Many Requests` when exceeded

---

## Available Templates by Service

### TruLoad (.NET/Hangfire)

| Template | Variables | Use Case |
|----------|-----------|----------|
| `truload/weight_ticket` | name, ticket_number, vehicle_reg, gross_weight, net_weight, compliance_status, download_link | Weight ticket generated |
| `truload/compliance_certificate` | name, certificate_number, vehicle_reg, expiry_date, download_link | Certificate available |
| `truload/special_release` | name, release_number, vehicle_reg, reason, authorized_by, view_link | Special release issued |

### ERP/Reports (Python/Django)

| Template | Variables | Use Case |
|----------|-----------|----------|
| `reports/report_ready` | name, report_name, report_type, generated_at, date_range, download_link, retention_days | Report generated |
| `reports/activity_report_submitted` | name, project_name, activity_title, submitted_by, submission_date, review_link | Activity report submitted |
| `reports/activity_report_approved` | name, project_name, activity_title, approved_by, approval_date, action_link | Report approved |
| `reports/activity_report_rejected` | name, project_name, activity_title, rejected_by, rejection_reason, action_link | Report rejected |

### Cafe (Python/Django)

| Template | Variables | Use Case |
|----------|-----------|----------|
| `cafe/cafe_contact_form` | name, email, message, submitted_at | Contact form submission |

### Generic (Any Service)

| Template | Variables | Use Case |
|----------|-----------|----------|
| `shared/generic_notification` | name, title, message, action_link | Any notification |
| `shared/system_alert` | name, alert_title, alert_message, severity, action_link | System alerts |
| `shared/approval_required` | name, item_type, item_id, requester, action_link | Approval requests |

---

## Integration Examples

### Python (requests)

```python
import requests

def send_notification(tenant_id: str, template: str, to: list, data: dict, subject: str, api_key: str):
    resp = requests.post(
        f"https://notificationsapi.codevertexitsolutions.com/{tenant_id}/notifications/messages",
        json={
            "channel": "email",
            "template": template,
            "to": to,
            "data": data,
            "metadata": {"subject": subject},
        },
        headers={
            "X-API-Key": api_key,
            "Content-Type": "application/json",
        },
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()

# Example: send weight ticket notification
send_notification(
    tenant_id="uuid-here",
    template="truload/weight_ticket",
    to=["driver@example.com"],
    data={
        "name": "John Doe",
        "ticket_number": "WT-2026-001",
        "vehicle_reg": "KDA 123A",
        "gross_weight": "45,000 kg",
        "net_weight": "30,000 kg",
        "compliance_status": "Compliant",
        "download_link": "https://app.example.com/tickets/WT-2026-001",
    },
    subject="Your Weight Ticket is Ready",
    api_key="your-api-key",
)
```

### Python/Celery Task

```python
from celery import shared_task

@shared_task(bind=True, max_retries=3)
def send_report_ready_notification(self, tenant_id, recipient_email, report_name, download_link):
    try:
        send_notification(
            tenant_id=tenant_id,
            template="reports/report_ready",
            to=[recipient_email],
            data={
                "name": "User",
                "report_name": report_name,
                "report_type": "Analytics",
                "download_link": download_link,
            },
            subject=f"Report Ready: {report_name}",
            api_key=settings.NOTIFICATIONS_API_KEY,
        )
    except Exception as exc:
        self.retry(exc=exc, countdown=60)
```

### C# (.NET/Hangfire)

```csharp
public class NotificationClient
{
    private readonly HttpClient _http;
    private readonly string _baseUrl;
    private readonly string _apiKey;

    public NotificationClient(string baseUrl, string apiKey)
    {
        _baseUrl = baseUrl;
        _apiKey = apiKey;
        _http = new HttpClient();
        _http.DefaultRequestHeaders.Add("X-API-Key", apiKey);
    }

    public async Task SendAsync(string tenantId, string template, string[] to,
        Dictionary<string, object> data, string subject)
    {
        var payload = new
        {
            channel = "email",
            template,
            to,
            data,
            metadata = new { subject }
        };

        var resp = await _http.PostAsJsonAsync(
            $"{_baseUrl}/{tenantId}/notifications/messages", payload);
        resp.EnsureSuccessStatusCode();
    }
}

// Usage in Hangfire job:
[AutomaticRetry(Attempts = 3)]
public void SendWeightTicketNotification(string tenantId, string email, WeightTicket ticket)
{
    var client = new NotificationClient(
        "https://notificationsapi.codevertexitsolutions.com",
        Environment.GetEnvironmentVariable("NOTIFICATIONS_API_KEY"));

    client.SendAsync(tenantId, "truload/weight_ticket", new[] { email },
        new Dictionary<string, object>
        {
            ["name"] = ticket.DriverName,
            ["ticket_number"] = ticket.TicketNumber,
            ["vehicle_reg"] = ticket.VehicleReg,
            ["gross_weight"] = ticket.GrossWeight,
            ["net_weight"] = ticket.NetWeight,
            ["compliance_status"] = ticket.ComplianceStatus,
            ["download_link"] = $"https://app.example.com/tickets/{ticket.TicketNumber}",
        },
        "Your Weight Ticket is Ready"
    ).GetAwaiter().GetResult();
}
```

---

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `NOTIFICATIONS_API_URL` | Base URL for notifications-api | `https://notificationsapi.codevertexitsolutions.com` |
| `NOTIFICATIONS_API_KEY` | API key for service-to-service auth | `sk_notif_...` |

---

## Error Handling

| Status | Meaning | Action |
|--------|---------|--------|
| `202` | Accepted — notification queued | Success |
| `400` | Invalid request (missing fields) | Fix payload |
| `401` | Authentication failed | Check JWT/API key |
| `429` | Rate limit exceeded | Retry after delay |
| `500` | Server error | Retry with backoff |
