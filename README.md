# Naish — Nasih Credit-Risk Service

Naish implements the **Nasih** capstone option: credit-risk scoring for small businesses. It predicts a default probability from monthly cash flow and business-registration age, then returns one of three decisions: `auto_approve`, `manual_review`, or `reject`.

The mandatory behavioural rule is protected by the real model: increasing monthly cash flow must never increase predicted default probability.

## Features

- Real scikit-learn logistic-regression model with a committed trained artifact
- Clean `src` architecture: domain, service, adapters, API
- Swappable model and store interfaces through Python `Protocol`
- FastAPI `POST /v1/predict` with strict validation and trace IDs
- Separate `/health` liveness and `/ready` readiness endpoints
- JSON structured logging correlated by trace ID
- Unit, integration, directional, invariance, and golden-reference tests
- Multi-stage non-root Docker image with `/ready` healthcheck
- Docker Compose with Redis health gating
- CI pipeline for lint/type/architecture checks, coverage, image smoke test, and SHA-tagged GHCR publishing
- Tested extension: Redis-backed prediction counter exposed at `GET /v1/stats`

## Architecture

```text
src/naish/
├── domain/       pure business rules and entities
├── service/      use-case orchestration and Protocol ports
├── adapters/     trained-model and storage implementations
├── api/          FastAPI endpoints, envelopes, tracing, logging
└── config.py     typed environment configuration
```

`import-linter` enforces that the domain does not depend on outer layers, the service does not depend on adapters/API, and adapters do not depend on API.

## Setup

Python 3.12 is recommended.

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Copy `.env.example` to `.env` if you want environment-based configuration. Do not commit `.env`.

### Environment variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `APP_ENV` | `development` | `development`, `test`, or `production` |
| `LOG_LEVEL` | `INFO` | Application log level |
| `MODEL_PATH` | `artifacts/nasih_model.joblib` | Trained model artifact path |
| `STORE_BACKEND` | `memory` | `memory` or `redis` |
| `REDIS_URL` | empty | Required when `STORE_BACKEND=redis` |

Typed settings fail immediately if Redis is selected without `REDIS_URL`.

## Train the model

The checked-in artifact is already trained. To reproduce it from the deterministic generated dataset:

```bash
python scripts/generate_dataset.py
python scripts/train_model.py
```

Current held-out metrics are recorded in `artifacts/metrics.json`.

## Run locally

```bash
make run
```

Or:

```bash
uvicorn naish.api.main:app --host 0.0.0.0 --port 8000
```

### Valid request

```bash
curl -X POST http://127.0.0.1:8000/v1/predict \
  -H "Content-Type: application/json" \
  -H "X-Trace-ID: demo-001" \
  -d '{"monthly_cash_flow_sar":150000,"registration_age_months":60}'
```

Example response shape:

```json
{
  "trace_id": "demo-001",
  "data": {
    "default_probability": 0.1357919621381105,
    "decision": "auto_approve"
  },
  "error": null
}
```

Malformed or unknown fields return the same envelope with `data: null` and an error object.

## Test and quality gates

```bash
make test
make lint
```

`make test` enforces branch coverage of at least 80% on the domain and service layers. The fast local gate is the full pytest suite and is designed to complete far below 60 seconds.

The behavioural suite includes:

- **Directional:** more monthly cash flow never increases default probability
- **Invariance:** numerically equivalent integer/float inputs produce the same result
- **Golden reference:** fixed reviewed cases in `tests/behavioural/golden_cases.json`

## Docker

Build:

```bash
make image
```

Run the full demo stack with Redis:

```bash
docker compose up --build
```

Then check:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/ready
curl http://127.0.0.1:8000/v1/stats
```

Smoke test the image:

```bash
make smoke
```

The CI job also rejects an image larger than 500 MB. Production publishing never uses the `:latest` tag; GHCR images are tagged with the exact commit SHA.

## CI/CD and branch protection

`.github/workflows/ci.yml` runs in this order:

1. Ruff, mypy, import-linter, and secret scan
2. Tests with branch-coverage gate
3. Docker image smoke test and 500 MB limit
4. GHCR publish only for a push/merge to `main`, tagged `${GITHUB_SHA}`

After pushing the repository, enable GitHub branch protection for `main`: require the CI checks, require at least one approving review, and disable force pushes.

## Makefile commands

```text
make install
make test
make lint
make image
make smoke
make train
make run
```

## Project files

- `BENCHMARKS.md` — measured model/test results and Docker measurement commands
- `DECISIONS.md` — five engineering decisions and rationale
- `.env.example` — safe configuration template
- `docker-compose.yml` — API + Redis demo stack
- `.github/workflows/ci.yml` — complete CI/CD pipeline
