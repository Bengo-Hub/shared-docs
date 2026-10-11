# Reports

Every Maskani report lives on one page: **Reports** in the menu. It only lists reports for the parts
of Maskani your estate runs and the ones your role may see.

## Finding a report

Pick a module on the left, or **All reports**, and choose the months at the top. Reports cover the
property picked at the top of the console, or all your properties when none is picked.

| Module | Report | Answers |
|---|---|---|
| Billing and collections | Collections by month | Are we collecting what we bill? |
| | Collections by block | Which blocks are behind? |
| | Billing by charge | How much of our billing is service charge, water, garbage? |
| | Payment channels | How do owners pay: M-Pesa, bank, cheque, cash? |
| | Arrears | Who owes, and how old is each debt? |
| | Estate performance | The month's headline pack for the board |
| Water | Water trend | Are we losing water between the bulk meter and the units? |
| Maintenance | Maintenance performance | Are repairs answered and fixed on time? |
| Vendors | Vendor scorecard | Which vendors deliver on time, at what cost, with valid papers? |
| Security | Security summary | How busy is the gate, and how many incidents? |
| Sales | Sales position | Which buyers are behind, and by how much? |
| | Instalment receivables | What will buyers owe each month, and what came in? |
| | Handover and title | Which paid-up units wait for handover, and where is each title? |

## Opening and downloading

**Open** shows the report on screen with a total row. **PDF**, **Excel** and **CSV** download the
same figures, branded with your estate's logo, for the board, auditors or owners. A report that
covers one property (the water trend) asks you to pick a property first.

```mermaid
flowchart LR
  P[Reports page] --> C{Pick module<br/>and months}
  C --> O[Open: table on screen]
  C --> D[Download: PDF, Excel, CSV]
  O --> D
```

Figures refresh as payments arrive and billing runs finish, so the same report run twice a few
minutes apart can differ if money came in between.

## The dashboard's performance section

Under the day-to-day tiles, **Performance and outlook** follows the filters at the top of the
dashboard. Choose up to twelve months, and optionally a block or a fund:

- **Collection rate, collected and billed** cover the months you chose, set against the same number
  of months just before (last month, when you chose one) and the same months a year earlier.
- **Revenue by charge**, **Blocks compared** and **Maintenance** cover the same months.
- A block narrows every figure to its units; a fund narrows billing, collections and balances, and
  leaves repairs and sales as they are.
- **Owing now**, occupancy and the forecast are always as of today.

**Report PDF** and **Excel** download exactly what the section shows, with the same filters.
