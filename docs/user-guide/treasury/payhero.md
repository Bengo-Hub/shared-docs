# Accepting payments with PayHero

PayHero lets your customers pay you by M-Pesa straight into your own paybill, till or bank
account, and, outside Kenya, by MTN, Airtel and other mobile money networks, by card, or by bank
deposit. Payments taken at your POS, from invoices and from online orders all settle into the
channels you choose, and land in the right account in your books automatically.

This page is for business owners and finance admins. Developers integrating with the API should
read the [PayHero Integration Reference](../../integrations/payhero-integration-reference.md).

## Before you start

- PayHero is included from the **Growth** plans (it comes with M-Pesa integration). On a lower
  plan the PayHero tab shows an upgrade option instead.
- You need to be an admin with permission to manage payment gateways in Treasury.
- Have your paybill, till or bank account details ready. PayHero adds these on its own dashboard,
  not in Treasury.
- If you choose to have payments go **straight to your account** (see How payments reach your
  account), your PayHero **service wallet** needs some credit: PayHero takes its fee from it and,
  with an empty wallet, refuses those payments. The other choices never need it.

## Step 1: Turn PayHero on and get your account

Go to **Treasury, Settings, Payments, PayHero, Account** and switch PayHero on. Pick how you want
to use it:

| Option | When to choose it |
|---|---|
| **Your own PayHero account under Codevertex** (recommended) | You get your own PayHero wallet, kept separate from every other business. This is the only option that supports escrow, and it is needed for wallet payments. |
| **Shared platform account** | You only want payments to go into your own paybill or till. Codevertex adds it on its PayHero account and attaches it to you. Each payment passes through Codevertex's PayHero wallet and is paid on to your paybill or till at once; PayHero's charge comes out of the payment, so you are never billed later. No wallet of your own. |
| **Your existing PayHero account** | You already have a PayHero account and API key. Your key is stored encrypted. |

With the recommended option, click **Create account**. Your business name, email and phone are
filled in from your company profile. If your PayHero account was already created on the PayHero
dashboard, choose **Link existing account** and enter its account id instead.

Also set your **country** here. It decides which payment methods your customers see (for example
M-Pesa in Kenya, MTN and Airtel in Uganda) and how phone numbers are read.

> If Treasury says your organization's plan cannot create accounts, ask the Codevertex team to
> set it up for you, or use one of the other two options in the meantime.

## Step 2: Add your paybills, tills and bank accounts

On the **shared platform account**, send your paybill or till details to the Codevertex team.
They add it on the PayHero account and attach it to your business; it then appears under
**Channels and routing** and your customers' payments are paid into it. Skip the rest of this
step.

PayHero channels (paybills, tills, bank accounts) are added on the PayHero dashboard. From the
Account tab, use **Invite admin** to send a dashboard invitation to the person who will add them.

Once they are added, open **Channels and routing** and click **Sync channels**. Treasury also
syncs automatically every 15 minutes. Switch off any channel you do not want to receive money.

## Step 3: Decide where each kind of payment goes

Still on **Channels and routing**, choose which channel receives each kind of payment:

1. **By outlet**: a branch can have its own till.
2. **By payment type**: for example POS sales to one till and invoice payments to the paybill.
3. **Default channel**: everything else.

Only the payment types your business actually receives are listed.

Each channel is linked to one of your financial accounts (Banking, Accounts) so balances in your
books follow the money. Treasury matches them automatically by account number or bank name; you
can change the match at any time.

## Step 4: Verify your business (KYC)

To collect money from the public into your PayHero wallet, and to use escrow, PayHero requires
the Company verification level (tier 3). Complete verification on the PayHero dashboard (your
Team, Management, Verification). Then open **Verification** in Treasury and click **Refresh KYC**
to read your level back. Treasury also refreshes it daily.

## Step 5: Choose what your customers see

In **Settings, Payments, Gateways**, make sure PayHero is switched on. PayHero shows as its own
payment option, like Paystack, everywhere your customers pay:

- The **payment page** has a **PayHero** option. It opens PayHero's checkout, with the methods
  PayHero offers for the payment's currency down the side and the chosen method's form beside
  them. Today that is M-PESA in Kenya. Airtel Money, MTN MoMo, card, bank and other countries
  appear once Codevertex has confirmed them with a live payment.
