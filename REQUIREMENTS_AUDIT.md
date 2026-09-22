# Requirements Audit

| Requirement | Status | Evidence |
| --- | --- | --- |
| `src` layout with domain/service/adapters/api | PASS | `src/naish/` |
| Swappable model interface with Protocol and DI | PASS | `service/ports.py`, startup wiring in `api/main.py` |
| Architecture enforced by import-linter | PASS | `pyproject.toml` contracts and CI `lint-imports` step |
| Unified Makefile install/test/lint/image/smoke | PASS | `Makefile` |
| `POST /v1/predict` unified response/error envelope with trace ID | PASS | `api/main.py`, `api/schemas.py`, integration tests |
| Strict input validation | PASS | `PredictRequest` uses `extra="forbid"` and numeric bounds |
| Model load and warm-up only at startup | PASS | FastAPI lifespan in `api/main.py` |
| Separate `/health` and `/ready` | PASS | API routes and integration test |
| Multi-stage Docker image | PASS | `Dockerfile` |
| Docker image ≤ 500 MB | MANUAL ACTION REQUIRED | CI enforces limit; local Docker daemon unavailable for measurement in this build environment |
| Non-root image and clean shutdown | PASS | `USER app`, `STOPSIGNAL SIGTERM`, Uvicorn lifecycle |
| Docker healthcheck targets `/ready` | PASS | `Dockerfile` and compose healthchecks |
| Compose service plus supporting service, health-gated | PASS | API + Redis with `condition: service_healthy` |
| Unit, integration, behavioural tests | PASS | `tests/unit`, `tests/integration`, `tests/behavioural` |
| Behavioural invariance, directional, golden reference | PASS | `test_model_behaviour.py`, `golden_cases.json` |
| Branch coverage ≥80% core | PASS | Local run measured 100% domain/service branch coverage |
| Fast gate ≤60 sec | PASS | Local full suite measured in `BENCHMARKS.md` |
| CI lint/type → tests → smoke → publish | PASS | `.github/workflows/ci.yml` job dependencies |
| Publish only on merge/push to main, SHA tag | PASS | `publish` job condition and GHCR `${{ github.sha }}` tag |
| Branch protection on main | MANUAL ACTION REQUIRED | GitHub repository setting must be enabled after push |
| Typed fail-fast settings | PASS | `config.py` |
| No secrets in code/history and scanning | PASS | `.env` ignored; safe `.env.example`; Gitleaks CI step |
| Structured JSON logs with trace ID and no sensitive data | PASS | `api/logging.py`; only event names are logged |
| GitHub URL and clean 5+ commit history | MANUAL ACTION REQUIRED | Local repository contains 5 commits; remote URL requires your GitHub repository |
| Green CI and GHCR image | MANUAL ACTION REQUIRED | Requires push to GitHub Actions/GHCR |
| README runbook | PASS | `README.md` |
| BENCHMARKS.md | PASS | Real model/test measurements present; Docker-only values explicitly await Docker run |
| DECISIONS.md with five decisions | PASS | `DECISIONS.md` |
| At least one working tested extension | PASS | `/v1/stats` prediction counter with integration test |
| Live demo readiness | PASS | Compose/runbook includes valid and malformed request flow; actual presentation is manual |
| No arbitrary golden regeneration | PASS | Golden file committed; no generator exists; decision documented |
| No production `:latest` | PASS | SHA-only GHCR publish |
