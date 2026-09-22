from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Decision(StrEnum):
    AUTO_APPROVE = "auto_approve"
    MANUAL_REVIEW = "manual_review"
    REJECT = "reject"


@dataclass(frozen=True)
class CreditRiskInput:
    monthly_cash_flow_sar: float
    registration_age_months: int


@dataclass(frozen=True)
class CreditRiskResult:
    default_probability: float
    decision: Decision
