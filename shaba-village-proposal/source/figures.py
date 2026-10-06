from diagrams import *  # noqa: F401,F403


def fig_architecture():
    b = []
    b.append(lane(10, 8, 740, 72, ""))
    users = [["Owners and residents", "phone, no app install"], ["Estate management", "office, finance, caretaker"],
             ["Gate and guards", "tablet at each gate"], ["Service providers", "agency supervisors"]]
    for i, l in enumerate(users):
        b.append(box(22 + i * 182, 30, 168, 42, l, "user", 10.2))

    b.append(lane(10, 98, 740, 76, "", "#FBF6FA"))
    b.append(box(60, 118, 250, 48, ["estates-ui", "Next.js PWA: portal, console, gate, vendors"], "new", 10.2))
    b.append(box(430, 118, 270, 48, ["estates-api", "Go: units, charges, meters, sales, works"], "new", 10.2))

    b.append(lane(10, 222, 740, 84, "", "#F3FAF6"))
    xs = [20, 167, 314, 461, 608]
    labels = [["auth-api", "SSO, phone OTP, roles"], ["treasury-api", "invoices, M-Pesa, ledger"],
              ["erp-api", "staff, payroll, casuals"], ["notifications-api", "SMS, WhatsApp, email"],
              ["subscriptions-api", "plan and features"]]
    for x, l in zip(xs, labels):
        b.append(box(x, 244, 135, 52, l, "reuse", 10.2))

    b.append(lane(10, 326, 740, 76, "", "#FDF9F1"))
    ext = [["Safaricom M-Pesa", "Shaba paybills"], ["Bank", "estate and sales accounts"],
           ["KRA", "eTIMS, PIN checks"], ["Africa's Talking", "SMS"], ["WhatsApp Cloud API", "messages"]]
    for x, l in zip(xs, ext):
        b.append(box(x, 348, 135, 46, l, "ext", 10.2))

    b.append(box(10, 414, 740, 32, ["Platform: PostgreSQL per service, Redis, NATS JetStream, MinIO, Cloudflare edge, Kubernetes with GitOps"], "grey", 10, bold_first=False))

    b.append(arrow([(106, 72), (150, 118)]))
    b.append(arrow([(288, 72), (220, 118)]))
    b.append(arrow([(470, 72), (290, 118)]))
    b.append(arrow([(652, 72), (300, 118)]))
    b.append(arrow([(310, 142), (430, 142)], "REST"))
    b.append(arrow([(110, 166), (88, 244)], "sign-in", lx=84, ly=205))
    b.append(arrow([(200, 166), (225, 244)], "pay modal", lx=200, ly=205))
    b.append(arrow([(445, 166), (300, 244)], color=BRAND))
    for tx in (382, 529, 676):
        b.append(arrow([(565, 166), (tx, 244)], color=BRAND))
    b.append(label_bg(660, 205, "S2S, service-client"))
    b.append(arrow([(262, 244), (470, 166)], color=GREEN, dashed=True))
    b.append(label_bg(372, 192, "payment and bill events (NATS)"))
    b.append(arrow([(234, 296), (88, 348)]))
    b.append(arrow([(250, 296), (234, 348)]))
    b.append(arrow([(270, 296), (382, 348)]))
    b.append(arrow([(529, 296), (529, 348)]))
    b.append(arrow([(560, 296), (660, 348)]))
    for y, t in ((8, "Users"), (98, "Estate applications"), (222, "Codevertex platform services"), (326, "External providers")):
        b.append(lane_title(10, y, t))
    b.append(legend(20, 458, [("new", "Built for the estate"), ("reuse", "Codevertex platform service"),
                              ("ext", "Third party"), ("user", "People")]))
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
              ("es", "estates-api", "new"), ("nt", "notifications|api", "reuse")]
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
    b.append(box(360, 100, 170, 42, ["Estate staff assigned", "erp-api employee"], "reuse", 10))
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
    b.append(text(10, 104, "estates-api runs the first four steps. treasury-api holds the vendor bill, the approval and the payment.", 9.5, 400, MUTED, "start"))
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
        "unit": (10, 20, ["units", "estate_id, block, code (B07)", "type, size, entitlement", "sale_status, occupancy"]),
        "own": (285, 20, ["unit_ownerships", "unit_id, owner_id, share", "from_date, to_date", "treasury_account_id"]),
        "occ": (560, 20, ["occupancies", "unit_id, occupant, role", "bill_to rules, from, to"]),
        "chg": (10, 150, ["charge_rules", "charge type, basis", "rate, from_date, fund", "penalty rule ref"]),
        "met": (285, 150, ["meters, meter_readings", "unit_id or source, serial", "reading, photo_key", "status, period"]),
        "run": (560, 150, ["billing_runs, run_lines", "estate_id, period (unique)", "unit_id, invoice_id (treasury)"]),
        "sale": (10, 285, ["sale_contracts", "unit_id, buyer_id, price", "plan_id (treasury)", "title_stage, handover_at"]),
        "wo": (285, 285, ["work_orders", "unit_id or area, category", "priority, sla_due_at", "assignee (vendor or erp)"]),
        "ven": (560, 285, ["vendor_contracts, visits", "vendor_id (treasury), sla", "schedule, evidence keys"]),
        "gate": (10, 410, ["passes, gate_events", "unit_id, code_hash, window", "event time (monthly partitions)"]),
        "agg": (285, 410, ["estate_daily_stats", "estate_id, day (unique)", "collections, water, works"]),
        "pers": (560, 410, ["agency_personnel, posts", "vendor_id, name, role", "post, shift, patrol scans"]),
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
    b.append(arrow([(380, 110), (380, 150)], "1 : n", lx=400, ly=135))
    b.append(arrow([(475, 180), (560, 180)], "feeds"))
    b.append(arrow([(200, 180), (285, 180)], "prices"))
    b.append(arrow([(470, 315), (560, 315)], "vendor"))
    return svg(760, 485, "".join(b), "estates-api data model")


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
        (10, "Owned by Shaba Village", "new", [["Estate data", "owners, units, ledgers"], ["Money", "own paybills and banks"],
                                                ["Documents", "agreements, by-laws"], ["Brand and accounts", "domain, Safaricom, Meta"]]),
        (265, "Licensed from Codevertex", "reuse", [["Estates service", "estates-api, estates-ui"], ["Treasury and ERP", "books, payroll"],
                                                   ["Notifications", "SMS, WhatsApp, email"], ["Platform operations", "hosting, backups, deploys"]]),
        (520, "Third-party providers", "ext", [["Safaricom", "M-Pesa paybills"], ["Banks", "estate and sales accounts"],
                                              ["Africa's Talking", "SMS delivery"], ["Meta", "WhatsApp delivery"]]),
    ]
    for x, title, kind, items in cols:
        b.append(lane(x, 8, 230, 268, ""))
        b.append(text(x + 115, 32, title, 12, 700, INK))
        for i, it in enumerate(items):
            b.append(box(x + 15, 48 + i * 56, 200, 46, it, kind, 10.5))
    b.append(arrow([(240, 140), (265, 140)], color=BRAND))
    b.append(arrow([(495, 140), (520, 140)], color=BRAND))
    b.append(text(380, 296, "Shaba Village licenses the platform for the term of the service agreement; its data, documents and money remain its own.", 9.5, 400, MUTED))
    return svg(760, 306, "".join(b), "Ownership boundaries")
