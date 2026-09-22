#!/usr/bin/env sh
set -eu

IMAGE="${IMAGE:-naish:smoke}"
CONTAINER="naish-smoke-$$"

docker build -t "$IMAGE" .
docker run -d --rm --name "$CONTAINER" -p 18000:8000 "$IMAGE" >/dev/null
trap 'docker stop "$CONTAINER" >/dev/null 2>&1 || true' EXIT

attempt=0
until curl --fail --silent http://127.0.0.1:18000/ready >/dev/null; do
  attempt=$((attempt + 1))
  if [ "$attempt" -ge 30 ]; then
    docker logs "$CONTAINER"
    exit 1
  fi
  sleep 1
done

curl --fail --silent \
  -H 'Content-Type: application/json' \
  -d '{"monthly_cash_flow_sar":150000,"registration_age_months":60}' \
  http://127.0.0.1:18000/v1/predict >/dev/null
