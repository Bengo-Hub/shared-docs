# Vouchers & Approvals

A **voucher** records money that moved without an invoice or a supplier bill: wages paid to a
casual worker, a repair paid in cash, transport, a deposit received, cash taken to the bank. It is
the same idea as the voucher book in Tally, Zoho Books, Odoo or QuickBooks: one form per kind of
movement, a voucher number, a payee, and sign-off before it reaches the ledger.

> **Direct link:** `https://books.codevertexafrica.com/{your-tenant-slug}/ledger/vouchers`

## Choosing the voucher type

| Type | Use it for | You fill in |
| --- | --- | --- |
| **Payment** | money paid out: casual wages, repairs, rent, transport, a supplier, salaries | the account it was paid from, then what it was for and how much |
| **Receipt** | money received that is not an invoice payment: a refund, a deposit, owner capital | the account it came into, then what it was for |
| **Contra** | moving money between your own accounts: cash banked, bank to M-Pesa | the from account, the to account and the amount |
| **Journal** | adjustments with no money moving: accruals, corrections | a debit and credit grid that must balance |
| **Sales** / **Purchase** | a sale or purchase recorded straight in the ledger without an invoice or bill | a debit and credit grid that must balance |

For a payment or a receipt you never enter the bank side yourself. You pick the cash, bank or
M-Pesa account once, list the accounts the money was for, and the voucher total is booked to that
account automatically, so the voucher always balances. Cash and bank accounts are not offered as
lines on these two types; moving money between them is a contra voucher.

Hover the **i** next to Account, Amount, Debit, Credit and Memo for what each one expects.

### Example: paying five casual workers and a supplier in one voucher

Each line of a payment or receipt has its own **Paid to** (or **Received from**), so one voucher
can cover several people.

1. **New Voucher**, type **Payment Voucher**.
2. **Paid from**: the bank or M-Pesa account the money left.
3. Lines, one per person or cost:
   - *Salaries and Wages* 1,000, **Paid to** set to **Not in system** with the worker's name. Add a
     line for each of the five workers; a new line keeps the type of the one above it.
   - *Repairs and Maintenance* 4,500, **Paid to** set to **Supplier** and the supplier picked from
     the list.
4. **Reference**: the M-Pesa or bank code. The voucher number (PV-000123) is given for you.
5. **Save and submit**. The bank account is credited once with the total, 9,500.

The voucher book shows the names on the voucher with how many people it paid, and searching for
any of them finds it. Use **Supplier**, **Customer** or **Staff** to pick someone already on record,
or leave **Paid to** empty on a line that paid no one in particular.

### Paying staff

- **No payroll in the system**: record each pay run as a payment voucher with the line on
  *Salaries and Wages*.
- **Payroll run in ERP**: when ERP processes payroll, Treasury already records the salary cost and
  what is owed (Salaries and Wages against *Accrued Salary Payable* and *Statutory Deductions
  Payable*). When you pay the net salaries, put the voucher line on **Accrued Salary Payable**, not
  on Salaries and Wages, or the wages are counted twice. Pay PAYE, SHIF, NSSF and the housing levy
  the same way against *Statutory Deductions Payable*.

## From draft to the ledger

| Status | Meaning | Next step |
| --- | --- | --- |
| Draft | saved, not submitted | **Submit** (send icon) |
| Awaiting approval | in the Approvals queue | an approver decides it there |
| Approved, not posted | signed off | **Post** (stamp icon) |
| Posted | in the ledger and the reports | **Reverse** if it was wrong |

A rejected voucher goes back to draft so it can be corrected and submitted again. A posted voucher
is never edited: reversing it books an opposite entry and keeps both on record. If two people
approve, post or reverse the same voucher at the same moment, only the first counts; the other is
told it has already moved on, so nothing is posted or reversed twice.

## Approval rules

Expenses, journal entries and vouchers all go through **Approvals**, the same queue invoices and
supplier bills use. **Approvals > Rules** sets, per document type, the amount bands that need
sign-off and the role that signs each step. Vouchers have their own type, so you can rule them
separately from journal entries.

- If you have never set a rule for a type, a default one is created the first time something is
  submitted: everything needs one sign-off by a Finance Admin. Change or replace it under Rules.
- When your rules leave an amount out (for example below your lowest band), that document is
  approved as soon as it is submitted.
- Approving on the expense or entry itself sends you to the Approvals queue whenever a rule
  applies, so the approver's role and, for expenses, the emailed code are always checked.
- Approving in the queue has the full effect: an approved expense is booked to the ledger and
  counted against its budget, an approved voucher is ready to post.

## Expenses and KRA eTIMS

When eTIMS is activated, the **Submit** dialog for an expense has a **Transmit to KRA eTIMS**
switch, like the invoice Send dialog. When it is on, the expense is recorded on eTIMS as a
purchase once it is paid, so the input VAT can be claimed. That needs the supplier's KRA PIN on
the expense. Turn it off for expenses that should not go to KRA.

Vouchers are not sent to KRA. When a supplier gives you a tax invoice you want to claim input VAT
on, record it as a supplier bill or an expense (which eTIMS receives as a purchase) and pay it from
there or with a payment voucher against the supplier's balance.
