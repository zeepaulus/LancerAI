"""SQLAlchemy base configuration for all ORM models."""

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# Naming convention for constraints (Alembic best practice)
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models.

    Uses the modern DeclarativeBase pattern (SQLAlchemy 2.0+).
    Includes consistent naming conventions for database constraints.
    """

    metadata = MetaData(naming_convention=convention)
