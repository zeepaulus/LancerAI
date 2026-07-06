"""LLM Response Cache model — Semantic response caching table.

Stores LLM prompt/response pairs with their vector embeddings.
On each request, cosine similarity is used to find semantically
equivalent prompts and serve cached responses without calling the API.
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class LLMResponseCache(Base):
    """Cached LLM prompt/response pairs with embedding for semantic lookup.

    Global cache shared across users, but ``triggered_by_user_id`` is
    stored for analytics / debugging purposes without restricting reuse.
    """

    __tablename__ = "llm_response_cache"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    # Quick exact-match lookup before doing vector similarity scan
    prompt_hash: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True, comment="SHA-256 hex of the full prompt text"
    )

    # Human-readable for debugging / inspection
    prompt_text: Mapped[str] = mapped_column(Text, nullable=False)
    response_text: Mapped[str] = mapped_column(Text, nullable=False)

    # Embedding stored as JSON array (list[float])
    # Uses core JSON — compatible with SQLite (tests) and PostgreSQL (prod).
    # Migrate to pgvector or move to Qdrant for large-scale ANN search.
    prompt_embedding: Mapped[list[Any]] = mapped_column(
        JSON, nullable=False, comment="Float32 embedding vector of prompt_text"
    )

    # Provenance metadata
    model_name: Mapped[str] = mapped_column(
        String(128), nullable=False, comment="LLM model name used to generate the response"
    )
    backend: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="nvidia | groq | ollama"
    )

    # The user whose request caused this cache MISS and triggered the LLM call.
    # Null if created by a system/background process.
    triggered_by_user_id: Mapped[str | None] = mapped_column(
        String(36), nullable=True, index=True,
        comment="user.id who triggered the original LLM call (analytics only)"
    )

    # Cache performance tracking
    hit_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False,
        comment="Number of times this entry was served from cache"
    )
    similarity_score: Mapped[float | None] = mapped_column(
        Float, nullable=True,
        comment="Cosine similarity of the best-matched cached prompt (populated on cache HIT)"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_accessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
        comment="Optional TTL — NULL means the entry never expires",
    )
