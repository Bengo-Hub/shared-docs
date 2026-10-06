from diagrams import *  # noqa: F401,F403


def fig_architecture():
    b = []
    b.append(lane(10, 8, 740, 72, ""))
    users = [["Public visitors", "house hunters (R3)"], ["Owners and tenants", "phone, no app install"],
             ["Tenant staff", "managers, finance, caretakers"], ["Guards and providers", "gate tablet, vendor portal"]]
    for i, l in enumerate(users):
        b.append(box(22 + i * 182, 30, 168, 42, l, "user", 10))

    b.append(lane(10, 98, 740, 76, "", "#FBF6FA"))
    b.append(box(24, 118, 190, 48, ["maskani-marketplace (R3)", "Maskani Marketplace"], "new", 10, dashed=True))
    b.append(box(232, 118, 230, 48, ["maskani-ui", "portals, console, gate, vendors"], "new", 10))
    b.append(box(500, 118, 236, 48, ["maskani-api", "multi-tenant property domain"], "new", 10))

    b.append(lane(10, 222, 740, 84, "", "#F3FAF6"))
    labels = [["auth-api", "tenants, SSO, OTP"], ["treasury-api", "billing, M-Pesa, GL"],
              ["erp-api", "staff, payroll"], ["notifications", "SMS, WhatsApp"],
              ["subscriptions", "plans, limits"], ["marketflow-api", "leads (R3)"], ["maps", "geocoding (R3)"]]
    xs = [16 + i * 105 for i in range(7)]
    for x, l in zip(xs, labels):
        b.append(box(x, 244, 99, 52, l, "reuse", 9.6))

    b.append(lane(10, 326, 740, 76, "", "#FDF9F1"))
    ext = [["Safaricom M-Pesa", "each tenant's paybills"], ["Banks", "tenant accounts"],
           ["KRA", "eTIMS, WHT, PIN checks"], ["Africa's Talking", "SMS"], ["WhatsApp Cloud API", "messages"]]
    for i, l in enumerate(ext):
        b.append(box(20 + i * 147, 348, 135, 46, l, "ext", 10))

    b.append(box(10, 414, 740, 32, ["Platform: PostgreSQL per service with tenant row security, Redis, NATS JetStream, MinIO, Cloudflare, Kubernetes, GitOps"], "grey", 9.6, bold_first=False))

    b.append(arrow([(106, 72), (119, 118)]))
    b.append(arrow([(288, 72), (320, 118)]))
    b.append(arrow([(470, 72), (370, 118)]))
    b.append(arrow([(652, 72), (420, 118)]))
    b.append(arrow([(462, 142), (500, 142)], "REST"))
    b.append(arrow([(119, 118), (119, 106), (640, 106), (640, 118)], dashed=True))
    b.append(label_bg(380, 110, "published listings (R3)"))
    b.append(arrow([(260, 166), (65, 244)], "sign-in", lx=150, ly=210))
    b.append(arrow([(300, 166), (170, 244)], "pay modal", lx=226, ly=228))
    for x in xs[1:]:
        b.append(arrow([(618, 166), (x + 50, 244)], color=BRAND))
    b.append(label_bg(690, 200, "S2S"))
    b.append(arrow([(150, 296), (88, 348)]))
    b.append(arrow([(170, 296), (234, 348)]))
    b.append(arrow([(185, 296), (381, 348)]))
    b.append(arrow([(380, 296), (528, 348)]))
    b.append(arrow([(400, 296), (675, 348)]))
    for y, t in ((8, "Users"), (98, "Property applications"), (222, "Codevertex platform services"), (326, "External providers")):
        b.append(lane_title(10, y, t))
    b.append(legend(20, 458, [("new", "Built for the platform"), ("reuse", "Existing Codevertex service"),
                              ("ext", "Third party"), ("user", "People")]))
    b.append(text(740, 467, "Dashed: Release 3", 9.5, 500, MUTED, "end"))
    return svg(760, 476, "".join(b), "Solution architecture")


