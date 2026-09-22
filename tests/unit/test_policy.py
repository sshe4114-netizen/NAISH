import pytest

from naish.domain.models import Decision
from naish.domain.policy import decision_from_probability

pytestmark = pytest.mark.unit


def test_decision_bands() -> None:
    assert decision_from_probability(0.10) is Decision.AUTO_APPROVE
    assert decision_from_probability(0.25) is Decision.MANUAL_REVIEW
    assert decision_from_probability(0.54) is Decision.MANUAL_REVIEW
    assert decision_from_probability(0.55) is Decision.REJECT


def test_probability_out_of_range_is_rejected() -> None:
    with pytest.raises(ValueError):
        decision_from_probability(1.1)
