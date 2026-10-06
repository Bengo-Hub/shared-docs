"""Builds the Shaba Village estate platform SRDD PDF.

Pass 1 renders the body with placeholder page numbers in the contents. The PDF outline gives the
page of every heading; pass 2 renders again with the real numbers. The cover is rendered on its own
(full bleed, no header or footer) and placed in front of the body, so page 1 is the first body page.
"""
import base64
import os
import re
import subprocess
import sys
from html import escape
from pathlib import Path

import pikepdf

import figures as F

here = Path(__file__).parent
OUT = here.parent / "Lintel-SRDD-Shaba-Village-Codevertex.pdf"
logo_uri = "data:image/png;base64," + base64.b64encode((here / "logo.png").read_bytes()).decode()

FORBIDDEN = ["—", "§", "→", "“", "”", "’"]


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def assemble():
    body = "".join((here / f"content_{p}.html").read_text() for p in ("a", "b", "c", "d", "hosting", "e"))
    figs = {
        "FIG_ARCH": F.fig_architecture(), "FIG_FUNDS": F.fig_funds(), "FIG_SALE": F.fig_sale_states(),
        "FIG_BILLING": F.fig_billing(), "FIG_WATER": F.fig_water(), "FIG_PAYMENT": F.fig_payment(),
        "FIG_WORKORDER": F.fig_workorder(), "FIG_VENDOR": F.fig_vendor(), "FIG_GATE": F.fig_gate(),
        "FIG_ONBOARD": F.fig_onboarding(), "FIG_ERD": F.fig_erd(), "FIG_GANTT": F.fig_gantt(),
        "FIG_WIRE": F.fig_wireframes(), "FIG_OWNERSHIP": F.fig_ownership(),
        "FIG_TENANCY": F.fig_tenancy(), "FIG_RELEASES": F.fig_releases(), "FIG_LEASE": F.fig_lease(), "FIG_LISTING": F.fig_listing(),
    }
    for k, v in figs.items():
        body = body.replace("{" + k + "}", v)
    assert "{FIG_" not in body

    # Number figures in order.
    n = 0

    def fig(m):
        nonlocal n
        n += 1
        return f'<figcaption><b>Figure {n}.</b> '
    body = re.sub(r"<figcaption>(?:Figure \d+\. )?", fig, body)

    # Number chapters and subsections, give every heading an id, collect the contents.
    toc, chap, sub, chap_id = [], 0, 0, ""
    out, pos = [], 0
    for m in re.finditer(r'<section(?: id="([^"]+)")?([^>]*)>|<h([23])([^>]*)>(.*?)</h\3>', body, re.S):
        out.append(body[pos:m.start()])
        pos = m.end()
        if m.group(0).startswith("<section"):
            out.append(m.group(0))
            chap_id = m.group(1) or ""
            continue
        level, attrs, title = m.group(3), m.group(4), m.group(5).strip()
        if level == "2":
            nonum = "nonum" in attrs
            if not nonum:
                chap += 1
                sub = 0
            hid = chap_id or slug(title)
            chap_id = hid
            label = "" if nonum else str(chap)
            if title != "Document control":
                toc.append((2, label, title, hid))
            num = "" if nonum else f'<span class="hnum">{label}</span>'
            out.append(f'<h2 id="h-{hid}"{attrs}>{num}<span class="htxt">{title}</span></h2>')
        else:
            idm = re.search(r'id="([^"]+)"', attrs)
            if chap and "nonum" not in attrs:
                sub += 1
                label = f"{chap}.{sub}"
            else:
                label = ""
            hid = idm.group(1) if idm else f"{chap_id}-{slug(title)}"
            attrs = re.sub(r'\s*id="[^"]+"', "", attrs)
            if label:
                toc.append((3, label, title, hid))
            num = f'<span class="hnum">{label}</span>' if label else ""
            out.append(f'<h3 id="h-{hid}"{attrs}>{num}{title}</h3>')
    out.append(body[pos:])
    body = "".join(out)
    # Links written as #id point at the heading anchors.
    body = re.sub(r'href="#([a-z0-9-]+)"', lambda m: f'href="#h-{m.group(1)}"', body)
    return body, toc


