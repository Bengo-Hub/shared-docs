# Customer Service Week 2026 banner — Codevertex Africa Limited

Social / print banner for Customer Service Week (October 5–11, 2026).

- `banner.html` — source (1536×1024). Uses the Montserrat and Great Vibes fonts from Google Fonts.
- `codevertex-customer-service-week-2026.png` / `.jpg` — rendered at 2x (3072×2048).
- `assets/codevertex-logo.png` — logo cropped from `codevertex-website/public/images/logo.png`.
- `assets/agent-source.jpg` — original customer-care agent photo.
- `assets/codevertex-agent.jpg` — the same photo with the full Codevertex logo embroidered on the left chest (satin-stitch texture, bevel, cast shadow, fabric shading), widened to landscape.
- `embroider_logo.py` — regenerates the photo: `python3 embroider_logo.py <scratch-dir> 150 576 800` (logo width, x, y on the 2x-upscaled source).

Contact details come from `codevertex-website/src/lib/constants.ts` (`SITE`).

To re-render with Playwright, open `banner.html` at a 1536×1024 viewport with `deviceScaleFactor: 2` and take a screenshot.