def fig_funds():
    b = []
    b.append(box(10, 30, 140, 56, ["Buyers", "deposit, instalments"], "user", 10))
    b.append(box(10, 150, 140, 56, ["Owners and occupants", "service charge, water"], "user", 10))
    b.append(lane(180, 10, 270, 100, "Sales collections", "#FDF9F1"))
    b.append(box(195, 40, 240, 56, ["Sales paybill and bank account", "account S-unit, e.g. S-B07"], "ext", 10))
    b.append(lane(180, 130, 270, 100, "Estate service fund", "#F3FAF6"))
    b.append(box(195, 160, 240, 56, ["Estate paybill and bank account", "account = unit code, e.g. B07"], "reuse", 10))
    b.append(box(500, 30, 250, 56, ["Developer revenue", "unit sale price, recognised by treasury"], "new", 10))
    b.append(box(500, 150, 250, 56, ["Estate operations", "vendors, utilities, staff, sinking fund"], "new", 10))
    b.append(arrow([(150, 58), (195, 68)]))
    b.append(arrow([(150, 178), (195, 188)]))
    b.append(arrow([(435, 68), (500, 58)]))
    b.append(arrow([(435, 188), (500, 178)]))
    b.append(text(380, 250, "Funds never mix: each pool has its own paybill, bank account and ledger, so the estate books can be", 9.5, 400, MUTED))
    b.append(text(380, 264, "handed to the owners' management corporation on its own.", 9.5, 400, MUTED))

    b.append(lane(10, 280, 740, 150, "Treasury books (double entry)", "#F3FAF6"))
    rows = [("Sale agreement signed", "DR Unit Sales Receivable", "CR Deferred Sale Income"),
            ("Instalment received", "DR Sales Bank or M-Pesa", "CR Unit Sales Receivable"),
            ("Monthly estate invoice", "DR Owner Receivable", "CR Service Charge, Water, Sinking Fund"),
            ("Vendor bill paid", "DR Estate Expense (by cost centre)", "CR Estate Bank, CR WHT Payable")]
    for i, (a, d, c) in enumerate(rows):
        y = 308 + i * 29
        b.append(text(24, y + 12, a, 10, 600, INK, "start"))
        b.append(box(215, y, 255, 22, [d], "plain", 9.5, bold_first=False))
        b.append(box(480, y, 260, 22, [c], "plain", 9.5, bold_first=False))
    return svg(760, 438, "".join(b), "Fund segregation and accounting")


def fig_sale_states():
    b = []
    b.append(pill(10, 90, 100, 34, "available", "reuse", 10.5))
    b.append(pill(160, 90, 100, 34, "reserved", "ext", 10.5))
    b.append(pill(310, 90, 130, 34, "under agreement", "ext", 10.5))
    b.append(pill(490, 90, 110, 34, "fully paid", "new", 10.5))
    b.append(pill(650, 90, 100, 34, "handed over", "new", 10.5))
    b.append(pill(310, 200, 130, 34, "in default", "warn", 10.5))
    b.append(pill(650, 200, 100, 34, "titled", "reuse", 10.5))
    b.append(arrow([(110, 107), (160, 107)], "fee paid", lx=135, ly=84))
    b.append(arrow([(260, 107), (310, 107)], "signed", lx=285, ly=84))
    b.append(arrow([(440, 107), (490, 107)], "balance 0", lx=465, ly=84))
    b.append(arrow([(600, 107), (650, 107)], "handover", lx=625, ly=84))
    b.append(arrow([(700, 124), (700, 200)], "title registered", lx=690, ly=166, anchor="end"))
    b.append(arrow([(350, 124), (350, 200)], "missed beyond grace", lx=340, ly=166, anchor="end"))
    b.append(arrow([(400, 200), (400, 124)], "arrears cleared", lx=410, ly=166, anchor="start"))
    b.append(arrow([(310, 217), (60, 217), (60, 124)], "terminated per agreement, refund per terms", lx=185, ly=211))
    b.append(arrow([(210, 90), (210, 50), (60, 50), (60, 90)], "reservation lapsed", lx=135, ly=44))
    b.append(text(470, 250, "Buyers pay outright or by deposit and instalments; both paths end at fully paid.", 9.5, 400, MUTED))
    return svg(760, 262, "".join(b), "Unit sale lifecycle")


