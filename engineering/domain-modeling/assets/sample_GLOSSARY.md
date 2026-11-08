# Glossary — Subscription Billing

The language of the billing context: how customers subscribe, are charged and leave.
Canonical terms are the headings; anything under **Avoid** should not appear in
new docs, tickets or identifiers.

## Customers

### Customer
**Definition:** A person or organisation that holds at least one Subscription and receives Invoices.
**Avoid:** Client, Account, Buyer
**Owner:** Billing product lead
**Related:** Subscription, Invoice
**Status:** agreed

### Account
**Definition:** The login identity a person uses to reach the self-service portal.
**Avoid:** User profile
**Owner:** Identity team
**Status:** agreed

## Subscriptions

### Subscription
**Definition:** A Customer's ongoing agreement to pay for a Plan on a recurring schedule until it is cancelled.
**Avoid:** Membership, Contract, Purchase
**Owner:** Billing product lead
**Related:** Plan, Customer, Cancellation
**Status:** agreed

### Plan
**Definition:** A priced offer with a fixed billing interval and a set of included features.
**Avoid:** Tier, Package
**Owner:** Pricing manager
**Status:** agreed

### Seat
**Definition:** A seat is one named person allowed to use a Subscription.
**Avoid:** License
**Owner:** Billing product lead
**Status:** agreed

### Trial
**Definition:** A period at the start of a Subscription during which no Charge is made.
**Avoid:** Free period
**Owner:** Growth team
**Status:** draft

### Cancellation
**Definition:** The Customer's instruction to end a Subscription at the close of the current billing period.
**Avoid:** Churn, Termination
**Owner:** Billing product lead
**Related:** Subscription, Refund
**Status:** agreed

### Downgrade
**Definition:** A move from one Plan to a cheaper Plan, effective at the next renewal.
**Avoid:** Churn, Plan change
**Owner:** Pricing manager
**Status:** agreed

## Money

### Invoice
**Definition:** A request for payment covering one billing period of one Subscription.
**Avoid:** Bill, Statement
**Status:** agreed

### Charge
**Definition:** A row in the payments table with a boolean captured flag, written by the charges endpoint when the gateway responds. It is retried three times. It may be partial. It references an Invoice.
**Avoid:** Payment, Transaction
**Owner:** Payments engineering
**Status:** agreed

### Plan
**Definition:** The pricing level a customer picked.
**Owner:** Sales
**Status:** agreed
