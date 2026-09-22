from __future__ import annotations

from naish.domain.models import CreditRiskInput, CreditRiskResult
from naish.domain.policy import decision_from_probability
from naish.service.ports import PredictionStore, RiskModel


class PredictCreditRisk:
    def __init__(self, model: RiskModel, store: PredictionStore) -> None:
        self._model = model
        self._store = store

    def execute(self, risk_input: CreditRiskInput) -> CreditRiskResult:
        probability = self._model.predict_default_probability(risk_input)
        result = CreditRiskResult(
            default_probability=probability,
            decision=decision_from_probability(probability),
        )
        self._store.increment_predictions()
        return result

    def prediction_count(self) -> int:
        return self._store.get_prediction_count()
