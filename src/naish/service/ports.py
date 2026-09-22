from __future__ import annotations

from typing import Protocol

from naish.domain.models import CreditRiskInput


class RiskModel(Protocol):
    def predict_default_probability(self, risk_input: CreditRiskInput) -> float: ...

    def warm_up(self) -> None: ...


class PredictionStore(Protocol):
    def increment_predictions(self) -> int: ...

    def get_prediction_count(self) -> int: ...

    def is_ready(self) -> bool: ...

    def close(self) -> None: ...
