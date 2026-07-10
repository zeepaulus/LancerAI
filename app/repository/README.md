# `app/repository/` - Data Access Layer

Repository layer cô lập truy cập dữ liệu khỏi service layer. Service không nên gọi SQLAlchemy, ChromaDB, Qdrant hoặc Neo4j trực tiếp nếu đã có repository tương ứng.

## Files

| File | Role |
|---|---|
| `relational_repository.py` | Generic async CRUD repository for SQLAlchemy models |
| `base_vector_repository.py` | Abstract vector store contract |
| `vector_repository.py` | ChromaDB and Qdrant implementations plus factory |
| `graph_repository.py` | Neo4j skill graph queries |
| `llm_cache_repository.py` | Exact and semantic lookup for cached LLM responses |

## RelationalRepository

Generic CRUD wrapper:

```python
user_repo = RelationalRepository(User)
cv_repo = RelationalRepository(CVRecord)
```

| Method | Description |
|---|---|
| `get_by_id(session, id)` | Lookup by primary key |
| `get_all(session, limit, offset)` | Paginated fetch |
| `filter_by(session, **kwargs)` | AND filter by model columns |
| `create(session, **kwargs)` | Insert and flush |
| `update(session, id, **kwargs)` | Partial update and flush |
| `delete(session, id)` | Hard delete |
| `exists(session, id)` | Boolean existence check |

Repositories flush but do not own high-level transaction decisions; callers commit/rollback.

## Vector Repository

Contract:

| Method | Description |
|---|---|
| `store_embedding(doc_id, text, embedding, metadata)` | Upsert document vector |
| `search_similar(query_embedding, top_k)` | Return nearest vectors |

Backends:

| Backend | Class | Selection |
|---|---|---|
| ChromaDB | `ChromaVectorRepository` | Default, `VECTOR_DB_BACKEND=chroma` |
| Qdrant | `QdrantVectorRepository` | `VECTOR_DB_BACKEND=qdrant` or Qdrant cloud host |

Used by:

- CV extraction for CV embeddings.
- Optimization retrieval context.
- Job matching recommendations.
- Crawler worker job embeddings.

## Graph Repository

`GraphRepository` wraps Neo4j operations.

| Method | Description |
|---|---|
| `get_related_skills(skill_name, depth)` | N-hop related skill lookup |
| `get_skill_importance(skill_name, domain)` | Importance score based on shortest path |
| `close()` | Release driver |

If Neo4j driver is unavailable, graph operations return empty/zero where possible. Query failures raise `GraphRepositoryError`.

## LLM Cache Repository

Stores prompt/response pairs in `llm_response_cache`.

Typical flow:

1. Exact SHA-256 hash lookup.
2. Embedding similarity lookup using cosine similarity.
3. Increment hit counter on cache hit.
4. Save prompt/response/embedding on miss.

## Design Notes

- Service layer type-hints vector access against `BaseVectorRepository`.
- Vector writes are usually best-effort because core user actions should not fail only because semantic search is down.
- Graph access is optional enrichment, not a hard dependency for matching.
