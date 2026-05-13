from __future__ import annotations

from unittest.mock import Mock

import pytest


def test_database_engine_sqlite(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.core.database
    import app.core.settings

    captured_kwargs: dict[str, object] = {}

    def fake_create_async_engine(url: str, **kwargs: object) -> Mock:
        captured_kwargs.update(kwargs)
        return Mock()

    monkeypatch.setattr(app.core.settings, "_settings_instance", None)
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
    monkeypatch.setattr(app.core.database, "create_async_engine", fake_create_async_engine)

    app.core.database._get_engine.cache_clear()
    app.core.database._get_engine()

    assert captured_kwargs["pool_pre_ping"] is True
    assert "pool_size" not in captured_kwargs
    assert "max_overflow" not in captured_kwargs


def test_database_engine_postgres(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.core.database
    import app.core.settings

    captured_kwargs: dict[str, object] = {}

    def fake_create_async_engine(url: str, **kwargs: object) -> Mock:
        captured_kwargs.update(kwargs)
        return Mock()

    monkeypatch.setattr(app.core.settings, "_settings_instance", None)
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/db")
    monkeypatch.setenv("DATABASE_POOL_SIZE", "50")
    monkeypatch.setenv("DATABASE_MAX_OVERFLOW", "30")
    monkeypatch.setattr(app.core.database, "create_async_engine", fake_create_async_engine)

    app.core.database._get_engine.cache_clear()
    app.core.database._get_engine()

    assert captured_kwargs["pool_pre_ping"] is True
    assert captured_kwargs["pool_size"] == 50
    assert captured_kwargs["max_overflow"] == 30
