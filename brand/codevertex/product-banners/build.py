"""Generate the POS Suite and ERP Suite promo banners (1080x1600 HTML).

Feature copy comes from the subscriptions-api seed catalogue
(cmd/seed/plans_powersuite_usecase.go, plans_erp.go, products.go).
Run:  python3 build.py   -> pos-suite.html, erp-suite.html
"""
from pathlib import Path

HERE = Path(__file__).parent

ICONS = {
    "phone": '<rect x="6" y="2" width="12" height="20" rx="2.5"/><path d="M10 18h4"/>',
    "wifi_off": '<path d="M2 8.8a15 15 0 0 1 4.2-2.6M10.7 5.1A15 15 0 0 1 22 8.8M5 12.5a10 10 0 0 1 5.2-2.7M16.8 11a10 10 0 0 1 2.2 1.5M8.5 16a5 5 0 0 1 7 0M12 20h.01M3 3l18 18"/>',
    "box": '<path d="M21 8l-9-5-9 5 9 5 9-5z"/><path d="M3 8v8l9 5 9-5V8M12 13v8"/>',
    "chart": '<path d="M3 20h18M6 16v-4M10 16V9M14 16v-6M18 16V5"/>',
    "users": '<circle cx="9" cy="8" r="3.2"/><path d="M3 20v-1a6 6 0 0 1 12 0v1M16 4.5a3.2 3.2 0 0 1 0 6.4M21 20v-1a6 6 0 0 0-3.5-5.4"/>',
    "cart": '<circle cx="9" cy="20" r="1.5"/><circle cx="18" cy="20" r="1.5"/><path d="M2 3h3l2.7 11.5h11L21 7H6.2"/>',
    "building": '<rect x="4" y="3" width="16" height="18" rx="1.5"/><path d="M9 7h1M14 7h1M9 11h1M14 11h1M9 15h1M14 15h1M10 21v-3h4v3"/>',
    "pie": '<path d="M12 3a9 9 0 1 0 9 9h-9z"/><path d="M15 3.5A9 9 0 0 1 20.5 9H15z"/>',
    "cal": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4M7 14h3M14 14h3M7 17.5h3"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',
    "call": '<path d="M5 3h4l2 5-2.5 1.5a11 11 0 0 0 6 6L16 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 5a2 2 0 0 1 2-2"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
}


def icon(name, cls="ico"):
    return f'<svg class="{cls}" viewBox="0 0 24 24">{ICONS[name]}</svg>'


POS = dict(
    slug="pos-suite",
    title="Codevertex POS Suite",
    h3size="92px",
    accent="#F59E0B", accent_dark="#B45309", accent_soft="#FEF3C7",
    product="POS Suite", product_sub="Sell · Track · Grow",
    h1="STILL RUNNING", h2="YOUR SHOP ON", h3="PAPER?",
    pains=["Long queues at the till", "Cash &amp; M-Pesa that never balance",
           "Stock running out unnoticed", "No idea what actually sells",
           "Shift handovers full of gaps"],
    before_title="Daily sales book",
    before_lines=[("Sugar 2kg x3", "720?"), ("Bread", "60"), ("M-Pesa — Wanjiku", "??"),
                  ("Soap (on credit)", "—"), ("Cash in drawer", "4,150")],
    before_total=("TOTAL", "doesn't add up!"),
    ribbon1="CODEVERTEX POS", ribbon2="SELLS, COUNTS &amp; BALANCES FOR YOU!",
    lead="Sell faster at the till",
    body="Checkout, M-Pesa, receipts, stock, shifts and reports, synced live across every outlet,",
    lead2="all in one system.",
    chips=["Hospitality", "Retail (Duka)", "Pharmacy (Dawa)"],
    features=[("phone", "M-Pesa at", "the till"), ("wifi_off", "Keeps selling", "offline"),
              ("box", "Live stock", "&amp; alerts"), ("chart", "Shift &amp; sales", "reports")],
    checks=["Plans from <b>KES 1,500/month</b>", "Receipt printing &amp; barcode scanning",
            "Multi-cashier &amp; multi-outlet", "Kitchen display &amp; table management"],
    url="pos.codevertexafrica.com", sign="Sell smarter, every day.",
)

