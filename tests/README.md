# `tests/` — Pytest

`test_smoke.py` kiểm tra app khởi động, `/` trả LancerAI, **OpenAPI** có các
path **API** v1, **health** phỏng vấn.

```bash
uv run pytest
uv run pytest tests/test_smoke.py -v
```

Mở rộng: `conftest.py`, **fixture** client + token, test tích hợp với stack
**docker compose**.
