import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_defaults() -> None:
    s = Settings(_env_file=None)
    assert s.environment == "development"
    assert s.log_level == "INFO"


def test_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BIZOPS_ENVIRONMENT", "production")
    assert Settings(_env_file=None).environment == "production"


def test_invalid_environment_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BIZOPS_ENVIRONMENT", "staging-ish")
    with pytest.raises(ValidationError):
        Settings(_env_file=None)