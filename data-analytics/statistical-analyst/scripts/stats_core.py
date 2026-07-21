#!/usr/bin/env python3
"""Standard-library implementations of the distributions the tests need.

Provides the normal, Student's t, and chi-square distributions plus the Wilson
score interval, with no scipy dependency. Imported by run_test.py and
test_selector.py; run directly with --selftest to verify every function against
published reference values before you trust a result.

Usage:
    python3 stats_core.py --selftest
    python3 stats_core.py --selftest --format json
"""

import argparse
import json
import math
import sys
from typing import Any, Callable, Dict, List, Tuple


def norm_sf(z: float) -> float:
    """Upper-tail probability of the standard normal distribution."""
    return 0.5 * math.erfc(z / math.sqrt(2.0))


def norm_ppf(p: float) -> float:
    """Inverse standard normal CDF (Acklam's rational approximation)."""
    if not 0.0 < p < 1.0:
        raise ValueError("probability must be strictly between 0 and 1")
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    plow = 0.02425
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
               ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    if p > 1 - plow:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
                ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    q = p - 0.5
    r = q * q
    return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / \
           (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)


def _betacf(a: float, b: float, x: float) -> float:
    """Continued-fraction expansion used by the incomplete beta function."""
    tiny, eps = 1e-30, 3e-13
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = tiny if abs(d) < tiny else d
    d = 1.0 / d
    h = d
    for m in range(1, 400):
        m2 = 2 * m
        for aa in (m * (b - m) * x / ((qam + m2) * (a + m2)),
                   -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))):
            d = 1.0 + aa * d
            d = tiny if abs(d) < tiny else d
            c = 1.0 + aa / c
            c = tiny if abs(c) < tiny else c
            d = 1.0 / d
            h *= d * c
        if abs(d * c - 1.0) < eps:
            break
    return h


def betai(a: float, b: float, x: float) -> float:
    """Regularized incomplete beta function I_x(a, b)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lead = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
                    + a * math.log(x) + b * math.log(1.0 - x))
    if x < (a + 1.0) / (a + b + 2.0):
        return lead * _betacf(a, b, x) / a
    return 1.0 - lead * _betacf(b, a, 1.0 - x) / b


def t_sf(t: float, df: float) -> float:
    """Upper-tail probability of Student's t distribution."""
    if df <= 0:
        raise ValueError("degrees of freedom must be positive")
    half = 0.5 * betai(df / 2.0, 0.5, df / (df + t * t))
    return half if t >= 0 else 1.0 - half


def t_crit(df: float, alpha: float) -> float:
    """Two-sided critical t value, found by bisection on the survival function."""
    lo, hi, target = 0.0, 200.0, alpha / 2.0
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if t_sf(mid, df) > target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def chi2_sf(x: float, df: int) -> float:
    """Upper-tail probability of the chi-square distribution."""
    a, xx = df / 2.0, x / 2.0
    if xx <= 0:
        return 1.0
    log_lead = -xx + a * math.log(xx) - math.lgamma(a)
    if xx < a + 1.0:
        ap, total, delta = a, 1.0 / a, 1.0 / a
        for _ in range(600):
            ap += 1.0
            delta *= xx / ap
            total += delta
            if abs(delta) < abs(total) * 1e-14:
                break
        return max(0.0, 1.0 - total * math.exp(log_lead))
    tiny = 1e-300
    b, c, d = xx + 1.0 - a, 1.0 / tiny, 1.0 / (xx + 1.0 - a)
    h = d
    for i in range(1, 600):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        d = tiny if abs(d) < tiny else d
        c = b + an / c
        c = tiny if abs(c) < tiny else c
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-14:
            break
    return h * math.exp(log_lead)


