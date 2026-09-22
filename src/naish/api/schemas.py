from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from naish.domain.models import Decision


class PredictRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    monthly_cash_flow_sar: float = Field(ge=-1_000_000, le=10_000_000)
    registration_age_months: int = Field(ge=1, le=1200)


class PredictionData(BaseModel):
    default_probability: float = Field(ge=0.0, le=1.0)
    decision: Decision


class ErrorData(BaseModel):
    code: str
    message: str
    details: Any | None = None


class PredictResponse(BaseModel):
    trace_id: str
    data: PredictionData | None
    error: ErrorData | None


class StatusData(BaseModel):
    status: str


class StatusResponse(BaseModel):
    trace_id: str
    data: StatusData | None
    error: ErrorData | None


class StatsData(BaseModel):
    predictions_processed: int = Field(ge=0)


class StatsResponse(BaseModel):
    trace_id: str
    data: StatsData | None
    error: ErrorData | None
