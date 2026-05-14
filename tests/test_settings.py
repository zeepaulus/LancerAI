"""Tests for app.core.settings — Settings validation and production guards."""

from __future__ import annotations

import pytest

from app.core.settings import Settings


class TestSettingsDefaults:
    """Settings must have correct defaults when no env vars are set."""

    def test_default_app_env_is_development(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("APP_ENV", raising=False)
        monkeypatch.setenv("AUTH_ALLOW_WEAK_SECRET", "true")
        s = Settings()  # type: ignore[call-arg]
        assert s.app_env == "development"

    def test_default_auth_algorithm_is_hs256(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("AUTH_ALLOW_WEAK_SECRET", "true")
        s = Settings()  # type: ignore[call-arg]
        assert s.auth_jwt_algorithm == "HS256"

    def test_allowed_origins_default_empty(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("AUTH_ALLOW_WEAK_SECRET", "true")
        s = Settings()  # type: ignore[call-arg]
        assert isinstance(s.allowed_origins, list)

    def test_vector_db_backend_default_is_chroma(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("AUTH_ALLOW_WEAK_SECRET", "true")
        s = Settings()  # type: ignore[call-arg]
        assert s.vector_db_backend == "chroma"


class TestProductionValidation:
    """Validator must block production deploys with insecure secret."""

    def test_weak_key_in_production_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("AUTH_ALLOW_WEAK_SECRET", "false")
        with pytest.raises(ValueError, match="AUTH_SECRET_KEY"):
            Settings(app_env="production", auth_secret_key="change-me-in-production")  # type: ignore[call-arg]

    def test_strong_key_in_production_passes(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("AUTH_ALLOW_WEAK_SECRET", "false")
        s = Settings(app_env="production", auth_secret_key="a-very-secure-key-64-chars-long!!")  # type: ignore[call-arg]
        assert s.app_env == "production"

    def test_weak_allow_flag_blocked_in_production(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("AUTH_ALLOW_WEAK_SECRET", "true")
        with pytest.raises(ValueError, match="AUTH_ALLOW_WEAK_SECRET"):
            Settings(app_env="production")  # type: ignore[call-arg]

    def test_development_with_default_key_passes(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("AUTH_ALLOW_WEAK_SECRET", "true")
        s = Settings(app_env="development", auth_secret_key="change-me-in-production")  # type: ignore[call-arg]
        assert s.app_env == "development"


class TestVectorDbSettings:
    """Vector DB settings reflect correct configuration."""

    def test_default_api_key_empty(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("AUTH_ALLOW_WEAK_SECRET", "true")
        s = Settings()  # type: ignore[call-arg]
        assert s.vector_db_api_key == ""

    def test_custom_vector_db_overrides(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("AUTH_ALLOW_WEAK_SECRET", "true")
        s = Settings(vector_db_host="http://mychroma", vector_db_port=9000, vector_db_collection="my_cvs")  # type: ignore[call-arg]
        assert s.vector_db_host == "http://mychroma"
        assert s.vector_db_port == 9000
        assert s.vector_db_collection == "my_cvs"

    def test_qdrant_backend(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("AUTH_ALLOW_WEAK_SECRET", "true")
        s = Settings(vector_db_backend="qdrant")  # type: ignore[call-arg]
        assert s.vector_db_backend == "qdrant"
