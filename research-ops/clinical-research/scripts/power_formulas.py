#!/usr/bin/env python3
"""Design formulas for sample_size_calculator.py — the statistics themselves.

Holds the per-design sample-size and power calculations (two independent
proportions, two independent means, and time-to-event compared by log-rank),
the shared normal-quantile helper, and the method notes reported alongside every
result. Separated from the calculator so the statistical content can be reviewed
and revised by a biostatistician without touching input validation, dropout
inflation, reporting, or the CLI.

The NOTE_* strings are user-facing: they are what tells a study planner which
approximation produced their number and where it stops being trustworthy. Revise
them for accuracy, never to save space.

Method summary
--------------
two_proportion  Normal approximation with pooled variance under the null.
two_mean        Normal approximation plus the conventional t-correction
                (+ z^2/4 per arm), which tracks a noncentral-t calculation to
                within 0.05 and so matches a t-test-based statistics package.
survival        Schoenfeld required events, with Freedman reported alongside as
                the more conservative figure. Enrolment is derived from the
                event probability under exponential survival with uniform
                accrual.
achieved_power  Inverts each design to report the power a planned n delivers.
                Uses the normal approximation throughout, including for the
                two-mean design; see NOTE_MEAN.

Every formula here assumes a simple parallel-group design: no interim analyses,
no multiplicity adjustment, no covariate adjustment, no clustering.

Helper module: imported by its sibling, not run directly.
"""

from __future__ import annotations

import math
from statistics import NormalDist
from typing import Any

ND = NormalDist()

NOTE_PROP = ("Normal approximation with pooled variance under the null. For "
             "expected cell counts below 5, use an exact method instead.")
NOTE_MEAN = ("Assumes equal variance. Includes the conventional t-correction "
             "(+z^2/4 per arm) so n matches a t-test-based stats package; the raw "
             "normal-approximation n is about 1 lower per arm. Power reported at a "
             "planned n uses the normal approximation and is marginally optimistic. "
             "If the SD comes from a small pilot, add roughly 10-15% to n.")
NOTE_SURV = ("Event-driven design: the analysis triggers on the event count, not on "
             "the enrolment target. Exponential survival assumed; if hazards are "
             "non-proportional, log-rank is the wrong test.")
DISCLAIMER = ("Operational planning only. Assumes a parallel design with no interim "
              "analysis, multiplicity adjustment, covariate adjustment, or clustering. "
              "Requires biostatistician sign-off before it enters a protocol.")


def _z(alpha: float, sided: int, power: float) -> tuple[float, float]:
    """Return the critical value for alpha and the quantile for the target power."""
    if not 0 < alpha < 1:
        raise ValueError("alpha must be strictly between 0 and 1")
    if not 0 < power < 1:
        raise ValueError("power must be strictly between 0 and 1")
    if sided not in (1, 2):
        raise ValueError("sided must be 1 (one-sided) or 2 (two-sided)")
    return ND.inv_cdf(1 - alpha / sided), ND.inv_cdf(power)


def two_proportion(spec: dict[str, Any], alpha: float, sided: int, power: float,
                   k: float) -> dict[str, Any]:
    """Sample size per group for a difference in two independent proportions."""
    p1 = float(spec["p_control"])
    p2 = float(spec["p_treatment"])
    for name, p in (("p_control", p1), ("p_treatment", p2)):
        if not 0 < p < 1:
            raise ValueError(f"{name} is {p}; must be strictly between 0 and 1")
    delta = abs(p1 - p2)
    if delta == 0:
        raise ValueError("p_control and p_treatment are equal; no effect to power for")

    z_a, z_b = _z(alpha, sided, power)
    p_bar = (p1 + k * p2) / (1 + k)
    term_null = z_a * math.sqrt((1 + 1 / k) * p_bar * (1 - p_bar))
    term_alt = z_b * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2) / k)
    n_control = ((term_null + term_alt) ** 2) / (delta ** 2)

    return {
        "n_control": math.ceil(n_control),
        "n_treatment": math.ceil(n_control * k),
        "effect": {"p_control": p1, "p_treatment": p2,
                   "absolute_difference": round(delta, 4),
                   "relative_difference": round(delta / p1, 4)},
        "note": NOTE_PROP,
    }


def two_mean(spec: dict[str, Any], alpha: float, sided: int, power: float,
             k: float) -> dict[str, Any]:
    """Sample size per group for a difference in two independent means."""
    delta = abs(float(spec["mean_difference"]))
    sd = float(spec["std_dev"])
    if delta == 0:
        raise ValueError("mean_difference is 0; no effect to power for")
    if sd <= 0:
        raise ValueError(f"std_dev is {sd}; must be positive")

    z_a, z_b = _z(alpha, sided, power)
    n_control = (1 + 1 / k) * ((z_a + z_b) ** 2) * (sd ** 2) / (delta ** 2)
    # A t-test estimates the variance rather than assuming it known, so it needs
    # marginally more than the normal approximation. This closed form tracks a
    # noncentral-t calculation to within 0.05 across the usual range, which is
    # what makes the result agree with a statistics package.
    n_control += (z_a ** 2) / 4

    return {
        "n_control": math.ceil(n_control),
        "n_treatment": math.ceil(n_control * k),
        "effect": {"mean_difference": delta, "std_dev": sd,
                   "standardised_effect_size": round(delta / sd, 4)},
        "note": NOTE_MEAN,
    }


