# API Key Rotation — Specification

This sample deliberately mixes precise and ambiguous requirements so the linter
produces findings on its own sample data.

## Key Issuance

- The issuance service must generate a 32-byte key using a CSPRNG and return it exactly once.
  - Given a valid tenant, when POST /keys is called, then a 32-byte key is returned with status 201.
  - Given the same key, when GET /keys/{id} is called, then the secret is absent from the response.
- The issuance service must reject requests from tenants holding 10 or more active keys with status 429.
  - Given a tenant with 10 active keys, when POST /keys is called, then status 429 is returned.
- Keys must be fast to generate.
- The system should be user-friendly and secure.

## Rotation

- The rotation job must mark a key as pending-revocation 14 days before its expiry timestamp.
  - Given a key expiring in 14 days, when the rotation job runs, then its state is pending-revocation.
- The rotation job must send one notification per pending-revocation transition, at most once per key.
  - Given a key already notified, when the rotation job runs again, then no second notification is sent.
- Notifications should be delivered.
- It must handle several edge cases and/or retries appropriately.

## Revocation

- The revocation endpoint must invalidate a key within 5 seconds of the call returning 204.
  - Given a revoked key, when it is used within 5 seconds, then status 401 is returned.
- Audit records must be written for every revocation by the audit service.
  - Given a revocation, when the audit log is queried, then a record with actor and timestamp exists.
- Revoked keys must not be reissued. TBD whether reuse of the key ID is permitted.

## Non-Functional

- The rotation job must complete a 100,000-key sweep in under 90 seconds at p95.
  - Given 100,000 keys, when the sweep runs, then p95 wall time is under 90 seconds.
- The service should be scalable and performant under load.