def wilson(successes: int, trials: int, z: float) -> Tuple[float, float]:
    """Wilson score interval for a single binomial proportion."""
    if trials <= 0:
        return (0.0, 0.0)
    p = successes / trials
    denom = 1.0 + z * z / trials
    centre = (p + z * z / (2 * trials)) / denom
    half = z * math.sqrt(p * (1 - p) / trials + z * z / (4 * trials * trials)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


# (label, computed value, published reference value, tolerance)
def _cases() -> List[Tuple[str, float, float, float]]:
    """Build the self-test cases against published reference values."""
    return [
        ("norm_sf(1.959964)", norm_sf(1.959964), 0.025, 1e-6),
        ("norm_sf(0)", norm_sf(0.0), 0.5, 1e-12),
        ("norm_sf(2.575829)", norm_sf(2.575829), 0.005, 1e-6),
        ("norm_ppf(0.975)", norm_ppf(0.975), 1.959964, 1e-5),
        ("norm_ppf(0.80)", norm_ppf(0.80), 0.8416212, 1e-5),
        ("norm_ppf(0.90)", norm_ppf(0.90), 1.2815516, 1e-5),
        ("norm_ppf(0.001)", norm_ppf(0.001), -3.0902323, 1e-4),
        ("t_sf(2.228, df=10) two-sided", 2 * t_sf(2.228, 10), 0.05, 1e-4),
        ("t_sf(1.960, df=1e6) two-sided", 2 * t_sf(1.959964, 1_000_000), 0.05, 1e-4),
        ("t_sf(12.706, df=1) two-sided", 2 * t_sf(12.7062, 1), 0.05, 1e-4),
        ("t_crit(df=10, a=0.05)", t_crit(10, 0.05), 2.228139, 1e-4),
        ("t_crit(df=30, a=0.05)", t_crit(30, 0.05), 2.042272, 1e-4),
        ("chi2_sf(3.841, df=1)", chi2_sf(3.841459, 1), 0.05, 1e-5),
        ("chi2_sf(5.991, df=2)", chi2_sf(5.991465, 2), 0.05, 1e-5),
        ("chi2_sf(12.592, df=6)", chi2_sf(12.591587, 6), 0.05, 1e-5),
        ("chi2_sf(18.307, df=10)", chi2_sf(18.307038, 10), 0.05, 1e-5),
        ("wilson(0/10) upper", wilson(0, 10, 1.959964)[1], 0.2775328, 1e-6),
        ("wilson(50/100) lower", wilson(50, 100, 1.959964)[0], 0.4038315, 1e-6),
    ]


def selftest() -> Dict[str, Any]:
    """Verify every distribution against published reference values."""
    results = []
    for label, got, want, tol in _cases():
        delta = abs(got - want)
        results.append({"case": label, "computed": got, "reference": want,
                        "delta": delta, "passed": delta <= tol})
    failed = [r for r in results if not r["passed"]]
    return {"total": len(results), "passed": len(results) - len(failed),
            "failed": len(failed), "cases": results}


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the self-test report as JSON or human-readable text."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    print("stats_core self-test — distributions vs published reference values")
    print("=" * 70)
    for case in report["cases"]:
        mark = "ok  " if case["passed"] else "FAIL"
        print(f"[{mark}] {case['case']:<34} computed={case['computed']:.8f} "
              f"reference={case['reference']:.8f}")
    print("-" * 70)
    print(f"{report['passed']}/{report['total']} passed")


def main() -> None:
    """Parse arguments and run the self-test."""
    parser = argparse.ArgumentParser(
        description="Standard-library statistical distributions; run --selftest "
                    "to verify them against published reference values.")
    parser.add_argument("--selftest", action="store_true",
                        help="Verify every distribution against known values.")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text).")
    args = parser.parse_args()

    if not args.selftest:
        parser.print_help()
        sys.exit(0)
    try:
        report = selftest()
    except (ValueError, OverflowError) as exc:
        print(f"ERROR: self-test could not complete: {exc}", file=sys.stderr)
        sys.exit(1)
    output(report, args.format)
    if report["failed"]:
        sys.exit(2)


if __name__ == "__main__":
    main()
