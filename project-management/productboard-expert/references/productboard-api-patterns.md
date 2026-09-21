# Productboard REST API Patterns

A practical catalog of API calls for common Productboard operations. The Productboard API is REST, JSON, and Bearer-token authenticated. All examples use `curl` and target **Public API v2**. They assume:

```bash
export PB_TOKEN="<personal-access-token>"
```

Authoritative reference: https://developer.productboard.com/ (append `.md` to any reference URL for a plain-markdown version, e.g. `https://developer.productboard.com/reference/createnote.md`).

## API version status (as of September 2026)

- **Public API v2 is the only supported version.** It became generally available on 2026-04-09, and the same changelog entry deprecated v1 ([changelog 2026-04-09](https://developer.productboard.com/changelog/2026-04-09)).
- **Public API v1 was scheduled to sunset on 2026-07-08**, after which v1 endpoints are no longer available. Any script still calling un-prefixed v1 paths (`/features`, `/notes/feature-links`, `/release-assignments`, `/hierarchy-entities/...`) with an `X-Version: 1` header must be migrated.
- Official migration guide: https://developer.productboard.com/reference/migration-guide

### v1 → v2 mapping at a glance

| v1 recipe | v2 replacement |
|---|---|
| `GET/POST /features`, `/components`, `/products`, `/releases`, `/objectives`, `/companies` | Unified `GET/POST /v2/entities` with `type` (`feature`, `component`, `product`, `release`, `releaseGroup`, `objective`, `keyResult`, `initiative`, `company`, `user`, ...) |
| `PATCH /features/{id}` | `PATCH /v2/entities/{id}` (`data.fields` or `data.patch`) |
| `POST /notes/feature-links` | `POST /v2/notes/{id}/relationships` (`type: "link"`) |
| `POST /release-assignments` | `POST /v2/entities/{featureId}/relationships` (`type: "link"`, target = release) |
| `POST /objectives/feature-links` | `POST /v2/entities/{featureId}/relationships` (`type: "link"`, target = objective) |
| `/hierarchy-entities/custom-fields` (definitions) | `GET /v2/entities/configurations/{type}` |
| `/hierarchy-entities/custom-fields-values` | Custom-field values are ordinary entity fields keyed by the field UUID, read/written through `/v2/entities/{id}` |
| `/customers` (v1 "customer"/user) | `POST /v2/entities` with `type: "user"` |
| `X-Version: 1` header | Not used in v2 — the version is in the path (`/v2/...`) |

### Not carried over to v2 (as of September 2026)

Per the migration guide's "Known Parity Gaps":

- **Removed permanently:** note followers (add/remove) and feedback forms (list/get configuration, submit).
- **Planned, not yet available:** company custom-field *definition* management (create/update/delete). Values on existing fields can still be read and written through the entity endpoints.
- **Notes search:** the migration guide still lists v1-style tag filtering (`anyTag` / `allTags`) as a remaining gap, although the `POST /v2/notes/search` reference example shows a `filter.fields.tag` array. Test tag filters against your workspace before relying on them; otherwise filter tags client-side. Full-text search (v1 `term`) is available via `data.search.query` on `POST /v2/notes/search`.
- **Notes responses no longer include** `followers[]`, `comments[]`, `totalResults`, or `features[].importance`.
- **No page-size control:** v1's `pageLimit` has no v2 equivalent — you cannot choose how many items a page returns.
- **Drivers / prioritization scores:** no Driver entity type is listed in the v2 entity types, and the recipes that read Driver scores are not mapped here. A beta *customer score* endpoint exists (`GET /v2/entities/{id}/score`, changelog 2026-07-20); treat anything Driver-related as UI-only until the reference documents it.

## Conventions

- Base URL: `https://api.productboard.com/v2`
- Required headers: `Authorization: Bearer $PB_TOKEN`, `Accept: application/json` (the docs state it is required on all requests), `Content-Type: application/json` for writes
- No `X-Version` header
- Pagination: cursor-based. List responses carry `links.next`; follow it until it is `null` or absent. The cursor is the `pageCursor` query parameter inside that link — treat it as opaque.
- Response envelope: reads return `{ "data": [...], "links": { "next": "..." } }` (lists) or `{ "data": { ... } }` (single item); **creates and updates return only a minimal reference** `{ "data": { "id", "type", "links": { "self" } } }` — follow `links.self` with a GET if you need the full record
- IDs are UUIDs. Entity and note responses also include `links.html` (deep link into the Productboard web UI, changelog 2026-04-30)
- Field control: `GET` list/retrieve endpoints accept `fields[]` (omit = only non-empty fields; `fields[]=all` = every configured field; or name specific fields)
- Rich-text fields (`description`, note `content`) take HTML strings — see the reference's Richtext page for allowed tags

```bash
PB="https://api.productboard.com/v2"
H=(-H "Authorization: Bearer $PB_TOKEN" -H "Accept: application/json")
```

## Authentication

### Personal access token

Generate a token in **Settings → Integrations → Public APIs → Access Token**. Per the docs, API tokens are available on the Pro plan and higher (as of September 2026 — check the pricing page). Treat as a secret; rotate periodically. Authentication is unchanged from v1.

```bash
curl -s "${H[@]}" "$PB/entities?type[]=feature"
```

### OAuth2

For multi-user or public integrations use OAuth 2.0. v2 documents four methods: API token, OAuth 2.0 authorization code, OAuth server-to-server (JWT), and OAuth for MCP clients (Dynamic Client Registration + PKCE). OAuth scopes follow the pattern `entities:read`, `write:entities`, `entities:delete`; PII fields (member emails, user names/emails) are returned as `[redacted]` without the `members:pii:read` / `users:pii:read` scopes.

## Discover your workspace schema first

v2 is configuration-driven: available fields (including custom fields, keyed by UUID), filters, and patch operations vary per workspace. Before scripting against a type, read its configuration.

```bash
# All entity types
curl -s "${H[@]}" "$PB/entities/configurations"

# One type (fields, custom-field UUIDs, supported filters)
curl -s "${H[@]}" "$PB/entities/configurations/feature"

# Note types
curl -s "${H[@]}" "$PB/notes/configurations"
```

## Features

### List Features

```bash
curl -s "${H[@]}" "$PB/entities?type[]=feature&fields[]=name&fields[]=status&fields[]=owner"
```

Response (abridged):

```json
{
  "data": [
    {
      "id": "3f1c2a9e-6b1d-4d0e-9a51-1b2c3d4e5f60",
      "type": "feature",
      "fields": {
        "name": "Shareable read-only dashboard view",
        "status": { "id": "447eb060-2a7e-4d1e-9d59-322a11e0fdb0", "name": "Planned" },
        "owner": { "id": "56caede9-bae0-4521-9702-d2c553488caf", "email": "pm@company.com" }
      },
      "relationships": [
        { "type": "parent", "target": { "id": "9b8c7d6e-...", "type": "component" } }
      ],
      "links": {
        "self": "https://api.productboard.com/v2/entities/3f1c2a9e-6b1d-4d0e-9a51-1b2c3d4e5f60",
        "html": "https://<workspace>.productboard.com/detail/..."
      },
      "createdAt": "2026-04-01T12:00:00Z",
      "updatedAt": "2026-05-20T15:30:00Z"
    }
  ],
  "links": { "next": "https://api.productboard.com/v2/entities?pageCursor=..." }
}
```

Useful list filters (check `filters` in the type's configuration for exact availability): `name`, `status[name]`, `status[id]`, `owner[email]`, `teams[name]`, `archived`, `parent[id]`, `metadata[source][system]`, `metadata[source][recordId]`. Multiple filters combine with AND only.

### Get a single Feature

```bash
curl -s "${H[@]}" "$PB/entities/3f1c2a9e-6b1d-4d0e-9a51-1b2c3d4e5f60?fields[]=all"
```

### Create a Feature

Features must have a parent (a component, or a feature for a subfeature). Set it through `relationships`:

```bash
curl -s -X POST "${H[@]}" -H "Content-Type: application/json" \
  -d '{
    "data": {
      "type": "feature",
      "fields": {
        "name": "Shareable read-only dashboard view",
        "description": "<p>Customers want to share dashboards with stakeholders who do not have an account. PDF export is a common workaround request; the underlying need is shareable links.</p>",
        "status": { "name": "New idea" },
        "owner": { "email": "pm@company.com" }
      },
      "relationships": [
        { "type": "parent", "target": { "id": "<component-uuid>" } }
      ]
    }
  }' \
  "$PB/entities"
```

The response contains only `id`, `type`, and `links.self`.

### Update a Feature

Simple replacement via `fields`:

```bash
curl -s -X PATCH "${H[@]}" -H "Content-Type: application/json" \
  -d '{ "data": { "fields": { "status": { "name": "Planned" } } } }' \
  "$PB/entities/3f1c2a9e-6b1d-4d0e-9a51-1b2c3d4e5f60"
```

Granular changes via `patch` (ops: `set`, `addItems`, `removeItems`, `clear`):

```bash
curl -s -X PATCH "${H[@]}" -H "Content-Type: application/json" \
  -d '{
    "data": {
      "patch": [
        { "op": "addItems", "path": "tags", "value": [ { "name": "enterprise" } ] },
        { "op": "clear", "path": "timeframe.startDate" }
      ]
    }
  }' \
  "$PB/entities/3f1c2a9e-6b1d-4d0e-9a51-1b2c3d4e5f60"
```

### Archive a Feature

```bash
curl -s -X PATCH "${H[@]}" -H "Content-Type: application/json" \
  -d '{ "data": { "fields": { "archived": true } } }' \
  "$PB/entities/3f1c2a9e-6b1d-4d0e-9a51-1b2c3d4e5f60"
```

### Move a Feature to another Component

```bash
curl -s -X PUT "${H[@]}" -H "Content-Type: application/json" \
  -d '{ "data": { "target": { "id": "<new-component-uuid>" } } }' \
  "$PB/entities/3f1c2a9e-6b1d-4d0e-9a51-1b2c3d4e5f60/relationships/parent"
```

### Delete — cascade warning

`DELETE /v2/entities/{id}` **cascades** in v2: deleting a feature removes its subfeatures, and deleting a release group removes its releases (v1 blocked these deletes). Check children first with `GET /v2/entities/{id}/relationships?type=child` and require explicit confirmation in your own tooling. Prefer archiving.

## Components

### List Components

```bash
curl -s "${H[@]}" "$PB/entities?type[]=component"
```

### Create a Component

```bash
curl -s -X POST "${H[@]}" -H "Content-Type: application/json" \
  -d '{
    "data": {
      "type": "component",
      "fields": {
        "name": "Reporting",
        "description": "<p>Dashboards, reports, exports</p>"
      },
      "relationships": [
        { "type": "parent", "target": { "id": "<product-uuid>" } }
      ]
    }
  }' \
  "$PB/entities"
```

## Insights (Notes)

In the API, customer feedback items are **notes** (`textNote`, `conversationNote`, and `opportunityNote` — the last is read-only via API). Linking a note to a feature is what creates an "insight" in the UI.

### List recent Notes

```bash
curl -s "${H[@]}" "$PB/notes?createdFrom=2026-09-01T00:00:00Z&fields[]=name&fields[]=tags&fields[]=processed"
```

Other list filters: `archived`, `processed`, `type[]`, `owner[email]`, `creator[email]`, `metadata[source][system]`, `metadata[source][recordId]`, `createdFrom/To`, `updatedFrom/To`.

### Create a Note (Insight)

```bash
curl -s -X POST "${H[@]}" -H "Content-Type: application/json" \
  -d '{
    "data": {
      "type": "textNote",
      "fields": {
        "name": "Acme Corp wants PDF export for board pack",
        "content": "On QBR call, CFO at Acme Corp asked for a way to share dashboards with their board. PDF export was mentioned as a workaround they would accept.",
        "tags": [ { "name": "enterprise" }, { "name": "reporting" }, { "name": "qbr" } ]
      },
      "metadata": {
        "source": { "system": "Salesforce", "recordId": "opp-12345" }
      },
      "relationships": [
        { "type": "customer", "target": { "type": "user", "email": "cfo@acme.com" } }
      ]
    }
  }' \
  "$PB/notes"
```

**Behaviour change from v1:** v2 does not auto-create users or companies. If `cfo@acme.com` does not exist the call returns **404**. Create the user (below) — its company is created automatically if needed — then retry.

### Link a Note to a Feature

```bash
curl -s -X POST "${H[@]}" -H "Content-Type: application/json" \
  -d '{
    "data": {
      "type": "link",
      "target": { "id": "3f1c2a9e-6b1d-4d0e-9a51-1b2c3d4e5f60", "type": "link" }
    }
  }' \
  "$PB/notes/<note-uuid>/relationships"
```

A note has at most **one** customer relationship (replace it with `PUT /v2/notes/{id}/relationships/customer`) and any number of `link` relationships. List them with `GET /v2/notes/{id}/relationships`.

### Get all Insights linked to a Feature

```bash
curl -s -X POST "${H[@]}" -H "Content-Type: application/json" \
  -d '{
    "data": {
      "filter": {
        "relationships": { "link": [ { "id": "3f1c2a9e-6b1d-4d0e-9a51-1b2c3d4e5f60" } ] }
      },
      "return": { "fields": [ "name", "content", "tags" ] }
    }
  }' \
  "$PB/notes/search"
```

Full-text search: add `"search": { "query": "board pack" }` inside `data`.

## Customers and Companies

In v2, companies and users (v1 "customers") are entity types.

### List Companies

```bash
curl -s "${H[@]}" "$PB/entities?type[]=company"
```

### Create a Company

```bash
curl -s -X POST "${H[@]}" -H "Content-Type: application/json" \
  -d '{
    "data": {
      "type": "company",
      "fields": {
        "name": "Acme Corp",
        "domain": "acme.com",
        "<mrr-custom-field-uuid>": 40000
      },
      "metadata": {
        "source": { "system": "Salesforce", "recordId": "sf-acct-001234" }
      }
    }
  }' \
  "$PB/entities"
```

Custom fields are addressed by UUID (get them from `GET /v2/entities/configurations/company`). Creating new company field *definitions* is not available in v2 as of September 2026 — create the field in the UI first.

### Create a User (v1 "Customer")

```bash
curl -s -X POST "${H[@]}" -H "Content-Type: application/json" \
  -d '{
    "data": {
      "type": "user",
      "fields": { "name": "Dana Lee", "email": "cfo@acme.com" },
      "relationships": [
        { "type": "parent", "target": { "id": "<company-uuid>" } }
      ],
      "metadata": { "source": { "system": "Salesforce", "recordId": "sf-contact-9876" } }
    }
  }' \
  "$PB/entities"
```

## Releases

### List Releases

```bash
curl -s "${H[@]}" "$PB/entities?type[]=release"
```

### Create a Release

```bash
curl -s -X POST "${H[@]}" -H "Content-Type: application/json" \
  -d '{
    "data": {
      "type": "release",
      "fields": {
        "name": "Q3 2026 Launch",
        "timeframe": { "startDate": "2026-07-01", "endDate": "2026-09-30", "granularity": "quarter" }
      },
      "relationships": [
        { "type": "parent", "target": { "id": "<release-group-uuid>" } }
      ]
    }
  }' \
  "$PB/entities"
```

### Assign a Feature to a Release

v1's `/release-assignments` resource (with its `state`) is replaced by a `link` relationship between the feature and the release:

```bash
curl -s -X POST "${H[@]}" -H "Content-Type: application/json" \
  -d '{ "data": { "type": "link", "target": { "id": "<release-uuid>" } } }' \
  "$PB/entities/3f1c2a9e-6b1d-4d0e-9a51-1b2c3d4e5f60/relationships"
```

v1's per-assignment `state` (e.g. `planned`) has no documented v2 equivalent on the relationship — track delivery state on the feature's `status` instead.

### List Features assigned to a Release

```bash
curl -s "${H[@]}" "$PB/entities/<release-uuid>/relationships?type=link&target[type]=feature"
```

## Drivers (Objectives and Key Results)

Objectives, key results, and initiatives are entity types in v2 (`objective`, `keyResult`, `initiative`). Driver-based prioritization scores are **not** mapped here — see "Not carried over to v2" above.

### List Objectives

```bash
curl -s "${H[@]}" "$PB/entities?type[]=objective"
```

### Link a Feature to an Objective

```bash
curl -s -X POST "${H[@]}" -H "Content-Type: application/json" \
  -d '{ "data": { "type": "link", "target": { "id": "<objective-uuid>" } } }' \
  "$PB/entities/3f1c2a9e-6b1d-4d0e-9a51-1b2c3d4e5f60/relationships"
```

Key-result `progress` in v2 returns only `startValue`, `targetValue`, `currentValue` — the server-computed percentage from v1 is gone. Compute it yourself: `(current - start) / (target - start) * 100`, guarding against `target == start`.

## Custom Fields

### List custom-field definitions

```bash
curl -s "${H[@]}" "$PB/entities/configurations/feature"
```

Custom fields appear in the configuration keyed by UUID with their type (number, text, single/multi select, tags, date, ...). For select-type fields, allowed options are listed with `GET /v2/entities/fields/{id}/values` ("List field values"; supports a `query` parameter for TAG fields since changelog 2026-09-09).

### Get a custom-field value

```bash
curl -s "${H[@]}" "$PB/entities/3f1c2a9e-6b1d-4d0e-9a51-1b2c3d4e5f60?fields[]=<tshirt-field-uuid>"
```

### Set a custom-field value

```bash
curl -s -X PATCH "${H[@]}" -H "Content-Type: application/json" \
  -d '{ "data": { "fields": { "<tshirt-field-uuid>": { "name": "L" } } } }' \
  "$PB/entities/3f1c2a9e-6b1d-4d0e-9a51-1b2c3d4e5f60"
```

Single-select values are assigned by `{ "name": ... }` or `{ "id": ... }`; number/text fields take the raw value; `null` clears.

## Webhooks

### Subscribe to events

```bash
curl -s -X POST "${H[@]}" -H "Content-Type: application/json" \
  -d '{
    "data": {
      "fields": {
        "name": "PM automation",
        "events": [
          { "eventType": "feature.created" },
          { "eventType": "feature.updated" },
          { "eventType": "note.created" },
          { "eventType": "feature-release-assignment.updated" }
        ],
        "notification": {
          "url": "https://your-app.example.com/webhooks/productboard",
          "version": 1,
          "headers": { "authorization": "Bearer <shared-secret>" }
        }
      }
    }
  }' \
  "$PB/webhooks"
```

The notification URL must be public HTTPS (no localhost/private addresses). Productboard sends the `headers.authorization` value on every notification — check it in your handler to authenticate the call.

### Sample webhook payload

```json
{
  "data": {
    "id": "3f1c2a9e-6b1d-4d0e-9a51-1b2c3d4e5f60",
    "eventType": "feature.updated",
    "updatedAttributes": ["status"],
    "links": {
      "target": "https://api.productboard.com/v2/entities/3f1c2a9e-6b1d-4d0e-9a51-1b2c3d4e5f60"
    }
  }
}
```

The payload references the affected record; fetch the full entity via a follow-up GET. `id` is absent for `feature-release-assignment.updated` and `hierarchy-entity.custom-field-value.updated`. Manage subscriptions with `GET /v2/webhooks`, `GET /v2/webhooks/{id}`, `DELETE /v2/webhooks/{id}`.

## Common bulk-operation patterns

### Backfill Insights from a CSV

Bulk-create Notes from an exported CSV (e.g. 2 years of support tickets at onboarding). Users must already exist in v2 — pre-create them or handle the 404:

```bash
while IFS=, read -r title content source record customer; do
  curl -s -X POST "${H[@]}" -H "Content-Type: application/json" \
    -d "$(jq -n --arg t "$title" --arg c "$content" --arg s "$source" --arg r "$record" --arg ce "$customer" '{
      data: {
        type: "textNote",
        fields: { name: $t, content: $c },
        metadata: { source: { system: $s, recordId: $r } },
        relationships: [ { type: "customer", target: { type: "user", email: $ce } } ]
      }
    }')" \
    "$PB/notes"
  sleep 0.1    # stay well under the per-token rate limit
done < insights.csv
```

### Snapshot Features weekly

Snapshot the Feature list every Monday for trend analysis (all pages):

```bash
DATE=$(date +%Y-%m-%d)
url="$PB/entities?type[]=feature&fields[]=name&fields[]=status"
while [ -n "$url" ] && [ "$url" != "null" ]; do
  page=$(curl -s "${H[@]}" "$url")
  echo "$page" | jq -c '.data[] | {id, name: .fields.name, status: .fields.status.name, updatedAt}'
  url=$(echo "$page" | jq -r '.links.next // empty')
done > "snapshots/features-$DATE.jsonl"
```

### Reconcile with Jira

Find Features marked "Done" in Productboard but missing from Jira's released-version list:

```bash
# Pseudocode:
# 1. List Productboard Features with status[name]=Done, updated in the last 30 days
# 2. For each Feature, read its Jira connection via the Jira Integrations API
#    (GET /v2/jira-integrations/{integrationId}/connections — can also look up by Jira issue key)
# 3. Check the Jira issue status via Jira API
# 4. Flag mismatches
```

The detail is environment-specific; the pattern is to use Productboard as the source of truth for "what should have shipped" and Jira/Linear for "what did ship".

## Rate-limit handling

The documented default limit is **50 requests per second per access token** (as of September 2026; unchanged from v1). Responses carry `X-RateLimit-Limit` and `X-RateLimit-Remaining`; a `429 Too Many Requests` includes `Retry-After` (seconds). A robust client honors it:

```bash
api_call() {
  local response code body wait
  while true; do
    response=$(curl -s -D /tmp/pb_headers -w "\n%{http_code}" "$@")
    code=$(tail -n1 <<<"$response")
    body=$(sed '$d' <<<"$response")
    if [ "$code" = "429" ]; then
      wait=$(awk 'tolower($1)=="retry-after:" {print $2+0}' /tmp/pb_headers)
      sleep "${wait:-2}"
      continue
    fi
    echo "$body"
    return
  done
}
```

For Python clients, wrap `urllib.request` calls in an exponential-backoff loop that reads `Retry-After`.

## Pagination

Always paginate. Skipping pagination yields silently-truncated data. Follow `links.next` until it is `null`/absent; you cannot set a page size in v2.

```bash
url="$PB/entities?type[]=feature"
while [ -n "$url" ] && [ "$url" != "null" ]; do
  response=$(curl -s "${H[@]}" "$url")
  echo "$response" | jq -c '.data[]'
  url=$(echo "$response" | jq -r '.links.next // empty')
done
```

## Idempotency

There is no idempotency-key header. For bulk creates that may retry, stamp each record with `metadata.source.system` + `metadata.source.recordId` (e.g. the Salesforce opportunity ID) and check existence first with the `metadata[source][system]` / `metadata[source][recordId]` list filters on `/v2/entities` or `/v2/notes`.

## API versioning

v2 is versioned in the path (`/v2/...`); the `X-Version` header is not needed. v2 evolves additively through the changelog (https://developer.productboard.com/changelog) — e.g. 2026-04-30 removed legacy flat properties from the `POST /v2/entities/search` body in favour of structured `filter` / `return` objects. Review the changelog before relying on beta endpoints (those gated by the `Pb-Beta` header or marked Beta).

## Caveats

- API tokens require the Pro plan or higher (as of September 2026). Confirm your workspace's plan before scripting.
- Permission semantics: a Personal Access Token inherits the user's permissions. A token from an Admin can do everything; a token from a Contributor cannot create Features in restricted Components.
- Driver weighted scores are not exposed by the v2 reference as of September 2026; scores are managed in the UI.
- v2 has an MCP server (Beta) for agent clients; see the "MCP Server (Beta)" pages in the reference.

## Further reading

- Productboard Developer Docs — https://developer.productboard.com/
- Migrating from v1 to v2 — https://developer.productboard.com/reference/migration-guide
- API changelog — https://developer.productboard.com/changelog
- Productboard Help Center — https://support.productboard.com/
