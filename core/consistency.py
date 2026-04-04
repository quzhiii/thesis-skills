from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from core.terminology import TextOccurrence


@dataclass(frozen=True)
class ConsistencyResult:
    canonical: str
    observed_variants: tuple[str, ...]
    anchor_variant: str
    anchor_occurrence: TextOccurrence
    evidence: str


def analyze_terminology_group(
    canonical: str,
    occurrences_by_variant: dict[str, Sequence[TextOccurrence]],
    *,
    min_distinct_variants: int = 2,
    min_total_occurrences: int = 2,
) -> ConsistencyResult | None:
    observed_variants = tuple(
        variant for variant, occurrences in occurrences_by_variant.items() if occurrences
    )
    total_occurrences = sum(len(occurrences) for occurrences in occurrences_by_variant.values())
    if len(observed_variants) < min_distinct_variants:
        return None
    if total_occurrences < min_total_occurrences:
        return None

    anchor_variant = next(
        (variant for variant in observed_variants if variant != canonical),
        observed_variants[0],
    )
    anchor_occurrence = occurrences_by_variant[anchor_variant][0]
    evidence = "; ".join(
        f"{variant} ({len(occurrences_by_variant[variant])})"
        for variant in observed_variants
    )
    return ConsistencyResult(
        canonical=canonical,
        observed_variants=observed_variants,
        anchor_variant=anchor_variant,
        anchor_occurrence=anchor_occurrence,
        evidence=evidence,
    )
