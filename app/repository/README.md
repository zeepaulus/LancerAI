# `repository/` — Truy cập dữ liệu

Lớp bọc truy vấn: **SQL** qua `RelationalRepository` (generic theo model), tương
lai vector (**Chroma**/Qdrant) và **Neo4j** qua `VectorRepository` / `GraphRepository`.

## Nguyên tắc

- Service gọi repository; **không** mở **SQL** tùy tiện trong router
- Luôn lọc theo người dùng / tổ chức cho dữ liệu thuộc tài khoản
