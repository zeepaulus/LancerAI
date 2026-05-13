"""Vector database repository — implementations and factory.

Two concrete backends are provided:
- ``ChromaVectorRepository``: ChromaDB (local persistent / HTTP server / Cloud)
- ``QdrantVectorRepository``: Qdrant (local server / Qdrant Cloud)

Factory function ``create_vector_repository`` selects the backend at runtime
based on the ``backend`` parameter (default: ``"chroma"``). The backend is
configured via ``Settings.vector_db_backend`` (env var: ``VECTOR_DB_BACKEND``).

Service layer should type-hint against ``BaseVectorRepository`` (from
``app.repository.base_vector_repository``) — NOT against the concrete classes
below. This keeps DIP intact.

Usage (via DI in app/core/providers/services.py):
    repo = create_vector_repository(host, port, collection, api_key, backend)
    # returns ChromaVectorRepository | QdrantVectorRepository
"""

from __future__ import annotations

import asyncio
import logging
import threading
import uuid
from functools import partial
from typing import Any

from app.repository.base_vector_repository import BaseVectorRepository

logger = logging.getLogger(__name__)


class VectorRepositoryError(Exception):
    """Raised when an underlying vector DB operation fails."""

    pass


# ===========================================================================
# ChromaDB backend
# ===========================================================================


def _create_chroma_client(host: str, port: int, api_key: str = "") -> Any:
    """Build and return a chromadb client for the given connection parameters.

    Supports three modes selected by ``host``:
    - ``api.trychroma.com`` in host → Chroma Cloud
    - ``http://`` / ``https://`` prefix  → Self-hosted HTTP server
    - anything else                      → Local PersistentClient (dev / tests)
    """
    import chromadb  # lazy import — only required when Chroma backend is selected

    if "api.trychroma.com" in host:
        headers = {"x-chroma-token": api_key} if api_key else {}
        client = chromadb.HttpClient(host=host, port=port, headers=headers)
        logger.info("ChromaDB: Chroma Cloud at %s", host)
    elif host.startswith("http://") or host.startswith("https://"):
        clean_host = host.split("://", 1)[1].split(":")[0]
        client = chromadb.HttpClient(host=clean_host, port=port)
        logger.info("ChromaDB: HTTP server at %s:%d", clean_host, port)
    else:
        client = chromadb.PersistentClient(path=host)
        logger.info("ChromaDB: local persistent store at %s", host)
    return client