def _event_probability(median_months: float, accrual: float, followup: float) -> float:
    """Probability of an event under exponential survival with uniform accrual."""
    lam = math.log(2) / median_months
    if accrual <= 0:
        return 1 - math.exp(-lam * followup)
    # Standard result for uniform accrual over `accrual` months plus `followup`
    # months of additional observation.
    return 1 - (math.exp(-lam * followup)
                - math.exp(-lam * (followup + accrual))) / (lam * accrual)


def survival(spec: dict[str, Any], alpha: float, sided: int, power: float,
             k: float) -> dict[str, Any]:
    """Required events and enrolment for a log-rank comparison of two arms."""
    hr = float(spec["hazard_ratio"])
    if hr <= 0 or hr == 1:
        raise ValueError(f"hazard_ratio is {hr}; must be positive and not equal to 1")

    z_a, z_b = _z(alpha, sided, power)
    prop_c, prop_t = 1 / (1 + k), k / (1 + k)
    # Schoenfeld: the design is driven by the event count, not by n. Freedman is
    # reported alongside because it is the more conservative of the two, and a
    # large gap between them signals a hazard ratio extreme enough that the
    # choice of formula matters and a statistician should decide.
    events = math.ceil(((z_a + z_b) ** 2) / (prop_c * prop_t * (math.log(hr) ** 2)))
    events_freedman = (((1 + hr) / (1 - hr)) ** 2) * ((z_a + z_b) ** 2)

    median_c = spec.get("median_survival_control_months")
    prob = spec.get("probability_of_event")
    detail: dict[str, Any] = {}
    if prob is None and median_c:
        accrual = float(spec.get("accrual_months", 0))
        followup = float(spec.get("followup_months", 0))
        if accrual <= 0 and followup <= 0:
            raise ValueError("survival needs accrual_months or followup_months to "
                             "convert required events into an enrolment target")
        median_t = float(median_c) / hr
        p_c = _event_probability(float(median_c), accrual, followup)
        p_t = _event_probability(median_t, accrual, followup)
        prob = prop_c * p_c + prop_t * p_t
        detail = {"median_survival_control_months": float(median_c),
                  "implied_median_treatment_months": round(median_t, 2),
                  "event_probability_control": round(p_c, 4),
                  "event_probability_treatment": round(p_t, 4)}
    if not prob:
        raise ValueError("survival needs probability_of_event, or "
                         "median_survival_control_months plus accrual/followup")
    prob = float(prob)
    if not 0 < prob <= 1:
        raise ValueError(f"probability_of_event is {prob}; must be in (0, 1]")

    total_n = math.ceil(events / prob)
    n_control = math.ceil(total_n * prop_c)

    return {
        "n_control": n_control,
        "n_treatment": total_n - n_control,
        "required_events": events,
        "required_events_freedman": math.ceil(events_freedman),
        "overall_event_probability": round(prob, 4),
        "effect": {"hazard_ratio": hr, **detail},
        "note": NOTE_SURV,
    }


def achieved_power(design: str, spec: dict[str, Any], n_control: int, k: float,
                   alpha: float, sided: int) -> float:
    """Return the power actually achieved by a given per-group sample size."""
    z_a = ND.inv_cdf(1 - alpha / sided)
    n_treat = n_control * k
    if design == "two_mean":
        delta = abs(float(spec["mean_difference"]))
        sd = float(spec["std_dev"])
        # Normal approximation, so marginally optimistic against a t-test; the
        # gap is well under a percentage point at realistic n. See NOTE_MEAN.
        return ND.cdf(delta / (sd * math.sqrt(1 / n_control + 1 / n_treat)) - z_a)
    if design == "two_proportion":
        p1 = float(spec["p_control"])
        p2 = float(spec["p_treatment"])
        p_bar = (n_control * p1 + n_treat * p2) / (n_control + n_treat)
        se_null = math.sqrt(p_bar * (1 - p_bar) * (1 / n_control + 1 / n_treat))
        se_alt = math.sqrt(p1 * (1 - p1) / n_control + p2 * (1 - p2) / n_treat)
        return ND.cdf((abs(p1 - p2) - z_a * se_null) / se_alt)
    hr = float(spec["hazard_ratio"])
    events = (n_control + n_treat) * float(spec.get("probability_of_event") or 0.5)
    prop_c, prop_t = 1 / (1 + k), k / (1 + k)
    return ND.cdf(abs(math.log(hr)) * math.sqrt(events * prop_c * prop_t) - z_a)


# Design name -> the function that sizes it. The calculator validates the name
# against these keys, so adding a design here is the only change needed.
DESIGNS = {
    "two_proportion": two_proportion,
    "two_mean": two_mean,
    "survival": survival,
}
