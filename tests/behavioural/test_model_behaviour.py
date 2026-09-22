import json
from pathlib import Path

import pytest

from naish.adapters.sklearn_model import SklearnRiskModel
from naish.domain.models import CreditRiskInput
from naish.domain.policy import decision_from_probability

pytestmark = pytest.mark.behavioural
MODEL_PATH = Path("artifacts/nasih_model.joblib")
GOLDEN_PATH = Path("tests/behavioural/golden_cases.json")


def model() -> SklearnRiskModel:
    return SklearnRiskModel(MODEL_PATH)


def test_directional_more_cash_flow_never_raises_default_probability() -> None:
    risk_model = model()
    for age in (6, 24, 60, 120):
        for cash_flow in (-20_000, 0, 25_000, 50_000, 100_000, 200_000):
            base = risk_model.predict_default_probability(CreditRiskInput(cash_flow, age))
            higher = risk_model.predict_default_probability(CreditRiskInput(cash_flow + 10_000, age))
            assert higher <= base


def test_invariance_integer_and_float_inputs_are_equivalent() -> None:
    risk_model = model()
    integer_input = CreditRiskInput(50_000, 24)
    float_input = CreditRiskInput(50_000.0, 24)

    assert risk_model.predict_default_probability(integer_input) == pytest.approx(
        risk_model.predict_default_probability(float_input), abs=1e-12
    )


def test_golden_reference_cases() -> None:
    risk_model = model()
    cases = json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))

    for case in cases:
        probability = risk_model.predict_default_probability(
            CreditRiskInput(case["monthly_cash_flow_sar"], case["registration_age_months"])
        )
        decision = decision_from_probability(probability)
        assert round(probability, 6) == case["expected_probability"]
        assert decision.value == case["expected_decision"]
