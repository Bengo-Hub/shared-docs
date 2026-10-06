from diagrams import *  # noqa: F401,F403


def fig_architecture():
    b = []
    b.append(lane(10, 8, 740, 72, ""))
    b.append(box(40, 30, 190, 42, ["Guests", "browser, WhatsApp link, no app"], "user", 10.5))
    b.append(box(285, 30, 190, 42, ["Registry owners", "couples, parents, graduates"], "user", 10.5))
    b.append(box(530, 30, 190, 42, ["Hadia team", "operations and finance"], "user", 10.5))

    b.append(lane(10, 98, 740, 76, "", "#FBF6FA"))
    b.append(box(60, 118, 250, 48, ["hadia-ui", "Next.js PWA, guest and owner views"], "new", 10.5))
    b.append(box(400, 118, 250, 48, ["hadia-api", "Go service: registries, items, reservations"], "new", 10.5))

    b.append(lane(10, 222, 740, 84, "", "#F3FAF6"))
    xs = [20, 167, 314, 461, 608]
    labels = [["auth-api", "SSO, phone OTP, API keys"], ["treasury-api", "books, escrow, payouts"],
              ["notifications-api", "SMS, WhatsApp, email"], ["subscriptions-api", "plan and features"],
              ["treasury-ui", "books and escrow console"]]
    for x, l in zip(xs, labels):
        b.append(box(x, 244, 135, 52, l, "reuse", 10.5))

    b.append(lane(10, 326, 740, 76, "", "#FDF9F1"))
    ext = [["PayHero", "collections, wallet, payouts"], ["M-Pesa, Airtel, card", "payer rails"],
           ["Africa's Talking", "SMS"], ["WhatsApp Cloud API", "messages"], ["SMTP mail server", "email"]]
    for x, l in zip(xs, ext):
        b.append(box(x, 348, 135, 46, l, "ext", 10.5))

    b.append(box(10, 414, 740, 32, ["Platform: PostgreSQL per service, Redis, NATS JetStream, MinIO, Cloudflare edge, Kubernetes with GitOps"], "grey", 10, bold_first=False))

    b.append(arrow([(135, 72), (160, 118)]))
    b.append(arrow([(380, 72), (260, 118)]))
    b.append(arrow([(700, 72), (720, 244)]))
    b.append(label_bg(700, 90, "books, approvals", anchor="end"))
    b.append(arrow([(310, 142), (400, 142)], "REST"))
    b.append(arrow([(110, 166), (90, 244)], "sign-in", lx=88, ly=205))
    b.append(arrow([(200, 166), (225, 244)], "pay modal", lx=196, ly=205))
    for tx in (300, 382, 529):
        b.append(arrow([(560, 166), (tx + 20 if tx == 300 else tx, 244)], color=BRAND))
    b.append(label_bg(600, 205, "S2S calls, service-client"))
    b.append(arrow([(275, 244), (450, 166)], color=GREEN, dashed=True))
    b.append(label_bg(390, 190, "escrow.* events (NATS)"))
    b.append(arrow([(234, 296), (88, 348)]))
    b.append(arrow([(155, 371), (167, 371)]))
    b.append(arrow([(370, 296), (382, 348)]))
    b.append(arrow([(410, 296), (529, 348)]))
    b.append(arrow([(440, 296), (660, 348)]))
    for y, t in ((8, "Users"), (98, "Hadia applications"), (222, "Codevertex platform services"), (326, "External providers")):
        b.append(lane_title(10, y, t))
    b.append(legend(20, 458, [("new", "Built for Hadia"), ("reuse", "Codevertex platform service"),
                              ("ext", "Third party"), ("user", "People")]))
    return svg(760, 476, "".join(b), "Hadia solution architecture")