ERP = dict(
    slug="erp-suite",
    title="Codevertex ERP Suite",
    h3size="70px",
    accent="#0EA5E9", accent_dark="#0369A1", accent_soft="#E0F2FE",
    product="ERP Suite", product_sub="People · Money · Operations",
    h1="DROWNING IN", h2="SPREADSHEETS &amp;", h3="PAPERWORK?",
    pains=["Payroll done by hand every month", "Leave &amp; attendance on paper",
           "Purchase approvals stuck in email", "Assets nobody can trace",
           "Reports that take days to compile"],
    before_title="Payroll_FINAL_v7.xlsx",
    before_lines=[("Basic pay — J. Otieno", "#REF!"), ("PAYE", "#VALUE!"), ("NSSF / SHIF", "?"),
                  ("Leave balance", "ask HR"), ("Approved LPOs", "see email")],
    before_total=("NET PAY", "#DIV/0!"),
    ribbon1="CODEVERTEX ERP", ribbon2="RUNS YOUR WHOLE BACK OFFICE!",
    lead="Run your organisation",
    body="HR, payroll, leave, procurement, assets, budgeting and reports, plus POS, inventory, payments and CRM,",
    lead2="all in one suite.",
    chips=["SMEs", "Corporates", "Institutions"],
    features=[("users", "HR &amp;", "payroll"), ("cart", "Procurement &amp;", "approvals"),
              ("building", "Assets &amp;", "budgeting"), ("pie", "BI &amp;", "reports")],
    checks=["Plans from <b>KES 10,000/month</b>", "Includes POS, inventory, payments &amp; CRM",
            "Role-based access &amp; approval workflows", "Built for African SMEs &amp; corporates"],
    url="erp.codevertexafrica.com", sign="One suite. Every department.",
)


def pos_screen():
    rows = [("Chapati x4", "120"), ("Beef stew", "350"), ("Soda 500ml x2", "160"), ("Tea", "50")]
    items = "".join(f'<div class="ln"><span>{a}</span><b>{b}</b></div>' for a, b in rows)
    tiles = "".join(f'<div class="tile"><i></i>{t}<small>KES {p}</small></div>' for t, p in
                    [("Chapati", 30), ("Pilau", 250), ("Beef stew", 350), ("Tea", 50), ("Soda", 80),
                     ("Mandazi", 20), ("Fries", 150), ("Juice", 120), ("Samosa", 40)])
    return f"""
    <div class="app">
      <div class="side"><div class="brand">POS</div>{''.join(f'<i class="{c}"></i>' for c in ['on','','','','',''])}</div>
      <div class="main">
        <div class="top"><b>New Sale</b><span>Till 2 · Shift A</span></div>
        <div class="tiles">{tiles}</div>
      </div>
      <div class="cart">
        <div class="ct">Order #00124</div>{items}
        <div class="tot"><span>TOTAL</span><b>KES 680</b></div>
        <div class="pay"><span class="mp">M-PESA</span><span class="cd">CASH</span></div>
      </div>
    </div>"""


def erp_screen():
    kpis = [("Employees", "142"), ("Payroll (Oct)", "KES 4.8M"), ("Open LPOs", "18"), ("Budget used", "62%")]
    k = "".join(f'<div class="kpi"><span>{a}</span><b>{b}</b></div>' for a, b in kpis)
    bars = "".join(f'<i style="height:{h}%"></i>' for h in [45, 60, 52, 70, 66, 82])
    return f"""
    <div class="app">
      <div class="side"><div class="brand">ERP</div>{''.join(f'<i class="{c}"></i>' for c in ['on','','','','',''])}</div>
      <div class="main wide">
        <div class="top"><b>Dashboard</b><span>FY 2026 · All departments</span></div>
        <div class="kpis">{k}</div>
        <div class="row2">
          <div class="panel"><div class="pt">Expenses vs budget</div><div class="bars">{bars}</div></div>
          <div class="panel"><div class="pt">Pending approvals</div>
            <div class="ap"><span>Leave · A. Wekesa</span><em>Approve</em></div>
            <div class="ap"><span>LPO-0381 · Stationery</span><em>Approve</em></div>
            <div class="ap"><span>Asset transfer · LT-22</span><em>Approve</em></div>
          </div>
        </div>
      </div>
    </div>"""


def phone(cfg):
    if cfg["slug"] == "pos-suite":
        return """<div class="ph"><div class="notch"></div>
          <div class="pc"><div class="ok">✓</div><b>M-PESA PAYMENT<br>RECEIVED</b>
          <div class="amt">KES 680</div><small>Ref QJK7H2XM4P</small>
          <div class="rcpt">Receipt sent</div></div></div>"""
    return """<div class="ph"><div class="notch"></div>
      <div class="pc"><div class="ok">✓</div><b>PAYSLIP READY</b>
      <div class="amt">October 2026</div><small>Leave balance: 14 days</small>
      <div class="rcpt">Self-service portal</div></div></div>"""


