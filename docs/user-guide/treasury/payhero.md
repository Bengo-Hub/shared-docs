# Accepting payments with PayHero

PayHero lets your customers pay you by M-Pesa straight into your own paybill, till or bank
account, and, outside Kenya, by MTN, Airtel and other mobile money networks, by card, or by bank
deposit. Payments taken at your POS, from invoices and from online orders all settle into the
channels you choose, and land in the right account in your books automatically.

This page is for business owners and finance admins. Developers integrating with the API should
read the [PayHero Integration Reference](../../integrations/payhero-integration-reference.md).

## Before you start

- You need to be an admin with permission to manage payment gateways in Treasury.
- Have your paybill, till or bank account details ready. PayHero adds these on its own dashboard,
  not in Treasury.
- For M-Pesa prompts to go through, your PayHero **service wallet** must have some credit. PayHero
  charges its fees from it, and with an empty wallet it refuses payments.

## Step 1: Turn PayHero on and get your account

Go to **Treasury, Settings, Payments, PayHero, Account** and switch PayHero on. Pick how you want
to use it:

| Option | When to choose it |
|---|---|
| **Your own PayHero account under Codevertex** (recommended) | You get your own PayHero wallet, kept separate from every other business. Needed for escrow and wallet payments. |
| **Shared platform account** | You only want payments to go into specific paybills or tills you claim. No wallet of your own. |
| **Your existing PayHero account** | You already have a PayHero account and API key. Your key is stored encrypted. |

With the recommended option, click **Create account**. Your business name, email and phone are
filled in from your company profile. If your PayHero account was already created on the PayHero
dashboard, choose **Link existing account** and enter its account id instead.

Also set your **country** here. It decides which payment methods your customers see (for example
M-Pesa in Kenya, MTN and Airtel in Uganda) and how phone numbers are read.

> If Treasury says your organization's plan cannot create accounts, ask the Codevertex team to
> set it up for you, or use one of the other two options in the meantime.

## Step 2: Add your paybills, tills and bank accounts

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

To collect money from the public into your PayHero wallet, PayHero requires verification: your
national ID and your company's KRA PIN. Open **Verification**, check the price of each check (PayHero
charges per check) and confirm to run it. Treasury keeps only the result, never the numbers you
enter. Your verification level is refreshed daily.

## Step 5: Choose what your customers see

In **Settings, Payments, Gateways**, make sure PayHero is switched on and, if you also use
another M-Pesa provider, choose which one is primary. Your POS and your invoice payment page then
show the PayHero methods available in your country.

## What your customer sees when they pay

1. They open your payment link (or **Pay Now** on an invoice) and see the methods your account
   accepts in their country.
2. They choose M-Pesa and type their phone number. The page says **Check your phone** and waits.
3. M-Pesa sends a prompt to their phone. For a bank paybill it names the bank's paybill and your
   account number there; they enter their PIN.
4. The money goes straight into the channel you routed that payment to. PayHero tells treasury,
   treasury confirms the payment with PayHero, and the invoice or sale is marked paid. The page
   updates on its own.

If the prompt never arrives, they can use the offline paybill below instead.

## Offline paybill for customers who cannot get a prompt

Sometimes the M-Pesa prompt does not reach the customer (no network, the prompt times out, or
several failed attempts in a row). Turn on **Offline paybill** on the Account tab and the payment
page will also offer **M-Pesa Paybill**: the customer sees a paybill and an account number and
pays from their M-Pesa menu. The payment is confirmed automatically when it arrives.

After several failed or cancelled prompts to the same phone, Treasury pauses further prompts for a
while and points the customer to the offline paybill, so nobody gets flooded with prompts.

## Payments in another currency

If you invoice in a different currency (for example USD) and the customer pays by M-Pesa, the
amount is converted at your stored exchange rate (Treasury, Currencies) and rounded up to whole
shillings. Your books still record the invoice's own currency and amount. If no exchange rate is
available, the payment is refused instead of charging the wrong amount.

## Moving money out of your PayHero wallet

Wallet balances (for example escrow commission or wallet payments) can be withdrawn from
**PayHero, Account, Withdraw**: choose the amount and one of your own channels or a phone number.
Your payout approval rules apply, so a withdrawal may need approval before it is sent. PayHero's
own fees come from the service wallet, which you top up on the PayHero dashboard.

## Common issues

| What you see | Why | What to do |
|---|---|---|
| The POS or payment page shows no M-Pesa option | PayHero is on, but your PayHero account has not been created or linked yet | Finish Step 1, or ask Codevertex to link your account |
| "Merchant has insufficient balance" | Your PayHero service wallet is empty | Top it up on the PayHero dashboard |
| Payments arrive in the wrong till | Routing sends that payment type or outlet elsewhere | Check Channels and routing |
| A new paybill is missing | Channels have not synced yet | Click Sync channels, or wait up to 15 minutes |
| The customer did not receive the prompt | Network or phone issue | Ask them to use the M-Pesa Paybill option |
| A payment made from a PayHero Payment Link does not appear | Dashboard Payment Links are not linked to an invoice or sale | Send customers your Treasury invoice link instead |