def fig_billing():
    b = []
    steps = [("25th", ["Meter readings", "photo per meter"], "new"), ("26 to 28", ["Validation", "spikes, zeros, gaps"], "warn"),
             ("1st", ["Billing run", "all charges, per unit"], "new"), ("1st", ["Invoices issued", "treasury, numbered"], "reuse"),
             ("1st", ["Owners notified", "SMS, WhatsApp, email"], "reuse"), ("10th", ["Due date", "reminders after"], "grey")]
    w, g = 112, 13
    for i, (when, l, kind) in enumerate(steps):
        x = 10 + i * (w + g)
        b.append(box(x, 34, w, 60, l, kind, 10.2))
        b.append(text(x + w / 2, 22, when, 9.5, 700, GOLD))
        if i < len(steps) - 1:
            b.append(arrow([(x + w, 64), (x + w + g, 64)]))
    b.append(arrow([(191, 94), (191, 124), (66, 124), (66, 94)], "re-read or estimate", lx=128, ly=118))
    b.append(text(380, 150, "A billing run is keyed by estate and month, so a retry never issues a second invoice for the same unit and period.", 9.5, 400, MUTED))
    return svg(760, 160, "".join(b), "Monthly billing cycle")


def fig_water():
    b = []
    b.append(box(10, 20, 150, 46, ["Mavoko Water", "bulk meter"], "ext", 10))
    b.append(box(10, 80, 150, 46, ["Borehole 1", "abstraction meter"], "ext", 10))
    b.append(box(10, 140, 150, 46, ["Borehole 2", "abstraction meter"], "ext", 10))
    b.append(box(220, 70, 150, 66, ["Reservoir and", "tanks", "total supplied"], "reuse", 10))
    for y in (43, 103, 163):
        b.append(arrow([(160, y), (220, 103)]))
    b.append(box(430, 20, 150, 40, ["Unit sub-meters", "sum billed"], "new", 10))
    b.append(box(430, 76, 150, 40, ["Common areas", "gardens, washing bays"], "grey", 10))
    b.append(box(430, 132, 150, 40, ["Unaccounted", "leaks, unmetered use"], "warn", 10))
    b.append(arrow([(370, 92), (430, 40)]))
    b.append(arrow([(370, 103), (430, 96)]))
    b.append(arrow([(370, 114), (430, 152)]))
    b.append(box(620, 60, 130, 76, ["Water balance", "report", "alert above", "set loss %"], "new", 10))
    b.append(arrow([(580, 40), (640, 60)]))
    b.append(arrow([(580, 152), (640, 136)]))
    return svg(760, 196, "".join(b), "Water balance")


def fig_payment():
    actors = [("o", "Owner|phone", "user"), ("mp", "M-Pesa", "ext"), ("tr", "treasury-api", "reuse"),
              ("es", "maskani-api", "new"), ("nt", "notifications|api", "reuse")]
    msgs = [
        ("o", "mp", "Paybill, account B07, KES 6,450", "call"),
        ("mp", "tr", "C2B confirmation", "call"),
        ("tr", "tr", "store once per M-Pesa receipt", "self"),
        ("tr", "tr", "match B07 to owner account", "self"),
        ("tr", "tr", "allocate oldest invoice first, post ledger", "self"),
        ("tr", "es", "payment.succeeded over NATS", "reply"),
        ("es", "es", "update unit balance view", "self"),
        ("es", "nt", "receipt to owner", "call"),
        ("nt", "o", "SMS or WhatsApp receipt", "reply"),
    ]
    return sequence(actors, msgs, title="Paybill payment sequence")


