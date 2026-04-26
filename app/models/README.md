# `models/` — ORM (SQLAlchemy)

Định nghĩa bảng **PostgreSQL**: `User` (có `tenant_id` là mã tổ chức), `CVRecord`,
`InterviewSession`, `JobListing`, … — quan hệ **FK** và index theo thiết kế sản phẩm.

## Nguyên tắc

- Model chỉ schema + quan hệ **ORM**; không nhét logic nghiệp vụ phức tạp
- Mọi truy vấn theo người dùng phải lọc `user_id` và lọc thêm `tenant_id` khi dữ
  liệu được tách theo tổ chức ở tầng repository/service

## Thay đổi schema

Dùng **Alembic** (`uv run alembic revision --autogenerate`) từ thư mục gốc repo.
