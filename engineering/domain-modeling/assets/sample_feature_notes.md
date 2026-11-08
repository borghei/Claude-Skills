# Feature notes: annual prepay

When a client switches to annual prepay, we create a new membership for the
remaining term and issue a single bill for the full year.

Edge cases from the sales call:
- Clients on a legacy tier keep their price for 12 months.
- If the buyer cancels mid-year we do not refund; churn is recorded at period end.

```ts
export function prepayAnnual(clientId: string, tierCode: string) {
  const membership = memberships.renew(clientId, { months: 12 });
  return billFor(membership);
}
```
