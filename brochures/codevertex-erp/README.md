# Codevertex ERP brochure

Source of `docs/user-guide/erp/assets/Codevertex-ERP.pdf`, the shareable PDF that shows prospects
the whole Codevertex ERP: HR core, leave, time and attendance, payroll and payroll extras,
statutory returns, appraisals, training, recruitment, self-service, approvals, reports, the
integrated Codevertex services, plans, support and customisation. It is linked as a download
button from the ERP guide's index and plans pages. It holds no customer names; prices match the
public plans in `docs/user-guide/erp/plans-and-support.md`.

| Path | Contents |
|---|---|
| `cover.html`, `body.html`, `style.css`, `fonts/` | The brochure |
| `logo.png`, `logo-light.png` | The official Codevertex logos (copies of `codevertex-website/public/images/brand/logo-full.png` and `logo-full-light.png`) |

Colours follow the logo purple (`--brand #801E68`, `--brand-deep #5B1549`) with the brand yellow
`--sun #F4B41A` and an amber `--amber #B45309` as accents.

The brochure uses the ERP guide's own screenshots in `docs/user-guide/erp/assets/` (written by
erp-ui's docs-capture suite, `e2e/docs-capture`), so there is one copy of each image.

## Rebuilding

1. Refresh the screenshots from erp-ui if the screens changed (needs the demo account in
   `E2E_LOGIN_EMAIL` and `E2E_LOGIN_PASSWORD`):
   `E2E_BASE_URL=https://erp.codevertexafrica.com npx playwright test --project=docs-capture-setup --project=docs-capture`
2. In this folder: `NODE_PATH=../../../erp/erp-ui/node_modules node build.cjs`
3. `python -I merge.py`

Each section starts its own page. After a rebuild, check that no section spills onto a second
page, and check every KES figure against `plans-and-support.md` before publishing.
