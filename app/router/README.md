# `app/router/` - API Route Declarations

Routers là lớp tiếp nhận HTTP/WebSocket request. Router chịu trách nhiệm validate input, áp dụng auth/rate limit, gọi service và serialize response.

Router không nên chứa business logic dài; logic nghiệp vụ nằm trong `app/service/`.

## Structure

```text
router/
|-- __init__.py
`-- v1/
    |-- __init__.py
    |-- auth_api.py
    |-- extraction_api.py
    |-- interview_api.py
    |-- job_matching_api.py
    |-- optimization_api.py
    `-- README.md
```

All v1 routers are mounted in `app/main.py` with prefix `/api/v1`.

## Responsibilities

- Parse path/query/body/form parameters.
- Enforce auth via `get_current_user` where required.
- Enforce rate limits with SlowAPI decorators.
- Perform resource ownership checks at the API boundary when needed.
- Convert service errors to HTTP status codes.
- Return Pydantic response models or plain JSON structures.

## Versioning

API versioning is directory-based. A future `/api/v2` should be added as `router/v2/` without changing v1 contracts.

See [v1/README.md](v1/README.md) for endpoint details.
