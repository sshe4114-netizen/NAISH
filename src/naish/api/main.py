from __future__ import annotations

import logging
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.responses import Response

from naish.api.logging import configure_logging
from naish.api.schemas import (
    ErrorData,
    PredictRequest,
    PredictResponse,
    PredictionData,
    StatsData,
    StatsResponse,
    StatusData,
    StatusResponse,
)
from naish.adapters.sklearn_model import SklearnRiskModel
from naish.adapters.stores import InMemoryPredictionStore, RedisPredictionStore
from naish.config import Settings
from naish.domain.models import CreditRiskInput
from naish.service.ports import PredictionStore
from naish.service.predict import PredictCreditRisk
logger = logging.getLogger(__name__)


def _trace_id(request: Request) -> str:
    return str(getattr(request.state, "trace_id", "unknown"))


def _build_store(settings: Settings) -> PredictionStore:
    if settings.store_backend == "redis":
        assert settings.redis_url is not None
        return RedisPredictionStore(settings.redis_url)
    return InMemoryPredictionStore()


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or Settings()
    configure_logging(resolved_settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        model = SklearnRiskModel(resolved_settings.model_path)
        store = _build_store(resolved_settings)
        model.warm_up()
        app.state.predictor = PredictCreditRisk(model, store)
        app.state.store = store
        logger.info("service_started", extra={"trace_id": "startup"})
        try:
            yield
        finally:
            store.close()
            logger.info("service_stopped", extra={"trace_id": "shutdown"})

    app = FastAPI(title="Nasih Credit Risk Service", version="1.0.0", lifespan=lifespan)

    @app.middleware("http")
    async def trace_middleware(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request.state.trace_id = request.headers.get("X-Trace-ID", str(uuid4()))
        response = await call_next(request)
        response.headers["X-Trace-ID"] = request.state.trace_id
        return response

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        body = PredictResponse(
            trace_id=_trace_id(request),
            data=None,
            error=ErrorData(
                code="validation_error",
                message="Request validation failed",
                details=exc.errors(),
            ),
        )
        return JSONResponse(status_code=422, content=body.model_dump())

    @app.exception_handler(Exception)
    async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled_error", extra={"trace_id": _trace_id(request)})
        body = PredictResponse(
            trace_id=_trace_id(request),
            data=None,
            error=ErrorData(code="internal_error", message="Internal server error"),
        )
        return JSONResponse(status_code=500, content=body.model_dump())

    @app.get("/health", response_model=StatusResponse)
    def health(request: Request) -> StatusResponse:
        return StatusResponse(
            trace_id=_trace_id(request),
            data=StatusData(status="alive"),
            error=None,
        )

    @app.get("/ready", response_model=StatusResponse)
    def ready(request: Request) -> StatusResponse | JSONResponse:
        store: PredictionStore = request.app.state.store
        if not store.is_ready():
            body = StatusResponse(
                trace_id=_trace_id(request),
                data=None,
                error=ErrorData(code="not_ready", message="Supporting service is unavailable"),
            )
            return JSONResponse(status_code=503, content=body.model_dump())
        return StatusResponse(
            trace_id=_trace_id(request),
            data=StatusData(status="ready"),
            error=None,
        )

    @app.post("/v1/predict", response_model=PredictResponse)
    def predict(request: Request, payload: PredictRequest) -> PredictResponse:
        predictor: PredictCreditRisk = request.app.state.predictor
        result = predictor.execute(
            CreditRiskInput(
                monthly_cash_flow_sar=payload.monthly_cash_flow_sar,
                registration_age_months=payload.registration_age_months,
            )
        )
        logger.info("prediction_completed", extra={"trace_id": _trace_id(request)})
        return PredictResponse(
            trace_id=_trace_id(request),
            data=PredictionData(
                default_probability=result.default_probability,
                decision=result.decision,
            ),
            error=None,
        )

    @app.get("/v1/stats", response_model=StatsResponse)
    def stats(request: Request) -> StatsResponse:
        predictor: PredictCreditRisk = request.app.state.predictor
        return StatsResponse(
            trace_id=_trace_id(request),
            data=StatsData(predictions_processed=predictor.prediction_count()),
            error=None,
        )

    return app


app = create_app()
