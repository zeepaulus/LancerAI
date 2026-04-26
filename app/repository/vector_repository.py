"""Vector database repository for embedding storage and retrieval.

Abstracts ChromaDB / Qdrant operations so the service layer
remains agnostic to the specific vector DB implementation.
"""

from typing import Any


class VectorRepository:
    """Manages vector embeddings for RAG and semantic matching.

    Used by:
    - Module 1: Store CV embeddings after extraction.
    - Module 2: Retrieve industry benchmarks for Roast/Rewrite agents.
    - Module 3: Semantic similarity scoring for JD matching.
    """

    def __init__(self, host: str, port: int, collection_name: str) -> None:
        self._host = host
        self._port = port
        self._collection_name = collection_name
        # TODO: Initialize ChromaDB/Qdrant client

    async def store_embedding(
        self,
        doc_id: str,
        text: str,
        embedding: list[float],
        metadata: dict[str, Any],
    ) -> None:
        """Store a document embedding with associated metadata."""
        raise NotImplementedError

    async def search_similar(self, query_embedding: list[float], top_k: int = 5) -> list[dict[str, Any]]:
        """Find the top-k most similar documents to a query embedding."""
        raise NotImplementedError
