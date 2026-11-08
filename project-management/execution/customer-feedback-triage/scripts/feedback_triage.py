#!/usr/bin/env python3
"""Customer Feedback Triage Tool.

Ingests inbound customer feedback (from support, sales, NPS, in-app, etc.),
deduplicates and clusters by opportunity similarity, applies a Kano-model
heuristic for category guessing, computes a priority score combining Kano
weight, volume, segment weight, and strategic alignment, and emits suggested
response templates per item.

Labels are placeholders unless items carry `opportunity_label`; replies are
"exploring" unless an item carries `decision` (will-build / won't-build).
Exit codes: 0 report written, 2 bad input. Formats: json|markdown|mermaid|
confluence|notion|linear (PM SHARED_OUTPUT_SCHEMA).

Usage:
    python feedback_triage.py --demo
    python feedback_triage.py --demo --format json
    python feedback_triage.py --input queue.json --format markdown
    python feedback_triage.py --input queue.json --threshold 5.0 --format linear
"""

import argparse
import json
import math
import re
import sys
from datetime import datetime, timezone

SCHEMA = "pm/customer-feedback-triage/v1"

# Kano keyword heuristic. Documented and transparent — this is
# a starting guess; the PM should override liberally.

KANO_KEYWORDS = {
    "basic": [
        "broken", "doesn't work", "does not work", "missing", "can't",
        "cannot", "blocked", "blocker", "404", "error", "crash",
        "login", "sign in", "log in", "export data", "data loss",
    ],
    "performance": [
        "faster", "slower", "speed", "performance", "latency", "slow",
        "more", "increase", "bulk", "batch", "scale", "limit",
        "throughput", "response time",
    ],
    "delight": [
        "would love", "wish", "dream", "magic", "ai", "smart",
        "automatic", "predict", "suggest", "delight", "wow",
        "innovative", "novel",
    ],
    "indifferent": [
        "color", "theme", "icon", "rename", "label",
    ],
    "reverse": [
        "too chatty", "annoying", "intrusive", "popup", "spam",
        "noise", "remove", "disable", "turn off",
    ],
}

KANO_WEIGHTS = {
    "basic": 4,
    "performance": 2,
    "delight": 3,
    "indifferent": 0,
    "reverse": -3,
}

DEFAULT_SEGMENT_WEIGHTS = {
    "enterprise": 4,
    "mid_market": 2,
    "smb": 1,
    "prosumer": 1,
    "unknown": 1,
}

# Coarse category classification — bug vs feature vs question vs strategy.
CATEGORY_KEYWORDS = {
    "bug": [
        "broken", "doesn't work", "does not work", "error", "crash",
        "404", "regression", "stopped working", "wrong result",
        "slow", "timeout", "times out", "takes forever", "hangs", "freezes",
    ],
    "question": [
        "how do i", "how to", "where is", "where can i", "is there a way",
        "documentation", "docs", "tutorial",
    ],
    "strategy": [
        "new market", "pricing", "plan", "package", "tier", "enterprise plan",
        "different industry", "expand into",
    ],
}


# Stopwords for the word-overlap clustering heuristic.
# Intentionally small and inspectable; not a real NLP stopword list.

STOPWORDS = set("""
a an the of to and or for in on at by with from as is are was were be been being
this that these those it its their our your we i you they them us my mine yours
have has had do does did will would should could can may might must shall
not no n't but if then so than too very just only also still even however
about into onto over under between among through during while before after
""".split())


def tokenize(text: str) -> set:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    words = [w for w in text.split() if w and w not in STOPWORDS and len(w) > 2]
    return set(words)


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


# Kano + category classification

def classify_kano(text: str) -> str:
    """Coarse Kano guess from keyword presence.

    Returns one of: basic, performance, delight, indifferent, reverse, unclassified.
    Documented as heuristic. Overrides expected.
    """
    text = text.lower()
    scores = {k: 0 for k in KANO_KEYWORDS}
    for cat, keywords in KANO_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                scores[cat] += 1
    # Pick highest-scoring category; fall back to "performance" as the
    # most common feature-request shape if nothing matches.
    best = max(scores.items(), key=lambda kv: kv[1])
    if best[1] == 0:
        return "performance"
    return best[0]


def classify_category(text: str) -> str:
    text = text.lower()
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                return cat
    return "feature_request"