CSS = """
:root{--deep:#24071F;--plum:#4E1245;--brand:#A3376A;--soft:#FBF3F7;--ink:#1F0A1B;--body:#3B2A37;--acc:%(accent)s;--accd:%(accent_dark)s;--accs:%(accent_soft)s;--x:#E11D48}
*{box-sizing:border-box;margin:0;padding:0}
body{width:1080px;height:1600px;font-family:Montserrat,sans-serif;color:var(--ink);background:#fff;overflow:hidden}
.b{position:relative;width:1080px;height:1600px;overflow:hidden;background:#fff}
.ico{fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}

/* header */
.hd{position:absolute;left:0;top:0;width:100%;height:150px;display:flex;align-items:center;justify-content:space-between;padding:0 50px;background:#fff;border-bottom:1px solid #F0E3EA}
.hd img{height:96px}
.pl{text-align:right}
.pl .n{font-size:50px;font-weight:900;color:var(--deep);line-height:1;letter-spacing:-.5px}
.pl .n span{color:var(--acc)}
.pl .s{font-size:18px;font-weight:700;color:var(--brand);letter-spacing:.18em;margin-top:8px}

/* problem */
.pr{position:absolute;left:0;top:150px;width:100%;height:520px;background:linear-gradient(180deg,var(--soft),#fff)}
.h{position:absolute;left:50px;font-weight:900;line-height:1;letter-spacing:-1px;color:var(--deep)}
.h.a{top:190px;font-size:58px}.h.b{top:252px;font-size:58px}
.h.c{top:316px;font-size:%(h3size)s;color:var(--brand)}
.h.c u{text-decoration:none;padding:0 4px;background:linear-gradient(transparent 84%%,var(--acc) 84%%)}
.pains{position:absolute;left:50px;top:424px;list-style:none}
.pains li{display:flex;align-items:center;gap:16px;font-size:27px;font-weight:600;color:var(--ink);margin-bottom:13px}
.pains li i{flex:none;width:36px;height:36px;border-radius:50%%;background:var(--x);color:#fff;display:grid;place-items:center;font-style:normal;font-size:20px;font-weight:800}

.before{position:absolute;right:50px;top:200px;width:410px;background:#FFFDF5;border-radius:14px;box-shadow:0 18px 40px rgba(36,7,31,.18);transform:rotate(3deg);padding:22px 26px 20px;font-family:'Caveat',cursive;color:#334}
.before:before{content:"";position:absolute;inset:0;border-radius:14px;background:repeating-linear-gradient(transparent 0 37px,#D5E3F3 37px 38px);opacity:.8;pointer-events:none}
.before .tt{font-size:34px;font-weight:700;color:#1E3A8A;border-bottom:2px solid #F3B4B4;padding-bottom:4px;margin-bottom:6px}
.before .r{display:flex;justify-content:space-between;font-size:30px;line-height:38px}
.before .r b{color:#B91C1C;font-weight:700}
.before .t{display:flex;justify-content:space-between;font-size:32px;font-weight:700;margin-top:4px;border-top:2px solid #334;padding-top:2px}
.before .t b{color:#B91C1C}
.stamp{position:absolute;right:70px;top:540px;transform:rotate(-8deg);border:4px solid var(--x);color:var(--x);font-weight:900;font-size:26px;letter-spacing:.12em;padding:6px 16px;border-radius:10px;background:rgba(255,255,255,.85)}

/* ribbon */
.rb{position:absolute;left:-20px;top:722px;width:860px;height:146px;background:linear-gradient(100deg,var(--deep),var(--plum) 60%%,var(--brand));border-radius:0 90px 90px 0;transform:rotate(-2deg);transform-origin:left;box-shadow:0 18px 40px rgba(36,7,31,.3);color:#fff;padding:18px 0 0 70px}
.rb .r1{font-size:60px;font-weight:900;letter-spacing:-.5px;line-height:1}
.rb .r2{font-size:34px;font-weight:800;margin-top:10px;line-height:1}
.rb .r2:after{content:"";display:block;width:420px;height:6px;border-radius:3px;background:var(--acc);margin-top:12px}
.arrow{position:absolute;right:70px;top:660px;width:200px;height:150px}

/* demo */
.dm{position:absolute;left:50px;top:900px;width:400px}
.dm .l{font-size:32px;font-weight:800;color:var(--brand);line-height:1.15}
.dm p{font-size:24px;line-height:1.45;color:var(--body);margin-top:10px;font-weight:500}
.dm .l2{font-size:30px;font-weight:800;color:var(--accd);margin-top:6px}
.chips{display:flex;flex-wrap:wrap;gap:10px;margin-top:18px}
.chips span{font-size:17px;font-weight:700;color:var(--deep);background:var(--accs);border:2px solid var(--acc);padding:6px 14px;border-radius:30px}

.lap{position:absolute;left:470px;top:898px;width:540px}
.scr{background:#1A1220;border-radius:18px 18px 0 0;padding:12px;height:310px}
.base{height:22px;background:linear-gradient(#D9D3DC,#A9A1AD);border-radius:0 0 30px 30px;width:600px;margin-left:-30px}
.app{display:flex;height:100%%;background:#fff;border-radius:6px;overflow:hidden;font-size:11px}
.side{width:46px;background:var(--deep);padding:8px 0;display:flex;flex-direction:column;align-items:center;gap:12px}
.side .brand{color:#fff;font-weight:900;font-size:10px;background:var(--brand);border-radius:6px;padding:4px 5px}
.side i{width:20px;height:20px;border-radius:5px;background:rgba(255,255,255,.18)} .side i.on{background:var(--acc)}
.main{flex:1;padding:10px;background:#F8F5F8}
.top{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:8px}
.top b{font-size:15px;color:var(--deep)} .top span{color:#7A6B76;font-size:10px}
.tiles{display:grid;grid-template-columns:repeat(3,1fr);gap:7px}
.tile{background:#fff;border-radius:8px;padding:8px 6px;font-weight:700;color:var(--deep);box-shadow:0 1px 3px rgba(0,0,0,.08);font-size:11px}
.tile small{display:block;font-weight:600;color:var(--brand);font-size:10px;margin-top:2px}
.tile i{display:block;height:28px;border-radius:6px;background:linear-gradient(135deg,var(--accs),#F3E2EC);margin-bottom:5px}
.cart{width:170px;padding:10px;border-left:1px solid #EEE}
.ct{font-weight:800;color:var(--deep);font-size:12px;margin-bottom:6px}
.ln{display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px dashed #E6DDE3;color:#444}
.tot{display:flex;justify-content:space-between;margin:10px 0;font-size:13px;color:var(--deep)} .tot b{color:var(--brand)}
.pay{display:flex;gap:6px}.pay span{flex:1;text-align:center;padding:8px 0;border-radius:6px;font-weight:800;font-size:11px;color:#fff}
.mp{background:#16A34A}.cd{background:var(--plum)}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:7px}
.kpi{background:#fff;border-radius:8px;padding:8px;box-shadow:0 1px 3px rgba(0,0,0,.08)}
.kpi span{display:block;color:#7A6B76;font-size:9.5px}.kpi b{font-size:15px;color:var(--deep)}
.row2{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:8px}
.panel{background:#fff;border-radius:8px;padding:8px;box-shadow:0 1px 3px rgba(0,0,0,.08);height:172px}
.pt{font-weight:800;color:var(--deep);font-size:11px;margin-bottom:8px}
.bars{display:flex;align-items:flex-end;gap:10px;height:124px;border-bottom:1px solid #DDD;padding:0 6px}
.bars i{flex:1;background:linear-gradient(var(--acc),var(--accd));border-radius:4px 4px 0 0}
.ap{display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid #F0E8ED;color:#333;font-size:10.5px}
.ap em{font-style:normal;background:var(--brand);color:#fff;border-radius:4px;padding:3px 6px;font-weight:700;font-size:9.5px}

.ph{position:absolute;left:900px;top:960px;width:160px;height:285px;background:#111;border-radius:28px;padding:10px;box-shadow:0 18px 40px rgba(0,0,0,.3)}
.notch{position:absolute;left:55px;top:12px;width:50px;height:12px;border-radius:8px;background:#000;z-index:2}
.pc{height:100%%;background:#fff;border-radius:20px;text-align:center;padding:28px 8px 8px;color:var(--deep)}
.pc .ok{width:56px;height:56px;margin:0 auto 10px;border-radius:50%%;background:#16A34A;color:#fff;font-size:32px;line-height:56px;font-weight:900}
.pc b{font-size:14px;line-height:1.2}.pc .amt{font-size:22px;font-weight:900;color:var(--brand);margin:10px 0 4px}
.pc small{font-size:11px;color:#666}.pc .rcpt{margin-top:12px;background:var(--accs);border-radius:10px;padding:8px;font-size:12px;font-weight:700;color:var(--accd)}

/* features */
.ft{position:absolute;left:0;top:1262px;width:100%%;display:flex;justify-content:center;gap:0;padding:0 30px}
.f{width:255px;text-align:center;border-right:2px solid #EADCE4}
.f:last-child{border-right:none}
.f .c{width:84px;height:84px;margin:0 auto 10px;border-radius:50%%;background:var(--accs);color:var(--accd);display:grid;place-items:center;border:3px solid var(--acc)}
.f .c svg{width:44px;height:44px}
.f b{display:block;font-size:22px;font-weight:800;color:var(--deep);line-height:1.2}

/* cta */
.cta{position:absolute;left:30px;top:1420px;width:1020px;height:110px;border-radius:24px;background:var(--soft);border:2px solid #EAD3E0}
.cta .tr{position:absolute;left:0;top:0;width:470px;height:110px;border-radius:24px 60px 60px 24px;background:linear-gradient(100deg,var(--deep),var(--brand));color:#fff;display:flex;align-items:center;gap:18px;padding-left:28px}
.cta .tr svg{width:58px;height:58px;color:var(--acc)}
.cta .tr div{font-size:30px;font-weight:600;line-height:1.1}
.cta .tr b{color:var(--acc);font-weight:900;font-size:36px}
.cta ul{position:absolute;left:500px;top:10px;list-style:none}
.cta li{font-size:18.5px;font-weight:600;color:var(--ink);line-height:22.5px}
.cta li:before{content:"✓";color:#16A34A;font-weight:900;margin-right:10px}

/* footer */
.fo{position:absolute;left:0;bottom:0;width:100%%;height:62px;background:var(--deep);color:#fff;display:flex;align-items:center;justify-content:space-between;padding:0 40px;font-size:19px;font-weight:600}
.fo span{display:flex;align-items:center;gap:10px}.fo svg{width:24px;height:24px;color:var(--acc)}
"""


