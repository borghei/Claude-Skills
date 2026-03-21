#!/usr/bin/env python3
"""Rule Manager - Manage a learned rules knowledge base.

Add, list, search, prune, and promote/demote rules with confidence scores.
Rules are stored as JSON in a local knowledge base file, following the
Self-Improving Agent confidence scoring model.

Usage:
    python rule_manager.py add --rule "Use pnpm not npm" --source observed --category tool-preference
    python rule_manager.py list --sort confidence
    python rule_manager.py search --query "test"
    python rule_manager.py prune --max-age 90 --min-confidence 0.3
    python rule_manager.py promote --id <rule-id>
    python rule_manager.py demote --id <rule-id> --reason "contradicted by new pattern"
"""

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

DEFAULT_DB = "rules_kb.json"

VALID_SOURCES = ["user-stated", "observed", "inferred", "guessed"]
SOURCE_SCORES = {"user-stated": 1.0, "observed": 0.8, "inferred": 0.6, "guessed": 0.3}

VALID_STATUSES = ["candidate", "promoted", "stale", "retired"]
VALID_CATEGORIES = [
    "coding-convention", "project-architecture", "tool-preference",
    "debugging-pattern", "style-guide", "api-usage", "git-workflow",
    "testing", "performance", "security", "other",
]


def load_db(path: str) -> dict:
    """Load the rules database from disk."""
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {"rules": [], "metadata": {"created": datetime.now().isoformat(), "version": "1.0.0"}}


def save_db(db: dict, path: str) -> None:
    """Persist the rules database to disk."""
    db["metadata"]["updated"] = datetime.now().isoformat()
    with open(path, "w") as f:
        json.dump(db, f, indent=2)


def compute_confidence(rule: dict) -> float:
    """Compute effective confidence using base * recency * consistency factors."""
    base = SOURCE_SCORES.get(rule.get("source", "guessed"), 0.3)
    updated = datetime.fromisoformat(rule["updated"])
    age_days = (datetime.now() - updated).days
    if age_days <= 7:
        recency = 1.0
    elif age_days <= 30:
        recency = 0.9
    elif age_days <= 90:
        recency = 0.7
    else:
        recency = 0.5
    consistency = rule.get("consistency_factor", 1.0)
    return round(base * recency * consistency, 3)


def cmd_add(args, db: dict) -> dict:
    """Add a new rule to the knowledge base."""
    rule_id = str(uuid.uuid4())[:8]
    now = datetime.now().isoformat()
    rule = {
        "id": rule_id,
        "rule": args.rule,
        "source": args.source,
        "category": args.category,
        "status": "candidate",
        "recurrence": 1,
        "consistency_factor": 1.0,
        "created": now,
        "updated": now,
        "notes": args.notes or "",
    }
    rule["confidence"] = compute_confidence(rule)
    db["rules"].append(rule)
    return {"action": "added", "rule": rule}


def cmd_list(args, db: dict) -> dict:
    """List rules with optional filtering and sorting."""
    rules = db["rules"]
    if args.status:
        rules = [r for r in rules if r["status"] == args.status]
    if args.category:
        rules = [r for r in rules if r["category"] == args.category]
    # Recompute confidence for all listed rules
    for r in rules:
        r["confidence"] = compute_confidence(r)
    sort_key = args.sort if args.sort else "confidence"
    reverse = sort_key in ("confidence", "recurrence")
    rules = sorted(rules, key=lambda r: r.get(sort_key, ""), reverse=reverse)
    if args.limit:
        rules = rules[: args.limit]
    return {"action": "list", "count": len(rules), "rules": rules}


def cmd_search(args, db: dict) -> dict:
    """Search rules by text query across rule text, notes, and category."""
    query = args.query.lower()
    matches = []
    for r in db["rules"]:
        searchable = f"{r['rule']} {r.get('notes', '')} {r['category']}".lower()
        if query in searchable:
            r["confidence"] = compute_confidence(r)
            matches.append(r)
    matches.sort(key=lambda r: r["confidence"], reverse=True)
    return {"action": "search", "query": args.query, "count": len(matches), "rules": matches}


def cmd_prune(args, db: dict) -> dict:
    """Remove rules that are stale or below confidence threshold."""
    now = datetime.now()
    pruned = []
    kept = []
    for r in db["rules"]:
        r["confidence"] = compute_confidence(r)
        age_days = (now - datetime.fromisoformat(r["updated"])).days
        should_prune = False
        reasons = []
        if args.max_age and age_days > args.max_age:
            should_prune = True
            reasons.append(f"age={age_days}d > {args.max_age}d")
        if args.min_confidence and r["confidence"] < args.min_confidence:
            should_prune = True
            reasons.append(f"confidence={r['confidence']} < {args.min_confidence}")
        if r["status"] == "retired":
            should_prune = True
            reasons.append("status=retired")
        if should_prune and not args.dry_run:
            r["prune_reasons"] = reasons
            pruned.append(r)
        elif should_prune:
            r["prune_reasons"] = reasons
            pruned.append(r)
            kept.append(r)  # dry run keeps them
        else:
            kept.append(r)
    if not args.dry_run:
        db["rules"] = kept
    return {
        "action": "prune",
        "dry_run": args.dry_run,
        "pruned_count": len(pruned),
        "remaining_count": len(db["rules"]),
        "pruned": pruned,
    }


