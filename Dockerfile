FROM python:3.12-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build
COPY pyproject.toml ./
COPY src ./src
RUN python -m pip install --prefix=/install .

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/usr/local/bin:$PATH

RUN groupadd --system app && useradd --system --gid app --create-home app

WORKDIR /app
COPY --from=builder /install /usr/local
COPY src ./src
COPY artifacts ./artifacts

ENV PYTHONPATH=/app/src \
    APP_ENV=production \
    MODEL_PATH=/app/artifacts/nasih_model.joblib \
    STORE_BACKEND=memory

USER app
EXPOSE 8000
STOPSIGNAL SIGTERM

HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=5 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/ready', timeout=2).read()" || exit 1

CMD ["uvicorn", "naish.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
