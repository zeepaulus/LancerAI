# `app/repository/` — Data Access Layer

Package triển khai Repository pattern — cô lập toàn bộ logic truy cập dữ liệu khỏi service layer. Service không được phép gọi SQLAlchemy, ChromaDB, hay Neo4j trực tiếp; mọi I/O đi qua các lớp repository này.

## Design Principles

- **Dependency Inversion**: service layer chỉ phụ thuộc vào contract (class interface), không phụ thuộc vào implementation.
- **Session injection**: không giữ session trong repository — `AsyncSession` được inject vào từng method, đảm bảo transaction boundary nằm ở service layer.
- **Generic typing**: `RelationalRepository[ModelT]` dùng Python `Generic[T]` và `TypeVar`, một class duy nhất phục vụ tất cả ORM models.

## Files

### `relational_repository.py` — PostgreSQL CRUD
Generic async CRUD repository cho toàn bộ SQLAlchemy ORM models.

```python
user_repo = RelationalRepository(User)
cv_repo   = RelationalRepository(CVRecord)
```

**Methods:**

| Method | Signature | Description |
|---|---|---|
| `get_by_id` | `(session, id) → ModelT \| None` | Lookup by PK |
| `get_all` | `(session, limit, offset) → Sequence[ModelT]` | Paginated fetch |
| `filter_by` | `(session, **kwargs) → Sequence[ModelT]` | AND filter trên bất kỳ column nào |
| `create` | `(session, **kwargs) → ModelT` | Insert; auto-gen UUID nếu `id` thiếu |
| `update` | `(session, id, **kwargs) → ModelT \| None` | Partial update |
| `delete` | `(session, id) → bool` | Hard delete by PK |
| `exists` | `(session, id) → bool` | Kiểm tra tồn tại |

Tất cả write operations dùng `session.flush()` thay vì `commit()` — commit được quản lý bởi `get_db_session()` dependency ở tầng trên.

**Technology:** `SQLAlchemy 2.0+` async API (`AsyncSession`, `select()`, typed `Mapped` columns).

### `vector_repository.py` — Vector Database
Abstraction layer cho embedding storage và semantic search.

Dùng bởi:
- **Module 1 (Extraction)**: lưu CV embeddings sau khi trích xuất.
- **Module 2 (Optimization)**: retrieve industry benchmarks cho Roast/Rewrite agents.
- **Module 3 (Matching)**: semantic similarity scoring giữa CV và JD.

**Methods:**

| Method | Description |
|---|---|
| `store_embedding(doc_id, text, embedding, metadata)` | Lưu vector + metadata vào collection |
| `search_similar(query_embedding, top_k)` | ANN search, trả về top-K kết quả |

**Technology:** ChromaDB hoặc Qdrant — chọn bằng `Settings.vector_db_backend` + factory `create_vector_repository` (`app/repository/vector_repository.py`). Contract: `BaseVectorRepository`.

### `base_vector_repository.py`

ABC `store_embedding` / `search_similar` — service chỉ import lớp này.

### `graph_repository.py` — Knowledge Graph
Abstraction layer cho Neo4j — quan hệ giữa skills/technologies.

Relationship examples trong graph:
```
(React) -[:BELONGS_TO]-> (Frontend)
(Docker) -[:REQUIRES]-> (Linux)
(Kubernetes) -[:EXTENDS]-> (Docker)
```

Dùng bởi:
- **Module 2 (Optimization)**: hiểu ngữ cảnh skill để roast chính xác hơn.
- **Module 3 (Matching)**: domain-aware weighting trong Hybrid Scoring.

**Methods:**

| Method | Description |
|---|---|
| `get_related_skills(skill, depth)` | Graph traversal N-hops từ một skill node |
| `get_skill_importance(skill, domain)` | Tính importance score của skill trong domain |

**Technology (planned):** Neo4j via `neo4j` Python driver (async).

## Technology Summary

| Repository | Backend | Status |
|---|---|---|
| `RelationalRepository` | PostgreSQL + SQLAlchemy | Implemented |
| `vector_repository` (`BaseVectorRepository`) | ChromaDB / Qdrant | Implemented (backend theo config) |
| `GraphRepository` | Neo4j | Stub — pending |
