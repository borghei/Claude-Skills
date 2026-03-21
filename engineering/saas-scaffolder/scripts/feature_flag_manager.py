#!/usr/bin/env python3
"""Feature Flag Manager — CRUD operations on a JSON-based feature flag store.

Manage feature flags for SaaS applications: create, read, update, delete,
list, and evaluate flags with support for percentage rollouts, plan-based
targeting, and environment scoping.

Uses ONLY Python standard library. No LLM or API calls.
"""

import argparse
import json
import os
import sys
import textwrap
from copy import deepcopy
from datetime import datetime, timezone


DEFAULT_STORE = "feature_flags.json"

# ---------------------------------------------------------------------------
# Flag store operations
# ---------------------------------------------------------------------------

def load_store(path):
    """Load the flag store from a JSON file. Returns dict."""
    if not os.path.exists(path):
        return {"flags": {}, "metadata": {"created_at": now_iso(), "updated_at": now_iso()}}
    with open(path, "r") as f:
        return json.load(f)


def save_store(store, path):
    """Persist the flag store to a JSON file."""
    store["metadata"]["updated_at"] = now_iso()
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w") as f:
        json.dump(store, f, indent=2)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# CRUD helpers
# ---------------------------------------------------------------------------

def create_flag(store, key, description="", enabled=False, environments=None,
                rollout_percentage=100, allowed_plans=None, tags=None):
    """Add a new feature flag to the store."""
    if key in store["flags"]:
        return False, f"Flag '{key}' already exists. Use 'update' to modify."

    store["flags"][key] = {
        "key": key,
        "description": description,
        "enabled": enabled,
        "environments": environments or ["development", "staging", "production"],
        "rollout_percentage": max(0, min(100, rollout_percentage)),
        "allowed_plans": allowed_plans or ["free", "pro", "enterprise"],
        "tags": tags or [],
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    return True, f"Flag '{key}' created."


def get_flag(store, key):
    """Retrieve a single flag by key."""
    flag = store["flags"].get(key)
    if not flag:
        return None, f"Flag '{key}' not found."
    return deepcopy(flag), None


def update_flag(store, key, **kwargs):
    """Update fields of an existing flag."""
    if key not in store["flags"]:
        return False, f"Flag '{key}' not found."

    flag = store["flags"][key]
    updatable = ("description", "enabled", "environments", "rollout_percentage", "allowed_plans", "tags")
    changed = []
    for field in updatable:
        if field in kwargs and kwargs[field] is not None:
            old_val = flag.get(field)
            new_val = kwargs[field]
            if field == "rollout_percentage":
                new_val = max(0, min(100, new_val))
            if old_val != new_val:
                flag[field] = new_val
                changed.append(field)

    if not changed:
        return True, f"Flag '{key}' unchanged (no new values)."

    flag["updated_at"] = now_iso()
    return True, f"Flag '{key}' updated: {', '.join(changed)}."


def delete_flag(store, key):
    """Remove a flag from the store."""
    if key not in store["flags"]:
        return False, f"Flag '{key}' not found."
    del store["flags"][key]
    return True, f"Flag '{key}' deleted."


def list_flags(store, tag=None, environment=None, enabled_only=False):
    """List flags with optional filters."""
    results = []
    for flag in store["flags"].values():
        if tag and tag not in flag.get("tags", []):
            continue
        if environment and environment not in flag.get("environments", []):
            continue
        if enabled_only and not flag.get("enabled", False):
            continue
        results.append(deepcopy(flag))
    results.sort(key=lambda f: f["key"])
    return results


def evaluate_flag(store, key, environment="production", plan="free", user_hash=None):
    """Evaluate whether a flag is active for given context."""
    flag = store["flags"].get(key)
    if not flag:
        return {"active": False, "reason": "flag_not_found"}

    if not flag.get("enabled", False):
        return {"active": False, "reason": "flag_disabled"}

    if environment not in flag.get("environments", []):
        return {"active": False, "reason": f"environment '{environment}' not targeted"}

    if plan not in flag.get("allowed_plans", []):
        return {"active": False, "reason": f"plan '{plan}' not allowed"}

    pct = flag.get("rollout_percentage", 100)
    if pct < 100:
        if user_hash is not None:
            bucket = hash(f"{key}:{user_hash}") % 100
            if bucket >= pct:
                return {"active": False, "reason": f"user outside {pct}% rollout"}
        else:
            return {"active": True, "reason": f"rollout {pct}% (no user_hash to evaluate)"}

    return {"active": True, "reason": "all_checks_passed"}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Manage feature flag configurations for SaaS projects (CRUD on a JSON store).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            examples:
              %(prog)s create --key dark-mode --description "Dark mode toggle" --enabled
              %(prog)s list --enabled-only
              %(prog)s update --key dark-mode --rollout-percentage 50
              %(prog)s evaluate --key dark-mode --environment production --plan pro
              %(prog)s delete --key dark-mode
        """),
    )

    parser.add_argument("--store", default=DEFAULT_STORE, help=f"Path to flag store JSON (default: {DEFAULT_STORE})")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output results as JSON")

    sub = parser.add_subparsers(dest="command", help="Operation to perform")

    # -- create --
    p_create = sub.add_parser("create", help="Create a new feature flag")
    p_create.add_argument("--key", required=True, help="Unique flag key (e.g. dark-mode)")
    p_create.add_argument("--description", default="", help="Human-readable description")
    p_create.add_argument("--enabled", action="store_true", help="Enable the flag immediately")
    p_create.add_argument("--environments", nargs="*", default=None,
                          help="Target environments (default: development staging production)")
    p_create.add_argument("--rollout-percentage", type=int, default=100, help="Rollout percentage 0-100")
    p_create.add_argument("--allowed-plans", nargs="*", default=None,
                          help="Plans that can see this flag (default: free pro enterprise)")
    p_create.add_argument("--tags", nargs="*", default=None, help="Tags for filtering")

    # -- get --
    p_get = sub.add_parser("get", help="Get a single flag by key")
    p_get.add_argument("--key", required=True, help="Flag key to retrieve")

    # -- update --
    p_update = sub.add_parser("update", help="Update an existing flag")
    p_update.add_argument("--key", required=True, help="Flag key to update")
    p_update.add_argument("--description", default=None)
    p_update.add_argument("--enabled", default=None, type=lambda v: v.lower() in ("true", "1", "yes"),
                          help="true/false")
    p_update.add_argument("--environments", nargs="*", default=None)
    p_update.add_argument("--rollout-percentage", type=int, default=None)
    p_update.add_argument("--allowed-plans", nargs="*", default=None)
    p_update.add_argument("--tags", nargs="*", default=None)

    # -- delete --
    p_delete = sub.add_parser("delete", help="Delete a feature flag")
    p_delete.add_argument("--key", required=True, help="Flag key to delete")

    # -- list --
    p_list = sub.add_parser("list", help="List feature flags")
    p_list.add_argument("--tag", default=None, help="Filter by tag")
    p_list.add_argument("--environment", default=None, help="Filter by target environment")
    p_list.add_argument("--enabled-only", action="store_true", help="Show only enabled flags")

    # -- evaluate --
    p_eval = sub.add_parser("evaluate", help="Evaluate a flag for a given context")
    p_eval.add_argument("--key", required=True, help="Flag key to evaluate")
    p_eval.add_argument("--environment", default="production", help="Environment context")
    p_eval.add_argument("--plan", default="free", help="Tenant plan context")
    p_eval.add_argument("--user-hash", default=None, help="User identifier for rollout bucketing")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    store = load_store(args.store)
    output = {}

    if args.command == "create":
        ok, msg = create_flag(
            store, args.key, description=args.description, enabled=args.enabled,
            environments=args.environments, rollout_percentage=args.rollout_percentage,
            allowed_plans=args.allowed_plans, tags=args.tags,
        )
        save_store(store, args.store)
        output = {"success": ok, "message": msg, "flag": store["flags"].get(args.key)}

    elif args.command == "get":
        flag, err = get_flag(store, args.key)
        output = {"success": flag is not None, "flag": flag, "error": err}

    elif args.command == "update":
        ok, msg = update_flag(
            store, args.key, description=args.description, enabled=args.enabled,
            environments=args.environments, rollout_percentage=args.rollout_percentage,
            allowed_plans=args.allowed_plans, tags=args.tags,
        )
        save_store(store, args.store)
        output = {"success": ok, "message": msg, "flag": store["flags"].get(args.key)}

    elif args.command == "delete":
        ok, msg = delete_flag(store, args.key)
        save_store(store, args.store)
        output = {"success": ok, "message": msg}

    elif args.command == "list":
        flags = list_flags(store, tag=args.tag, environment=args.environment,
                           enabled_only=args.enabled_only)
        output = {"success": True, "count": len(flags), "flags": flags}

    elif args.command == "evaluate":
        result = evaluate_flag(store, args.key, environment=args.environment,
                               plan=args.plan, user_hash=args.user_hash)
        output = {"success": True, "key": args.key, "evaluation": result}

    # --- Output ---
    if args.json_output:
        print(json.dumps(output, indent=2))
    else:
        _print_human(args.command, output)


def _print_human(command, output):
    """Pretty-print results for human consumption."""
    if not output.get("success", False) and output.get("error"):
        print(f"Error: {output['error']}")
        sys.exit(1)

    if command in ("create", "update", "delete"):
        print(output.get("message", "Done."))
        flag = output.get("flag")
        if flag:
            _print_flag_summary(flag)

    elif command == "get":
        flag = output.get("flag")
        if flag:
            _print_flag_summary(flag)
        else:
            print(f"Error: {output.get('error')}")
            sys.exit(1)

    elif command == "list":
        flags = output.get("flags", [])
        print(f"Feature Flags ({output.get('count', 0)} total)")
        print("=" * 70)
        if not flags:
            print("  (none)")
        for flag in flags:
            status = "ON " if flag["enabled"] else "OFF"
            pct = flag.get("rollout_percentage", 100)
            plans = ", ".join(flag.get("allowed_plans", []))
            envs = ", ".join(flag.get("environments", []))
            print(f"  [{status}] {flag['key']:<30} rollout={pct:>3}%  plans=[{plans}]")
            if flag.get("description"):
                print(f"        {flag['description']}")

    elif command == "evaluate":
        ev = output.get("evaluation", {})
        key = output.get("key", "?")
        active = ev.get("active", False)
        reason = ev.get("reason", "")
        symbol = "ACTIVE" if active else "INACTIVE"
        print(f"Flag '{key}': {symbol}")
        print(f"  Reason: {reason}")


def _print_flag_summary(flag):
    """Print a single flag in a readable format."""
    status = "ENABLED" if flag["enabled"] else "DISABLED"
    print(f"\n  Key:         {flag['key']}")
    print(f"  Status:      {status}")
    print(f"  Description: {flag.get('description', '(none)')}")
    print(f"  Rollout:     {flag.get('rollout_percentage', 100)}%")
    print(f"  Plans:       {', '.join(flag.get('allowed_plans', []))}")
    print(f"  Envs:        {', '.join(flag.get('environments', []))}")
    print(f"  Tags:        {', '.join(flag.get('tags', [])) or '(none)'}")
    print(f"  Updated:     {flag.get('updated_at', 'N/A')}")


if __name__ == "__main__":
    main()
