"""
Lifecycle classification logic.

Given a skill's demand_score and year-over-year growth_rate, classify it
into one of PRISM's lifecycle stages. This is genuinely computed from the
numbers (not copied from the seed archetype label) so that later phases
recomputing metrics from different data still produce consistent labels.

Stages: Emerging, Growing, Established, Transforming, Declining, Ghost
"""
from dataclasses import dataclass


@dataclass
class LifecycleThresholds:
    ghost_demand_ceiling: float = 15.0
    emerging_growth_floor: float = 35.0
    growing_growth_floor: float = 12.0
    declining_growth_ceiling: float = -12.0
    established_demand_floor: float = 55.0


DEFAULT_THRESHOLDS = LifecycleThresholds()


def classify_lifecycle_stage(
    demand_score: float,
    growth_rate: float,
    is_first_year: bool = False,
    transforming_hint: bool = False,
    thresholds: LifecycleThresholds = DEFAULT_THRESHOLDS,
) -> str:
    """
    transforming_hint marks skills whose *context of use* is shifting even
    though raw demand may look flat-to-growing (e.g. Data Engineering
    absorbing GenAI pipelines). It only nudges the label when the metrics
    are otherwise ambiguous — it never overrides a clear Ghost/Emerging
    signal, so the derived label still tracks the actual numbers.
    """
    if demand_score < thresholds.ghost_demand_ceiling:
        return "Ghost"

    if is_first_year:
        # No prior year to compare against; classify on demand level alone.
        return "Established" if demand_score >= thresholds.established_demand_floor else "Growing"

    if growth_rate <= thresholds.declining_growth_ceiling:
        return "Declining"

    if growth_rate >= thresholds.emerging_growth_floor:
        return "Emerging"

    if growth_rate >= thresholds.growing_growth_floor:
        if transforming_hint and demand_score >= thresholds.established_demand_floor:
            return "Transforming"
        return "Growing"

    if transforming_hint:
        return "Transforming"

    return "Established" if demand_score >= thresholds.established_demand_floor else "Growing"
