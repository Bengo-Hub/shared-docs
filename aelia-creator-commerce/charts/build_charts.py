#!/usr/bin/env python3
"""Regenerate the SRDD's inline-SVG charts.

    python3 charts/build_charts.py

Writes scope.svg, team.svg and payout-waterfall.svg next to this script. build/build-pdf.cjs
injects them wherever the SRDD markdown has <!-- chart:NAME -->.

scope.svg is computed from the SRDD itself: every requirement row `| ABC-nn | ... [MVP|v1|Later]`
is counted by module and release. The totals are printed so the prose figures in §7.2 can be
kept in step after edits.

Palette validated with the dataviz skill's validator against the cream page (#faf6ee):
releases  MVP #9a4a9a · v1 #12805f · Later #b5651d  (adjacent CVD ΔE 7.5, so every segment is
          direct-labelled and a legend is shown)
people    #2f7fb8 · #b5651d · #7a5aa6               (all checks pass)
"""
import collections
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SRDD = os.path.join(HERE, '..', 'AELIA-Creator-Commerce-System-Requirements-and-Design.md')

INK, MUT, GRID, PLUMD = '#2c2530', '#7c6f7c', '#e3d6cf', '#3f1a3f'


def write(name, parts):
    with open(os.path.join(HERE, f'{name}.svg'), 'w') as f:
        f.write(''.join(parts))
    print(f'wrote charts/{name}.svg')


def legend(o, x, items, y=8, step=70):
    for colour, label in items:
        o.append(f'<rect x="{x}" y="{y}" width="12" height="12" rx="3" fill="{colour}"/>'
                 f'<text x="{x+17}" y="{y+10}" font-size="11" fill="{INK}">{label}</text>')
        x += step


# ── 1. requirements per module by release (computed from the SRDD) ─────────────
MODULES = [('REG', 'Registration & Verification'), ('CPP', 'Creator Passport'), ('BPP', 'Brand Passport'),
           ('DIS', 'Creator Discovery'), ('MAT', 'AELIA Match'), ('CMP', 'Campaign Creation & Composer'),
           ('WSP', 'Campaign Workspace'), ('CNT', 'Content & Approval'), ('AGR', 'Contracts & Rights'),
           ('COM', 'Communication'), ('PAY', 'Payments'), ('TAX', 'Tax & Compliance'),
           ('PRF', 'Performance Tracking'), ('REP', 'Reputation'), ('RBK', 'Rebooking'), ('RPT', 'Reporting'),
           ('ADM', 'Administration'), ('AIC', 'AI Content Lane'), ('INT', 'Integrations Hub')]
FUTURE = {'MOB', 'AFF', 'GEO', 'AUT', 'AIX'}  # §4.20 future platform modules, shown as one row
RELEASES = ['MVP', 'v1', 'Later']


def scope_chart():
    src = open(SRDD, encoding='utf8').read()
    counts = collections.defaultdict(collections.Counter)
    for m in re.finditer(r'^\| ([A-Z]{3})-\d+ \|[^\n]*?\[(MVP|v1|Later)\]', src, re.M):
        if m.group(1) == 'NFR':  # non-functional requirements are not part of the functional scope chart
            continue
        key = 'FUT' if m.group(1) in FUTURE else m.group(1)
        counts[key][m.group(2)] += 1
    known = {k for k, _ in MODULES} | {'FUT'}
    unknown = set(counts) - known
    if unknown:
        raise SystemExit(f'unmapped requirement prefixes {sorted(unknown)}: add them to MODULES or FUTURE')
    rows = [(name, *[counts[k][r] for r in RELEASES]) for k, name in MODULES]
    rows.append(('Future modules', *[counts['FUT'][r] for r in RELEASES]))

    colours = ['#9a4a9a', '#12805f', '#b5651d']
    widest = max(sum(r[1:]) for r in rows)
    ticks = (widest + 1) // 2 * 2
    L, U, H, G, top = 190, 34, 17, 7, 34
    W, Ht = L + ticks * U + 60, top + len(rows) * (H + G) + 30
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {Ht}" width="{W}" role="img" '
         f'aria-label="Requirements per module by release">']
    legend(o, L, zip(colours, RELEASES))
    for v in range(0, ticks + 1, 2):
        gx = L + v * U
        o.append(f'<line x1="{gx}" y1="{top-4}" x2="{gx}" y2="{Ht-24}" stroke="{GRID}" stroke-width="1"/>'
                 f'<text x="{gx}" y="{Ht-10}" font-size="10" fill="{MUT}" text-anchor="middle">{v}</text>')
    for i, (name, *vals) in enumerate(rows):
        y = top + i * (H + G)
        o.append(f'<text x="{L-8}" y="{y+12.5}" font-size="10.5" fill="{INK}" text-anchor="end">{name.replace("&", "&amp;")}</text>')
        x = L
        for colour, v in zip(colours, vals):
            if not v:
                continue
            w = v * U - 2  # 2px surface gap between segments
            o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{H}" rx="3" fill="{colour}"/>'
                     f'<text x="{x+w/2}" y="{y+12.5}" font-size="10" font-weight="700" fill="#fff" text-anchor="middle">{v}</text>')
            x += v * U
        o.append(f'<text x="{x+6}" y="{y+12.5}" font-size="10" fill="{MUT}">{sum(vals)}</text>')
    o.append('</svg>')
    write('scope', o)

    totals = [sum(r[i] for r in rows) for i in (1, 2, 3)]
    total = sum(totals)
    print(f'requirements: {total} total · MVP {totals[0]} · v1 {totals[1]} · Later {totals[2]} '
          f'· in 6-month plan {totals[0]+totals[1]} ({round((totals[0]+totals[1])*100/total)}%)')
    print('  -> keep §7.2 (Figure 5 caption and the four KPI tiles) and the README in step with these numbers')


