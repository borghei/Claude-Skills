# Feedback Triage Tool Reference

> Read this when you need the `feedback_triage.py` flags, the input JSON schema, or the output schemas (JSON / Markdown / Mermaid / Confluence / Notion / Linear).

## feedback_triage.py

Ingest a JSON queue of inbound feedback. Produce deduplicated clusters, Kano categorization, priority scores, and suggested response templates.

| Flag | Type | Default | Description |
|---|---|---|---|
| `--input` | string | (required unless `--demo`) | Path to JSON file with feedback items |
| `--demo` | flag | off | Run with built-in 12-item sample queue |
| `--format` | choice | `markdown` | One of `json`, `markdown`, `mermaid`, `confluence`, `notion`, `linear` |
| `--output` | string | stdout | File path to write output |
| `--segment-weights` | string | `enterprise=4,mid_market=2,smb=1,prosumer=1` | Override default segment weights |
| `--threshold` | float | `4.0` | Minimum priority score to route into prioritization-frameworks |

## Input schema

```json
{
  "items": [
    {
      "id": "FB-2026-0001",
      "channel": "support",
      "customer_id": "cust-1234",
      "segment": "enterprise",
      "raw_text": "We really need a way to export results to PDF for our weekly board pack",
      "received_at": "2026-05-12T14:23:00Z",
      "submitter": "support-agent-jane",
      "opportunity_area": "reporting",
      "customer_name": "Priya",
      "opportunity_label": "Share results with people who have no login",
      "decision": "will-build"
    }
  ]
}
```

Required: `id`, `channel`, `customer_id`, `raw_text`, `received_at`. Optional fields the tool honours:

- `opportunity_label` — the job this ask serves, written by a person. The first one in a cluster becomes the cluster label; without it the label is `[write the job] keywords: ...`, a placeholder to replace.
- `decision` — `will-build` or `won't-build`, recorded after the triage meeting. Without it every reply is drafted as `exploring`; the score only fills `suggested_tier`.
- `customer_name` — used in the greeting ("Hi there," otherwise).

Routing: bug-like clusters (including slowness and timeouts) go to the bug tracker and get a `bug-acknowledged` reply (logged as a defect, no roadmap promise); Basic and Performance clusters go to prioritization even below the threshold; only low-scoring Delight, Indifferent or Reverse asks are archived.

**Exit codes:** 0 report written; 2 missing file, invalid JSON, wrong shape, empty queue or missing required fields.

## Output schemas

**JSON** (`pm/customer-feedback-triage/v1`):

```json
{
  "schema": "pm/customer-feedback-triage/v1",
  "generated_at": "2026-05-22T00:00:00Z",
  "data": {
    "clusters": [
      {
        "cluster_id": "C-001",
        "opportunity_label": "Share results with non-licensed stakeholders",
        "kano_category": "performance",
        "category": "feature_request",
        "request_count": 5,
        "distinct_customers": 4,
        "segment_breakdown": {"enterprise": 2, "mid_market": 2},
        "priority_score": 12.4,
        "above_threshold": true,
        "items": ["FB-2026-0001", "FB-2026-0007", "..."]
      }
    ],
    "routing": {
      "to_prioritization": ["C-001"],
      "to_bug_tracker": ["C-008"],
      "to_strategy": ["C-012"],
      "to_docs": ["C-005"]
    },
    "responses": [
      {
        "item_id": "FB-2026-0001",
        "template": "exploring",
        "suggested_tier": "will-build candidate",
        "body_markdown": "..."
      }
    ]
  }
}
```

**Markdown** (default): a triage-board document with sections per cluster, routing summary, and response drafts.

**Mermaid**: a `flowchart TD` of clusters → routing destinations.

**Confluence / Notion / Linear**: storage-format-appropriate variants of the markdown output.
