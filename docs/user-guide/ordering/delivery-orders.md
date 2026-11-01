# Delivery orders

A delivery order is accepted and prepared like a pickup order, then a rider takes it to the
customer. This page follows one from Demo City Supermarket to a customer in Kondele (KES 150
delivery), paid on delivery.

## 1. Accept and prepare

The order rings under **Delivery** in the POS **Online orders** queue. Accept it the same way as
a [pickup order](pickup-orders.md#1-accept-or-reject).

![A new delivery order](assets/delivery/01-new-order.png)

A shop packs the order and presses **Ready** on the card; a restaurant's kitchen presses **Ready**
on the kitchen screen. Either way the customer is told it is ready and a delivery job is created
for your riders.

## 2. Getting a rider

The job goes to a rider in one of three ways, depending on your
[dispatch settings](setting-up.md#how-jobs-reach-riders):

- **Automatically** to the nearest available rider on shift.
- **By a dispatcher**, from **Logistics, Deliveries** (or **Assign rider** on the POS card).
- **By a rider** taking it from **Open jobs** in the rider app. Only one rider can take a job.

![The job on the Logistics deliveries board](assets/delivery/02-logistics-job.png)

Once a rider has the job, the POS card shows their name and phone and the customer sees who is
coming.

## 3. The rider app

Riders use the rider app on their phone (`https://riderapp.codevertexafrica.com`). To get jobs
they switch themselves **online**, which also shares their location while they work.

![Going online in the rider app](assets/delivery/03-rider-online.png)

**Open jobs** lists jobs waiting for a rider, with the outlet, the area and the fee.

![Open jobs](assets/delivery/04-rider-open-jobs.png)

After taking a job the rider sees the route to the outlet, then:

1. **At the counter**, checks the bag against the order on screen and marks it **Picked up**. The
   customer's page changes to *On the way* and shows the rider on the map. Any kitchen tickets
   still open for the order close.
2. **At the door**, asks for the customer's **6-digit delivery code** and enters it.
3. For **pay on delivery**, records how the customer paid: cash, or M-Pesa with the code. The app
   says **Collect payment at the door** with the amount.
4. Submits the proof of delivery. The order is delivered, the customer is told, and the stock is
   taken off.

![The active delivery](assets/delivery/05-rider-active.png)

![Proof of delivery with the code and payment](assets/delivery/06-rider-proof.png)

If the customer is not reachable or refuses the order, the rider reports a failed delivery with a
reason instead (see [When things go wrong](when-things-go-wrong.md#a-delivery-fails)).

## 4. Rider cash

Cash a rider collects belongs to the business until they hand it in. Riders see what they hold
as **Cash to hand in** on their app. In **Logistics, Rider cash**, the dispatcher or manager
counts the cash, enters the amount received with **Record hand-in**, and any shortfall stays on
the record for a manager to follow up.

![Rider cash in Logistics](assets/delivery/07-rider-cash.png)

## Delivering with your own staff

If you deliver without the rider app, press **Delivered (own staff)** on the POS card once the
order has reached the customer.

## What the customer sees

![The customer's order page while on the way](assets/delivery/08-customer-on-the-way.png)
