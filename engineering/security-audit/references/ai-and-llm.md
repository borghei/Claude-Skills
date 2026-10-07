# AI, LLM, and Agent Companion

Tier: focused, full.

## Select this companion when

A language model takes part in a decision that matters: an assistant or
chatbot, retrieval-augmented generation, persistent agent memory, a
tool-calling loop, an MCP server or client, code that builds prompts from
text someone else wrote, or code that acts on what a model returns.

The flow to follow is: content an attacker can write, into a model's context
or memory, out to a capability, an authority, or a sink. Ordinary boundaries
around that flow — transport, per-object access, query building, rendering —
stay with the core classes. On a large target, give each stage of that flow
its own units.

## Ground rules

```text
- "The model can be talked into it" is not a finding. Point to the code that
  let untrusted content reach another principal's context, use authority the
  requester lacks, disclose data they cannot read, or drive a sink they cannot
  reach themselves.
- Treat model output, memory entries, tool descriptions, and tool results as
  untrusted input. The defect is in the code that trusts them.
- Instructions in a system prompt are not a control. Only deterministic checks
  count: authorization on the named resource, isolation of context, binding of
  an approval to an action, credentials with limited reach.
- Name the attacker, the affected principal, the identity the action runs as,
  the resource, the exact action, and the visible result.
- A user asking the agent to do what that user may already do is intended
  behaviour, however the request is phrased.
- Authorization and intent are different controls. An action that is
  permitted for the victim but that the victim never asked for is a binding
  failure when attacker-written content caused it.
- Use local fixtures and a stubbed or recorded model response. Do not call a
  paid or hosted model API to demonstrate a defect.
```

## Hunting classes

### Indirect injection through retrieved content

Someone can write a document, page, email, ticket, file, or tool result that
later enters a different principal's context. For each source, establish its
authors, the filter applied when it is fetched, the session that ends up
reading it, and the powers that session holds. The defect is the missing isolation or the missing binding between
the content and the reader's intent.

### Context shared across sessions or tenants

Conversation state, vector stores, fetched passages, or cached prompts keyed
more broadly than the principal. Check that tenant and access filters are part of the
query and of every cache key, on every path including batch and background
jobs. A tenant field stored on the object but absent from the query is not
enforcement.

### Memory poisoning

Attacker-influenced content or a model's own summary is written to long-lived
memory and later shapes another task or another user's session. Review who can
create, update, merge, and delete memory, how its origin is recorded, and
whether a low-trust observation can be stored as a standing instruction.

### Role and provenance spoofing in prompt assembly

Untrusted text can pass as a system message, an earlier turn, a tool result,
or a policy because the prompt is built by concatenation, history is untyped,
the caller supplies a role field, or a serialization round trip drops the
source label. Confirm the forged origin changes a decision made in code or
unlocks a capability.

### Tool arguments reaching a sink

Model-produced arguments flow into a query, a shell, a file path, a URL fetch,
or a privileged API with no validation in the handler. Treat the tool schema
as a parser: it constrains shape, not safety. Trace each argument from the
decoded call to the sink exactly as for any other untrusted input.

### Agent acting beyond the requester's authority

The agent runs with a service identity or broad credential, and the tool
handler does not check whether the requesting user may perform that operation
on that resource. Compare with what the same user can do through the normal
product interface.

### Approval not bound to the action

A confirmation step exists, but what the human approved is not what executes:
arguments change after approval, approval is reusable, a summary differs from
the real call, or one approval covers a batch the user did not see.

### Tool schema and dispatcher mismatch

The dispatcher resolves tool names loosely, accepts fields the schema does
not declare, coerces types, or routes to a handler other than the one the
policy checked. Compare the declared schema, the validation code, and the
handler signature.

### Runaway action loops

A model-driven loop with no bound on steps, spend, recursion, or fan-out, where
attacker content can keep it going at the operator's cost or against a shared
resource.

### Inherited trust in sub-agents and connected servers

A sub-agent or connected server receives the parent's full context,
credentials, or tool set when the task needs a fraction, or its output is
merged back as trusted. Trace what crosses the boundary in each direction.

### MCP server and tool identity

Tools from different servers share a name space; a server can shadow or
redefine a tool, change its definition after approval, or be reached at an
address the user did not vet. Check how identity is pinned and re-verified.

### Tool metadata treated as policy

Descriptions, annotations, or schema text supplied by a tool provider decide
what is safe, what needs approval, or what the agent may read. Metadata from a
party you do not control is input.

### Unsafe rendering of model output

Model text rendered as HTML or rich markup, turned into links or images that
load automatically, or executed by a client, giving attacker content a path
to script execution or to leaking context through a requested URL.

### Extraction of hidden context

System prompts, other users' data, retrieved documents, or credentials placed
in context can be read back by a user who should not see them. This matters
when the context holds something that user cannot otherwise obtain; a system
prompt alone is rarely a secret worth a finding.

## Cross-cutting moves

- Draw the path as writer, store, retriever, context, model, dispatcher,
  handler, sink. Ask who controls each arrow.
- For every tool, answer: whose identity runs it, who is checked, and on
  which resource.
- Look for the second consumer: the same content read by a more privileged
  agent, a scheduled job, or an admin view.
- Check what persists after the conversation: memory, caches, logs,
  generated files.
- Replace the model with a stub returning attacker-chosen output. If the
  system is unsafe under that stub, the defect is in the code.

## Evidence bar

- Confirmed needs a deterministic local reproduction: a fixture document or a
  stubbed model response, the resulting tool call or output, and the affected
  dummy principal.
- A defect that depends on how a particular hosted model responds is
  `needs_validation`; state the response shape that would trigger it.
- Prompt wording, missing guard prompts, and jailbreak susceptibility are not
  findings without a code-level boundary failure.
- Severity follows the action reached and the data exposed, not the fact that
  injection was possible.