def fig_money():
    b = []
    b.append(box(10, 40, 130, 60, ["Guests", "M-Pesa, Airtel, card"], "user"))
    b.append(lane(175, 10, 300, 220, "Hadia PayHero wallet (licensed provider)", "#FDF9F1"))
    b.append(box(195, 40, 260, 34, ["All gift money is held here, never by Codevertex"], "plain", 9.5, bold_first=False))
    for i, (t, amt) in enumerate([("Pot: Achieng and David", "KSh 42,000"), ("Pot: Baby Wanjiru", "KSh 9,500"),
                                  ("Pot: Otieno graduation", "KSh 15,200")]):
        b.append(box(195, 84 + i * 38, 175, 30, [t], "ext", 9.8))
        b.append(text(410, 103 + i * 38, amt, 10, 600, INK))
    b.append(box(195, 198, 260, 24, ["Commission retained, swept on schedule"], "new", 9.5))
    b.append(box(520, 40, 230, 60, ["Registry owner", "net release to verified M-Pesa"], "user"))
    b.append(box(520, 160, 230, 60, ["Hadia business account", "paybill, till or bank (commission)"], "new"))
    b.append(arrow([(140, 70), (195, 70)], "contribution"))
    b.append(arrow([(455, 100), (520, 75)], "auto release, net", lx=490, ly=80))
    b.append(arrow([(455, 210), (520, 195)], "commission sweep", lx=488, ly=222))

    b.append(lane(10, 245, 740, 150, "Treasury books (double entry, per pot sub-ledger)", "#F3FAF6"))
    rows = [("Contribution confirmed", "DR 1215 PayHero Wallet", "CR 2015 Escrow Funds Held"),
            ("Release confirmed", "DR 2015 Escrow Funds Held (gross)", "CR 1215 (net) and CR 4800 Commission"),
            ("Refund confirmed", "DR 2015 Escrow Funds Held", "CR 1215 PayHero Wallet"),
            ("Commission sweep", "DR bank or paybill account", "CR 1215 PayHero Wallet")]
    for i, (a, d, c) in enumerate(rows):
        y = 272 + i * 29
        b.append(text(24, y + 12, a, 10, 600, INK, "start"))
        b.append(box(200, y, 260, 22, [d], "plain", 9.5, bold_first=False))
        b.append(box(475, y, 265, 22, [c], "plain", 9.5, bold_first=False))
    return svg(760, 402, "".join(b), "Money flow and accounting")


def fig_pot_states():
    b = []
    b.append(pill(20, 90, 110, 36, "open", "reuse"))
    b.append(pill(250, 90, 120, 36, "releasing", "ext"))
    b.append(pill(500, 90, 110, 36, "released", "new"))
    b.append(pill(250, 200, 120, 36, "cancelled", "warn"))
    b.append(arrow([(130, 100), (250, 100)], "rule met or owner asks"))
    b.append(arrow([(370, 100), (500, 100)], "payout confirmed"))
    b.append(arrow([(250, 118), (130, 118)], "payout failed, money returned", lx=190, ly=136))
    b.append(arrow([(555, 90), (555, 50), (310, 50), (310, 90)], "new money and rule met again", lx=430, ly=44))
    b.append(arrow([(75, 126), (75, 218), (250, 218)], "closed, with or without refunds", lx=160, ly=212))
    b.append(text(640, 104, "Further gifts keep", 9.5, 400, MUTED, "start"))
    b.append(text(640, 118, "arriving after a release", 9.5, 400, MUTED, "start"))
    return svg(760, 250, "".join(b), "Pot lifecycle")


def fig_contribution():
    actors = [("g", "Guest|phone", "user"), ("ui", "hadia-ui", "new"), ("tr", "treasury-api", "reuse"),
              ("ph", "PayHero", "ext"), ("ha", "hadia-api", "new"), ("nt", "notifications|api", "reuse")]
    msgs = [
        ("g", "ui", "Contribute KSh 2,000", "call"),
        ("ui", "tr", "escrow contribution + Idempotency-Key", "call"),
        ("tr", "ph", "collection into Hadia wallet", "call"),
        ("ph", "g", "M-Pesa STK prompt, guest enters PIN", "call"),
        ("ph", "tr", "callback (treated as a hint)", "reply"),
        ("tr", "ph", "transaction-status lookup", "call"),
        ("tr", "tr", "credit pot once, post DR 1215 / CR 2015", "self"),
        ("tr", "ui", "status paid (page polls every 3 s)", "reply"),
        ("tr", "ha", "escrow.pot_credited over NATS", "reply"),
        ("ha", "ha", "item progress, gift log, thank-you list", "self"),
        ("ha", "nt", "receipt to guest, alert to owner", "call"),
    ]
    return sequence(actors, msgs, title="Guest contribution sequence")


