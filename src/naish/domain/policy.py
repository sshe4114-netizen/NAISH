from __future__ import annotations

from naish.domain.models import Decision


def decision_from_probability(default_probability: float) -> Decision:
    if not 0.0 <= default_probability <= 1.0:
        raise ValueError("default_probability must be between 0 and 1")
    if default_probability < 0.25:
        return Decision.AUTO_APPROVE
    if default_probability < 0.55:
        return Decision.MANUAL_REVIEW
    return Decision.REJECT
