"""SVG helpers for the Hadia SRDD diagrams. Every diagram is plain inline SVG so the PDF stays
vector, sharp and small."""

from html import escape

BRAND = "#6E1A5A"
BRAND_SOFT = "#F6EEF4"
GOLD = "#B8862B"
GOLD_SOFT = "#FBF2E2"
MAROON = "#8E2B2B"
INK = "#1F2430"
MUTED = "#5B6270"
LINE = "#C9CDD6"
GREEN = "#2F7D5B"
GREEN_SOFT = "#E6F3EC"
BLUE = "#2D5B9A"
BLUE_SOFT = "#E8EFF8"
GREY_SOFT = "#F3F4F7"

KINDS = {
    "new": (BRAND_SOFT, BRAND),
    "reuse": (GREEN_SOFT, GREEN),
    "ext": (GOLD_SOFT, GOLD),
    "user": (BLUE_SOFT, BLUE),
    "plain": ("#FFFFFF", LINE),
    "grey": (GREY_SOFT, LINE),
    "warn": ("#FBEAEA", MAROON),
}


def svg(w, h, body, title=""):
    t = f"<title>{escape(title)}</title>" if title else ""
    return (
        f'<svg viewBox="0 0 {w} {h}" width="100%" xmlns="http://www.w3.org/2000/svg" role="img" '
        f'font-family="Heros, Helvetica, Arial, sans-serif">{t}'
        '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
        f'orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="{MUTED}"/></marker>'
        '<marker id="ahb" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
        f'orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="{BRAND}"/></marker></defs>'
        f"{body}</svg>"
    )


def text(x, y, s, size=11, weight=400, fill=INK, anchor="middle", italic=False):
    st = ' font-style="italic"' if italic else ""
    return (
        f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
        f'text-anchor="{anchor}"{st}>{escape(s)}</text>'
    )


def box(x, y, w, h, lines, kind="plain", size=11, rx=8, bold_first=True, dashed=False):
    fill, stroke = KINDS[kind]
    da = ' stroke-dasharray="5 4"' if dashed else ""
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.3"{da}/>']
    if isinstance(lines, str):
        lines = [lines]
    lh = size + 4
    start = y + h / 2 - (len(lines) - 1) * lh / 2 + size / 3
    for i, ln in enumerate(lines):
        wgt = 600 if (i == 0 and bold_first) else 400
        col = INK if i == 0 else MUTED
        sz = size if i == 0 else size - 1
        out.append(text(x + w / 2, start + i * lh, ln, sz, wgt, col))
    return "".join(out)


def diamond(cx, cy, w, h, lines, size=10.5):
    pts = f"{cx},{cy-h/2} {cx+w/2},{cy} {cx},{cy+h/2} {cx-w/2},{cy}"
    out = [f'<polygon points="{pts}" fill="{GOLD_SOFT}" stroke="{GOLD}" stroke-width="1.3"/>']
    if isinstance(lines, str):
        lines = [lines]
    lh = size + 3
    start = cy - (len(lines) - 1) * lh / 2 + size / 3
    for i, ln in enumerate(lines):
        out.append(text(cx, start + i * lh, ln, size, 600 if i == 0 else 400))
    return "".join(out)


def pill(x, y, w, h, s, kind="user", size=11):
    fill, stroke = KINDS[kind]
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2}" fill="{fill}" stroke="{stroke}" stroke-width="1.3"/>'
            + text(x + w / 2, y + h / 2 + size / 3, s, size, 600))


def arrow(pts, label="", color=MUTED, dashed=False, lx=None, ly=None, lsize=9.5, anchor="middle"):
    d = "M" + " L".join(f"{x},{y}" for x, y in pts)
    da = ' stroke-dasharray="5 4"' if dashed else ""
    mk = "ahb" if color == BRAND else "ah"
    out = f'<path d="{d}" fill="none" stroke="{color}" stroke-width="1.3"{da} marker-end="url(#{mk})"/>'
    if label:
        if lx is None:
            (x1, y1), (x2, y2) = pts[0], pts[1]
            lx, ly = (x1 + x2) / 2, (y1 + y2) / 2 - 5
        out += label_bg(lx, ly, label, lsize, anchor)
    return out


def label_bg(x, y, s, size=9.5, anchor="middle"):
    w = len(s) * size * 0.53 + 8
    bx = x - w / 2 if anchor == "middle" else (x - 4 if anchor == "start" else x - w + 4)
    return (f'<rect x="{bx}" y="{y - size}" width="{w}" height="{size + 5}" rx="3" fill="#FFFFFF" opacity="0.92"/>'
            + text(x, y, s, size, 500, MUTED, anchor))


def lane(x, y, w, h, title, fill=GREY_SOFT):
    out = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="{LINE}" stroke-dasharray="4 4"/>'
    return out + (lane_title(x, y, title) if title else "")