class ChromaVectorRepository(BaseVectorRepository):
    """ChromaDB implementation of BaseVectorRepository."""

    def __init__(self, host: str, port: int, collection_name: str, api_key: str = "") -> None:
        self._collection_name = collection_name
        self._client = _create_chroma_client(host, port, api_key)
        # Force cosine distance so the score formula ``1.0 - distance``
        # is always in [0, 1]. With the default L2 metric, distances can
        # exceed 1.0 and produce negative scores.
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    async def store_embedding(
        self,
        doc_id: str,
        text: str,
        embedding: list[float],
        metadata: dict[str, Any],
    ) -> None:
        loop = asyncio.get_running_loop()
        try:
            await loop.run_in_executor(
                None,
                partial(
                    self._collection.upsert,
                    ids=[doc_id],
                    embeddings=[embedding],
                    metadatas=[metadata],
                    documents=[text],
                ),
            )
        except Exception as e:
            logger.exception("ChromaDB: Failed to store embedding")
            raise VectorRepositoryError("Failed to store embedding in ChromaDB") from e

    async def search_similar(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        loop = asyncio.get_running_loop()
        try:
            results = await loop.run_in_executor(
                None,
                partial(
                    self._collection.query,
                    query_embeddings=[query_embedding],
                    n_results=top_k,
                ),
            )
        except Exception as e:
            logger.exception("ChromaDB: Failed to search similar")
            raise VectorRepositoryError("Failed to search similar in ChromaDB") from e
        if not results or not results.get("ids") or not results["ids"][0]:
            return []

        ids = results["ids"][0]
        distances = (results.get("distances") or [[]])[0]
        metadatas = (results.get("metadatas") or [[]])[0]
        documents = (results.get("documents") or [[]])[0]

        def _score_at(i: int) -> float:
            if i >= len(distances):
                raw = 0.0
            else:
                d = distances[i]
                raw = 1.0 - float(d) if d is not None else 0.0
            return max(0.0, min(1.0, raw))

        return [
            {
                "id": ids[i],
                "score": _score_at(i),
                "metadata": metadatas[i] if i < len(metadatas) else {},
                "text": documents[i] if i < len(documents) else "",
            }
            for i in range(len(ids))
        ]


# ===========================================================================
# Qdrant backend
# ===========================================================================


class QdrantVectorRepository(BaseVectorRepository):
    """Qdrant implementation of BaseVectorRepository.

    Mode selection (based on ``host``):
    - ``cloud.qdrant.io`` in host → Qdrant Cloud (requires ``api_key``)
    - anything else               → Local Qdrant server

    Collection is auto-created on first ``store_embedding`` call using
    COSINE distance (standard for text embeddings).
    """

    def __init__(self, host: str, port: int, collection_name: str, api_key: str = "") -> None:
        from qdrant_client import QdrantClient

        self._collection_name = collection_name

        if "cloud.qdrant.io" in host:
            self._client = QdrantClient(url=host, api_key=api_key)
            logger.info("Qdrant: Cloud at %s", host)
        else:
            self._client = QdrantClient(host=host, port=port)
            logger.info("Qdrant: local server at %s:%d", host, port)

        self._collection_ensured = False
        # Lock prevents concurrent requests from racing to create the collection
        # on first use (TOCTOU: both threads see _collection_ensured=False).
        self._ensure_lock = threading.Lock()

    def _ensure_collection(self, vector_size: int) -> bool:
        """Ensure the Qdrant collection exists. Returns True if ready, False if not."""
        with self._ensure_lock:
            if self._collection_ensured:
                return True

            from qdrant_client.http.models import Distance, VectorParams

            if self._client.collection_exists(collection_name=self._collection_name):
                if vector_size > 0:
                    collection_info = self._client.get_collection(collection_name=self._collection_name)
                    vectors_config = collection_info.config.params.vectors
                    db_size = None
                    if isinstance(vectors_config, VectorParams):
                        db_size = vectors_config.size
                    elif isinstance(vectors_config, dict) and vectors_config:
                        # Extract the size from the first/default named vector configuration
                        db_size = next(iter(vectors_config.values())).size

                    if db_size is not None and db_size != vector_size:
                        raise VectorRepositoryError(
                            f"Qdrant collection dimension mismatch: expected {db_size}, "
                            f"got {vector_size}. Recreate/migrate collection before inserting."
                        )
                self._collection_ensured = True
                return True

            if vector_size == 0:
                return False

            try:
                self._client.create_collection(
                    collection_name=self._collection_name,
                    vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
                )
                logger.info("Qdrant: created collection '%s' (dim=%d)", self._collection_name, vector_size)
            except Exception:
                logger.exception("Qdrant: failed to create collection '%s'", self._collection_name)
                raise

            self._collection_ensured = True
            return True

    @staticmethod
    def _to_qdrant_id(doc_id: str) -> str:
        """Convert an arbitrary string ID to a valid Qdrant UUID."""
        try:
            return str(uuid.UUID(doc_id))
        except ValueError:
            return str(uuid.uuid5(uuid.NAMESPACE_OID, doc_id))

    async def store_embedding(
        self,
        doc_id: str,
        text: str,
        embedding: list[float],
        metadata: dict[str, Any],
    ) -> None:
        from qdrant_client.http.models import PointStruct

        loop = asyncio.get_running_loop()
        # Always pass the real embedding size so the collection can be created
        # with the correct vector dimensions on first insert.
        await loop.run_in_executor(None, self._ensure_collection, len(embedding))

        try:
            await loop.run_in_executor(
                None,
                partial(
                    self._client.upsert,
                    collection_name=self._collection_name,
                    points=[
                        PointStruct(
                            id=self._to_qdrant_id(doc_id),
                            vector=embedding,
                            payload={"text": text, **metadata, "_original_id": doc_id},
                        )
                    ],
                ),
            )
        except Exception as e:
            logger.exception("Qdrant: Failed to store embedding")
            raise VectorRepositoryError("Failed to store embedding in Qdrant") from e

    async def search_similar(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        loop = asyncio.get_running_loop()

        # Ensure collection exists before querying. Pass vector_size=0 so that
        # _ensure_collection skips creation (we don't know dims here and it's
        # fine to return [] for an empty/missing collection).
        collection_ready = await loop.run_in_executor(None, self._ensure_collection, 0)
        if not collection_ready:
            return []

        try:
            results = await loop.run_in_executor(
                None,
                partial(
                    self._client.query_points,
                    collection_name=self._collection_name,
                    query=query_embedding,
                    limit=top_k,
                ),
            )
        except Exception as e:
            logger.exception("Qdrant: query_points failed for collection '%s'", self._collection_name)
            raise VectorRepositoryError(f"Failed to search similar in Qdrant collection {self._collection_name}") from e

        output = []
        for res in results.points:
            payload = dict(res.payload or {})
            text = payload.pop("text", "")
            original_id = payload.pop("_original_id", str(res.id))
            output.append(
                {
                    "id": original_id,
                    "score": res.score,
                    "metadata": payload,
                    "text": text,
                }
            )
        return output


# ===========================================================================
# Factory
# ===========================================================================


def create_vector_repository(
    host: str,
    port: int,
    collection_name: str,
    api_key: str = "",
    backend: str = "chroma",
) -> BaseVectorRepository:
    """Return the correct vector repository backend.

    Selection priority:
    1. ``backend == "qdrant"``          → QdrantVectorRepository
    2. ``cloud.qdrant.io`` in host      → QdrantVectorRepository (Cloud)
    3. everything else                  → ChromaVectorRepository
    """
    if backend.lower() == "qdrant" or "cloud.qdrant.io" in host:
        return QdrantVectorRepository(host=host, port=port, collection_name=collection_name, api_key=api_key)

    return ChromaVectorRepository(host=host, port=port, collection_name=collection_name, api_key=api_key)