def fig_workorder():
    b = []
    b.append(box(10, 20, 140, 46, ["Request raised", "resident, staff, schedule"], "user", 10))
    b.append(arrow([(150, 43), (185, 43)]))
    b.append(box(185, 20, 140, 46, ["Triage", "category, priority, SLA"], "new", 10))
    b.append(arrow([(325, 43), (370, 43)]))
    b.append(diamond(445, 43, 150, 60, ["Who does it?"]))
    b.append(arrow([(520, 43), (570, 43)], "vendor"))
    b.append(box(570, 20, 180, 46, ["Vendor assigned", "quote if above limit"], "ext", 10))
    b.append(arrow([(445, 73), (445, 100)], "staff", lx=458, ly=92, anchor="start"))
    b.append(box(360, 100, 170, 42, ["Staff assigned", "erp-api employee"], "reuse", 10))
    b.append(arrow([(660, 66), (660, 160), (530, 160)]))
    b.append(arrow([(445, 142), (445, 165)]))
    b.append(box(330, 165, 230, 42, ["Work done", "photos, parts, time on site"], "new", 10))
    b.append(arrow([(330, 186), (260, 186)]))
    b.append(box(90, 165, 170, 42, ["Resident confirms", "or reopens in 7 days"], "user", 10))
    b.append(arrow([(175, 207), (175, 230)]))
    b.append(box(60, 230, 230, 40, ["Closed; cost to estate, or", "recharged to the unit if in-unit"], "reuse", 10))
    b.append(text(560, 245, "Breached SLA timers raise an alert", 9.5, 500, MUTED, "start"))
    b.append(text(560, 259, "to the estate manager.", 9.5, 500, MUTED, "start"))
    return svg(760, 280, "".join(b), "Work order flow")


def fig_vendor():
    steps = [["Onboard", "licences, KRA PIN"], ["Contract", "scope, fee, SLAs"], ["Schedule", "visits, posts, rosters"],
             ["Evidence", "check-ins, photos"], ["Invoice", "eTIMS, SLA credits"], ["Approve", "budget, OTP"], ["Pay", "bank or M-Pesa"]]
    b = []
    w, g = 96, 11
    kinds = ["new", "new", "new", "new", "reuse", "reuse", "reuse"]
    for i, l in enumerate(steps):
        x = 10 + i * (w + g)
        b.append(box(x, 20, w, 60, l, kinds[i], 10))
        if i < len(steps) - 1:
            b.append(arrow([(x + w, 50), (x + w + g, 50)]))
    b.append(text(10, 104, "maskani-api runs the first four steps. treasury-api holds the vendor bill, the approval and the payment.", 9.5, 400, MUTED, "start"))
    return svg(760, 112, "".join(b), "Service provider cycle")


def fig_gate():
    b = []
    b.append(box(10, 20, 150, 48, ["Visitor at gate"], "user", 10.5))
    b.append(arrow([(160, 44), (200, 44)]))
    b.append(diamond(285, 44, 170, 64, ["Has a pass?", "QR or 6-digit code"]))
    b.append(arrow([(370, 44), (420, 44)], "yes"))
    b.append(box(420, 20, 150, 48, ["Pass checked", "unit, time window"], "new", 10))
    b.append(arrow([(570, 44), (605, 44)]))
    b.append(box(605, 20, 145, 48, ["Entry logged", "host notified"], "reuse", 10))
    b.append(arrow([(285, 76), (285, 110)], "no", lx=298, ly=98, anchor="start"))
    b.append(box(190, 110, 190, 48, ["Guard records name, phone", "and host unit"], "new", 10))
    b.append(arrow([(380, 134), (420, 134)]))
    b.append(box(420, 110, 150, 48, ["Host approves", "in app or by SMS"], "user", 10))
    b.append(arrow([(570, 134), (677, 134), (677, 68)], "approved", lx=630, ly=128))
    b.append(arrow([(495, 158), (495, 185)], "declined or no reply in 5 min", lx=505, ly=178, anchor="start"))
    b.append(box(420, 185, 150, 36, ["Entry refused, logged"], "warn", 10))
    return svg(760, 230, "".join(b), "Visitor entry")