# Clustering — group items by opportunity similarity.
# Simple greedy clustering on Jaccard token similarity, stdlib only.

CLUSTER_SIMILARITY_THRESHOLD = 0.12  # tuned empirically against the demo set; word-overlap only


def cluster_items(items: list) -> list:
    tokenized = [(item, tokenize(item.get("raw_text", ""))) for item in items]
    clusters = []
    for item, tokens in tokenized:
        placed = False
        for cluster in clusters:
            sim = jaccard(tokens, cluster["centroid_tokens"])
            if sim >= CLUSTER_SIMILARITY_THRESHOLD:
                cluster["items"].append(item)
                # Update centroid as union of tokens (cheap; not strict centroid)
                cluster["centroid_tokens"] |= tokens
                placed = True
                break
        if not placed:
            clusters.append({
                "items": [item],
                "centroid_tokens": set(tokens),
            })
    # Assign cluster IDs and labels
    for idx, cluster in enumerate(clusters, start=1):
        cluster["cluster_id"] = f"C-{idx:03d}"
        cluster["opportunity_label"] = derive_label(cluster["items"])
    return clusters


def derive_label(items: list) -> str:
    """Use a human-written opportunity_label if any item carries one.

    Otherwise return a marked placeholder plus the top keywords. Naming the
    job ("share results with people who have no login") is a judgement the
    PM or model makes; keyword soup must not pass for a label.
    """
    given = [it["opportunity_label"] for it in items if it.get("opportunity_label")]
    if given:
        return given[0]
    counts = {}
    for item in items:
        for tok in tokenize(item.get("raw_text", "")):
            counts[tok] = counts.get(tok, 0) + 1
    if not counts:
        return "Unlabeled opportunity"
    top = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:4]
    return "[write the job] keywords: " + ", ".join(t[0] for t in top)


# Scoring

def score_cluster(cluster: dict, segment_weights: dict, strategic_alignment_map: dict) -> dict:
    """Compute composite priority score for a cluster.

    priority = kano_weight * log10(volume + 1) * max_segment_weight * (1 + strategic_alignment)
    """
    items = cluster["items"]
    # Kano: majority vote across items, with override if any item is "basic"
    kano_votes = {}
    for item in items:
        guess = item.get("_kano") or classify_kano(item.get("raw_text", ""))
        kano_votes[guess] = kano_votes.get(guess, 0) + 1
    if "basic" in kano_votes:
        kano_cat = "basic"
    else:
        kano_cat = max(kano_votes.items(), key=lambda kv: kv[1])[0]
    kano_weight = KANO_WEIGHTS.get(kano_cat, 0)

    # Volume: distinct customers
    distinct_customers = len(set(it.get("customer_id") for it in items if it.get("customer_id")))
    volume_factor = math.log10(distinct_customers + 1)

    # Segment: pick the highest-weight segment present in the cluster
    max_segment_weight = 0
    segment_breakdown = {}
    for item in items:
        seg = (item.get("segment") or "unknown").lower()
        seg_w = segment_weights.get(seg, segment_weights.get("unknown", 1))
        max_segment_weight = max(max_segment_weight, seg_w)
        segment_breakdown[seg] = segment_breakdown.get(seg, 0) + 1

    # Strategic alignment: per-cluster lookup, default 0
    sa = strategic_alignment_map.get(cluster["cluster_id"], 0)

    priority = kano_weight * volume_factor * max(max_segment_weight, 1) * (1 + sa)

    # Categorize the cluster overall (bug/question/strategy/feature) by majority
    cat_votes = {}
    for item in items:
        c = item.get("_category") or classify_category(item.get("raw_text", ""))
        cat_votes[c] = cat_votes.get(c, 0) + 1
    overall_category = max(cat_votes.items(), key=lambda kv: kv[1])[0]

    return {
        "cluster_id": cluster["cluster_id"],
        "opportunity_label": cluster["opportunity_label"],
        "kano_category": kano_cat,
        "kano_weight": kano_weight,
        "category": overall_category,
        "request_count": len(items),
        "distinct_customers": distinct_customers,
        "segment_breakdown": segment_breakdown,
        "max_segment_weight": max_segment_weight,
        "strategic_alignment": sa,
        "priority_score": round(priority, 2),
        "item_ids": [it.get("id") for it in items],
    }


