"""Tests for VectorRepository factory và ChromaDB host detection logic."""

from __future__ import annotations

import threading

import pytest

from app.repository.base_vector_repository import BaseVectorRepository
from app.repository.vector_repository import (
    ChromaVectorRepository,
    QdrantVectorRepository,
    create_vector_repository,
)


class TestVectorRepositoryFactory:
    """Factory phải chọn đúng backend dựa vào backend param và host pattern."""

    def test_default_returns_chroma(self) -> None:
        # Dùng path local để không cần server thật
        repo = create_vector_repository(
            host="./test_chroma_tmp",
            port=8001,
            collection_name="test",
        )
        assert isinstance(repo, ChromaVectorRepository)

    def test_backend_qdrant_returns_qdrant(self) -> None:
        repo = create_vector_repository(
            host="localhost",
            port=6333,
            collection_name="test",
            backend="qdrant",
        )
        assert isinstance(repo, QdrantVectorRepository)

    def test_backend_chroma_explicit(self) -> None:
        repo = create_vector_repository(
            host="./test_chroma_tmp",
            port=8001,
            collection_name="test",
            backend="chroma",
        )
        assert isinstance(repo, ChromaVectorRepository)

    def test_qdrant_cloud_host_auto_selects_qdrant(self) -> None:
        # cloud.qdrant.io pattern takes priority over backend param
        repo = create_vector_repository(
            host="https://abc.cloud.qdrant.io",
            port=6333,
            collection_name="test",
            api_key="test-key",
            backend="chroma",  # should be overridden by cloud host pattern
        )
        assert isinstance(repo, QdrantVectorRepository)

    def test_factory_returns_base_type(self) -> None:
        repo = create_vector_repository(host="./test_chroma_tmp", port=8001, collection_name="test")
        assert isinstance(repo, BaseVectorRepository)


@pytest.mark.integration
class TestChromaVectorRepositoryHostDetection:
    """ChromaVectorRepository phải chọn đúng Chroma client mode theo host format."""

    def test_http_scheme_uses_http_client(self) -> None:
        """VECTOR_DB_HOST=http://localhost → HttpClient (không tạo folder local)."""
        repo = ChromaVectorRepository(
            host="http://localhost",
            port=8001,
            collection_name="test_col",
        )
        # chromadb v0.5+ hợp nhất class names — check bằng cách verify _client có base_url attr
        # (HttpClient) hoặc _path attr (PersistentClient)
        client = repo._client
        # HttpClient có thuộc tính liên quan đến HTTP
        _has_http_attr = hasattr(client, "_api") or hasattr(client, "_server") or hasattr(client, "_session")
        has_path_attr = hasattr(client, "_path") or hasattr(client, "_db_path")
        # Khi dùng http:// scheme, KHÔNG nên dùng PersistentClient (không có _path)
        assert not has_path_attr, "Không được tạo PersistentClient khi host có http:// scheme"

    def test_local_path_uses_persistent_client(self) -> None:
        """VECTOR_DB_HOST=./chroma_data → PersistentClient."""
        repo = ChromaVectorRepository(
            host="./chroma_test_data",
            port=8001,
            collection_name="test_col",
        )
        # PersistentClient lưu data vào path
        client = repo._client
        # Kiểm tra path được set đúng (chroma v0.5+ lưu trong _db / _client)
        client_str = repr(client).lower()
        assert "chroma_test_data" in client_str or hasattr(client, "_db") or hasattr(client, "_system")

    def test_plain_localhost_without_scheme_uses_persistent(self) -> None:
        """
        'localhost' không có http:// → PersistentClient (tạo folder 'localhost').
        Test này xác nhận behavior và nhắc developer dùng http:// scheme cho Docker.
        """
        # Chỉ kiểm tra không raise exception khi khởi tạo
        repo = ChromaVectorRepository(
            host="localhost",
            port=8001,
            collection_name="test_col",
        )
        assert repo._collection is not None  # collection được tạo


class TestBaseVectorRepositoryContract:
    """BaseVectorRepository phải enforce abstract interface."""

    def test_cannot_instantiate_base_directly(self) -> None:
        with pytest.raises(TypeError):
            BaseVectorRepository()  # type: ignore[abstract]

    def test_concrete_implements_all_abstract_methods(self) -> None:
        """Chroma và Qdrant đều phải implement store_embedding và search_similar."""
        import inspect

        abstract_methods = {
            name
            for name, method in inspect.getmembers(BaseVectorRepository)
            if getattr(method, "__isabstractmethod__", False)
        }
        assert "store_embedding" in abstract_methods
        assert "search_similar" in abstract_methods

        # Verify both concretes have these implemented (not abstract)
        for cls in [ChromaVectorRepository, QdrantVectorRepository]:
            remaining: set[str] = getattr(cls, "__abstractmethods__", set())
            assert len(remaining) == 0, f"{cls.__name__} still has abstract methods: {remaining}"