def css(cfg):
    out = CSS.replace("%%", "%")
    for k in ("accent", "accent_dark", "accent_soft", "h3size"):
        out = out.replace(f"%({k})s", cfg[k])
    return out


def build(cfg):
    pains = "".join(f"<li><i>✕</i>{p}</li>" for p in cfg["pains"])
    lines = "".join(f'<div class="r"><span>{a}</span><b>{b}</b></div>' for a, b in cfg["before_lines"])
    feats = "".join(f'<div class="f"><div class="c">{icon(i)}</div><b>{a}<br>{b}</b></div>' for i, a, b in cfg["features"])
    checks = "".join(f"<li>{c}</li>" for c in cfg["checks"])
    chips = "".join(f"<span>{c}</span>" for c in cfg["chips"])
    screen = pos_screen() if cfg["slug"] == "pos-suite" else erp_screen()
    name, rest = cfg["product"].split(" ", 1)
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>{cfg['title']}</title>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800;900&family=Caveat:wght@500;700&family=Great+Vibes&display=swap" rel="stylesheet">
<style>{css(cfg)}</style></head>
<body><div class="b">
  <div class="hd"><img src="assets/codevertex-logo.png" alt="Codevertex Africa Limited">
    <div class="pl"><div class="n">{name} <span>{rest}</span></div><div class="s">{cfg['product_sub'].upper()}</div></div></div>
  <div class="pr"></div>
  <div class="h a">{cfg['h1']}</div><div class="h b">{cfg['h2']}</div><div class="h c"><u>{cfg['h3']}</u></div>
  <ul class="pains">{pains}</ul>
  <div class="before"><div class="tt">{cfg['before_title']}</div>{lines}
    <div class="t"><span>{cfg['before_total'][0]}</span><b>{cfg['before_total'][1]}</b></div></div>
  <div class="stamp">SOUND FAMILIAR?</div>
  <div class="rb"><div class="r1">{cfg['ribbon1']}</div><div class="r2">{cfg['ribbon2']}</div></div>
  <div class="dm"><div class="l">{cfg['lead']}</div><p>{cfg['body']}</p><div class="l2">{cfg['lead2']}</div>
    <div class="chips">{chips}</div></div>
  <div class="lap"><div class="scr">{screen}</div><div class="base"></div></div>
  {phone(cfg)}
  <div class="ft">{feats}</div>
  <div class="cta"><div class="tr">{icon('cal')}<div>Try it <b>FREE</b><br>for <b>14 days!</b></div></div><ul>{checks}</ul></div>
  <div class="fo"><span>{icon('globe')}{cfg['url']}</span><span>{icon('call')}+254 742 201 368</span><span>{icon('mail')}info@codevertexafrica.com</span></div>
</div></body></html>"""
    (HERE / f"{cfg['slug']}.html").write_text(html)


if __name__ == "__main__":
    for c in (POS, ERP):
        build(c)