def fig_onboarding():
    steps = [("1", ["Import", "units and owners"]), ("2", ["Invite", "SMS link"]), ("3", ["Sign in", "phone OTP"]),
             ("4", ["Confirm", "terms, privacy"]), ("5", ["Household", "occupants, cars"]), ("6", ["Statement", "opening balance"])]
    b = []
    w, g = 112, 13
    for i, (n, l) in enumerate(steps):
        x = 10 + i * (w + g)
        kind = "reuse" if i in (2, 5) else "new"
        b.append(box(x, 30, w, 60, l, kind, 10.5))
        b.append(f'<circle cx="{x+14}" cy="30" r="11" fill="{BRAND}"/>' + text(x + 14, 34, n, 10, 700, "#FFFFFF"))
        if i < len(steps) - 1:
            b.append(arrow([(x + w, 60), (x + w + g, 60)]))
    return svg(760, 100, "".join(b), "Owner onboarding")


def fig_erd():
    b = []
    ents = {
        "port": (10, 20, ["portfolios, mandates", "tenant_id, client (landlord)", "fee rules, remittance account"]),
        "prop": (285, 20, ["properties, blocks", "tenant_id, portfolio_id, type", "location, outlet_id (auth)"]),
        "unit": (560, 20, ["units", "property_id, code, use, size", "entitlement, status"]),
        "own": (10, 140, ["ownerships, occupancies", "unit_id, party, from, to", "bill_to rules, account_id"]),
        "lease": (285, 140, ["leases (R2)", "unit_id, tenant party, term", "rent, escalation, deposit"]),
        "chg": (560, 140, ["charge_rules, meters", "basis, rate, fund", "readings, photo_key"]),
        "sale": (10, 260, ["sale_contracts", "unit_id, buyer, price", "plan_id (treasury), title"]),
        "run": (285, 260, ["billing_runs, run_lines", "tenant, property, period", "invoice_id (treasury)"]),
        "wo": (560, 260, ["work_orders, vendors", "unit or area, priority, SLA", "vendor_id (treasury)"]),
        "list": (10, 380, ["listings (R3)", "unit_id or land, type, price", "status, verified_at, geo"]),
        "gate": (285, 380, ["passes, gate_events", "property_id, code_hash", "monthly partitions"]),
        "agg": (560, 380, ["daily_stats", "tenant, property, day", "collections, occupancy"]),
    }
    for k, (x, y, lines) in ents.items():
        h = 22 + 15 * (len(lines) - 1) + 8
        b.append(f'<rect x="{x}" y="{y}" width="190" height="{h}" rx="6" fill="#fff" stroke="{BRAND}" stroke-width="1.2"/>')
        b.append(f'<rect x="{x}" y="{y}" width="190" height="22" rx="6" fill="{BRAND}"/>')
        b.append(text(x + 95, y + 15, lines[0], 10.5, 700, "#FFFFFF"))
        for i, ln in enumerate(lines[1:]):
            b.append(text(x + 10, y + 37 + i * 15, ln, 9.5, 400, INK, "start"))
    b.append(arrow([(200, 50), (285, 50)], "1 : n"))
    b.append(arrow([(475, 50), (560, 50)], "1 : n"))
    b.append(arrow([(560, 75), (200, 150)], "1 : n", lx=330, ly=112))
    b.append(arrow([(600, 95), (475, 150)], "1 : n", lx=548, ly=128))
    b.append(text(380, 482, "Every table carries tenant_id; row-level security enforces it in the database.", 9.5, 500, MUTED))
    return svg(760, 490, "".join(b), "maskani-api data model")


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

    r = [f'<rect x="22" y="60" width="196" height="70" rx="10" fill="{GOLD_SOFT}"/>',
         text(120, 84, "Unit B07, 3 bedroom", 12, 700, INK), text(120, 100, "Balance due KES 6,450", 10, 600, INK),
         text(120, 116, "Due 10 November", 9.5, 400, MUTED),
         card(22, 140, "Pay now", "M-Pesa paybill or prompt", "Pay"),
         card(22, 210, "Purchase plan", "KES 4.2M of 7.5M paid", "View", 0.56),
         card(22, 280, "Water, October", "9 m3, reading photo", "View"),
         text(120, 370, "Requests  Visitors  Notices", 9.5, 600, GREEN)]
    g = [f'<rect x="282" y="60" width="196" height="54" rx="10" fill="{BRAND_SOFT}"/>',
         text(380, 82, "Main gate", 12, 700, INK), text(380, 98, "Guard: on duty since 06:00", 9.5, 400, MUTED),
         f'<rect x="296" y="124" width="168" height="30" rx="6" fill="{GREY_SOFT}"/>', text(380, 144, "Enter code or scan QR", 10.5, 500, MUTED),
         card(282, 166, "Pass valid", "Guest of B07 until 18:00", "Admit"),
         card(282, 236, "Walk-in visitor", "Ask host to approve", "New"),
         card(282, 306, "Patrol round", "4 of 6 points scanned", "Scan", 0.66)]
    m = [f'<rect x="542" y="60" width="196" height="64" rx="10" fill="#fff" stroke="{LINE}"/>',
         text(640, 82, "October collections", 10.5, 700, INK), text(640, 100, "KES 1.31M of 1.52M billed", 10, 600, INK),
         f'<rect x="556" y="108" width="168" height="6" rx="3" fill="{GOLD_SOFT}"/>', f'<rect x="556" y="108" width="145" height="6" rx="3" fill="{GOLD}"/>',
         card(542, 136, "Arrears over 60 days", "7 units, KES 96,300", "List"),
         card(542, 206, "Work orders", "12 open, 2 past SLA", "Open"),
         card(542, 276, "Water loss", "8.4% this month", "View"),
         text(640, 370, "Vendors due for renewal: 1", 9.5, 600, MUTED)]
    body = phone(10, "Owner portal", r) + phone(270, "Gate tablet", g) + phone(530, "Manager dashboard", m)
    return svg(760, 420, body, "Key screens, low fidelity")


