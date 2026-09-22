.PHONY: install test lint image smoke train run

install:
	python -m pip install -e ".[dev]"

test:
	pytest

lint:
	ruff check .
	mypy src
	lint-imports

image:
	docker build -t naish:local .

smoke:
	./scripts/smoke.sh

train:
	python scripts/generate_dataset.py
	python scripts/train_model.py

run:
	uvicorn naish.api.main:app --host 0.0.0.0 --port 8000
