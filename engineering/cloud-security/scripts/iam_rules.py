#!/usr/bin/env python3
"""IAM rule data and privilege primitives used by iam_least_privilege.py.

Holds the severity scale, the admin-grant and write-verb vocabularies, the
privilege-escalation path catalog, and the primitives that flatten policy
statements, match wildcard actions, and classify effective privilege. The
per-principal checks, scoring, and CLI live in iam_least_privilege.py.

Usage:
    python3 iam_rules.py --list-rules
"""

import argparse
import json
import sys
from typing import Any, Dict, Iterable, List, Tuple

SEVERITY_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3}
SEVERITY_WEIGHT = {"critical": 40, "high": 20, "medium": 8, "low": 3}

ADMIN_GRANTS = {"*", "*:*", "owner", "roles/owner", "roles/editor",
                "microsoft.authorization/*", "contributor", "administrator"}
WRITE_VERBS = ("create", "delete", "update", "put", "write", "modify", "attach",
               "detach", "set", "remove", "terminate", "invoke")

ESCALATION_PATHS: List[Dict[str, Any]] = [
    {"name": "PassRole to compute",
     "all_of": [["iam:passrole"],
                ["ec2:runinstances", "lambda:createfunction", "ecs:runtask",
                 "glue:createdevendpoint", "cloudformation:createstack"]],
     "why": "The principal can hand an existing high-privilege role to a compute "
            "resource it launches, then act as that role."},
    {"name": "Managed-policy version rewrite",
     "all_of": [["iam:createpolicyversion", "iam:setdefaultpolicyversion"]],
     "why": "The principal can publish a new default version of any attached "
            "policy, granting itself arbitrary permissions."},
    {"name": "Self-attach admin policy",
     "all_of": [["iam:attachuserpolicy", "iam:attachrolepolicy",
                 "iam:putuserpolicy", "iam:putrolepolicy"]],
     "why": "The principal can attach AdministratorAccess to itself."},
    {"name": "Trust-policy rewrite",
     "all_of": [["iam:updateassumerolepolicy"]],
     "why": "The principal can make any role assumable by itself or an external "
            "account."},
    {"name": "Function code overwrite",
     "all_of": [["lambda:updatefunctioncode"], ["iam:passrole"]],
     "why": "The principal can replace the code of a function running under a "
            "higher-privileged execution role."},
    {"name": "Service-account impersonation",
     "all_of": [["iam.serviceaccounts.actas", "iam.serviceaccounts.getaccesstoken",
                 "iam.serviceaccountkeys.create"]],
     "why": "The principal can mint credentials for a higher-privileged service "
            "account."},
    {"name": "Project IAM policy rewrite",
     "all_of": [["resourcemanager.projects.setiampolicy",
                 "resourcemanager.folders.setiampolicy"]],
     "why": "The principal can grant itself any role on the project or folder."},
    {"name": "Role-assignment write",
     "all_of": [["microsoft.authorization/roleassignments/write"]],
     "why": "The principal can assign itself Owner on any scope it can reach."},
]


def granted_actions(principal: Dict[str, Any]) -> List[Tuple[str, List[str], Dict[str, Any]]]:
    """Flatten a principal's allow statements into (action, resources, conditions)."""
    flat: List[Tuple[str, List[str], Dict[str, Any]]] = []
    for policy in principal.get("policies", []) or []:
        for stmt in policy.get("statements", []) or []:
            if str(stmt.get("effect", "allow")).lower() != "allow":
                continue
            resources = [str(r) for r in stmt.get("resources", ["*"])]
            conditions = stmt.get("conditions", {}) or {}
            for action in stmt.get("actions", []) or []:
                flat.append((str(action).lower(), resources, conditions))
    return flat


def action_matches(granted: str, target: str) -> bool:
    """Return True if a granted action pattern covers a specific target action."""
    if granted in {"*", "*:*"}:
        return True
    if granted.endswith("*"):
        return target.startswith(granted[:-1])
    return granted == target


def privilege_tier(actions: Iterable[Tuple[str, List[str], Dict[str, Any]]]) -> str:
    """Classify a principal's effective privilege into a coarse tier."""
    actions = list(actions)
    for action, resources, _ in actions:
        if action in ADMIN_GRANTS and any(r == "*" for r in resources):
            return "admin"
    if any(action in ADMIN_GRANTS for action, _, _ in actions):
        return "admin-scoped"
    broad_write = [a for a, res, _ in actions
                   if any(v in a for v in WRITE_VERBS) and "*" in res]
    if broad_write:
        return "write-broad"
    if any(a.endswith("*") for a, _, _ in actions):
        return "write-scoped"
    return "narrow"


def finding(fid: str, severity: str, principal: str, title: str,
            evidence: str, remediation: str) -> Dict[str, Any]:
    """Build one normalized IAM finding record."""
    return {"id": fid, "severity": severity, "principal": principal, "title": title,
            "evidence": evidence, "remediation": remediation}


def matched_escalations(action_set: List[str]) -> List[Tuple[Dict[str, Any], List[str]]]:
    """Return each escalation path the granted actions satisfy, with the legs used.

    A principal holding unrestricted admin satisfies every path; reporting eight
    escalation findings on top of the wildcard finding is noise, not signal, so
    full admin short-circuits to no paths.
    """
    if any(a in {"*", "*:*"} for a in action_set):
        return []
    hits: List[Tuple[Dict[str, Any], List[str]]] = []
    for path in ESCALATION_PATHS:
        matched: List[str] = []
        for group in path["all_of"]:
            leg = next((granted for granted in action_set for target in group
                        if action_matches(granted, target)), None)
            if leg is None:
                matched = []
                break
            matched.append(leg)
        if matched:
            hits.append((path, matched))
    return hits


def rule_catalog() -> Dict[str, Any]:
    """Return every tunable rule input, for review before a review is trusted."""
    return {
        "severity_weight": SEVERITY_WEIGHT,
        "admin_grants": sorted(ADMIN_GRANTS),
        "write_verbs": list(WRITE_VERBS),
        "escalation_paths": [{"name": p["name"], "requires": p["all_of"],
                              "why": p["why"]} for p in ESCALATION_PATHS],
    }


def output(catalog: Dict[str, Any], fmt: str) -> None:
    """Print the rule catalog as JSON or human-readable text."""
    if fmt == "json":
        print(json.dumps(catalog, indent=2))
        return
    print("Severity weights (summed into the per-principal risk score)")
    for severity, weight in catalog["severity_weight"].items():
        print(f"  {severity:<10} {weight}")
    print(f"\nActions treated as admin: {', '.join(catalog['admin_grants'])}")
    print(f"Substrings treated as writes: {', '.join(catalog['write_verbs'])}")
    print("\nPrivilege-escalation paths")
    for path in catalog["escalation_paths"]:
        print(f"  {path['name']}")
        for group in path["requires"]:
            print(f"    needs one of: {', '.join(group)}")
        print(f"    {path['why']}")


def main() -> None:
    """Parse arguments and print the rule catalog."""
    parser = argparse.ArgumentParser(
        description="IAM rule data for iam_least_privilege.py; run --list-rules "
                    "to inspect the severity weights, admin vocabulary, and the "
                    "privilege-escalation path catalog.")
    parser.add_argument("--list-rules", action="store_true",
                        help="Print every tunable rule input.")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text).")
    args = parser.parse_args()

    if not args.list_rules:
        parser.print_help()
        sys.exit(0)
    output(rule_catalog(), args.format)


if __name__ == "__main__":
    main()