def toc_html(toc, pages):
    rows = []
    for level, label, title, hid in toc:
        pg = pages.get(hid, "")
        rows.append(
            f'<a class="toc-l{level}" href="#h-{hid}"><span class="toc-n">{label}</span>'
            f'<span class="toc-t">{escape(title, quote=False)}</span><span class="toc-d"></span>'
            f'<span class="toc-p">{pg}</span></a>')
    return '<h2 class="nonum toc-h"><span class="htxt">Contents</span></h2><nav class="toc">' + "".join(rows) + "</nav>"


def page_html(body, css):
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Lintel SRDD</title>'
            f'<style>{css}</style></head><body>{body}</body></html>')


def render(html_name, pdf_name, chrome):
    subprocess.run(["node", str(here / "render.js"), str(here), html_name, pdf_name, chrome],
                   check=True, env={**os.environ, "NODE_PATH": subprocess.check_output(["npm", "root", "-g"]).decode().strip()})


def outline_pages(pdf_path, toc):
    """Maps heading ids to body page numbers from the PDF outline. Chromium may repeat a heading's
    number or text in the outline title, so a title matches when it ends with the heading text and
    what precedes it is empty, the number, the number twice, or the text again."""
    items = []
    with pikepdf.open(pdf_path) as pdf:
        index = {p.objgen: i + 1 for i, p in enumerate(pdf.pages)}
        with pdf.open_outline() as ol:
            stack = list(ol.root)
            while stack:
                it = stack.pop(0)
                stack.extend(it.children)
                dest = it.destination
                if isinstance(dest, pikepdf.Array) and len(dest):
                    items.append((re.sub(r"\s+", " ", it.title.strip()), index.get(dest[0].objgen, "")))
    pages = {}
    for level, label, title, hid in toc:
        for t, pg in items:
            if t.endswith(title) and t[: len(t) - len(title)].strip() in ("", label, label + label, title):
                pages[hid] = pg
                break
    return pages


def main():
    css = (here / "style.css").read_text().replace("FONTDIR", (here / "fonts").as_uri())
    body, toc = assemble()
    for bad in FORBIDDEN:
        if bad in body:
            sys.exit(f"forbidden character {bad!r}")

    # Pass 1 with placeholder numbers of the same width.
    (here / "body.html").write_text(page_html(body.replace("{TOC}", toc_html(toc, {h: "00" for *_, h in toc})), css))
    render("body.html", "body.pdf", "body")
    pages = outline_pages(here / "body.pdf", toc)
    missing = [t for _, _, t, h in toc if h not in pages]
    if missing:
        print("no page found for:", missing)
    # Pass 2 with real numbers.
    (here / "body.html").write_text(page_html(body.replace("{TOC}", toc_html(toc, pages)), css))
    render("body.html", "body.pdf", "body")
    if outline_pages(here / "body.pdf", toc) != pages:
        print("warning: page numbers moved between passes")

    cover_css = (here / "cover.css").read_text().replace("FONTDIR", (here / "fonts").as_uri())
    cover = (here / "cover.html").read_text().replace("{LOGO}", logo_uri)
    (here / "cover_page.html").write_text(page_html(cover, cover_css))
    render("cover_page.html", "cover.pdf", "cover")

    with pikepdf.open(here / "body.pdf") as pdf, pikepdf.open(here / "cover.pdf") as cov:
        pdf.pages.insert(0, cov.pages[0])
        pdf.docinfo["/Title"] = "Lintel by Codevertex: SRDD and Shaba Village Launch Proposal"
        pdf.docinfo["/Author"] = "Codevertex Africa Limited"
        pdf.docinfo["/Subject"] = "Multi-tenant property management and real estate marketplace platform"
        pdf.Root.PageMode = pikepdf.Name.UseOutlines
        pdf.remove_unreferenced_resources()
        pdf.save(OUT, compress_streams=True, recompress_flate=True,
                 object_stream_mode=pikepdf.ObjectStreamMode.generate)
    print("ok", OUT.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