# Response templating

WILL_BUILD_BODY = (
    "Hi{name},\n\n"
    "Thanks for raising this. {heard}We've decided to work on it and will "
    "let you know when it reaches you.\n\n"
    "What you asked for: {request}\n"
    "What we plan to ship: a solution that addresses the underlying need; "
    "the exact shape is being finalized.\n\n"
    "— The product team"
)

EXPLORING_BODY = (
    "Hi{name},\n\n"
    "Thank you for the detailed feedback. We're hearing this kind of request "
    "from a handful of customers and we're looking into the underlying need "
    "more carefully before committing to a solution. We don't have a date yet, "
    "but if you'd be open to a 30-minute conversation about how you'd use it, "
    "we'd value that.\n\n"
    "What you asked for: {request}\n\n"
    "— The product team"
)

BUG_BODY = (
    "Hi{name},\n\nThanks for reporting this, and sorry for the trouble. We've logged it with "
    "engineering as a defect and will update you when there's a fix or a workaround.\n\n"
    "What you reported: {request}\n\n— The product team")

WONT_BUILD_BODY = (
    "Hi{name},\n\n"
    "Thank you for the suggestion. We've thought carefully about this and "
    "have decided not to build it in the foreseeable future. A few reasons:\n"
    "  - It doesn't fit the direction of the product for the next 2-3 quarters.\n"
    "  - We've heard the request from a small number of customers and want "
    "to focus on changes that benefit a wider base.\n\n"
    "If there's a closely related workaround that would help in the meantime, "
    "let us know and we'll help you find it.\n\n"
    "What you asked for: {request}\n\n"
    "— The product team"
)


def response_for(item: dict, cluster_score: dict, threshold: float) -> dict:
    """Draft a reply. Exploring unless a decision is recorded on the item.

    "Always acknowledge, sometimes commit, rarely promise": the score only
    suggests a tier; will-build / won't-build need `decision` set by a person.
    """
    score = cluster_score["priority_score"]
    name = f" {item['customer_name']}" if item.get("customer_name") else " there"
    request_excerpt = (item.get("raw_text", "") or "")[:140]
    if cluster_score["category"] in ("bug", "question", "strategy"):
        suggested = "route:" + cluster_score["category"]
    elif score >= threshold * 1.5:
        suggested = "will-build candidate"
    elif score >= threshold:
        suggested = "exploring"
    else:
        suggested = "won't-build candidate"
    decision = (item.get("decision") or "").lower()
    if decision == "will-build":
        others = max(cluster_score["distinct_customers"] - 1, 0)
        heard = (f"{others} other customer{'s' if others != 1 else ''} asked for the same thing. "
                 if others else "")
        template, body = "will-build", WILL_BUILD_BODY.format(name=name, heard=heard, request=request_excerpt)
    elif decision == "won't-build":
        template, body = "won't-build", WONT_BUILD_BODY.format(name=name, request=request_excerpt)
    elif cluster_score["category"] == "bug":
        template, body = "bug-acknowledged", BUG_BODY.format(name=name, request=request_excerpt)
    else:
        template, body = "exploring", EXPLORING_BODY.format(name=name, request=request_excerpt)
    return {"item_id": item.get("id"), "template": template, "suggested_tier": suggested,
            "body_markdown": body}


# Routing

def build_routing(scores: list, threshold: float) -> dict:
    routing = {
        "to_prioritization": [],
        "to_bug_tracker": [],
        "to_docs": [],
        "to_strategy": [],
        "to_archive": [],
    }
    for s in scores:
        if s["category"] == "bug":
            routing["to_bug_tracker"].append(s["cluster_id"])
        elif s["category"] == "question":
            routing["to_docs"].append(s["cluster_id"])
        elif s["category"] == "strategy":
            routing["to_strategy"].append(s["cluster_id"])
        elif s["priority_score"] >= threshold or s["kano_category"] in ("basic", "performance"):
            routing["to_prioritization"].append(s["cluster_id"])
        else:
            routing["to_archive"].append(s["cluster_id"])
    return routing


# Demo data