def cmd_promote(args, db: dict) -> dict:
    """Promote a rule from candidate to promoted status."""
    for r in db["rules"]:
        if r["id"] == args.id:
            old_status = r["status"]
            if old_status == "promoted":
                return {"action": "promote", "error": f"Rule {args.id} is already promoted"}
            r["status"] = "promoted"
            r["updated"] = datetime.now().isoformat()
            r["recurrence"] = max(r["recurrence"], 3)
            r["confidence"] = compute_confidence(r)
            return {
                "action": "promote",
                "id": args.id,
                "old_status": old_status,
                "new_status": "promoted",
                "rule": r,
            }
    return {"action": "promote", "error": f"Rule {args.id} not found"}


def cmd_demote(args, db: dict) -> dict:
    """Demote a rule by reducing consistency and optionally retiring it."""
    for r in db["rules"]:
        if r["id"] == args.id:
            old_status = r["status"]
            r["consistency_factor"] = max(0.0, r.get("consistency_factor", 1.0) - 0.3)
            if r["consistency_factor"] <= 0.0:
                r["status"] = "retired"
            elif args.retire:
                r["status"] = "retired"
            else:
                r["status"] = "stale"
            r["updated"] = datetime.now().isoformat()
            r["notes"] = f"{r.get('notes', '')} [Demoted: {args.reason}]".strip()
            r["confidence"] = compute_confidence(r)
            return {
                "action": "demote",
                "id": args.id,
                "old_status": old_status,
                "new_status": r["status"],
                "new_confidence": r["confidence"],
                "reason": args.reason,
                "rule": r,
            }
    return {"action": "demote", "error": f"Rule {args.id} not found"}


def format_human(result: dict) -> str:
    """Format result for human-readable output."""
    action = result.get("action", "unknown")
    lines = []

    if "error" in result:
        return f"Error: {result['error']}"

    if action == "added":
        r = result["rule"]
        lines.append(f"Added rule [{r['id']}]: {r['rule']}")
        lines.append(f"  Source: {r['source']}  Category: {r['category']}  Confidence: {r['confidence']}")

    elif action == "list":
        lines.append(f"Rules ({result['count']} total):")
        lines.append(f"{'ID':<10} {'Status':<12} {'Conf':<7} {'Rec':<5} {'Category':<22} Rule")
        lines.append("-" * 100)
        for r in result["rules"]:
            lines.append(
                f"{r['id']:<10} {r['status']:<12} {r['confidence']:<7} "
                f"{r['recurrence']:<5} {r['category']:<22} {r['rule'][:50]}"
            )

    elif action == "search":
        lines.append(f"Search results for '{result['query']}' ({result['count']} matches):")
        for r in result["rules"]:
            lines.append(f"  [{r['id']}] (conf={r['confidence']}) {r['rule']}")

    elif action == "prune":
        mode = " (DRY RUN)" if result["dry_run"] else ""
        lines.append(f"Prune{mode}: {result['pruned_count']} removed, {result['remaining_count']} remaining")
        for r in result["pruned"]:
            reasons = ", ".join(r.get("prune_reasons", []))
            lines.append(f"  [{r['id']}] {r['rule'][:50]} -- {reasons}")

    elif action in ("promote", "demote"):
        r = result.get("rule", {})
        lines.append(f"{action.title()}: [{result['id']}] {r.get('rule', '')}")
        lines.append(f"  {result.get('old_status', '')} -> {result.get('new_status', '')}")
        if "reason" in result:
            lines.append(f"  Reason: {result['reason']}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Rule Manager - Manage a learned rules knowledge base",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--db", default=DEFAULT_DB, help="Path to rules database file (default: rules_kb.json)")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output in JSON format")

    sub = parser.add_subparsers(dest="command", help="Available commands")

    # add
    p_add = sub.add_parser("add", help="Add a new rule")
    p_add.add_argument("--rule", required=True, help="The rule text")
    p_add.add_argument("--source", choices=VALID_SOURCES, default="observed", help="How the rule was learned")
    p_add.add_argument("--category", choices=VALID_CATEGORIES, default="other", help="Rule category")
    p_add.add_argument("--notes", help="Additional context or notes")

    # list
    p_list = sub.add_parser("list", help="List rules")
    p_list.add_argument("--sort", choices=["confidence", "recurrence", "created", "updated", "category"], default="confidence")
    p_list.add_argument("--status", choices=VALID_STATUSES, help="Filter by status")
    p_list.add_argument("--category", choices=VALID_CATEGORIES, help="Filter by category")
    p_list.add_argument("--limit", type=int, help="Max number of rules to show")

    # search
    p_search = sub.add_parser("search", help="Search rules by text")
    p_search.add_argument("--query", required=True, help="Search query")

    # prune
    p_prune = sub.add_parser("prune", help="Remove stale or low-confidence rules")
    p_prune.add_argument("--max-age", type=int, help="Max age in days before pruning")
    p_prune.add_argument("--min-confidence", type=float, help="Min confidence threshold")
    p_prune.add_argument("--dry-run", action="store_true", help="Show what would be pruned without removing")

    # promote
    p_promote = sub.add_parser("promote", help="Promote a rule to enforced status")
    p_promote.add_argument("--id", required=True, help="Rule ID to promote")

    # demote
    p_demote = sub.add_parser("demote", help="Demote a rule (reduce confidence)")
    p_demote.add_argument("--id", required=True, help="Rule ID to demote")
    p_demote.add_argument("--reason", required=True, help="Why the rule is being demoted")
    p_demote.add_argument("--retire", action="store_true", help="Immediately retire the rule")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    db = load_db(args.db)

    commands = {
        "add": cmd_add,
        "list": cmd_list,
        "search": cmd_search,
        "prune": cmd_prune,
        "promote": cmd_promote,
        "demote": cmd_demote,
    }

    result = commands[args.command](args, db)
    save_db(db, args.db)

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(format_human(result))


if __name__ == "__main__":
    main()