- The **POS** has one **PayHero** button (with PayHero's logo) that opens the same checkout.
- **STK Push** and **C2B** on the POS, and **M-Pesa** on the payment page, are your own M-Pesa
  paybill or till connected directly through Safaricom (Daraja). They only appear when that is
  set up; PayHero never shows under them.

## What your customer sees when they pay

1. They open your payment link (or **Pay Now** on an invoice) and see the options your account
   accepts.
2. They choose **PayHero**, keep **M-PESA** selected and type their phone number. The page says
   **Check your phone** and waits.
3. M-Pesa sends a prompt to their phone. For a bank paybill it names the bank's paybill and your
   account number there; they enter their PIN.
4. The money reaches the channel you routed that payment to, either straight away or relayed
   through a PayHero wallet (see below). PayHero tells treasury, treasury confirms the payment
   with PayHero, and the invoice or sale is marked paid. The page updates on its own.

## How payments reach your account

An M-Pesa payment can reach your paybill, till or bank in two ways:

- **Straight to your account.** PayHero takes its fee (a small flat amount from its published
  schedule, which Codevertex keeps up to date daily) from your PayHero **service wallet**.
- **Relayed through a PayHero wallet.** The payment goes into a PayHero wallet first, PayHero
  takes its charge out of the payment itself, and the rest is paid on to your account straight
  away. No service wallet is needed.

Choose on the PayHero **Account** tab:

| Choice | What happens |
|---|---|
| **Let the system decide** (recommended) | Straight to your account while your service wallet covers the fee. Relayed when that has been measured to be cheaper for the amount, or when your service wallet runs short, so no payment is refused. |
| **Always relay** | Every payment is relayed; you never top up a service wallet. |
| **Always straight to my account** | You keep the service wallet topped up; payments are refused while it is empty. |

On the shared platform account every payment is relayed, whatever you choose.

Relayed payments pass through your own PayHero wallet once your account reaches PayHero's KYC
tier 3 (PayHero lets a wallet take customers' payments only from that tier); until then they pass
through Codevertex's PayHero wallet and are paid on to you the same way.

PayHero does not publish its wallet charges, so Treasury learns them from the charges PayHero
reports on real relayed payments and prices later payments from them. Until a charge has been
seen for a similar amount, "Let the system decide" relays only when your service wallet is short.

## The PayHero fee

You choose who pays PayHero's fee on the PayHero Account tab:

- **Customer pays** (the default): the fee is added to the amount. The payment page shows the fee
  and the total before the prompt is sent, and the fee is recorded in your books as a recovered
  charge. On a relayed payment the customer pays the relay's charge instead, and your account
  receives exactly the price.
- **I pay**: the customer is prompted for the amount only and you carry the fee. On a relayed
  payment your account receives the price less PayHero's charge.

Every payment's fee is shown with the transaction, and PayHero's charge on a relayed payment is
booked as a transaction fee against the account it landed in. Nothing is billed to you afterwards:
the fee is always recovered from the payment itself or from your own service wallet.

## Offline paybill for customers who cannot get a prompt

Sometimes the M-Pesa prompt does not reach the customer (no network, the prompt times out, or
several failed attempts in a row). The **Offline paybill** switch on the Account tab adds an
**M-PESA Paybill** method to PayHero's checkout: the customer sees a paybill and an account
number and pays from their M-Pesa menu, and the payment is confirmed automatically when it
arrives.

The offline paybill is not available yet: it appears only after Codevertex has confirmed it with
a live payment, even if your switch is on. Until then customers who cannot get a prompt can try
again later or pay another way.

After several failed or cancelled prompts to the same phone, Treasury pauses further prompts for a
while, so nobody gets flooded with prompts.

## Payments in another currency

If you invoice in a different currency (for example USD) and the customer pays by M-Pesa, the
amount is converted at your stored exchange rate (Treasury, Currencies) and rounded up to whole
shillings. Your books still record the invoice's own currency and amount. If no exchange rate is
available, the payment is refused instead of charging the wrong amount.

## Moving money out of your PayHero wallet

Wallet balances (for example escrow commission or wallet payments) can be withdrawn from
**PayHero, Account, Withdraw**: choose the amount and one of your own channels or a phone number.
Your payout approval rules apply, so a withdrawal may need approval before it is sent. PayHero
takes its withdrawal charge from the wallet itself, not from the service wallet. Relayed payments
show in the same withdrawal history.

## Common issues

| What you see | Why | What to do |
|---|---|---|
| The POS or payment page shows no PayHero option | PayHero is on, but your PayHero account has not been created or linked yet | Finish Step 1, or ask Codevertex to link your account |
| The POS shows PayHero but no STK Push or C2B | STK Push and C2B are for an M-Pesa paybill or till connected directly through Safaricom | Use the PayHero button for M-Pesa |
| "Merchant has insufficient balance" | Payments go straight to your account and your PayHero service wallet is empty | Top it up in **Settings, Payments, PayHero, Wallet** (Top up the service wallet sends an M-Pesa prompt; the balance moves once it is paid) or on the PayHero dashboard, or choose "Let the system decide" or "Always relay" |
| The customer sees no Airtel Money option | Only M-PESA is offered until other methods are confirmed live | Take M-PESA, or another gateway |
| Payments arrive in the wrong till | Routing sends that payment type or outlet elsewhere | Check Channels and routing |
| A new paybill is missing | Channels have not synced yet | Click Sync channels, or wait up to 15 minutes |
| The customer did not receive the prompt | Network or phone issue | Check the number and send it again, or take another payment method |
| A payment made from a PayHero Payment Link does not appear | Dashboard Payment Links are not linked to an invoice or sale | Send customers your Treasury invoice link instead |