def demo_items() -> list:
    return [
        {"id": "FB-2026-0001", "channel": "support", "customer_id": "cust-1001",
         "segment": "enterprise", "received_at": "2026-05-10T09:00:00Z",
         "submitter": "support-jane",
         "raw_text": "We really need a way to export results to PDF for our weekly board pack."},
        {"id": "FB-2026-0002", "channel": "support", "customer_id": "cust-1002",
         "segment": "mid_market", "received_at": "2026-05-10T11:23:00Z",
         "submitter": "support-rao",
         "raw_text": "Can we share a dashboard with someone who doesn't have a login? PDF export would work."},
        {"id": "FB-2026-0003", "channel": "sales", "customer_id": "cust-1003",
         "segment": "enterprise", "received_at": "2026-05-11T15:00:00Z",
         "submitter": "ae-priya",
         "raw_text": "Customer asked for read-only sharing links for their CFO. Blocker for renewal."},
        {"id": "FB-2026-0004", "channel": "in_app", "customer_id": "cust-1004",
         "segment": "smb", "received_at": "2026-05-12T08:30:00Z",
         "submitter": "self-serve-widget",
         "raw_text": "Login is broken on Safari. Keeps redirecting in a loop."},
        {"id": "FB-2026-0005", "channel": "support", "customer_id": "cust-1005",
         "segment": "smb", "received_at": "2026-05-12T09:00:00Z",
         "submitter": "support-jane",
         "raw_text": "Safari login redirects forever. Cannot sign in."},
        {"id": "FB-2026-0006", "channel": "nps", "customer_id": "cust-1006",
         "segment": "mid_market", "received_at": "2026-05-13T12:00:00Z",
         "submitter": "nps-survey",
         "raw_text": "Reports are slow to load. Sometimes takes 30 seconds."},
        {"id": "FB-2026-0007", "channel": "support", "customer_id": "cust-1007",
         "segment": "mid_market", "received_at": "2026-05-13T14:00:00Z",
         "submitter": "support-rao",
         "raw_text": "Dashboard speed is a real problem on the analytics page. Faster please."},
        {"id": "FB-2026-0008", "channel": "exec_ask", "customer_id": "cust-1008",
         "segment": "enterprise", "received_at": "2026-05-14T10:00:00Z",
         "submitter": "ceo",
         "raw_text": "Customer at lunch said they wished we had an AI-powered query assistant. Would love to see it."},
        {"id": "FB-2026-0009", "channel": "in_app", "customer_id": "cust-1009",
         "segment": "prosumer", "received_at": "2026-05-14T16:00:00Z",
         "submitter": "self-serve-widget",
         "raw_text": "Could we get a dark theme? Pretty please."},
        {"id": "FB-2026-0010", "channel": "social", "customer_id": "cust-1010",
         "segment": "smb", "received_at": "2026-05-15T09:00:00Z",
         "submitter": "social-listening",
         "raw_text": "The in-app chatbot is too chatty. Annoying. Please remove."},
        {"id": "FB-2026-0011", "channel": "sales", "customer_id": "cust-1011",
         "segment": "enterprise", "received_at": "2026-05-15T11:00:00Z",
         "submitter": "ae-priya",
         "raw_text": "Big bank prospect wants a separate enterprise plan with SSO and audit logs at a higher price tier."},
        {"id": "FB-2026-0012", "channel": "support", "customer_id": "cust-1012",
         "segment": "mid_market", "received_at": "2026-05-16T08:00:00Z",
         "submitter": "support-jane",
         "raw_text": "How do I export a single report to CSV? I can't find it in the docs."},
    ]


# Renderers

def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def render_json(payload: dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=False)