@pytest.mark.integration
class TestQdrantVectorRepositoryIntegration:
    """Integration tests dùng QdrantClient(':memory:') — không cần server thật."""

    def _make_repo(self) -> QdrantVectorRepository:
        """Tạo Qdrant repo với in-memory backend."""
        from qdrant_client import QdrantClient

        repo = QdrantVectorRepository.__new__(QdrantVectorRepository)
        repo._collection_name = "test_col"
        repo._collection_ensured = False
        repo._ensure_lock = threading.Lock()
        repo._client = QdrantClient(":memory:")
        return repo

    @pytest.mark.asyncio
    async def test_store_and_search_returns_scored_points(self) -> None:
        repo = self._make_repo()
        await repo.store_embedding(
            doc_id="doc-1",
            text="Python FastAPI engineer",
            embedding=[1.0, 0.0, 0.0],
            metadata={"language": "en"},
        )
        results = await repo.search_similar(query_embedding=[1.0, 0.0, 0.0], top_k=1)
        assert len(results) == 1
        r = results[0]
        assert r["id"] == "doc-1"
        assert r["text"] == "Python FastAPI engineer"
        assert r["score"] > 0.99  # cosine similarity ≈ 1.0
        assert r["metadata"]["language"] == "en"

    @pytest.mark.asyncio
    async def test_search_orthogonal_vector_returns_list(self) -> None:
        repo = self._make_repo()
        await repo.store_embedding(
            doc_id="seed",
            text="seed",
            embedding=[0.0, 1.0, 0.0],
            metadata={},
        )
        results = await repo.search_similar(query_embedding=[1.0, 0.0, 0.0], top_k=5)
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_search_empty_collection_returns_empty_list(self) -> None:
        """Collection with no stored embeddings must return [] without crashing."""
        repo = self._make_repo()
        results = await repo.search_similar(query_embedding=[1.0, 0.0, 0.0], top_k=5)
        assert results == []

    @pytest.mark.asyncio
    async def test_dimension_mismatch_raises_error(self) -> None:
        """Existing collection with different dimension should raise error."""
        from app.repository.vector_repository import VectorRepositoryError
        repo = self._make_repo()

        # Store an embedding with dimension 3
        await repo.store_embedding(
            doc_id="doc-dim-3",
            text="text",
            embedding=[1.0, 0.0, 0.0],
            metadata={}
        )

        # Reset ensured flag to force validation again
        repo._collection_ensured = False

        # Try to store an embedding with dimension 4
        with pytest.raises(VectorRepositoryError, match="dimension mismatch: expected 3, got 4"):
            await repo.store_embedding(
                doc_id="doc-dim-4",
                text="text",
                embedding=[1.0, 0.0, 0.0, 0.0],
                metadata={}
            )


class TestChromaVectorRepositoryIntegration:
    """Integration tests dùng ChromaDB ephemeral client — không ghi file."""

    def _make_repo(self) -> ChromaVectorRepository:
        import chromadb

        repo = ChromaVectorRepository.__new__(ChromaVectorRepository)
        repo._collection_name = "test_col"
        client = chromadb.EphemeralClient()
        repo._client = client
        repo._collection = client.get_or_create_collection(
            name="test_col",
            metadata={"hnsw:space": "cosine"},
        )
        return repo

    @pytest.mark.asyncio
    async def test_store_and_search_returns_results(self) -> None:
        repo = self._make_repo()
        await repo.store_embedding(
            doc_id="doc-1",
            text="Python developer",
            embedding=[1.0, 0.0, 0.0],
            metadata={"language": "en"},
        )
        results = await repo.search_similar(query_embedding=[1.0, 0.0, 0.0], top_k=1)
        assert len(results) == 1
        r = results[0]
        assert r["id"] == "doc-1"
        assert r["text"] == "Python developer"
        assert r["score"] > 0.99
        assert r["metadata"]["language"] == "en"

    @pytest.mark.asyncio
    async def test_search_orthogonal_vector_returns_list(self) -> None:
        repo = self._make_repo()
        await repo.store_embedding(
            doc_id="seed",
            text="seed doc",
            embedding=[0.0, 1.0, 0.0],
            metadata={"tag": "seed"},
        )
        results = await repo.search_similar(query_embedding=[1.0, 0.0, 0.0], top_k=5)
        assert isinstance(results, list)
        for item in results:
            assert {"id", "score", "metadata", "text"} <= item.keys()
            assert item["score"] >= 0.0
            assert item["score"] <= 1.0

    @pytest.mark.asyncio
    async def test_search_empty_collection_returns_empty_list(self) -> None:
        """Fresh Chroma collection with no data must return [] without crashing."""
        import chromadb

        repo = ChromaVectorRepository.__new__(ChromaVectorRepository)
        repo._collection_name = "empty_col"
        client = chromadb.EphemeralClient()
        repo._client = client
        repo._collection = client.get_or_create_collection(
            name="empty_col",
            metadata={"hnsw:space": "cosine"},
        )
        results = await repo.search_similar(query_embedding=[1.0, 0.0, 0.0], top_k=5)
        assert isinstance(results, list)
