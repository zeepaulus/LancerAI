"""Vector database repository for embedding storage and retrieval.

Abstracts ChromaDB / Qdrant operations so the service layer
remains agnostic to the specific vector DB implementation.
"""

import logging
from typing import Any

import chromadb

logger = logging.getLogger(__name__)


class VectorRepository:
    """Manages vector embeddings for RAG and semantic matching.

    Used by:
    - Module 1: Store CV embeddings after extraction.
    - Module 2: Retrieve industry benchmarks for Roast/Rewrite agents.
    - Module 3: Semantic similarity scoring for JD matching.
    """

    def __init__(self, host: str, port: int, collection_name: str, api_key: str = "") -> None:
        self._host = host
        self._port = port
        self._collection_name = collection_name
        self._api_key = api_key
        
        self.db_type = None
        self._chroma_client = None
        self._qdrant_client = None
        self._collection = None

        if "cloud.qdrant.io" in host:
            self.db_type = "qdrant"
            from qdrant_client import QdrantClient
            self._qdrant_client = QdrantClient(url=host, api_key=api_key)
            logger.info(f"Initialized Qdrant Cloud at {host}, collection: {collection_name}")
            
        elif host == "localhost":
            self.db_type = "qdrant"
            from qdrant_client import QdrantClient
            self._qdrant_client = QdrantClient(host=host, port=port)
            logger.info(f"Initialized local Qdrant at {host}:{port}, collection: {collection_name}")
            
        elif "api.trychroma.com" in host or ("chroma" in host and "http" in host):
            self.db_type = "chroma"
            headers = {"x-chroma-token": api_key} if api_key else {}
            self._chroma_client = chromadb.HttpClient(
                host=host, 
                port=port,
                headers=headers
            )
            self._collection = self._chroma_client.get_or_create_collection(name=self._collection_name)
            logger.info(f"Initialized Chroma Cloud at {host}, collection: {collection_name}")
            
        else:
            self.db_type = "chroma"
            self._chroma_client = chromadb.PersistentClient(path=host)
            self._collection = self._chroma_client.get_or_create_collection(name=self._collection_name)
            logger.info(f"Initialized local ChromaDB at {host}, collection: {collection_name}")

    def _ensure_qdrant_collection(self, size: int) -> None:
        if self.db_type != "qdrant":
            return
            
        from qdrant_client.http.models import VectorParams, Distance
        try:
            self._qdrant_client.get_collection(self._collection_name)
        except Exception:
            self._qdrant_client.create_collection(
                collection_name=self._collection_name,
                vectors_config=VectorParams(size=size, distance=Distance.COSINE)
            )

    async def store_embedding(
        self,
        doc_id: str,
        text: str,
        embedding: list[float],
        metadata: dict[str, Any],
    ) -> None:
        """Store a document embedding with associated metadata."""
        if self.db_type == "chroma":
            self._collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                metadatas=[metadata],
                documents=[text]
            )
        elif self.db_type == "qdrant":
            from qdrant_client.http.models import PointStruct
            self._ensure_qdrant_collection(len(embedding))
            
            # Qdrant strictly requires UUID or int as ID.
            # Convert string to UUID deterministically if not UUID
            import uuid
            try:
                # check if it's already a valid UUID string
                uuid_obj = uuid.UUID(doc_id)
                qdrant_id = str(uuid_obj)
            except ValueError:
                # generate a deterministic UUID
                qdrant_id = str(uuid.uuid5(uuid.NAMESPACE_OID, doc_id))

            self._qdrant_client.upsert(
                collection_name=self._collection_name,
                points=[
                    PointStruct(
                        id=qdrant_id,
                        vector=embedding,
                        payload={"text": text, **metadata, "_original_id": doc_id}
                    )
                ]
            )

    async def search_similar(self, query_embedding: list[float], top_k: int = 5) -> list[dict[str, Any]]:
        """Find the top-k most similar documents to a query embedding."""
        formatted_results = []
        if self.db_type == "chroma":
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            if not results or not results['ids'] or not results['ids'][0]:
                return formatted_results
                
            ids = results['ids'][0]
            distances = results['distances'][0] if 'distances' in results and results['distances'] else []
            metadatas = results['metadatas'][0] if 'metadatas' in results and results['metadatas'] else []
            documents = results['documents'][0] if 'documents' in results and results['documents'] else []
            
            for i in range(len(ids)):
                score = 1.0 - distances[i] if i < len(distances) else 0.0
                formatted_results.append({
                    "id": ids[i],
                    "score": score,
                    "metadata": metadatas[i] if i < len(metadatas) else {},
                    "text": documents[i] if i < len(documents) else ""
                })
                
        elif self.db_type == "qdrant":
            results = self._qdrant_client.search(
                collection_name=self._collection_name,
                query_vector=query_embedding,
                limit=top_k
            )
            for res in results:
                payload = res.payload or {}
                text = payload.pop("text", "")
                original_id = payload.pop("_original_id", str(res.id))
                formatted_results.append({
                    "id": original_id,
                    "score": res.score,
                    "metadata": payload,
                    "text": text
                })
                
        return formatted_results