def render_markdown(payload: dict) -> str:
    data = payload["data"]
    out = []
    out.append("# Customer Feedback Triage Report")
    out.append("")
    out.append(f"Generated: {payload['generated_at']}")
    out.append(f"Schema: `{payload['schema']}`")
    out.append("")
    out.append("## Clusters")
    out.append("")
    out.append("| Cluster | Opportunity | Category | Kano | Reqs | Customers | Segment max | Score | Above threshold |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    for c in data["clusters"]:
        out.append(
            f"| {c['cluster_id']} | {c['opportunity_label']} | {c['category']} | "
            f"{c['kano_category']} | {c['request_count']} | {c['distinct_customers']} | "
            f"{c['max_segment_weight']} | {c['priority_score']} | {'yes' if c['above_threshold'] else 'no'} |"
        )
    out.append("")
    out.append("## Routing")
    out.append("")
    for dest, ids in data["routing"].items():
        out.append(f"- **{dest}**: {', '.join(ids) if ids else '(none)'}")
    out.append("")
    out.append("## Response drafts")
    out.append("")
    for r in data["responses"]:
        out.append(f"### {r['item_id']} — `{r['template']}` (suggested: {r['suggested_tier']})")
        out.append("")
        out.append("```")
        out.append(r["body_markdown"])
        out.append("```")
        out.append("")
    return "\n".join(out)


def render_mermaid(payload: dict) -> str:
    data = payload["data"]
    lines = ["```mermaid", "flowchart TD"]
    for c in data["clusters"]:
        node = f"{c['cluster_id']}[\"{c['opportunity_label']}<br/>score: {c['priority_score']}\"]"
        lines.append(f"    {node}")
    dest_labels = {
        "to_prioritization": "Prioritization (RICE/ICE)",
        "to_bug_tracker": "Bug Tracker",
        "to_docs": "Docs / Support",
        "to_strategy": "Strategy / Exec",
        "to_archive": "Archive (won't build)",
    }
    for dest, label in dest_labels.items():
        lines.append(f"    {dest}([{label}])")
    for dest, ids in data["routing"].items():
        for cid in ids:
            lines.append(f"    {cid} --> {dest}")
    lines.append("```")
    return "\n".join(lines)


def render_confluence(payload: dict) -> str:
    data = payload["data"]
    out = []
    out.append("<h2>Customer Feedback Triage Report</h2>")
    out.append(f"<p>Generated: {payload['generated_at']}</p>")
    out.append("<h3>Clusters</h3>")
    out.append("<table><tbody>")
    out.append(
        "<tr><th>Cluster</th><th>Opportunity</th><th>Category</th><th>Kano</th>"
        "<th>Reqs</th><th>Customers</th><th>Score</th></tr>"
    )
    for c in data["clusters"]:
        out.append(
            f"<tr><td>{c['cluster_id']}</td><td>{c['opportunity_label']}</td>"
            f"<td>{c['category']}</td><td>{c['kano_category']}</td>"
            f"<td>{c['request_count']}</td><td>{c['distinct_customers']}</td>"
            f"<td>{c['priority_score']}</td></tr>"
        )
    out.append("</tbody></table>")
    out.append("<h3>Routing</h3>")
    out.append("<ul>")
    for dest, ids in data["routing"].items():
        out.append(f"<li><strong>{dest}</strong>: {', '.join(ids) if ids else '(none)'}</li>")
    out.append("</ul>")
    return "\n".join(out)


def render_notion(payload: dict) -> str:
    # Notion accepts most GitHub-flavored Markdown; add callouts at the top.
    data = payload["data"]
    out = []
    out.append("# Customer Feedback Triage Report")
    out.append("")
    out.append(f"> [!NOTE]")
    out.append(f"> Generated: {payload['generated_at']} | Schema: `{payload['schema']}`")
    out.append("")
    out.append("## Clusters")
    out.append("")
    for c in data["clusters"]:
        out.append(f"### {c['cluster_id']} — {c['opportunity_label']}")
        out.append("")
        out.append(f"- Category: `{c['category']}`")
        out.append(f"- Kano: `{c['kano_category']}`")
        out.append(f"- Requests: {c['request_count']} from {c['distinct_customers']} customers")
        out.append(f"- Score: **{c['priority_score']}** ({'above' if c['above_threshold'] else 'below'} threshold)")
        out.append("")
    return "\n".join(out)


def render_linear(payload: dict) -> str:
    data = payload["data"]
    out = []
    out.append("# Feedback Triage")
    out.append("")
    out.append("Suggested Linear issues to create (one per high-priority cluster):")
    out.append("")
    for c in data["clusters"]:
        if not c["above_threshold"]:
            continue
        priority_label = "Urgent" if c["priority_score"] > 10 else "High" if c["priority_score"] > 6 else "Medium"
        out.append(f"## {c['opportunity_label']}")
        out.append("")
        out.append(f"Priority: ~~{priority_label}~~")
        out.append(f"Cluster: `{c['cluster_id']}`")
        out.append(f"Kano: `{c['kano_category']}` ({c['request_count']} requests, {c['distinct_customers']} customers)")
        out.append("")
        out.append("Originating feedback IDs: " + ", ".join(c["item_ids"]))
        out.append("")
    return "\n".join(out)


RENDERERS = {
    "json": render_json,
    "markdown": render_markdown,
    "mermaid": render_mermaid,
    "confluence": render_confluence,
    "notion": render_notion,
    "linear": render_linear,
}


# Main orchestration

def validate_items(items: list) -> list:
    required = ["id", "channel", "customer_id", "raw_text", "received_at"]
    errors = []
    for idx, item in enumerate(items):
        for field in required:
            if not item.get(field):
                errors.append(f"item[{idx}] missing required field `{field}`")
    return errors


def parse_segment_weights(spec: str) -> dict:
    weights = dict(DEFAULT_SEGMENT_WEIGHTS)
    if not spec:
        return weights
    for pair in spec.split(","):
        if "=" not in pair:
            continue
        k, v = pair.split("=", 1)
        try:
            weights[k.strip().lower()] = float(v.strip())
        except ValueError:
            pass
    return weights


def triage(items: list, segment_weights: dict, threshold: float) -> dict:
    # Pre-annotate each item with Kano + category guesses (consumed by clustering scorer).
    for item in items:
        item["_kano"] = classify_kano(item.get("raw_text", ""))
        item["_category"] = classify_category(item.get("raw_text", ""))

    clusters = cluster_items(items)

    # No external strategic alignment input; default 0. Hook for future input.
    strategic_alignment_map = {}

    scores = []
    for cluster in clusters:
        s = score_cluster(cluster, segment_weights, strategic_alignment_map)
        s["above_threshold"] = s["priority_score"] >= threshold
        scores.append(s)

    # Sort by score desc for readability
    scores.sort(key=lambda x: -x["priority_score"])

    routing = build_routing(scores, threshold)

    # Build response drafts per item, using its cluster's score
    score_by_cluster = {s["cluster_id"]: s for s in scores}
    responses = []
    for cluster in clusters:
        s = score_by_cluster[cluster["cluster_id"]]
        for item in cluster["items"]:
            responses.append(response_for(item, s, threshold))

    return {
        "schema": SCHEMA,
        "generated_at": now_iso(),
        "data": {
            "clusters": scores,
            "routing": routing,
            "responses": responses,
            "config": {
                "threshold": threshold,
                "segment_weights": segment_weights,
                "kano_weights": KANO_WEIGHTS,
            },
        },
    }


def main():
    p = argparse.ArgumentParser(description="Customer feedback triage")
    p.add_argument("--input", help="Path to JSON file with feedback items")
    p.add_argument("--demo", action="store_true", help="Run with built-in 12-item sample queue")
    p.add_argument(
        "--format", choices=list(RENDERERS.keys()), default="markdown",
        help="Output format (default: markdown)"
    )
    p.add_argument("--output", help="Write output to file (default: stdout)")
    p.add_argument(
        "--segment-weights", default="",
        help="Override segment weights, e.g. 'enterprise=4,mid_market=2,smb=1'"
    )
    p.add_argument("--threshold", type=float, default=4.0, help="Min priority to route into prioritization-frameworks")
    args = p.parse_args()

    if args.demo:
        items = demo_items()
    elif args.input:
        try:
            with open(args.input) as f:
                payload = json.load(f)
        except (OSError, ValueError) as e:
            print(f"Error reading input: {e}", file=sys.stderr)
            sys.exit(2)
        items = payload.get("items") if isinstance(payload, dict) else None
        if not isinstance(items, list) or not items or not all(isinstance(i, dict) for i in items):
            print("error: input must be a JSON object with a non-empty 'items' list of objects", file=sys.stderr)
            sys.exit(2)
    else:
        p.error("Either --demo or --input is required.")

    errors = validate_items(items)
    if errors:
        print("Input validation errors:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(2)

    segment_weights = parse_segment_weights(args.segment_weights)
    result = triage(items, segment_weights, args.threshold)

    rendered = RENDERERS[args.format](result)
    if args.output:
        with open(args.output, "w") as f:
            f.write(rendered)
    else:
        print(rendered)


if __name__ == "__main__":
    try:
        main()
    except (TypeError, ValueError, AttributeError, KeyError) as exc:  # field of the wrong type
        print(f"error: input has a field of the wrong type: {exc}", file=sys.stderr)
        sys.exit(2)
