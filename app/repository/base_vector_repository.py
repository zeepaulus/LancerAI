"""Abstract base class for vector embedding storage and retrieval.

Service layer (ExtractionService, OptimizationService, MatchingService)
should depend ONLY on this abstract class — not on ChromaVectorRepository
or QdrantVectorRepository. This enforces the Dependency Inversion Principle.

Concrete implementations live in ``app/repository/vector_repository.py``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseVectorRepository(ABC):
    """Interface for vector embedding backends.

    Used by:
    - Module 1: Store CV embeddings after extraction.
    - Module 2: Retrieve industry benchmarks for RAG (Roast/Rewrite agents).
    - Module 3: Semantic similarity scoring for JD matching.
    """

    @abstractmethod
    async def store_embedding(
        self,
        doc_id: str,
        text: str,
        embedding: list[float],
        metadata: dict[str, Any],
    ) -> None:
        """Persist a document embedding with its text and metadata."""

    @abstractmethod
    async def search_similar(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Return the top-k most similar documents to a query embedding."""