def fig_gantt():
    rows = [
        ("Product delivery", 0, 0, "plain", True),
        ("Sprint 0: discovery, design, data audit", 1, 1, "new"),
        ("Sprint 1: units, owners, portal, import", 2, 3, "new"),
        ("Sprint 2: charges, meters, billing, paybill", 4, 5, "new"),
        ("Sprint 3: sales, instalments, statements", 6, 7, "new"),
        ("Sprint 4: vendors, works, gate, patrols", 8, 10, "new"),
        ("Sprint 5: reports, ERP link, compliance", 11, 12, "new"),
        ("Hardening, parallel billing run, UAT", 13, 13, "warn"),
        ("Launch, training and handover", 14, 14, "reuse"),
        ("Shaba Village workstream", 0, 0, "plain", True),
        ("Owner register, balances, sale files", 1, 4, "ext"),
        ("Paybill and Daraja access for both funds", 1, 3, "ext"),
        ("Vendor contracts and licences", 3, 8, "ext"),
        ("ODPC registration, DPIA, by-law review", 2, 10, "ext"),
    ]
    return gantt(rows, weeks=14, milestones=[(0.5, "M1 Kick-off"), (7, "M2 Demo"), (12, "M3 Features", "end"), (14, "M4 Launch", "end")],
                 title="Implementation schedule")