# ── 2. planned team days per phase (Part B §10.2) ──────────────────────────────
PHASES = [('D Design', 10, 0, 0), ('P0 Setup', 9, 4, 8), ('P1 Core', 3, 15, 15), ('P2 Campaigns', 1, 12, 15),
          ('P3 Payments', 21, 16, 13), ('P4 Intelligence', 22, 34, 33), ('P5 Hardening', 20, 20, 16)]
PEOPLE = ['Titus Owuor, technical lead', 'Steve Oginga, backend', 'Meshack Isava, frontend']


def team_chart():
    colours = ['#2f7fb8', '#b5651d', '#7a5aa6']
    W, base, sc, bw = 640, 280, 2.2, 52
    gap = (W - 60 - len(PHASES) * bw) / len(PHASES)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} 330" width="{W}" role="img" '
         f'aria-label="Planned team days per phase">']
    legend(o, 50, zip(colours, PEOPLE), step=190)
    for v in range(0, 101, 20):
        y = base - v * sc
        o.append(f'<line x1="44" y1="{y}" x2="{W-6}" y2="{y}" stroke="{GRID}"/>'
                 f'<text x="38" y="{y+4}" font-size="10" fill="{MUT}" text-anchor="end">{v}</text>')
    for i, (name, *vals) in enumerate(PHASES):
        x, y = 50 + gap / 2 + i * (bw + gap), base
        for colour, v in zip(colours, vals):
            if not v:
                continue
            h = v * sc
            o.append(f'<rect x="{x}" y="{y-h+1}" width="{bw}" height="{h-2}" rx="3" fill="{colour}"/>')
            if h > 14:
                o.append(f'<text x="{x+bw/2}" y="{y-h/2+4}" font-size="10" font-weight="700" fill="#fff" text-anchor="middle">{v}</text>')
            y -= h
        code, label = name.split(' ', 1)
        o.append(f'<text x="{x+bw/2}" y="{y-6}" font-size="10.5" font-weight="700" fill="{PLUMD}" text-anchor="middle">{sum(vals)}</text>'
                 f'<text x="{x+bw/2}" y="{base+16}" font-size="10" fill="{INK}" text-anchor="middle">{code}</text>'
                 f'<text x="{x+bw/2}" y="{base+29}" font-size="9" fill="{MUT}" text-anchor="middle">{label}</text>')
    o.append(f'<text x="12" y="100" font-size="10" fill="{MUT}" transform="rotate(-90 12 100)">team days</text></svg>')
    write('team', o)
    print('team days: ' + ' · '.join(f'{p.split(",")[0]} {sum(r[i+1] for r in PHASES)}' for i, p in enumerate(PEOPLE)))


# ── 3. payout test vector waterfall (Part J §33.4) ─────────────────────────────
GROSS, COMMISSION_RATE, WHT_RATE = 20000, 0.08, 0.05


def waterfall_chart():
    commission, wht = round(GROSS * COMMISSION_RATE), round(GROSS * WHT_RATE)
    net = GROSS - commission - wht
    steps = [('Creator fee (gross)', GROSS, 'total'),
             (f'Platform commission {COMMISSION_RATE:.0%}', -commission, 'ded'),
             (f'Withholding {WHT_RATE:.0%} of gross', -wht, 'ded'),
             ('Net paid to creator', net, 'total')]
    colour = {'total': '#9a4a9a', 'ded': '#b5651d'}
    W, H, base, top = 640, 300, 250, 40
    sc, bw = (base - top) / GROSS, 96
    gap = (W - 80 - 4 * bw) / 4
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" role="img" '
         f'aria-label="Payout calculation waterfall">']
    for v in range(0, GROSS + 1, 5000):
        y = base - v * sc
        o.append(f'<line x1="60" y1="{y}" x2="{W-10}" y2="{y}" stroke="{GRID}"/>'
                 f'<text x="54" y="{y+4}" font-size="10" fill="{MUT}" text-anchor="end">{v:,}</text>')
    run = 0
    for i, (name, v, kind) in enumerate(steps):
        x = 70 + gap / 2 + i * (bw + gap)
        if kind == 'total':
            y0, y1, run = 0, v, v
        else:
            y0, y1 = run + v, run
            run += v
        ytop, h = base - y1 * sc, (y1 - y0) * sc
        label = f'KES {abs(v):,}' if kind == 'total' else f'−KES {abs(v):,}'
        words = name.split(' ')
        o.append(f'<rect x="{x}" y="{ytop+1}" width="{bw}" height="{max(h-2, 2)}" rx="4" fill="{colour[kind]}"/>'
                 f'<text x="{x+bw/2}" y="{ytop-6}" font-size="11" font-weight="700" fill="{PLUMD}" text-anchor="middle">{label}</text>'
                 f'<text x="{x+bw/2}" y="{base+16}" font-size="10" fill="{INK}" text-anchor="middle">{" ".join(words[:2])}</text>'
                 f'<text x="{x+bw/2}" y="{base+29}" font-size="10" fill="{INK}" text-anchor="middle">{" ".join(words[2:])}</text>')
        if i < len(steps) - 1:
            yy = base - run * sc
            o.append(f'<line x1="{x+bw}" y1="{yy}" x2="{x+bw+gap}" y2="{yy}" stroke="{MUT}" stroke-dasharray="3 3"/>')
    legend(o, 70, [(colour['total'], 'Amount'), (colour['ded'], 'Deduction')], step=80)
    o.append('</svg>')
    write('payout-waterfall', o)
    print(f'payout vector: gross {GROSS:,} - commission {commission:,} - WHT {wht:,} = net {net:,}')


if __name__ == '__main__':
    scope_chart()
    team_chart()
    waterfall_chart()
