from __future__ import annotations

from threading import Lock

from redis import Redis


class InMemoryPredictionStore:
    def __init__(self) -> None:
        self._count = 0
        self._lock = Lock()

    def increment_predictions(self) -> int:
        with self._lock:
            self._count += 1
            return self._count

    def get_prediction_count(self) -> int:
        with self._lock:
            return self._count

    def is_ready(self) -> bool:
        return True

    def close(self) -> None:
        return None


class RedisPredictionStore:
    KEY = "naish:predictions:count"

    def __init__(self, redis_url: str) -> None:
        self._client = Redis.from_url(redis_url, decode_responses=True, socket_connect_timeout=2)

    def increment_predictions(self) -> int:
        return int(self._client.incr(self.KEY))

    def get_prediction_count(self) -> int:
        value = self._client.get(self.KEY)
        return int(value or 0)

    def is_ready(self) -> bool:
        try:
            return bool(self._client.ping())
        except Exception:
            return False

    def close(self) -> None:
        self._client.close()
