# Hadia Gifting Registry: proposal and SRDD

Client-facing proposal and software requirements and design document for Hadia, prepared by
Codevertex Africa Limited. The finished document is `Hadia-Gifting-Registry-SRDD-Codevertex.pdf`
(42 pages, about 640 KB).

## Rebuilding the PDF

The document is plain HTML with inline SVG diagrams, rendered by headless Chromium.

1. Edit the chapters in `source/content_*.html` or the diagrams in `source/figures.py`.
2. From `source/`, convert the Inter fonts to TrueType once (Chromium embeds CFF fonts as large
   Type 3 glyphs): `python3 otf2ttf.py Regular Medium SemiBold Bold Italic`. This writes
   `fonts/`, which is not committed.
3. `python3 build.py` assembles `hadia-srdd.html`. It refuses em dashes, section signs, arrow
   characters and curly quotes, in line with the house writing style.
4. `node render.js "$PWD"` renders the PDF (needs Playwright).
5. `python3 compress.py Hadia-Gifting-Registry-SRDD-Codevertex.pdf out.pdf` adds metadata and
   compresses it with object streams (needs pikepdf).
