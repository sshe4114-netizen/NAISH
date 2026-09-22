import pytest
from pydantic import ValidationError

from naish.config import Settings

pytestmark = pytest.mark.unit


def test_redis_backend_requires_url() -> None:
    with pytest.raises(ValidationError):
        Settings(store_backend="redis", redis_url=None)
