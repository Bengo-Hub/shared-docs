# Leave

Leave in Codevertex ERP runs from a leave type, through each person's yearly entitlement and
balance, to a request that is approved and deducted. Approved leave also protects the person in
attendance: a day on approved leave is never marked absent.

```mermaid
flowchart TD
  A[Leave types set up] --> B[Entitlements per employee and year]
  B --> C[Accrual job builds balances, with carryover]
  C --> D[Staff apply in self-service, or HR applies for them]
  D --> E{Approval workflow for leave?}
  E -->|yes| F[Each step approves in turn]
  E -->|no| G[HR approves or rejects directly]
  F -->|all steps approve| H[Approved: days deducted from balance]
  G -->|approve| H
  F -->|any step rejects| I[Rejected with a reason]
  G -->|reject| I
  H --> J[Employee notified, leave log updated]
  I --> J
  H --> K[Days on leave are never marked absent]
```

## Leave types

Go to **HRM → Leave → Types**.

![Leave types](assets/hrm-leave-types.png)

| Field | What it does |
|---|---|
| Name | For example Annual, Sick, Maternity, Paternity, Compassionate |
| Max days | The default number of days a year for this type, used when a person has no entitlement of their own |
| Paid | Whether the leave is paid |
| Carry forward | Whether unused days move into next year |
| Description | Notes for staff |

The **Days counted** column sets how a request of that type is counted. HR picks it per type in
the list, and it applies to requests filed from then on:

- **Working days** skips the person's own days off and the public holidays that apply to them. A
  half-day shift override counts as half a day.
- **Calendar days** counts every date from the start to the end.

Maternity and paternity leave start on calendar days, every other type on working days.

The **Beyond the balance** column sets what happens to a request for more days than the person has
left: **Refuse**, or **Allow with a warning**. Paid types start on refuse, unpaid types on allow.

### Platform defaults, customised and own types

Annual, Sick, Maternity, Paternity, Compassionate, Study and Unpaid leave come with the ERP as
**Platform default** types that every company shares. Editing one changes it for this company only:
the badge turns to **Customised**, and the **Restore platform values** button next to it drops the
company's changes. A platform type keeps its name and cannot be deleted; switch it off instead by
turning off **Active** (a switched-off type takes no new requests, while requests already filed on
it stay). A type added here is the company's **Own**. An own type with the same name as a platform
type (capitals and spaces ignored) takes that type's place for this company.

The two columns are set per company for every type, platform ones included.

## Entitlements

Go to **HRM → Leave → Entitlement** to give a person a different number of days from the
default, for example more annual leave for long service. Each entitlement is one employee, one
leave type, a number of days and a year. Deleting one puts the person's balance back to the type's
default days; days already taken stay.

![Leave entitlement](assets/hrm-leave-entitlement.png)

## Accrual and balances

A background job runs once a day and builds every active employee's balance for each active
leave type the company uses in the current year, platform types included (with the company's
changes to them):

- **Entitled** is the person's entitlement for the year, or the type's default days if they
  have none, plus any days carried forward from last year (capped at the type's carryover
  limit, and only for types that allow carry forward).
- **Used** is the days taken on approved leave.
- **Remaining** is entitled less used. It can drop below zero when more days are approved than
  the person has; the daily job then shows it as zero.

Running it again never undoes days already taken; it only refreshes what each person is
entitled to. If you have just changed an entitlement and want the balances updated straight
away, click **Run Accrual** on the balances page.

Go to **HRM → Leave → Balances** to see entitled, used and remaining days per person and type.

![Leave balances](assets/hrm-leave-balances.png)

## Requests

Go to **HRM → Leave → Requests**.

![Leave requests](assets/hrm-leave-requests.png)

**Staff** apply from **My Dashboard → Apply for Leave**; any account linked to an employee record
can. **HR** (the permission to manage leave) can apply on anyone's behalf with **Apply for Leave**
on the requests page. The form asks for:

| Field | Notes |
|---|---|
| Employee | The person going on leave. Only shown to HR; staff always apply for themselves |
| Leave type | One of your leave types |
| Start date, end date | The end date cannot be before the start date |
| Reason | Optional |

You do not type the number of days. Once the dates are in, the form shows how many days the
request takes, the public holidays and days off it skips, and the remaining balance. Days off come
from the person's planned shifts: a shift override first, then their roster, their own work shift
and the company default shift. With no shift at all, the default working days in the attendance
settings apply. Dates with nothing to count are refused, and so are dates that overlap another
pending or approved request of the same person.

A request is also held against the balance of its type and year, less the days already in the
person's pending requests. When it takes more, the type's rule decides: the form either shows the
reason and does not let you submit, or warns and lets you. With no balance set for that year the
request is allowed. The balance is checked again when the request is approved. The rule binds HR
too: to let someone go over, change the rule or give them an entitlement.

Staff can cancel their own request in **My Leave** while it is pending. Once it is approved, ask HR.

A new request starts as **Pending**. The page has two tabs: **All Requests**, which you can
filter by status (Pending, Approved, Rejected), and **Approvals Queue**, which shows only what
is waiting for a decision. The search box finds people by name or staff number.

## Approving and rejecting

Approvers see pending requests in the **Approvals Queue** with **Approve** and **Reject**
buttons. Rejecting asks for a reason, which the employee sees.

- **With a leave approval workflow** (set under **Administration → Settings → Approval
  Workflows**, module "Leave Request"), each step approves in order. The request stays Pending
  until the last step approves it. A rejection at any step ends it.
- **Without a workflow**, anyone with permission to approve leave decides it in one step.

Nobody can approve their own request. A decision made on the **Approvals** screen and one made here
do the same thing.

When a request is approved, its days are taken off the person's balance for that year. The
employee is notified of the decision either way. See [Approvals](approvals.md).

## Public holidays

Go to **HRM → Leave → Public Holidays** to see the company's holiday calendar. Each holiday has a
name and a date, and is either national (it applies to everyone) or a county holiday (it applies
only to staff whose HR region is that county). Pick a year at the top to see that year's list.

Kenya's national holidays come with the ERP as **Platform default** rows, following the Public
Holidays Act (Cap. 110): New Year's Day, Good Friday, Easter Monday, Labour Day, Madaraka Day,
Mazingira Day, Mashujaa Day, Jamhuri Day, Christmas and Boxing Day. When one falls on a Sunday the
next Monday is the holiday, marked "(observed)". Idd-ul-Fitr and other days declared in the Kenya
Gazette are added once declared. A company that works on one of them turns off its **Observed**
switch, and turns it on again to restore it; platform holidays cannot be edited or deleted. The
company's own holidays (a county day, a company day) are added, edited and deleted here. Holidays matter
beyond leave: the overnight absence check never marks anyone absent on a holiday that applies to
them, hours worked on one earn the holiday rate when overtime is paid through payroll, leave
counted in working days skips them, and they come off staff working capacity in project planning.

## Leave logs

Go to **HRM → Leave → Logs** for the audit trail: every request filed, approved, rejected or
cancelled, with who did it and when.

![Leave logs](assets/hrm-leave-logs.png)

## How leave affects attendance and payroll

- **Attendance.** The overnight absence check skips anyone on approved leave that day, so they
  are never marked absent and no absence penalty is raised against them. Approved leave also
  comes off the person's working capacity in project planning; leave that is still pending does
  not.
- **Payroll.** Because days on approved leave are not absences, they do not create attendance
  deductions in the payroll run. Approve leave before you run payroll for the month so the
  attendance figures are final.

See [Time and Attendance](time-and-attendance.md) for the absence rules.