def fig_payout():
    b = []
    b.append(pill(300, 6, 160, 30, "Job runs every 5 min", "grey", 10.5))
    b.append(arrow([(380, 36), (380, 56)]))
    b.append(diamond(380, 92, 260, 70, ["Pot due?", "threshold reached or hold date passed"]))
    b.append(arrow([(250, 92), (150, 92)], "no"))
    b.append(box(20, 72, 130, 40, ["Wait for next run"], "grey", 10))
    b.append(arrow([(380, 127), (380, 150)], "yes", lx=395, ly=142, anchor="start"))
    b.append(diamond(380, 186, 260, 68, ["Above approval limit?", "Hadia sets the amount"]))
    b.append(arrow([(510, 186), (575, 186)], "yes"))
    b.append(box(575, 160, 175, 52, ["Approval request", "finance approves with OTP"], "warn", 10))
    b.append(arrow([(662, 212), (662, 262), (530, 262)], "once approved", lx=690, ly=240))
    b.append(arrow([(380, 220), (380, 245)], "no", lx=395, ly=238, anchor="start"))
    b.append(box(230, 245, 300, 40, ["Commission worked out", "pot override, else Hadia fee rule"], "new", 10))
    b.append(arrow([(380, 285), (380, 302)]))
    b.append(box(230, 302, 300, 40, ["Claim ESC-code-n and debit pot", "one release in flight per pot"], "reuse", 10))
    b.append(arrow([(380, 342), (380, 359)]))
    b.append(box(230, 359, 300, 40, ["Payout through dispatcher", "to the owner's verified M-Pesa"], "reuse", 10))
    b.append(arrow([(380, 399), (380, 418)]))
    b.append(diamond(380, 452, 220, 64, ["PayHero confirms?"]))
    b.append(arrow([(490, 452), (560, 452)], "success"))
    b.append(box(560, 426, 190, 52, ["Book, mark released", "notify owner and guests"], "reuse", 10))
    b.append(arrow([(270, 452), (200, 452)], "failed"))
    b.append(box(10, 426, 190, 52, ["Money back to pot", "ops alerted, retried next run"], "warn", 10))
    b.append(arrow([(380, 484), (380, 505)], "no callback in 15 min", lx=395, ly=500, anchor="start"))
    b.append(box(255, 505, 250, 32, ["Status lookup with PayHero"], "grey", 10))
    return svg(760, 545, "".join(b), "Automated payout decision flow")


def fig_owner_onboarding():
    steps = [("1", ["Sign up", "mobile and OTP"]), ("2", ["Accept terms", "versioned"]),
             ("3", ["Create event", "type, date, story"]), ("4", ["Verify payout", "OTP on M-Pesa line"]),
             ("5", ["Escrow opened", "treasury"]), ("6", ["Share link", "WhatsApp preview"])]
    b = []
    w, g = 112, 13
    for i, (n, l) in enumerate(steps):
        x = 10 + i * (w + g)
        kind = "reuse" if i in (0, 1, 4) else "new"
        b.append(box(x, 30, w, 60, l, kind, 10.5))
        b.append(f'<circle cx="{x+14}" cy="30" r="11" fill="{BRAND}"/>' + text(x + 14, 34, n, 10, 700, "#FFFFFF"))
        if i < len(steps) - 1:
            b.append(arrow([(x + w, 60), (x + w + g, 60)]))
        return svg(760, 100, "".join(b), "Registry owner onboarding")


def fig_tenant_onboarding():
    steps = [["Company KYC", "documents, KRA PIN"], ["Tenant set-up", "plan with escrow"],
             ["PayHero Team", "KYC tier 3"], ["Channels", "paybill, wallet"],
             ["Rules", "fees, limits"], ["Go-live", "KES 1 tests"]]
    b = []
    w, g = 112, 13
    for i, l in enumerate(steps):
        x = 10 + i * (w + g)
        b.append(box(x, 20, w, 60, l, "ext" if i in (0, 2) else "reuse", 10.5))
        if i < len(steps) - 1:
            b.append(arrow([(x + w, 50), (x + w + g, 50)]))
    return svg(760, 92, "".join(b), "Hadia business onboarding")