def fig_ownership():
    b = []
    cols = [
        (10, "Owned by each tenant", "new", [["Estate data", "owners, units, ledgers"], ["Money", "own paybills and banks"],
                                                ["Documents", "agreements, by-laws"], ["Brand and accounts", "domain, paybills, Meta"]]),
        (265, "Licensed from Codevertex", "reuse", [["Property platform", "maskani-api, maskani-ui"], ["Treasury and ERP", "books, payroll"],
                                                   ["Notifications", "SMS, WhatsApp, email"], ["Platform operations", "hosting, backups, deploys"]]),
        (520, "Third-party providers", "ext", [["Safaricom", "M-Pesa paybills"], ["Banks", "tenant accounts"],
                                              ["Africa's Talking", "SMS delivery"], ["Meta", "WhatsApp delivery"]]),
    ]
    for x, title, kind, items in cols:
        b.append(lane(x, 8, 230, 268, ""))
        b.append(text(x + 115, 32, title, 12, 700, INK))
        for i, it in enumerate(items):
            b.append(box(x + 15, 48 + i * 56, 200, 46, it, kind, 10.5))
    b.append(arrow([(240, 140), (265, 140)], color=BRAND))
    b.append(arrow([(495, 140), (520, 140)], color=BRAND))
    b.append(text(380, 296, "Each tenant licenses the platform for its subscription term; its data, documents and money remain its own.", 9.5, 400, MUTED))
    return svg(760, 306, "".join(b), "Ownership boundaries")


def fig_tenancy():
    b = []
    b.append(box(280, 8, 200, 40, ["Codevertex platform", "operations, plans, marketplace"], "grey", 10))
    tenants = [(20, ["Estate operator", "e.g. Shaba Village"], "new"), (270, ["Property manager", "manages for landlords"], "new"),
               (520, ["Landlord or developer", "self-managed"], "new")]
    for x, l, k in tenants:
        b.append(box(x, 78, 220, 44, l, k, 10.5))
        b.append(arrow([(380, 48), (x + 110, 78)]))
    b.append(label_bg(380, 68, "tenant = organisation in auth-api"))
    b.append(box(270, 150, 220, 40, ["Client portfolios", "one per landlord, with mandate"], "reuse", 10))
    b.append(arrow([(380, 122), (380, 150)]))
    b.append(box(20, 150, 220, 40, ["Estate", "phases, blocks"], "reuse", 10))
    b.append(arrow([(130, 122), (130, 150)]))
    b.append(box(520, 150, 220, 40, ["Own portfolio", "buildings, plots"], "reuse", 10))
    b.append(arrow([(630, 122), (630, 150)]))
    b.append(box(150, 218, 460, 40, ["Properties", "estates, apartment blocks, office and retail buildings, land; staff assigned per property"], "reuse", 10))
    for x in (130, 380, 630):
        b.append(arrow([(x, 190), (380 if x == 380 else (250 if x < 380 else 510), 218)]))
    b.append(box(150, 284, 460, 40, ["Units", "houses, apartments, offices, shops, bays, plots"], "reuse", 10))
    b.append(arrow([(380, 258), (380, 284)]))
    b.append(box(40, 350, 210, 40, ["Owners, buyers", "estate and sales accounts"], "user", 10))
    b.append(box(275, 350, 210, 40, ["Tenants and occupants", "leases (R2)"], "user", 10))
    b.append(box(510, 350, 210, 40, ["Listings (R3)", "published to the marketplace"], "ext", 10))
    for x in (145, 380, 615):
        b.append(arrow([(380, 324), (x, 350)]))
    return svg(760, 398, "".join(b), "Tenant and property hierarchy")


