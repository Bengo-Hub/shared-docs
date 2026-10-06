"""Builds the Maskani brand assets: mark, favicon, logos and PNG exports.

The mark is a house inside the Codevertex ring. Its right roof slope and the rising tail form the
Codevertex check, which breaks out of the ring at the top right as it does in the parent logo. The
ring is the enclosed home compound, and the gold doorway is the way in. Wordmarks are
set in TeX Gyre Adventor and converted to outlines, so the SVGs need no font at render time.

Run: python3 build_brand.py   (PNG export needs Node with Playwright)
"""
import os
import subprocess
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

HERE = Path(__file__).parent
OUT = HERE / "assets"
FONTS = Path("/usr/share/texmf/fonts/opentype/public/tex-gyre")

PLUM = "#6E1A5A"
PLUM_DARK = "#4E1240"
GOLD = "#C8963E"
GREY = "#6A6E78"
WHITE = "#FFFFFF"


def text_path(s, font_file, size, x, y, tracking=0.0):
    """Returns an SVG path for s with its baseline at (x, y), and the advance width."""
    font = TTFont(FONTS / font_file)
    gs = font.getGlyphSet()
    cmap = font.getBestCmap()
    scale = size / font["head"].unitsPerEm
    pen = SVGPathPen(gs)
    cx = 0.0
    for ch in s:
        name = cmap[ord(ch)]
        tp = TransformPen(pen, (scale, 0, 0, -scale, x + cx, y))
        gs[name].draw(tp)
        cx += gs[name].width * scale + tracking * size
    return pen.getCommands(), cx - tracking * size


def mark(ring=PLUM, stroke=PLUM, door=GOLD, sw=9):
    """The Maskani mark in a 120 by 120 box: a house in the Codevertex ring."""
    # Ring of radius 47 around (60, 62), open at the top right where the tail leaves it.
    ring_path = "M 102.6 42.1 A 47 47 0 1 1 77.6 18.4"
    # House: left eave, roof peak, right roof down to the right wall, walls and floor.
    house = "M 23 61 L 45 37 L 66 59 L 66 95 L 32 95 L 32 53"
    # The Codevertex check tail, rising from the right roof corner and out through the ring.
    tail = "M 61.2 61.8 L 104 9 L 111.5 4 L 108.5 12.5 L 70.6 64.6 Z"
    return (f'<path d="{ring_path}" fill="none" stroke="{ring}" stroke-width="{sw}" stroke-linecap="round"/>'
            f'<path d="{house}" fill="none" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{tail}" fill="{stroke}"/>'
            f'<rect x="43" y="72" width="12" height="23" rx="2.5" fill="{door}"/>')


def svg(w, h, body, bg=None, title="Maskani"):
    rect = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-label="{title}"><title>{title}</title>{rect}{body}</svg>\n')


def icon(bg=None, rounded=False, **kw):
    if rounded:
        body = f'<rect width="120" height="120" rx="26" fill="{bg}"/><g transform="translate(6 4) scale(0.9)">{mark(**kw)}</g>'
        return svg(120, 120, body, title="Maskani icon")
    return svg(120, 120, mark(**kw), bg=bg, title="Maskani icon")


def favicon():
    """Simplified for 16 to 32 pixels: heavier strokes, no ring."""
    body = (f'<rect width="32" height="32" rx="7" fill="{PLUM}"/>'
            f'<path d="M 6 16 L 12.5 9.5 L 18 15 L 18 25 L 8.5 25 L 8.5 14" fill="none" stroke="{WHITE}" stroke-width="2.6" '
            f'stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="M 18 15 L 27 5" stroke="{WHITE}" stroke-width="2.6" stroke-linecap="round"/>'
            f'<rect x="11.5" y="18.5" width="3.6" height="6.5" rx="0.8" fill="{GOLD}"/>')
    return svg(32, 32, body, title="Maskani")


def lockup(sub, word_color=PLUM, sub_color=GREY, by=True, dark=False, **kw):
    """Horizontal logo: mark, MASKANI wordmark, and a tracked sub-line."""
    word, ww = text_path("MASKANI", "texgyreadventor-bold.otf", 64, 0, 0, tracking=0.04)
    subp, sw_ = text_path(sub, "texgyreadventor-regular.otf", 17, 0, 0, tracking=0.32)
    tx = 138
    w = int(tx + max(ww, sw_) + 16)
    body = [f'<g transform="translate(4 4)">{mark(**kw)}</g>',
            f'<path transform="translate({tx} 74)" d="{word}" fill="{word_color}"/>',
            f'<path transform="translate({tx + 2} 104)" d="{subp}" fill="{sub_color}"/>']
    return svg(w, 128, "".join(body), bg=(PLUM_DARK if dark else None),
               title="Maskani" + ("" if sub.startswith("BY") else " " + sub.title()))


def stacked(sub, **kw):
    word, ww = text_path("MASKANI", "texgyreadventor-bold.otf", 56, 0, 0, tracking=0.04)
    subp, sw_ = text_path(sub, "texgyreadventor-regular.otf", 15, 0, 0, tracking=0.32)
    w = int(max(ww, sw_, 160) + 40)
    body = [f'<g transform="translate({(w - 140) / 2} 6) scale(1.1667)">{mark(**kw)}</g>',
            f'<path transform="translate({(w - ww) / 2} 210)" d="{word}" fill="{PLUM}"/>',
            f'<path transform="translate({(w - sw_) / 2} 240)" d="{subp}" fill="{GREY}"/>']
    return svg(w, 256, "".join(body), title="Maskani")


def main():
    OUT.mkdir(exist_ok=True)
    white = dict(ring=WHITE, stroke=WHITE, door=GOLD)
    files = {
        "maskani-icon.svg": icon(),
        "maskani-icon-app.svg": icon(bg=PLUM, rounded=True, **white),
        "maskani-icon-white.svg": icon(**white),
        "favicon.svg": favicon(),
        "maskani-logo.svg": lockup("BY CODEVERTEX"),
        "maskani-logo-dark.svg": lockup("BY CODEVERTEX", word_color=WHITE, sub_color="#E7C27A", dark=True, **white),
        "maskani-marketplace-logo.svg": lockup("MARKETPLACE", sub_color=GOLD),
        "maskani-marketplace-logo-dark.svg": lockup("MARKETPLACE", word_color=WHITE, sub_color="#E7C27A", dark=True, **white),
        "maskani-logo-stacked.svg": stacked("BY CODEVERTEX"),
        "maskani-marketplace-logo-stacked.svg": stacked("MARKETPLACE"),
    }
    for name, content in files.items():
        (OUT / name).write_text(content)
    # PNG exports for app manifests, store listings and documents.
    pngs = [("maskani-icon-app.svg", "maskani-icon-512.png", 512), ("maskani-icon-app.svg", "maskani-icon-192.png", 192),
            ("maskani-icon-app.svg", "apple-touch-icon.png", 180), ("favicon.svg", "favicon-32.png", 32),
            ("maskani-logo.svg", "maskani-logo.png", 1200), ("maskani-marketplace-logo.svg", "maskani-marketplace-logo.png", 1200),
            ("maskani-logo-dark.svg", "maskani-logo-dark.png", 1200)]
    env = {**os.environ, "NODE_PATH": subprocess.check_output(["npm", "root", "-g"]).decode().strip()}
    for src, dst, width in pngs:
        subprocess.run(["node", str(HERE / "render_png.js"), str(OUT / src), str(OUT / dst), str(width)], check=True, env=env)
    print("ok", len(files), "svg,", len(pngs), "png")


if __name__ == "__main__":
    main()