def fig_listing():
    b = []
    b.append(box(10, 20, 150, 48, ["Owner adds item"], "user", 10.5))
    b.append(arrow([(160, 44), (200, 44)]))
    b.append(diamond(285, 44, 170, 64, ["Pasted a link?"]))
    b.append(arrow([(285, 76), (285, 110)], "no", lx=298, ly=98, anchor="start"))
    b.append(box(200, 110, 170, 48, ["Manual form", "title, price, photo"], "new", 10))
    b.append(arrow([(370, 44), (420, 44)], "yes"))
    b.append(box(420, 18, 160, 52, ["Safe fetch", "allow-list, 3 s, 1 MB cap"], "new", 10))
    b.append(arrow([(580, 44), (610, 44)]))
    b.append(box(610, 18, 140, 52, ["Prefill form", "owner confirms"], "new", 10))
    b.append(arrow([(680, 70), (680, 134), (370, 134)], "fields missing or fetch fails", lx=540, ly=128))
    b.append(arrow([(285, 158), (285, 186)]))
    b.append(box(130, 186, 310, 44, ["Item saved", "image resized to WebP, source credited"], "reuse", 10))
    b.append(arrow([(440, 208), (500, 208)]))
    b.append(box(500, 186, 250, 44, ["Mode: reserve, fund, or both", "group gifting on any item"], "new", 10))
    return svg(760, 240, "".join(b), "Listing an item")


def fig_reservation():
    b = []
    b.append(box(10, 20, 140, 46, ["Guest taps Reserve"], "user", 10))
    b.append(arrow([(150, 43), (185, 43)]))
    b.append(box(185, 20, 170, 46, ["Name and phone", "OTP if phone given"], "new", 10))
    b.append(arrow([(355, 43), (390, 43)]))
    b.append(diamond(475, 43, 170, 62, ["Still available?", "one atomic update"]))
    b.append(arrow([(560, 43), (600, 43)], "yes"))
    b.append(box(600, 20, 150, 46, ["Reserved", "link to cancel sent"], "reuse", 10))
    b.append(arrow([(475, 74), (475, 100)], "no", lx=488, ly=92, anchor="start"))
    b.append(box(370, 100, 210, 40, ["Offer to contribute instead"], "warn", 10))
    b.append(arrow([(675, 66), (675, 120), (600, 120)]))
    b.append(text(690, 140, "Reminder at 14 days", 9.5, 500, MUTED, "end"))
    b.append(text(690, 154, "release if not bought", 9.5, 500, MUTED, "end"))
    return svg(760, 162, "".join(b), "Reserving an item")


def fig_sweep():
    b = []
    b.append(pill(10, 30, 150, 30, "Daily, or on release", "grey", 10))
    b.append(arrow([(160, 45), (190, 45)]))
    b.append(box(190, 20, 190, 52, ["Available commission", "wallet minus pots minus in flight"], "new", 9.8))
    b.append(arrow([(380, 45), (410, 45)]))
    b.append(diamond(495, 45, 170, 60, ["Above sweep floor?", "after reserve"]))
    b.append(arrow([(580, 45), (610, 45)], "yes"))
    b.append(box(610, 20, 140, 52, ["Payout to Hadia", "locked own channel"], "reuse", 9.8))
    b.append(arrow([(495, 75), (495, 100)], "no", lx=508, ly=92, anchor="start"))
    b.append(box(420, 100, 150, 32, ["Keep in wallet"], "grey", 10))
    return svg(760, 140, "".join(b), "Commission sweep")


def fig_refund():
    b = []
    b.append(box(10, 20, 150, 48, ["Owner or Hadia cancels", "event called off"], "user", 10))
    b.append(arrow([(160, 44), (195, 44)]))
    b.append(box(195, 20, 160, 48, ["Approval", "policy, bound to balance"], "warn", 10))
    b.append(arrow([(355, 44), (390, 44)]))
    b.append(box(390, 20, 160, 48, ["Pot closed first", "no new gifts accepted"], "reuse", 10))
    b.append(arrow([(550, 44), (585, 44)]))
    b.append(box(585, 20, 165, 48, ["Each gift paid back", "to its payer's phone"], "reuse", 10))
    b.append(arrow([(667, 68), (667, 100)]))
    b.append(box(560, 100, 190, 40, ["No phone on record:", "manual refund list"], "grey", 10))
    b.append(box(300, 100, 230, 40, ["Failed refund: money back to pot", "retried, never paid twice"], "grey", 10))
    return svg(760, 150, "".join(b), "Cancellation and refunds")


