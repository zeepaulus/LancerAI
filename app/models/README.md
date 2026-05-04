# `app/models/` — SQLAlchemy ORM Models

Package định nghĩa database schema thông qua **SQLAlchemy 2.0 Declarative ORM**. Mỗi file tương ứng một table trong PostgreSQL. Đây là single source of truth cho cấu trúc data — Alembic migrations sẽ được generate từ đây.

## Design Decisions

- Sử dụng `DeclarativeBase` (SQLAlchemy 2.0+) thay cho legacy `declarative_base()`.
- Primary keys là **UUID string (36 chars)** thay vì integer sequence, phù hợp cho distributed systems và multi-tenant routing.
- `MetaData` được cấu hình với **Alembic naming conventions** (`ix_`, `uq_`, `ck_`, `fk_`, `pk_`) để migration scripts nhất quán.
- Tất cả timestamp columns dùng `DateTime(timezone=True)` với `server_default=func.now()` — timezone-aware từ database layer.

## Files

### `base.py`
`Base` class dùng chung cho tất cả ORM models.

```python
class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=convention)
```

Constraint naming convention đảm bảo Alembic luôn generate tên constraint xác định (deterministic), tránh tên tự động dạng `fk_1`.

### `user.py` — Table: `users`
Tài khoản người dùng, thiết kế **multi-tenant ready**.

| Column | Type | Notes |
|---|---|---|
| `id` | `String(36)` PK | UUID auto-generated |
| `tenant_id` | `String(36)` | Indexed; isolation boundary cho SaaS |
| `email` | `String(255)` | Unique, login identifier |
| `display_name` | `String(100)` | |
| `password_hash` | `String(255)` | bcrypt/argon2 hash |
| `role` | `String(20)` | `user` \| `admin` |
| `is_active` | `Boolean` | Soft-disable account |
| `created_at` / `updated_at` | `DateTime(tz)` | Server-side timestamps |

Relationships: `cv_records` (one-to-many), `interview_sessions` (one-to-many) — lazy `selectin` để tránh N+1.

### `cv_record.py` — Table: `cv_records`
Lưu dữ liệu CV sau khi trích xuất và tối ưu.

| Column | Type | Notes |
|---|---|---|
| `id` | `String(36)` PK | UUID |
| `user_id` | `String(36)` FK → `users.id` | Data isolation per user |
| `filename` | `String(255)` | Original upload filename |
| `language` | `String(5)` | `vi` \| `en` |
| `extracted_data` | `JSON` | Deep CV JSON từ LLM extraction |
| `optimized_data` | `JSON` (nullable) | Kết quả từ multi-agent pipeline |
| `created_at` | `DateTime(tz)` | |

Relationships: `owner` (many-to-one `User`), `interview_sessions` (one-to-many).

### `interview_session.py` — Table: `interview_sessions`
Lưu kết quả một phiên phỏng vấn giọng nói.

| Column | Type | Notes |
|---|---|---|
| `id` | `String(36)` PK | UUID |
| `user_id` | `String(36)` FK → `users.id` | Indexed |
| `cv_id` | `String(36)` FK → `cv_records.id` | Context CV của phiên |
| `mode` | `String(20)` | `practice` \| `mock` \| `quick` |
| `total_questions` | `Integer` | |
| `overall_confidence` | `Float` | 0–100 |
| `star_scores` | `JSON` | List of per-answer STAR scores |
| `logic_issues` | `JSON` | List of logical inconsistencies |
| `improvement_suggestions` | `JSON` | List of actionable suggestions |
| `started_at` | `DateTime(tz)` | |
| `completed_at` | `DateTime(tz)` (nullable) | Null nếu session bị abort |

### `job_listing.py` — Table: `job_listings`
Lưu Job Description data thu thập từ crawler.

| Column | Type | Notes |
|---|---|---|
| `id` | `String(36)` PK | UUID |
| `source` | `String(50)` | `topcv` \| `itviec` \| `linkedin` |
| `source_url` | `String(500)` | Canonical URL |
| `title` | `String(300)` | Job title |
| `company` | `String(200)` | |
| `location` | `String(200)` | |
| `description` | `Text` | Full JD body |
| `requirements` | `JSON` | Structured skills / requirements |
| `salary_range` | `String(100)` | |
| `is_active` | `Boolean` | Soft-delete |
| `created_by` | `String(36)` FK → `users.id` (nullable) | Admin who imported |
| `crawled_at` | `DateTime(tz)` | |

## Technology

| Component | Library / Feature |
|---|---|
| ORM | `SQLAlchemy 2.0+`, `DeclarativeBase`, `Mapped`, `mapped_column` |
| Database | PostgreSQL via `asyncpg` driver |
| Schema migration | `Alembic` (migrations generated từ models này) |
| Primary keys | UUID (`uuid.uuid4()`) — distributed-safe |
| Timestamps | `DateTime(timezone=True)`, `server_default=func.now()` |
