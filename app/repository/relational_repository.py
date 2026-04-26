"""Relational (PostgreSQL) repository layer.

Provides type-safe CRUD operations for all SQLAlchemy ORM models.
All methods are async and expect an injected AsyncSession.
"""

import uuid
from collections.abc import Sequence
from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

# Generic model type — must be a SQLAlchemy declarative model
ModelT = TypeVar("ModelT", bound=Base)


class RelationalRepository(Generic[ModelT]):
    """Generic async CRUD repository for a single ORM model.

    Instantiate once per model type:
        user_repo = RelationalRepository(User)
        cv_repo   = RelationalRepository(CVRecord)
    """

    def __init__(self, model: type[ModelT]) -> None:
        self._model = model

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    async def get_by_id(self, session: AsyncSession, record_id: str) -> ModelT | None:
        """Fetch a single record by primary key."""
        return await session.get(self._model, record_id)

    async def get_all(
        self,
        session: AsyncSession,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[ModelT]:
        """Fetch all records with pagination."""
        result = await session.execute(select(self._model).limit(limit).offset(offset))
        return result.scalars().all()

    async def filter_by(
        self,
        session: AsyncSession,
        **kwargs: Any,
    ) -> Sequence[ModelT]:
        """Fetch records matching all given keyword filters (AND logic)."""
        stmt = select(self._model)
        for field, value in kwargs.items():
            column = getattr(self._model, field, None)
            if column is None:
                raise ValueError(f"Model {self._model.__name__} has no column '{field}'")
            stmt = stmt.where(column == value)
        result = await session.execute(stmt)
        return result.scalars().all()

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    async def create(self, session: AsyncSession, **kwargs: Any) -> ModelT:
        """Insert a new record; auto-generates UUID if `id` not provided."""
        if "id" not in kwargs:
            kwargs["id"] = str(uuid.uuid4())
        record = self._model(**kwargs)
        session.add(record)
        await session.flush()  # Write to DB within the transaction (no commit yet)
        return record

    async def update(
        self,
        session: AsyncSession,
        record_id: str,
        **kwargs: Any,
    ) -> ModelT | None:
        """Update fields on an existing record. Returns None if not found."""
        record = await self.get_by_id(session, record_id)
        if record is None:
            return None
        for field, value in kwargs.items():
            if hasattr(record, field):
                setattr(record, field, value)
        await session.flush()
        return record

    async def delete(self, session: AsyncSession, record_id: str) -> bool:
        """Delete a record by primary key. Returns True if deleted."""
        record = await self.get_by_id(session, record_id)
        if record is None:
            return False
        await session.delete(record)
        await session.flush()
        return True

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    async def exists(self, session: AsyncSession, record_id: str) -> bool:
        """Check if a record with the given ID exists."""
        return await self.get_by_id(session, record_id) is not None