def fig_erd():
    b = []
    ents = {
        "owner": (10, 20, ["owner_profiles", "user_id (auth)", "display_name, phone_verified_at", "kyc_status, terms_version"]),
        "reg": (280, 20, ["registries", "owner_id, slug, type, event_date", "status, plan (free|premium)", "escrow_pot_id (treasury)", "payout_rule_id, visibility"]),
        "item": (560, 20, ["registry_items", "registry_id, mode, title", "price, qty, source_url", "image_key, funded (projection)", "position, archived_at"]),
        "res": (560, 200, ["reservations", "item_id, guest_name, phone_hash", "status, cancel_token_hash", "expires_at, purchased_at"]),
        "gift": (280, 200, ["gift_log (projection)", "registry_id, intent_id (unique)", "amount, guest_name, message", "item_id, thanked_at"]),
        "prem": (10, 200, ["premium_purchases", "registry_id, intent_id", "feature set, amount, status"]),
        "rule": (10, 330, ["payout_rules", "registry_id, threshold", "hold_days, instant (premium)"]),
        "stats": (280, 340, ["registry_daily_stats", "registry_id, day (unique pair)", "gifts, amount, views, shares"]),
        "cons": (560, 340, ["consents and audit", "subject, purpose, version", "granted_at, withdrawn_at"]),
    }
    for k, (x, y, lines) in ents.items():
        h = 22 + 15 * (len(lines) - 1) + 8
        b.append(f'<rect x="{x}" y="{y}" width="190" height="{h}" rx="6" fill="#fff" stroke="{BRAND}" stroke-width="1.2"/>')
        b.append(f'<rect x="{x}" y="{y}" width="190" height="22" rx="6" fill="{BRAND}"/>')
        b.append(text(x + 95, y + 15, lines[0], 10.5, 700, "#FFFFFF"))
        for i, ln in enumerate(lines[1:]):
            b.append(text(x + 10, y + 37 + i * 15, ln, 9.5, 400, INK, "start"))
    b.append(arrow([(200, 50), (280, 50)], "1 : n"))
    b.append(arrow([(470, 50), (560, 50)], "1 : n"))
    b.append(arrow([(655, 110), (655, 200)], "1 : n", lx=675, ly=160))
    b.append(arrow([(375, 125), (375, 200)], "1 : n", lx=395, ly=165))
    b.append(arrow([(300, 125), (105, 200)], "1 : n", lx=210, ly=158))
    b.append(arrow([(290, 125), (105, 330)], "1 : 1", lx=170, ly=290))
    b.append(arrow([(420, 125), (420, 340)], "1 : n", lx=440, ly=320))
    return svg(760, 410, "".join(b), "hadia-api data model")


