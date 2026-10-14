# Codevertex product banners: POS Suite and ERP Suite

Portrait promo banners (1080×1600, rendered at 2x as 2160×3200 PNG/JPG).

- `build.py` generates `pos-suite.html` and `erp-suite.html` from one template. To change copy, edit the `POS` / `ERP` dicts and run `python3 build.py`.
- Render: open the HTML at a 1080×1600 viewport with `deviceScaleFactor: 2` (Playwright) and screenshot.

Copy sources:
- Features: subscriptions-api `cmd/seed/plans_powersuite_usecase.go` (POS core, Hospitality/Duka/Dawa families) and `cmd/seed/plans_erp.go` (ERP modules + bundled commerce stack).
- Pricing: POS from KES 1,500/month (Dawa Basic); ERP from KES 10,000/month (Starter). Both have a 14-day free trial.
- URLs and contacts: codevertex-website `src/config/services.ts` and `src/lib/constants.ts`.
