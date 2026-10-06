"""Assembles the Hadia SRDD HTML from the content files and the SVG figures."""
import base64
import re
import sys
from pathlib import Path

import figures as F

here = Path(__file__).parent
logo = "data:image/png;base64," + base64.b64encode((here / "logo.png").read_bytes()).decode()

body = "".join((here / f"content_{p}.html").read_text() for p in "abcd")
figs = {
    "FIG_ARCH": F.fig_architecture(), "FIG_MONEY": F.fig_money(), "FIG_STATES": F.fig_pot_states(),
    "FIG_PAYOUT": F.fig_payout(), "FIG_SWEEP": F.fig_sweep(), "FIG_TENANT": F.fig_tenant_onboarding(),
    "FIG_OWNER": F.fig_owner_onboarding(), "FIG_LISTING": F.fig_listing(), "FIG_RESERVE": F.fig_reservation(),
    "FIG_CONTRIB": F.fig_contribution(), "FIG_REFUND": F.fig_refund(), "FIG_ERD": F.fig_erd(),
    "FIG_GANTT": F.fig_gantt(), "FIG_WIRE": F.fig_wireframes(), "LOGO": logo,
}
for k, v in figs.items():
    body = body.replace("{" + k + "}", v)
assert "{FIG_" not in body, re.findall(r"\{FIG_\w+\}", body)
# Figure numbers come from a CSS counter so figures can move freely.
body = re.sub(r"<figcaption>Figure \d+\. ", "<figcaption>", body)

css = (here / "style.css").read_text()
html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Hadia Gifting Registry SRDD</title>
<meta name="author" content="Codevertex Africa Limited">
<style>{css}</style></head><body>{body}</body></html>"""

# House style: no em dashes, section signs or arrow characters in prose.
for bad in ["—", "§", "→", "“", "”", "’"]:
    if bad in html:
        sys.exit(f"forbidden character {bad!r} found")
(here / "hadia-srdd.html").write_text(html)
print("ok", len(html))