def fig_releases():
    rows = [("R1", "MVP and Shaba Village launch", "14 weeks", "Multi-tenant core, properties and units, staff per property, estate billing, utilities, sales and instalments, owner portal, providers, works, gate, ERP staff, reports", "new"),
            ("R2", "Rental and portfolio management", "Q2 2027", "Landlord clients and mandates, tenant onboarding, leases, rent and deposits, inspections, turnover repairs, landlord statements and remittances, commercial leases", "reuse"),
            ("R3", "Public marketplace", "Q3 2027", "Listings for rent and sale (homes, offices, shops, land), search and map, enquiries, viewings, applications, verified listers, featured listings", "ext"),
            ("R4", "Extensions", "Later", "Native apps, smart meters, e-signatures, tenant credit checks, owner voting, AI assistant", "grey")]
    b = []
    for i, (r, t, when, d, k) in enumerate(rows):
        y = 10 + i * 66
        b.append(box(10, y, 70, 56, [r], k, 16))
        b.append(box(90, y, 660, 56, [], "plain"))
        b.append(text(104, y + 20, t, 11, 700, INK, "start"))
        b.append(text(740, y + 20, when, 10, 700, GOLD, "end"))
        words, line, lines = d.split(" "), "", []
        for w in words:
            if len(line) + len(w) > 112:
                lines.append(line)
                line = w
            else:
                line = (line + " " + w).strip()
        lines.append(line)
        for j, ln in enumerate(lines[:2]):
            b.append(text(104, y + 36 + j * 13, ln, 9.4, 400, MUTED, "start"))
    return svg(760, 276, "".join(b), "Release plan")


def fig_lease():
    b = []
    steps = [["Listing or enquiry", "vacant unit"], ["Application", "consent, KYC"], ["Approval", "manager, landlord"],
             ["Lease and deposit", "signed, paid"], ["Move-in", "inspection, keys"]]
    w, g = 132, 15
    for i, l in enumerate(steps):
        x = 10 + i * (w + g)
        b.append(box(x, 20, w, 54, l, "new" if i else "ext", 10))
        if i < len(steps) - 1:
            b.append(arrow([(x + w, 47), (x + w + g, 47)]))
    steps2 = [["Monthly rent", "invoices, M-Pesa"], ["Renewal or review", "notice, escalation"], ["Move-out", "inspection, readings"],
              ["Deposit settled", "deductions itemised"], ["Turnover", "repaint, repairs, clean"]]
    for i, l in enumerate(steps2):
        x = 10 + (4 - i) * (w + g)
        b.append(box(x, 120, w, 54, l, "reuse" if i < 4 else "warn", 10))
        if i < len(steps2) - 1:
            b.append(arrow([(x, 147), (x - g, 147)]))
    b.append(arrow([(674, 74), (674, 120)]))
    b.append(arrow([(76, 120), (76, 74)], "vacant again", lx=88, ly=100, anchor="start"))
    b.append(text(380, 198, "Rent collected is remitted to the landlord monthly, net of management fees, approved expenses and withholding tax.", 9.5, 400, MUTED))
    return svg(760, 206, "".join(b), "Lease lifecycle")


def fig_listing():
    b = []
    b.append(box(10, 20, 150, 48, ["Lister", "manager, agent, developer"], "user", 10))
    b.append(arrow([(160, 44), (195, 44)]))
    b.append(box(195, 20, 150, 48, ["Verification", "KYC, EARB, documents"], "warn", 10))
    b.append(arrow([(345, 44), (380, 44)]))
    b.append(box(380, 20, 150, 48, ["Moderation", "photos, price, duplicates"], "warn", 10))
    b.append(arrow([(530, 44), (565, 44)]))
    b.append(box(565, 20, 185, 48, ["Published", "search, map, share link"], "new", 10))
    b.append(arrow([(657, 68), (657, 100)]))
    b.append(box(565, 100, 185, 48, ["House hunter", "enquiry or viewing request"], "user", 10))
    b.append(arrow([(565, 124), (530, 124)]))
    b.append(box(380, 100, 150, 48, ["Lead to lister", "contact masked, CRM"], "reuse", 10))
    b.append(arrow([(380, 124), (345, 124)]))
    b.append(box(195, 100, 150, 48, ["Viewing", "booked, confirmed"], "reuse", 10))
    b.append(arrow([(195, 124), (160, 124)]))
    b.append(box(10, 100, 150, 48, ["Application", "into R2 leasing or sale"], "new", 10))
    b.append(text(380, 172, "Units managed on the platform can be published from their vacancy in one step, already verified.", 9.5, 400, MUTED))
    return svg(760, 180, "".join(b), "Listing and enquiry flow")
