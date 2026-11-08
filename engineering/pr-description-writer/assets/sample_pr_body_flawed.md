## Summary

This PR refactors the customer model to support split names, updates the serializers, adjusts the API schema, adds a migration, and also cleans up some old code in the views that was not being used anymore, plus some test updates and a changelog entry.

## Why

BILL-412

## Evidence

Tested it and it works fine now. Here is the log from my run:

    curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0In0.abc123def456ghi789" https://staging.example.com/api/customers

## How to verify

Tested locally.

## Merge risk

Low risk, fully reversible. <!-- describe rollback -->