def fig_wireframes():
    def phone(x, title, body):
        out = [f'<rect x="{x}" y="10" width="220" height="400" rx="26" fill="#fff" stroke="{INK}" stroke-width="2"/>',
               f'<rect x="{x+80}" y="20" width="60" height="6" rx="3" fill="{LINE}"/>',
               text(x + 110, 48, title, 11, 700, MAROON)]
        out += body
        return "".join(out)

    def card(x, y, t, sub, btn, pct=None):
        o = [f'<rect x="{x}" y="{y}" width="196" height="62" rx="10" fill="#fff" stroke="{LINE}"/>',
             text(x + 10, y + 20, t, 10.5, 600, INK, "start"), text(x + 10, y + 36, sub, 9, 400, MUTED, "start"),
             f'<rect x="{x+130}" y="{y+12}" width="58" height="22" rx="11" fill="#fff" stroke="{MAROON}"/>',
             text(x + 159, y + 27, btn, 9.5, 600, MAROON)]
        if pct is not None:
            o.append(f'<rect x="{x+10}" y="{y+46}" width="176" height="6" rx="3" fill="{GOLD_SOFT}"/>')
            o.append(f'<rect x="{x+10}" y="{y+46}" width="{176*pct}" height="6" rx="3" fill="{GOLD}"/>')
        return "".join(o)

    g = [f'<rect x="22" y="60" width="196" height="70" rx="10" fill="{GOLD_SOFT}"/>',
         text(120, 88, "Achieng and David", 12, 700, INK), text(120, 104, "Naivasha, 12 December", 9.5, 400, MUTED),
         text(120, 120, "Reserve a gift or send a little something", 9, 400, MUTED),
         card(22, 140, "6-piece cookware set", "KSh 8,500, Sunrise Home", "Reserve"),
         card(22, 210, "Honeymoon fund", "KSh 42,000 of 100,000", "Give", 0.42),
         card(22, 280, "Baby stroller", "Reserved by a guest", "Taken"),
         text(120, 368, "Fees: none for guests. Hadia keeps 4%", 8.6, 500, MUTED),
         text(120, 381, "of cash gifts when they are paid out.", 8.6, 500, MUTED)]
    o = [f'<rect x="282" y="60" width="196" height="64" rx="10" fill="{BRAND_SOFT}"/>',
         text(380, 84, "KSh 57,200 received", 12, 700, INK), text(380, 100, "KSh 42,000 paid out, 3 payouts", 9.5, 400, MUTED),
         text(380, 114, "Next payout at KSh 10,000", 9.5, 400, MUTED),
         card(282, 136, "Gift log", "38 guests, 6 not thanked", "Thank"),
         card(282, 206, "Items", "14 listed, 9 reserved", "Edit"),
         card(282, 276, "Payout settings", "M-Pesa 0712 *** 678", "View"),
         text(380, 370, "Share on WhatsApp", 10, 700, GREEN)]
    m = [f'<rect x="542" y="60" width="196" height="150" rx="10" fill="#fff" stroke="{LINE}"/>',
         text(640, 82, "Give to: Honeymoon fund", 10.5, 700, INK),
         f'<rect x="556" y="94" width="168" height="26" rx="6" fill="{GREY_SOFT}"/>', text(640, 112, "KSh 2,000", 11, 600, INK),
         f'<rect x="556" y="128" width="168" height="26" rx="6" fill="{GREY_SOFT}"/>', text(640, 146, "0712 345 678", 11, 500, INK),
         f'<rect x="556" y="164" width="168" height="30" rx="15" fill="{MAROON}"/>', text(640, 184, "Pay KSh 2,000 with M-Pesa", 10, 700, "#fff"),
         text(640, 236, "Check your phone for the", 10, 500, MUTED), text(640, 250, "M-Pesa prompt", 10, 500, MUTED),
         f'<circle cx="640" cy="290" r="18" fill="none" stroke="{GOLD}" stroke-width="3" stroke-dasharray="80 40"/>',
         text(640, 340, "Amount charged is exactly", 9, 500, MUTED), text(640, 353, "what you entered.", 9, 500, MUTED)]
    body = phone(10, "Guest view", g) + phone(270, "Owner dashboard", o) + phone(530, "Contribution", m)
    return svg(760, 420, body, "Key screens, low fidelity")


def fig_gantt():
    rows = [
        ("Product delivery", 0, 0, "plain", True),
        ("Sprint 0: discovery, design, architecture", 1, 1, "new"),
        ("Sprint 1: onboarding, registries, items", 2, 3, "new"),
        ("Sprint 2: guest pages, reservations, sharing", 4, 5, "new"),
        ("Sprint 3: contributions, events, notifications", 6, 7, "new"),
        ("Sprint 4: payouts, commission, refunds, premium", 8, 9, "new"),
        ("Sprint 5: administration, reports, compliance", 10, 10, "new"),
        ("Hardening: security, load testing, UAT", 11, 11, "warn"),
        ("Launch, training and handover", 12, 12, "reuse"),
        ("Business and regulatory workstream", 0, 0, "plain", True),
        ("Company documents, KRA PIN, bank account", 1, 2, "ext"),
        ("PayHero Team, KYC tier 3, paybill", 1, 5, "ext"),
        ("ODPC registration, DPIA, legal review", 2, 8, "ext"),
        ("Pilot event recruitment", 6, 11, "ext"),
    ]
    return gantt(rows, milestones=[(0.5, "M1 Kick-off"), (7, "M2 Demo"), (10, "M3 Features", "end"), (12, "M4 Launch")],
                 title="Implementation schedule")
