"""LLM Response Cache Repository — Semantic lookup and persistence.

Provides three operations:
  - ``find_similar``: Loads all embeddings from DB and finds the entry with
    the highest cosine similarity to a given prompt embedding. Returns the
    cached entry if similarity >= threshold, else None.
  - ``save``: Persists a new prompt/response pair with its embedding.
  - ``increment_hit``: Updates hit_count and last_accessed_at when a cache
    entry is served.

Performance note:
    Cosine similarity is computed in Python (numpy) over all rows. This is
    fine for up to ~50 000 entries. For larger scale, migrate to pgvector
    (PostgreSQL extension) or move embeddings into the Vector DB (Qdrant /
    Chroma) with its native ANN search.
"""

from __future__ import annotations

import hashlib
import logging
import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

import numpy as np
from sqlalchemy import func, select, update

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from app.models.llm_cache import LLMResponseCache

logger = logging.getLogger(__name__)


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two equal-length float vectors."""
    va = np.array(a, dtype=np.float32)
    vb = np.array(b, dtype=np.float32)
    norm_a = float(np.linalg.norm(va))
    norm_b = float(np.linalg.norm(vb))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return float(np.dot(va, vb) / (norm_a * norm_b))


def sha256_hex(text: str) -> str:
    """Return SHA-256 hex digest of a UTF-8 string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class LLMCacheRepository:
    """Async repository for the llm_response_cache table."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ------------------------------------------------------------------
    # Read — semantic lookup
    # ------------------------------------------------------------------

    async def find_similar(
        self,
        prompt_embedding: list[float],
        model_name: str,
        threshold: float = 0.92,
    ) -> tuple[LLMResponseCache, float] | None:
        """Find the most similar cached entry for a given embedding.

        Args:
            prompt_embedding: Float32 embedding of the incoming prompt.
            model_name: Only compare against entries from the same model
                        to avoid cross-model semantic drift.
            threshold: Cosine similarity cutoff. Entries below this score
                       are not considered a cache HIT.

        Returns:
            A tuple of ``(LLMResponseCache, similarity_score)`` if a HIT
            is found, or ``None`` for a MISS.
        """
        if not prompt_embedding:
            return None

        # Load only the columns needed for similarity computation.
        # Avoid loading response_text for all rows — fetch it only for the winner.
        stmt = select(
            LLMResponseCache.id,
            LLMResponseCache.prompt_embedding,
            LLMResponseCache.hit_count,
        ).where(LLMResponseCache.model_name == model_name)

        result = await self._session.execute(stmt)
        rows = result.all()

        if not rows:
            return None

        best_id: str | None = None
        best_score: float = -1.0

        for row in rows:
            entry_embedding: list[float] = list(row.prompt_embedding or [])
            if not entry_embedding:
                continue
            score = _cosine_similarity(prompt_embedding, entry_embedding)
            if score > best_score:
                best_score = score
                best_id = str(row.id)

        if best_id is None or best_score < threshold:
            logger.debug(
                "[LLMCache] MISS — best score=%.4f < threshold=%.4f for model=%s",
                best_score,
                threshold,
                model_name,
            )
            return None

        # Fetch the full winner row
        full_stmt = select(LLMResponseCache).where(LLMResponseCache.id == best_id)
        full_result = await self._session.execute(full_stmt)
        entry = full_result.scalar_one_or_none()
        if entry is None:
            return None

        logger.info(
            "[LLMCache] HIT — id=%s score=%.4f model=%s hit_count=%d",
            best_id,
            best_score,
            model_name,
            entry.hit_count,
        )
        return entry, best_score

    # ------------------------------------------------------------------
    # Write — persist new entry
    # ------------------------------------------------------------------

    async def save(
        self,
        prompt_text: str,
        response_text: str,
        prompt_embedding: list[float],
        model_name: str,
        backend: str,
        triggered_by_user_id: str | None = None,
    ) -> LLMResponseCache:
        """Save a new prompt/response pair with its embedding to the cache.

        Args:
            prompt_text: The full prompt string sent to the LLM.
            response_text: The LLM response to cache.
            prompt_embedding: Float32 embedding of ``prompt_text``.
            model_name: LLM model identifier (e.g. ``google/gemma-4-31b-it``).
            backend: Backend name — ``nvidia``, ``groq``, or ``ollama``.
            triggered_by_user_id: Optional user ID for analytics tracing.

        Returns:
            The newly created ``LLMResponseCache`` ORM instance.
        """
        entry = LLMResponseCache(
            id=str(uuid.uuid4()),
            prompt_hash=sha256_hex(prompt_text),
            prompt_text=prompt_text,
            response_text=response_text,
            prompt_embedding=prompt_embedding,
            model_name=model_name,
            backend=backend,
            triggered_by_user_id=triggered_by_user_id,
            hit_count=0,
            created_at=datetime.now(UTC),
            last_accessed_at=datetime.now(UTC),
        )
        self._session.add(entry)
        await self._session.flush()  # assign DB id without committing
        logger.debug(
            "[LLMCache] Saved new entry id=%s model=%s backend=%s",
            entry.id,
            model_name,
            backend,
        )
        return entry

    # ------------------------------------------------------------------
    # Update — cache HIT bookkeeping
    # ------------------------------------------------------------------

    async def increment_hit(self, entry_id: str) -> None:
        """Atomically increment hit_count and update last_accessed_at.

        Uses a DB-side UPDATE to avoid the read-modify-write race condition
        that would arise from fetching the row and then saving it back.
        """
        stmt = (
            update(LLMResponseCache)
            .where(LLMResponseCache.id == entry_id)
            .values(
                hit_count=LLMResponseCache.hit_count + 1,
                last_accessed_at=func.now(),
            )
        )
        await self._session.execute(stmt)
        await self._session.flush()

    # ------------------------------------------------------------------
    # Convenience — exact hash lookup (O(1) fast path)
    # ------------------------------------------------------------------

    async def find_exact(self, prompt_text: str, model_name: str) -> LLMResponseCache | None:
        """Fast exact-match lookup by prompt hash before doing vector scan.

        This short-circuits the similarity computation for identical prompts,
        which is common in repeated API calls with templated system prompts.
        """
        prompt_hash = sha256_hex(prompt_text)
        stmt = (
            select(LLMResponseCache)
            .where(
                LLMResponseCache.prompt_hash == prompt_hash,
                LLMResponseCache.model_name == model_name,
            )
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
