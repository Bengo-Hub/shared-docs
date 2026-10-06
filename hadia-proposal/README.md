# Hadia Gifting Registry: Technical Proposal and SRDD

`Hadia-Gifting-Registry-SRDD-Codevertex.pdf` is the client document (41 pages). It is set in
TeX Gyre Heros, a Helvetica-class typeface under the GUST Font License, with vector diagrams,
a linked contents page and PDF bookmarks.

## Rebuilding

Requirements: Python 3 with fonttools and pikepdf, Node with Playwright, and the `fonts-texgyre`
package (for `texgyreheros-*.otf`).

1. Convert the font to TrueType once, from `source/`, so Chromium embeds compact subsets:

   ```
   mkdir -p fonts
   python3 -c "from otf2ttf import convert; src='/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyreheros-'; [convert(src+w+'.otf', 'fonts/heros-'+w+'.ttf') for w in ('regular','bold','italic','bolditalic')]"
   cp fonts/*.ttf ~/.local/share/fonts/ && fc-cache -f
   ```

2. Edit the chapters in `content_*.html`, the cover in `cover.html`, or the diagrams in
   `figures.py`.
3. Run `python3 build.py`. It numbers sections and figures, renders twice to fill the contents
   page numbers, adds the cover and writes the compressed PDF.
