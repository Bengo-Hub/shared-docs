# Delivery areas, geofencing and delivery quotes

logistics-api is the only service that knows where a tenant delivers and what a delivery costs. Every other service asks it. This page is the integration contract; the full rule and field list live in logistics-api `docs/delivery-zones.md`.

## Who owns what

| Data | Owner | Others keep |
|---|---|---|
| Delivery areas (circles and polygons, fee or free, minimum order, ETA, priority, outlet scope, no-delivery areas) | logistics-api `geo_fences` | nothing |
| Distance pricing and geofence policy (per-km rate, minimum, rounding, buffer around the areas, maximum distance) | logistics-api `logistics.delivery_quote_policy` | nothing |
| Outlet map pin | auth-api outlet metadata (`latitude`, `longitude`), published on `auth.outlet.*` | mirrors in logistics and ordering |
| The fee charged on an order | ordering-backend `orders.delivery_fee` plus `metadata.delivery_quote` snapshot | logistics task metadata (`zone_id`, `zone_name`, `distance_km`, `delivery_fee`) |
| Ordering's own fees (service, packaging, small order, delivery discount, free delivery minimum) | ordering-backend `service_configs.fee_config` | nothing |

No service other than logistics-api computes distances, point-in-area checks or delivery fees.

## How to price a delivery

Server side, at checkout:

```
POST {LOGISTICS_SERVICE_URL}/api/v1/s2s/zones/{tenant-uuid-or-slug}/quote
X-API-Key: <INTERNAL_SERVICE_KEY>
{"lat": 0.47, "lng": 34.16, "outlet_id": "<optional>", "order_total": 800}
```

The response says whether the pin is deliverable, the fee, the matched area or the nearest one, the distance and the ETA. Charge the returned fee (after any of your own adjustments) and store the quote with the order. Never fall back to a guessed fee: if logistics cannot be reached, refuse delivery and keep pickup working. Quotes may be cached for `cache_seconds` per tenant, outlet and pin.

Browser side (public, throttled per IP):

| Endpoint | Use |
|---|---|
| `GET /api/v1/{tenant}/zones/coverage` | Draw the delivery areas and centre a map |
| `GET /api/v1/{tenant}/zones/quote?lat&lng&outlet_id&order_total` | Live fee while a customer moves the pin |
| `GET /api/v1/{tenant}/routing/geocode/search?q` | Place search (tenant areas first) |
| `GET /api/v1/{tenant}/routing/geocode/reverse?lat&lng` | Name the place at a pin |

Use `@bengo-hub/maps` v0.3.0 or later for the UI: `LocationPicker` for a single pin, `ZoneLayer` to draw areas, `ZoneEditor` for admin editing.

## Where admins configure it

logistics-ui, Delivery areas (`/{tenant}/zones`): add or edit areas on the map or by typed coordinates, set the distance rate and geofence, test any location, and see deliveries by area. Shifts can list the areas a rider covers, which auto-dispatch prefers. Other UIs link there instead of copying the screens.

## Current consumers

- ordering-backend and ordering-frontend (checkout, header location, saved addresses, outlet listing).
- logistics task intake and dispatch (zone tagging, zone-aware rider choice, rider earnings by real distance).
- rider-app (area, distance and fee on jobs).

POS till deliveries, courier tenants and distribution tenants (KEMSA-style regional delivery) use the same quote and areas: configure areas in logistics-ui and call the S2S quote.
