## Summary

Split `customers.full_name` into `given_name` and `family_name` (expand phase only). The API returns all three fields; nothing reads the new columns yet.

```diff
 Customer
   id
   full_name        # still written and returned
+  given_name       # new, nullable, backfilled
+  family_name      # new, nullable, backfilled
```

## Why

Invoices for customers in Hungary and Japan print names in the wrong order because we guess the split at render time. Billing asked for stored, editable name parts (BILL-412). This PR adds the columns and backfills them; switching reads happens in a follow-up.

## Evidence

**Before:** invoice preview for customer `c_8812` renders "Tanaka Yuki" as "Yuki Tanaka".
**After:** the backfill stores `given_name=Yuki`, `family_name=Tanaka`; the preview is unchanged because reads still use `full_name`.

```text
$ pytest tests/customers/test_name_split.py -q
........                                                   [100%]
8 passed in 0.41s

$ python manage.py migrate --plan
db/migrations/20261102_split_customer_name  (add 2 nullable columns, backfill 41,203 rows in batches of 5,000)
```

Staging run: https://ci.example.com/actions/runs/88123 (migration 38 s, no lock waits over 200 ms).

## How to verify

1. `make db-reset && python manage.py migrate` on a local database seeded with `make seed-customers`.
2. `psql -c "select count(*) from customers where given_name is null and full_name <> ''"` returns 0.
3. `curl -s localhost:8000/api/customers/c_8812 | jq '.given_name, .family_name, .full_name'` prints all three.
4. Run the suite: `pytest tests/customers -q`.

## Merge risk

**Classification:** One-way door. The migration adds and backfills columns; reverting the code leaves the columns in place.
**Blast radius:** the `customers` table (41k rows) and the public `Customer` schema in `api/openapi.yaml`. Clients ignoring unknown fields are unaffected.

**Rollback plan:** the columns are additive and nullable, so the safe rollback is to revert the application code and leave the schema; nothing reads the new columns yet. If the backfill itself misbehaves, the on-call engineer runs `python manage.py migrate customers 0047` (down-migration drops both columns, about 2 s on staging). `full_name` is never modified, so no data is lost either way.
