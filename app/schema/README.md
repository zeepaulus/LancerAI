# `schema/` — Pydantic (API)

Request/response **JSON** cho **REST**; tách với `models` (ORM) và `service/agents/state`
(LangGraph).

Dùng `Field`, `Literal` nơi cần enum chặt; ổn định hợp đồng thì thêm
`response_model` trên router.
