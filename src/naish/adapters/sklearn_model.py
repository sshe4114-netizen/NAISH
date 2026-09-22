from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import joblib
import numpy as np
from sklearn.pipeline import Pipeline

from naish.domain.models import CreditRiskInput


class SklearnRiskModel:
    def __init__(self, model_path: Path) -> None:
        if not model_path.exists():
            raise FileNotFoundError(f"Model artifact not found: {model_path}")
        artifact = cast(dict[str, Any], joblib.load(model_path))
        self._pipeline = cast(Pipeline, artifact["pipeline"])
        self._features = cast(list[str], artifact["features"])
        if self._features != ["monthly_cash_flow_sar", "registration_age_months"]:
            raise ValueError("Model artifact has an unexpected feature contract")

    def predict_default_probability(self, risk_input: CreditRiskInput) -> float:
        row = np.array(
            [[risk_input.monthly_cash_flow_sar, risk_input.registration_age_months]],
            dtype=float,
        )
        probability = float(self._pipeline.predict_proba(row)[0, 1])
        return probability

    def warm_up(self) -> None:
        self.predict_default_probability(
            CreditRiskInput(monthly_cash_flow_sar=50_000.0, registration_age_months=24)
        )
