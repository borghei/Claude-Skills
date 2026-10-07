# Protocols, RPC, and Messaging Companion

Tier: full.

## Select this companion when

Components talk to each other through something other than plain
request-response HTTP handled by a framework: gRPC and other RPC systems,
schema-based serialization, hand-written wire protocols, message queues and
brokers, publish-subscribe topics, webhooks, and long-lived or streaming
connections.

These paths often sit "inside" the network and inherit less scrutiny than
public endpoints, while carrying the same authority.

## Ground rules

```text
- Every message has a producer, a channel, and a consumer. Establish who can
  act as the producer and what the consumer assumes about it.
- A channel being internal is a deployment fact, not a control visible in
  source. If safety rests on network placement or broker access rules that
  are not in the repository, the lead is needs_validation.
- Identity carried inside a message is a claim. Identity established by the
  channel is evidence. Find where the code confuses them.
- Delivery is at-least-once, unordered, and delayed unless the source proves
  otherwise. Ask what happens on duplicate, reordered, and stale messages.
- Reproduce with an in-process or loopback fixture: a fake producer, the real
  consumer code, dummy tenants. Never publish to or read from a shared broker.
```

## Hunting classes

### Message boundary and canonical form disagreement

Two parties parse the same bytes differently: length prefixes versus
delimiters, duplicate fields, unknown fields kept or dropped, different
canonical encodings of the same value, a signature computed over one form and
a decision made on another.

### Union, enum, and default handling

Unset fields that default to a permissive value, unknown enum values mapped
to a privileged or pass-through case, one-of fields where two alternatives
can both be populated, and version skew between producer and consumer
schemas.

### Envelope and payload identity mismatch

Routing, tenant, or sender information appears in both the envelope and the
body, and the authorization check reads one while the handler acts on the
other.

### Interceptor and method coverage gaps

Authentication or authorization applied by middleware that does not cover
every method: newly added methods, streaming variants, reflection and health
services, a second server instance registered without the interceptor.

### Peer identity mapped to application principal

A transport-level identity — a service certificate, a connection credential —
is treated as permission to act for any user the message names. Check whether
the callee validates that this peer may speak for that principal.

### Per-item and streaming authorization

Authorization done once at stream open or batch start and not for each item,
resource, or subscription change that follows; long-lived streams that
outlast a revoked permission.

### Callback and reply correlation

Replies matched to requests by a guessable or reusable identifier, reply
destinations chosen by the requester without restriction, and callbacks
delivered to an address the sender supplied.

### Topic and subscription scope

Tenants or roles able to subscribe to, or publish on, topics beyond their
own: wildcard subscriptions, topic names built from caller input, shared
consumer groups, per-tenant data on a common topic with filtering left to the
consumer.

### Dead-letter, retry, and diagnostic leakage

Failed messages, with their full payloads, parked where a wider audience can
read them, or replayed later under different authorization. Includes
diagnostic and tracing topics.

### Producer treated as control plane

Consumers that execute commands, change configuration, or grant access based
on a message, on a channel where less-trusted producers can also publish.

### Duplicate delivery and idempotency

Handlers that apply an effect each time a message arrives: payments,
grants, counters, notifications. Check for a deduplication key, where it is
stored, and whether it is chosen by the sender.

### Stale and out-of-order messages

An older message applied after a newer one, undoing a revocation or restoring
a previous state; missing version or sequence checks; timestamps trusted from
the producer.

### Acknowledge and commit ordering

A message acknowledged before its effect is durable, or an effect committed
without the acknowledgment, so a crash loses or repeats a security-relevant
step.

### Partial fan-out transitions

One event consumed by several services, where some apply the change and
others fail, leaving access granted in one place and revoked in another.

## Cross-cutting moves

- For each channel, write who can produce, who can consume, and what the code
  — not the network — enforces about each.
- Send the consumer a message its own producer would never send: extra
  fields, missing fields, wrong tenant, unknown type.
- Deliver every message twice, then in reverse order.
- Check webhook receivers for signature verification, replay windows, and
  which bytes the signature covers.
- Compare the public API's checks with those on the internal RPC that does
  the same thing.

## Evidence bar

- Confirmed needs a local fixture run: the crafted message, the consumer's
  code path, and the wrong effect on a dummy tenant or resource.
- Whether a lower-trust actor can actually publish to the channel is often a
  broker or network fact. If it is not in the repository, record
  `needs_validation` with an owner check for the exact access rule.
- Missing encryption or authentication on a channel that the source shows to
  be loopback-only is a hardening note.
- Severity follows the consumer's authority: a message that grants access or
  moves value is high; a duplicated notification is low.