def lane_title(x, y, title, size=8.5):
    t = title.upper()
    w = len(t) * size * 0.68 + 12
    return (f'<rect x="{x + 6}" y="{y + 6}" width="{w}" height="{size + 7}" rx="3" fill="#FFFFFF"/>'
            + text(x + 12, y + 6 + size + 2, t, size, 700, MUTED, "start"))


def legend(x, y, items):
    out = []
    cx = x
    for kind, label in items:
        fill, stroke = KINDS[kind]
        out.append(f'<rect x="{cx}" y="{y}" width="14" height="10" rx="2" fill="{fill}" stroke="{stroke}"/>')
        out.append(text(cx + 19, y + 9, label, 9.5, 500, MUTED, "start"))
        cx += 26 + len(label) * 5.4
    return "".join(out)


def sequence(actors, msgs, width=760, gap=None, top=20, row=30, title=""):
    """actors: list of (key, label, kind). msgs: list of (from, to, label, style) where style is
    'call', 'reply', 'self' or 'note'."""
    n = len(actors)
    gap = gap or (width - 40) / n
    xs = {k: 20 + gap * i + gap / 2 for i, (k, _, _) in enumerate(actors)}
    h = top + 50 + row * len(msgs) + 30
    out = []
    for k, lab, kind in actors:
        x = xs[k]
        out.append(f'<line x1="{x}" y1="{top+38}" x2="{x}" y2="{h-12}" stroke="{LINE}" stroke-dasharray="4 4"/>')
        bw = min(gap - 10, 130)
        out.append(box(x - bw / 2, top, bw, 36, lab.split("|"), kind, 10.5))
    y = top + 62
    for i, m in enumerate(msgs):
        f, t_, label, style = m
        if style == "note":
            x1, x2 = xs[f], xs[t_]
            lo, hi = min(x1, x2) - 50, max(x1, x2) + 50
            out.append(f'<rect x="{lo}" y="{y-13}" width="{hi-lo}" height="20" rx="4" fill="{GOLD_SOFT}" stroke="{GOLD}"/>')
            out.append(text((lo + hi) / 2, y + 1, label, 9.5, 500, INK))
        elif style == "self":
            x = xs[f]
            out.append(f'<path d="M{x},{y-8} h28 v14 h-26" fill="none" stroke="{MUTED}" stroke-width="1.2" marker-end="url(#ah)"/>')
            out.append(text(x + 34, y + 2, label, 9.5, 500, MUTED, "start"))
        else:
            x1, x2 = xs[f], xs[t_]
            dashed = style == "reply"
            col = MUTED if dashed else BRAND
            out.append(arrow([(x1, y), (x2 - (6 if x2 > x1 else -6), y)], color=col, dashed=dashed))
            out.append(label_bg((x1 + x2) / 2, y - 5, f"{i+1}. {label}", 9.3))
        y += row
    return svg(width, h, "".join(out), title)


def gantt(rows, weeks=12, width=760, title="", milestones=()):
    """rows: list of (label, start_week, end_week, kind, group_header?)"""
    left, top, rh = 250, 34, 21
    cw = (width - left - 10) / weeks
    h = top + rh * len(rows) + 30
    out = []
    for wk in range(weeks):
        x = left + wk * cw
        out.append(f'<rect x="{x}" y="{top-24}" width="{cw}" height="20" fill="{BRAND if wk % 2 == 0 else "#8E3A77"}"/>')
        out.append(text(x + cw / 2, top - 10, f"W{wk+1}", 9.5, 600, "#FFFFFF"))
        out.append(f'<line x1="{x}" y1="{top}" x2="{x}" y2="{h-24}" stroke="#E6E8EE"/>')
    for i, r in enumerate(rows):
        label, s, e, kind = r[:4]
        y = top + i * rh
        header = len(r) > 4 and r[4]
        if header:
            out.append(f'<rect x="0" y="{y+2}" width="{width-10}" height="{rh-3}" fill="{GREY_SOFT}"/>')
            out.append(text(6, y + 15, label, 10, 700, INK, "start"))
            continue
        out.append(text(12, y + 15, label, 9.8, 400, INK, "start"))
        fill, stroke = KINDS[kind]
        out.append(f'<rect x="{left + (s-1)*cw + 2}" y="{y+4}" width="{(e-s+1)*cw - 4}" height="{rh-8}" rx="4" fill="{stroke}" opacity="0.85"/>')
    for m in milestones:
        wk, lab = m[0], m[1]
        x = left + wk * cw
        anchor = m[2] if len(m) > 2 else ("end" if wk >= weeks else ("start" if wk <= 0.5 else "middle"))
        out.append(f'<path d="M{x},{h-24} l5,7 l-5,7 l-5,-7z" fill="{GOLD}"/>')
        out.append(text(x, h + 2, lab, 8.8, 700, INK, anchor))
    return svg(width, h + 10, "".join(out), title)
