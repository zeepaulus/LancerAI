# `router/` — Phiên bản API

Gom **router** theo version (`v1/`, sau này có thể thêm `v2/`). **Main** gắn
prefix `/api/v1` (xem `app/main.py`).

Thêm version mới: tạo `app/router/v2/`, `include_router(..., prefix="/api/v2")`.
