import pytest

from naish.domain.models import CreditRiskInput, Decision
from naish.service.predict import PredictCreditRisk

pytestmark = pytest.mark.unit


class FakeModel:
    def __init__(self, probability: float) -> None:
        self.probability = probability

    def predict_default_probability(self, risk_input: CreditRiskInput) -> float:
        return self.probability

    def warm_up(self) -> None:
        return None


class FakeStore:
    def __init__(self) -> None:
        self.count = 0

    def increment_predictions(self) -> int:
        self.count += 1
        return self.count

    def get_prediction_count(self) -> int:
        return self.count

    def is_ready(self) -> bool:
        return True

    def close(self) -> None:
        return None


def test_prediction_service_returns_decision_and_tracks_count() -> None:
    store = FakeStore()
    service = PredictCreditRisk(FakeModel(0.20), store)

    result = service.execute(CreditRiskInput(100_000.0, 36))

    assert result.default_probability == 0.20
    assert result.decision is Decision.AUTO_APPROVE
    assert service.prediction_count() == 1


def test_manual_review_probability_maps_correctly() -> None:
    service = PredictCreditRisk(FakeModel(0.40), FakeStore())

    result = service.execute(CreditRiskInput(40_000.0, 18))

    assert result.decision is Decision.MANUAL_REVIEW
