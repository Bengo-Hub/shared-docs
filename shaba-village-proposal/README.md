# Codevertex Property Platform: SRDD and Shaba Village launch proposal

`Codevertex-Property-Platform-SRDD-Shaba-Village.pdf` is the client document (78 pages). It specifies the
multi-tenant property SaaS across four releases (R1 estate management and Shaba launch, R2 rental and
portfolio management, R3 public marketplace, R4 extensions), with tenant-configurable modules, use case
presets, a seeded charge catalogue and layered configuration, plus the Release 1 commercials for Shaba Village. It uses the
same build, typeface (TeX Gyre Heros), page design and diagram style as the Hadia SRDD, with a
linked contents page and PDF bookmarks.

## What changed from the original requirements document

The first draft ("Property Management and Real Estate Services Platform", v1.0) was a generic
rental-management specification written without reference to the Codevertex platform. This version
replaces it. The main corrections:

| Area | Original draft | This version |
|---|---|---|
| Product shape | A single generic rental app | Multi-tenant SaaS: estate operators (Shaba first), property managers and landlords, and a verified public marketplace in R3; modules and use cases configured per tenant and per property |
| Architecture | A new monolith with its own users, invoices, payments, receipts, notifications and audit tables | Only `property-api`, `property-ui` and (R3) `marketplace-ui` are new. Identity, invoices, M-Pesa, ledger, approvals, payouts, payroll and messaging reuse auth, treasury, erp and notifications, with references by ID |
| Money | One payments table, no fund separation | Sales and estate funds kept apart (paybills, bank accounts, ledgers), ready for handover to the management corporation |
| Utilities | "Utility billing" with no method | Meter rounds with photos, anomaly checks, estimates, water balance against Mavoko and borehole supply; electricity not resold |
| Service providers | A "service provider" role that updates job status | Full provider cycle: licences with expiry, contracts and SLAs, schedules, guard posts, rosters, patrols, evidence, vendor portal, SLA credits, approval and payment |
| Staff | Not covered | Regular and casual staff in erp-api payroll and casual payments |
| Security | Not covered | Gate tablet with offline mode, passes, walk-in approval, occurrence book, data minimisation per ODPC guidance |
| Compliance | One line on "Kenyan data protection" | Data Protection Act and registration, ODPC private security guidance, Sectional Properties Act, Water Act, Energy Act, Waste Act, PSRA, Estate Agents Act, AML, tax and eTIMS, case law on disconnection, GDPR for diaspora owners |
| Commercials | None | KES 250,000 build; monthly tiers adapted from the ERP subscription tiers (10,000, 20,000, 35,000, quote) including hosting and support |

## Rebuilding

Requirements: Python 3 with fonttools and pikepdf, Node with Playwright, and the `fonts-texgyre`
package.

1. From `source/`, convert the font once:

   ```
   mkdir -p fonts
   python3 -c "from otf2ttf import convert; src='/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyreheros-'; [convert(src+w+'.otf', 'fonts/heros-'+w+'.ttf') for w in ('regular','bold','italic','bolditalic')]"
   cp fonts/*.ttf ~/.local/share/fonts/ && fc-cache -f
   ```

2. Edit chapters in `content_*.html`, the cover in `cover.html` or diagrams in `figures.py`.
3. Run `python3 build.py`. It numbers sections and figures, renders twice to fill the contents
   page numbers, refuses forbidden characters (long dash, section sign, arrows, curly quotes),
   adds the cover and writes the PDF one folder up.
