# Maskani brand assets

Logo and icon for Maskani, the Codevertex property platform, and Maskani Marketplace, its public
marketplace. `maskani-brand-sheet.png` shows every variant together.

## The mark

A house inside the Codevertex ring. The right slope of the roof and the rising tail form the
Codevertex check, which breaks out of the ring at the top right exactly as it does in the parent
logo. The ring is the enclosed home compound, and the gold doorway is the way in. In Kiswahili,
maskani is home: the place you live and return to.

## Colours

| Name | Hex | Use |
|---|---|---|
| Codevertex plum | `#6E1A5A` | Mark, wordmark, app icon background |
| Deep plum | `#4E1240` | Dark backgrounds |
| Door gold | `#C8963E` | Doorway, Marketplace sub-line |
| Light gold | `#E7C27A` | Sub-line on dark backgrounds |
| Slate | `#6A6E78` | "BY CODEVERTEX" sub-line on light backgrounds |

The wordmark is TeX Gyre Adventor Bold (sub-lines in Regular, widely tracked), converted to
outlines, so the SVGs render the same everywhere without the font installed.

## Files (`assets/`)

| File | Use |
|---|---|
| `maskani-logo.svg`, `.png` | Primary horizontal logo for maskani-ui: header, documents, emails |
| `maskani-logo-dark.svg`, `.png` | On dark or plum backgrounds |
| `maskani-logo-stacked.svg` | Square spaces: sign-in screens, splash |
| `maskani-marketplace-logo.svg`, `.png` | maskani-marketplace header |
| `maskani-marketplace-logo-dark.svg` | Marketplace on dark backgrounds, footer |
| `maskani-marketplace-logo-stacked.svg` | Marketplace square spaces |
| `maskani-icon.svg` | Mark alone on light backgrounds |
| `maskani-icon-white.svg` | Mark alone on dark backgrounds |
| `maskani-icon-app.svg`, `maskani-icon-512.png`, `maskani-icon-192.png` | PWA manifest and app icons |
| `apple-touch-icon.png` | iOS home screen (180 px) |
| `favicon.svg`, `favicon-32.png` | Browser tab; simplified mark without the ring for small sizes |

Keep clear space around the logo of at least the width of the doorway on every side, and do not
recolour, stretch or rotate the mark.

## Rebuilding

`python3 build_brand.py` regenerates every file from the geometry in the script. It needs Python
with fonttools, the `fonts-texgyre` package and Node with Playwright for the PNG exports.
