#!/usr/bin/env python3
"""
tam_sam_som_builder.py — Build TAM/SAM/SOM top-down and bottom-up, reconcile
the two chains, and flag implausible ratios.

Reads a JSON market model containing an optional top-down chain (a published
anchor plus named retention filters) and an optional bottom-up chain (unit
counts, qualification, value per unit, reach, win rate). Emits both chains,
their layer-by-layer divergence, and a list of plausibility findings.

Stdlib only. Deterministic. Text (default) or JSON output.

Usage:
    python3 tam_sam_som_builder.py --input market_model.json
    python3 tam_sam_som_builder.py --input market_model.json --format json
    python3 tam_sam_som_builder.py --input market_model.json --strict

Input schema (see assets/sample_market_model.json for a complete example):
{
  "market": str, "currency": str, "horizon_years": 3,
  "top_down": {"anchor_source", "anchor_vintage_years", "total_market_value",
               "sam_filters": [{"name", "retention", "basis"}],
               "som_filters": [{"name", "retention", "basis"}]},
  "bottom_up": {"unit_name", "total_units", "qualified_unit_ratio",
                "annual_value_per_unit", "reachable_unit_ratio",
                "expected_win_rate"}
}
At least one of top_down / bottom_up is required; supply both to reconcile.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Plausibility bands. Crossing one is not fatal, but it must be explained.
SAM_TAM_WARN = 0.40
SAM_TAM_FAIL = 0.60
SOM_SAM_WARN = 0.10
SOM_SAM_FAIL = 0.20
SOM_TAM_WARN = 0.05
DIVERGENCE_WARN = 3.0
DIVERGENCE_FAIL = 10.0
STALE_ANCHOR_YEARS = 1.5


@dataclass
class Finding:
    """A single plausibility observation about the model."""

    severity: str
    layer: str
    message: str


@dataclass
class Chain:
    """One sizing chain (top-down or bottom-up) with its intermediate steps."""

    method: str
    tam: float = 0.0
    sam: float = 0.0
    som: float = 0.0
    steps: list[str] = field(default_factory=list)


def _retention_product(filters: list[dict[str, Any]], steps: list[str],
                       label: str) -> float:
    """Multiply named retention fractions, recording each step."""
    product = 1.0
    for f in filters:
        retention = float(f.get("retention", 1.0))
        if not 0.0 < retention <= 1.0:
            raise ValueError(
                f"{label} filter '{f.get('name', '?')}' has retention "
                f"{retention}; must be greater than 0 and at most 1"
            )
        product *= retention
        steps.append(f"{label}: x{retention:.3f} — {f.get('name', 'unnamed filter')}")
    return product


def build_top_down(spec: dict[str, Any]) -> Chain:
    """Build the top-down chain from a published anchor and retention filters."""
    chain = Chain(method="top-down")
    anchor = float(spec.get("total_market_value", 0.0))
    if anchor <= 0:
        raise ValueError("top_down.total_market_value must be a positive number")
    chain.tam = anchor
    chain.steps.append(f"anchor: {anchor:,.0f} — {spec.get('anchor_source', 'unsourced')}")
    chain.sam = anchor * _retention_product(
        spec.get("sam_filters", []) or [], chain.steps, "SAM"
    )
    chain.som = chain.sam * _retention_product(
        spec.get("som_filters", []) or [], chain.steps, "SOM"
    )
    return chain


def build_bottom_up(spec: dict[str, Any]) -> Chain:
    """Build the bottom-up chain from unit counts and observed conversion."""
    chain = Chain(method="bottom-up")
    units = float(spec.get("total_units", 0.0))
    value = float(spec.get("annual_value_per_unit", 0.0))
    if units <= 0 or value <= 0:
        raise ValueError(
            "bottom_up.total_units and bottom_up.annual_value_per_unit "
            "must both be positive numbers"
        )
    qualified = float(spec.get("qualified_unit_ratio", 1.0))
    reachable = float(spec.get("reachable_unit_ratio", 1.0))
    win_rate = float(spec.get("expected_win_rate", 1.0))
    for name, val in (("qualified_unit_ratio", qualified),
                      ("reachable_unit_ratio", reachable),
                      ("expected_win_rate", win_rate)):
        if not 0.0 < val <= 1.0:
            raise ValueError(f"bottom_up.{name} is {val}; must be in (0, 1]")

    unit_label = spec.get("unit_name", "unit")
    chain.tam = units * value
    chain.steps.append(f"{units:,.0f} {unit_label}s x {value:,.0f} value")
    chain.sam = units * qualified * value
    chain.steps.append(f"qualified: x{qualified:.3f}")
    chain.som = chain.sam * reachable * win_rate
    chain.steps.append(f"reachable: x{reachable:.3f}, win rate: x{win_rate:.3f}")
    return chain


def check_ratios(chain: Chain, horizon_years: float) -> list[Finding]:
    """Flag SAM/TAM, SOM/SAM, and SOM/TAM ratios outside plausible bands."""
    out: list[Finding] = []
    if chain.tam <= 0:
        return out
    sam_tam = chain.sam / chain.tam
    som_sam = chain.som / chain.sam if chain.sam > 0 else 0.0
    som_tam = chain.som / chain.tam
    m = chain.method

    if sam_tam >= SAM_TAM_FAIL:
        out.append(Finding("fail", m, f"SAM is {sam_tam:.0%} of TAM — you are claiming "
                           "nearly the whole market is addressable; tighten the definition"))
    elif sam_tam >= SAM_TAM_WARN:
        out.append(Finding("warn", m, f"SAM is {sam_tam:.0%} of TAM — above the 40% "
                           "band; justify in the memo"))
    if som_sam >= SOM_SAM_FAIL:
        out.append(Finding("fail", m, f"SOM is {som_sam:.0%} of SAM over {horizon_years:g}y "
                           "— that is category leadership inside the horizon"))
    elif som_sam >= SOM_SAM_WARN:
        out.append(Finding("warn", m, f"SOM is {som_sam:.0%} of SAM over {horizon_years:g}y "
                           "— aggressive; name the channel that delivers it"))
    if som_tam >= SOM_TAM_WARN:
        out.append(Finding("warn", m, f"SOM is {som_tam:.1%} of TAM — above 5%; verify "
                           "the reach and win-rate assumptions"))
    return out


def reconcile(top: Chain | None, bottom: Chain | None) -> tuple[list[Finding], dict[str, Any]]:
    """Compare the two chains layer by layer and flag divergence."""
    findings: list[Finding] = []
    divergence: dict[str, Any] = {}
    if top is None or bottom is None:
        findings.append(Finding("warn", "reconciliation", "only one chain supplied — a "
                                "single-method size cannot be cross-checked; state the "
                                "method explicitly in the memo"))
        return findings, divergence

    for layer in ("tam", "sam", "som"):
        a, b = getattr(top, layer), getattr(bottom, layer)
        if a <= 0 or b <= 0:
            continue
        ratio = max(a, b) / min(a, b)
        divergence[layer] = round(ratio, 2)
        larger = "top-down" if a > b else "bottom-up"
        if ratio >= DIVERGENCE_FAIL:
            findings.append(Finding("fail", layer.upper(), f"{ratio:.1f}x divergence "
                                    f"({larger} larger) — the two chains are sizing "
                                    "different markets"))
        elif ratio >= DIVERGENCE_WARN:
            findings.append(Finding("warn", layer.upper(), f"{ratio:.1f}x divergence "
                                    f"({larger} larger) — explain the definitional gap"))
    return findings, divergence


def analyse(model: dict[str, Any]) -> dict[str, Any]:
    """Run the full build, ratio check, and reconciliation."""
    horizon = float(model.get("horizon_years", 3))
    top = build_top_down(model["top_down"]) if model.get("top_down") else None
    bottom = build_bottom_up(model["bottom_up"]) if model.get("bottom_up") else None
    if top is None and bottom is None:
        raise ValueError("model must contain at least one of 'top_down' or 'bottom_up'")

    findings: list[Finding] = []
    for chain in (top, bottom):
        if chain is not None:
            findings.extend(check_ratios(chain, horizon))

    vintage = float((model.get("top_down") or {}).get("anchor_vintage_years", 0))
    if vintage > STALE_ANCHOR_YEARS:
        findings.append(Finding("warn", "top-down", f"anchor is {vintage:g} years old — "
                                "apply an explicit growth bridge and show both figures"))

    recon_findings, divergence = reconcile(top, bottom)
    findings.extend(recon_findings)

    counts = {"fail": 0, "warn": 0}
    for f in findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1
    return {
        "market": model.get("market", ""),
        "currency": model.get("currency", ""),
        "horizon_years": horizon,
        "chains": [
            {"method": c.method, "tam": round(c.tam, 2), "sam": round(c.sam, 2),
             "som": round(c.som, 2), "steps": c.steps}
            for c in (top, bottom) if c is not None
        ],
        "divergence_multiple": divergence,
        "severity_counts": counts,
        "findings": [{"severity": f.severity, "layer": f.layer, "message": f.message}
                     for f in findings],
    }


def render_text(report: dict[str, Any]) -> str:
    """Render the report as human-readable text."""
    cur = report["currency"]
    lines = [f"Market sizing — {report['market']}",
             f"Horizon: {report['horizon_years']:g} years | Currency: {cur}", ""]
    for chain in report["chains"]:
        lines.append(f"[{chain['method']}]")
        for layer in ("tam", "sam", "som"):
            lines.append(f"  {layer.upper():4} {chain[layer]:>18,.0f} {cur}")
        for step in chain["steps"]:
            lines.append(f"    - {step}")
        lines.append("")
    if report["divergence_multiple"]:
        lines.append("Reconciliation (larger / smaller):")
        for layer, ratio in report["divergence_multiple"].items():
            lines.append(f"  {layer.upper():4} {ratio:.2f}x")
        lines.append("")
    counts = report["severity_counts"]
    lines.append(f"Findings: {counts.get('fail', 0)} fail, {counts.get('warn', 0)} warn")
    if not report["findings"]:
        lines.append("  none — ratios and reconciliation are within band")
    for f in report["findings"]:
        lines.append(f"  [{f['severity'].upper():4}] {f['layer']}: {f['message']}")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Build and reconcile TAM/SAM/SOM from an assumption set.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--input", required=True,
                        help="Path to the JSON market model (see schema in --help epilog)")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format; text is the default")
    parser.add_argument("--output", help="Write output to this file instead of stdout")
    parser.add_argument("--strict", action="store_true",
                        help="Exit non-zero if any finding has severity 'fail'")
    return parser.parse_args()


def main() -> int:
    """CLI entry point."""
    args = parse_args()
    try:
        model = json.loads(Path(args.input).read_text(encoding="utf-8"))
        report = analyse(model)
        out = json.dumps(report, indent=2) if args.format == "json" else render_text(report)
        if args.output:
            Path(args.output).write_text(out, encoding="utf-8")
            print(f"wrote {args.output}", file=sys.stderr)
        else:
            print(out)
    except OSError as exc:
        print(f"error: cannot read or write file: {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"error: --input is not valid JSON: {exc}", file=sys.stderr)
        return 1
    except (ValueError, KeyError, TypeError, ZeroDivisionError) as exc:
        print(f"error: invalid market model: {exc}", file=sys.stderr)
        return 1

    if args.strict and report["severity_counts"].get("fail", 0) > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
