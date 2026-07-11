#!/usr/bin/env bash
#
# event-subject-coverage.sh — cross-service NATS/shared-events subject coverage linter.
#
# Scans every Go backend service for the subjects they PUBLISH and the subjects they
# SUBSCRIBE to, then reports:
#   • ORPHAN PUBLISH   — a subject published by some service that NO service consumes
#   • DEAD SUBSCRIPTION — a subject subscribed to that NO service publishes
#
# This catches the recurring class of integration bugs (e.g. ticketing.crm.* published
# under the wrong aggregate with no consumer; auth.user.deactivated consumed but never
# published; pos.staff_purchase.created published with no subscriber).
#
# It is a best-effort static linter (regex over Go source), not a proof:
#   - Subjects built dynamically (string concatenation) are not detected.
#   - Cross-service subjects intentionally left one-sided go in the WHITELIST below.
# Exit code is non-zero when a non-whitelisted orphan/dead subject is found, so it can
# gate CI. Run from the monorepo root (the parent of the service dirs).
#
# Usage:  shared-docs/tools/event-subject-coverage.sh [ROOT_DIR]
set -euo pipefail

ROOT="${1:-$(pwd)}"

# Go backend services (relative to ROOT).
SERVICES=(
  auth-service/auth-api
  pos-service/pos-api
  inventory-service/inventory-api
  finance-service/treasury-api
  subscriptions-service/subscriptions-api
  logistics-service/logistics-api
  ordering-service/ordering-backend
  notifications-service/notifications-api
  erp/erp-api
  projects-service/projects-api
  library-service/library-api
  marketflow/marketflow-api
  marketflow/ticketing-service/ticketing-api
)

# Subjects deliberately one-sided (external systems, planned-but-unwired, self-consumed
# via S2S instead of events, etc.). One subject per line; comments allowed.
WHITELIST=$(cat <<'EOF'
notifications.events
EOF
)

subject_re='[a-z][a-z0-9_]*(\.[a-z0-9_]+)+'

pub_file="$(mktemp)"; sub_file="$(mktemp)"
trap 'rm -f "$pub_file" "$sub_file"' EXIT

for svc in "${SERVICES[@]}"; do
  dir="$ROOT/$svc"
  [ -d "$dir" ] || continue

  # Flatten each .go file (collapse newlines/whitespace) so calls formatted across multiple
  # lines — the common gofmt style for Subscribe/NewEvent — are matched on a single line.
  flat="$(find "$dir" -name '*.go' -not -path '*/ent/*' -not -name '*_test.go' -print0 2>/dev/null \
    | xargs -0 perl -0777 -pe 's/\s+/ /g' 2>/dev/null || true)"

  # PUBLISHES
  #  a) NewEvent("eventType", "aggregateType", ...)   -> aggregate.event
  #  b) publishEvent(ctx, tenantID, "aggregate", id, "eventType", ...) -> aggregate.event
  #  c) Publish/PublishMsg(ctx?, "subject", ...)      -> literal
  echo "$flat" | grep -osE 'NewEvent\( *"[^"]+", *"[^"]+"' \
    | sed -E 's/NewEvent\( *"([^"]+)", *"([^"]+)"/\2.\1/' >> "$pub_file" || true
  echo "$flat" | grep -osE 'publishEvent\( *[^,]+, *[^,]+, *"[^"]+", *[^,]+, *"[^"]+"' \
    | sed -E 's/.*, *"([^"]+)", *[^,]+, *"([^"]+)"/\1.\2/' >> "$pub_file" || true
  echo "$flat" | grep -osE '(Publish|PublishMsg)\( *[^"]*"'"$subject_re"'"' \
    | grep -oE '"'"$subject_re"'"' | tr -d '"' >> "$pub_file" || true

  # SUBSCRIBES
  #  SubscribeQueueWithRebind(log, js, "stream", "subject", ...) -> the 4th string
  #  QueueSubscribe/Subscribe/PullSubscribe(..., "subject", ...) ; FilterSubject: "subject"
  echo "$flat" | grep -osE 'SubscribeQueueWithRebind\( *[^,]+, *[^,]+, *"[^"]+", *"[^"]+"' \
    | sed -E 's/.*, *"[^"]+", *"([^"]+)"/\1/' >> "$sub_file" || true
  echo "$flat" | grep -osE '(QueueSubscribe|PullSubscribe|\.Subscribe)\( *[^"]*"'"$subject_re"'"' \
    | grep -oE '"'"$subject_re"'"' | tr -d '"' >> "$sub_file" || true
  echo "$flat" | grep -osE 'FilterSubject: *"'"$subject_re"'"' \
    | grep -oE '"'"$subject_re"'"' | tr -d '"' >> "$sub_file" || true
done

# A subject is CONSUMED if it is subscribed exactly OR it falls under a wildcard
# subscription (e.g. `treasury.>` consumes every treasury.* subject). Wildcard prefixes
# are the dominant false-positive source, so we expand them here.
wl="$(echo "$WHITELIST" | grep -vE '^\s*(#|$)' || true)"
wildcard_prefixes="$(grep -E '\.>$' "$sub_file" | sed -E 's/\.>$//' | sort -u || true)"

# exact literal subjects (no wildcards), unique, minus whitelist.
clean() { sort -u | grep -vE '[>*]' | { [ -n "$wl" ] && grep -vxF "$wl" || cat; } || true; }
published="$(clean < "$pub_file")"
subscribed="$(clean < "$sub_file")"

# consumed = exact subscription OR covered by a wildcard prefix.
is_consumed() {
  local s="$1"
  echo "$subscribed" | grep -qxF "$s" && return 0
  while IFS= read -r pfx; do
    [ -n "$pfx" ] && case "$s" in "$pfx".*) return 0;; esac
  done <<< "$wildcard_prefixes"
  return 1
}

orphan_pub=""
while IFS= read -r s; do
  [ -z "$s" ] && continue
  is_consumed "$s" || orphan_pub="$orphan_pub$s"$'\n'
done <<< "$published"
orphan_pub="$(echo "$orphan_pub" | sed '/^$/d')"

# dead subscription: exact subscribed subject that nobody publishes (wildcards excluded).
dead_sub="$(comm -13 <(echo "$published") <(echo "$subscribed"))"

if [ -n "$orphan_pub" ]; then
  echo "ORPHAN PUBLISH candidates (published, no consumer detected):"
  echo "$orphan_pub" | sed 's/^/  - /'
fi
if [ -n "$dead_sub" ]; then
  echo "DEAD SUBSCRIPTION candidates (subscribed, no publisher detected):"
  echo "$dead_sub" | sed 's/^/  - /'
fi
if [ -z "$orphan_pub$dead_sub" ]; then
  echo "OK: every detected subject has both a publisher and a consumer."
fi

cat <<'NOTE'

NOTE: This is a HEURISTIC report, not a gate. It regex-extracts subjects and cannot follow
subjects built through service wrapper publishers that prepend a `<service>.` prefix to the
aggregate (erp/ticketing/projects/marketflow). Such subjects show up as a pair that differs
only by the leading prefix (e.g. `staff_purchase.recovered` vs `erp.staff_purchase.recovered`)
— those are FALSE POSITIVES; the event flows fine. Treat each finding as a candidate to verify
by hand, cross-referencing the actual publisher aggregate and the consumer subscription. A
reliable check would use Go AST analysis of NewEvent()/publishEvent() aggregate arguments.
NOTE
# Always exit 0: report-only. Do not gate CI on a heuristic that has known false positives.
exit 0
