# Online Orders: Accept, Prepare, Hand Over, Dispatch

Orders customers place on your online ordering app (for example "Urban Eats") arrive in the POS
**Online Orders Queue**. This page covers what the counter, the kitchen and your riders do with
them, for restaurants, shops and service businesses.

> **Direct link:** `https://pos.codevertexafrica.com/{your-tenant-slug}/online-orders`

Who can use the queue: cashiers, waiters, floor supervisors, receptionists and managers (the
**Online orders** permission). The kitchen works from the KDS and never needs the queue.

## 1. Accept or reject a new order

A new order rings and appears under **New orders to accept** marked **New · accept?**, and keeps
ringing every 30 seconds until someone acts. Check you can make it (items in stock, kitchen not overloaded), then:

- **Accept**: the kitchen gets the tickets and the chit prints. The customer is told the order
  was accepted.
- **Reject**: pick a reason. The customer is told, a paid order is refunded and the stock hold is
  released.

Orders are accepted by hand unless your admin turned on automatic acceptance (ordering staff
dashboard **Settings > Order acceptance**). A scheduled order accepted early goes to the kitchen at its
preparation time.

## 2. Payment the counter must check

| Label on the card | What to do |
|---|---|
| **Paid online** | Nothing to collect. |
| **M-Pesa (code) · confirm payment** | The customer paid your Till or Paybill and typed the code. Match it with your M-Pesa message and press **Confirm M-Pesa**. If you cannot find it, reject the order. |
| **Pay at counter** / **Pay on delivery** with an amount | Take cash or M-Pesa at hand-over. |

## 3. Prepare

What happens once an order is accepted depends on your kind of outlet:

| Outlet | Pickup and delivery orders |
|---|---|
| Restaurant, café, bar, hotel, quick service | Tickets go to the KDS station that makes each item and the kitchen and bar chits print. |
| Shop (retail) | No kitchen. The order goes straight to the queue as a pick list ("To pick & pack"); the bill prints as the pick list if your outlet prints orders automatically. |
| Service business selling goods (salon products, spare parts) | Same as a shop. Online bookings for a service go to **Appointments**, not the queue. |

Restaurants: the kitchen presses **Start** and **Ready** on the KDS; the customer sees
"Preparing" and then "Ready". Printer-only kitchens and shops packing an order press **Ready**
on the queue card instead.

Every kitchen and bar chit prints the order type in large letters at the top (**DINE-IN**,
**TAKEAWAY**, **DELIVERY**, **ROOM SERVICE**, **BAR TAB**, **ONLINE PICKUP**, **ONLINE DELIVERY**)
and where the order came from (**POS** or **Online store** with its order number), the customer's
name for takeaway and delivery, the promised time for a scheduled order and the customer's note.
Chits for items added later keep the order type under the **ADDITIONAL ITEMS** line.

## 4. Hand over a pickup order

Press **Hand over** and ask the customer for the **6-digit collection code** from their order
page or message. The POS checks it (it never shows you the code). If the customer cannot show it
(phone off, message deleted), choose **Customer does not have the code** and write how you
checked them, for example name and phone number; this is saved on the order. For an unpaid
order, choose Cash or M-Pesa (with the code) before releasing it.

## 5. Delivery orders and riders

When a delivery order is ready it goes to your riders:

- **Automatic**: the nearest available rider is assigned (logistics setting).
- **Dispatcher**: assign a rider from the queue or from the logistics console.
- **Riders take jobs**: riders see **Open jobs** in the rider app and tap **Take job**. Only one
  rider can take a job.

The rider checks the bag against the order at the counter, delivers, asks the customer for the
**delivery code**, and records cash or the M-Pesa code for pay-on-delivery orders. Riders get a
phone alert when a job is assigned to them once notifications are enabled in the rider app.

If you deliver with your own staff and no rider app, press **Delivered (own staff)** on the queue
card.

The **Delivery** tab groups orders by where they are: waiting for a rider, ready for the rider,
**Out for delivery** and **Delivered, to settle or close**. Each card shows the rider's name and
phone once a rider has the job. A delivery taken at the till (not online) works the same way:
press **Assign rider** and the rider is told how much to collect at the door. When the rider
delivers it, the card shows how the customer paid (cash, or M-Pesa with its code); press
**Settle** to take that money into the till and the order closes. If a delivery fails or is
cancelled the card says so and you can assign a rider again.

A till takeaway or delivery order cannot be handed over before it is paid. Till orders already
paid at the till leave the queue after a day even if nobody pressed **Hand over**.

## 6. Rider cash hand-in

Cash riders collect on delivery is tracked per rider. In the logistics console, **Finance >
Rider Cash** lists every rider still holding cash, with each delivery. When a rider hands the
cash in, press **Record hand-in**, enter the amount you counted and save. Any shortfall is kept
on the record for a manager to follow up. Riders see their own "Cash to hand in" on the rider
app dashboard.

## Service bookings

A booking for a service (haircut, car service, printing job) is added to the appointment
calendar instead of the kitchen. The storefront only offers free time slots, and the balance is
charged at the POS when the appointment is completed.

## Your app's name and icon

Admins can give each app its own name and icon in Accounts > My Organisation > Branding > **App
Names and Icons** (for example the ordering app as "Urban Eats"). Customers see it in the
browser tab, on the sign-in page and on their home screen when they install the app.
