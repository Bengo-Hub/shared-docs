# Realtime Fan-out (WebSocket and SSE across replicas)

Every backend runs at least two pods with no sticky sessions. A client's WebSocket or SSE stream
lives on whichever pod accepted it, while the event that should reach it (a price change, a ticket
update, a rider position) is raised on whichever pod handled the write. A hub that only knows its
own pod's clients therefore reaches about one in N clients. This page is the one pattern for
getting it right.

## Building blocks (shared-events)

| Piece | What it does |
|---|---|
| `Broadcaster` | Relays a message to every replica over core NATS with a plain (non-queue) subscription. Subjects are `_rt.<namespace>.<topic>.<tenant>.<scope>`; the `_rt.` prefix is outside every `{service}.>` JetStream stream, so nothing is persisted. `Publish` delivers to this pod's handlers first, then relays; each pod drops its own echo, so no replica delivers twice. |
| `FanoutHub` | The registry every hub shares: subscribers per tenant with optional scopes (`user:<id>`, `outlet:<id>`, `task:<id>`, or `WildcardScope` for "all outlets"). `Publish(tenant, "", data)` reaches the whole tenant; a scope reaches only its holders. Never across tenants. Full buffers drop and count in `Sub.Dropped`. |
| `Pump` | The one socket write loop: hello frame, hub messages, 5 s write deadline, 25 s server ping, optional reply to client frames. `Socket` is three functions, so any WebSocket library adapts in three lines. |

A queue-group subscription is wrong for fan-out: it hands each message to one pod only.

## Writing a hub

```go
fan, _ := eventslib.NewFanoutHub(relay, "kds", 64) // relay = eventslib.NewBroadcaster(log, nc, "pos")

func (h *Hub) ServeWS(ctx context.Context, conn *websocket.Conn, tenantID, outletID uuid.UUID) {
    sub := h.fan.Subscribe(tenantID.String(), "outlet:"+outletID.String())
    defer h.fan.Unsubscribe(sub)
    eventslib.Pump(ctx, realtime.Socket(conn), sub, hello, replyToPing)
}

func (h *Hub) BroadcastToOutlet(tenantID, outletID uuid.UUID, msg Message) {
    b, _ := json.Marshal(msg)
    h.fan.Publish(tenantID.String(), "outlet:"+outletID.String(), b)
}
```

SSE handlers subscribe the same way and write `event:`/`data:` frames from `sub.C`.

## Streaming hygiene

- Wrap chi `Compress` and `Timeout` (and logging) in `httpware.BypassForStreaming`: Compress cannot
  hijack, and Timeout cancels the request context at its deadline, killing every stream.
- SSE: call `httpware.StreamHeaders(w)` (includes `X-Accel-Buffering: no`, or nginx holds events)
  and `httpware.ExtendWriteDeadline(w)` (lifts the server `WriteTimeout` for that response), flush
  through `http.NewResponseController(w)` rather than a `w.(http.Flusher)` assertion, and send a
  comment heartbeat every 15 s.
- Delivery is best effort: a reconnecting pod misses messages. Clients keep their resync path
  (version poll, refetch on reconnect).

## Hubs on this pattern

pos-api (notifications, KDS, print agent), inventory-api (notifications), logistics-api (fleet
tracking, dispatcher notifications, task SSE), notifications-api (WhatsApp inbox), ticketing-api
(ticket SSE). Cross-pod cache invalidation (pos-api outlet settings and maintenance windows, the
API-key revocation topic `auth/apikey.changed`) uses the same `Broadcaster`.
